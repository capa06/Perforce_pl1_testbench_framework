/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_apm.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup ApmDriver Active Power Management Driver
 * Active Power Management driver
 * @ingroup  PwrMgt
 */

/**
 * @addtogroup ApmDriver
 * @{
 */

/**
 * @file drv_apm.h Active Power Management driver public interface
 *
 */

#ifndef DRV_APM_H
#define DRV_APM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_APM_MAX_NUM_PROFILES (12)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * APM version
 */
typedef enum
{
    DRV_APM_VERSION_DUMMY = 0,
    //DRV_APM_VERSION_V1   = 0x00010000,  /* 8040 APM variant (historic, no longer supported) */
    //DRV_APM_VERSION_V2   = 0x00020000,  /* 8060 APM2 variant  (historic, no longer supported) */
    DRV_APM_VERSION_V2_1 = 0x00020001,  /* 9xxx APM2 variant */
    DRV_APM_VERSION_V3   = 0x00030000,  /* 9xxx APM3 (DFLL) variant with profile mode support */
    DRV_APM_VERSION_V3_1 = 0x00030001   /* 9xxx APM3 (DFLL) variant with NO profile mode support */
} drv_ApmVersion;

/**
 * APM state
 */
typedef enum
{
    DRV_APM_STATE_FORCED_TO_MAX_MHZ = 0,
    DRV_APM_STATE_DISABLED = DRV_APM_STATE_FORCED_TO_MAX_MHZ,
    DRV_APM_STATE_NORMAL_OPERATION = 1,
    DRV_APM_STATE_ENABLED = DRV_APM_STATE_NORMAL_OPERATION,
    DRV_APM_STATE_FORCED_TO_HIGH_MHZ = 2,
    DRV_APM_STATE_FORCED_FLAT = 3,
    DRV_APM_STATE_FORCED_INITIAL = 4,
    DRV_APM_STATE_FORCED_MHZ = 5,
    DRV_APM_STATE_LAST_APM_IN_BUILD = DRV_APM_STATE_FORCED_MHZ,
    DRV_APM_STATE_NOT_IN_BUILD = DRV_APM_STATE_LAST_APM_IN_BUILD + 1
} drv_ApmState;

/**
 * Frequency floor selection list
 */
typedef enum
{
    DRV_APM_FREQ_FLOOR_DEFAULT   = 0,
    DRV_APM_FREQ_FLOOR_SLOW_BBRF = 1,
    DRV_APM_FREQ_FLOOR_FAST_BBRF = 2,
    DRV_APM_FREQ_FLOOR_NUM
} drv_ApmFreqFloorSel;

/**
 * Execution profile descriptor
 */
typedef struct
{
    uint32 profile_length;            /**< Execution profile length (quarter chips) */
    uint32 min_high_interval_length;  /**< Minimum requested high interval of the profile duration (quarter chips) */
    uint32 high_mhz;                  /**< MHz required for the high interval of the execution profile */
    uint32 average_mhz;               /**< Long term average required MHz for the execution profile */
} drv_ApmProfileDesc;

/**
 * Externally available state information
 */
typedef struct
{
    drv_ApmVersion apm_version;       /**< APM version */
    uint8 profile_mode_supported;     /**< 0 means APM does not support profile mode, !=0 means profile mode is supported */
    uint8 in_profile_mode;            /**< 0 means APM is in direct (flat) mode, !=0 means APM is in profile mode */
    uint16 high_dxp_mhz;              /**< high interval DXP MHz */
    uint16 low_dxp_mhz;               /**< low interval DXP MHz */
    uint16 high_soc_var_mhz;          /**< high interval var SoC MHz */
    uint16 low_soc_var_mhz;           /**< low interval var SoC MHz */
    uint16 min_direct_dxp_mhz;        /**< Minimum direct MHz (i.e. frequency floor); valid only for DRV_APM_VERSION_V3 */
} drv_ApmInfo;

/**
 * Externally available statistics
 */
typedef struct
{
    uint32 event_counter;             /**< profile mode period counter if profile mode supported, request counter otherwise */
    uint32 time_high;                 /**< time spent in high interval (in stat ticks) if profile mode supported (0 otherwise) */
    uint32 time_low;                  /**< time spent in low interval (in stat ticks) if profile mode supported (0 otherwise) */
    uint64 cumulative_avg2_mhz;       /**< cumulative average MHz squared (for variance, to get real avg, divide by cumulative_counter) */
    uint32 cumulative_avg_mhz;        /**< cumulative average MHz (to get real avg, divide by cumulative_div) */
    uint32 cumulative_avg_high_mhz;   /**< cumulative average high MHz (to get real avg, divide by cumulative_div) if profile mode supported (0 otherwise) */
    uint32 cumulative_avg_low_mhz;    /**< cumulative average high MHz (to get real avg, divide by cumulative_div) if profile mode supported (0 otherwise) */
    uint32 cumulative_div;            /**< divisor for cumulative values above */
    uint16 stat_ticks_per_ms;         /**< stat ticks per ms */
} drv_ApmStats;


/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Opens APM driver.
 *
 * @param dxp0_mhz Initially requested DXP0 MHz (0 is a valid request).
 *
 * @return void.
 */
extern void drv_ApmOpen(uint32 dxp0_mhz);

/**
 * Closes APM driver (not implemented - always returns an error).
 *
 * @return void.
 */
extern void drv_ApmClose(void);

