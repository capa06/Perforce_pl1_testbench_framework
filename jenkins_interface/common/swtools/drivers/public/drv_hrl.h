/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_hrl.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup HrlDriver HRL Driver
 * @ingroup SoCLowLevelDrv
 * HRL (Hardware Regulated Latency) driver
 */

/**
 * @addtogroup HrlDriver
 * @{
 */

/**
 * @file drv_hrl.h Basic HRL driver public interface
 *
 */

#ifndef DRV_HRL_H
#define DRV_HRL_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

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
 * HRL instances enumeration
 */
typedef enum
{
    DRV_HRL_INSTANCE_HRL0,
    DRV_HRL_INSTANCE_HRL1,
    DRV_HRL_INSTANCE_NUM
} drv_HrlInstance;

/**
 * HRL handle
 */
typedef void *drv_HrlHandle;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Opens HRL instance and locks it for exclusive use.
 *
 * @param hrl_fifo HRL instance id.
 *
 * @return HRL instance handle.
 */
extern drv_HrlHandle drv_HrlOpen(drv_HrlInstance hrl_instance);

/**
 * Closes HRL instance and unlocks it.
 *
 * @param handle HRL instance handle.
 *
 * @return void.
 */
extern void drv_HrlClose(drv_HrlHandle handle);

/**
 * Check Ready status for an HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return true if Ready
 */
extern bool drv_HrlGetReadyStatus(drv_HrlHandle handle);

/**
 * Check Empty status for an HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return true if Empty
 */
extern bool drv_HrlGetEmptyStatus(drv_HrlHandle handle);

/**
 * Check SIC miss status for an HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return true if SIC missed
 */
extern bool drv_HrlGetSicMissStatus(drv_HrlHandle handle);

/**
 * Clear Status for an HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return true if SIC missed
 */
extern void drv_HrlClearStatus(drv_HrlHandle handle);

/**
 * Resets an HRL instance.
 *
 * @param handle  HRL instance handle.
 *
 */
extern void drv_HrlSWReset(drv_HrlHandle handle );

/**
 * Triggers by software the HRL instance.
 *
 * @param handle  HRL instance handle.
 * @param size Number of pairs to trigger
 *
 */
extern void drv_HrlSWTrigger(drv_HrlHandle handle, uint32 size );

/**
 * Gets FIFO address for HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return FIFO addressfor the HRL instance.
 */
extern uint32 drv_HrlGetFifoAddr(drv_HrlHandle handle);

/**
 * Gets DMA request id for HRL instance.
 *
 * @param handle HRL instance handle.
 *
 * @return DMA request id for the HRL instance.
 */
extern uint32 drv_HrlGetFifoDmaReqId(drv_HrlHandle handle);

/**
 * Reprogram HRLs that are in use after hibernation power up.
 *
 * @return void.
 */
extern void drv_HrlPostHibPowerUp(void);

#endif /* DRV_HRL_H */

/** @} END OF FILE */

