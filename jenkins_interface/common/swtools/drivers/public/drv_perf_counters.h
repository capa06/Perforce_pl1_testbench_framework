/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_perf_counters.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

 /**
 * @addtogroup drv_perf
  *
  * @{
  */

 /**
  *@file drv_perf_counters.h functions for periodic performance
  *      counter (PCB) capture
  *
  */

#ifndef DRV_PERF_COUNTERS_H
#define DRV_PERF_COUNTERS_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

#include "spd_pcb_regs_cdefs.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* Four channels, ordered like this: DXP ch0, DXP ch1, SoC ch0. SoC ch1 */
#define DRV_AMBEXTMEM_NUM_CHANNELS 4

#define DRV_AMB_ORGMASK_DXP0 BIT(0)
#define DRV_AMB_ORGMASK_DXP1 BIT(1)
#define DRV_AMB_ORGMASK_DXP2 BIT(2)
#define DRV_AMB_ORGMASK_SDMA BIT(6)
#define DRV_AMB_ORGMASK_FDMA BIT(7)

#define DRV_PERF_PCB_SIZE (SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK + 1)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

typedef enum
{
    DRV_PERF_BLOCK_DXP0_2 = 0,
    DRV_PERF_BLOCK_DXP1
} drv_PerfBlock;

typedef enum
{
    DRV_AMB_OPERATION_ACTION_NOP = 0,
    DRV_AMB_OPERATION_ACTION_INT
} drv_AmbAction;

typedef struct
{
    uint32 period_us;
    uint8 ch0_in_use;
    uint8 ch0_org_mask;
    uint8 ch0_i_not_d_mask;
    uint8 ch0_w_not_r_mask;
    uint8 ch0_burst_filter;
    uint8 ch1_in_use;
    uint8 ch1_org_mask;
    uint8 ch1_i_not_d_mask;
    uint8 ch1_w_not_r_mask;
    uint8 ch1_burst_filter;
} drv_AmbInstanceConf;

typedef struct
{
    /* all limits expressed in Bytes/s */
    uint32 ch0_dxs_limit;
    uint32 ch0_soc_limit;
    uint32 ch1_dxs_limit;
    uint32 ch1_soc_limit;
} drv_AmbLimitConf;

typedef enum
{
    DRV_BBMCI_PORT_LL_RD = 0,
    DRV_BBMCI_PORT_DMA_RD,
    DRV_BBMCI_PORT_WR,
    DRV_BBMCI_PORT_NUM
} drv_BbmciPort;

typedef struct
{
    uint32 latency_min;
    uint32 latency_max;
    uint64 latency_avg;
} drv_BbmciCntrStat;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Creates a thread that reads and accumulates PCB counters
 * periodically. Counters are available in an uncached
 * structure: can be read from dxp-run.
 *
 * @param bus_id: DXP to be monitored
 * @param period_us: Sampling period
 * @param initial_enable: Initial accumulate enable state
 * @return void
 *
 */
extern void drv_PcbRunPeriodic(uint32 bus_id, uint32 period_us, uint32 initial_enable);

/**
 * Force the thread created by drv_PcbRunPeriodic to exit and 
 * release the timer used. 
 *
 * @return void
 *
 */
extern void drv_PcbStopPeriodic();

/**
 * Enables/disables PCB counter accumulation by the periodic thread
 * @param enable: New accumulate enable state
 * @return void
 *
 */
extern void drv_PcbPeriodicAccumulationEnable(uint32 enable);

/**
 * Get Enabled/disabled status for PCB counter accumulation
 *
 * @return !=0 if enabled, 0 if disabled
 *
 */
extern uint32 drv_PcbPeriodicAccumulationIsEnabled();

/**
 * Resets PCB accumulated counters
 * @return void
 *
 */
extern void drv_PcbPeriodicResetAccumulatedCounters(void);

/**
 * Add the accumulated counters to a destination buffer
 * @param buffer: destination buffer
 * @return void
 *
 */
extern void drv_PcbPeriodicAddAndResetAccumulation(uint64 *buffer);

/**
 * Read the counters and accumulate with prevopous counters read.
 * Counters are available in an uncached
 * structure: can be read from dxp-run.
 * Use with care.
 *
 * @param bus_id: DXP to be monitored
 *
 */
extern void drv_PcbReadAndAccumulateCounters(uint32 bus_id);

