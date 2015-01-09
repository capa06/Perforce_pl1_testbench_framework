/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_cbc.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_cbc.c Cross Boot Check utilities
 *
 */

/*************************************************************************************************
 *  Project header files. The first in this list should always be the public interface for this
 *  file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"

#include "hwplatform.h"
#include "drv_arch.h"
#include "drv_arch_local.h"
#include "drv_fs.h"
#include "drv_arch_cbc.h"
#include "os_uist_ids.h"
#if defined(ICERA_FEATURE_REMOTE_FS) || defined(DRV_PLATCFG_FROM_NONINIT)
#include "drv_dbg_noninit.h" /** drv_DbgFopen, DRV_DBG_PLAT_CFG_BUF_SIZE,... */
#include "drv_mphal_nk_if.h" /** drv_InExternalDebugMode */
#endif

/*************************************************************************************************
 *  Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <stdio.h>

/*************************************************************************************************
 *  Private Macros
 ************************************************************************************************/

/*************************************************************************************************
 *  Private type definitions
 ************************************************************************************************/

/*************************************************************************************************
 *  Private function declarations
 ************************************************************************************************/

/*************************************************************************************************
 *  Private variable definitions
 ************************************************************************************************/

#if defined(ICERA_FEATURE_REMOTE_FS) || defined(DRV_PLATCFG_FROM_NONINIT)
/** On platforms using remote file system, hwplatform
 *  information is needed for some I/O init prior to host
 *  interface initialization required for remote file system
 *  access.
 *
 *  In general, this info will be provided to BT2 responsible
 *  for storing it in noninit.
 *
 *  Since BT2 copy in noninit is not done when using dxp-run,
 *  there's the possibility to provide content of a platform
 *  config file to modem application with:
 *  "set_plat_config <plat_conf_str>" tcl procedure.
 */

/** Memory area populated with "set_plat_config <plat_conf_str>" tcl procedure */
DXP_UNCACHED char dxp_run_platform_config[DRV_DBG_PLAT_CFG_BUF_SIZE]= "";
#endif /* #ifdef ICERA_FEATURE_REMOTE_FS */

/*************************************************************************************************
 *  Public variable definitions
 ************************************************************************************************/

/************************************************************************************************
 *  Private function definitions
 ************************************************************************************************/

/************************************************************************************************
 *  Public function definitions
 ************************************************************************************************/

extern PlatformConfig_t * drv_ArchGetRfmBoardConfig(void)
{
    PlatformConfig_t * plat_conf = NULL;
    struct drv_fs_Stat s;

    /* If file exists */
    if (drv_fs_Lstat(RFM_PLAT_CFG_FILE, &s) >= 0)
    {
        /* Try and open RFM board name file from FS */
        plat_conf = cfg_GetPlatformConfigData(RFM_PLAT_CFG_FILE);
        if (plat_conf)
        {
            /* Only one field of interest in the RFM module's platcfg */
            if (plat_conf->rfPlat == NULL)
            {
                drv_ArchFreePlatformConfigFile(plat_conf);
                plat_conf = NULL;
            }
        }
    }

    return plat_conf;
}

