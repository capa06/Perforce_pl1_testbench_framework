/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_backup.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_backup.c Handle filesystem archive backup
 *       feature
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"

#ifndef ICERA_FEATURE_DISABLE_FFS_BACKUP
#include "drv_arch_backup.h"
#include "drv_fs.h"
#include "drv_arch.h"
#include "drv_arch_local.h"
#include "os_uist_ids.h"
#include "mphal_wdt.h"
#include "mphal_powerclk.h"
#include "drv_security.h"
#if defined(USE_NOR)
#include "drv_nor_flash.h"
#endif

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <errno.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/
#define DRV_FS_BACKUP_FILES   0
#define DRV_FS_ORIGINAL_FILES 1

#define DRV_BACKUP_APP_DIR         DRV_FS_DIR_NAME_BACKUP""DRV_FS_APP_DIR_NAME
#define DRV_BACKUP_DATA_DIR        DRV_FS_DIR_NAME_BACKUP""DRV_FS_DATA_DIR_NAME
#define DRV_BACKUP_DATA_FACT_DIR   DRV_FS_DIR_NAME_BACKUP""DRV_FS_DATA_FACT_DIR_NAME

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

/** Here's the table describing files to copy from/to main FS
 *  partition to/from back up partition during backup/restore
 *  operation.
 */
const tArchBackupFileProperty arch_backup_mandatory_files[] =
{
    {LDR_APPLICATION_FILE, DRV_BACKUP_APP_DIR"/loader.wrapped"},
    {CALIBRATION_0_FILE,   DRV_BACKUP_DATA_FACT_DIR"/calibration_0.bin"},
    {CALIBRATION_1_FILE,   DRV_BACKUP_DATA_FACT_DIR"/calibration_1.bin"},
    {PLATFORM_CONFIG_FILE, DRV_BACKUP_DATA_DIR"/platformConfig.bin"},
    {SECURED_IMEI_FILE,    DRV_BACKUP_DATA_FACT_DIR"/imei.bin"}
};

const uint32 arch_backup_files_id = sizeof(arch_backup_mandatory_files)/sizeof(tArchBackupFileProperty);

/** Here's the table describing config files to copy from/to
 *  main FS partition to/from back up partition during
 *  backup/restore operation.
 */
const tArchBackupFileProperty arch_backup_mandatory_config_files[] =
{
    {CUSTOMER_CONFIG_FILE, DRV_BACKUP_DATA_DIR"/customConfig.bin"},
    {DEVICE_CONFIG_FILE, DRV_BACKUP_DATA_DIR"/deviceConfig.bin"},
    {PRODUCT_CONFIG_FILE, DRV_BACKUP_DATA_DIR"/productConfig.bin"},
};

const uint32 arch_backup_config_files_id = sizeof(arch_backup_mandatory_config_files)/sizeof(tArchBackupFileProperty);

/** Here's the table describing info from files to be stored at
 *  backup and restore in main FS partition
 *
 *  "backup_source_file" file will contain the header (+
 *  extended header) of the corresponding source file.
 *
 *  .info file will contain the key ID used to sign the
 *  corresponding source file.
 *
 *  Here are mandatory informations to restore for firmware
 *  update...
 */
const tArchBackupInfoProperty arch_backup_mandatory_infos[] =
{
    /* Infos for MDM */
    {
        MDM_APPLICATION_FILE,
        MDM_APPLICATION_FILE".info",
        DRV_BACKUP_APP_DIR"/modem.wrapped",
        DRV_BACKUP_APP_DIR"/modem.wrapped.info"
    }

};

const uint32 arch_backup_infos_id = sizeof(arch_backup_mandatory_infos)/sizeof(tArchBackupInfoProperty);

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/
static void FormatProgressCB(int progress)
{
    progress++; /* To do something and avoid warning... */
}

/**
 *  Check either main FS partition contents
 *  (DRV_FS_ORIGINAL_FILES) or backup FS partition contents
 *  (DRV_FS_BACKUP_FILES).
 *
 */
static int CheckFilesExistence(int filetype)
{
    int i;
    int ret = 1;
    int res = 0;
    struct drv_fs_Stat stat;

    /* Check list of mandatory files */
    for(i=0; i < (int)arch_backup_files_id; i++)
    {
        if(filetype == DRV_FS_ORIGINAL_FILES)
        {
            res = drv_fs_Lstat(arch_backup_mandatory_files[i].original_path, &stat);
        }
        else
        {
            res = drv_fs_Lstat(arch_backup_mandatory_files[i].backup_path, &stat);
        }

        if(res < 0)
        {
            ret = 0;
            break;
        }
    }

    if(ret)
    {
        /* Check list of mandatory infos */
        for(i=0; i < (int)arch_backup_infos_id; i++)
        {
            if(filetype == DRV_FS_ORIGINAL_FILES)
            {
                res = drv_fs_Lstat(arch_backup_mandatory_infos[i].source_file, &stat);
                if(res < 0)
                {
                    ret = 0;
                    break;
                }
            }
            else
            {
                res = drv_fs_Lstat(arch_backup_mandatory_infos[i].backup_source_file, &stat);
                if(res < 0)
                {
                    ret = 0;
                    break;
                }
                res = drv_fs_Lstat(arch_backup_mandatory_infos[i].backup_info_file, &stat);
                if(res < 0)
                {
                    ret = 0;
                    break;
                }
            }
        }
    }

    return ret;
}

