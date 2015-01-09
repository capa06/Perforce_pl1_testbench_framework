/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_tbdummy.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup SerialDriver
 * @{
 */

/**
 * @file drv_serial_tbdummy.h Serial Uart Driver API Functions definitions.
 */

#ifndef DRV_SERIAL_TBDUMMY_H
#define DRV_SERIAL_TBDUMMY_H

#include "drv_serial.h"


/******************************************************************************
 * Exported defines
 ******************************************************************************/

#define DRV_SERIAL_TBDUMMY_NUM_IFS 1

/******************************************************************************
 * Exported Variables
 ******************************************************************************/

extern DXP_CACHED_UNI1 drv_serial_ops_t drv_serial_tbdummy_ops;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

extern drv_serial_index_e drv_SerialTbdummyGetHookup(uint32 phy_index);
extern void drv_SerialTbdummyStartAtCommands(void);

#endif /* #ifndef DRV_SERIAL_TBDUMMY_H */

/** @} END OF FILE */
