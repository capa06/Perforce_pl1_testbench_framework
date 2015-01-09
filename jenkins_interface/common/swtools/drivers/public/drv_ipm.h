/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_ipm.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup IpmDriver Idle Power Management Driver
 * @ingroup  PwrMgt
 */

/**
 * @addtogroup IpmDriver
 * @{
 *
 * Vivalto2 IPM Implementation Notes
 *
 * ********************************************************************
 * OVERVIEW
 * ********************************************************************
 *
 * The IPM driver ensures that at any point in time the chip is
 * allowed to enter the lowest possible idle state when a core
 * enters idle (i.e. executes the 'wait' instruction).
 *
 * IPM may configure the system to enter any of the following
 * power states (@see drv_IpmPowerMode) when a DXP enters idle:
 * - CLS_IDLE: in this mode the DXP clock is cut (unless a call
 *   to drv_IpmSetDebugModeEnable(!0) was made previously);
 *   DMEM, GMEM, Cluster and Interconnect clocks are allowed to
 *   be cut, provided no ongoing operation such as a DMA
 *   transfer exists to prevent it;
 * - STOP: in this mode all abovementioned clocks are allowed to
 *   be cut; all derivatives from PLLs (including SOC, USI, UMCD
 *   clocks) are allowed to be cut, provided no ongoing
 *   operation such as a DMA transfer exists to prevent it; DRAM
 *   is in self refresh; the CET clock keeps running however; it
 *   is possible to come out of this mode without any visible
 *   latency;
 * - RETENTION: all clocks and PLLs are cut but the CET clock
 *   keeps running; core voltage is lowered and the SOC is
 *   completely static; it is no longer possible to wake the
 *   system on non-RTC wake events; the state of the chip is
 *   retained; there is some latency in waking up from this
 *   state as PLLs need to be restarted and some margin must be
 *   allowed for PMIC to raise core voltage;
 * - HIBERNATE: core power is off and the state of blocks that
 *   are outside of the Always-On domain is lost; there is some
 *   latency ([tens of]milliseconds) in waking up from HIBERNATE
 *   as the full state of the chip must be restored; in DSDA
 *   case one modem could enter PARKED mode, where its
 *   associated CLK_REQ is de-asserted (and the corresponding RF
 *   is put in HOLD mode) but the state of the chip is otherwise
 *   retained, if the other modem is active; there is some
 *   latency in waking up from PARKED mode as the RF needs to be
 *   reset and reprogrammed.
 *
 * IPM provides an API to allow any module to register and
 * contribute to the overall idle power management. These
 * modules are called Power Control Units (PCU).
 *
 * IPM provides an API to allow registered PCUs to notify the
 * framework of any state change that affects IPM. These
 * notifications take the form of 'constraints', that is to say
 * limitations that PCUs force onto the rest of the system to
 * allow them to remain functional. There are two types of
 * constraints:
 * - resource constraints: PCUs can explicitly request/release
 *   clock trees (@see drv_IpmResourceType). IPM maintains a
 *   reference count for clock requests such that a clock cannot
 *   be gated unless all registered PCUs agree; in order to
 *   avoid having to constantly request/release the SOC clock
 *   PCUs may request their SOC module to be enabled at all
 *   times unless the system enters STOP, RETENTION or HIBERNATE
 *   modes through
 *   DRV_IPM_RESOURCE_SOC_MODULE_CLOCK_GATING_ALLOWED;
 * - timing constraints: these allow a PCU to let IPM know the
 *   timestamp at which their next activity is planned (if any),
 *   and the amount of acceptable latency in interrupt handling.
 *   IPM ensures that all timing constraints are met, such that
 *   all PCUs are allowed to have their interrupt handlers
 *   scheduled within the specified time; all timing constraints
 *   are expressed as a 64-bit number of CET ticks.
 *
 * IPM provides an API to allow registered PCUs to receive a
 * notification through a callback on these events:
 * - pre-idle: this is called immediately before entering idle
 *   in order to let PCUs take appropriate measures for idle,
 *   although PCUs are encouraged not to make use of these:
 *   where possible PCUs should take action to be able to
 *   restore their state without a call to the pre-idle callback
 *   and they should not have to modify their state before
 *   entering idle; PCUs can specify a mask to let IPM know when
 *   to call the pre-idle callback depending on the targeted
 *   low-power mode; it is illegal to call OS routines or modify
 *   IPM timing constraints from the context of pre-idle
 *   callbacks;
 * - post-idle: this is called immediately after exiting idle
 *   in order to let PCUs take action to restore their state;
 *
 * IPM interacts with several key components:
 * - the CRPC silicon block provides means for controlling clock
 *   gating and which power state to enter; the CRPC programming
 *   model is designed in such a way that DXPs can independently
 *   make a decision about which power state to aim for and
 *   program CRPC accordingly; CRPC is reponsible for
 *   aggregating requests from DXPs, DMAs and all modules on the
 *   Interconnect to ensure the lowest power state is entered;
 * - the RTB silicon block is responsible for bringing the chip
 *   in and out of RETENTION, HIBERNATE and PARKED modes; the
 *   RTB controls PWR_REQ, RETENTION_REQ and CLK_REQ signals and
 *   provides means for controlling how these signals are
 *   asserted/de-asserted; the RTB also provides 32kHz-based
 *   timers to program a synchronous wake-up from one of these
 *   low-power modes;
 * - the CET driver provides a time base as well as information
 *   on timers; CET supports the notion of coarse timers but as
 *   far as IPM is concerned only the deadline should be
 *   communicated to IPM through timing requests; the CET
 *   silicon block is in the always-on domain, which allows for
 *   CET timers to keep running as long as the corresponding
 *   master clock is ON;
 *
 * The following drivers, though not strictly internal to IPM,
 * are essential to IPM:
 * - the RTC calibration (drv_cal32k) driver provides an
 *   accurate CET/RTC clock ratio;
 * - the RTC/CET Sync (drv_sync_rtc_cet) driver provides an API
 *   to synchronously start CET on an edge of the RTC and also
 *   provides an API to take a snapshot of the CET counter on an
 *   edge of the RTC
 * - the Wake Scheduler (drv_wake_sch) driver measures the
 *   latency to come out of RETENTION, HIBERNATE and PARKED
 *   modes according to the current state of the chip; this
 *   driver also programs RTC timers to schedule an exit from
 *   one of these modes;
 *
 * ********************************************************************
 * DETAILS
 * ********************************************************************
 *
 * ********************************************************************
 *  Initial configuration
 *
 * On cold/warm boot, IPM configures the system as follows:
 * - DXP and DMEM clocks are allowed to auto idle;
 * CRPC.dxp_clk_ctrl[dxp].dxp[dxp]_mode = AUTO
 * CRPC.dxp_clk_ctrl[dxp].dmem[dxp]_mode = AUTO
 * - GMEM, CLS and IC clocks are allowed to auto idle;
 * CRPC.cls_clk_ctrl[dxp].gmem[cls]_mode = AUTO
 * CRPC.cls_clk_ctrl[dxp].cls[cls]_mode = AUTO
 * CRPC.cls_clk_ctrl[dxp].ic[cls]_mode = AUTO
 *
 * If debug mode is enabled, the DXS root clock is kept ON
 * except where HIBERNATE or RETENTION are possible:
 * CRPC.debug.keep_dxs_root_on = 1
 *
 * CLK_REQ is not allowed to be de-asserted in RETENTION mode:
 * RTB.retention_config[app].disable_clk_req = 0
 *
 * CLK_REQ is allowed to be cut in HIBERNATE and PARKED modes:
 * RTB.hibernate_config[app].disable_clk_req = 1
 * RTB.parked_config[app].disable_clk_req = 1
 *
 * ********************************************************************
 *  Top-level Pre-Idle Handler
 *
 * IPM registers a pre-idle handler to NanoK; this is where the
 * decision to enter low-power modes happens.
 *
 * The pre-idle handler operates as follows:
 * 1. if the next CET timer is due to fire in less than the
 * IDLE GUARD TIME (~hundred microseconds) then program the
 * system for CLS_IDLE and return immediately so as to limit
 * the potential impact on timer jitter;
 * 2. make a sleep decision based on all requests from
 * registered PCUs; the output of this sleep decision is the
 * combination of a target IPM state and a date for the
 * earliest deadline (if any);
 * 3. configure the system for the target IPM state (see
 * sections below on)
 *
 * Pseudo code:
 *
 *  if (cet_ticks_to_next_interrupt < IDLE_GUARD_TIME)
 * 	 PrepareCLSIdle
 *     return
 * [global_target_ipm_state,earliest_deadline] = MakeSleepDecision
 * if global_target_ipm_state == CLS_IDLE
 * 	PrepareCLSIdle
 * 	return
 * if global_target_ipm_state == STOP
 * 	PrepareSTOP
 * 	return
 * if global_target_ipm_state == RETENTION
 * 	PrepareRETENTION(earliest_deadline)
 * 	return
 * if global_target_ipm_state == HIBERNATE
 * 	PrepareHIBERNATE(earliest_deadline)
 * 	return
 *
 * ********************************************************************
 *  Top-level Post-Idle handler
 *
 * IPM registers a post-idle handler to NanoK; this is called
 * to restore some of the chip state, if applicable.
 *
 * There isn't anything to restore when coming out CLS_IDLE,
 * STOP or RETENTION modes.
 *
 * When coming out of RETENTION mode it is nonetheless useful
 * to measure the latency associated with waking up from this
 * mode.
 *
 * When coming out of PARKED mode the RF must be reset and
 * reprogrammed, the CET time base must be restored, the CET
 * must be instructed to restart on an edge of the RTC
 *
 * When coming out of HIBERNATE the full state of the chip must
 * be restored, including internal memory, all peripheral
 * drivers, etc.; care must be taken to unfreeze I/Os in a
 * controlled way in order to avoid glitches; as in PARKED mode,
 * the RF and CET timebase must be restored.
 *
 * ********************************************************************
 *  Pre-idle decision making
 *
 * The first step towards choosing which state to target on idle
 * is to review all resource requests. If at least one PCU has
 * explicitly requested a SOC module then IPM will target
 * CLS_IDLE.
 *
 * If all PCUs agree to have their SOC module disabled then IPM
 * will target one of STOP, RETENTION of HIBERNATE modes. There
 * is some latency associated with waking up from RETENTION and
 * HIBERNATE modes so the second step towards choosing the
 * target state is to review timing constraints. IPM goes
 * through all PCUs to find the earliest deadline and the
 * smallest allowed interrupt latency. IPM then takes the
 * minimum of the smallest allowed interrupt latency and the
 * ticks to the next scheduled activity to figure out how long
 * there is until the next deadline. If this number is less than
 * the latency to come out of RETENTION then the target state is
 * STOP. Otherwise if this number is less than the latency to
 * come out of HIBERNATE then the target state is RETENTION.
 * Otherwise the target state is HIBERNATE.
 *
 * Pseudo code:
 *
 * resource_request = OR_foreach_pcu(clock_request[pcu])
 * if (resource_request & SOC_CLOCK) next_power_mode = CLS_IDLE
 *  goto exit
 *
 * earliest_deadline = MIN_foreach_pcu(scheduled_activity[pcu])
 * allowed_interrupt_latency = MIN_foreach_pcu(allowed_latency[pcu])
 * ticks_to_next_activity = MIN(allowed_interrupt_latency,
 *                              earliest_deadline - time(now)  )
 *
 * if (ticks_to_next_activity < MIN_RETENTION_TIME)
 * 	next_power_mode = STOP
 * 	goto exit
 * if (ticks_to_next_activity < MIN_HIBERNATE_TIME)
 * 	next_power_mode = RETENTION
 * 	goto exit
 * next_power_mode = HIBERNATE
 *
 * exit:
 * returns: [next_power_mode,earliest_deadline]
 *
 * ********************************************************************
 *  Getting ready for CLS_IDLE
 *
 * All that is required is to configure CRPC to enter at most
 * ACTIVE and disable PARKED mode. PLLs are not allowed to be
 * cut.
 *
 * Pseudo code:
 *
 * CRPC.soc_idle_ctrl[dxp].allow_state = ACTIVE
 * CRPC.soc_idle_ctrl[dxp].allow_parked = 0
 * CRPC.soc_idle_ctrl[dxp].cut_plls = 0
 *
 * ********************************************************************
 *  Getting ready for STOP mode
 *
 * All that is required is to configure CRPC to enter at most
 * STOP and disable PARKED mode. PLLs are not allowed to be cut.
 *
 * CRPC.soc_idle_ctrl[dxp].allow_state = STOP
 * CRPC.soc_idle_ctrl[dxp].allow_parked = 0
 * CRPC.soc_idle_ctrl[dxp].cut_plls = 0
 *
 * *********************************************************************
 *  Getting ready for RETENTION mode
 *
 * Since it is not possible to come out of RETENTION using
 * regular interrupts the RTB must be programmed to allow a wake
 * event, if applicable. PLLs are allowed to be cut.
 *
 * This involves three things:
 * - the RTB external wake mask must have been configured to
 *   wake on appropriate external I/Os (this is preferably done
 *   at boot/run time, not in the process of entering idle);
 * - an RTC_LSB wake timer must be programmed, if necessary; the
 *   RTC_LSB wake timer is a shared resource across the entire
 *   application so it must be accessed with parsimony and under
 *   SMP atomic section to avoid concurrency issues; see section
 *   below for a summary of how this may be implemented;
 * - the RTC_WUT T1 and T4 thresholds must be programmed with
 *   appropriate timings for RETENTION; the RTC_WUT is a shared
 *   resource so it must be accessed with parsimony and under
 *   SMP lock.
 *
 * Pseudo code:
 *
 * CRPC.soc_idle_ctrl[dxp].allow_state = RETENTION
 * CRPC.soc_idle_ctrl[dxp].allow_parked = 0
 * CRPC.soc_idle_ctrl[dxp].cut_plls = 1
 * TakeSMPLockForApp(app)
 *  global_array_of_target_state[app][dxp] = RETENTION
 *  RtbWutProgramThresholds(RETENTION)
 * ReleaseSMPLock(app)
 * WakeSchProgramRtcLsbWake(earliest_deadline-RETENTION_LATENCY)
 *
 * *********************************************************************
 *  Getting ready for HIBERNATE/PARKED modes
 *
 *
 * There is no guarantee that the system will enter HIBERNATE
 * therefore care must be taken when programming the RTB; the
 * actual power mode may end up being:
 * - CLS_IDLE/STOP,
 * - RETENTION,
 * - PARKED: RTB WUT must be configured accordingly to allow for
 *   enough time to wait for the main crystal to become stable
 *   (~ a couple of milliseconds)
 * - HIBERNATE: if the system enters HIBERNATE the PNR interrupt
 *   will be raised, giving IPM and registered PCUs a chance to
 *   take last minute action before power down;
 *
 * Similar to RETENTION mode, it is not possible to come out of
 * HIBERNATE using regular interrupts so the RTB must be
 * programmed to allow a wake event, if applicable.
 *
 * This involves three things:
 * - the RTB external wake mask must have been configured to
 *   wake on appropriate external I/Os (this is preferably done
 *   at boot/run time, not in the context of entering idle);
 * - an RTC_LSB wake timer must be programmed, if necessary; the
 *   RTC_LSB wake timer is a shared resource across the entire
 *   application so it must be accessed with parsimony and under
 *   SMP atomic section to avoid concurrency issues; see section
 *   below for a summary of how this may be implemented;
 * - the RTC_WUT T1 and T4 thresholds must be programmed with
 *   appropriate timings for PARKED;
 *
 * @FIXME: if within the same app DXPa is willing to RETENTION
 * then it needs to program RTB_WUT for RETENTION; if DXPb
 * subsequently attempts to HIBERNATE then it needs to program
 * RTB_WUT for PARKED. In this case we will at most enter
 * RETENTION but the wake-up latency will be higher than a
 * regular wake from RETENTION due to the RTB_WUT settings. On
 * this app we will end up waking up too late.
 * Possible solutions:
 * - have a SW handshake mechanism to verify if another DXP has
 *   already bidden for RETENTION, in which case we don't
 *   overwrite RTB_WUT. This could be achieved with an uncached
 *   array where (under SMP lock) each DXP writes its target
 *   low-power state. Only if the combined state is HIBERNATE
 *   would the DXP overwrite RTB_WUT settings for PARKED
 *   otherwise RETENTION settings should prevail. This is
 *   probably the easiest solution for now;
 * - program RTC_LSB wake margin such that it will always be
 *   large enough for PARKED, even if we just want to enter
 *   RETENTION;
 *   Problem: this will cause an early wake-up when coming out
 *   of RETENTION (small waste of power)
 * - come up with a single set of RTB_WUT settings that work for
 *   both RETENTION and PARKED;
 *   Problem: that will increase the wake-from-RETENTION latency
 *   (small waste of power)
 * - introduce a pre-PARKED PNR; is it possible?
 * - change the semantics of RTB_WUT such that triggers are not
 *   absolute counter values but relative to each other and
 *   ignore irrelevant thresholds such as T2(CLOCK_REQ
 *   assertion) when coming out of RETENTION.
 *
 * Since the system could enter PARKED mode (without any
 * intervening notification such as the PNR) and the CET clock
 * could be cut, care must be taken to take a snapshot of the
 * CET counter at a specified edge of the RTC_LSB; this is
 * required to figure out an accurate estimate of the current
 * real time when the system subsequently wakes up from either
 * PARKED or HIBERNATE; this only needs to happen on one DXP per
 * application (the 'CET master').
 *
 * Pseudo code:
 *
 * CRPC.soc_idle_ctrl[dxp].allow_state = HIBERNATE
 * CRPC.soc_idle_ctrl[dxp].allow_parked = 1
 * CRPC.soc_idle_ctrl[dxp].cut_plls = 1
 * TakeSMPLockForApp(app)
 *  global_array_of_target_state[app][dxp] = RETENTION
 *  target=MAX_foreach_dxp(global_array_of_target_state[app][dxp])
 *  if target == HIBERNATE
 *   RtbWutProgramThresholds(PARKED)
 * ReleaseSMPLock(app)
 * if (dxp==DXP_APP_1_CET_MASTER OR dxp==DXP_APP_2_CET_MASTER)
 *  SyncRtcCetTakeCetSnapshot()
 * WakeSchProgramRtcLsbWake(earliest_deadline-HIBERNATE_LATENCY)
 *
 * ********************************************************************
 *  Point of No Return (PNR)
 *
 * IPM receives a notification from NanoK on all DXPs when the
 * system is ready to HIBERNATE; this should be used to carry
 * out any operation required before chip power down; this
 * includes, among other things, saving the contents of internal
 * memory and updating RTB_WUT parameters for hibernate.
 *
 * ********************************************************************
 *  Scheduling an RTC wake from an RTB low-power mode
 *
 * There is a single RTC_LSB per application so within an
 * application care must be taken to program RTC_LSB for the
 * earliest deadline across the application; this needs to
 * happen under SMP lock.
 *
 * A global array in uncached memory must be maintained to keep
 * track of earliest deadlines on all DXPs within an
 * application; under the SMP lock each DXP must update the
 * global array with its own earliest deadline; then if it is
 * determined that this DXP has the earliest deadline across
 * the application, ths RTC_LSB must be programmed for that
 * DXP.
 *
 * Pseudo code:
 *
 * TakeSMPLock(app)
 * global_next_rtc_timeout[app][dxp] = timestamp
 * if timestamp == MIN_foreach_dxp(global_next_rtc_timeout[app][dxp])
 * 	RtcLsbTimerProgram(timestamp)
 * ReleaseSMPLock(app)
 *
 * ********************************************************************
 */

