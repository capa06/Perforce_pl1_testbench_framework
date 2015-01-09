/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup UsbDriver
 * @{
 */

/**
 * @file drv_usb.h USB public interface
 *
 */

#ifndef DRV_USB_H
#define DRV_USB_H

/******************************************************************************
 * Project header files
 ******************************************************************************/
#include "icera_global.h"

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Reset the USB like after a power cycle, so that it is ready
 * to enumerate like the first time.
 */
void drv_UsbResetToBootState(void);

#endif /* #ifndef DRV_USB_H */

/** @} END OF FILE */
