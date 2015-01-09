/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_cal32k.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

#ifndef DRV_CAL32K_H
#define DRV_CAL32K_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "drv_rtb.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#ifdef __dxp__
#include "dxpnk_types.h"      /* NanoK types and defines       */
#include "icera_global.h"     /* Global defines (such as bool) */
#else /* #ifdef __dxp__ */
#include "types.h"
#endif /* #ifdef __dxp__ */

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_CAL32K_IDEAL_LOW_FREQ ((double)DRV_RTB_FREQ)
#define DRV_CAL32K_DIFF_FILTER_COEFF    (0.1)
#define DRV_CAL32K_INVALID_FREQUENCY (0)

/**
 * Time (in high res ticks) after which a calibration sample is
 * considered meaningless since the temperature and the Low
 * Resolution frequency may have changed dramatically
 *
 */
#define DRV_CAL32K_MAX_CALIBRATION_TIME_SECONDS (10) /* in seconds */

/**
 * Drift statistics are reported as bins of a histogram
 * The number of bins is set by the define below - make it
 * an even number for better display, so there are an integer
 * number of bins on the negative range and on the positive
 * range
 */
#define DRV_CAL32K_DRIFT_STATS_BINS (6*2)

/**
 * Total span covered by drift bins, expressed as a multiple of
 * the drift threshold.
 *
 * example: 3 means we will cover 1.5 thresholds in the negative
 * range, 1.5 thresholds in the positive range
 */
#define DRV_CAL32K_DRIFT_STATS_SPAN (3)

/**
 * Cal time statistics are reported as bins of a histogram The
 * number of bins is set by the define below
 */
#define DRV_CAL32K_CAL_TIME_STATS_BINS (15)

/**
 * Cal time bin size (expressed in RTC ticks)
 *
 */
#define DRV_CAL32K_CAL_TIME_STATS_BIN_SIZE ( 10*DRV_RTB_FREQ/1000 ) /* 10ms */

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  enumeration of paging scenarios
 */
typedef enum
{
    DRV_CAL32K_SCENARIO_2G=0,
    DRV_CAL32K_SCENARIO_3G,
    DRV_CAL32K_SCENARIO_LTE,
    DRV_CAL32K_NUM_SCENARIOS
} drv_Cal32kPagingScenario;

/**
 *  enumeration of paging scenarios
 */
typedef enum
{
    DRV_CAL32K_ACQUISITION=0,
    DRV_CAL32K_SETTLING,
    DRV_CAL32K_STABLE,
    DRV_CAL32K_NUM_STATES
} drv_Cal32kState;

/**
 * Cal32k parameters and state variables
 */
typedef struct
{
    /**
     * the paging scenario to configure the paging scenario for
     */
    drv_Cal32kPagingScenario paging_scenario;

    /**
     * the last time_drift reported by PL1
     */
    uint32 time_drift;

    /**
     * High resolution frequency
     */
    uint64 high_resolution_frequency;

    /**
     * Estimate of low resolution frequency
     */
    double low_resolution_frequency_estimate;

    /**
     * filter frequency drift (from frequency express in PPM)
     */
    double frequency_drift_filter;

    /**
     * last frequency drift rate
     */
    double frequency_drift_rate;

    /**
     * Last sample (expressed in PPM for ideal low frequency)
     */
    double last_sample_ppm;

    /**
     * Timestamp for when we received the last sample
     */
    uint64 last_sample_timestamp;

    /**
     * Indicate whether the calibration has converged
     */
    drv_Cal32kState current_state;

    /**
     * The last scenario that was reported by PL1
     */
    drv_Cal32kPagingScenario current_scenario;

    /**
     *  Array of drift statistics There are
     *  DRV_SYNC_DRIFT_STATS_BINS bins for each RAT. The span of all
     *  bins is indicated by DRV_SYNC_STATS_SPAN
     *
     * example:
     *  threshold=10
     *  nbins=8
     *  span=4 => bins will be:
     *   ]-inf,-15[,[-15,-10[,[-10,-5[,[-5,0[,[0,5[,[5,10[,[10,15[,[15,inf[
     */
    uint32 drift_stats[DRV_CAL32K_NUM_SCENARIOS][DRV_CAL32K_DRIFT_STATS_BINS];

    /**
     *  Array of cal time statistics There are DRV_SYNC_CAL_TIME_STATS_BINS
     *  bins.
     *  Each bin represents a duration of
     *  DRV_SYNC_CAL_TIME_STATS_BIN_SIZE RTC cycles
     */
    uint32 caltime_stats[DRV_CAL32K_CAL_TIME_STATS_BINS];

    /**
     *  Array of State stats - one element per state, this tracks
     *  the number of hits of every state
     */
    uint32 state_stats[DRV_CAL32K_NUM_STATES];

    /**
     * Min wake time (expressed in RTC cycles) - for test purpose
     * only
     */
    uint32 test_mode_min_wake_time_rtc;

    /**
     * last hibernate duration
     */
    uint64 last_hibernate_duration_rtc;

    /**
     * PL1 drift reported since last fix
     */
    uint32 pl1_drift_report_since_last_fix;

} drv_Cal32kPrivateHandle;

/**
 * Calibration parameters for a given mode
 */