/**
 * @file drv_ipm.h Power management interface.
 *
 */

#ifndef DRV_IPM_H
#define DRV_IPM_H

#include "icera_global.h"               /* Fundamental Icera definitions */
#include "com_machine.h"
#include "drv_stats.h"
/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/**** Features ****/

/** define this in order to run simulation tests */
#undef DRV_IPM_STANDALONE

/** define this to enable insane paranoid checks */
#undef DRV_IPM_PARANOID

/** define this to enable register debug through AT commands  */
#undef DRV_IPM_REGISTER_DEBUG

/**
 *  for callback profiling, this makes it possible to monitor
 *  the min/max time spent in each IPM callback
 */
#define DRV_IPM_CALLBACK_PROFILE

/**** Constants ****/

/** indicates infinite time */
#define DRV_IPM_ETERNITY (UINT64_MAX)

/** maximum number of PCUs per DXP */
#define DRV_IPM_MAX_PCUS_PER_DXP (50)

/** number of CRPC modules banks */

/* HACK: leave this set to 2 although it should really be
   1 on 9xxx. This is to avoid making changes in all client
   drivers now */
#define DRV_IPM_CRPC_MODULES_BANKS (2)

/**
 * Use this define in callback call circumstances to indicate
 * that the callback should always be called
 */
