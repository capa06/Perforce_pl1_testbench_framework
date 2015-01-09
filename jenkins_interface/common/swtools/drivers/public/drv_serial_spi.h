/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_spi.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup Driver
 *
 *
 * @{
 */

/**
 * @file drv_serial_spi.h public interface for SPI serial driver
 *
 */

#ifndef DRV_SERIAL_SPI_H
/**
 * A description of TEMPLATE_H, used to protect against recursive inclusion.
 */
#define DRV_SERIAL_SPI_H

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include "dxpnk_types.h"
#include "icera_global.h"
#include "drv_xsi.h"
#include "drv_serial.h"

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef struct
{
    drv_XsiDeviceId fsiInstance;
    drv_XsiChipSelectId chipSelect;
    int master;
    int bitOrder;
    int csPol;
    int clkSpeed;
    int clkPol;
    int clkPhase;
} drv_SpiConf;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern void drv_SpiSerialInitialize(drv_SpiConf *conf, uint32 index);

extern void *drv_SpiSerialOpen( uint32 index );

extern drv_serial_error_e drv_SpiSerialClose( drv_serial_handle_t handle );

extern drv_serial_error_e drv_SpiSerialRead( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_read );

extern drv_serial_error_e drv_SpiSerialWrite( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_write );

extern drv_serial_error_e drv_SpiSerialControl( drv_serial_handle_t handle, drv_serial_control_ops_e op, uint32 data );

#endif /* #ifndef DRV_SERIAL_SPI_H */

/** @} END OF FILE */