extern PlatformConfig_t * drv_ArchCheckPlatformConfigFile(drv_ArchCbcStatus *status)
{
    PlatformConfig_t *plat_conf = NULL;
    status->value = DEFAULT_OK;

    do
    {
#if !defined(ICERA_FEATURE_REMOTE_FS) && !defined(DRV_PLATCFG_FROM_NONINIT)
        int res;
        struct drv_fs_Stat s;

        /* Check PLATFORM_CONFIG_FILE content in file system */
        res = drv_fs_Lstat(PLATFORM_CONFIG_FILE, &s);
        if (res == -1)
        {
            status->value = NO_FILE;
            break;
        }

        /* Decode  PLATFORM_CONFIG_FILE data */
        plat_conf = cfg_GetPlatformConfigData(PLATFORM_CONFIG_FILE);
        if (plat_conf == NULL)
        {
            status->value = DATA_INVALID;
            break;
        }

/* EEPROM attached to baseband - must be a RF module based system */
#if defined (USE_EEPROM_CAL_STORAGE)
        /* Extended platform config format */
        if (plat_conf->bbPlat)
        {
            /* Read RFM board platform file */
            PlatformConfig_t *rfplat_conf = drv_ArchGetRfmBoardConfig();
            if (rfplat_conf)
            {
                if(strlen(rfplat_conf->rfPlat))
                {
                    /* rfPlat not empty in RFM, cat bbPlat & RFM board name from FS to replace hwPlat */
                    REL_ASSERT(plat_conf->hwPlat != NULL);
                    free(plat_conf->hwPlat);

                    int new_str_len = strlen(plat_conf->bbPlat) + strlen("-") + strlen(rfplat_conf->rfPlat);
                    plat_conf->hwPlat = malloc(new_str_len + 1);
                    REL_ASSERT(plat_conf->hwPlat != NULL);

                    /* Form new platform config name from RFM module file (from EEPROM) & bbPlat from platformConfig */
                    strcpy(plat_conf->hwPlat, plat_conf->bbPlat);
                    strcat(plat_conf->hwPlat, "-");
                    strcat(plat_conf->hwPlat, rfplat_conf->rfPlat);
                }

                drv_ArchFreePlatformConfigFile(rfplat_conf);
            }
        }
#endif

#else
        int fd, len, plat_len=0, from_noninit=1;
        char *plat_conf_buffer = NULL;
        char *plat_conf_buffer_for_asn1;

        /* Look for platform config in this order:
           - dxp-run override
           - noninit */

        if(drv_InExternalDebugMode())
        {
            /* Check if dxp_run_platform_config has been updated */
            plat_len = strlen(dxp_run_platform_config);
            if(plat_len > 0)
            {
                plat_conf_buffer = dxp_run_platform_config;
                from_noninit = 0;
                OS_UIST_SMARKER(DRV_ARCH_UIST_PLAT_CFG_NONINIT_DBG);
            }
        }

        if(!plat_conf_buffer)
        {
            /* Check if platform config is found in noninit */
            fd = drv_DbgFopen (DRV_DBG_PLAT_CFG, DRV_DBG_O_RDONLY, 0);
            if (fd == -1)
            {
                OS_UIST_SMARKER(DRV_ARCH_UIST_PLAT_CFG_NONINIT_KO);
            }
            else
            {
                /* Plat config info exists in noninit... */
                plat_len = drv_DbgFGetfilesize(DRV_DBG_PLAT_CFG);
                /* Read plat cfg buffer */
                plat_conf_buffer = calloc(1, plat_len);
                REL_ASSERT(plat_conf_buffer != NULL);
                len = drv_DbgFread(fd, plat_conf_buffer, plat_len);
                DEV_ASSERT(len == plat_len);
                drv_DbgFclose(fd);
                OS_UIST_SMARKER(DRV_ARCH_UIST_PLAT_CFG_NONINIT);
            }
        }

        if(!plat_conf_buffer)
        {
            status->value = NO_FILE;
        }
        else
        {
            /** check if it is a buffer of XML data or old scheme with
             *  ONLY hwplat_value from <hwplat>hwplat_value</hwplat>  */
            plat_conf_buffer_for_asn1 = malloc(plat_len+1);
            REL_ASSERT(plat_conf_buffer_for_asn1 != NULL);
            memcpy(plat_conf_buffer_for_asn1, plat_conf_buffer, plat_len);
            plat_conf_buffer_for_asn1[plat_len] = 0;
            plat_conf = cfg_GetPlatformConfigDataFromBuffer(plat_conf_buffer_for_asn1, plat_len);
            free(plat_conf_buffer_for_asn1);
            if(!plat_conf)
            {
                /* old scheme */
                plat_conf = calloc(1, sizeof(*plat_conf));
                REL_ASSERT(plat_conf != NULL);
                plat_conf->hwPlat = malloc(plat_len + 1);
                REL_ASSERT(plat_conf->hwPlat != NULL);
                strncpy(plat_conf->hwPlat, plat_conf_buffer, plat_len);
                plat_conf->hwPlat[plat_len] = 0;
            }
            if(from_noninit)
            {
                free(plat_conf_buffer);
            }

            /** Extended platform config format */
            if ((plat_conf->bbPlat) && (plat_conf->rfPlat))
            {
                /** Form new platform config name from rfPlat & bbPlat to
                 *  replace hwPlat. If no rfPlat data, keep hwPlat as is */
                if(strlen(plat_conf->rfPlat))
                {
                    int new_str_len = strlen(plat_conf->bbPlat) + strlen("-") + strlen(plat_conf->rfPlat);

                    /* realloc existing hwPlat if required */
                    REL_ASSERT(plat_conf->hwPlat != NULL);
                    if(strlen(plat_conf->hwPlat) < new_str_len)
                    {
                        free(plat_conf->hwPlat);
                        plat_conf->hwPlat = malloc(new_str_len + 1);
                        REL_ASSERT(plat_conf->hwPlat != NULL);
                    }

                    /* form new hwPlat */
                    strcpy(plat_conf->hwPlat, plat_conf->bbPlat);
                    strcat(plat_conf->hwPlat, "-");
                    strcat(plat_conf->hwPlat, plat_conf->rfPlat);
                }
            }
        }
#endif /* !defined(ICERA_FEATURE_REMOTE_FS) && !defined(DRV_PLATCFG_FROM_NONINIT) */
    } while (0);

    return plat_conf;
}