#define DRV_IPM_CALL_ALWAYS (DRV_IPM_DXP_CLOCK_ACTIVE|DRV_IPM_DXP_IDLE|DRV_IPM_SOC_IDLE|DRV_IPM_HIBERNATE)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  enumeration of return codes
 */
typedef enum
{
    DRV_IPM_ERROR,                               /** error indication */
    DRV_IPM_OK,                                  /** success indication */
} drv_IpmReturnCode;

/**
 * resource request/release - this is a bitmap composed
 * of drv_IpmResourceType pre-defined resource types
 */
typedef uint32 drv_IpmResourceClaim;

/**
 * IPM timestamp (this maps to GUT CET timestamps)
 */
typedef uint64 drv_IpmTimestamp;

/**
 *  enumeration of pre-defined callback orders
 */
typedef enum
{
    DRV_IPM_CALLBACK_MAX_ORDER=0,                /** max priority/order */
    DRV_IPM_CALLBACK_HIGHER_ORDER=15,            /** higher priority/order */
    DRV_IPM_CALLBACK_HIGH_ORDER=30,              /** high priority/order */
    DRV_IPM_CALLBACK_MEDIUM_ORDER=45,            /** medium priority/order */
    DRV_IPM_CALLBACK_LOW_ORDER=60,               /** low priority/order */
    DRV_IPM_CALLBACK_LOWER_ORDER=76,             /** lower priority/order */
    DRV_IPM_CALLBACK_MIN_ORDER=99,               /** min priority/order */
    DRV_IPM_CALLBACK_IGNORED_ORDER=100           /** for use by drivers that don't register a callback */
} drv_IpmCallbackOrder;

