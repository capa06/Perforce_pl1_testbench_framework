/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_mac.h#1 $
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

#ifndef DRV_USB_MAC_H
#define DRV_USB_MAC_H

/******************************************************************************
 * Project header files
 ******************************************************************************/
#include "icera_global.h"

/******************************************************************************
 * Types
 ******************************************************************************/

/** USB MAC Handle */
typedef void * drv_UsbMacHandle;

/** USB MAC Interrupt Handler
 *
 * @param nkH           nanoK Init handler, defined for sole compatibility with os_RegisterIntHandler. Unused.
 * @param thrDataPtr    Data pointer passed to the interrupt handler.
 * @param intcStatus    interrupt controller status, defined for sole compatibility with os_RegisterIntHandler. Unused.
 */
typedef void (*drv_UsbMacInterruptHandler)( void * nkH, void * thrDataPtr, uint32 intcStatus );

/**
 * Handle USB Suspend
 *
 * @param handle        Handle to the USB MAC
 *
 */
typedef void (*drv_UsbMacHandleSuspend)( drv_UsbMacHandle handle );

/**
 * Handle USB Remote Wakeup
 *
 * @param handle        Handle to the USB MAC
 *
 */
typedef void (*drv_UsbMacHandleRemoteWakeup)( drv_UsbMacHandle handle );

/**
 * Recover from unexpected bus RESET (currently used for http://nvbugs/1262501)
 *
 * @param handle        Handle to the USB MAC
 *
 */
typedef void (*drv_UsbMacRecoverFromUnexpectedReset)( drv_UsbMacHandle handle );

/** Power Management specific USB MAC -> USB Stack callbacks */
typedef struct {
    drv_UsbMacHandleSuspend                     handle_suspend;
    drv_UsbMacHandleRemoteWakeup                handle_remote_wakeup;
    drv_UsbMacRecoverFromUnexpectedReset        recover_from_reset;
} drv_UsbStackUsbMacPowerMgmtCBs;

/**
 * USB Stack Resume Software Interrupt
 *  The function need to call its internal resume function.
 *
* @param handle        Pointer to the USB Stack driver handle
*
*/
typedef void (*drv_UsbStackResumeSwInt)( void * handle );

/** Power Management specific USB Stack -> USB MAC callbacks */
typedef struct {
    /** Resume Software Interrupt */
    drv_UsbStackResumeSwInt     resume_sw_int;
} drv_UsbMacUsbStackPowerMgmtCBs;


/******************************************************************************
 * Constants
 ******************************************************************************/

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Initialize the USB MAC
 */
void drv_UsbMacInitialise( void );

/**
 * Register the USB MAC driver callbacks for Power Management
 *
 * @param cbs_mac_stk   Pointer to USB MAC driver callbacks USB MAC -> USB Stack
 * @param cbs_stk_mac   Pointer to USB Stack driver callbacks USB Stack -> USB MAC filled by function
 * @param stk_handle    Pointer to the USB Stack Driver handle
 *
 */
void drv_UsbMacRegisterPowerManagement(const drv_UsbMacUsbStackPowerMgmtCBs * cbs_mac_stk,
                                       drv_UsbStackUsbMacPowerMgmtCBs       * cbs_stk_mac,
                                       void                                 * stk_handle);

/**
 * Registers the interrupt handler to the USB MAC Interrupt
 *
 * @param interrupt_cb  Pointer to the Interrupt Handler function
 * @param inth_data     Pointer to data to be passed to the interrupt handler
 *
 * @return              false if failed to register
 *
 */
bool drv_UsbMacRegisterInterruptHandler(drv_UsbMacInterruptHandler   interrupt_cb,
                                        void                       * inth_data,
                                        int                          isr_index);

/**
 * UnRegisters the interrupt handler to the USB MAC Interrupt
 */
void drv_UsbMacUnRegisterInterruptHandler(int isr_index);


#endif /* #ifndef DRV_USB_MAC_H */

/** @} END OF FILE */
