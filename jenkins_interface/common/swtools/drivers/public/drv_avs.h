/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_avs.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup AvsDriver AVS Driver
 * @ingroup PwrMgt
 */

/**
 * @addtogroup AvsDriver
 * @{
 */

/**
 * @file drv_avs.h AVS public interface
 *
 */

#ifndef DRV_AVS_H
#define DRV_AVS_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include "icera_global.h"

#ifdef HOST_TESTING
#include "ht_stub.h"
#endif

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_AVS_OK      1
#define DRV_AVS_ERROR   0

#define DRV_AVS_UNCHANGED_VOLT (0)
#define DRV_AVS_DEFAULT_SAFE_VOLT (0xfff)
#define DRV_AVS_DEFAULT_VOLT (0xfff-1)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/* Enum for the profile mode of the AVS driver */
typedef enum
{
    DRV_AVS_FLAT_PROFILE     = 0,
    DRV_AVS_INTERVAL_PROFILE = 1
} drv_AvsProfileMode;

/* Enum for the intervals for PMU measurements */
typedef enum
{
    DRV_AVS_HIMHZ        = 0,
    DRV_AVS_LOWMHZ       = 1,
    DRV_AVS_NMB_INTERVAL = 2
} drv_AvsInterval;

/* Enum for the state of the AVS driver */
typedef enum
{
    DRV_AVS_SLOW_MODE    = 0,
    DRV_AVS_FAST_MODE    = 1,
    DRV_AVS_SUSPEND_MODE = 2,
    DRV_AVS_INITIAL_MODE = 3
} drv_AvsMode;

/* PMUs on 9xxx */
typedef enum
{
    DRV_AVS_PMU0_LOGIC = 0,
    DRV_AVS_PMU0_METAL = 1,
    DRV_AVS_PMU1_LOGIC = 2,
    DRV_AVS_PMU1_METAL = 3,
    DRV_AVS_PMU2_LOGIC = 4,
    DRV_AVS_PMU2_METAL = 5,
    DRV_AVS_PMU3_LOGIC = 6,
    DRV_AVS_PMU3_METAL = 7,
    DRV_AVS_PMU4_LOGIC = 8,
    DRV_AVS_PMU4_METAL = 9,
    DRV_AVS_PMU5_LOGIC = 10,
    DRV_AVS_PMU5_METAL = 11,
    DRV_AVS_PMU6_LOGIC = 12,
    DRV_AVS_PMU6_METAL = 13,
    DRV_AVS_PMU7_LOGIC = 14,
    DRV_AVS_PMU7_METAL = 15,
    DRV_AVS_PMU8_LOGIC = 16,
    DRV_AVS_PMU8_METAL = 17,
    DRV_AVS_PMU9_LOGIC = 18,
    DRV_AVS_PMU9_METAL = 19,
    DRV_AVS_PMU10_LOGIC = 20,
    DRV_AVS_PMU10_METAL = 21,
    DRV_AVS_PMU11_LOGIC = 22,
    DRV_AVS_PMU11_METAL = 23,
    DRV_AVS_PMUM0_RAM_CELL = 24,
    DRV_AVS_PMUM1_RAM_CELL = 25,
    DRV_AVS_PMUM2_RAM_CELL = 26,
    DRV_AVS_NO_CLK1 = 27,
    DRV_AVS_NO_CLK2 = 28,
    DRV_AVS_NO_CLK3 = 29,
    DRV_AVS_NO_CLK4 = 30,
    DRV_AVS_CRPC_CLK5  = 31,
    DRV_AVS_PMU_INVALID,
    DRV_AVS_PMU_AUTOREAD_MAX = DRV_AVS_PMUM2_RAM_CELL + 1
} drv_AvsOscID;

/*
 * These 2 structures are storing debugging information and stats...
 */
typedef struct
{
    int pmu_read_success;
    int pmu_read_fail;
    int voltage_update_done;
    int voltage_update_failed;
    int voltage_update_canceled;
    int voltage_update_retried;
} drv_AvsIntervalStats;

typedef struct
{
    int profile_req;
    int flat_req;
} drv_AvsGlobalStats;


/**
 * AVS information for a given interval
 */
typedef struct
{
    int dxp_clk;                 /**< Curent dxp clock */
    int core_mv;                 /**< Current mV for the core */
    int last_voltage_request;    /**< Last mV requested for the core  */
    drv_AvsMode operation_mode;  /**< Fast or Slow, tells us where we are in the convergence process */
    drv_AvsProfileMode profile_mode;
    int pmu[DRV_AVS_PMU_AUTOREAD_MAX];
    int clock_estimate;
    int floorfreq;
    drv_AvsIntervalStats interval_stats;
    drv_AvsGlobalStats global_stat;
} drv_AvsDetails;


