/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_utils.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_utils.c Archive file utilities
 *
 * ...
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_security.h"
#include "drv_arch.h"
#include "drv_arch_local.h"
#include "os_uist_ids.h"
#include "drv_arch_pubk.h"
#include "drv_security.h"
#include "drv_fs.h"
#include "drv_chpc.h"
#include "drv_nvram.h"
#include "drv_flash.h"
#ifdef USE_NAND
#include "drv_nand_flash.h"
#endif
#include "drv_brom_iface.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include <string.h>
#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>

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

static DXP_UNCACHED char *ArchPath[] =
{
    [ARCH_ID_APP]          = MDM_APPLICATION_FILE
    ,[ARCH_ID_BT2]         = BT2_APPLICATION_FILE
    ,[ARCH_ID_IFT]         = IFT_APPLICATION_FILE
    ,[ARCH_ID_LDR]         = LDR_APPLICATION_FILE
    ,[ARCH_ID_IMEI]        = SECURED_IMEI_FILE
    ,[ARCH_ID_CUSTCFG]     = CUSTOMER_CONFIG_FILE
    ,[ARCH_ID_ZEROCD]      = ZEROCD_MASS0_FILE
    ,[ARCH_ID_MASS]        = MAS_APPLICATION_FILE
    ,[ARCH_ID_AUDIOCFG]    = AUDIO_CONFIG_FILE
    ,[ARCH_ID_COMPAT]      = COMPATIBILITY_FILE
    ,[ARCH_ID_PLATCFG]     = PLATFORM_CONFIG_FILE
    ,[ARCH_ID_SECCFG]      = SECURE_CONFIG_FILE
    ,[ARCH_ID_UNLOCK]      = UNLOCK_FILE
    ,[ARCH_ID_CALIB]       = CALIBRATION_0_FILE
    ,[ARCH_ID_CALIB_PATCH] = NULL
    ,[ARCH_ID_SSL_CERT]    = NULL
    ,[ARCH_ID_DEVICECFG]   = DEVICE_CONFIG_FILE
    ,[ARCH_ID_PRODUCTCFG]  = PRODUCT_CONFIG_FILE
    ,[ARCH_ID_ROBCOUNTER]  = NULL
    ,[ARCH_ID_FLASHDISK]   = MASS_STORAGE_FLASH_DISK_FILE
	,[ARCH_ID_WEBUI_PACKAGE]   = NULL
	,[ARCH_ID_BT3]         = NULL
    ,[ARCH_ID_ACT]         = ACT_APPLICATION_FILE
	,[ARCH_ID_ACT_DATA]    = ACTIVATE_DATA_FILE

};

static DXP_UNCACHED uint32 ArchPathMaxNum = sizeof(ArchPath)/sizeof(char *);

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/
static int GetKeyIndex(unsigned char *key_id,
                       const RsaPublicKey *pubkey_table,
                       int num_of_keys)
{
    int i, j, res = 0;
    int key_index = -1;

    for (i = 0; i < num_of_keys; i++)
    {
        /* For each public key in table, compare 4 1st bytes with key_id  */
        for (j = 0; j< KEY_ID_BYTE_LEN; j++)
        {
            if (*(key_id + j) != pubkey_table[i].rsa_modulus[j])
            {
                /* No need to continue after a wrong comparison */
                break;
            }
            else
            {
                if(j == (KEY_ID_BYTE_LEN -1))
                {
                    res = 1;
                    /* No need to continue after a good comparison */
                    break;
                }
            }
        }
        if (res)
        {
            key_index = i;
            /* Found the key ID, no need to continue */
            break;
        }
    }

    return key_index;
}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
#ifdef ICERA_FEATURE_REMOTE_FS
ArchId drv_arch_GetIdByPath(char *path)
{
    ArchId id = -1;
    int i;

    for(i = 0; i < arch_type_max_id; i++)
    {
        if(strcmp(path, ArchPath[i]) == 0)
        {
            id = i;
            break;
        }
    }

    return id;
}
#endif /* #ifdef ICERA_FEATURE_REMOTE_FS */

char *drv_arch_GetPathById(ArchId arch_id)
{
    /** Simply returns ArchPath table entry: NULL or
     *  initialised... */
    return ArchPath[arch_id];
}

int drv_arch_CalIsAvailable(void)
{
    int ok = 1;
    drv_NvramRoSegmentInfo *seg_info;

    seg_info = drv_NvramRoGetSegmentInfo(0);
    if (seg_info->state != DRV_NVRAM_RO_SEGMENT_STATE__OK)
    {
        seg_info = drv_NvramRoGetSegmentInfo(1);
        if (seg_info->state != DRV_NVRAM_RO_SEGMENT_STATE__OK)
        {
            ok = 0;
        }
    }

    return ok;
}

