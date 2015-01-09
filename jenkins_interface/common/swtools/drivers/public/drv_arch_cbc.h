/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch_cbc.h#1 $ 
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_cbc.h Archive Extra Header ASN.1 
 *       encoding/decoding utilities
 *  
 */

#ifndef DRV_ARCH_CBC_H
#define DRV_ARCH_CBC_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "asn1_api.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef enum
{
    DEFAULT_OK,
    NO_FILE,                 /**< Currently, no file available in filesystem */
    SIG_INVALID,             /**< SHA1/RSA file signature is invalid */
    DATA_INVALID,            /**< ASN.1 encoded data file is invalid (only for PLATFORM_CONFIG)*/
    CHIPID_INVALID,          /**< Embedded public Chip ID in file doesn't match with platform one */
    DEFAULT_VALUES,          /**< ASN1 decoder returned spec default values */
    UPDATE_DISABLED,         /**< Update is disable in current file */
    UPDATE_DISABLED_DEFAULT, /**< Update is disable in default values */
    VERSION_INVALID,         /**< CBC: version compatibility check failed */
    PLATFORM_INVALID,        /**< CBC: hw platform compatibility check failed */
    CBC_DISABLED,            /**< CBC: disabled in custom config file */
    ASN1_INVALID,            /**< ASN1 decoder fail to decode ASN1 encoded buffer */
    PRODUCT_INVALID,         /**< CBC: incompatible supported product in config file to update */
} drv_ArchCbcResult;

/**
 * CBC Status
 */
typedef struct
{
    drv_ArchCbcResult value; /* CBC status */
    uint32 cur_version;      /* current archive version number */
    uint32 new_version;      /* version number of archive used for update */
    bool krm_enabled;        /* Key revocation mechanism enabled/disabled */
} drv_ArchCbcStatus;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 * Check data validity in /data/platformConfig.bin
 * 
 * @param status struct filled to give status on dta file check
 * 
 * @return NULL in case of non existence or invalid data, a pointer to the 
 *         decoded data buffer in case of success
 *         status.value is set to indicate status. 
 */
extern PlatformConfig_t * drv_ArchCheckPlatformConfigFile(drv_ArchCbcStatus *status);

/**
 * Free platform config structure.
 * 
 * @param plat_conf  Platform config structure
 *
 */
extern void drv_ArchFreePlatformConfigFile(PlatformConfig_t *plat_conf);

/**
 * Try and read the RFM module board config file from FS.
 * Allocates memory if successful which the caller is responsible for freeing.
 * @return Platform config structure or NULL
 */
extern PlatformConfig_t * drv_ArchGetRfmBoardConfig(void);

/**
 * Check data validity in /data/customConfig.bin
 * 
 * @param status struct filled to give status on data file check 
 * @param file_id identifier of file to update (0 for appli, 1 
 *                for bt2, 2 for ft, 3 for loader,...)
 * 
 * @return void
 *         status.value is set to indicate status. 
 */
extern void drv_ArchCheckCustomConfigFile(drv_ArchCbcStatus *status, int file_id);

/**
 *  Retreive and decode extended header of the archive to
 *  download.
 * 
 * @param arch_hdr_ptr pointer to buffer containing header of 
 *                     the archive to download
 *
 * @return NULL or a pointer to buffer containing archive 
 *         decoded extended header.
 *
 */
extern ExtendedHeader_t * drv_ArchExtractExtendedHeaderFromHeader(tAppliFileHeader *arch_hdr_ptr);

/**
 *  Retreive and decode extended header of the archive to
 *  update.
 * 
 * @param wrapped_name filename of the archive to update.
 *
 * @return NULL or a pointer to buffer containing archive 
 *         decoded extended header.
 *
 */
extern ExtendedHeader_t * drv_ArchExtractExtendedHeaderFromWrapped(char *wrapped_name);


/**
 * Perform Cross Boot Check on firmware file 
 * 
 * @param status struct filled to give status on CBC 
 * @param ext_hdr pointer to buffer containing archive to 
 *                download decoded extended header.
 * @param plat_conf pointer to buffer containing decoded 
 *                 platformConfig.bin data
 * @param file_id identifier of file to update (0 for appli, 1 
 *                for bt2, 2 for ft, 3 for loader,...) 
 *
 * @return void
 *         status.value is set to indicate status.
 *
 */
extern void drv_ArchCheckFirmwareCompatibility(drv_ArchCbcStatus *status, ExtendedHeader_t *ext_hdr, PlatformConfig_t * plat_conf, int file_id);

/** 
 * Perform Cross Boot Check on config files 
 *  
 * Make the comparison between "product" flag found in flash 
 * file system and "compatibleProduct" found in file to update. 
 *  
 * compatibleProduct might always ends with "*" char. 
 *  
 * If "product" not found in FFS: check is OK 
 * If "compatibleProduct" not found in file to update: check is 
 * OK 
 * If default "product" value found: check is OK. Default is "*"
 * If invalid ASN1 in file to update: check is KO. 
 * If char per char comparison between "product" & 
 * "compatibleProduct" differs: check is KO. With the fact that 
 * char per char comparison stops as soon as "*" is found in 
 * "compatibleProduct" 
 * 
 * @param arch_hdr file to update header
 * @param data     file to update data
 * 
 * @return drv_ArchCbcResult
 */
extern drv_ArchCbcResult drv_ArchCheckCustomConfigFileCompatibility(tAppliFileHeader *arch_hdr, uint8 *data);

#endif /* #ifndef DRV_ARCH_CBC_H */

/** @} END OF FILE */
