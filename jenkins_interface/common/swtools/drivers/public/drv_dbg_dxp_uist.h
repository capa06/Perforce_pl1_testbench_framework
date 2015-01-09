/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dbg_dxp_uist.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup DbgDriver
 * @{
 */

/**
 * @file drv_dbg_dxp_uist.h DXP UISTs Debug interface.
 *
 */

#ifndef DRV_DBG_DXP_UIST_H
#define DRV_DBG_DXP_UIST_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_machine.h"
#include "mphal_gut.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_DBG_DXP_UIST_RECORD_INDEX_BITS (10)
/** Maximum number of records in the ring */
#define DRV_DBG_DXP_UIST_MAX_RECORDS       (1<<DRV_DBG_DXP_UIST_RECORD_INDEX_BITS)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/** UIST Record */
typedef struct {
    uint32 instance;
    uint32 value;
    drv_dbg_dxp_uist_type type;
    uint32 pc;
    enum com_DxpInstance dxp;
    uint32 timestamp_CET; /* normally 15.36 MHz, can be different for special builds (like TB) */
    uint32 timestamp_32k;
} drv_dbg_dxp_uist_record;

/** UIST Records Structure */
typedef struct {
    uint32 index;
    uint32 start;
    uint32 total;
    uint32 max_records;
    mphalgutt_Handle * gut_hdl;
    char *threadnames; /* pointer to thread names array in uncached memory, used for UBT over UISTs */
    drv_dbg_dxp_uist_record records[ DRV_DBG_DXP_UIST_MAX_RECORDS ];
} drv_dbg_dxp_uist_records_struct;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public constant declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/** Return the address of the UISTs buffer for the specified DXP
 *
 * @param dxp_instance          Which DXP
 *
 * @return                      Address of the UISTs buffer
 *
 */
drv_dbg_dxp_uist_records_struct * drv_DbgDxpUistsGetBuffer( int dxp_instance );

/** 
 *  Enable UISTs logging to RAM
 */
void drv_DbgEnableUistsLoggingToRam(void);


/** 
 *  Disable UISTs logging to RAM
 */
void drv_DbgDisableUistsLoggingToRam(void);

#endif /* #ifdef DRV_DBG_DXP_UIST_H */

/** @} END OF FILE */