/**
 *  Check either main FS partition contents
 *  (DRV_FS_ORIGINAL_FILES) or backup FS partition contents
 *  (DRV_FS_BACKUP_FILES).
 *
 */
static int CheckConfigFilesExistence(int filetype, uint8 *id_list)
{
    int i;
    int ret = 0;
    int res = 0;
    struct drv_fs_Stat stat;


    REL_ASSERT(id_list != NULL);
    memset(id_list, 0, arch_backup_config_files_id);

    /* Check list of mandatory config files */
    for(i=0; i < (int)arch_backup_config_files_id; i++)
    {
        if(filetype == DRV_FS_ORIGINAL_FILES)
        {
            res = drv_fs_Lstat(arch_backup_mandatory_config_files[i].original_path, &stat);
            if(res == 0)
            {
                /* Store id information in case all files are not here */
                id_list[i] = 1;
                /* We've found at least config file */
                ret = 1;
            }
        }
        else
        {
            res = drv_fs_Lstat(arch_backup_mandatory_config_files[i].backup_path, &stat);
            if(res == 0)
            {
                /* Store id information in case all files are not here */
                id_list[i] = 1;
                /* We've found at least config file */
                ret = 1;
            }
        }
    }

    return ret;
}

/**
 *  For a given source file, extract and store in 2 different
 *  files:
 *    - the file header & extended header
 *    - the keyID used to sign SHA1/RSA sign the source file
 *
 *  The function doesn't assert (except for malloc) to give the
 *  opportynity to update the platform with reliable source
 *  files.
 */
static int BuildInfoFiles(tArchBackupInfoProperty backup_info)
{
    int fd, fd1, current_offset, key_id_offset, bytes_read, bytes_written;
    tAppliFileHeader *file_hdr = NULL;
    uint32 current_key_id;
    int ret = -1;
    int res;

    file_hdr = malloc(sizeof(tAppliFileHeader));
    REL_ASSERT(file_hdr != NULL);

    do
    {
        /* Open source file */
        fd = drv_fs_Open(backup_info.source_file, O_RDONLY, 0);
        DEV_ASSERT(fd >= 0);

        /* Read archive header */
        res = drv_arch_ReadHeader(file_hdr, fd);
        if(res == 0)
        {
			drv_fs_Close(fd);
            break;
        }

        /* Set source file descriptor to read keyID */
        key_id_offset = file_hdr->file_size - KEY_ID_BYTE_LEN - NONCE_SIZE - RSA_SIGNATURE_SIZE;
        current_offset = drv_fs_Lseek(fd, key_id_offset, SEEK_CUR);
        if(current_offset != (key_id_offset + file_hdr->length))
        {
            break;
        }

        /* Read source file keyID */
        bytes_read = drv_fs_Read(fd, &current_key_id, KEY_ID_BYTE_LEN);
        if(bytes_read != KEY_ID_BYTE_LEN)
        {
            break;
        }

        /* Close source file */
        drv_fs_Close(fd);

        /* Open file in backup part. to store source file header */
        fd1 = drv_fs_Open(backup_info.backup_source_file,
                          O_CREAT | O_WRONLY | O_TRUNC,
                          S_IREAD | S_IWRITE | S_IEXEC);
        if(fd1 < 0)
        {
            break;
        }

        /* Store file header in backup part. */
        bytes_written = drv_fs_Write(fd1, (char *)file_hdr, file_hdr->length);
        if(bytes_written != file_hdr->length)
        {
            break;
        }

        drv_fs_Close(fd1);

        /* Open file in backup part. to store keyID */
        fd1 = drv_fs_Open(backup_info.backup_info_file,
                          O_CREAT | O_WRONLY | O_TRUNC,
                          S_IREAD | S_IWRITE | S_IEXEC);
        if(fd1 < 0)
        {
            break;
        }

        /* Store key ID in backup part. */
        bytes_written = drv_fs_Write(fd1, &current_key_id, KEY_ID_BYTE_LEN);
        if(bytes_written != KEY_ID_BYTE_LEN)
        {
            break;
        }

        drv_fs_Close(fd1);

        ret = 0;

    } while(0);

    free(file_hdr);

    return ret;
}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