extern void drv_ArchFreePlatformConfigFile(PlatformConfig_t *plat_conf)
{
    if (plat_conf != NULL)
    {
        cfg_FreePlatformConfigData(plat_conf);
        plat_conf = NULL;
    }
}

extern void drv_ArchCheckCustomConfigFile(drv_ArchCbcStatus *status, int file_id)
{
    CbcConfig_t* cbcConfig;
    bool update_enable = false;
    status->value = DEFAULT_OK;
    status->krm_enabled   = true;

    do
    {
        cbcConfig = cfg_GetCbcConfig(NULL, 0);

        /* Check CUSTOMER_CONFIG_FILE existence */
        if (cbcConfig->status == NOT_PRESENT)
        {
            status->value = NO_FILE;
            break;
        }

        /* Get key revocation mechanism status */
        status->krm_enabled = cbcConfig->keyRevocationEnable;

        /* Check if Cross Boot Check Is Enabled */
        if( ! (cbcConfig->crossBootCheckEnable) )
        {
            status->value = CBC_DISABLED;
            break;
        }

        if (cbcConfig->status == FROM_DEFAULT)
        {
            status->value = DEFAULT_VALUES;
        }

        /* Check firmware update flag */
        switch (file_id)
        {
        case ARCH_ID_APP:
            update_enable = cbcConfig->appliUpdateEnable;
            break;
        case ARCH_ID_BT2:
            update_enable = cbcConfig->secondaryBootUpdateEnable;
            break;
        case ARCH_ID_IFT:
            update_enable = cbcConfig->factoryTestsUpdateEnable;
            break;
        case ARCH_ID_LDR:
            update_enable = cbcConfig->loaderUpdateEnable;
            break;
        case ARCH_ID_MASS:
        default:
            break;
        }
        if ((!update_enable) && (status->value == DEFAULT_VALUES))
        {
            status->value = UPDATE_DISABLED_DEFAULT;
        }
        if ((!update_enable) && (status->value == DEFAULT_OK))
        {
            status->value = UPDATE_DISABLED;
        }
    } while (0);

    /* free resources */
    cfg_FreeCbcConfig(cbcConfig);

    return;
}

