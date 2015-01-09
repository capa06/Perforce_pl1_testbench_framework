/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_i2c.h#1 $
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

#ifndef DRV_XSI_I2C_H
#define DRV_XSI_I2C_H


/********************************************************************
 * Exported types
 ********************************************************************/

/**
 * I2C Header format (7 or 10 bit address field)
 */
enum {
    DRV_XSI_I2C_HEADER7 = 0,
    DRV_XSI_I2C_HEADER10,    
};


/**
 * I2C protocol configuration parameters
 */
typedef struct {

  /** SCL clock frequency = (USI clock) / clkDiv (values 0-199 are illegal).
     The SCL clock frequency must be compatible with "mode"  
      FIXME: how to reconcile FSI and USI here ?????
  */
    unsigned int clkDiv;

    /** SIP pins to be used for SCL and SDA.
     */
    unsigned char sclPinNumber;
    unsigned char sdaPinNumber;
    
} drv_XsiConfigI2C;

/********************************************************************
 * Exported functions
 ********************************************************************/

extern int drv_XsiBuildI2CFrame(char *buf, 
                                unsigned int address,
                                unsigned int length,
                                unsigned int link,
                                unsigned int format);

#endif

