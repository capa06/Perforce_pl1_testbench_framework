
/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_wake_sch.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DrvWakeSch Schedule Wake from Hibernate
 * @ingroup  HighLevelServices
 */

/**
 * @addtogroup DrvWakeSch
 * @{
 */

/**
 * @file drv_wake_sch.h Schedule Wake from Hibernate
 */

#ifndef DRV_WAKE_SCH_H
#define DRV_WAKE_SCH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_machine.h"                /* machine definitions */
#include "drv_ipm.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#if defined (TARGET_DXP9140)
#define DRV_WAKE_SCH_TOLERATE_LATE_WAKE
#endif

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  enumeration of max sleep time IDs
 */
typedef enum
{
    DRV_WAKESCH_MAX_SLEEP_TIME_ID_AT=0,
    DRV_WAKESCH_MAX_SLEEP_TIME_ID_CAL32K,
    DRV_WAKESCH_MAX_SLEEP_TIME_NUM_IDS,
} drv_WakeSchMaxSleepTimeId;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialise the Wake scheduler
 *
 * @return none
 */
extern void drv_WakeSchInit(void);

/**
 * Set maximum sleep time
 * @param max_sleep_time Max sleep time in ms
 * @param id ID to set max sleep time of
 * @return none
 */
extern void drv_WakeSchSetMaxSleepTime(drv_WakeSchMaxSleepTimeId id, int max_sleep_time);

/*
 * Return date of earliest scheduled activity
*/
drv_IpmTimestamp drv_WakeSchGetDateOfEarliestSchedAct(void);

/*
 * Determine whether the specified duration (expressed in
 * CET ticks) is long enough to safely get in/out of hibernate
 * @param cet_ticks Duration of sleep
 * @return true if hibernate is possible
*/
bool drv_WakeSchIsHibernatePossible(uint64 cet_ticks);

/**
 * On SHM platforms, wait until AP applies frequency floor.
 * On other platforms, this function will return immediately.
 */
void drv_WakeSchWaitEMC(void);

#endif /* #ifndef DRV_WAKE_SCH_H */

/** @} END OF FILE */