extern ExtendedHeader_t * drv_ArchExtractExtendedHeaderFromHeader(tAppliFileHeader *arch_hdr_ptr)
{
    ExtendedHeader_t * ext_hdr=NULL;
    int ext_hdr_len;

    char *ext_hdr_buf = NULL;

    /* Decode extended header data */
    ext_hdr_len  = arch_hdr_ptr->length - ARCH_HEADER_BYTE_LEN;
    DEV_ASSERT(ext_hdr_len > 0);
    ext_hdr_buf = (char *)arch_hdr_ptr + ARCH_HEADER_BYTE_LEN;
    ext_hdr = cfg_GetExtendedHeaderData(ext_hdr_buf, ext_hdr_len);

    return ext_hdr;
}

extern ExtendedHeader_t * drv_ArchExtractExtendedHeaderFromWrapped(char *wrapped_name)
{
    int fd;
    int ext_hdr_len;
    ExtendedHeader_t *ext_hdr = NULL;
    char *ext_hdr_buf = NULL;

#ifdef ICERA_FEATURE_REMOTE_FS
    ArchId id, current_id=-1;
    int bytes_read;

    /* Extended header of running appli may be stored in noninit... */

    /* 1st check we're considering running appli */
    id = drv_arch_GetIdByPath(wrapped_name);
    if(IS_MODEM_FIRMWARE())
    {
        current_id = ARCH_ID_APP;
    }
    else if(IS_BT3_FIRMWARE())
    {
        current_id = ARCH_ID_BT3;
    }
    else
    {
        DEV_FAIL("Non supported running appli");
    }
    DEV_ASSERT_EXTRA(id == current_id, 2, id, current_id);

    fd = drv_DbgFopen (DRV_DBG_EXT_HDR, DRV_DBG_O_RDONLY, 0);
    if(fd != -1)
    {
        /* File exists in noninit: read extended header data */
        ext_hdr_len = drv_DbgFGetfilesize(DRV_DBG_EXT_HDR);
        ext_hdr_buf = malloc(ext_hdr_len);
        REL_ASSERT(ext_hdr_buf != NULL);

        bytes_read = drv_DbgFread(fd, ext_hdr_buf, ext_hdr_len);
        DEV_ASSERT_EXTRA(bytes_read == ext_hdr_len, 2, bytes_read, ext_hdr_len);
        drv_DbgFclose(fd);

        /* Decode extended header data */
        ext_hdr     = cfg_GetExtendedHeaderData(ext_hdr_buf, ext_hdr_len);
        free(ext_hdr_buf);
    }
#else
    /* Decode data from both the current and the new extended header */
    tAppliFileHeader *arch_start = NULL;
    int res;
    fd = drv_fs_Open(wrapped_name, O_RDONLY, 0);
    if (fd >= 0)
    {
        /*Allocate buffer for header and extended header reading */
        /* sizeof(tAppliFileHeader) is always >= (ARCH_HEADER_BYTE_LEN + extended_header_len) */
        /* it is checked when building archive */
        arch_start = calloc(1, sizeof(tAppliFileHeader));
        REL_ASSERT(arch_start != NULL);

        do
        {
            /* Read archive header */
            res = drv_arch_ReadHeader(arch_start, fd);
            if(res == 0)
            {
                break;
            }

            /* Decode extended header data if it is there */
            ext_hdr_len = arch_start->length - ARCH_HEADER_BYTE_LEN;
            if (ext_hdr_len)
            {
                ext_hdr_buf = (char *)arch_start + ARCH_HEADER_BYTE_LEN;
                ext_hdr     = cfg_GetExtendedHeaderData(ext_hdr_buf, ext_hdr_len);
            }
        }
        while (0);

        free(arch_start);
        drv_fs_Close(fd);
    }
#endif

    return ext_hdr;
}

