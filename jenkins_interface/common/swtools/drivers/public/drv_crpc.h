/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_crpc.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup CrpcDriver CRPC Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup CrpcDriver
 * @{
 */

/**
 * @file drv_crpc.h CRPC interface to provide constants and functions for
 *       Clock Reset and Power Control
 *
 */

#ifndef DRV_CRPC_H
#define DRV_CRPC_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

#if defined (ICE9XXX_PMSS)
#include "drv_crpc_9xxx.h"
#endif


#endif /* #ifndef DRV_CRPC_H */

/** @} END OF FILE */
