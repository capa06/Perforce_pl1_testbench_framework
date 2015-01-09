/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_gut.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup drv_gut GUT Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup drv_gut
 * @{
 */

/**
 * @file drv_gut.h Header file for gut driver
 *
 */

#ifndef DRV_GUT_H
#define DRV_GUT_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#ifndef HOST_TESTING
#include "livanto_memmap.h"
#include "livanto_config.h"
#include "mphal_gut.h"
#include "dxpnk_types.h"
#endif
#include "stdbool.h"
#ifdef HOST_TESTING
#include "ht_stub.h"
#endif
/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#if 0
#define DRV_GUT_SIC_DEBUG
#define DRV_GUT_INT_DEBUG
#define DRV_GUT_WRAP_DEBUG
#endif

#define DRV_GUT_GPIO_DEBUG  DRV_GPIO0

#define DRV_GUT_SPU_SLAVE_INT_DEBUG 3

#define DRV_GUT_SPU_SLAVE_WRAP_DEBUG 4

#define DRV_GUT_SPU_SLAVE_SIC_DEBUG 5

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * GUT Driver Handle
 */
typedef struct GutPriv drv_GutHandle;

/**
 * Timer and Trigger Handles
 */
typedef void drv_GutTimerH;
typedef void drv_GutTriggerH;

typedef enum {
    DRV_GUT_TIMER_PRIO_RF=0,
    DRV_GUT_TIMER_PRIO_DEFAULT,
    DRV_GUT_TIMER_PRIO_INVALID,
    DRV_GUT_NUM_TIMER_PRIO = DRV_GUT_TIMER_PRIO_INVALID
} drv_GutTimerPrio;

typedef enum
{
    DRV_GUT_CET_HI_RES=0,
    DRV_GUT_CET_LO_RES,
    DRV_GUT_NUM_INSTANCES
} drv_GutId;

typedef void (*drv_GutFnCb)(dxpnkt_Handle *, void* data, uint64 time);

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 * Convert time in usecs into GUT ticks
 * @param handle        : GUT Driver Handle
 * @param usecs         : Time in us
 * @return unsigned int : Time in gut ticks
*/
extern unsigned int drv_GutUsecsToTicks(drv_GutHandle *handle, unsigned int usecs);

/**
 * Convert time in msecs into GUT ticks
 * @param handle        : GUT Driver Handle
 * @param msecs         : Time in ms
 * @return unsigned int : Time in gut ticks
*/
extern unsigned int drv_GutMsecsToTicks(drv_GutHandle *handle, unsigned int msecs);

/**
 * Convert GUT ticks into usecs
 * @param handle        : GUT Driver Handle
 * @param ticks         : Time in gut ticks
 * @return unsigned int : Time in us
*/
extern unsigned int drv_GutTicksToUsecs(drv_GutHandle *handle, unsigned int ticks);

/**
 * Convert GUT ticks into msecs
 * @param handle        : GUT Driver Handle
 * @param ticks         : Time in gut ticks
 * @return unsigned int : Time in us
*/
extern unsigned int drv_GutTicksToMsecs(drv_GutHandle *handle, unsigned int ticks);


/**
 * Initialize the GUT driver
 * @return void
 */
extern void drv_GutInit();


/**
 * Gain access to a GUT instance
 * High resolution timers can be used ONLY on DXP0. However, it is possible
 * to open the high resolution timer driver on DXP1, for the sole purpose of getting
 * a 32-bit timestamp.
 * @param nkH              : NanoK Handle
 * @param id
 * @return *drv_GutHandle  : Gut Driver Handle
 */
extern drv_GutHandle *drv_GutOpen(dxpnkt_Handle *nkH, drv_GutId id);

/**
 * Relinquish access to GUT instance
 * @param handle       : Gut Driver Handle
 * @return void
 */
extern void drv_GutClose(drv_GutHandle *handle);


/**
 * Enable GUT
 * @param handle       : GUT Driver Handle
 * @param sync         : Start from synchronised trigger
 * @return void
 */
extern void drv_GutEnable(drv_GutHandle *handle, bool sync);

/**
 * Disable GUT
 * @param handle       : GUT Driver Handle
 * @param sync         : Stop from synchronised trigger
 * @return void
 */
extern void drv_GutDisable(drv_GutHandle *handle, bool sync);

/**
 * Get current 64-bit counter derived from the GUT (and the WRAP interrupt)
 * @param handle       : GUT Driver Handle
 * @return unsigned int                : GUT Counter
 */
extern uint64 drv_GutGetTimeStamp(drv_GutHandle *handle);


/**
 * Set current 64-bit counter.
 * This will also set the GUT counter accordingly.
 * @param handle       : GUT Driver Handle
 * @param value        : 32-bit timestamp
 */
extern void drv_GutSetTimeStamp(drv_GutHandle *handle, uint64 value);

/**
 * Return !0 if counter is enabled 
 * @param handle       : GUT Driver Handle 
 */
extern uint32 drv_GutIsCounterEnabled(drv_GutHandle *handle);

/**
 * Return contents of snapshot register and extend to 64 bits 
 * assuming at most one wrap of CET counter occurred since 
 * SIC pulse occurred 
 *  
 * @param handle       : GUT Driver Handle 
 */
extern uint64 drv_GutGetSnapshot(drv_GutHandle *handle);

/**
 * Reserve (or unreserve) a threshold for other uses (HLP)
 *  
 * @param handle       : GUT Driver Handle
 * @param threshold    : Threshold number
 * @param reserve      : True = reserve, False = unreserve
 */
extern void drv_GutReserveThreshold(drv_GutHandle *handle, int threshold, bool reserve);

/**
 * Create Timer
 * @param handle       : GUT Driver Handle
 * @param relative     : True is the timer is relative to current time.
 * @param ticks        : Expiration time when relative=false
 *                       Offset to current time when relative=true
 *                       (timer will expire at now + ticks)
 * @param period       : This parameter is 0 for one shot timers.
 *                       For periodic timers, it indicates the
 *                       period in ticks.
 * @param prio         : Timer priority, 0 has highest priority.
 *                       For CET, it shall be used ONLY by RF
 *                       driver. priority is not significant for
 *                       low resolution timers.
 * @param function     : Pointer to callback function. If NULL,
 *                       then a dxpnk_MsgQWrite will be
 *                 performed tocalling thread, at timer expiry
 *                 (with datum=data).
 * @param callback_params : Pointer to callback parameters
 *
 * @return drv_GutTimerH* : Timer Handle or NULL
 */
extern drv_GutTimerH *drv_GutCreateTimerDxp0(drv_GutHandle *handle,
                                         bool relative, uint64 ticks, unsigned int period, drv_GutTimerPrio prio,
                                         void  (*function)(dxpnkt_Handle *, void* data, uint64 time), void *callback_params);
extern drv_GutTimerH *drv_GutCreateTimer(drv_GutHandle *handle,
                                         bool relative, uint64 ticks, unsigned int period, drv_GutTimerPrio prio,
                                         drv_GutFnCb function, void *callback_params);

/**
 * Cancel a previously created timer
 * @param handle                    : GUT Driver Handle
 * @param timerH                    : Timer Handle
 * @return void
 */
extern void drv_GutCancelTimer(drv_GutHandle *handle, drv_GutTimerH *timerH);


/**
 * Create a Trigger (using SIC and sic_word)
 *
 * @param handle               : GUT Driver Handle
 * @param relative             : True is the trigger is relative to current time.
 * @param ticks                : Expiration time when relative=false Offset to current time when relative=true (trigger will expire at now + ticks)
 * @param sic_word             : SIC word value
 * @param spu_mask             : Target SPU slave mask
 * @param function             : Pointer to callback function
 *                             (can be NULL)
 * @param callback_params      : Pointer to callback parameters
 *
 * @return drv_GutTriggerH*
 */
extern drv_GutTriggerH *drv_GutCreateTrigger(drv_GutHandle *handle,
                                             bool relative, uint64 ticks,
                                             unsigned char sic_word, uint64 spu_mask,
                                             drv_GutFnCb function, void *callback_params);

/**
 * Cancel a previously created trigger
 * @param handle               : GUT Driver Handle
 * @param triggerH
 * @return void
 */
extern void drv_GutCancelTrigger(drv_GutHandle *handle, drv_GutTriggerH *triggerH);

/**
 * Get a timer's expiry date. This can be useful when the timer is periodic or when
 * it was started with relative=true.
 * @param handle               : Timer handle
 * @param timerH
 * @return unsigned int        : Absolute 32-bit expiry date.
 */
extern uint64 drv_GutGetTimerExpiry(drv_GutHandle *handle, drv_GutTimerH *timerH);

/**
 * Wait a given number msecs, using a GUT timer
 * @param priv                 : GUT Driver Handle
 * @param msecs                : Number of msecs to wait
 */
extern void drv_GutWaitMsecs(drv_GutHandle *priv, unsigned int msecs);

/**
 * Get the number of ticks to next CET expiry. 
 *  
 * @param  guard_ticks          : distance to threshold 
 *                              programmed date below which
 *                              hibernation is prohibited
 *  
 * @return unsigned int        : Number of ticks to next 
 *         interrupt
 */
extern unsigned int drv_GutCetTicksToNextInterrupt(uint32 guard_ticks);

/**
 *  Register a a GUT instance with the power management driver
 *  @param priv                : GUT Driver Handle
 */
extern void drv_GutIpmRegister(drv_GutHandle *priv);

/**
 *  Return a 64-bit CET timestamp on DXP#0
 */
extern uint64 drv_GutTimeStampDxp0(void);

/**
 *  Return a 64-bit CET timestamp on DXP#1
 */
extern uint64 drv_GutTimeStampDxp1(void);

/**
 *  Return a 32-bit 10ms timestamp
 */
extern uint32 drv_GutLoResTimeStamp(void);

/*
 *  Close CET so MPHAL POWERCLK can re-lock the APP PLL.
 */
extern void drv_GutCloseCet(void);

/**
 *  Re-open CET after a call to drv_GutCloseCet().
 */
extern void drv_GutReopenCet(void);

/** 
* Re-initialize GUT Hi Res DMEM data and registers. This needs 
* to happen before any call to os_Timestamp() 
*/
extern void drv_GutLowLevelReInit(void);

#endif

/** @} END OF FILE */

