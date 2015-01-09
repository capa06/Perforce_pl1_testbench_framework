/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_uart.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup SerialDriver
 * @{
 */

/**
 * @file drv_serial_uart.h Serial Uart Driver API Functions definitions.
 */

#ifndef DRV_SERIAL_UART_H
#define DRV_SERIAL_UART_H

#include "drv_serial.h"

/******************************************************************************
 * Exported Variables
 ******************************************************************************/

extern DXP_CACHED_UNI1 drv_serial_ops_t drv_serial_uart_ops;

/**
 * Hook Diag and/or AT port to the uart connector. 
 *
 */
void drv_SerialUartGetHook(drv_serial_index_e* logging, drv_serial_index_e* at);

#endif /* #ifndef _DRV_SERIAL_UART_H_ */

/** @} END OF FILE */
