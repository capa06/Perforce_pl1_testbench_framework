/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_loader.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_loader.c Loader AT command set for use in loader and modem
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_arch.h"
#include "os_uist_ids.h"
#include "drv_arch_cbc.h"
#include "drv_brom_iface.h"
#include "int_atci.h"
#include "drv_fs.h"
#include "asn1_api.h"

#include "int_ldr_atcmd.h"
#include "int_shared_atcmd.h"
#include "drv_arch_loader.h" /* some functions are common to modem and are in drv_arch */


/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

uint8 DXP_UNCACHED *file_storage_start = NULL;

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/
static int check_file_for_programming(tAppliFileHeader *dld_fh_ptr, uint8 *file_data,
                                      bool file_in_ram, uint8 *update_key_id, uint8 *file_hash,
                                      uint8 *file_signature, uint8 *file_ppid,
                                      void(*special_print)(const char*, ...))
{
    int err = NO_ERR;
    tZipAppliFileHeader * dld_zip_fh_ptr = NULL;

    int update_key_index = 0;

    PlatformConfig_t *plat_cfg = NULL;
    drv_ArchCbcStatus cbc_status;
    ExtendedHeader_t *ext_hdr = NULL;
    bool cross_boot_check_enabled = true;
    int arch_entry;

    arch_entry = drv_archGetTableEntry(GET_ARCH_ID(dld_fh_ptr->file_id));

    if(ZIP_MODE_NONE != GET_ZIP_MODE(dld_fh_ptr->file_id))
    {
        dld_zip_fh_ptr = (tZipAppliFileHeader *) (file_data) ;
    }
    if(drv_arch_HeaderVerify(dld_fh_ptr,dld_zip_fh_ptr) != 0)
    {
        special_print( "ARCH Header Consistency Check Failed" ATC_NEWLINE);
        OS_UIST_SMARKER( LDR_UIST_ID_DLD_ARCH_HDR_CHECK_FAILED );
        err = ERR;
    }

    /* Get CBC status from config data file */
    drv_ArchCheckCustomConfigFile(&cbc_status, GET_ARCH_ID(dld_fh_ptr->file_id));

    if(arch_type[arch_entry].key_set != ARCH_NO_AUTH)
    {
        if(arch_type[arch_entry].key_set == ARCH_EXT_AUTH)
        {
           /* External security mechanism must have been ran previously to the file update. */
           /* Here, it is only a status that's checked to allow or not file update. */
           if(drv_SecurityExtAuthGetState() != EXT_AUTH_UNLOCKED)
           {
               special_print( "ARCH External Authentication Failed" ATC_NEWLINE);
               OS_UIST_SMARKER( LDR_UIST_ID_DLD_ARCH_EXT_AUTH_FAILED );
               err = ERR;
           }
        }
        else
        {
            /* Check authenticity of the downloaded archive */
            /* Only SHA1-RSA signed archive are accepted */
            /* The key index of the downloaded application shall be higher than,
               or equal to the one of the current application */
            if(err == NO_ERR)
            {
                /* Get update key index */
                update_key_index = drv_arch_GetKeyIndex(GET_ARCH_ID(dld_fh_ptr->file_id), update_key_id);
                if(update_key_index == -1)
                {
                    /* We did not find any valid key to match with update key ID...*/
                    special_print( "Invalid key ID" ATC_NEWLINE);
                    OS_UIST_SMARKER(DRVARCH_UIST_INVALID_KEY_ID);
                    err = ERR;
                }
            }

            if(err == NO_ERR)
            {
                if(( (dld_fh_ptr->sign_type != ARCH_SIGN_TYPE__RSA) && (dld_fh_ptr->sign_type != ARCH_SIGN_TYPE__RSA2) ) ||
                   ( !drv_arch_CheckUpdateKeyValidity(GET_ARCH_ID(dld_fh_ptr->file_id), update_key_index, cbc_status.krm_enabled) ) ||
                   ( drv_arch_RSASignVerify(file_in_ram, file_in_ram ? file_data : NULL, dld_fh_ptr, file_hash, file_signature, file_in_ram ? NULL : ((uint32 *)update_key_id)) != 0 ))
                {
                    special_print( "ARCH RSA Authentication Failed" ATC_NEWLINE);
                    OS_UIST_SMARKER( LDR_UIST_ID_DLD_ARCH_AUTH_FAILED );
                    err = ERR;
                }
                else
                {
                    OS_UIST_SMARKER( LDR_UIST_ID_DLD_ARCH_AUTH_SUCCEEDED );
                }
            }
        }
    }

    /* Check public platform ID in file if required */
    if((err == NO_ERR) &&
       (arch_type[arch_entry].ppid_check ))
    {
        if(drv_arch_PPIDVerifyBuffer(file_ppid, arch_type[arch_entry].ppid_check) == -1)
        {
            special_print( "PPID Authentication Failed" ATC_NEWLINE);
            OS_UIST_SMARKER( LDR_UIST_ID_DLD_PPID_AUTH_FAILED );
            err = ERR;
        }
        else
        {
            OS_UIST_SMARKER( LDR_UIST_ID_DLD_PPID_AUTH_SUCCEEDED );
        }
    }


#if defined(ICERA_FEATURE_SECURE_CONFIG) && defined(ICERA_FEATURE_DOMAIN_AUTH)

    if ((err == NO_ERR) &&
        (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_SECCFG))
    {
        /* Initially assume failure */
        err = ERR;

        if (drv_SecuritySubmitResponseBinary(SEC_DOMAIN_SECCFG,
                file_data + (dld_fh_ptr->file_size - NONCE_SIZE - RSA_SIGNATURE_SIZE),
                NONCE_SIZE,
                update_key_index) == SEC_DOMAIN_NO_ERR)
        {
            if (drv_SecurityGetState(SEC_DOMAIN_SECCFG) == SEC_DOMAIN_AUTHENTICATED)
            {
                err = NO_ERR;
            }
        }

        if (err == ERR)
        {
            special_print( "ARCH Challenge Response Authentication Failed" ATC_NEWLINE);
            OS_UIST_SMARKER( LDR_UIST_ID_DLD_CR_AUTH_FAILED );
        }
        else
        {
            OS_UIST_SMARKER( LDR_UIST_ID_DLD_CR_AUTH_SUCCEEDED );
        }
        /* Regardless, clear the state */
        drv_SecurityClearState(SEC_DOMAIN_SECCFG);

    }

#endif

    /* Perform Cross Boot Check on firmware */
    /* For BT2, only check if firmware update is enabled. */
    /* 3 main steps during CBC:*/
    /* - check of customization file */
    /* - check of platform configuration file */
    /* - check of extended headers */
    if(( err == NO_ERR ) &&
       ( (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_APP ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_IFT ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_LDR ) ||
#ifdef ICERA_FEATURE_ZEROCD
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_MASS ) ||
#endif
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_BT2 ) ))
    {
        switch(cbc_status.value)
        {
        case CBC_DISABLED:
            special_print( "Cross Boot Check disabled on this platform." ATC_NEWLINE);
            cross_boot_check_enabled = false;
            break;
        case NO_FILE:
            special_print( "No customization file available." ATC_NEWLINE);
            err = ERR;
            break;

        case DEFAULT_VALUES:
            special_print( "Using default custom values" ATC_NEWLINE);
            break;

        case UPDATE_DISABLED:
            special_print( "Update is not allowed for this firmware." ATC_NEWLINE);
            err = ERR;
            break;

        case UPDATE_DISABLED_DEFAULT:
            special_print( "Using default custom values" ATC_NEWLINE);
            special_print( "Update is not allowed for this firmware." ATC_NEWLINE);
            err = ERR;
            break;

        default:
            break;
        }

        if(err == ERR)
        {
            special_print( "Cross Boot Check Failure" ATC_NEWLINE);
        }
    }

    if(( err == NO_ERR ) &&
       ( (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_APP ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_IFT ) ||
#ifdef ICERA_FEATURE_ZEROCD
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_MASS ) ||
#endif
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_LDR )) &&
       cross_boot_check_enabled)
    {
        plat_cfg = drv_ArchCheckPlatformConfigFile(&cbc_status);
        switch(cbc_status.value)
        {
        case NO_FILE:
            special_print( "No platform configuration available" ATC_NEWLINE);
            err = ERR;
            break;

        case DATA_INVALID:
            special_print( "Invalid platform configuration data" ATC_NEWLINE);
            err = ERR;
            break;

        default:
            break;

        }

        if(err == ERR)
        {
            special_print( "Cross Boot Check Failure" ATC_NEWLINE);
        }
    }

    if(( err == NO_ERR ) &&
       ( (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_APP ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_IFT ) ||
#ifdef ICERA_FEATURE_ZEROCD
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_MASS ) ||
#endif
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_LDR )) &&
       cross_boot_check_enabled)
    {
        ext_hdr = drv_ArchExtractExtendedHeaderFromHeader(dld_fh_ptr);
        if(ext_hdr == NULL)
        {
            special_print( "Invalid CBC header data" ATC_NEWLINE);
            err = ERR;
        }
        else
        {
            REL_ASSERT(plat_cfg != NULL);
            drv_ArchCheckFirmwareCompatibility(&cbc_status, ext_hdr, plat_cfg, GET_ARCH_ID(dld_fh_ptr->file_id));
            switch(cbc_status.value)
            {
            case VERSION_INVALID:
                if(brom_GetLivantoSecurityState() == SECURITY_STATE__DEV)
                {
                    /* Downgrade allowed on dev platform... */
                    special_print( "WARNING: Incompatible archive version (dev.)" ATC_NEWLINE);
                }
                else
                {
                    /*  We have to check if this is an unlocked platform */
                    if(!drv_UnlockedPlatform())
                    {
                        /* Downgrade forbidden on prod platform... */
                        special_print( "Incompatible archive version" ATC_NEWLINE);
                        err = ERR;
                    }
                    else
                    {
                        /* Downgrade allowed on unlocked prod platform... */
                        special_print( "WARNING: Incompatible archive version (prod.)" ATC_NEWLINE);
                    }
                }
                special_print( "Try to update %x with %x" ATC_NEWLINE,
                                   cbc_status.cur_version, cbc_status.new_version);
                break;

            case PLATFORM_INVALID:
                special_print( "Incompatible supported platform" ATC_NEWLINE);
                special_print( "Try to update with firmware built for %s" ATC_NEWLINE,
                                   ext_hdr->compatibleHwPlatPattern);
                err = ERR;
                break;

            default:
                err = NO_ERR;
                break;
            }
            cfg_FreeExtendedHeaderData(ext_hdr);
        }

        if(err == ERR)
        {
            special_print( "Cross Boot Check Failure" ATC_NEWLINE);
        }
        else
        {
            special_print( "Cross Boot Check Successful" ATC_NEWLINE);
        }
    }
    if(plat_cfg != NULL)
    {
        cfg_FreePlatformConfigData(plat_cfg);
    }

    /* Perform specific additional cross boot check for BT2: check extended trailer compatibility */
    int res;
    if(( err == NO_ERR ) &&  (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_BT2 ))
    {
        res = drv_archCheckBt2ExtendedTrailer(file_data);
        switch(res)
        {
        case ARCH_BT2_COMPAT_NO_ERR:
        case ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE:
        case ARCH_BT2_COMPAT_INVALID_FLASH_TRAILER:
        case ARCH_BT2_COMPAT_INCOMPLETE_FLASH_TRAILER:
        case ARCH_BT2_COMPAT_FLASH_TRAILER_NOT_FOUND:
            break;

        case ARCH_BT2_COMPAT_NO_RAM_TRAILER:
        case ARCH_BT2_COMPAT_INVALID_RAM_TRAILER:
        case ARCH_BT2_COMPAT_INCOMPLETE_RAM_TRAILER:
        case ARCH_BT2_COMPAT_FAILURE:
            err= ERR;
            special_print( "Incompatible BT2 version: %d" ATC_NEWLINE, res); //HLL this won't work quite right in MODEM mode
            break;

        default:
            DEV_FAIL_EXTRA("Unknown return value ", 1, res);
            break;
        }
    }

    /* Perform specific additional cross boot check for cust config files */
    if(( err == NO_ERR ) &&
       ( (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_CUSTCFG ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_DEVICECFG ) ||
         (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_PRODUCTCFG ) ))
    {
        res = drv_ArchCheckCustomConfigFileCompatibility(dld_fh_ptr, file_data);
        switch(res)
        {
        case ASN1_INVALID:
            special_print("ASN1 decode failure." ATC_NEWLINE);
            err = ERR;
            break;
        case PRODUCT_INVALID:
            special_print("Incompatible product." ATC_NEWLINE);
            err = ERR;
            break;
        default:
            break;
        }
    }

    if(err == NO_ERR)
    {
        if(arch_type[arch_entry].is_patch)
        {
            /* Apply patch */
            drv_archPatchHandler patch_cb = drv_arch_GetPatchHandler(GET_ARCH_ID(dld_fh_ptr->file_id));
            REL_ASSERT(patch_cb != NULL);
            err = patch_cb(dld_fh_ptr, file_data);
            if(err != NO_ERR)
            {
                special_print("File %s: fail to apply patch with error %d" ATC_NEWLINE, arch_type[arch_entry].acr, err);
            }
        }
    }
    return err;
}