/**
 * enumeration of hardware resources
 */
typedef enum
{
    /** no resource */
    DRV_IPM_NO_RESOURCE=0,
    /**
     *  SOC clock resource, prohibit RTB low-power modes (STOP,
     *  PARKED, RETENTION, HIBERNATE)
     */
    DRV_IPM_RESOURCE_SOC_CLOCK=BIT(1),
    /**
     *  keep SOC module enabled but do not prohibit any RTB
     *  low-power mode
     */
    DRV_IPM_RESOURCE_SOC_MODULE=BIT(2),
} drv_IpmResourceType;

/**
 * enumeration of low-power modes - power modes are ordered by
 * the power save level
 */
typedef enum
{
    DRV_IPM_INVALID_POWER_MODE=0,
#if 1
    /* 9040 */
    DRV_IPM_DXP_CLOCK_ACTIVE=BIT(0),
    DRV_IPM_DXP_IDLE=BIT(2),
    DRV_IPM_SOC_IDLE=BIT(3),
    DRV_IPM_HIBERNATE=BIT(4)
#else
    /* 9060 */
    DRV_IPM_CLS_IDLE=BIT(0),
    DRV_IPM_STOP=BIT(1),
    DRV_IPM_RETENTION=BIT(2),
    DRV_IPM_HIBERNATE=BIT(3),
#endif
} drv_IpmPowerMode;

