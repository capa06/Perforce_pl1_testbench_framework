/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_ahub.h#1 $
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

#ifndef DRV_XSI_AHUB_H
#define DRV_XSI_AHUB_H

/********************************************************************
  Exported constants/MACROs
 ********************************************************************/

/********************************************************************
 * Exported types
 ********************************************************************/

/** drv_XsiConfigAHUB
 
    AHUB configuration parameters
 
*/

typedef struct {

  unsigned int numChannels; /* (1, 2, 4, 6, 8) */ 
  unsigned int bitsPerChannel;  /* (8, 16, 20, 24, 32) */

} drv_XsiConfigAHUB;

/********************************************************************
 * Exported functions
 ********************************************************************/
#endif
