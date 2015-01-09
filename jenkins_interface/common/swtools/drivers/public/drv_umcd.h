/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_umcd.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup UMCDDriver UMCD Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup UMCDDriver
 * @{
 */

/**
 * @file drv_umcd.h DRAM controller public interface
 *
 */

#ifndef DRV_UMCD_H
#define DRV_UMCD_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#ifndef HOST_TESTING
#include "livanto_memmap.h"
#endif
#include "drv_hwplat.h"

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
 * drv_UmcdDramInitStart
 *
 * Initialise and start the DRAM controller. 
 * During cold boot (from secondary boot or equivalent), this will bring-up DRAM and
 * enable access to it.
 * No access to DRAM should be attempted prior to drv_UmcdDramInitStart.
 * For UMCD, this function will not be called during the warm boot process.
 * Called from DXP0.
 * 
 * @return The uncached start address of DRAM
 */
extern uint32 drv_UmcdDramInitStart(unsigned int warmBootNotColdBoot);

/**
 * drv_UmcdApplicationInit
 *
 * This function is called from both DXP0 & DXP1 during early application init.
 * Used to perform any required setup / initialisation.
 * NOTE: Any action taken here must be safe to do whilst running from external RAM.
 */
extern void drv_UmcdApplicationInit(void);

/**
 * drv_UmcdPowerDown
 *
 * Called when preparing for hibernate from drv_system's IPM handler.
 * Used to save any required state in-case a hibernate actually occurs.
 */
extern void drv_UmcdPowerDown(void);

/**
 * drv_UmcdPowerUp
 *
 * Post hibernate (system actually hibernated), this function is called to allow for any post
 * warm boot actions to be performed.
 * NOTE: Any action taken here must be safe to do whilst running from external RAM.
 */
extern void drv_UmcdPowerUp(void);

#endif

/** @} END OF FILE */