/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize and start the AVS driver
 *
 *  Resources needed for AVS (AVS-GUT, GPT2) are locked.
 *  AVS thread is created,
 *  Monitoring is started on the default values.
 *  Can be called from either DXP, the thread will be created on the dxp used to make this call.
 *
 * @param si_speed_mhz_target: MHz target for silicon speed auto-discovery (0 means assume AVS default)
 * @param initial_core_mhz_margin: Initial MHz margin
 * @param initial_floor_frequency: Initial frequency floor
 *
 * @return int equal to DRV_AVS_OK if the operation was succesfull.
 */
extern int drv_AvsOpen(unsigned int si_speed_mhz_target, int initial_core_mhz_margin, int initial_floor_frequency);

/**
 * Stops the AVS driver.
 *
 * AVS, AVS-GUT, GPT2 released,
 * The AVS thread is destroyed.
 * Can be called from either DXP.
 *
 * @return void
 */
extern void drv_AvsClose(void);

/**
 *
 * Return the margin currently in use
 *
 * @see drv_AvsGetMargin
 *
 * @return int: margin value currently in use (in MHz)
 */
extern int drv_AvsGetMargin(void);

/**
 * Set the MHz margin for AVS operations
 *
 * the AVS driver uses the supplied safety margin for subsequent voltage monitoring. Can be called from either DXP.
 * Be EXTREMELY careful with the margin you apply as this may lead to instabilities.
 *
 * @param mhz: voltage safety margin in MHz
 * @return void
 */
extern void drv_AvsSetMargin(int mhz);

/**
 * Set up a flat MHz request for a given component.
 *
 * Clock frequency and voltage levels are set to support highest requested performance level.
 * Avs will handle the right voltage transition and clock set up in a safe and quick fashion.
 * Will cancel previous request for that component.
 * Will cancel profiled mode if previously set up.
 * Can be called from either DXP.
 *
 * @param mhz is performance required for that component.
 * @return void
 */
extern void drv_AvsRequireMHz(unsigned int mhz);

/**
 * Get Avs details.
 *
 * Obtain various data about the AVS driver operation
 *
 * @see drv_AvsDetails
 *
 * @param avs_details: Pointer to a structure of type drv_AvsDetails that will be filled by the AVS driver with  the relevant information.
 * @param interval: The interval for which we want to obtain the data (ignored in flat mode)
 * @return unsigned int: DRV_AVS_OK if successfull, something else if not (most likely avs_driver not running)
 */
extern unsigned int drv_AvsGetAvsDetails(drv_AvsDetails *avs_details, drv_AvsInterval interval);

/**
 * Returns the current disabled state
 * AVS is considered disabled when both voltage limits are set to max voltage
 *
 *
 * @see drv_AvsIsDisabled
 *
 * @return unsigned int: 'AVS disabled' flag
 */
extern unsigned int drv_AvsIsDisabled(void);

/**
 * Returns the current voltage limits in use for vCore.
 *
 *
 * @see drv_AvGetVoltageLimits
 *
 * @param low:  Pointer to a int32 that the API will fill with the lower limit for vCore in mV.
 * @param high: Pointer to a int32 that the API will fill with the higher limit for vCore in mV.
 * @return unsigned int: DRV_AVS_OK if successfull, something else if not (most likely avs_driver not running)
 */
extern unsigned int drv_AvsGetVoltageLimits(int32* low, int32* high);

/**
 * Modify the voltage limits for vCore.
 * The voltage may be changed immediately to be within the requested values.
 * To force operations at a given voltage: prvide the same value for both limits
 * Be EXTREMELY careful with the voltage you apply as some combination of clock settings/ vCore value may lead to some instabilities
 *
 * @see drv_AvsSetVoltageLimits
 *
 * @param low:  a int32 that contain the new value to be used for the lower limit for vCore in mV.
 * @param high: a int32 that contain the new value to be used for the higher limit for vCore in mV..
 * @return unsigned int: DRV_AVS_OK if successfull, something else if not (most likely avs_driver not running or the boundaries are not in the right order)
 */

extern unsigned int drv_AvsSetVoltageLimits(int32 low, int32 high);

/**
 * Reset the statistical counter... No impact on operation.
 *
 * @see drv_AvsResetStats
 *
 */
extern void drv_AvsResetStats(void);

#endif /* DRV_AVS_H */
/** @} END OF FILE */