uint32 drv_arch_GetLastSignatureWord( uint32 arch_id )
{
    tAppliFileHeader    file_header;
    uint32              last_signature_word = 0;
    uint32              result;

    memset(&file_header, 0, sizeof(tAppliFileHeader));

    if (arch_id == ARCH_ID_BT2)
    {
        if (drv_ChpcGetBootMode() == 0)
        {
            return 0xA0A0A0A0;
        }

        do
        {
            /* Read BT2 header */
            int ok = drv_FlashReadBt2Data((uint8 *)&file_header, 0, sizeof(file_header));
            if(!ok)
            {
                /* No valid header found. */
                break;
            }

            /* Check BT2 header before using length field... */
            if (drv_arch_HeaderVerify(&file_header,SKIP_ZIP_ARCH_CHECK) == 0)
            {
                ok = drv_FlashReadBt2Data((uint8 *)&last_signature_word,
                                          file_header.length + file_header.file_size - sizeof(uint32),
                                          sizeof(uint32));
                if(!ok)
                {
                   last_signature_word = 0;
                }
            }
        } while(0);
    }
    else
    {
        int fd = drv_fs_Open(drv_arch_GetPathById(arch_id), O_RDONLY, 0);

        if (fd >= 0)
        {
            if( (drv_fs_Lgetsize(fd)) <= (sizeof(file_header)) )
            {
               last_signature_word = 0;
            }
            else
            {
                /* Read archive header */
                result = drv_arch_ReadHeader(&file_header, fd);
                if (result)
                {
                    if (drv_arch_HeaderVerify(&file_header,SKIP_ZIP_ARCH_CHECK) == 0)
                    {
                        /* read RSA signature */
                        drv_fs_Lseek(fd, file_header.file_size + file_header.length - sizeof(uint32), SEEK_SET);
                        int bytes_read = drv_fs_Read(fd, (char *)&last_signature_word, sizeof(uint32));
                        if (bytes_read != sizeof(uint32))
                        {
                            last_signature_word = 0;
                        }
                    }
                }
                else
                {
                    last_signature_word = 0xdeadbeef;
                }
            }
            drv_fs_Close(fd);
        }
    }

    /* turn to big endian */
    result   = ((last_signature_word & 0xFF) << 24);
    last_signature_word >>= 8;
    result  |= ((last_signature_word & 0xFF) << 16);
    last_signature_word >>= 8;
    result  |= ((last_signature_word & 0xFF) <<  8);
    last_signature_word >>= 8;
    result  |= ((last_signature_word & 0xFF) <<  0);

    return result;
}

int drv_arch_PPIDVerify( uint8 * arch_start, tAppliFileHeader * file_desc)
{
    unsigned char *arch_platform_id;
    int ppid_offset;

    /* Retreive public platform ID in file... */
    DEV_ASSERT_EXTRA(file_desc->file_size >= (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN + SHA1_DIGEST_SIZE), 1, file_desc->file_size);
    ppid_offset = file_desc->file_size - RSA_SIGNATURE_SIZE - NONCE_SIZE - KEY_ID_BYTE_LEN - SHA1_DIGEST_SIZE;
    arch_platform_id = arch_start + ppid_offset;

    /* ...and check with platform one...*/
    int arch_entry = drv_archGetTableEntry(GET_ARCH_ID(file_desc->file_id));
    return drv_arch_PPIDVerifyBuffer(arch_platform_id, arch_type[arch_entry].ppid_check);
}

int drv_arch_PPIDVerifyBuffer( uint8 *ppid, tArchPpidType type)
{
    unsigned char public_platform_id[SHA1_DIGEST_SIZE];

    if (drv_IsFuseIdProgrammed() && (type != ARCH_PCID))
    {
        /* Retreive platform public fuse ID */
        drv_GetPublicFuseId(public_platform_id);
        if (memcmp(ppid, public_platform_id, SHA1_DIGEST_SIZE) == 0)
        {
            OS_UIST_SMARKER(DRVARCH_UIST_VALID_PUB_FUSE_ID);
            return 0;
        }

        OS_UIST_SMARKER(DRVARCH_UIST_INVALID_PUB_FUSE_ID);
        return -1;
    }

    if (type != ARCH_PFID)
    {
        /* Retreive platform public chip ID */
        drv_GetPublicChipId(public_platform_id);
        if (memcmp(ppid, public_platform_id, SHA1_DIGEST_SIZE) == 0)
        {
            OS_UIST_SMARKER(DRVARCH_UIST_VALID_PUB_CHIP_ID);
            return 0;
        }
    }

    OS_UIST_SMARKER(DRVARCH_UIST_INVALID_PUB_CHIP_ID);
    return -1;
}

