/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_avs_monitor.h#1 $
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
 * @file drv_avs_monitor.h AVS monitor public interface
 *
 */

#ifndef DRV_AVS_MONITOR_H
#define DRV_AVS_MONITOR_H

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

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize AVS monitor
 *
 * @return void.
 */
extern void drv_MonAvsInit(void);

/**
 * Request to perform AVS monitor measurement(s).
 *
 * @param window_us: Window length over which AVS count will be collected.
 * @param window_us: If !=0 AVS monitor will retrigger the measurement indefinitely.
 * @return: 0 if all OK, !=0 if something went wrong
 */
extern uint32 drv_MonAvsStart(uint32 window_us, uint32 auto_repeat);

#endif /* DRV_AVS_MONITOR_H */

/** @} END OF FILE */
