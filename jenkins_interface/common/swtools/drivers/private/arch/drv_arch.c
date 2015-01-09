/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch.c Archive file utilities
 *
 * ...
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

#include "icera_global.h"
#include "livanto_memmap.h"
#include "hwplatform.h"
#include "dxp_caches.h"
#include "mphal_wdt.h"
#include "drv_security.h"
#include "drv_brom_iface.h"
#include "drv_hwplat.h"
#include "drv_arch.h"
#include "drv_arch_local.h"
#include "os_uist_ids.h"
#include "drv_arch_pubk.h"
#include "drv_pmic.h"
#include "drv_fs.h"
#include "drv_chpc.h"
#include "drv_flash.h"
#include "ezxml.h"

#ifdef ICERA_FEATURE_EXTENDED_MODEM
#include "drv_dbg_noninit.h" /* drv_DbgFopen,... */
#endif

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include <string.h>
#include <stdio.h>
#include <stddef.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/

/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/* Archive table used in embedded software */
const tArchFileProperty arch_type[] =
{
    ARCH_PROP_APP
    ,ARCH_PROP_BT2
    ,ARCH_PROP_IFT
    ,ARCH_PROP_LDR
#if defined(ICERA_FEATURE_UNSIGNED_IMEI_FILE)
    ,ARCH_PROP_IMEI_NO_AUTH
#elif defined(ICERA_FEATURE_EXT_AUTH_IMEI_FILE)
    ,ARCH_PROP_IMEI_EXT_AUTH
#elif defined(ICERA_FEATURE_SOFT_ACTIVATION)
    ,ARCH_PROP_IMEI_SOFT_ACTIVATION
#elif defined(ICERA_FEATURE_ENCRYPTED_IMEI_FILE)
    ,ARCH_PROP_IMEI_ENCRYPTED_IMEI_FILE
#else
    ,ARCH_PROP_IMEI
#endif
#if defined(ICERA_FEATURE_UNSIGNED_CUSTCFG_FILE)
    ,ARCH_PROP_CUSTCFG_NO_AUTH
#elif defined(ICERA_FEATURE_EXT_AUTH_CUSTCFG_FILE)
    ,ARCH_PROP_CUSTCFG_EXT_AUTH
#else
    ,ARCH_PROP_CUSTCFG
#endif
#if defined (ICERA_FEATURE_ZEROCD_IGNORE_MAGIC)
    ,ARCH_PROP_ZEROCD_IGNORE_MAGIC
#else
    ,ARCH_PROP_ZEROCD
#endif
    ,ARCH_PROP_MASS
    ,ARCH_PROP_AUDIOCFG
    ,ARCH_PROP_COMPAT
    ,ARCH_PROP_PLATCFG
    ,ARCH_PROP_SECCFG
    ,ARCH_PROP_UNLOCK
#if defined(ICERA_FEATURE_EXT_AUTH_CALIB_FILE)
    ,ARCH_PROP_CALIB_EXT_AUTH
#else
    ,ARCH_PROP_CALIB
#endif
    ,ARCH_PROP_CALIB_PATCH
    ,ARCH_PROP_SSL_CERT
#if defined(ICERA_FEATURE_UNSIGNED_DEVICECFG_FILE)
    ,ARCH_PROP_DEVICECFG_NO_AUTH
#elif defined(ICERA_FEATURE_EXT_AUTH_DEVICECFG_FILE)
    ,ARCH_PROP_DEVICECFG_EXT_AUTH
#elif defined(ICERA_FEATURE_NO_PPID_DEVICECFG_FILE)
    ,ARCH_PROP_DEVICECFG_NO_PPID
#else
    ,ARCH_PROP_DEVICECFG
#endif
    ,ARCH_PROP_PRODUCTCFG
    ,ARCH_PROP_ROBCOUNTER
    ,ARCH_PROP_FLASHDISK
    ,ARCH_PROP_WEBUI_PACKAGE
#ifdef ICERA_FEATURE_REMOTE_FS
    ,ARCH_PROP_BT3
#endif
#ifdef ICERA_FEATURE_SOFT_ACTIVATION
    ,ARCH_PROP_ACT
    ,ARCH_PROP_ACT_DATA
#endif
};

