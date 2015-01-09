
/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_stats_ids.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DrvStatsID Driver Statistics IDs
 * @ingroup  Driver
 */

/**
 * @addtogroup DrvStats
 * @{
 */

/**
 * @file drv_stats_ids.h Driver Statistics IDs
 */

#ifndef DRV_STATS_IDS_H
#define DRV_STATS_IDS_H

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
 *  enumeration of statistical item ids
 */
typedef enum
{
    DRV_STATS_ID_LAST_ITEM_ID=0,
    /* IPM */
    DRV_STATS_ID_IPM,
    DRV_STATS_ID_IPM_SYSTEM_TIME,
    DRV_STATS_ID_IPM_UPTIME,
    DRV_STATS_ID_IPM_DOWNTIME,
    DRV_STATS_ID_IPM_LOAD,
    DRV_STATS_ID_IPM_IDLE_TIME_DISTRIB,
    DRV_STATS_ID_IPM_DXP0,
    DRV_STATS_ID_IPM_DXP0_N_DMEM_ACTIVE,
    DRV_STATS_ID_IPM_DXP0_N_DXP_IDLE,
    DRV_STATS_ID_IPM_DXP0_N_SOC_IDLE,
    DRV_STATS_ID_IPM_DXP0_N_POWER_OFF,
    DRV_STATS_ID_IPM_DXP0_LAST,
    DRV_STATS_ID_IPM_DXP1,
    DRV_STATS_ID_IPM_DXP1_N_DMEM_ACTIVE,
    DRV_STATS_ID_IPM_DXP1_N_DXP_IDLE,
    DRV_STATS_ID_IPM_DXP1_N_SOC_IDLE,
    DRV_STATS_ID_IPM_DXP1_N_POWER_OFF,
    DRV_STATS_ID_IPM_DXP1_LAST,
    /* sync RTC/CET */
    DRV_STATS_ID_SYNC_RTC_CET,
    DRV_STATS_ID_SYNC_RTC_CET_MIN_WAKEUP_TIME,
    DRV_STATS_ID_SYNC_RTC_CET_MAX_WAKEUP_TIME,
    /* USB */
    DRV_STATS_ID_USB,
    DRV_STATS_ID_USB_SUSPEND_COUNT,
    DRV_STATS_ID_USB_RESUME_COUNT,
    DRV_STATS_ID_USB_REMOTE_WAKEUP_COUNT,
    DRV_STATS_ID_USB_ENUMERATION_COUNT,
    DRV_STATS_ID_USB_EP_ERROR_COUNT,
    /* Wireless Disable */
    DRV_STATS_ID_WIRELESS_DISABLE,
    /* cal 32k */
    DRV_STATS_ID_CAL32K,
    DRV_STATS_ID_CAL32K_DRIFT_STATS_2G,
    DRV_STATS_ID_CAL32K_DRIFT_STATS_3G,
    DRV_STATS_ID_CAL32K_DRIFT_STATS_LTE,
    DRV_STATS_ID_CAL32K_STATE_STATS,
    DRV_STATS_ID_CAL32K_CALTIME_STATS,
    DRV_STATS_ID_CAL32K_LO_RES_FREQ,
    DRV_STATS_ID_CAL32K_CURRENT_STATE,
    /* SHM */
    DRV_STATS_ID_SHM,
    DRV_STATS_ID_SHM_QUEUE,
    DRV_STATS_ID_SHM_IOBUF,
    DRV_STATS_ID_SHM_IF,
    DRV_STATS_ID_SHM_QUEUE_PUT,
    DRV_STATS_ID_SHM_QUEUE_GET,
    DRV_STATS_ID_SHM_IOBUF_ALLOC,
    DRV_STATS_ID_SHM_IOBUF_FREE,
    DRV_STATS_ID_SHM_IF_SENT,
    DRV_STATS_ID_SHM_IF_RECEIVED,
    DRV_STATS_ID_SHM_IF_GIVEN,
    DRV_STATS_ID_SHM_IF_TAKEN,
    DRV_STATS_ID_SHM_SIGNAL,
    DRV_STATS_ID_SHM_SIGNAL_UL,
    DRV_STATS_ID_SHM_SIGNAL_DL,
    /* IPC Timers */
    DRV_STATS_ID_IPC_TIMER,
    DRV_STATS_ID_IPC_TIMER_ACTIVITY_COUNT,
    DRV_STATS_ID_IPC_TIMER_FLUSH_COUNT,
    DRV_STATS_ID_IPC_TIMER_AP_WAKE_COUNT,
    /* Wake Scheduler */
    DRV_STATS_ID_WAKESCH,
    DRV_STATS_ID_WAKESCH_MAX_RESTORE_TIME,
    DRV_STATS_ID_WAKESCH_MIN_RESTORE_TIME,
    DRV_STATS_ID_WAKESCH_EMC_WAIT_COUNT,
    /* Malloc in heap */
    DRV_STATS_ID_MALLOC,
    DRV_STATS_ID_MALLOC_NUM_CURRENT,
    DRV_STATS_ID_MALLOC_NUM_PEAK,
    DRV_STATS_ID_MALLOC_NUM_ALL,
    DRV_STATS_ID_MALLOC_BYTE_CURRENT,
    DRV_STATS_ID_MALLOC_BYTE_PEAK,
    DRV_STATS_ID_MALLOC_BYTES_ALL,
    DRV_STATS_ID_MALLOC_BYTE_AVAIL_CURRENT,
    DRV_STATS_ID_MALLOC_BYTE_AVAIL_PEAK,
    /* iobuf stats */
    DRV_STATS_ID_IOBUF_FREE_CURRENT,
    DRV_STATS_ID_IOBUF_FREE_MIN,
    DRV_STATS_ID_IOBUF,
    /* NCM1.0 MBIM network interface */
    DRV_STATS_ID_NCM_NDP_DECODE_ERR,
    DRV_STATS_ID_NCM_NDP_ENTRY_VALIDATE_ERR,
    DRV_STATS_ID_NCM_NDP_SIGNATURE_ERR,
    DRV_STATS_ID_NCM_NTH_SIGNATURE_ERR,
    DRV_STATS_ID_NCM_NTH_HEADER_LENGTH_ERR,
    DRV_STATS_ID_NCM,
} drv_StatsItemId;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

#endif /* #ifndef DRV_STATS_IDS_H */

/** @} END OF FILE */