/**
 *  enumeration of IPM contexts
 */
typedef enum
{
    DRV_IPM_CONTEXT_PRE_IDLE_CALLBACK,           /** context of a pre-idle callback */
    DRV_IPM_CONTEXT_POST_IDLE_CALLBACK,          /** context of a post-idle callback */
    DRV_IPM_CONTEXT_OTHER                        /** other contexts */
} drv_IpmContext;

/**
 * Type definition for a Driver handle
 *
 * Driver handles are passed to PCUs when their callback functions
 * are invoked.
*/
typedef void *drv_Handle;

/**
 * Type definition for a pre-idle callback.
 *
 * Pre-idle callbacks are called by the IPM framework after a
 * decision to idle.
 *
 * PCUs are encourage to save their state on a regular basis
 * instead of relying on their pre-idle callback to do so; PCUs
 * should refrain from modifying their IPM constraints from the
 * context of their pre-idle callback.
 *
 * Pre-idle callbacks are intended to carry out the required
 * actions to prepare the system for low power and perform the
 * necessary context saving to allow for further restoration of
 * the driver and underlying peripheral.
 *
 * Pre-idle callbacks are called in the context of the NanoK
 * pre idle callback, while interrupts are masked.
 *
 * Pre-idle callbacks must not block.
 *
 * On error, pre-idle callbacks may return DRV_IPM_ERROR to
 * interrupt the idle entry process. On success, DRV_IPM_OK must
 * be returned.
 *
 * @param driver_handle The driver handle
 * @param power_mode The mode to which the system is attempting
 *                   to transition
 * @param earliest_deadline Earliest scheduled activity on the
 *                          calling DXP
 * @return The return code
 * @see Idle Power Specification
 */