const uint32 arch_type_max_id = sizeof(arch_type)/sizeof(tArchFileProperty);

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
int drv_arch_ReadHeader(tAppliFileHeader *fh, int fd)
{
    int ret = 1;

    REL_ASSERT(fh != NULL);
    DEV_ASSERT(fd >= 0);

    /* read tag/length fields of archive header */
    int bytes_read = drv_fs_Read(fd,  (char *)fh, offsetof(tAppliFileHeader,file_size));

    /* Check that we have read the number of bytes requested,
    and check the consistency of the header length field */
    if ((bytes_read != offsetof(tAppliFileHeader,file_size)) ||
        (fh->length < offsetof(tAppliFileHeader, rfu)) ||
        (fh->length > sizeof(tAppliFileHeader)))
    {
        ret = 0;
    }

    if(ret)
    {
        /* read remaining of archive header */
        bytes_read = drv_fs_Read(fd,  (char *)&fh->file_size, fh->length - offsetof(tAppliFileHeader,file_size));
        if (bytes_read != fh->length - offsetof(tAppliFileHeader,file_size))
        {
            ret = 0;
        }
    }

    return ret;
}

int drv_arch_RSASignVerify(bool in_ram,
                           uint8 *arch_start,
                           tAppliFileHeader * file_desc,
                           uint8 *hash_digest,
                           uint8 *rsa_sig,
                           uint32 *key_id)
{
    int i, ret, result = -1;
    uint8  readRsa[RSA_SIGNATURE_SIZE];
    uint32 keyID;
    uint8  *computedHashDigest = NULL;

    REL_ASSERT(file_desc != NULL);

    if(in_ram)
    {
        /* It's an archive buffer in RAM to authenticate.
          Need to find out all data for authentication:
           - perform a hash of archive data
           - get key ID
           - get RSA sig.*/
        OS_UIST_SMARKER( DRVARCH_UIST_ID_ARCH_ALREADY_IN_RAM );

        REL_ASSERT(arch_start != NULL);
        DEV_ASSERT(hash_digest == NULL);
        DEV_ASSERT(rsa_sig == NULL);
        DEV_ASSERT(key_id == NULL);

        uint32 rsaOffset = file_desc->file_size - RSA_SIGNATURE_SIZE;

        if ((rsaOffset > 0) && brom_ReadEFUSEAuthEnable())
        {
            uint8 *rxSignature = arch_start + rsaOffset;
            computedHashDigest=malloc(drv_HashGetDigestSize());
            REL_ASSERT(computedHashDigest != NULL);

            /* Compute archive hash now */
            drv_HashCtx hash_ctx;
            drv_HashBegin(&hash_ctx);
            drv_Hash(&hash_ctx, (void *) file_desc, file_desc->length);
            drv_Hash(&hash_ctx, (void *) arch_start, rsaOffset);
            drv_HashEnd(&hash_ctx, computedHashDigest);
            hash_digest = computedHashDigest;

            /* Get RSA sig */
            for (i = 0; i < RSA_SIGNATURE_SIZE; i++)
            {
                readRsa[i] = *rxSignature++;
            }
            rsa_sig = readRsa;

            /* Get Key ID */
            memcpy(&keyID, arch_start + (file_desc->file_size - KEY_ID_BYTE_LEN - NONCE_SIZE - RSA_SIGNATURE_SIZE), sizeof(int));
            key_id = &keyID;
        }
    }

    if (!brom_ReadEFUSEAuthEnable())
    {
        /* non secured chip - skip signature archive authentification */
        /* No need to finish SHA1 then */
        OS_UIST_SMARKER(DRVARCH_UIST_ID_AUTH_DISABLED);
        return 0;
    }

    REL_ASSERT(hash_digest != NULL);
    REL_ASSERT(rsa_sig != NULL);
    REL_ASSERT(key_id != NULL);

#if defined (USE_WHITELIST)
    drv_CheckChipIdInWhitelist();
#endif

    /* Check RSA against each key not explicitly disabled     */
    /* Use ICE-ICE public keys in ROM to check a BT2 archive  */
    /* Use ICE-OEM public keys to check other wrapped archive */
    /* Use OEM_FACT public keys to check data files           */
    if (GET_ARCH_ID(file_desc->file_id) == ARCH_ID_BT2)
    {
        uint8 invalid_keys = brom_ReadEFUSERSAKeyDisable();

        OS_UIST_SMARKER( DRVARCH_UIST_ID_ICE_ICE_AUTH );
        for (i = 0; i < BROM_NUM_RSA_KEYS; i++)
        {
            if (!(invalid_keys & 1))
            {
                ret = drv_HashRSAVerify(rsa_sig,
                                          hash_digest,
                                        brom_GetBt2KeyModulus() + i*RSA_MODULUS_SIZE,
                                        brom_GetBt2KeyExponent() + i*8);
                if(ret == 0)
                {
                    OS_UIST_SVALUE(DRVARCH_UIST_ID_ICE_ICE_AUTH_PASS, i);
                    result = 0;
                }
            }
            invalid_keys >>= 1;
        }
    }
    else
    {
        uint8 *pub_key_modulus;
        uint8 *pub_key_exponent;

        int arch_id = GET_ARCH_ID(file_desc->file_id);
        int entry = drv_archGetTableEntry(arch_id);

        if(entry < 0)
        {
            return -1;
        }

        switch (arch_type[entry].key_set)
        {
        case ARCH_ICE_OEM_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_ICE_OEM_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               ice_oem_keys,
                                               ICE_OEM_NUM_RSA_KEYS,
                                               ARCH_ICE_OEM_KEY_SET);
            break;

        case ARCH_OEM_FACT_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_OEM_FACT_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               oem_fact_keys,
                                               OEM_FACT_NUM_RSA_KEYS,
                                               ARCH_OEM_FACT_KEY_SET);
            break;

        case ARCH_ICE_FACT_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_ICE_FACT_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               ice_fact_keys,
                                               ICE_FACT_NUM_RSA_KEYS,
                                               ARCH_ICE_FACT_KEY_SET);
            break;

        case ARCH_ICE_DBG_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_ICE_DBG_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               ice_dbg_keys,
                                               ICE_DBG_NUM_RSA_KEYS,
                                               ARCH_ICE_DBG_KEY_SET);
            break;

        case ARCH_OEM_FIELD_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_OEM_FIELD_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               oem_field_keys,
                                               OEM_FIELD_NUM_RSA_KEYS,
                                               ARCH_OEM_FIELD_KEY_SET);
            break;

