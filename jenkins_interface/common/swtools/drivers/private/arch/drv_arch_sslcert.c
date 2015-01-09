/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_sslcert.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_sslcert.c SSL cert update utilities
 *  
 */ 

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_arch.h"
#include "drv_fs.h"

#ifdef ENABLE_SUPL_FEATURE

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <string.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/
#define DRV_ARCH_SSL_RECORD_DIR            DRV_FS_DATA_SSL_DIR_NAME
#define DRV_ARCH_SSL_FILE_NAME_BODY        "cert_"
#define DRV_ARCH_SSL_FILE_NAME_EXTENSION   ".pem"
#define DRV_ARCH_SSL_FILE_NAME_FORMAT      DRV_ARCH_SSL_FILE_NAME_BODY""DRV_FS_INDEX_FORMAT""DRV_ARCH_SSL_FILE_NAME_EXTENSION
#define DRV_ARCH_SSL_MAX_IDX               DRV_FS_MAX_IDX
#define DRV_ARCH_SSL_FILE_FULL_NAME_FORMAT DRV_ARCH_SSL_RECORD_DIR""DRV_FS_SEPARATOR""DRV_ARCH_SSL_FILE_NAME_FORMAT

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

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
int32 drv_arch_UpdateSslCert(tAppliFileHeader *arch_hdr, uint8 *arch_start)
{
    int file_size_adding = 0, cert_data_size;
    uint32 first_idx = 1, last_idx = UINT32_MAX;
    int arch_entry;
    char cert_name[MAX_FILENAME_LENGTH];

    DEV_ASSERT(arch_hdr->file_id == ARCH_ID_SSL_CERT);

    arch_entry = drv_archGetTableEntry(arch_hdr->file_id);
    if(arch_type[arch_entry].key_set != ARCH_NO_AUTH &&
       arch_type[arch_entry].key_set != ARCH_EXT_AUTH &&
       arch_type[arch_entry].key_set != ARCH_SELF_ENCRYPTION)
    {
        /* This file is a signed file */
        file_size_adding += KEY_ID_BYTE_LEN + NONCE_SIZE + RSA_SIGNATURE_SIZE;
    }
    if(arch_type[arch_entry].ppid_check)
    {
        /* PPID was embedded in this file */
        file_size_adding += SHA1_DIGEST_SIZE;
    }

    /* Only cert data is copied, all "wrapped" information is lost (header and signing stuff...) */
    cert_data_size = arch_hdr->file_size - file_size_adding;
    drv_fs_GetRecordIdx(&first_idx, 
                        &last_idx, 
                        DRV_ARCH_SSL_RECORD_DIR,
                        DRV_ARCH_SSL_FILE_NAME_BODY,
                        DRV_ARCH_SSL_FILE_NAME_EXTENSION);

    /* Increase last idx for next certificate */
    last_idx +=1;
    DEV_ASSERT(last_idx <= DRV_ARCH_SSL_MAX_IDX);

    memset(cert_name, 0, sizeof(cert_name));
    sprintf(cert_name, DRV_ARCH_SSL_FILE_FULL_NAME_FORMAT, last_idx);
    int fd = drv_fs_Open(cert_name, O_CREAT | O_WRONLY, S_IREAD | S_IWRITE);
    int bytes_written = drv_fs_Write(fd, arch_start, cert_data_size);
    DEV_ASSERT(bytes_written == cert_data_size);
    drv_fs_Close(fd);

    return 0;
}

void drv_arch_RemoveSslCert(void)
{
    drv_fs_RmDirContent(DRV_ARCH_SSL_RECORD_DIR);
}


#endif /* #ifdef ENABLE_SUPL_FEATURE */
/** @} END OF FILE */
