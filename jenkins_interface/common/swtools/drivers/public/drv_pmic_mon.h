/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_pmic_mon.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup PmicDriver
 * @{
 */

/**
 * @file drv_pmic_mon.c Power measurement IC interface
 *
 */

#ifndef DRV_PMIC_MON_H
#define DRV_PMIC_MON_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

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
 * Initialise current / voltage measurement companion ICs
 *
 * @return          0 if success, non-zero if error
 */
int drv_pmic_mon_init(void);

/**
 * Read bus voltage measurement from power measurement device.
 *
 * @param device    Device number (0-x)
 * @return          16-bit voltage in mV
 */
uint16 drv_pmic_mon_read_voltage(int device);

/**
 * Read shunt voltage measurement from power measurement device.
 *
 * @param device    Device number (0-x)
 * @return          16-bit voltage in mV
 */
uint16 drv_pmic_mon_read_shunt_voltage(int device);

/**
 * Read current measurement from power measurement device.
 *
 * @param device    Device number (0-x)
 * @return          Signed 32-bit current in uA
 */
int32 drv_pmic_mon_read_current(int device);

/**
 * Generate status text for AT command containing a single 
 * voltage and current measurement.
 *
 * @param device    Device number (0-x)
 * @param msg       Target for text storage
 * @param max_len   Max string length
 * @return          0 if success, non-zero if error
 */
int drv_pmic_mon_get_status(int device, char *msg, int max_len);

/**
 * Generate status text for AT command containing all measured
 * voltages and currents.
 *
 * @param msg       Target for text storage
 * @param max_len   Max string length
 * @param machine_readable Machine readable format (do not alter!)
 * @return          0 if success, non-zero if error
 */
int drv_pmic_mon_get_status_all(char *msg, int max_len, int machine_readable);


#endif /* DRV_PMIC_MON_H */

/** @} END OF FILE */

