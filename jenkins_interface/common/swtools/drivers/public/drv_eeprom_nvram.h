/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_eeprom_nvram.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup EepromDriver
 * @{
 */

/**
 * @file drv_eeprom_nvram.h EEPROM NVRAM (calibration file storage)
 *
 */

#ifndef DRV_EEPROM_NVRAM_H
#define DRV_EEPROM_NVRAM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "os_abs.h"

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
 * Initialise EEPROM NVRAM storage driver.
 *
 * If a calibration file is present in EEPROM which does not match that of the file-system,
 * the EEPROM version will replace the copy on the fs.
 * If no cal file is present in the EEPROM, but present on the FS, it will be copied FS->EEPROM.
 */
void drv_eeprom_nvram_init(void);

/**
 * Store calibration data from file-system on the EEPROM.
 * This would be done post-calibration.
 */
void drv_eeprom_nvram_sync_from_fs(void);

/**
 * Erase data stored in EEPROM.
 */
void drv_eeprom_nvram_erase(void);

#endif /* DRV_EEPROM_NVRAM_H */

/** @} END OF FILE */