static int program_from_ram(tAppliFileHeader *dld_fh_ptr, uint32 do_flash_update,
                            void(*special_print)(const char*, ...), void (*flashCB)(int))
{
    uint8 *file_data = file_storage_start;
    uint8 *update_key_id = NULL;
    int    err = NO_ERR;
    uint8 *ppid = NULL;
    int arch_entry;

    arch_entry = drv_archGetTableEntry(GET_ARCH_ID(dld_fh_ptr->file_id));

    if(arch_type[arch_entry].key_set != ARCH_NO_AUTH && arch_type[arch_entry].key_set != ARCH_EXT_AUTH &&
       arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION)
    {
        /* Retrieve update public key ID */
        DEV_ASSERT_EXTRA(dld_fh_ptr->file_size >= (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN), 1, dld_fh_ptr->file_size);
        update_key_id = file_data + (dld_fh_ptr->file_size - KEY_ID_BYTE_LEN - NONCE_SIZE - RSA_SIGNATURE_SIZE);
    }

    /* Check public chip ID in file if required */
    if(arch_type[arch_entry].ppid_check )
    {
        int ppid_offset;
        DEV_ASSERT_EXTRA(dld_fh_ptr->file_size >= (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN + SHA1_DIGEST_SIZE), 1, dld_fh_ptr->file_size);
        ppid_offset = dld_fh_ptr->file_size - RSA_SIGNATURE_SIZE - NONCE_SIZE - KEY_ID_BYTE_LEN - SHA1_DIGEST_SIZE;
        ppid = file_data + ppid_offset;
    }

    err = check_file_for_programming(dld_fh_ptr, file_data, true, update_key_id, NULL, NULL, ppid, special_print);

    if(err == NO_ERR && do_flash_update)
    {
        /* Flash update */
        if(!drv_arch_FlashWrite(dld_fh_ptr, file_storage_start, flashCB))
        {
            special_print("Fail to write file in flash" ATC_NEWLINE);
            OS_UIST_SMARKER( LDR_UIST_ID_FLASHWRITE_FAILED );
            err = ERR;
        }
        else
        {
            OS_UIST_SMARKER( LDR_UIST_ID_FLASHWRITE_PASSED );
        }
    }

    return err;
}