/**
 * Registers an execution profile in APM.
 *
 * @param profile_id Returned profile ID (if registration successful), always !=0.
 * @param desc Profile descriptor for the profile being registered.
 *
 * @return void.
 */
extern void drv_ApmRegisterProfile(uint32 *profile_id, const drv_ApmProfileDesc *desc);


/**
 * Unregisters an execution profile in APM.
 *
 * @param profile_id Profile ID to unregister.
 *
 * @return void.
 */
extern void drv_ApmUnregisterProfile(uint32 profile_id);

/**
 * Selects an execution profile in APM. Can be called from DXP0 only.
 *
 * @param profile_id Selected profile ID (0 unselects the profile).
 * @param dxp_mhz Requested direct MHz (meaningful only if profile_id==0).
 *
 * @return void.
 */
extern void drv_ApmSelectProfile(uint32 profile_id, uint32 dxp_mhz);


/**
 * Requests directly (non-profile based) MHz. Can be called from DXP1 only.
 *
 * @param dxp_mhz Requested MHz (0 is a valid request).
 *
 * @return void.
 */

extern void drv_ApmRequestMhz(uint32 dxp_mhz);


/**
 * Sets operation mode. Callable from DXP1 only.
 * Intended to be used by an AT command.
 *
 * @param operation_mode Operation mode
 * @param param Operation mode parameter
 *
 * @return void.
 */

extern void drv_ApmSetOperationMode(drv_ApmState operation_mode, uint32 param);

/**
 * Starts the process of changing the frequency floor.
 * drv_ApmChangeFrequencyFloorStart must always be followed by drv_ApmChangeFrequencyFloorComplete
 * This function is non-blocking.
 *
 * @param freq_floor_sel Frequency floor selection
 *
 * @return void.
 */
extern void drv_ApmChangeFrequencyFloorStart(drv_ApmFreqFloorSel freq_floor_sel);

/**
 * Attempts to complete the process of changing the frequency floor.
 * If the change is complete, returns a value !=0
 * This function is non-blocking.
 * drv_ApmChangeFrequencyFloorComplete must always be preceded by drv_ApmChangeFrequencyFloorStart
 * This function is non-blocking.
 *
 * @return uint32: "Completed" flag.
 */
extern uint32 drv_ApmChangeFrequencyFloorComplete(void);

/**
 * Overrides the current frequency floor selection.
 * For AT command use.
 *
 * @param freq_floor_mhz Frequency floor in MHz
 *
 * @return void.
 */
extern void drv_ApmOverrideFrequencyFloor(int32 freq_floor_mhz);

/**
 * Overrides the default request scaling factor.
 * For AT command use.
 *
 * @param new_scaling_factor New scaling factor (in %; -1 switches off the override; 0 requests current value only)
 *
 * @return Current scaling factor.
 */
extern uint32 drv_ApmOverrideScalingFactor(int32 new_scaling_factor);

/**
 * Converts an operation mode id to a string describing it.
 *
 * @param operation_mode Operation mode
 *
 * @return String describing the operation mode given.
 */

extern char *drv_ApmGetOperationModeString(drv_ApmState operation_mode);


/**
 * Retrieves info about APM.
 * Intended to be used by an AT command.
 *
 * @param operation_mode Returns APM operation mode
 * @param info Returns APM current information.
 * @param stats Returns APM statistics.
 *
 * @return void.
 */

extern void drv_ApmGetInfo(drv_ApmState *operation_mode, drv_ApmInfo *info, drv_ApmStats *stats);


/**
 * Resets APM statistics.
 * APM gathers statistics about its execution.
 * This statistics can be retrieved using drv_ApmGetInfo.
 * Statistics is reset:
 *  - on request calling drv_ApmResetStats
 *  - autonomously when statistics counters overflow
 * DXP0 function.
 *
 * @return void.
 */

extern void drv_ApmResetStats(void);


/**
 * Signals the beginning of the high interval to APM.
 *
 * @return void.
 */
#define drv_ApmToggleIntervalToHighWithNow(now) drv_ApmToggleIntervalToHigh()
extern void drv_ApmToggleIntervalToHigh(void);


/**
 * Signals the beginning of the low interval to APM.
 *
 * @param local_profile_length (quarter chips)
 * @param local_low_mhz_delta
 *
 * @return Configuration change pending status (!=0 -> pending).
 */
extern uint32 drv_ApmToggleIntervalToLow(uint32 local_profile_length, int32 local_low_mhz_delta);


/**
 * Returns the current sequence number.
 * LSB of the sequence number encodes interval: 0:high, 1:low
 *   - always 0 in flat mode
 *   - in profile mode it doesn't go to 1 if APM decides not to go to low interval
 * remaining bits are the real sequence number
 *   that increases monotonically every profile period
 *   until it wraps from max 32-bit value to 0
 *
 * @return Sequence number.
 */
extern uint32 drv_ApmGetSequenceNumber(void);


/**
 * Prepares APM for post-hibernation power-up.
 * Expected to be called from power-up IPM callback
 *
 * @return void.
 */
extern void drv_ApmPostHibPowerUp(void);


/**
 * Completes APM post-hibernation power-up.
 * Expected to be called from a normal thread
 *
 * @return void.
 */
extern void drv_ApmPostHibComplete(void);


/* These are debug functions */

/**
 * Returns a 'Vdd change pending' flag. If it's 0, latest Vdd request has been completed.
 *
 * @return Configuration change pending status (!=0 -> pending).
 */
extern uint32 drv_ApmDebugVddChangePending(void);


#endif /* DRV_APM_H */

/** @} END OF FILE */

