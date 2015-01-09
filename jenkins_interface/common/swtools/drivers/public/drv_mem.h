/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_mem.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup MemDriver Internal Memory Driver
 *  
 * Backup and restore memory regions after hibernate. 
 */

/**
 * @addtogroup MemDriver 
 * @{
 */

/**
 * @file drv_mem.h 
 */

#ifndef DRV_MEM_H
#define DRV_MEM_H

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
 * Public Function Definitions
 ************************************************************************************************/

/**
 *  Initialise internal memory driver (DMEM, GMEM, IMEM).
 *  All DXPs should call this.
 */
void drv_MemInit(void);

/**
 *  Perform pre-hibernate backup of internal memory that would be lost during hibernate.
 *  All DXPs should call this.
 */
void drv_MemSave(void);

/**
 *  Perform post-hibernate restore of internal memory that was lost during power-down.
 *  This should only be called if power loss actually occurred.
 *  All DXPs should call this.
 */
void drv_MemRestore(void);

/**
 *  Multi-core and thread safe wrapper for mphal_SetupLeakageState, which sets the requested bits
 *  in the leakage control registers.  drv_MemInit must have been called on DXP#0 before calling
 *  this function
 */
void drv_MemSetLeakageState(unsigned int leakage_mask_dxp_gmem,
                            unsigned int leakage_mask_soc);

/**
 *  Multi-core and thread safe wrapper for mphal_SetupLeakageState, which clears the requested bits
 *  in the leakage control registers.  drv_MemInit must have been called on DXP#0 before calling
 *  this function
 */
void drv_MemClearLeakageState(unsigned int leakage_mask_dxp_gmem,
                              unsigned int leakage_mask_soc);
#endif /* DRV_MEM_H */
/** @} END OF FILE */