typedef drv_IpmReturnCode (*drv_IpmPreIdleCallback)(drv_Handle driver_handle,
                                                    drv_IpmPowerMode power_mode
#if 0 /* add back for Viv2 */
                                                    ,drv_IpmTimestamp earliest_deadline
#endif
);

/**
 * Type definition for a post-power down callback.
 *
 * Post-power down callbacks are called by the power management
 * framework after the system resumes from a power down request.
 *
 * Post-power down callbacks are intended to perform the
 * necessary context restoration to bring the driver and
 * peripheral back to operational state.
 *
 * Post-power down callbacks are called in the context of the
 * NanoK post idle callback, while interrupts are masked.
 *
 * Post-power down callbacks must not block.
 *
 * Post-power down callbacks may be called even if the system
 * did not power off. The power_lost boolean parameter is used
 * to differentiate between the two. A non-zero value indicates
 * that power was cut.
 *
 * On error, pre-power down callbacks may return DRV_IPM_ERROR.
 * On success, DRV_IPM_OK must be returned.
 *
 * @param driver_handle The driver handle
 * @param power_lost Indication of power lost (zero: power was
 *                   not cut, non-zero: power was cut) - NOTE:
 *                   this parameter may be removed if
 *                   unnecessary
 * @return The return code
 * @see Idle Power Specification
 */

typedef drv_IpmReturnCode (*drv_IpmPostPowerDownCallback)(drv_Handle driver_handle,
                                                          bool power_lost);

/**
 * Type definition for a Power Control Unit (PCU) functional
 * interface
 *
 * pre_idle_callback_circumstances:
 *   this bit field defines under which circumstances the pre
 *   idle callback is called,
 *	 @see drv_IpmPowerMode for power mode definitions
 *   example: set DRV_IPM_SOC_IDLE if the callback must be
 *   called before entering DRV_IPM_SOC_IDLE mode
 */
typedef struct
{
    drv_IpmPreIdleCallback pre_callback;         /**< pre idle callback */
    int pre_idle_callback_circumstances;
    uint32 pre_callback_order;                   /**< pre idle callback order */
    drv_IpmPostPowerDownCallback post_callback;  /**< post power down callback */
    uint32 post_callback_order;                  /**< post power down order */
} drv_IpmPcuFuncs;

/**
 * Type definition for a Power Control Unit (PCU) handle.
 *
 * PCUs are software entities that may request or release
 * hardware resources through calls to the Power Management
 * driver
 *
 * Each registered Power Control Unit (PCU) is associated with a
 * unique handle. Driver handles are initialised during driver
 * registration to the Power Management framework.
 */
typedef struct drv_IpmPrivatePcu *drv_IpmPcuHandle;

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * Driver registration routine
 *
 * This function is used to register a driver to the power
 * management framework.
 *
 * Drivers who are registered to the Power Management framework
 * are allowed to request hardware resources such as clocks and
 * thus force clock domains to be turned on. Drivers may also
 * communicate timing requirements, which the power management
 * framework makes use of to determine the best allowed power
 * mode.
 *
 * Drivers register pre/post power down callback when they need
 * to perform context saving/restoration before/after a power
 * cut. Drivers that do not need to register a pre/post power
 * down callback may pass a NULL parameter instead.
 *
 * Drivers specify the relative order in which their callbacks
 * must be called through the 'order' parameters. A low number
 * indicates high priority (the callback is called early) while
 * a high number indicates low priority (the callback is called
 * late). See the drv_IpmCallbackOrder enumeration and
 * drv_ipm_order.h. If a callback is set to NULL to indicate it
 * is not used, the associated callback order must be set to
 * DRV_IPM_CALLBACK_IGNORED_ORDER.
 *
 * Drivers may specify a CRPC module mask to request SOC clock
 * sub-domains. The mask is provided by the crpc_modules
 * parameters. This parameter is a pointer to an array of 32-bit
 * integers. There must be one item per CRPC bank in the array.
 *
 * Registered drivers will be initialised to power OFF state by
 * default. This means that they must explicitly request
 * resources by updating their status at initialisation time if
 * required.
 *
 * NOTE: handle_ptr may be encapsulated in a generic driver
 * handle in the future
 *
 * @param pcu_handle Pointer to an unitialised PCU handle (this
 *                   is initialised by this function)
 * @param driver_handle The driver handle
 * @param crpc_modules Pointer to
 *                     DRV_IPM_CRPC_MODULES_BANKS-sized array of
 *                     CRPC modules banks
 * @param pcu_name Human-friendly name for PCU instance
 *                 (character string must be statically
 *                 allocated)
 * @param funcs_ptr pointer to PCU function interface
 * @return DRV_IPM_ERROR on failure, DRV_IPM_OK on success
 * @see Idle Power Specification
 */
