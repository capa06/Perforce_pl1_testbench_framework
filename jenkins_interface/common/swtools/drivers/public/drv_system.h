/*************************************************************************************************
 * Nvidia Inc
 * Copyright (c) 20011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_system.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup SystemDriver System Driver 
 *  
 * Backup and restore system parameters before and after power 
 * loss, i.e. DMEM, IMEM, clocks, PLL, DXP and SoC clock 
 * divisors and DMC timing configurations. 
 */

/**
 * @addtogroup SystemDriver 
 * @{
 */

/**
 * @file drv_system.h System-wide power management 
 *       initialisation and powerup/power down callbacks
 *  
 */

#ifndef DRV_SYSTEM_H
#define DRV_SYSTEM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "drv_ipm.h"
#include "drv_usb_phy.h"

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
 * Public Function Definitions
 ************************************************************************************************/

/**
 * System driver pre power down callback 
 *  
 * Called before power down to: 
 *  - save PLL & DMC context
 *  - configure RTB for power down
 *  
 * Can be used for any save/config not explicitaly done by other 
 * registered drivers. 
 *  
 * 
*/
drv_IpmReturnCode drv_SystemPreCb(drv_Handle driver_handle, drv_IpmPowerMode power_mode);

/**
 * System driver post power down callback 
 *  
 * Called after a warm boot to: 
 *  - check PLL & DMC settings well restored
 *  - re-init SDRAM
 *  - force re-map of overlay
 *  
 * Can be used for any restore/check not explicitaly done by 
 * other registered drivers. 
*/
drv_IpmReturnCode drv_SystemPostCb(drv_Handle driver_handle, bool power_lost);

/**
 * System driver init
 * 
 * This function is used by drivers to initialize system
 *
 * It registers post power down callback into Power Management 
 * framework. 
 *  
*/
void drv_SystemInit(void);

/** 
 * Prepare Power Down
 * 
 * This function is called to prepare a Power Down on DXP#0 - 
 * this releases the latency timings in the system PCU and 
 * programs RTB for wakeup 
 *  
 * @return none
 */ 
void drv_SystemPreparePowerDown(void);

/** 
 * One-time Init Hibernation
 * 
 * This function allows for doing a one-time,
 * initialisation-time hibernation
 *  
 * @return none
 */ 
void drv_SystemOneTimeInitHibernation(void);

/**
 * Save overlay restorable variables.
 *
 * This function saves the restorable overlay variables to a static off-chip area.
 * This is invoked automatically when hibernating, but must be called manually
 * for inter-RAT measurements before switching overlays.
 *
 * @return none
 */
void drv_SystemRestoreOverlayData(int overlay_id);

/**
 * Restore overlay restorable variables.
 *
 * This function restores overlay variables. It is invoked automatically on wakeup
 * but must be called manually following inter-RAT measurements after restoring the
 * current RAT's overlay.
 */
void drv_SystemSaveOverlayData(int overlay_id);


/* 
 * Initialisation of USB phy may be done by other DXP 
*/ 
void drv_SystemDiscoverUsbPhyType(usb_phy_select phy_sel);


#endif /* #ifndef DRV_SYSTEM_H */
/** @} END OF FILE */

