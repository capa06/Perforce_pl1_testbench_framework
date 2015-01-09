/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006-2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_phy.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup UsbDriver
 * @{
 */

/**
 * @file drv_usb_phy.h USB PHY Register access functions definitions
 *
 */

#ifndef DRV_USB_PHY_H
#define DRV_USB_PHY_H

#include "drv_usb_mac.h"
/******************************************************************************
 * Constants
 ******************************************************************************/

/******************************************************************************
 * Exported macros
 ******************************************************************************/

/******************************************************************************
 * Exported types
 ******************************************************************************/
typedef unsigned (*drv_UsbStatePoll)( void * handle );

typedef struct drv_UsbPhyPoll {
    /** Resume Software Interrupt */
    drv_UsbStatePoll    poll_cb;
    void*               arg;
} drv_UsbPhyPoll_t;

typedef enum {
    DRV_USB_PHY_TYPE_SYNOPSYS = 0,
    DRV_USB_PHY_TYPE_HSIC,
    DRV_USB_PHY_TYPE_INVALID
} usb_phy_select;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Initializes the USB PHY
 */
void drv_UsbPhyInit();

/**
 * Check if ULPI bus is working properly.
 * This function checks that ULPI CLK is valid otherwise the write/read will fail.
 * It also checks that all bits can be either 0 or 1.
 */
int drv_UsbPhyCheckUlpiBus();

/**
 * Place the USB PHY into it's lowest possible power state when the PHY supports is.
 * This function is intended for use in applications which do not use the on-chip PHY.
 * Calling this function from applications which use the on-chip PHY provoke a deliberate link failure.
 */
void drv_UsbPhyPowerDown( void);

/**
 * Enables the Polling of the Usb Phy for USB Phy supporting it
 *
 * @param arg Private handle for the caller
 */
void drv_UsbPhyPollInit(drv_UsbPhyPoll_t* usbPhyPoll );

/**
 * Configure the USB PHY
 */
void drv_UsbPhyConfigure();

/**
 * Wrapper function for drv_UsbPhyPreReset();
 */
void drv_UsbPhyPreResetWrapper();

/**
 * Wrapper function for drv_UsbPhySuspend();
 */
void drv_UsbPhySuspendWrapper();

/**
 * Wrapper function for drv_UsbPhySuspend();
 */
void drv_UsbPhyResumeWrapper();

/**
 * Shut down unused USB PHY power supplies.
 */
void drv_UsbPhyDisableUnusedSupplies();

/**
 * Turn off any USB PHY related power supplies which are not 
 * needed and activate the ones that are required
 */
void drv_UsbPhyConfigureLDOSupplies();

#endif /* #ifndef DRV_USB_PHY_H */

/** @} END OF FILE */
