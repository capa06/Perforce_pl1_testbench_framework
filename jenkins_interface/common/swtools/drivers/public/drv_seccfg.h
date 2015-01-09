/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_seccfg.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup SecureConfig Secure configuration file
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup SecureConfig
 *
 * @{
 */

/**
 * @file drv_seccfg.h Security API definition
 *
 */

#ifndef DRV_SECCFG_H
#define DRV_SECCFG_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Available Capabilities 
 */
typedef enum
{
    DRV_SECCFG_CAP_HSDPA,     /**< HSDPA Category */
    DRV_SECCFG_CAP_HSUPA,     /**< HSUPA Category */
    DRV_SECCFG_CAP_PMIC,      /**< PMIC allowed */
    DRV_SECCFG_CAP_CM,        /**< CM allowed */

    DRV_SECCFG_CAP_MAX 

} DRV_SecCfgCapability;


/**
 * HSPA category enumeration
 */
enum
{
    DRV_SECCFG_NO_HSPA = 0,
    DRV_SECCFG_HSPA_CAT1,
    DRV_SECCFG_HSPA_CAT2,
    DRV_SECCFG_HSPA_CAT3,
    DRV_SECCFG_HSPA_CAT4,
    DRV_SECCFG_HSPA_CAT5,
    DRV_SECCFG_HSPA_CAT6,
    DRV_SECCFG_HSPA_CAT7,
    DRV_SECCFG_HSPA_CAT8,
    DRV_SECCFG_HSPA_CAT9,
    DRV_SECCFG_HSPA_CAT10,
    DRV_SECCFG_HSPA_CAT11,
    DRV_SECCFG_HSPA_CAT12,
    DRV_SECCFG_HSPA_CAT13,
    DRV_SECCFG_HSPA_CAT14,

    DRV_SECCFG_HSDPA_CAT_MAX,
    DRV_SECCFG_HSUPA_CAT_MAX = DRV_SECCFG_HSPA_CAT7
};


/**
 * PMIC enumeration
 */
enum
{
    DRV_SECCFG_NO_PMIC = 0,
    DRV_SECCFG_PMIC_ICE8145,  /**< ICERA 8145 */

    DRV_SECCFG_PMIC_MAX
};


/**
 * Connection manager enumeration
 */
enum
{
    DRV_SECCFG_NO_CM = 0,
    DRV_SECCFG_CM_WELLPHONE,

    DRV_SECCFG_CM_MAX
};

/**
 * Errors
 */
enum
{
    DRV_SECCFG_OK            = 1,
    DRV_SECCFG_ERROR_NO_FILE = -1,
    DRV_SECCFG_ERROR_BAD_CAP = -2,
    DRV_SECCFG_ERROR         = 0,
};

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/


/**
 * drv_SecCfgGetCapability Get a given capability
 *
 * Note that the system must have parsed the configuration file to be able to perform this
 *
 * @param capability The capability to return
 * @return the capability value or an appropriate error code
 * @see DRV_SecCfgCapability
 */
int drv_SecCfgGetCapability(DRV_SecCfgCapability capability);


/**
 * drv_SecCfgInit Initialize the secure configuration driver. 
 *
 * Loads file into memory, but does not verify its contents 
 */
void drv_SecCfgInit(void);


/**
 * drv_SecCfgStart Validates and parses configuration file
 */
void drv_SecCfgStart(void);


/**
 * drv_SecCfgCreateFile Given parameters, encode a configuration file
 *
 * @param hsdpa      The HSDPA category to encode
 * @param hsupa      The HSUPA category to encode
 * @param pmic       The PMIC value to encode
 * @param cm         The CM value to encode
 * @param output     Pointer to character pointer which will receive encoded file contents
 * @param output_len Pointer to integer which will receive the length of the output 
 * @return 1 if successful, 0 otherwise. On failure, *output is NULL and *output_len is 0
 * @note The memory is allocated by malloc, and needs to be freed by the user
 */
int drv_SecCfgCreateFile(int hsdpa, int hsupa, int pmic, int cm, char **output, int *output_len);


/**
 * drv_SecCfgSetFromFile From an encoded file, set the internal configuration parameters
 *
 * @param buffer The encoded file contents
 * @param len The number of bytes in the buffer
 * @return 1 if parsed successfully, 0 otherwise
 */
int drv_SecCfgSetFromFile(char *buffer, int len);


/**
 * drv_SecureConfigHspaCatCheck Check the secure configuration file
 *
 * @param fileOk Pointer to integer which will contain TRUE if the configuration file is OK, otherwise FALSE
 * @param hsdpa Pointer to integer which will contain the configured max HSDPA category
 * @param hsupa Pointer to integer which will contain the configured max HSUPA category
 * @return TRUE if secure configuration is enabled, FALSE if not
 * @see DRV_SecCfgCapability
 */
int drv_SecureConfigHspaCatCheck(int *fileOk, int *hsdpa, int *hsupa);

#endif

/** @} END OF FILE */

