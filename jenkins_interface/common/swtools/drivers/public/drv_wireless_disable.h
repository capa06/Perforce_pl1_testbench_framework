/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_wireless_disable.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup DrvWirelessDisable
 * @{
 */

/**
 * @file drv_wireless_disable.h Wireless Disable Driver
 *       Interface
 *
 */

#ifndef DRV_WIRELESS_DISABLE_H
#define DRV_WIRELESS_DISABLE_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "drv_sync_rtc_cet.h"
#include "drv_clocks.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** indication of an error in the wireless disable API */
#define DRV_WIRELESS_DISABLE_ERROR (-1)

/** when an edge is detected on the wireless disable I/O, a
 * timer is started to later check the state of the I/O in order
 * to filter glitches out. The following setting is the duration
 * (in milliseconds) of the timer
 */
#define DRV_WIRELESS_DISABLE_DEBOUNCE_LATENCY_MS (30)

/** when a bounce is detected a new timer is started. Every
 *  bounce causes the timeout to be multiplied by two up to a
 *  certain limit, defined by the below identifier
 */
#define DRV_WIRELESS_DISABLE_MAX_BOUNCE_DOUBLES (7)

/**
 * minimum time (in milliseconds) required between the last
 * detected to claim the I/O has settled. make it less than the
 * above latency in order to cope with a laxist GUT low res */
#define DRV_WIRELESS_DISABLE_DEBOUNCE_MIN_STILL_TIME_MS (40)

/**
 *  same as DRV_WIRELESS_DISABLE_DEBOUNCE_MIN_STILL_TIME_MS, but
 *  expressed in system (CET) ticks, rather than milliseconds
 */
#define DRV_WIRELESS_DISABLE_DEBOUNCE_LATENCY_SYSTEM_TICKS \
    (DRV_WIRELESS_DISABLE_DEBOUNCE_MIN_STILL_TIME_MS*DRV_CET_CLK_SPEED_KHZ)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  Type definition for the Wireless Disable I/O toggle
 *  notification callback
 *
 *  The notification callback is called when the wireless disable
 *  I/O toggles. It is called in the context of an interrupt
 *  service routine and must *not* block.
 *
 *  @param id        The I/O id (should always be
 *                   IO_WWAN_DISABLE_N), other values reserved
 *                   for further use
 *  @param value     zero or non-zero value, depending on the
 *                   I/O state
 */
typedef void (*drv_WirelessDisableCallback)(uint32 id, uint32 value);

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * Initialise the Wireless Disable I/O driver
 *
 * This configures the I/O, enables extWake events on the I/O
 * and registers an interrupt handler to dispatch I/O toggle
 * notifications to a registered listener
 *
 * @see drv_WirelessDisableRegisterNotificationCallback()
 * @return none
 */
extern void drv_WirelessDisableInit(void);

/**
 * Register a notification callback for the Wireless Disable I/O
 *
 * @see drv_WirelessDisableCallback
 * @param callback Pointer to the notification callback
 * @return none
 */
extern void drv_WirelessDisableRegisterNotificationCallback(drv_WirelessDisableCallback callback);

/**
 *  Returns the state of the wireless disable I/O
 *  @param id I/O ID
 *  @return state of the I/O (zero or non-zero), or
 *               DRV_WIRELESS_DISABLE_ERROR in case an error
 *               occurred
 */
extern int32 drv_WirelessDisableGetState(uint32 id);

#endif /* #ifndef DRV_WIRELESS_DISABLE_H */
/** @} END OF FILE */