#if defined(ICERA_FEATURE_SOFT_ACTIVATION)
        case ARCH_ACT_ACT_KEY_SET:
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               act_act_keys,
                                               ACT_ACT_NUM_RSA_KEYS,
                                               ARCH_ACT_ACT_KEY_SET);
            break;
#endif

#ifdef EROBUSTA
        case ARCH_ICE_CFG_KEY_SET:
            OS_UIST_SMARKER( DRVARCH_UIST_ID_ICE_CFG_AUTH );
            result = drv_arch_GetPublicKeyInfo((uint8 *)key_id,
                                               (uint8 **)&pub_key_modulus,
                                               (uint8 **)&pub_key_exponent,
                                               ice_cfg_keys,
                                               ICE_CFG_NUM_RSA_KEYS,
                                               ARCH_ICE_CFG_KEY_SET);
            break;
#endif /* #ifdef EROBUSTA */

        default:
            OS_UIST_SMARKER( DRVARCH_UIST_INVALID_KEY_SET );
            break;
        }

        /* Check RSA against pub_key */
        if (result == 0)
        {
            ret = drv_HashRSAVerify(rsa_sig,
                                        hash_digest,
                                        pub_key_modulus,
                                    pub_key_exponent);
            if (ret == 0)
            {
                uint32 id;
                memcpy(&id, key_id, sizeof(int));
                OS_UIST_SVALUE( DRVARCH_UIST_ID_AUTH_PASS, id);
                result = 0;
            }
            else
            {
                OS_UIST_SVALUE( DRVARCH_UIST_ID_AUTH_FAIL, ret );
                result = -1;
            }
        }
        else
        {
            OS_UIST_SVALUE( DRVARCH_UIST_ID_AUTH_INDEX_BOUNDS, *key_id);
        }
    }

    if(computedHashDigest)
    {
        free(computedHashDigest);
    }

    return result;
}

