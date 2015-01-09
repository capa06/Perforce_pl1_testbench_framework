/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_mphal_nand.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup NandFlashDriver Nand Flash Driver
 *
 * @{
 */

/**
 * @file drv_mphal_nand.h Extensions to NAND MPHAL
 *
 * Extension of the NAND MPHAL source code.
 * The aim is to provide missing functionality for NAND access until such time that mphal_nand
 * supports it, once mphal_nand does, this file will be removed!
 */


#ifndef DRV_MPHAL_NAND_H
#define DRV_MPHAL_NAND_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"

/* TODO: TARGET_DXP9140 - Temp hack to allow RAM filesystem builds */
#if defined (TARGET_DXP9140)
  #define MPHAL_HW_NAND_PREFIX(name) mphalumco_##name
#endif

#include "mphal_nand.h"

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

/** drv_mphalnand_PageRead
 *    Temporary extension to mphal_nand to support API required by filesystem usage.
 *    Extension allows data & tags/spares sections to be sourced from destinct buffers.
 *
 *    @param data      optional data section pointer
 *    @param dataLen   optional data section length (can be 0)
 *    @param tags      optional data section pointer
 *    @param tagLen    optional data section length (can be 0)
 *    @return int      result as per mphalnand_PageRead
 *
 *    See mphalnand_PageRead for further details.
 **/
int drv_mphalnand_PageRead(mphalnandt_Handle *nH, int pageId, 
                           uint8 *data, int dataLen, 
                           uint8 *tags, int tagLen, 
                           mphalnandt_ECCKind eccKind, mphalnandt_ECCStatus *eccStatus);

/** drv_mphalnand_PageProgram
 *    Temporary extension to mphal_nand to support API required by filesystem usage.
 *    Extension allows data & tags/spares sections to be sourced from destinct buffers.
 *
 *    @param data      optional data section pointer
 *    @param dataLen   optional data section length (can be 0)
 *    @param tags      optional data section pointer
 *    @param tagLen    optional data section length (can be 0)
 *    @return int      result as per mphalnand_PageRead
 *
 *    See mphalnand_PageProgram for further details.
 */
int drv_mphalnand_PageProgram(mphalnandt_Handle *nH, int pageId, 
                            uint8 *data, int dataLen, 
                            uint8 *tags, int tagLen, 
                            mphalnandt_ECCKind eccKind);

/** drv_mphalnand_BlockEraseIgnoringBadBlockState
 *  As per mphalnand_BlockErase but ignoring bad block status.
 */
int drv_mphalnand_BlockEraseIgnoringBadBlockState(mphalnandt_Handle *nH, int blockId);

/** drv_mphalnand_PageReadWhichAllowsBadBlockToBeRead
 *  As per drv_mphalnand_PageRead but ignoring bad block status.
 */
int drv_mphalnand_PageReadWhichAllowsBadBlockToBeRead(mphalnandt_Handle *nH, 
                                                      int pageId, 
                                                      uint8 *data, int dataLen, 
                                                      uint8 *tags, int tagLen, 
                                                      mphalnandt_ECCKind eccKind);

#endif

/** @} END OF FILE */