static void prog_info(void(*special_print)(const char*, ...), void (*flashCB)(int), int percent, const char *string)
{
    if (flashCB)
    {
        flashCB(percent);
    }
    else
    {
        special_print(string);
    }
}

static int program_from_flash(tAppliFileHeader *dld_fh_ptr, uint8 *update_key_id, uint8 *file_hash, uint8 *file_signature,
                              uint8 *file_ppid, uint8 *temp_buffer, size_t temp_buffer_size, uint32 do_flash_update,
                              void(*special_print)(const char*, ...), void (*flashCB)(int))
{
    char   arch_file_path_new[MAX_FILENAME_LENGTH];
    char   arch_file_path_old[MAX_FILENAME_LENGTH];
    uint32 file_data_required = 0;
    uint8  *file_data = NULL;
    char   *arch_file_path;
    int    err = NO_ERR;
    int    arch_entry;

    arch_entry = drv_archGetTableEntry(GET_ARCH_ID(dld_fh_ptr->file_id));

    arch_file_path = drv_arch_GetPathById(GET_ARCH_ID(dld_fh_ptr->file_id));
    strcpy(arch_file_path_new,arch_file_path);
    strcat(arch_file_path_new,".new");
    strcpy(arch_file_path_old,arch_file_path);
    strcat(arch_file_path_old,".old");

    if ((arch_type[arch_entry].is_patch) ||
#if defined(ICERA_FEATURE_SECURE_CONFIG) && defined(ICERA_FEATURE_DOMAIN_AUTH)
             (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_SECCFG) ||
#endif /* ICERA_FEATURE_SECURE_CONFIG and ICERA_FEATURE_DOMAIN_AUTH */
             (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_CUSTCFG ) ||
             (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_DEVICECFG ) ||
             (GET_ARCH_ID(dld_fh_ptr->file_id) == ARCH_ID_PRODUCTCFG ) )
    {
        /* For various reasons (security response, patch file, CBC) we need the whole file */
        file_data_required = dld_fh_ptr->file_size;
    }
    else if(ZIP_MODE_NONE != GET_ZIP_MODE(dld_fh_ptr->file_id))
    {
        DEV_ASSERT_EXTRA(dld_fh_ptr->file_size >= sizeof(tZipAppliFileHeader), 1, dld_fh_ptr->file_size);
        file_data_required = sizeof(tZipAppliFileHeader);
    }

    if (file_data_required <= temp_buffer_size)
    {
        file_data = temp_buffer;
    }
    else
    {
        file_data = calloc(file_data_required, 1);
    }

    if (file_data)
    {
        int fd = drv_fs_Open(arch_file_path_new, O_RDONLY, 0);
        if (fd != -1)
        {
            int res;

            res = drv_fs_Lseek(fd, dld_fh_ptr->length, SEEK_SET);
            DEV_ASSERT(res == dld_fh_ptr->length);

            /* Read required archive data. */
            res = drv_fs_Read(fd, file_data, file_data_required);
            DEV_ASSERT(res == file_data_required);

            drv_fs_Close(fd);
            err = check_file_for_programming(dld_fh_ptr, file_data, false, update_key_id, file_hash, file_signature, file_ppid, special_print);
        }
        else
        {
            special_print("No file to program" ATC_NEWLINE);
            err = ERR;
        }

        if (file_data != temp_buffer)
        {
            free(file_data);
        }
    }
    else
    {
        special_print("No buffer space for file" ATC_NEWLINE);
        err = ERR;
    }

    if (err == NO_ERR)
    {
        /* Flash update */
        if(do_flash_update)
        {
            prog_info(special_print, flashCB, 50, "Swapping the filenames over" ATC_NEWLINE);

            do
            {
                if ((-1==drv_fs_Rename(arch_file_path,arch_file_path_old)) &&
                        (!drv_arch_AllowedFirstFileProgramming(dld_fh_ptr->file_id)))
                {
                    /* This file cannot be programmed for the 1st time through
                     * this f/w update mechanism... */
                    prog_info(special_print, flashCB, 100, "Failed to rename old version" ATC_NEWLINE);
                    err = ERR;
                    break;
                }
                if (-1==drv_fs_Rename(arch_file_path_new,arch_file_path))
                {
                    /* If here, original file doesn't exits anymore... */
                    prog_info(special_print, flashCB, 100, "Failed to rename new version" ATC_NEWLINE);
                    err = ERR;
                    if (-1==drv_fs_Rename(arch_file_path_old,arch_file_path))
                    {
                        prog_info(special_print, flashCB, 100, "Panic - can't put old one back either" ATC_NEWLINE);
                    }
                    break;
                }
                prog_info(special_print, flashCB, 100, "All Done" ATC_NEWLINE);
            } while(0);
        }
        else
        {
            drv_fs_Remove(arch_file_path_new);
        }
    }
    return err;
}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
extern int drv_arch_perform_programming(tAppliFileHeader *dld_fh_ptr, bool in_flash, bool check_even_in_flash,
                                        uint8 *update_key_id, uint8 *file_hash, uint8 *file_signature,
                                        uint8 *file_ppid, uint8 *temp_buffer, size_t temp_buffer_size,
                                        uint32 do_flash_update, void(*special_print)(const char*, ...),
                                        void (*flashCB)(int))
{
    int err = NO_ERR;

    /* No progress updates required  */
    if (do_flash_update == 1)
    {
        flashCB = NULL;
    }

    if(in_flash)
    {
        if(check_even_in_flash)
        {
            err = program_from_flash(dld_fh_ptr, update_key_id, file_hash, file_signature, file_ppid,
                                     temp_buffer, temp_buffer_size, do_flash_update, special_print, flashCB);
        }
        else
        {
            /* !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING!
             * FOR THE MOMENT NO AUTHENTICATION AT ALL ON THE ZEROCD ARCH WHEN THE ARCH IS FLUSHED IN FLASH
             * Only non-zerocd archives are authenticated - this is used for "loader in modem mode"
             * !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING! !WARNING!
             */
            OS_UIST_SMARKER( LDR_UIST_ID_FLASHWRITE_PASSED );
            err = NO_ERR;
        }
    }
    else
    {
        err = program_from_ram(dld_fh_ptr, do_flash_update, special_print, flashCB);
    }
    return err;
}