int drv_arch_BackupFiles(void)
{
    int i;
    int res = 0;
    int ret = DRV_ARCH_BACKUP_SUCCESS;
#if defined(USE_NOR)
    int ans = 0;
#endif

    /* Check any missing files */
    res = CheckFilesExistence(DRV_FS_ORIGINAL_FILES);
    if(!res)
    {
        return DRV_ARCH_BACKUP_MISSING_FILE;
    }

    /* Check any missing config files */
    uint8 id_list[arch_backup_config_files_id];
    res = CheckConfigFilesExistence(DRV_FS_ORIGINAL_FILES, id_list);
    if(!res)
    {
        return DRV_ARCH_BACKUP_MISSING_FILE;
    }

    /** Un-mount partition before format: no action should be
     *  possible once partition is formatted. */
    res = drv_fs_Unmount(DRV_FS_DEVICE_NAME_BACKUP, drv_fs_GetFsName());
    if(!res)
    {
        /* Only accept case where device was noy mounted. Other is fatal.. */
        DEV_ASSERT(drv_fs_GetLastError(drv_fs_GetFsName()) == -EINVAL);
    }


    /* Format the backup partition */
    res = drv_fs_Format(DRV_FS_DEVICE_NAME_BACKUP, drv_fs_GetFsName(), FormatProgressCB);
    DEV_ASSERT(res);

    /* Mount backup partition */
    OS_UIST_SMARKER( DRV_UIST_ID_FS_MOUNT_BACKUP );
    int is_mount_ok = drv_fs_Mount(DRV_FS_DIR_NAME_BACKUP, DRV_FS_DEVICE_NAME_BACKUP, drv_fs_GetFsName() );
    OS_UIST_SVALUE( DRV_UIST_ID_FS_MOUNTED_BACKUP, is_mount_ok );

    /* Create/Restore folder architecture */
    drv_fs_Mkdir(DRV_BACKUP_APP_DIR, S_IRWXU);
    drv_fs_Mkdir(DRV_BACKUP_DATA_DIR, S_IRWXU);
    drv_fs_Mkdir(DRV_BACKUP_DATA_FACT_DIR, S_IRWXU);

#if defined(USE_NOR)
    /* Make backup partition writeable */
    ans = drv_NorChangeSegmentAccessMode(NOR_MAP_SEGMENT_ID__BACKUP_PARTITION, NOR_ACCESS_MODE__READ_WRITE);
    DEV_ASSERT(ans);
#endif

    /* Backup files from main FS partition */
    for(i=0; i < (int)arch_backup_files_id; i++)
    {
        res = drv_fs_Copy(arch_backup_mandatory_files[i].original_path,
                          arch_backup_mandatory_files[i].backup_path);
        if(res < 0)
        {
            ret = DRV_ARCH_BACKUP_FILES_FAILURE;
            break;
        }
    }

    /* Backup config files from main FS partition */
    for(i=0; i < (int)arch_backup_config_files_id; i++)
    {
        if(id_list[i])
        {
            dxp_UIST_SINGLE_VALUE(9999, i);
            res = drv_fs_Copy(arch_backup_mandatory_config_files[i].original_path,
                              arch_backup_mandatory_config_files[i].backup_path);
            if(res < 0)
            {
                ret = DRV_ARCH_BACKUP_FILES_FAILURE;
                break;
            }
        }
    }

    /* Build info files */
    if(res >= 0)
    {
        for(i = 0; i < (int)arch_backup_infos_id; i++)
        {
           res = BuildInfoFiles(arch_backup_mandatory_infos[i]);
           if(res < 0)
           {
               ret = DRV_ARCH_BACKUP_INFOS_FAILURE;
               break;
           }
        }
    }

#if defined(USE_NOR)
    /* Restore backup partition as read/only */
    ans = drv_NorRestoreSegmentAccessMode(NOR_MAP_SEGMENT_ID__BACKUP_PARTITION);
    DEV_ASSERT(ans);
#endif

    return ret;
}

