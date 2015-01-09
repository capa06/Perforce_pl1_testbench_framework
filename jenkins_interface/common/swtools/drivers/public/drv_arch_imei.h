/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch_imei.h#1 $ 
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_imei.h Access to IMEI data
 *
 */

#ifndef DRV_ARCH_IMEI_H
#define DRV_ARCH_IMEI_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_arch_type.h"

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
 * Verify imei file data validity and store it if valid.
 *
 * If not valid then store default.
 * 
 * @param imei_ptr buffer where IMEI must be stored
 * @param default_imei_ptr buffer where default IMEI value is stored
 * @param default_imei_size sizeof of default IMEI value
 * 
 * @return IMEI_LENGTH if imei file data are valid, 0 if not valid.
 */
extern int drv_ArchGetImeiFromFile(char *const imei_ptr, const char *const default_imei_ptr, const int default_imei_size);

/** 
 * Write/Update an IMEI file on target. 
 *  
 * To ensure IMEI file can always be updated through download 
 * mechanism, file on target is generated with a valid Icera 
 * header so that it doesn't break any compatibility. 
 *  
 * This function is only successfull when IMEI file has either: 
 *  ARCH_NO_AUTH
 *  or
 *  ARCH_EXT_AUTH
 *  key_set attributes in arch_type table.
 *  
 * Concerning ARCH_EXT_AUTH, platform must be in 
 * EXT_AUTH_UNLOCKED state to allow write/update. 
 * 
 * @param imei_ptr IMEI data
 * @param imei_len IMEI_LENGTH mandatory for the moment (kept as
 *                 argument in case we want to implement Lhun
 *                 checksum mechanism
 * 
 * @return ArchError.
 */
extern ArchError drv_ArchSetImeiInFile(uint8 *imei_ptr, int imei_len);

/**
 * Check that there is a valid IMEI file, and that it contains a non-zero value
 *
 * @return Zero if invalid, One if valid
 */
extern int drv_arch_HaveValidImeiFile();

/**
 * Delete the IMEI file.
 *
 * @return Zero if successfull, -1 if failure
 */
extern int drv_arch_DeleteImeiFile();

#endif /* #ifndef DRV_ARCH_IMEI_H */

/** @} END OF FILE */