char * drv_arch_GetDataFromFile(char *filename, int *size)
{
    int fd;
    uint8 *file_data;
    char *data_ptr = NULL;
    int ret = 0;
    tAppliFileHeader *arch_fh_ptr=NULL;
    int file_size_adding = 0;
    int arch_id, arch_entry;

    do
    {
        fd = drv_fs_Open(filename, O_RDONLY, 0);
        if (fd == -1)
        {
            break;
        }

        /* Read archive header */
        arch_fh_ptr = malloc(sizeof(tAppliFileHeader));
        REL_ASSERT(arch_fh_ptr != NULL);
        ret = drv_arch_ReadHeader(arch_fh_ptr, fd);
        if(ret == 0)
        {
            break;
        }

        /* Check header validity. Those files are not zipped. */
        ret = drv_arch_HeaderVerify(arch_fh_ptr, SKIP_ZIP_ARCH_CHECK);
        if (ret == -1)
        {
            OS_UIST_SMARKER(DRVARCH_UIST_ID_BAD_ARCH_HEADER);
            break;
        }

        /* Read remaining archive data. File is not zipped... */
        file_data = malloc(arch_fh_ptr->file_size);
        REL_ASSERT(file_data != NULL);
        int bytes_read = drv_fs_Read(fd, file_data, arch_fh_ptr->file_size);
        DEV_ASSERT(bytes_read == arch_fh_ptr->file_size);

        /* Check SHA1/RSA signature validity if required. */
        arch_id = GET_ARCH_ID(arch_fh_ptr->file_id);
        arch_entry = drv_archGetTableEntry(arch_id);
        switch(arch_type[arch_entry].key_set)
        {
            case ARCH_EXT_AUTH:
            case ARCH_NO_AUTH:
                break;
            case ARCH_SELF_ENCRYPTION:
                {   
                   uint8* dec_data = NULL;
                   int   dec_data_size = 0;  
                                   
                    /* Apply the De-encryption on file_data; returns dec_data (dynamic memory pointer) */
                   dec_data = drv_nvramCheckAndDecryptBuffer((uint8*) file_data, 
									                (uint32)  arch_fh_ptr->file_size, 
									                (uint32*) &dec_data_size); 
                   free(file_data);

                   if (dec_data == NULL)
                   {
                       /* An error occured */
                       ret = -1;
                   }
                   else
                   {
                       /* file_data carries the clear data */
                       file_data = dec_data;
                       arch_fh_ptr->file_size = dec_data_size;
                   }
                }
                break;
            default:
                ret = drv_arch_RSASignVerify(true, file_data, arch_fh_ptr, NULL, NULL, NULL);
                file_size_adding += KEY_ID_BYTE_LEN + NONCE_SIZE + RSA_SIGNATURE_SIZE;
        }

        /* Check public chip ID validity if required */
        if ((ret == 0) && (arch_type[arch_entry].ppid_check ))
        {
            ret = drv_arch_PPIDVerify(file_data, arch_fh_ptr);
            file_size_adding += SHA1_DIGEST_SIZE;
        }

        if (ret == 0)
        {
            *size = arch_fh_ptr->file_size - file_size_adding;
            DEV_ASSERT(arch_fh_ptr->file_size > file_size_adding);
            data_ptr = (char *)file_data;
        }

    } while (0);

    if (fd >= 0)
    {
        free(arch_fh_ptr);
        drv_fs_Close(fd);
    }

    return data_ptr;
}

ArchError drv_arch_SetDataInFile(char *filename, uint8 *buf, int len)
{
    int i, arch_entry = -1;
    tAppliFileHeader *file_header = NULL;
    ArchError error = ARCH_ERR_NO_ERROR;
    uint8 *buf_to_write = NULL;
    int    len_to_write = 0;

    for(i=0; i<ArchPathMaxNum; i++)
    {
        /* Parse ArchPath table looking for filename */
        if(ArchPath[i])
        {
            if(strcmp(filename, ArchPath[i]) == 0)
            {
                /* Found file entry */
                arch_entry = drv_archGetTableEntry(i);

                if((arch_type[arch_entry].key_set != ARCH_NO_AUTH) &&
                   (arch_type[arch_entry].key_set != ARCH_EXT_AUTH) &&
                   (arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION))
                {
                    /* Cannot build a file with other security level */
                    error = ARCH_ERR_INVALID_SECURITY_STATE;
                    break;
                }
                else
                {
                    if((arch_type[arch_entry].key_set == ARCH_EXT_AUTH) &&
                       (drv_SecurityExtAuthGetState() != EXT_AUTH_UNLOCKED))
                    {
                        /* Platform is not unlocked */
                        error = ARCH_ERR_PROTECTED_ARCH;
                        break;
                    }

                    /* check if an encryption is requested */
                    if (arch_type[arch_entry].key_set == ARCH_SELF_ENCRYPTION)
                    {
                       buf_to_write =  drv_nvramDigestAndEncryptBuffer(buf, 
										                               (uint32)  len, 
										                               (uint32*) &len_to_write);                                        
                    }
                    else
                    {
                       buf_to_write = buf;
                       len_to_write = len;
                    }

                    /* Build file header */
                    file_header = malloc(sizeof(tAppliFileHeader));
                    REL_ASSERT(file_header != NULL);
                    drv_arch_BuildDataFileHeader(len_to_write, file_header, arch_type[arch_entry].arch_id);
                    break;
                }
            }
        }
    }

    if(arch_entry == -1)
    {
        error = ARCH_ERR_ARCH_NOT_FOUND;
    }

    if(error == ARCH_ERR_NO_ERROR)
    {
        struct drv_fs_Stat stat;

        /* We will create 1st a tmp file and then rename at the end */
        char *tmp_name = malloc(MAX_FILENAME_LENGTH);
        REL_ASSERT(tmp_name != NULL);
        strcpy(tmp_name, filename);
        strcat(tmp_name, ".tmp");

        /* Additionally, remove tmp file if already exists */
        int ret = drv_fs_Lstat(tmp_name, &stat);
        if(ret == 0)
        {
            drv_fs_Remove(tmp_name);
        }

        /* Build data file */
        int fd, bytes_written;

        /* Create & Open file */
        fd = drv_fs_Open(tmp_name, O_CREAT | O_WRONLY, S_IREAD | S_IWRITE);
        DEV_ASSERT(fd >= 0);

        /* Write header in file */
        REL_ASSERT(file_header != NULL);
        bytes_written = drv_fs_Write(fd, file_header, file_header->length);
        DEV_ASSERT_EXTRA(bytes_written == file_header->length, 2, bytes_written, file_header->length);

        /* Write buf in file */
        bytes_written = drv_fs_Write(fd, buf_to_write, len_to_write);
        DEV_ASSERT_EXTRA(bytes_written == len_to_write, 2, bytes_written, len_to_write);

        /* Close file */
        drv_fs_Close(fd);

        /* Replace existing file */
        ret = drv_fs_Rename(tmp_name, filename);
        DEV_ASSERT(ret==0);

        free(tmp_name);
    }

    /* Free resources */
    if(file_header)
    {
        free(file_header);
    }

    if ((buf_to_write != NULL) && (buf_to_write != buf))
    {
        /* that means a buffer has been malloced to embed the encrypted data */
        drv_nvramEncryptionBufferRelease(buf_to_write);
    }
    return error;
}