int drv_arch_RestoreFiles(void)
{
    int i;
    int res = 0;

    /* Mount backup partition */
    OS_UIST_SMARKER(DRV_UIST_ID_FS_MOUNT_BACKUP);
    res = drv_fs_Mount(DRV_FS_DIR_NAME_BACKUP, DRV_FS_DEVICE_NAME_BACKUP, drv_fs_GetFsName());
    DEV_ASSERT(res);
    OS_UIST_SVALUE(DRV_UIST_ID_FS_MOUNTED_BACKUP, res);

    /* Check files existence in backup partition */
    res = CheckFilesExistence(DRV_FS_BACKUP_FILES);
    if(!res)
    {
        return DRV_ARCH_RESTORE_MISSING_FILE;
    }

    /* Check config files existence in backup partition */
    uint8 id_list[arch_backup_config_files_id];
    res = CheckConfigFilesExistence(DRV_FS_BACKUP_FILES, id_list);
    if(!res)
    {
        return DRV_ARCH_BACKUP_MISSING_FILE;
    }

    /** Un-mount partition before format: no action should be
     *  possible once partition is formatted. */
    res = drv_fs_Unmount(DRV_FS_DEVICE_NAME_PARTITION1, drv_fs_GetFsName());
    if(!res)
    {
        /* Only accept case where device was noy mounted. Other is fatal.. */
        DEV_ASSERT(drv_fs_GetLastError(drv_fs_GetFsName()) == -EINVAL);
    }

    /* Format main fs partition */
    res = drv_fs_Format(DRV_FS_DEVICE_NAME_PARTITION1, drv_fs_GetFsName(), FormatProgressCB);
    DEV_ASSERT(res);

    /* Mount main fs partition */
    OS_UIST_SMARKER(DRV_UIST_ID_FS_MOUNT_ROOT);
    res = drv_fs_Mount(DRV_FS_DIR_NAME_PARTITION1, DRV_FS_DEVICE_NAME_PARTITION1, drv_fs_GetFsName());
    DEV_ASSERT(res);
    OS_UIST_SVALUE(DRV_UIST_ID_FS_MOUNTED_ROOT, res);

    /* Restore folder architecture in main partition before restoring files */
    drv_fs_Mkdir(DRV_FS_APP_DIR_NAME, S_IRWXU);
    drv_fs_Mkdir(DRV_FS_DATA_DIR_NAME, S_IRWXU);
    drv_fs_Mkdir(DRV_FS_DATA_FACT_DIR_NAME, S_IRWXU);
    drv_fs_Mkdir(DRV_FS_DATA_MODEM_DIR_NAME, S_IRWXU);
    drv_fs_Mkdir(DRV_FS_DEBUG_DATA_DIR_NAME, S_IRWXU);

    /* Restore files in main FS partition */
    for(i=0; i < (int)arch_backup_files_id; i++)
    {
        res = drv_fs_Copy(arch_backup_mandatory_files[i].backup_path,
                          arch_backup_mandatory_files[i].original_path);
        if(res < 0)
        {
            return DRV_ARCH_RESTORE_FAILURE;
        }
    }

    /* Restore config files in main FS partition */
    for(i=0; i < (int)arch_backup_config_files_id; i++)
    {
        if(id_list[i])
        {
            res = drv_fs_Copy(arch_backup_mandatory_config_files[i].backup_path,
                              arch_backup_mandatory_config_files[i].original_path);
            if(res < 0)
            {
                return DRV_ARCH_RESTORE_FAILURE;
            }
        }
    }

    /* Restore infos */
    for(i=0; i < (int)arch_backup_infos_id; i++)
    {
        res = drv_fs_Copy(arch_backup_mandatory_infos[i].backup_source_file,
                          arch_backup_mandatory_infos[i].source_file);
        if(res < 0)
        {
            return DRV_ARCH_RESTORE_FAILURE;
        }
        res = drv_fs_Copy(arch_backup_mandatory_infos[i].backup_info_file,
                          arch_backup_mandatory_infos[i].info_file);
        if(res < 0)
        {
            return DRV_ARCH_RESTORE_FAILURE;
        }
    }

    return DRV_ARCH_RESTORE_SUCCESS;
}

void drv_arch_FsRecover(void)
{
#ifndef USE_NAND
    /* Disable watchdog timer: need time to format main fs partition */
    mphal_WDTDisable();
#endif /* #ifndef USE_NAND */

    if(!drv_fs_IsInitialised())
    {
        /* Recover can be called after 6 consecutive asserts before a call to
           drv_fs_Init().
           Call drv_fs_FormatInit to initialise filesystem instance and be able
           to mount backup partition correctly */
        drv_fs_FormatInit();
    }

    /* Restore back up files */
    drv_arch_RestoreFiles();

#ifndef USE_NAND
    /* Enable watchdog timer: that will fire with while(1) below
       and cause BT2 restart with restored main FS partition */
#ifndef BOOT_FROM_SPI
    mphal_WDTEnable(12*NUM_USECS_IN_ONE_SEC,10*NUM_USECS_IN_ONE_SEC);
#else /* #ifndef BOOT_FROM_SPI */
    mphal_WDTEnable(52*NUM_USECS_IN_ONE_SEC,50*NUM_USECS_IN_ONE_SEC);
#endif /* #ifndef BOOT_FROM_SPI */
#endif /* #ifndef USE_NAND */

    return;
}

#endif /* #ifndef ICERA_FEATURE_DISABLE_FFS_BACKUP */
/** @} END OF FILE */
