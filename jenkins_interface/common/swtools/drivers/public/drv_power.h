/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_power.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup HwPlatform
 * @{
 */

/**
 * @file drv_power.h
 *
 */

#ifndef DRV_POWER_H
#define DRV_POWER_H

#include "icera_global.h"
#include "drv_pmic.h"

/******************************************************************************
 * Macros
 ******************************************************************************/
#define POWER_SET_PA_VOLTAGE(high, low, callback, callback_param)       drv_power_SetPaVoltage(high, low, callback, callback_param)
#define POWER_SET_RF_VOLTAGE(dcdc, vcc, callback, callback_param)       drv_power_SetRfVoltage(dcdc, vcc, callback, callback_param)

/******************************************************************************
 * Exported types
 ******************************************************************************/

/******************************************************************************
 * Exported Functions
 ******************************************************************************/
/*****************************************/
/* Public Power configuration functions. */
/* Allow the customer to configure their */
/* Power configuration                   */
/*****************************************/
extern void drv_power_SetPaVoltage(uint32 high, uint32 low, drv_PmicCb callback, void * callback_param);
extern void drv_power_SetRfVoltage(drv_PmicRfDcDc dcdc, uint32 vcc, drv_PmicCb callback, void * callback_param);

#endif /* #ifndef DRV_POWER_H */

/** @} END OF FILE */