int drv_arch_GetKeyIndex(int arch_id, uint8 *key_id)
{
    int i, j;
    int key_index = -1;
    int res = 0;
    int arch_entry = drv_archGetTableEntry(arch_id);

    switch (arch_type[arch_entry].key_set)
    {
    case ARCH_ICE_ICE_KEY_SET:
        for (i = 0; i < BROM_NUM_RSA_KEYS; i++)
        {
            uint8 *key_brom_rsa_modulus = brom_GetBt2KeyModulus() + i*BROM_RSA_MODULUS_SIZE;
            /* For each public key in table, compare 4 1st bytes with key_id  */
            for (j = 0; j< KEY_ID_BYTE_LEN; j++)
            {
                if (*(key_id + j) != key_brom_rsa_modulus[j])
                {
                    /* No need to continue after a wrong comparison */
                    break;
                }
                else
                {
                    if(j == (KEY_ID_BYTE_LEN -1))
                    {
                        res = 1;

                        /* No need to continue after a good comparison */
                        break;
                    }
                }
            }
            if (res)
            {
                key_index = i;

                /* Found the key ID, no need to continue */
                break;
            }
        }
        break;

    case ARCH_ICE_OEM_KEY_SET:
        key_index = GetKeyIndex(key_id, ice_oem_keys, ICE_OEM_NUM_RSA_KEYS);
        break;

    case ARCH_OEM_FACT_KEY_SET:
        key_index = GetKeyIndex(key_id, oem_fact_keys, OEM_FACT_NUM_RSA_KEYS);
        break;

    case ARCH_ICE_FACT_KEY_SET:
        key_index = GetKeyIndex(key_id, ice_fact_keys, ICE_FACT_NUM_RSA_KEYS);
        break;

    case ARCH_ICE_DBG_KEY_SET:
        key_index = GetKeyIndex(key_id, ice_dbg_keys, ICE_DBG_NUM_RSA_KEYS);
        break;

    case ARCH_OEM_FIELD_KEY_SET:
        key_index = GetKeyIndex(key_id, oem_field_keys, OEM_FIELD_NUM_RSA_KEYS);
        break;

#if defined(ICERA_FEATURE_SOFT_ACTIVATION)
    case ARCH_ACT_ACT_KEY_SET:
        key_index = GetKeyIndex(key_id, act_act_keys, ACT_ACT_NUM_RSA_KEYS);
        break;
#endif

    default:
        OS_UIST_SMARKER( DRVARCH_UIST_INVALID_KEY_SET );
        break;
    }

    return key_index;
}

int drv_arch_AllowedFirstFileProgramming(int arch_id)
{
#ifdef ICERA_FEATURE_ALLOW_FIRST_FILE_PROGRAM
    return 1;
#else
    int allowed = 0;
    LivantoSecurityState security_state = brom_GetLivantoSecurityState();

    /* Only on dev platforms and for some files, 1st programming remains allowed */
    if((security_state == SECURITY_STATE__DEV) ||
       (arch_id == ARCH_ID_PRODUCTCFG) ||
       (arch_id == ARCH_ID_DEVICECFG) ||
       (arch_id == ARCH_ID_IMEI) ||
       (arch_id == ARCH_ID_ACT_DATA) ||
       (arch_id == ARCH_ID_SECCFG) ||
       (arch_id == ARCH_ID_UNLOCK) ||
       (arch_id == ARCH_ID_AUDIOCFG))
    {
        allowed = 1;
    }
    return allowed;
#endif /* #ifdef ICERA_FEATURE_ALLOW_FIRST_FILE_PROGRAM */
}

