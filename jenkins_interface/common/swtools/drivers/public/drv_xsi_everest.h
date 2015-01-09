/********************************************************************
 * mphal_usi_spi.h : SPI Protocol definitions for USI.
 *
 * Copyright (c) 2011 Icera Inc
 * 
 * 07/04/2011: ThomasF - originated
 *
 *  Everest microcode are dedicated SPI implementations.
 *
 *   They are hard wired for 32-bit word access, and there
 *  is one for CPOL=0/CPHA=0 and one for CPOL=1/CPHA=1.
 *
 *  They use the same clock divided control as the normal
 *  SPI and that's the only soft configuration that they
 *  use.
 * 
 ********************************************************************/

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

#ifndef DRV_XSI_EVEREST_H
#define DRV_XSI_EVEREST_H

/********************************************************************
  Exported constants/MACROs
 ********************************************************************/

/********************************************************************
 * Exported types
 ********************************************************************/


/* drv_XsiConfigEverest
*/
typedef struct {
  
  /* Clock divider. USI clock is divided by (clkdiv+1)*2.
     Values less than 7 are unlikely to give desired clock
     rate and will jitter.
  */
  unsigned short clkDiv;

  /* From EV4.7c, it is possible to return all RX_DATA on logical channel 0,
     instead of the transmitting channel.
  */
  unsigned short returnRxDataToLogicalChannel0;
   
} drv_XsiConfigEverest;

/********************************************************************
 * Exported functions
 ********************************************************************/

#endif