int drv_arch_HeaderVerify( tAppliFileHeader * appl_hd, tZipAppliFileHeader * zip_appl_hd )
{
    int status = -1;

    int arch_id = GET_ARCH_ID(appl_hd->file_id);
    int arch_entry = drv_archGetTableEntry(arch_id);

    /* Consistency checks */
    if((appl_hd->tag == ARCH_TAG) || arch_type[arch_entry].ignore_magic)
    {
        if((arch_type[arch_entry].key_set != ARCH_NO_AUTH) &&
           (arch_type[arch_entry].key_set != ARCH_EXT_AUTH) &&
           (arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION))
        {
            if(appl_hd->file_size > (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN))
            {
                /**
                 * A signed file must contain at least a header, a signature
                 * (key_id + nonce +sha1/rsa sig) and 1 byte of data...
                 */
                status = 0;
            }
        }
        else if(appl_hd->file_size > 0)
        {
            /* An unsigned file must at least contain a header and 1 byte of data... */
            status = 0;
        }
    }

    if (GET_ARCH_ID(appl_hd->file_id) == ARCH_ID_BT2 &&
        appl_hd->entry_address != BT2_EXPECTED_START_ADDR)
    {
        status = -1;
    }

    if(zip_appl_hd)
    {
        if (GET_ZIP_MODE(appl_hd->file_id) > ZIP_MODE_LAST)
        {
            status = -1;
            OS_UIST_SVALUE( DRVARCH_UIST_ID_BAD_ZIP_MODE, GET_ZIP_MODE(appl_hd->file_id) );
        }

        /* Checking if the ZIP version is consistent when having a zip_appl_header */
        if ((ZIP_MODE_NONE != GET_ZIP_MODE(appl_hd->file_id)) )
        {
            switch(zip_appl_hd->zip_arch_ver)
            {
            case ZIP_ARCH_VER_1_0:
                OS_UIST_SVALUE( DRVARCH_UIST_ID_SUPPORTED_ZIP_VERSION, zip_appl_hd->zip_arch_ver );
                break;

            default:
                status = -1;
                OS_UIST_SVALUE( DRVARCH_UIST_ID_UNSUPPORTED_ZIP_VERSION, zip_appl_hd->zip_arch_ver );
            }
        }
    }

    if (status ==0)
    {
        uint32  checksum    = 0;
        uint32  *p          = (uint32*)appl_hd;
        int     header_size = appl_hd->length;

        while (header_size)
        {
            checksum ^= *p++;
            header_size -= sizeof(checksum);
        }

        status = checksum;                       /* 0 if correct */
    }

    return status;
}

int drv_archGetTableEntry(int arch_id)
{
    int i;
    int err = -1;

    for(i=0; i< arch_type_max_id; i++)
    {
        if(arch_type[i].arch_id == arch_id)
        {
            return i;
        }
    }

    return err;
}

const tArchFileProperty *drv_archGetArchProperties(uint32 arch_id)
{
    return (arch_id < arch_type_max_id) ? &arch_type[arch_id] : NULL;
}

uint32 drv_arch_GetMaxArchId(void)
{
    return arch_type_max_id;
}

ArchBt2HwplatCompat drv_archGetBt2TrailerFromFlash(ArchBt2ExtTrailer *bt2_ext_trailer)
{
    int ok = 0;
    tAppliFileHeader bt2_hdr;
    ArchBt2BootMap bt2_boot_map;
    int extended_trailer_offset;
    ArchBt2HwplatCompat result = ARCH_BT2_COMPAT_FLASH_TRAILER_NOT_FOUND;

    REL_ASSERT(bt2_ext_trailer != NULL);

    if (drv_ChpcGetBootMode() == 0)
    {
        /* External boot source... */
        return result;
    }

    do
    {
        /* Read BT2 header */
        ok = drv_FlashReadBt2Data((uint8 *)&bt2_hdr, 0, sizeof(bt2_hdr));
        if(!ok)
        {
            /* No valid header found. */
            result = ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE;
            break;
        }

        /* Check BT2 header before using length field... */
        if (drv_arch_HeaderVerify(&bt2_hdr,SKIP_ZIP_ARCH_CHECK) == 0)
        {
            /* Found valid header in flash
               Otherwise, means either 1st progranmming (empty flash) or BT2
               corruption: not a source of error...*/

            /* Read BT2 boot map */
            ok = drv_FlashReadBt2Data((uint8 *)&bt2_boot_map,
                                      bt2_hdr.length,
                                      sizeof(bt2_boot_map));
            if(!ok)
            {
                /* Valid header found but failure reading boot map... */
                result = ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE;
                break;
            }

            /* Read BT2 trailer magic & size */
            extended_trailer_offset = bt2_hdr.length + (bt2_boot_map.dmem_load_addr & ~0x40000000) + bt2_boot_map.imem_size;
            ok = drv_FlashReadBt2Data((uint8 *)bt2_ext_trailer,
                                      extended_trailer_offset,
                                      offsetof(ArchBt2ExtTrailer,data));
            if(!ok)
            {
                /* Valid header and valid boot map found but failure reading trailer infos */
                result = ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE;
                break;
            }

            if(bt2_ext_trailer->magic == ARCH_TAG_BT2_TRAILER)
            {
                /* Found trailer's magic in flash, let's read trailer data */
                bt2_ext_trailer->data = malloc(bt2_ext_trailer->size);
                REL_ASSERT(bt2_ext_trailer->data != NULL);
                ok = drv_FlashReadBt2Data(bt2_ext_trailer->data,
                                          extended_trailer_offset + offsetof(ArchBt2ExtTrailer,data),
                                          bt2_ext_trailer->size);
                if(!ok)
                {
                    /* Valid header, boot map and trailer infos but failure reading trailer data */
                    result = ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE;
                    break;
                }
                result = ARCH_BT2_COMPAT_NO_ERR;
            }
        }
    } while(0);

    return result;
}