int drv_arch_CheckUpdateKeyValidity(int arch_id, int update_key_index, bool krm_enabled)
{
    int result = 1;
    int arch_entry = drv_archGetTableEntry(arch_id);
    LivantoSecurityState security_state = brom_GetLivantoSecurityState();

    if(arch_type[arch_entry].is_patch)
    {
        /* This file is never programmed in flash, this test is useless... */
        return result;
    }

    int fd, res;
    int current_key_index;
    int current_key_id = -1;
    char *update_context_file = NULL;
    int first_file_program_allowed = drv_arch_AllowedFirstFileProgramming(arch_id);

    /* Get current key index */
    /* Need to read current firmware to extract info from header and read current key ID */
    if(arch_id == ARCH_ID_BT2)
    {
        tAppliFileHeader bt2_hdr;

        if (drv_ChpcGetBootMode() == 0)
        {
            return 1;
        }

        do
        {
            /* Read BT2 header */
            int ok = drv_FlashReadBt2Data((uint8 *)&bt2_hdr, 0, sizeof(bt2_hdr));
            if(!ok)
            {
                /* Fail to read header */
                result = 0;
                break;
            }

            /* Check BT2 header before using length field... */
            if (drv_arch_HeaderVerify(&bt2_hdr,SKIP_ZIP_ARCH_CHECK) == 0)
            {
                /* Found valid header in flash, read key index */
                ok =  drv_FlashReadBt2Data((uint8 *)&current_key_id,
                                           bt2_hdr.length + bt2_hdr.file_size - KEY_ID_BYTE_LEN - NONCE_SIZE - RSA_SIGNATURE_SIZE,
                                           sizeof(int));
                if(!ok)
                {
                    /* Fail to read key ID */
                    result = 0;
                }
            }
            else
            {
                /* Invalid header... */
                result = 0;
            }
        } while(0);

        if(result == 0 && first_file_program_allowed)
        {
            /* All "errors" above will be due generally to an ampty flash (maybe a flash corruption...)
               Return success in case first file programming is allowed */
            return 1;
        }
    }
    else
    {
        do
        {
            int bytes_read, file_size;
            struct drv_fs_Stat s;

            /* Get file name where current archive update context could be stored */
            update_context_file = malloc(MAX_FILENAME_LENGTH + strlen(".info"));
            REL_ASSERT(update_context_file != NULL);
            strcpy(update_context_file, drv_arch_GetPathById(arch_id));
            strcat(update_context_file, ".info");

            /* Check if .info file exists */
            if(drv_fs_Lstat(update_context_file, &s) == 0)
            {
                /* Last current firmware update was aborted */
                /* Let's read key ID in .info file */
                fd = drv_fs_Open(update_context_file, O_RDONLY, 0);
                bytes_read = drv_fs_Read(fd, &current_key_id, KEY_ID_BYTE_LEN);
                drv_fs_Close(fd);
                if(bytes_read != KEY_ID_BYTE_LEN)
                {
                    /* File was invalid or failure at reading... */
                    result = 0;
                }
            }

            /* Open current archive */
            fd = drv_fs_Open(drv_arch_GetPathById(arch_id), O_RDONLY, 0);
            if (fd < 0)
            {
                /* This is the 1st update */
                if (first_file_program_allowed)
                {
                    /**
                     *  We allow to not perform update key validity check for:
                     *    - custom config file
                     *    - imei file
                     *    - development platform */
                    result = 1;
                    free(update_context_file);
                    return result;
                }
                else
                {
                    /* Error: File not found, no way to perform check update key validity */
                    OS_UIST_SMARKER(DRVARCH_UIST_FLASH_READ_FAILURE);
                    result = 0;
                }
                break;
            }

            if(current_key_id == -1)
            {
                /* Get current archive key ID */
                file_size = drv_fs_Lgetsize(fd);
                DEV_ASSERT(file_size > (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN));

                res = drv_fs_Lseek(fd, file_size - (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN), SEEK_CUR);
                DEV_ASSERT(res == (file_size - (RSA_SIGNATURE_SIZE + NONCE_SIZE + KEY_ID_BYTE_LEN)));
                bytes_read = drv_fs_Read(fd, &current_key_id, KEY_ID_BYTE_LEN);
                DEV_ASSERT(bytes_read == KEY_ID_BYTE_LEN);
            }

            drv_fs_Close(fd);

        } while(0);
    }

    if(result)
    {
       current_key_index =  drv_arch_GetKeyIndex(arch_id, (uint8 *)&current_key_id);
       if(update_key_index == -1)
       {
           /* Error: We did not find any valid key to match with current key ID...*/
           /* How did this firmware was put in the flash ? */
           result = 0;
       }
    }

    if(result)
    {
        if(update_key_index < current_key_index)
        {
            /* Error: key revocation mechanism forbids lower key index when updating a firmware. */
            OS_UIST_SVALUE(DRV_ARCH_UIST_REVOCATION_KEY, update_key_index);
            result = 0;
        }
    }

    if(update_context_file)
    {
        free(update_context_file);
        /**
         * Note:
         * The .info file has not been removed. It will be replaced at
         * next update and even removed if update is successfull. But we
         * always keep it for safety.
         */
    }

    if(result == 0)
    {
        /*  We have to check if this is an unlocked platform */
        if(drv_UnlockedPlatform())
        {
            if(arch_id != ARCH_ID_BT2)
            {
                /* Key revocation mechanism disabled on unlocked platform, except for BT2 update:
                    if a dev. signed BT2 is programmed on a production platform, then it will never
                    boot up successfully because of BootROM protection.*/
                result = 1;
            }
        }

        /* We can also check if key revocation mechanism is disabled */
        if((security_state == SECURITY_STATE__DEV) && !krm_enabled)
        {
            /* Key revoc. mechanism can only be disabled on a dev. platform. */
            OS_UIST_SMARKER(DRV_ARCH_UIST_REVOCATION_KEY_DISABLED);
            result = 1;
        }
    }

    return result;
}

