/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_mac_stats.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup UsbDriver
 * @{
 */

/**
 * @file drv_usb_mac.h USB MAC functions definitions
 *
 */

#ifndef DRV_USB_MAC_STATS_H
#define DRV_USB_MAC_STATS_H

/*************************************************************************************************
 * Types
 ************************************************************************************************/
/** USB Statistics Additional values index */
typedef enum {
    DRV_USB_MAC_STATISTICS_ADDITIONAL_NB
} drv_UsbMacStatisticsAdditionalIndex;

/*************************************************************************************************
 * Constants
 ************************************************************************************************/

/*************************************************************************************************
 * Exported Functions
 ************************************************************************************************/

/**
 * Initialize USB MAC Statistics
 *
 */
void drv_UsbMacStatsInit( void );

/**
 * Stop the USB MAC Statistics (in case of Suspend)
 */
void drv_UsbMacStatsStop( void );

/**
 * Starts the USB MAC Statistics (after Resume)
 */
void drv_UsbMacStatsStart( void );

/**
 * Inform a value for additional statistic
 *
 * @param index     Additional Statistic index
 * @param value     Value to add for the statistic
 *
 */
void drv_UsbMacStatsInfoAdditional( uint32 index, uint32 value );

/**
 * Inform a USB suspend has occurred
 */
void drv_UsbMacStatsInfoSuspendComplete( void );

/**
 * Inform a USB resume has occurred
 */
void drv_UsbMacStatsInfoResumeComplete( void );

/**
 * Inform a USB remote wakeup resume has occurred
 */
void drv_UsbMacStatsInfoRemoteWakeupComplete( void );

/**
 * Inform a USB enumeration has occurred
 */
void drv_UsbMacStatsInfoEnumerationComplete( void );

/**
 * Inform a USB endpoint error has occurred
 */
void drv_UsbMacStatsInfoEpError( void );

/**
 * Register a function that will be called everytime statistics
 * are displayed. This allows adding debug logpoints.
 *
 * @param function      function to be called
 * @param arg           argument that will be passed
 *                      transparently to the function
 *
 */
void drv_UsbMacStatsRegisterCb( void (*function)(void *arg), void *arg );

#endif /* #ifndef DRV_USB_MAC_STATS_H */

/** @} END OF FILE */