ArchBt2HwplatCompat drv_archCheckBt2ExtendedTrailer(uint8 *arch_start)
{
    int extended_trailer_offset;
    ArchBt2ExtTrailer bt2_ext_trailer_from_flash, bt2_ext_trailer_in_ram;
    ArchBt2BootMap bt2_boot_map;
    ArchBt2HwplatCompat result = ARCH_BT2_COMPAT_NO_ERR;

    if (drv_ChpcGetBootMode() == 0)
    {
        /* We shouldn't call this function if external boot mode... */
        DEV_ASSERT(0);
    }

    do
    {
        /* Init both trailers to 0... */
        memset(&bt2_ext_trailer_from_flash, 0, sizeof(bt2_ext_trailer_from_flash));
        memset(&bt2_ext_trailer_in_ram, 0, sizeof(bt2_ext_trailer_in_ram));

        /* Get bt2 trailer from flash */
        result = drv_archGetBt2TrailerFromFlash(&bt2_ext_trailer_from_flash);

        if(result != ARCH_BT2_COMPAT_NO_ERR)
        {
            break;
        }

        /* Get boot map from BT2 archive in RAM */
        memcpy(&bt2_boot_map, arch_start, sizeof(bt2_boot_map));

        /* Get trailer's magic & size from BT2 archive in RAM */
        extended_trailer_offset = (bt2_boot_map.dmem_load_addr & ~0x40000000) + bt2_boot_map.imem_size;
        memcpy(&bt2_ext_trailer_in_ram, arch_start + extended_trailer_offset, offsetof(ArchBt2ExtTrailer,data));

        if(bt2_ext_trailer_in_ram.magic != ARCH_TAG_BT2_TRAILER)
        {
            /* No trailer in image to update, only allowed on dev. device. */
            if (brom_GetLivantoSecurityState() == SECURITY_STATE__PROD)
            {
                result = ARCH_BT2_COMPAT_NO_RAM_TRAILER;
            }
            break;
        }

        /* Found trailer's magic in RAM, let's read trailer data */
        bt2_ext_trailer_in_ram.data = malloc(bt2_ext_trailer_in_ram.size);
        REL_ASSERT(bt2_ext_trailer_in_ram.data != NULL);
        memcpy(bt2_ext_trailer_in_ram.data,
               arch_start + extended_trailer_offset + offsetof(ArchBt2ExtTrailer,data),
               bt2_ext_trailer_in_ram.size);

        /* We can now decode both trailers and perform comparison */
        ezxml_t dec_trailer_from_flash = ezxml_parse_str((char *)bt2_ext_trailer_from_flash.data, bt2_ext_trailer_from_flash.size);
        if(!dec_trailer_from_flash)
        {
            /* Trailer found invalid in flash... */
            result = ARCH_BT2_COMPAT_INVALID_FLASH_TRAILER;
            break;
        }

        ezxml_t dec_trailer_in_ram = ezxml_parse_str((char *)bt2_ext_trailer_in_ram.data, bt2_ext_trailer_in_ram.size);
        if(!dec_trailer_in_ram)
        {
            /* Trailer found invalid in RAM... */
            result = ARCH_BT2_COMPAT_INVALID_RAM_TRAILER;
            break;
        }

        /* Let's look for Hwplatform indication for each trailer */
        ezxml_t child;

        /* In flash...*/
        child = dec_trailer_from_flash->child;
        char *hwplat_in_flash = NULL;
        while((ezxml_t)(child->sibling))
        {
            if(strcmp(((ezxml_t)(child->sibling))->name,"compatibleHwPlatPattern") == 0)
            {
                /* Found sibling for compatibleHwPlatPattern in flash */
                hwplat_in_flash = ((ezxml_t)(child->sibling))->txt;
                break;
            }
        }
        if(!hwplat_in_flash)
        {
            /* Trailer found incomplete in flash... */
            result = ARCH_BT2_COMPAT_INCOMPLETE_FLASH_TRAILER;
            break;
        }

        /* In ram...*/
        child = dec_trailer_in_ram->child;
        char *hwplat_in_ram = NULL;
        while((ezxml_t)(child->sibling))
        {
            if(strcmp(((ezxml_t)(child->sibling))->name,"compatibleHwPlatPattern") == 0)
            {
                /* Found sibling for compatibleHwPlatPattern in flash */
                hwplat_in_ram = ((ezxml_t)(child->sibling))->txt;
                break;
            }
        }
        if(!hwplat_in_ram)
        {
            /* Trailer found incomplete in RAM... */
            result = ARCH_BT2_COMPAT_INCOMPLETE_RAM_TRAILER;
            break;
        }

        /* Let's check hwplatform compatibility */
        char *p = hwplat_in_flash; /* previous in flash */
        char *n = hwplat_in_ram;   /* new in RAM */
        while (*p && (*p != '*'))
        {
            if (*n != *p)
            {
                /* One character in new BT2 trailer in RAM differs from the one stored in flash... */
                result = ARCH_BT2_COMPAT_FAILURE;
                break;
            }
            p++;
            n++;
        }
    } while(0);

    /* Free resources... */
    if(bt2_ext_trailer_from_flash.data)
    {
        free(bt2_ext_trailer_from_flash.data);
    }
    if(bt2_ext_trailer_in_ram.data)
    {
        free(bt2_ext_trailer_in_ram.data);
    }

    return result;
}