extern void drv_ArchCheckFirmwareCompatibility(drv_ArchCbcStatus *status, ExtendedHeader_t *new_ext_hdr, PlatformConfig_t * platConf, int file_id)
{
    ExtendedHeader_t *current_ext_hdr = NULL;
    char *p;
    char *n;

    /* Decode data from both the current and the new extra header */

    status->value = DEFAULT_OK;

    /* Perform hardware compatibility check */
    if ((!platConf->hwPlat) ||
        (strlen(platConf->hwPlat) < 1) ||
        (!new_ext_hdr->compatibleHwPlatPattern) ||
        (strlen(new_ext_hdr->compatibleHwPlatPattern) < 1))
    {
        status->value = PLATFORM_INVALID;
    }
    else
    {
        p = (char *)platConf->hwPlat;
        n = (char *)new_ext_hdr->compatibleHwPlatPattern;

        while (*p && (*n != '*'))
        {
            if (*n != *p)
            {
                status->value = PLATFORM_INVALID;
                break;
            }
            p++;
            n++;
        }
    }

    if(status->value == DEFAULT_OK)
    {
        /* Perforn version number compatibility check */
        current_ext_hdr = drv_ArchExtractExtendedHeaderFromWrapped(drv_arch_GetPathById(file_id));
        if(current_ext_hdr)
        {
            if (new_ext_hdr->versionNumber < current_ext_hdr->versionNumber)
            {
                status->value = VERSION_INVALID;
                status->cur_version = current_ext_hdr->versionNumber;
                status->new_version = new_ext_hdr->versionNumber;
            }
            cfg_FreeExtendedHeaderData(current_ext_hdr);
        }
    }

    return;
}


extern drv_ArchCbcResult drv_ArchCheckCustomConfigFileCompatibility(tAppliFileHeader *arch_hdr, uint8 *data)
{
    drv_ArchCbcResult ret = DEFAULT_OK;
    CbcConfig_t *from_flash = NULL, *to_flash=NULL;
    uint8 *p, *n;

    do
    {
        /* Get custom config data from flash file system */
        from_flash = cfg_GetCbcConfig(NULL, 0);
        if(from_flash->product == NULL)
        {
            /* Either no flag set by file owner: check OK
            or no flag because old file: check OK */
            OS_UIST_SMARKER(DRV_ARCH_UIST_NO_PRODUCT_FLAG);
            break;
        }

        /* Get custom config data from buffer to put in flash file system */
        to_flash = cfg_GetCbcConfig((char *)data, arch_hdr->file_size);
        if(!to_flash)
        {
            /* Fail to decode asn1 from this buffer: check fail... */
            ret = ASN1_INVALID;
            break;
        }

        /* Check if this file was encoded with any crossbootCheck info:
        looking specifically for to_flash->crossBootCheck->compatibleProduct->buf */
        int compat_prod = 0;

        if(to_flash->compatibleProduct)
        {
            compat_prod = 1;
        }

        if(!compat_prod)
        {
            /* No compatibleProduct flag found: check is OK.
            It is file owner responsability to force compatibility check or not... */
            OS_UIST_SMARKER(DRV_ARCH_UIST_NO_COMPATIBLE_PRODUCT_FLAG);
            break;
        }

        /* Perform compatibility check */
        p = (uint8 *)from_flash->product;
        n = (uint8 *)to_flash->compatibleProduct;

        if( *p == '*' )
        {
            /* This is default value from flash: check is OK */
            OS_UIST_SMARKER(DRV_ARCH_UIST_DEFAULT_PRODUCT);
            break;
        }

        while (*p && (*n != '*') && *n)
        {
            if (*n != *p)
            {
                ret = PRODUCT_INVALID;
                break;
            }
            p++;
            n++;
        }
    } while (0);

    /* Free resources... */
    cfg_FreeCbcConfig(from_flash);
    cfg_FreeCbcConfig(to_flash);

    return ret;
}
/** @} END OF FILE */
