/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dram.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DRAMDriver DRAM Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup DRAMDriver
 * @{
 */

/**
 * @file drv_dram.h DRAM controller public interface
 *
 */

#ifndef DRV_DRAM_H
#define DRV_DRAM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_umcd.h"

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
 * drv_DramInitStart
 *
 * Initialise and start the DRAM controller. 
 * During cold boot (from secondary boot or equivalent), this will bring-up DRAM and
 * enable access to it.
 * No access to DRAM should be attempted prior to drv_DramInitStart.
 * Called from DXP0.
 * During warm boot, this function may restore the DRAM configuration depending on
 * the underlying memory controller.
 *
 * @return The uncached start address of DRAM
 */
extern uint32 drv_DramInitStart(unsigned int warmBootNotColdBoot);

/**
 * drv_DramApplicationInit
 *
 * This function is called from both DXP0 & DXP1 during early application init.
 * Used to perform any required setup / initialisation.
 * NOTE: Any action taken here must be safe to do whilst running from external RAM.
 */
extern void drv_DramApplicationInit(void);

/**
 * drv_DramPowerDown
 *
 * Called when preparing for hibernate from drv_system's IPM handler.
 * Used to save any required state in-case a hibernate actually occurs.
 */
extern void drv_DramPowerDown(void);

/**
 * drv_DramPowerUp
 *
 * Post hibernate (system actually hibernated), this function is called to allow for any post
 * warm boot actions to be performed.
 * NOTE: Any action taken here must be safe to do whilst running from external RAM.
 */
extern void drv_DramPowerUp(void);

/**
 * drv_DramGetExtraUnusedRamSize
 *
 * @return The size of the extra RAM (if any) in the current configuration 
 * @note extra ram must be used with extreme care for a few specific purpose 
 * (when RAM space is a crucial and rare resource like in in firmware download). 
 *  Use at your own risk.  
 */
extern uint32 drv_DramGetExtraUnusedRamSize(void);

/**
 * drv_DramGetRamStartAddr
 *
 * @return The RAM start address
 */
extern uint32 drv_DramGetRamStartAddr(void);

/**
 * drv_DramGetRamEndAddr
 *
 * @return The RAM end address
 */
extern uint32 drv_DramGetRamEndAddr(void);

/**
 * drv_DramGetRamSize
 *
 * @return The RAM size
 */
extern uint32 drv_DramGetRamSize(void);


#endif

/** @} END OF FILE */