drv_IpmReturnCode drv_IpmRegisterDriver(
                                       drv_IpmPcuHandle *pcu_handle,
                                       drv_Handle driver_handle,
                                       const uint32 *crpc_modules,
                                       const char *pcu_name,
                                       const drv_IpmPcuFuncs *funcs_ptr);

/**
 * Driver status update routine
 *
 * This function is used to request/release hardware resources
 *
 * Drivers may request/release the SOC clock, in which case the
 * power management framework will take responsability of
 * updating the CRPC_ENABLE_x registers accordingly. Note that
 * an SMP lock is used to synchronise access to these registers.
 *
 * Prior to calling this function, the default status of a
 * registered PCU is that there is no request on any hardware
 * resource
 *
 * Calling this function resets the PCU power loss flag.
 *
 * This function can be called in any context.
 *
 * @param pcu_handle The PCU handle
 * @param resource_request Bitmap of resource requests (see
 *                         drv_IpmResourceType)
 * @return DRV_ERROR on failure
 * @see Idle Power Specification
 */
drv_IpmReturnCode drv_IpmUpdateResourceConstraints(
                                                  drv_IpmPcuHandle pcu_handle,
                                                  drv_IpmResourceClaim resource_request);

/**
 * Driver status update routine
 *
 * This function is used to communicate driver's timing constraints
 *
 * Drivers need to communicate the date of their next scheduled
 * activity, expressed in system time. In cases when there is no
 * information on next scheduled activity date, drivers may
 * provide DRV_IPM_ETERNITY. Note: a date which occurs in the
 * past (i.e. earlier than NOW) is ignored when calling this
 * function, and ignored when making a sleep decision.
 *
 * Drivers need to communicate their expected interrupt latency,
 * expressed in ticks of the system time. In cases when there is
 * no information on interrupt latency, drivers may provide
 * DRV_IPM_ETERNITY.
 *
 * Prior to calling this function, the default status of a
 * registered PCU is that there is no timing constraint (this
 * maps to: date_of_next_scheduled_activity==DRV_IPM_ETERNITY,
 * min_allowed_interrupt_latency==DRV_IPM_ETERNITY)
 *
 * Calling this function resets the PCU power loss flag
 *
 * Note for Vivalto2: there is no plan to have a DXP0 version of
 * this function on Vivalto2 is the CET driver is expected to
 * communicate its timing constraint to IPM from the context of
 * drv_CetTicksToNextInterrupt().
 *
 * This function can be called in any context.
 *
 * @param pcu_handle The PCU handle
 * @param date_of_next_scheduled_activity Date of next scheduled
 *                                        activity (expressed in
 *                                        system time)
 * @param min_allowed_interrupt_latency Minimum allowed latency
 *                                      (expressed in ticks of
 *                                      system time)
 * @return DRV_IPM_ERROR on failure
 * @see Idle Power Specification
 */
drv_IpmReturnCode drv_IpmUpdateTimingConstraints(
                                                drv_IpmPcuHandle pcu_handle,
                                                drv_IpmTimestamp date_of_next_scheduled_activity,
                                                drv_IpmTimestamp min_allowed_interrupt_latency);

/**
 * IPM Driver initialisation function
 *
 * This function is used initialise the IPM driver. This
 * function is expected to be called during sytem
 * initialisation.
 *
 * This function uses DXP_MULTI data and must be called on each
 * DXP instance
 *
 * @return The return code (error=DRV_IPM_ERROR, success=DRV_IPM_OK)
 */
drv_IpmReturnCode drv_IpmInit();

/**
 * IPM Driver de-initialisation function
 *
 * This function is used de-initialise the IPM driver.
 *
 * This function uses DXP_MULTI data and must be called on each
 * DXP instance
 *
 * @return The return code (error=DRV_IPM_ERROR, success=DRV_IPM_OK)
 */
drv_IpmReturnCode drv_IpmDeInit(void);

/**
 * IPM Driver prepare idle function
 *
 * This function is used to prepare the system for idle. This
 * function must be called in the context of the NanoK preIdle
 * callback, while interrupts are masked.
 *
 * This function takes all driver requests into consideration in
 * order to determine the best allowed power mode - this is
 * known as 'making a sleep decision'. If SOC idle (or better)is
 * allowed on a given DXP instance, this function makes a
 * system-wise sleep decision. Depending on the outcome of the
 * sleep decision, the SOC_IDLE_CTRL register may be altered and
 * the pre-power down callback may be called.
 *
 *  @param this_dxp_power_mode Pointer to local DXP power mode
 *  @param soc_power_mode Pointer to SOC power mode
 *  @return The return code (error=DRV_IPM_ERROR, success=DRV_IPM_OK)
 */
drv_IpmReturnCode drv_IpmPrepareIdle(drv_IpmPowerMode *this_dxp_power_mode
                                     );

/**
 * IPM Driver sleep decision function
 *
 * This function is used to make a sleep decision, based on the
 * state of the IPM driver internal state variables
 *
 * This function is not intended to be called from outside the
 * PM driver, but is exported to external modules for testing
 * purpose
 *
 * This function returns the lowest allowed power mode
 *
 * @param power_mode_ptr Pointer to power mode
 * @return The return code (error=DRV_IPM_ERROR, success=DRV_IPM_OK)
 */
