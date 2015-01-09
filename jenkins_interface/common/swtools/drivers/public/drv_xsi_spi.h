/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_spi.h#1 $
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

#ifndef DRV_XSI_SPI_H
#define DRV_XSI_SPI_H


/********************************************************************
 * Exported types
 ********************************************************************/

/**
 * SPI protocol configuration parameters
 */
typedef struct {

  unsigned char masterNotSlave;
    
  /** Polarity of slave selects (1 = active high).
  */
  drv_XsiCsPolarity   polarity;

  /** Most significant bit of the data in TX/RX Fifo
  */  
  unsigned int dataWidth;
  
  /** Clock polarity (CPOL)
  */
  drv_XsiClkPolarity clkPolarity;       
  
  /** Delay first bit clock edge by 1/2 cycle?  (CPHA)
  */
  drv_XsiClkPhase bitClockPhase;
  
  /** Selects bit ordering.
  */
  drv_XsiBitOrder bitOrder;
  
  /** Clock divider. USI clock is divided by (clkdiv + 1) * 2.
     Values less than 7 are unlikely to give desired clock
     rate and will jitter.

    FIXME: how to reconcile FSI and USI here ?????
  */
  unsigned int clkDiv;

  /** Data bit in which SSn is de-asserted.
     (0 means at the end of the transfer)
  */
  int sselDataBitForDeassert;

  /** Data bit in which MOMI is tri-stated/SISO is enabled
     (bidirectional only) 
  */
  int sdoDataBitForTristate;

  /** Delay (in bit times) between SSEL assert and first clocked bit. */
  int addSetupTime;

  /** Delay (in bit times) between last clocked bit and SSEL deassert. */
  int addHoldTime;

   /* Programmable delay defining interval between one transmitted message and the next (various protocols) */
   int                     messageGap;
  
} drv_XsiConfigSPI;

/********************************************************************
 * Exported functions
 ********************************************************************/

#endif

/** @} END OF FILE */
