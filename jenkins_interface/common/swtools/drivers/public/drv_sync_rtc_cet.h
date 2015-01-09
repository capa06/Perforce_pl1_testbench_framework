/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_sync_rtc_cet.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/


/**
 * @addtogroup RtbDriver
 * @{
 */

/**
 * @file drv_sync_rtc_cet.h Synchronisation of the CET using the
 *       RTC (also known as 32KHz calibration)
 *
 */

/******************************************************************************
  Original Author: Joe W

  Brief description:


  @@@@ To do:
  @@@@   More intelligent control of XTAL drift (including temp info etc...)?
  @@@@   Add support for the RTC driver

  Notes:
                                _   _   _            _                                _
    CET counter:               | | | | | |          | |                              | |
                          -----   -   -   -.......-   ----..........................-  -
                              ^                        ^                             ^
    RTC SIC triggers:         |                        |                             |
                               ____      ____      ____           ____      ____      ___
    RTC counter:              |    |    |    |    |    |         |    |    |    |    |
                          ----      ----      ----      --.....--      ----      ----
                         (0) (1)                      (2)                          (3)

    (0) Initialise ourselves, that is:
          - Register functions to be called pre-IDLE and post-IDLE with the PowerManagement
            driver.

    (1) At the dawn of time the CET is enabled synchronously using RTC (by use of a SIC trigger).

    (2) We prepare for entering HIBERNATE (called as part of the pre-IDLE call-back):
          - Our pre-IDLE call-back checks whether it is worth us entering HIBERNATE (i.e.
            there is XXX amount of time before the next scheduled CET PINT)
          - If we are entering HIBERNATE our pre-IDLE call-back configures RTC to
            synchronously disable CET (by use of a SIC trigger) and blocks until it has been
            disabled. It then calculates the expected point of WAKE in terms of RTC and CET
            counter clock cycles, and configures RTC to launch a WAKE at the appropriate time
            (allowing enough time for our state to be restored by the BootROM/NanoK/drivers
            etc...).

    (3) We prepare for exiting HIBERNATE after the programmed WAKE has been launched (called as
        part of the post-IDLE call-back):
          - Our post-IDLE call-back configures CET with the expected count, configures
            RTC to enable CET synchronously (by use of a SIC trigger) and blocks
            until it has been enabled.

 ******************************************************************************/

#ifndef DRV_SYNC_RTC_CET_H
#define DRV_SYNC_RTC_CET_H

#include "icera_global.h" /* Global defines (such as bool) */
#include "drv_ipm.h"      /* PowerManagement driver        */
#include "drv_gut.h"      /* GUT driver */

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* DRV_SYNC_RTC_CET_CET_FREQUENCY replaced with DRV_CET_CLK_SPEED_HZ */

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

extern DXP_CACHED_UNI0 mphalgutt_Handle *gutRTCLSB;
extern DXP_CACHED_UNI0 mphalgutt_Handle *gutCET_READONLY;

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  enumeration of timebase types
 */
typedef enum
{
    DRV_SYNC_RTC_CET_TIMEBASE_FINE,          /** accurate timebase (microseconds) */
    DRV_SYNC_RTC_CET_TIMEBASE_COARSE,        /** less accurate timebase (milliseconds) */
} drv_SyncRtcCetTimebaseType;

/*************************************************************************************************
  Exported functions.
 ************************************************************************************************/

/**
*   drv_SyncRtcCetInit
*
*   Takes control of CET and RTC, registers drv_SyncRTCCET_PreIDLECB() and
*   drv_SyncRTCCET_PostIDLECB() with the PowerManagement driver, and enables CET synchronously
*   using RTC.
*
*   pre  : Called as part of driver initialisation (the PowerManagement driver *must* already
*          have been initialised).
*   post : We are set up for RTC and CET calibration as part of HIBERNATION, and returns the driver
*         handle for the SyncRTCCET driver.
*
* @return The RTC CET driver handle
*/
drv_Handle *drv_SyncRtcCetInit();


/**
*   drv_SyncRtcCetPreIdleCallback
*
*   Determines if we should HIBERNATE (i.e. have we enough time to HIBERNATE before the next
*   scheduled CET PINT), and configures the PowerManagement driver appropriately. If we can
*   HIBERNATE we synchronously disable CET using RTC, determines the point of WAKE and configure RTC
*   to perform the WAKE.
*
*   pre  : Called as part of the PowerManagement driver's pre-IDLE call-back
*          syncRTCCETHandle - The SyncRTCCET driver handle, the type is actually a (void *).
*          powerMode        - The power mode (must be DRV_IPM_POWER_OFF).
*   post : Returns DRV_IPM_OK.
*
*   @param syncRTCCETHandle Handle passed to
*                           drv_IpmRegisterDriver()
*   @param powerMode power mode we are attempting to enter
*   @return IPM return code
*/
drv_IpmReturnCode drv_SyncRtcCetPreIdleCallback (drv_Handle syncRTCCETHandle,
                                            drv_IpmPowerMode powerMode);


/**
*   drv_SyncRtcCetPostIdleCallback
*
*   If the voltage supply of the core-power domain was removed (i.e. we performed a HIBERNATE) we
*   configure CET to appear as if the HIBERNATE never occured and synchronously enable CET
*   using the RTC, otherwise we do nothing.
*
*   pre  : Called as part of the PowerManagement driver's post-IDLE call-back
*          syncRTCCETHandle - The SyncRTCCET driver handle, the type is actually a (void *).
*          powerRemoved     - True if the voltage supply of the core-power domain was removed, else
*                             false, (this is a bool type, and ideally should not be - instead it
*                             should be an int with a test for 0 or != 0).
*   post : Returns DRV_IPM_OK.
*
*   @param syncRTCCETHandle Handle passed to
*                           drv_IpmRegisterDriver()
*   @param powerRemoved Flag to indicate whether a reset
*                       occurred
*   @return IPM return code
*/
drv_IpmReturnCode drv_SyncRtcCetPostIdleCallback (drv_Handle syncRTCCETHandle, bool powerRemoved);

/**
*  drv_SyncRtcCetIsRestored
*
*  @return non zero value if the Sync driver has completed the
*  re-initialisation after hibernate
*/
int drv_SyncRtcCetIsRestored(void);

/**
*   drv_SyncRtcCetIsRestored
*
*   This allows foreign modules to specify the required accuracy
*   of the timebase. This can be used for example by protocol
*   stack entities to request an accurate timebase when there is
*   a need to wake up at a specific time to run a
*   network-related activity (e.g. paging).
*
*   @param type Request accuracy (coarse/fine grain)
*/
void drv_SyncRequestTimebase(drv_SyncRtcCetTimebaseType type);

void drv_SyncFixupWakeup(void);

/**
*   drv_SyncRtcGetPreHibernateTimestamps
*
*   This function returns the RTC and CET timestamps
*   at the time CET was stopped
*
*   @param rtc_ts Pointer to address to write RTC timestamp to
*   @param cet_ts Pointer to address to write CET timestamp to
*/
void drv_SyncRtcGetPreHibernateTimestamps(drv_IpmTimestamp *rtc_ts, drv_IpmTimestamp *cet_ts);

/**
 * Return current time base drift (expressed in ticks of the CET
 * clock) between the local time base and the real time base. If
 * the returned value is zero, then there is no (known) drift.
 *
 * Must be called from DXP0
 */
uint64 drv_SyncRtcGetCurrentDrift(void);

#endif
/** @} END OF FILE */

