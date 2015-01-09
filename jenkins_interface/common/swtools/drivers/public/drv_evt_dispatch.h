
/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_evt_dispatch.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DrvEvtDispatch Driver Event Dispatcher 
 * @ingroup  HighLevelServices
 */

/**
 * @addtogroup DrvEvtDispatch
 * @{
 */

/**
 * @file drv_evt_dispatch.h Driver Event Dispatcher interface. 
 *       The Driver Event Dispatcher can be used to trigger
 *       events, or register a listener to a specific event
 */

#ifndef DRV_EVT_DISPATCH_H
#define DRV_EVT_DISPATCH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_machine.h"                /* machine definitions */

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
 *  enumeration of event codes 
 */
typedef enum 
{
    DRV_EVT_DISPATCH_CROSS_DXP_EVENT,            /** cross DXP event */
    DRV_EVT_DISPATCH_DFC,                        /** Deferred Function Call event */
} drv_EvtDispatchEventCode; 

/**
 *  enumeration of priority codes
 */
typedef enum 
{
    DRV_EVT_DISPATCH_PRIO_INVALID=0x1000,
    DRV_EVT_DISPATCH_PRIO_LOW,
    DRV_EVT_DISPATCH_PRIO_MEDIUM,
    DRV_EVT_DISPATCH_PRIO_HIGH,
} drv_EvtDispatchPrioCode; 

/**
 *  enumeration of blocking codes 
 */
typedef enum 
{
    DRV_EVT_DISPATCH_NOT_BLOCKING=0,
    DRV_EVT_DISPATCH_BLOCKING=1,
} drv_EvtDispatchBlockingCode;

/**
 * Type definition for an event callback.
 *
 * Event callbacks are called by the event dispatcher when an 
 * event is received 
 * 
 * Event callbacks must not block.
 * 
 * @param event      The nature of the event
 * @param bufin      Pointer to a buffer that contains
 *                   information required to perform the
 *                   operation - this buffer was orignally
 *                   passed by the event originator and copied
 *                   to a safe location by the event dispatcher
 *                   (this can be NULL)
 * @param bufinsize  Size, in bytes, of the buffer pointed to by
 *                   bufin
 * @param bufout     Pointer to a buffer that receives the 
 *                   output data for the operation - will be set
 *                   to NULL on a non-blocking cross DXP event
 *                   or on a DFC event
 * @param bufoutsize Size, in bytes, of the buffer pointed to by 
 *                   bufout - will be set to 0 on a non-blocking
 *                   cross DXP event or on a DFC event
 * @return           Custom return code
 */   
typedef int32 (*drv_EvtDispatchCallback)(drv_EvtDispatchEventCode event,void *bufin, uint32 bufin_size, void *bufout, uint32 bufout_size);

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialise the Driver Event Dispatcher 
 *  
 * This creates a multi-core queue and a task that infinitely 
 * waits for messages on the created multi-core queue 
 *  
 * @return none 
 */
extern void drv_EvtDispatchInit(void);

/** 
* Defer a function call to when interrupts are
* next unmasked, or immediately if this function
* is called when interrupts are already unmasked 
*  
* This function allows for prioritization of DFC through 
* the priority parameter. Priorities are used when there are 
* several DFCs in the queue to execute the most prioritised 
* first 
*  
* @param callback     The function to execute 
* @param priority     Priority  
* @param bufin        Pointer to a buffer that contains 
*                     information required to perform the
*                     operation (this can be NULL)
* @param bufin_size   Size, in bytes, of the buffer pointed to 
*                     by bufin
* @return             0
* @see drv_EvtDispatchPrioCode 
*/ 
extern int32 drv_EvtDispatchDeferredFunctionCall(
    drv_EvtDispatchCallback callback,
    drv_EvtDispatchPrioCode priority,
    void *bufin,
    uint32 bufin_size);

/** 
* Initiate a cross DXP event (for execution of code on the
* other DXP instance) 
*  
* This function allows for prioritization of events through the 
* priority parameter. Priorities are used when there are several 
* DFCs in the queue to execute the most prioritised first 
*  
* @param dxp_instance DXP to dispatch the event to 
* @param callback     The function to execute 
* @param blocking     blocking or not blocking (see 
*                     drv_EvtDispatchBlockingCode)
* @param priority     Priority  
* @param bufin        Pointer to a buffer that contains 
*                     information required to perform the
*                     operation (this can be NULL)
* @param bufin_size   Size, in bytes, of the buffer pointed to 
*                     by bufin
* @param bufout       Pointer to a buffer that receives the 
*                     output data from the operation - must be
*                     NULL in case of a non-blocking call
* @param bufout_size  Size, in bytes, of the buffer pointed to 
*                     by bufout - must be zero in case of a
*                     non-blocking call
* @return             Custom return code
* @see drv_EvtDispatchPrioCode 
*/  
extern int32 drv_EvtDispatchInitiateCrossDxpEvent(
    enum com_DxpInstance dxp_instance,
    drv_EvtDispatchCallback callback,
    drv_EvtDispatchBlockingCode blocking,
    drv_EvtDispatchPrioCode priority,
    void *bufin,
    uint32 bufin_size,
    void *bufout,
    uint32 bufout_size);

#endif /* #ifndef DRV_EVT_DISPATCH_H */

/** @} END OF FILE */

