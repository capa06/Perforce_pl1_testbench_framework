/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_sar.h#1 $
 * $Date: 2014/11/13 $
 * $Revision: #1 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup SARDriver SAR Driver
 */

/**
 * @addtogroup SARDriver
 * @{
 */

/**
 * @file drv_sar.h SAR Driver interface 
 * 
 */

#ifndef DRV_SAR_H
#define DRV_SAR_H

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
 *  Type definition for the SAR detect notification callback
 *
 *  The notification callback is called when the SAR condition changes
 *  It is called in the context of an interrupt service routine and must *NOT* block.
 *
 *  @param value     one if SAR condition detected, else zero
 */
typedef void (*drv_SarDetCallback)(uint32 value);

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * Initialise the SAR detect I/O driver
 *
 * This configures the I/O, enables extWake events on the I/O
 * and registers an interrupt handler to dispatch I/O toggle
 * notifications to a registered listener
 *
 * @see drv_SarDetRegisterNotificationCallback()
 * @return none
 */
extern void drv_SarDetInit(void);

/**
 * Register a notification callback for the SAR detect I/O
 *
 * @see drv_SarDetCallback
 * @param callback Pointer to the notification callback
 * @return none
 */
extern void drv_SarDetRegisterNotificationCallback(drv_SarDetCallback callback);

/**
 * Unregister a notification callback for the SAR detect I/O
 *
 * @see drv_SarDetCallback
 * @param none
 * @return none
 */
extern void drv_SarDetUnregisterNotificationCallback(void);

/**
 * Return a boolean indicating if driver is ready
 *
 * @see drv_SarIsInitialized
 * @param none
 * @return boolean : 1 if ready.
 *                 : 0 if not ready
 */
extern bool drv_SarIsInitialized();
#endif

/** @} END OF FILE */