void drv_arch_BuildDataFileHeader(int data_len, tAppliFileHeader *file_header, int arch_id)
{
    int i;
    uint32  checksum    = 0;
    uint32  *p          = (uint32*)file_header;
    int arch_entry = drv_archGetTableEntry(arch_id);

    REL_ASSERT(file_header != NULL);

    memset(file_header, 0, ARCH_HEADER_BYTE_LEN);

    if((arch_type[arch_entry].key_set != ARCH_NO_AUTH) &&
       (arch_type[arch_entry].key_set != ARCH_EXT_AUTH) &&
       (arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION))
    {
        DEV_FAIL("Building of signed file not supported !");
    }
    file_header->tag       = ARCH_TAG;
    file_header->length    = ARCH_HEADER_BYTE_LEN;
    file_header->file_size = data_len;
    file_header->file_id   = arch_id;
#ifdef SHA1_RSA_SIGNED
    file_header->sign_type = ARCH_SIGN_TYPE__RSA;
#else
    file_header->sign_type = ARCH_SIGN_TYPE__RSA2;
#endif
    for(i=0; i<ARCH_HEADER_BYTE_LEN/4; i++)
    {
        checksum ^= p[i];
    }
    file_header->checksum  = checksum;

    return;
}

drv_archPatchHandler drv_arch_GetPatchHandler(ArchId arch_id)
{
    drv_archPatchHandler handler = NULL;
    switch(arch_id)
    {
    case ARCH_ID_CALIB_PATCH:
        handler = drv_NvramRoApplyPatch;
        break;

#ifdef ENABLE_SUPL_FEATURE
    case ARCH_ID_SSL_CERT:
        handler = drv_arch_UpdateSslCert;
        break;
#endif

    case ARCH_ID_WEBUI_PACKAGE:
        handler = drv_arch_UpdateWebUiPackage;
        break;

    default:
        DEV_FAIL_EXTRA("This archive is not a patch !", 1, arch_id);
    }

    return handler;
}

bool drv_arch_IsEnoughSpaceToWriteFile(uint32 arch_id, const uint32 file_size, char ** arch_file_path)
{
    bool    status = false;
    int     existing_file_size    = 0;
    int     avail_space_partition = 0;
    struct  drv_fs_MountInfo mount_info;
    struct drv_fs_Stat s;

    char *temp_update_file = NULL;

    *arch_file_path = drv_arch_GetPathById(arch_id);
    existing_file_size = drv_fs_Getfilesize(*arch_file_path);

    temp_update_file = malloc(MAX_FILENAME_LENGTH);
    REL_ASSERT(temp_update_file != NULL);
    strcpy(temp_update_file, *arch_file_path);
    strcat(temp_update_file, ".tmp");

    if(drv_fs_Lstat(temp_update_file,&s) == 0)
    {
        /* Then TEMP_UPDATE_FILE is still in filesystem and must be removed now */
        drv_fs_Remove(temp_update_file);
    }

	free(temp_update_file);

    if(existing_file_size < 0) existing_file_size = 0; /* For non existing file */

    if(drv_fs_GetMountInfo(*arch_file_path,&mount_info))
    {
        avail_space_partition = drv_fs_Freespace(mount_info.device_name);
        if(avail_space_partition >= 0)
        {
            avail_space_partition += existing_file_size;
            if (avail_space_partition >= file_size)
            {
                status = true;
            }
        }
    }

    return status;
}

