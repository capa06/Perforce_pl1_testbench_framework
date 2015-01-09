/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_rffe.h#1 $
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

#ifndef DRV_XSI_RFFE_H
#define DRV_XSI_RFFE_H


/********************************************************************
 * Exported types
 ********************************************************************/

/********************************************************************
 * Exported types
 ********************************************************************/

/* drv_XsiConfigRFFE
 
    RFFE protocol configuration parameters
    These configuration parameters are passed to the SIP
    microcode when setting up the instruction connection.
 
*/
typedef struct {

  /* Full speed clock divide value
   USI clock is divided by (clkdiv + 1) * 2.
     USI clock is divided by (clkdiv + 1) * 2.
     Values less than 7 are unlikely to give desired clock
     rate and will jitter.
  */
  unsigned short clkDiv;

} drv_XsiConfigRFFE;


/********************************************************************
 * Exported functions
 ********************************************************************/

#endif