ArchId drv_archGetRequiredModeFromNoninit(void)
{
#ifdef ICERA_FEATURE_EXTENDED_MODEM
    int fd, len;
    ArchId arch_id = ARCH_ID_APP; /* MDM appli is the default mode... */

    fd = drv_DbgFopen (DRV_DBG_APP_MODE, DRV_DBG_O_RDONLY, 0);
    if (fd == -1)
    {
        OS_UIST_SMARKER(DRV_ARCH_UIST_APP_MODE_NONINIT_KO);
    }
    else
    {
        /* APP mode info exists in noninit... */
        len = drv_DbgFread(fd, &arch_id, sizeof(ArchId));
        DEV_ASSERT_EXTRA(len == sizeof(ArchId), 2, len, sizeof(ArchId));
        drv_DbgFclose(fd);
        OS_UIST_SVALUE(DRV_ARCH_UIST_APP_MODE_NONINIT, arch_id);
    }

    return arch_id;
#else
    DEV_FAIL("Extended modem feature not activated.");
    return -1;
#endif
}

void drv_archSetRequiredModeToNoninit(ArchId arch_id)
{
#ifdef ICERA_FEATURE_EXTENDED_MODEM
    int fd, len;

    fd = drv_DbgFopen (DRV_DBG_APP_MODE, DRV_DBG_O_WRONLY, 0);
    if (fd == -1)
    {
        OS_UIST_SMARKER(DRV_ARCH_UIST_APP_MODE_NONINIT_STORE_KO);
    }
    else
    {
        /* Store required APP mode in noninit... */
        len = drv_DbgFwrite(fd, &arch_id, sizeof(ArchId));
        DEV_ASSERT_EXTRA(len == sizeof(ArchId), 2, len, sizeof(ArchId));
        drv_DbgFclose(fd);
        OS_UIST_SVALUE(DRV_ARCH_UIST_APP_MODE_NONINIT_STORE, arch_id);
    }

    return;
#else
    DEV_FAIL("Extended modem feature not activated.");
#endif
}

/** @} END OF FILE */