int drv_arch_FlashWrite( tAppliFileHeader *arch_fh_ptr, uint8 *file_data_ptr, void (*FlashProgressCB)(int))
{
    int status = false;
    int arch_id= GET_ARCH_ID(arch_fh_ptr->file_id);

    if (arch_id == ARCH_ID_BT2)
    {
        /* BT2 archive is outside VFS */
        int res = drv_FlashBt2Prog((uint8 *)arch_fh_ptr,
                                   arch_fh_ptr->length,
                                   file_data_ptr,
                                   arch_fh_ptr->file_size,
                                   FlashProgressCB);
        DEV_ASSERT(res);
        status=true;
    }
    else
    {
        int   bytes_written, bytes_read;
        int   fd, fd1;
        int   size = arch_fh_ptr->length + arch_fh_ptr->file_size;
        int   total_size = size;
        int   src_offset = 0;
        int   block_size = 0x8000;
        int   prev_completion = 0;
        int   completion;
        char *arch_file_path        = NULL;
        int   res = -1;
        char *update_context_file   = NULL;
        int   current_offset, key_id_offset;
        uint32 current_key_id;
        struct drv_fs_Stat s;
        int info_exist = -1;
        tAppliFileHeader *current_arch_hdr = NULL;
        char *temp_update_file = NULL;
        int arch_entry = drv_archGetTableEntry(arch_id);
#ifdef ICERA_FEATURE_CUST_14
        struct drv_fs_Stat fs_stat;
#endif
        DEV_ASSERT(drv_fs_IsInitialised());

        if(!drv_arch_IsEnoughSpaceToWriteFile(arch_id, size, &arch_file_path))
        {
            OS_UIST_SMARKER(DRVARCH_UIST_NOT_ENOUGH_SPACE_ON_FLASH);
        }
        else
        {
            REL_ASSERT(arch_file_path != NULL);

            if((arch_type[arch_entry].key_set != ARCH_NO_AUTH) &&
               (arch_type[arch_entry].key_set != ARCH_EXT_AUTH) &&
               (arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION))
            {
                /* Get file name where current archive update context could be stored */
                update_context_file = malloc(MAX_FILENAME_LENGTH + strlen(".info"));
                REL_ASSERT(update_context_file != NULL);
                strcpy(update_context_file, arch_file_path);
                strcat(update_context_file, ".info");

                /* Check if .info file exists */
                info_exist = drv_fs_Lstat(update_context_file, &s);
                if(info_exist == 0)
                {
                    /* .info file exists */
                    /* There's been a problem during previous update */
                    if(drv_fs_Getfilesize(update_context_file) != KEY_ID_BYTE_LEN)
                    {
                        /* Let's remove it, it is useless */
                        /* We will create a new one later */
                        drv_fs_Remove(update_context_file);
                        info_exist = -1;
                    }
                }

                do
                {
                    /* Check if archive already exist. */
                    if(drv_fs_Lstat(arch_file_path, &s) == 0)
                    {
                        /* Open current existing archive */
                        fd = drv_fs_Open(arch_file_path, O_WRONLY, S_IREAD | S_IWRITE | S_IEXEC);
                        DEV_ASSERT(fd >= 0);

                        if(info_exist == -1)
                        {
                            /* Retreive archive header */
                            current_arch_hdr = calloc(1, sizeof(tAppliFileHeader));
                            REL_ASSERT(current_arch_hdr != NULL);

                            res = drv_arch_ReadHeader(current_arch_hdr, fd);
                            if(res == 0)
                            {
                                free(current_arch_hdr);

                                /* Useless archive */
                                drv_fs_Close(fd);
                                break;
                            }

                            /* Get current archive update context: key ID */
                            key_id_offset = current_arch_hdr->file_size - KEY_ID_BYTE_LEN - NONCE_SIZE - RSA_SIGNATURE_SIZE;
                            current_offset = drv_fs_Lseek(fd, key_id_offset, SEEK_CUR);
                            DEV_ASSERT(current_offset == (key_id_offset + current_arch_hdr->length));
                            bytes_read = drv_fs_Read(fd, &current_key_id, KEY_ID_BYTE_LEN);
                            free(current_arch_hdr);
                            if(bytes_read != KEY_ID_BYTE_LEN)
                            {
                                /* Incomplete file but with a valid header...*/
                                /* Will be truncated later */
                                drv_fs_Close(fd);
                            }
                            else
                            {
                                /* Create file to store current archive update context */
                                fd1 = drv_fs_Open(update_context_file, O_CREAT | O_WRONLY | O_TRUNC, S_IREAD | S_IWRITE | S_IEXEC);
                                DEV_ASSERT(fd1 >= 0);
                                info_exist = 0;

                                /* Store current archive update context */
                                bytes_written = drv_fs_Write(fd1, &current_key_id, KEY_ID_BYTE_LEN);
                                DEV_ASSERT(bytes_written == KEY_ID_BYTE_LEN);

                                drv_fs_Close(fd1);
                            }
                        }

                        drv_fs_Close(fd);

                        /* Truncate current archive */
                        OS_UIST_SMARKER(DRVARCH_UIST_TRUNCATE_FILE);
                        res = drv_fs_Truncate(arch_file_path, arch_fh_ptr->length);
                        DEV_ASSERT(res >= 0);
                    }
                } while(0);
            } /* (arch_type[arch_entry].key_set != ARCH_NO_AUTH) && (arch_type[arch_entry].key_set != ARCH_EXT_AUTH) &&
                   (arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION) */

            /* Open temp file to store new firmware */
            temp_update_file = malloc(MAX_FILENAME_LENGTH);
            REL_ASSERT(temp_update_file != NULL);
            strcpy(temp_update_file, arch_file_path);
            strcat(temp_update_file, ".tmp");

            fd = drv_fs_Open(temp_update_file, O_CREAT | O_WRONLY, S_IREAD | S_IWRITE | S_IEXEC);
            DEV_ASSERT(fd >= 0);

            if(!arch_type[arch_entry].keep_wrapped_info)
            {
                DEV_ASSERT(arch_type[arch_entry].type == ARCH_TYPE_DATA);

                /* Wrapped info is not stored in filesystem for some kind of data files. */
                /* (i.e. header + all "signing data": PPID/KeyID/Nonce & signature)*/
                /* Only used to be able to authenticate & update this file through downloader.*/
                if(arch_type[arch_entry].key_set == ARCH_NO_AUTH ||
                   arch_type[arch_entry].key_set == ARCH_EXT_AUTH ||
                   (arch_type[arch_entry].key_set == ARCH_SELF_ENCRYPTION))
                {
                    /* Unsigned file: skip flush of header in flash */
                    size -= arch_fh_ptr->length;
                }
                else
                {
                    /* Signed file: we don't either copy additional "signing data" */
                    size -= (arch_fh_ptr->length
                             + KEY_ID_BYTE_LEN
                             + NONCE_SIZE
                             + RSA_SIGNATURE_SIZE);
                    if(arch_type[arch_entry].ppid_check)
                    {
                        /* File also embeds a PPID */
                        size -= SHA1_DIGEST_SIZE;
                    }
                    DEV_ASSERT(size > 0);
                }
            }
            else
            {
                /* For all other archive: write WRAPPED header in filesystem. */
                bytes_written = drv_fs_Write(fd, (char *)arch_fh_ptr, arch_fh_ptr->length);
                DEV_ASSERT(bytes_written == arch_fh_ptr->length);
                size -= arch_fh_ptr->length;
            }

            while (size)
            {
                if (block_size > size) block_size = size;

                bytes_written = drv_fs_Write(fd, (char *)&file_data_ptr[src_offset], block_size);

                // Check if there was an issue...
                if (bytes_written != block_size)
                {
                    free(temp_update_file);
                    free(update_context_file);
                    drv_fs_Close(fd);
                    return false;
                }

                size -= block_size;
                src_offset += block_size;

                completion = (src_offset * 100) / total_size;
                if (completion>=prev_completion+1)
                {
                    prev_completion = completion;
                    OS_UIST_SVALUE(DRVARCH_UIST_WRITING_FILE, completion);
                    if (FlashProgressCB)
                    {
                        FlashProgressCB(completion);
                    }
                }
            }

            drv_fs_Close(fd);

            /* Rename tmp archive now it is fully available */
            res = drv_fs_Rename(temp_update_file, arch_file_path);
            DEV_ASSERT(res >= 0);

            if(arch_id == ARCH_ID_CALIB)
            {
#ifdef ICERA_FEATURE_CUST_14
                /* Delete the patch history file */
                if (drv_fs_Lstat(CAL_PATCH_HISTORY, &fs_stat) == 0)
                    {
                    res = drv_fs_Remove(CAL_PATCH_HISTORY);
                    DEV_ASSERT(res >= 0);
                    }
#endif
                /* We've just updated CALIBRATION_0_FILE
                   Let's update the back-up copy: CALIBRATION_1_FILE */
                res = drv_fs_Copy(arch_file_path, CALIBRATION_1_FILE);
                DEV_ASSERT(res >= 0);
            }

            if(info_exist == 0)
            {
                /* Remove current archive update context now it is useless */
                res = drv_fs_Remove(update_context_file);
                DEV_ASSERT(res == 0);
            }

            free(temp_update_file);

            if(update_context_file)
            {
                free(update_context_file);
            }

            status = true;
        }
    }

    return status;
}

ArchId drv_ArchIdFromAcronym(char* str)
{
    if (str)
    {
        for (uint16 i = 0; i < arch_type_max_id; ++i)
        {
            if (strcmp(str, arch_type[i].acr) == 0)
            {
                return arch_type[i].arch_id;
            }
        }
    }
    return (ArchId)0xFFFF;
}

const char * drv_archGetTempAudioConfigFilename(void)
{
    return AUDIO_CONFIG_TEMP_FILE;
}

/** @} END OF FILE */