//#if defined (ICERA_FEATURE_INTERNAL)
/**
 * Handler for %NVDEL AT command.
 *
 * @param at_cmd  A pointer on the AT command descriptor.
 *
 * @return int
 */
extern int drv_arch_nverase(bool eraseSimLockFile)
{
            /* Remove all files from /data/modem directory
               (where TTP-NVRAM files are actually stored) */

            FactoryData_t *data;
            int status = ERR;

            struct drv_fs_Stat s;
            int res;

            /* Remove Data/modem content */
            drv_fs_RmDirContent(DRV_FS_DATA_MODEM_DIR_NAME);

            /* Remove personalisation file if requested */
            if(eraseSimLockFile == true)
            {
                res = drv_fs_Lstat(DRV_FS_DATA_PERSISTENT_DIR_NAME"/NRAM2_ME_PERSONALISATION.bin", &s);
                if (res == 0)
                {
                    res = drv_fs_Remove(DRV_FS_DATA_PERSISTENT_DIR_NAME"/NRAM2_ME_PERSONALISATION.bin");
                    DEV_ASSERT(res >= 0);
                }
            }

            /* remove also nvram_rw.bin file */
            res = drv_fs_Lstat(NVRAM_RW_FILE, &s);
            if (res == 0)
            {
                res = drv_fs_Remove(NVRAM_RW_FILE);
                DEV_ASSERT(res >= 0);
            }

            /* clear fullcoredumpSetting field from ft_data.bin */
            if (cfg_GetFactoryData(&data) > 0)
            {
                data->fullcoredumpSetting = FULL_COREDUMP_UNDEFINED;
                if (!cfg_SetFactoryData(data))
                {
                    status = ERR;
                }
            }
            cfg_FreeFactoryData(data);

            status = NO_ERR;

    return status;

}
//#endif
/** @} END OF FILE */