/**
 * Start performance counter on a particular DXP.
 * Should not be used in-conjunction with drv_PcbRunPeriodic.
 *
 * @param dxp : DXP instance
 * @return void
 *
 */
extern void drv_PerfStart(int dxp);

/**
 * Return raw cycles between drv_PerfStart & drv_PerfStop.
 * Should not be used in-conjunction with drv_PcbRunPeriodic.
 *
 * @param dxp : DXP instance
 * @return      32-bit raw cycle count
 *
 */
extern uint32 drv_PerfStop(int dxp);


#if defined(ICE9XXX_UMCD) || defined(ICE9XXX_BBMCI)

/**
 * Creates a thread that reads and accumulates UMCD/BBMCI AMB
 * counters periodically. Counters are available in an uncached
 * structure: can be read from dxp-run.
 *
 * @param conf: Configuration of UMCD/BBMCI AMB and sampling
 * @param initial_enable: Initial accumulate enable state
 * @return void
 *
 */
extern void drv_AmbExtmemRunPeriodic(drv_AmbInstanceConf *conf, uint32 initial_enable);

/**
 * Force the thread created by drv_AmbExtmemRunPeriodic to exit 
 * and release the timer used. 
 *
 * @return void
 *
 */
extern void drv_AmbExtmemStopPeriodic();

/**
 * Enables/disables AMB counter accumulation by the periodic thread
 * @param enable: New accumulate enable state
 * @return void
 *
 */
extern void drv_AmbExtmemPeriodicAccumulationEnable(uint32 enable);

/**
 * Get Enabled/disabled status for AMB counter accumulation
 *
 * @return !=0 if enabled, 0 if disabled
 *
 */
extern uint32 drv_AmbExtmemPeriodicAccumulationIsEnabled();

/**
 * Resets AMB accumulated counters
 * @return void
 *
 */
extern void drv_AmbExtmemPeriodicResetAccumulatedCounters(void);

/**
 * Add the accumulated counters to a destination buffer and provide the max of the counters over a sampling period
 * @param buffer: destination buffer
 * @param buffer-max: destination buffer for the max values
 * @return void
 *
 */
void drv_AmbExtmemPeriodicAddAndResetAccumulation(uint64 *buffer, uint64 *buffer_max, uint64 *periodic_count);

/**
 * Returns B/s value from monitored channels
 * @param bytes_per_sec: Pointer to array receiving B/s values
 * @return !=0 if target array is written with valid B/s values, 0 otherwise
 *
 */
extern uint32 drv_AmbExtmemPeriodicGetBytesPerSec(uint32 *bytes_per_sec);

/**
 * Sets up reapeated window on AMB, with limits
 * @param conf: Configuration of UMCD/BBMCI AMB and sampling
 * @param limits: Throughput limits
 * @param action: Action taken on violating limits
 *
 */
extern void drv_AmbExtmemSetupAutoRepeatWindow(drv_AmbInstanceConf *conf, drv_AmbLimitConf *limits, drv_AmbAction action);

/**
 * Get the status of the limits set on the AMB counters.
 * reporting 0 means that the limit has not been reached.
 * reporting other values means that the limit was reached.
 * @param dxs_status: pointer where to report status for dxs
 * @param dxs_status: pointer where to report status for soc
 */
void drv_AmbExtmemGetAndClearPintStatus(int *dxs_status, int *soc_status);

#endif /* defined(ICE9XXX_UMCD) || defined(ICE9XXX_BBMCI) */


#if defined(ICE9XXX_BBMCI)

/**
 * Enable and configure BBMCI latency counters
 * @param reset_counters: reset counters while enabling them
 * @return void
 *
 */
extern void drv_BbmciCntrStart(uint32 reset_counters);

/**
 * Read BBMCI latency counters
 * @param stat: stats filled; a pointer to an array of DRV_BBMCI_PORT_NUM items
 * @param reset_counters: reset counters after reading them
 * @return void
 *
 */
extern void drv_BbmciCntrGetStat(drv_BbmciCntrStat *stat, uint32 reset_counters);

#endif /* defined(ICE9XXX_BBMCI) */

/**
 * Start performance monitoring. What is started depends on the build #defines.
 *
 */
extern void drv_PerfMonitoringInit(void);

#endif

/** @} END OF FILE */
