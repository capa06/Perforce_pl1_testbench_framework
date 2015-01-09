/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_loopback.h#1 $
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

#ifndef DRV_XSI_LOOPBACK_H
#define DRV_XSI_LOOPBACK_H
/********************************************************************
  Exported constants/MACROs
 ********************************************************************/

/********************************************************************
 * Exported types
 ********************************************************************/

/** drv_XsiConfigLoopback
 
    LOOPBACK configuration parameters
 
*/

typedef struct {

    /* When true, the microcode will echo an inverted version of the data */
    unsigned char enableDataInversion;

} drv_XsiConfigLoopback;

/********************************************************************
 * Exported functions
 ********************************************************************/
#endif
