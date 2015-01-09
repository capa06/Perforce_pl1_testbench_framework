/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_pinmux.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup TopPinMux Pinmux Driver
 * @ingroup BoardLevelDrv
 */

/**
 * @addtogroup TopPinMux
 * @{
 */

/**
 * @file drv_pinmux.h Pinmux driver interfaces.
 *
 */

#ifndef DRV_PINMUX_H
#define DRV_PINMUX_H

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

/* List of pinmux configurations */
enum DrvPinmuxCfgId
{
    DEFAULT_PINMUX_CFG_ID,
    USB_HIBERNATE_PINMUX_CFG_ID,

    /* Pinmux config to use UART RX platform as an input I/O for UART H/W detection */
    UART_HIF_DETECT_PINMUX_CFG_ID, 
    LAST_PINMUX_CFG_ID
};

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/*
 * Initialise the Pinmux driver; this write the default pinmux configuration
 */
extern void drv_PinmuxInit(void);

/*
 * Re-Initialise the Pinmux driver; this write the current pinmux configuration
 */
extern void drv_PinmuxReInit(void);

/*
 * Save pinmux settings before hibernate.
 */
extern void drv_PinmuxPreHibernateSave(void);

/*
 * Restore pinmux settings after hibernate.
 */
extern void drv_PinmuxPostHibernateRestore(void);

/*
 * Take the pinmux resource and reconfigure the pinmux.
 * The pinmux resource remains locked until an explicit call to drv_PinmuxRelease()
 *
 * @param pinmux_cfg the pinmux configuration to apply.
 */
extern void drv_PinmuxTakeAndSet(enum DrvPinmuxCfgId pinmux_cfg);

/*
 * Release the pinmux resource.
 *
 * @param pinmux_cfg the pinmux configuration that was applied when the resource was locked.
 */
extern void drv_PinmuxRelease(enum DrvPinmuxCfgId pinmux_cfg);

/*
 * Get the current pinmux configuration.
 *
 * @return the current pinmux configuration
 */
extern enum DrvPinmuxCfgId drv_PinmuxGetCurrentConfig(void);

/*
 * Get the current pinmux status.
 *
 * @return the current pinmux status (in use)
 */
extern bool drv_PinmuxInUse(void);

#endif

/** @} END OF FILE */
