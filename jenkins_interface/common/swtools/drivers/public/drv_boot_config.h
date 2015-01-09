/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_boot_config.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup BootConfigDriver Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup BootConfigDriver
 * @{
 */

/**
 * @file drv_boot_config.h public interface
 *
 */

#ifndef DRV_BOOT_CONFIG_H
#define DRV_BOOT_CONFIG_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * the following function is used to store the mode in config boot file 
 *
 * @param mode the device starts in this mode at the next power up
 * @return bool, the file was correctly written in memory
*/
bool drv_BootConfigStoreFirmwareMode(char mode);

/**
 * the following function is used to delete the config boot file 
 *
 * @param void
 * @return void
*/
void drv_BootConfigDeleteFirmwareMode(void);

#endif /* #ifndef DRV_BOOT_CONFIG_H */

/** @} END OF FILE */