drv_IpmReturnCode drv_IpmMakeSocSleepDecision(drv_IpmPowerMode *power_mode_ptr);

/**
 * IPM prepare DXP global state variables
 *
 * This function is used to update the drv_IpmGlobalStateTable[] array
 * for a given DXP instance
 *
 * this function  must be called with interrupts disabled (e.g. in the
 * context of a Nanok callback) as it does not explicitly
 * protect against race conditions on global variables
 *
 * @param dxp_instance The DXP instance (0 or 1)
 * @return The return code
 */
drv_IpmReturnCode drv_IpmPrepareDxpGlobalState(enum com_DxpInstance dxp_instance);

/**
* drv_IpmGetDateOfNextScheduledActivity
*
* Returns the last computed date of next scheduled activity -
* note that the date of the next scheduled activity is only
* relevant in the context of IPM pre-idle callbacks, and should
* be used with care in any other context since the returned
* value may be out-of-date
* @return The date of the next scheduled activity
*/
drv_IpmTimestamp drv_IpmGetDateOfNextScheduledActivity(void);

/**
* drv_IpmWaitUntilAfterPostPowerDownCallbackCompletes
*
* Allows waiting until a post power down callback completes
* @param order order of the post power down callback
* @param dxp_instance dxp_instance the post power down callback
*                     is running on
* @return none
*/
void drv_IpmWaitUntilAfterPostPowerDownCallbackCompletes(drv_IpmCallbackOrder order,
                                                         enum com_DxpInstance dxp_instance);

/**
 * drv_IpmSetDeepestAllowedSleepMode
 *
 * This function is used modify the deepest allowed sleep mode.
 * This function is expected to be called during sytem initialisation.
 *
 * @param power_mode Deepest allowed sleep mode to set.
 *
 * @return none
 */
void drv_IpmSetDeepestAllowedSleepMode(drv_IpmPowerMode power_mode);

/**
 * This function can be used to determine if the caller is in
 * pre/post idle context, or other
 *
 * @return the current IPM context
 */
drv_IpmContext drv_IpmGetCurrentContext(void);

/**
 * returns a human readable power mode
 */
char *drv_IpmDebugPowerModeString(drv_IpmPowerMode power_mode);

/**
* Reset IPM stats
*/
void drv_IpmDebugResetStats(enum com_DxpInstance dxp_instance);

/**
* Return PCU information on a given DXP
* @param dxp_instance DXP instance
* @param index DRV_IPM_DEBUG_FIRST for first item,
*              DRV_IPM_DEBUG_NEXT for next item
* @param buf output buffer (make it big enough >=200 bytes)
* @param buf_len Size of buffer pointed to by buf
* @return true if success, false if failure (when last item is
*         reached)
*/
bool drv_IpmDebugReturnPcuInfo(enum com_DxpInstance dxp_instance,
                               int index,
                               char *buf,
                               uint32 buf_len);

/**
* Return the value of a statistical item
* see drv_stats_ids.h for a list of item IDs
* @param driver_handle Not used
* @param item_id Item ID
* @param int_value pointer to 32-bit variable receiving the item
*                  the item value
*/
void drv_IpmStatsInt(drv_StatsHandle driver_handle,
                     drv_StatsItemId item_id,
                     int32 *int_value);

/**
 * Set deepest allowed power mode
 * @param power_mode The deepest allowed power mode
 */
void drv_IpmDebugSetDeepestAllowedPowerMode(drv_IpmPowerMode power_mode);

/**
 * @return the deepest allowed power mode
 */
drv_IpmPowerMode drv_IpmDebugGetDeepestAllowedPowerMode(void);

/**
 * Power Management Debug function
 *
 * @param param Parameter list (5 words)
 * @param entity Entity context to be passed to atPrintLn
 *               function
 * @param atPrintLn Pointer to function to send messages out to
 *                  the AT command interface
 *
 * @return true if the type is valid
 */
extern bool drv_IpmDbgTest(unsigned long *param,
                           int entity,
                           void atPrintLn(int entity,char *buf));

/**
 * Set Debug Mode Enable
 *
 * @param enable If not zero, force DXS clock ON but do not
 *               prevent HIBERNATE or RETENTION
 */
extern void drv_IpmSetDebugModeEnable(int enable);

/**
 * Schedule immediate wake. This can be used in the case
 * where hibernate entry must be aborted, e.g. because there
 * isn't enough time to hibernate or more generally when the
 * conditions required to hibernate were not met.
 * This can also be used to schedule a dummy task from the context
 * of a post-hibernate callback.
 */
void drv_IpmTriggerImmediateWake(void);

/**
 * Configure IPM to reset the Watch Dog Timer (WDT) on next
 * idle. Note that IPM will only reset the WDT once so this
 * function must called every time WDT needs to be kicked
 */
void drv_IpmResetWdtOnNextIdle(void);

#endif /* #ifndef DRV_IPM_H */
/** @} END OF FILE */


