/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch_backup.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @file drv_arch_backup.h
 *
 */

#ifndef DRV_ARCH_BACKUP_H
#define DRV_ARCH_BACKUP_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
/* drv_arch_BackupFiles return values */
#define DRV_ARCH_BACKUP_SUCCESS        1
#define DRV_ARCH_BACKUP_MISSING_FILE  -1
#define DRV_ARCH_BACKUP_FILES_FAILURE -2
#define DRV_ARCH_BACKUP_INFOS_FAILURE -3

/* drv_arch_RestoreFiles return values */
#define DRV_ARCH_RESTORE_SUCCESS       1
#define DRV_ARCH_RESTORE_MISSING_FILE -1
#define DRV_ARCH_RESTORE_FAILURE      -2

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Backup file property
 */
typedef struct
{
    char *original_path;  /* File path in the default partition */
    char *backup_path;    /* File path in the backup partition  */
}tArchBackupFileProperty;

/**
 * Backup info property
 */
typedef struct
{
    char *source_file;
    char *info_file;
    char *backup_source_file;
    char *backup_info_file;
}tArchBackupInfoProperty;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern const tArchBackupFileProperty arch_backup_mandatory_files[];
extern const uint32 arch_backup_files_id;

extern const tArchBackupInfoProperty arch_backup_mandatory_infos[];
extern const uint32 arch_backup_infos_id;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 * Format R/W data partition and restore folder architecture
 */
void drv_arch_ClearMdmDataPartition(void);

/**
 * Format main fs partition and restore files stored in back up partition.
 *
 * List of files to restore is defined in arch_backup_mandatory_files[] table.
 * Used by BT2 when recover corrupted fs or by LDR/IFT with AT%IRESTORE AT cmd.
 *
 * @return int to indicate success, or file missing, or restore failure.
 */
int drv_arch_RestoreFiles(void);

/**
 * Format back up partition and store files from main fs
 * partition in it.
 *
 * List of the copied files is defined in
 * arch_backup_mandatory_files[] table.
 * Used by LDR/IFT with AT%IBACKUP AT cmd.
 *
 *
 * @return int to indicate success, or file missing or copy
 *         failure.
 */
int drv_arch_BackupFiles(void);

/**
 * Restore files in main fs partition and format modem data
 * partition.
 *
 * Called from BT2 after filesystem corruption detected.
 *
 */
void drv_arch_FsRecover(void);

#endif /* #ifndef DRV_ARCH_BACKUP_H */

/** @} END OF FILE */
