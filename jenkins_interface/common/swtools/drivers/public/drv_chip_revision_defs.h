/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2009-2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_chip_revision_defs.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup Top
 * @{
 */

/**
 * @file drv_chip_revision.h Public definitions of Chip Revision eFuse usage.
 */

#ifndef DRV_CHIP_REVISION_DEFS_H
#define DRV_CHIP_REVISION_DEFS_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "chpc_cdefs.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** eFuse locations within CHPC register space */
#if defined (ICE9XXX_PMSS)
#define PROD_ENG_0_EFUSE_OFFSET (5)
#define PROD_ENG_1_EFUSE_OFFSET (6)
#endif

/** PROD_ENG_0_EFUSE encoding */
#if defined (ICE9XXX_PMSS)
#define PROD_ENG_0_EFUSE_HW_ID_SCHEME_SHIFT    (CHPC_EFUSE_STATE_5_HWIDSCHEME_SHIFT)
#define PROD_ENG_0_EFUSE_HW_ID_SCHEME_MASK     (CHPC_EFUSE_STATE_5_HWIDSCHEME_MASK)

#endif

/**
 * HW_ID_SCHEME encoding
 */
#define DRV_CHIP_REV_HW_ID_SCHEME0             (0)
#define DRV_CHIP_REV_HW_ID_SCHEME1             (1)
#define DRV_CHIP_REV_HW_ID_NULL_SCHEME         (-1) /* Used to fill spaces in the table */

#define DRV_CHIP_REV_HW_ID_NUM_SCHEMES         (2)

/*************************************************************************************************
 * HW_ID_SCHEME 0x00
 ************************************************************************************************/
/**
 *                            ||     ICE1210 (Livanto) Revision
 *                               ||  ICE1410 (Trinitario) Revision
 */
typedef enum {
    DRV_CHIP_REV_SCHEME0_8040_A0_A0 = 0, /* Not a production device */
    DRV_CHIP_REV_SCHEME0_8040_A1_A0 = 1, /* Not a production device */
    DRV_CHIP_REV_SCHEME0_8040_A2_A0 = 2, /* Not a production device */
    DRV_CHIP_REV_SCHEME0_8040_A2_B0 = 3,
    DRV_CHIP_REV_SCHEME0_8040_A2_B1 = 4,
    DRV_CHIP_REV_SCHEME0_8040_A3_A1 = 5,
    DRV_CHIP_REV_SCHEME0_8040_B0_B1 = 6,

    DRV_CHIP_REV_SCHEME0_NUM_IDS
} drv_ChipRevScheme0Ids;

/*************************************************************************************************
 * HW_ID_SCHEME 0x01
 ************************************************************************************************/
/**
 * PROD_ENG_1_EFUSE Encoding for SCHEME 1
 */
#if defined (ICE9XXX_PMSS)
#define PROD_ENG_1_EFUSE_SCHEME1_NUM_DIE_SHIFT       (CHPC_EFUSE_STATE_6_CHIPREVS1NUMDIE_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_NUM_DIE_MASK        (CHPC_EFUSE_STATE_6_CHIPREVS1NUMDIE_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_1_VERSION_SHIFT (CHPC_EFUSE_STATE_6_CHIPREVS1DIE1VERSION_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_1_VERSION_MASK  (CHPC_EFUSE_STATE_6_CHIPREVS1DIE1VERSION_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_2_ID_SHIFT      (CHPC_EFUSE_STATE_6_CHIPREVS1DIE2ID_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_2_ID_MASK       (CHPC_EFUSE_STATE_6_CHIPREVS1DIE2ID_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_2_VERSION_SHIFT (CHPC_EFUSE_STATE_6_CHIPREVS1DIE2VERSION_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_2_VERSION_MASK  (CHPC_EFUSE_STATE_6_CHIPREVS1DIE2VERSION_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_3_ID_SHIFT      (CHPC_EFUSE_STATE_6_CHIPREVS1DIE3ID_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_3_ID_MASK       (CHPC_EFUSE_STATE_6_CHIPREVS1DIE3ID_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_3_VERSION_SHIFT (CHPC_EFUSE_STATE_6_CHIPREVS1DIE3VERSION_SHIFT)
#define PROD_ENG_1_EFUSE_SCHEME1_DIE_3_VERSION_MASK  (CHPC_EFUSE_STATE_6_CHIPREVS1DIE3VERSION_MASK)
#define PROD_ENG_1_EFUSE_SCHEME1_SILICONTYPE_SHIFT   (24)
#define PROD_ENG_1_EFUSE_SCHEME1_SILICONTYPE_MASK    (0x03)

#endif

/**
 * Part Number codes for Livanto and Vivalto devices.
 */
typedef enum {
    DRV_CHIP_REV_LIV123_PARTNUM = 0,
    DRV_CHIP_REV_VIV1_PARTNUM   = 2,
    DRV_CHIP_REV_BBC1_PARTNUM   = 2,
    DRV_CHIP_REV_NUM_LIV_PARTNUMS
} drv_ChipRevLivPartNum;

/**
 * Version codes for Livanto and Vivalto devices.
 */
typedef enum {
    DRV_CHIP_REV_LIV1_VERSION    = 0,
    DRV_CHIP_REV_VIV1_VERSION    = 0,
    DRV_CHIP_REV_BBC1_VERSION    = 1,
    DRV_CHIP_REV_LIV2_VERSION    = 2,
    DRV_CHIP_REV_LIV3_VERSION    = 3,
    DRV_CHIP_REV_NUM_LIV_VERSIONS
} drv_ChipRevLivVersion;

/**
 * Derived ID chip ID code.
 */
typedef enum {
    DRV_CHIP_REV_UNKNOWN_ID = 0,
    DRV_CHIP_REV_LIV1_ID = 1,
    DRV_CHIP_REV_LIV2_ID = 2,
    DRV_CHIP_REV_LIV3_ID = 3,
    DRV_CHIP_REV_VIV1_ID = 4,
    DRV_CHIP_REV_BBC1_ID = 5,
    DRV_CHIP_REV_NUM_LIV_IDS
} drv_ChipRevLivId;

/**
 * ID codes for devices which may be stacked with Livanto.
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_STACKED_NONE_ID              = 0,
    DRV_CHIP_REV_SCHEME1_STACKED_TRIN1_ID             = 1,
    DRV_CHIP_REV_SCHEME1_STACKED_TRIN2_ID             = 2,
    DRV_CHIP_REV_SCHEME1_STACKED_VULCAN1_ID           = 3,
    DRV_CHIP_REV_SCHEME1_STACKED_TRIN3_ID             = 4,
    DRV_CHIP_REV_SCHEME1_STACKED_HYNIX_H5MS2562JKA_ID = 5,
    DRV_CHIP_REV_SCHEME1_NUM_STACKED_IDS
} drv_ChipRevScheme1StackedId;

/**
 * Livanto 1 (ICE1200):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_LIV1_VERSION_A0    = 0,
    DRV_CHIP_REV_SCHEME1_LIV1_VERSION_A1    = 1,
    DRV_CHIP_REV_SCHEME1_LIV1_VERSION_A2    = 2,
    DRV_CHIP_REV_SCHEME1_LIV1_VERSION_A3    = 3,
    DRV_CHIP_REV_SCHEME1_LIV1_VERSION_A4    = 4,
    DRV_CHIP_REV_SCHEME1_LIV1_NUM_VERSIONS
} drv_ChipRevScheme1Liv1Version;

/**
 * Livanto 2 (ICE1210):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_LIV2_VERSION_A0    = 0,
    DRV_CHIP_REV_SCHEME1_LIV2_VERSION_A1    = 1,
    DRV_CHIP_REV_SCHEME1_LIV2_VERSION_A2    = 2,
    DRV_CHIP_REV_SCHEME1_LIV2_VERSION_A3    = 3,
    DRV_CHIP_REV_SCHEME1_LIV2_VERSION_B0    = 4,
    DRV_CHIP_REV_SCHEME1_LIV2_NUM_VERSIONS
} drv_ChipRevScheme1Liv2Version;

/**
 * Livanto3 (ICE1220):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_LIV3_VERSION_A0    = 0,
    DRV_CHIP_REV_SCHEME1_LIV3_VERSION_A1    = 1,
    DRV_CHIP_REV_SCHEME1_LIV3_VERSION_A2    = 2,
    DRV_CHIP_REV_SCHEME1_LIV3_NUM_VERSIONS
} drv_ChipRevScheme1Liv3Version;

/**
 * Vivalto1 (ICE904x):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_VIV1_VERSION_A01   = 0,
    DRV_CHIP_REV_SCHEME1_VIV1_VERSION_A02   = 1,
    DRV_CHIP_REV_SCHEME1_VIV1_VERSION_A02P  = 2,
    DRV_CHIP_REV_SCHEME1_VIV1_NUM_VERSIONS
} drv_ChipRevScheme1Viv1Version;

/**
 * Vivalto1 (ICE904x):
 *   Silicon type ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_VIV1_TYPE_NOMINAL  = 0,
    DRV_CHIP_REV_SCHEME1_VIV1_TYPE_FAST     = 1,
    DRV_CHIP_REV_SCHEME1_VIV1_NUM_TYPES
} drv_ChipRevScheme1Viv1Type;

/**
 * BBC1:
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_BBC1_VERSION_UNFUSED = 0,
    DRV_CHIP_REV_SCHEME1_BBC1_VERSION_A01     = 1,
    DRV_CHIP_REV_SCHEME1_BBC1_VERSION_A02     = 2,
    DRV_CHIP_REV_SCHEME1_BBC1_NUM_VERSIONS
} drv_ChipRevScheme1Bbc1Version;

/**
 * Trinitario1 (ICE1400):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_TRIN1_VERSION_A0   = 0,
    DRV_CHIP_REV_SCHEME1_TRIN1_VERSION_B0   = 1,
    DRV_CHIP_REV_SCHEME1_TRIN1_VERSION_B1   = 2,
    DRV_CHIP_REV_SCHEME1_TRIN1_NUM_VERSIONS
} drv_ChipRevScheme1Trin1Version;

/**
 * Trinitario2 (ICE1410):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_TRIN2_VERSION_A0   = 0,
    DRV_CHIP_REV_SCHEME1_TRIN2_VERSION_B0   = 1,
    DRV_CHIP_REV_SCHEME1_TRIN2_VERSION_B1   = 2,
    DRV_CHIP_REV_SCHEME1_TRIN2_NUM_VERSIONS
} drv_ChipRevScheme1Trin2Version;

/**
 * Trinitario3 (ICE1420):
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_TRIN3_VERSION_A0   = 0,
    DRV_CHIP_REV_SCHEME1_TRIN3_NUM_VERSIONS
} drv_ChipRevScheme1Trin3Version;

/**
 * Vulcan
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_VULCAN_VERSION_A0  = 0,
    DRV_CHIP_REV_SCHEME1_VULCAN_VERSION_A1  = 1,
    DRV_CHIP_REV_SCHEME1_VULCAN_VERSION_B0  = 2,
    DRV_CHIP_REV_SCHEME1_VULCAN_VERSION_B1  = 3,
    DRV_CHIP_REV_SCHEME1_VULCAN_VERSION_C0  = 4,
    DRV_CHIP_REV_SCHEME1_VULCAN_NUM_VERSIONS
} drv_ChipRevScheme1VulcanVersion;

/**
 * Hynix H5MS2562JKA Memory
 *   Silicon revision ID codes
 */
typedef enum {
    DRV_CHIP_REV_SCHEME1_HYNIX_H5MS2562JKA_VERSION_1 = 0,
    DRV_CHIP_REV_SCHEME1_HYNIX_H5MS2562JKA_NUM_VERSIONS
} dev_ChipRevScheme1HynixH5ms2562jkaVersion;

#define DRV_CHIP_REV_UNUSED (-1)

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

#endif

/** @} END OF FILE */