typedef struct
{
    /**
     * if the drift indicator is less than this value, we switch to the lower (quicker) mode
     */
    double stability_threshold;

    /**
     * if the drift indicator is greater than this value, we switch to the upper (safer) mode
     */
    double instability_threshold;

    /**
     * minimum calibration duration, expressed in low resolution cycles
     */
    uint64 min_calibration_duration;

    /**
     * user friendly name
     */
    char *name;
} drv_Cal32kStateParameters;


/**
 * Min cal time parameters
 */
typedef struct
{
    /**
     * min sleep time for this parameter
     */
    uint64 min_sleep_time;

    /**
     * min cal time for this parameter
    */
    uint64 min_cal_time;

} drv_Cal32kMinCalTimeParameters;


/*************************************************************************************************
 * Public Variable Definitions
 ************************************************************************************************/

/**
 * parameters and state variables - this is made public in order to facilitate inspection
 * during debug
 */
extern drv_Cal32kPrivateHandle drv_cal32k_handle;

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * drv_Cal32kInit
 *
 * Initialise the crystal calibration algorithm
 *
 * @param high_resolution_frequency Frequency of the high resolution clock
 * @return none
*/
void drv_Cal32kInit(uint64 high_resolution_frequency);


/**
 * drv_Cal32kSetScenario
 *
 * Configure the calibration algorithm for a specific scenario. The scenario is inferred from the paging
 * interval settings
 *
 * @param paging_scenario The scenario to configure the calibration for
 * @return none
*/
void drv_Cal32kSetPagingScenario(drv_Cal32kPagingScenario paging_scenario);

/**
 * drv_Cal32kAlignCalibrationDuration
 *
 * Align the calibration duration, expressed in low resolution ticks, to the nearest desired
 * boundary.
 * Aligning the calibration duration allows for the introduction of various optimisation
 * techniques that reduce the measurement error.
 * Depending on the algorithm, the aligned calibration duration may be
 * several low resolution ticks longer than the length provided.
 *
 * @param calibration_duration The calibration duration, expressed in low resolution ticks
 * @return The aligned calibration duration
*/
uint64 drv_Cal32kAlignCalibrationDuration(uint64 calibration_duration);

/**
 * drv_Cal32kGetMinCalibrationDuration
 *
 * Depending on whether the calibration has converged or not, the desired duration
 * of calibration will vary. This function returns the minimum duration required at
 * a particular point of time
 *
 * @param The expected time until the next wake-up expressed in
 *            low resolution ticks
 * @return The aligned calibration duration
*/
uint64 drv_Cal32kGetMinCalibrationDuration(uint64 lowres_tick_till_wakeup);

/**
 * drv_Cal32kAddCalibrationSample
 *
 * Provide a new sample of calibration data to the calibration algorithm
 *
 * @param timestamp The current timestamp, expressed in low res
 *                  ticks
 * @param low_resolution_ticks Calibration length, expressed in low resolution ticks
 * @param high_resolution_ticks Calibration length, expressed in high resolution ticks
 * @return none
*/
void drv_Cal32kAddCalibrationSample(uint64 rtc_timestamp,
                                    uint64 high_resolution_ticks,
                                    uint64 low_resolution_ticks);

/**
 *
 * drv_Cal32kAddTimeDriftSample
 *
 * Provide a new time drift sample to the calibration algorithm.
 * This is used to adapt the duration of calibration, should the
 * time drift exceed an arbitrary threshold
 *
 * @param time_drift The time drift, expressed in eighth_chips
 *                      or bits, depending on the current
 *                      scenario (2G, 3G or LTE)
 * @param rat The RAT being used
*/
void drv_Cal32kAddTimeDriftSample(int32 time_drift, drv_Cal32kPagingScenario rat);

/**
 * drv_Cal32kGetFilteredFrequency
 *
 * Return the output of the frequency filter
 *
 * @param none
 * @return The low resolution frequency
*/
double drv_Cal32kGetLowResolutionFrequency(void);

/**
 * drv_Cal32kHasConverged
 *
 * Return whether the calibration has converged
 *
 * @param none
 * @return true if the calibration has converged, false otherwise
*/
bool drv_Cal32kHasConverged(void);

/**
 * Return point to array of drift statistics - statistics are
 * returned in the form of histogram bins.
 *
 *
 * @param rat The RAT to return drift stats of
 * @return pointer to the array of drift stats (the array is
 * DRV_SYNC_STATS_BINS long)
 *
*/
uint32 *drv_Cal32kGetDriftStats(drv_Cal32kPagingScenario rat);

/**
 * Return the algo state - this should only be used for
 * information purpose i.e. not of the state fields should be
 * updated
 * @return point to the sync algo state
 *
*/
drv_Cal32kPrivateHandle *drv_Cal32kGetState(void);

/*
 * Set min awake time (for debug/testing purpose)
 * @param min_wake_time_ms Min wake time (expressed in ms)
*/
void drv_Cal32kSetMinWakeTime(uint32 min_wake_time_ms);

/**
*   Return an offset (in seconds) to apply to the system
*   timebase to compensate time drift compensation
*/
double drv_Cal32kFixDrift(void);

/**
 * Notify cal32k driver that we just woke up from hibernate
 *
 * @param rtc_timestamp RTC timestamp at wake (CET enable)
 */
void drv_Cal32kNotifyWakeFromPowerOff(uint64 rtc_timestamp);

#endif /*DRV_CAL32K_H_*/
