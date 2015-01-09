/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_iqdump.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup SMCDriver
 * @{
 */

/**
 * @file drv_iqdump.c Driver configuring SMC for IQ dump
 *
 * This module is responsible for SMC configuration for IQ dump
 */

#ifndef DRV_IQDUMP_H
#define DRV_IQDUMP_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#define DRV_IQDUMP_CS_USED        (2) /** Which chip select is used for IQ dump? */

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
 * Configures XMC/SMC for IQ dump stream
 *
 * @return void *: Pointer to the memory area configured for IQ dump use
 */
extern void *drv_IQDumpConfigure(void);

/**
 * Convert from circular buffer to normal array.
 *
 */
extern void drv_IQDumpCopyCircToLinear(void *out_ptr, const circ_ptr_s *in_cptr_ptr, int n, int atomsize);

/**
 *  Dump samples to the IQDUMP device
 *
 *  @param  src_buffer  Circular buffer to be dumped
 *  @param  num_samples Number of samples to be dumped
 *  @param  atomsize    Size of each sample, in bytes
 *  @param  dest_ptr    Destination device pointer
 *
 */
extern void drv_IQDumpSamples(const circ_ptr_s * const src_buffer, int32 num_samples, int32 atomsize, void * dest_ptr);

#endif /* DRV_IQDUMP_H */
/** @} END OF FILE */
