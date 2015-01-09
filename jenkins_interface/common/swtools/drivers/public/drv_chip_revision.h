/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_chip_revision.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup ChipRevisionIDs
 * Definitions of Chip Revision IDs, (eventually) auto-generated from Product Engineering master
 * documents.
 */

/**
 * @addtogroup ChipRevisionIDs
 * @{
 */

/**
 * @file drv_chip_revision.h Public definitions of Chip Revision eFuse usage.
 */

#ifndef DRV_CHIP_REVISION_H
#define DRV_CHIP_REVISION_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_chip_revision_defs.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#define DRV_CHIP_REV_INIT_MAGIC (0xcafebabe)

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
typedef struct {
    uint8 hw_rev;            /** Hardware Revision. */
    uint8 die1_id;
} drv_ChipRevScheme0Data;

typedef struct {
    uint8 num_die;         /** Number of die. */
    uint8 die1_version;    /** Die 1 Version info. */
    uint8 die1_id;         /** Die 1 ID. */
    uint8 die1_type;       /** Die 1 Type. */
    uint8 die2_version;    /** Die 2 Version info. */
    uint8 die2_id;         /** Die 2 ID. */
    uint8 die3_version;    /** Die 3 Version info. */
    uint8 die3_id;         /** Die 3 ID. */
} drv_ChipRevScheme1Data;

typedef union {
    drv_ChipRevScheme0Data scheme0;
    drv_ChipRevScheme1Data scheme1;
} drv_ChipRevSchemeData;

typedef struct {
    uint8 scheme_id;
    drv_ChipRevSchemeData scheme_data;
    uint32 init_magic;
} drv_ChipRevHandle;

typedef struct {
    int8 schemes[DRV_CHIP_REV_HW_ID_NUM_SCHEMES];
    int8 die1_id;
    int8 scheme1_num_stacked;
    int8 scheme1_die2_id;
    int8 scheme1_die3_id;
} drv_ChipRevAllowedRevs;

typedef enum {
    DRV_CHIP_REV_ID_REQ = 0,
    DRV_CHIP_REV_VERSION_REQ,
    DRV_CHIP_REV_TYPE_REQ,  
    DRV_CHIP_REV_NUM_REQS
} drv_ChipRevRequest;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 *  Check Chip IDs, and compare them against the list of allowed devices provided in the
 *  hwplatform definition.  If a chip is found which is not allowed, this function will ASSERT.
 *  If all valid devices are found, then the function will return.
 */
void drv_ChipRevCheckIds();

/**
 *  Check a particular chip's Revision ID is greater than or equal to a specified value.
 *
 *  @param MinRevisionScheme0 - If revision ID scheme 0 is used, check that the device version is at
 *                              least as large as this value.
 *  @param ChipId - Specifies the ID code of the chip to be interrogated.
 *  @param MinRevisionScheme1 - If revision ID scheme 1 is used, check that the device with Chip ID
 *                              <ChipID> has it's version field set to at least this value.
 *
 *  @return - Returns a 0 if MinRevision > Revision ID from eFuses, otherwise returns a non-zero
 *            value.
 */
int drv_ChipRevCheckRevAtLeast(int MinRevisionScheme0, int ChipId, int MinRevisionScheme1);

/**
 *  Returns Chip silicon type (Vivalto)
 *
 *  @return - Chip silicon type (nominal / fast)
 */
drv_ChipRevScheme1Viv1Type drv_ChipRevGetDie1Type();

/**
 *  Return the number of die of the Processor chip and give
 *  information about die Id and version.
 *
 *  @param str - returned String giving the die Id or version
 *  @param die_number - Specifies the die number.
 *  @param id_or_rev - Specifies the request :
 *      DRV_CHIP_REV_ID_REQ to request the die Id
 *      DRV_CHIP_REV_VERSION_REQ to request the die version
 *      DRV_CHIP_REV_TYPE_REQ to request the die type (Vivalto1 only).
 *
 *  @return - Returns the total number of die in the chip
 */
int drv_ChipRevGetInfo(char *str, int die_number, drv_ChipRevRequest req);

#endif

/** @} END OF FILE */

