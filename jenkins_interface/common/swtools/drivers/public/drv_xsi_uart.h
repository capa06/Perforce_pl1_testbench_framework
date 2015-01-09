/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_uart.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup XsiDriver Generic FSI/USI Driver
 *
 * Generic XSI Driver built upon mphal_fsi on 80xx platforms and
 * mphal_usi on 90xx platforms @{ 
 */

/**
 * @file drv_xsi.h Generic FSI/USI driver 
 *
 */

#ifndef DRV_XSI_UART_H
#define DRV_XSI_UART_H

/********************************************************************
 * Exported types
 ********************************************************************/

/**
  @struct mphalusit_UARTChannelConfig
 
  @brief Channel-specific UART configuration parameters 

*/
typedef struct {

  unsigned char dataBits;     /* number of data bits per character */
  unsigned char stopBits;    /* number of stop bits */
  unsigned char parityEnable;  
  unsigned char parityType;   /* @see mphalusit_UARTParityType */
  unsigned char disableFlowControl;
  unsigned int baudRate;
} drv_XsiConfigUART;

#endif
