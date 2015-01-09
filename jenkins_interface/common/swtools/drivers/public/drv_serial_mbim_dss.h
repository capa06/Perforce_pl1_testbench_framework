/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_mbim_dss.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/


/**
 * @defgroup HostCom Host Communication
 */

/**
 * @defgroup SerialDriver Serial Driver
 * @ingroup  HostCom
 */

/**
 * @addtogroup SerialDriver
 * @{
 */

/**
 * @file drv_serial.h Serial Driver API Functions definitions.
 */

#ifndef DRV_SERIAL_MBIM_DSS_H
#define DRV_SERIAL_MBIM_DSS_H

#if defined (__dxp__)
#include "dxpnk_types.h"
#endif
#include "icera_global.h"
#include <stdlib.h>
#include "iobuf.h"
#include "drv_usb_config.h"
#include "drv_serial.h"
#include "drv_usb_mbim_dss_api.h"

/** Number of MBIM DSS Instances */
#define DRV_SERIAL_MBIM_DSS_PORT_NB        DRV_SERIAL_PORT_NB

/******************************************************************************
 * Exported types
 ******************************************************************************/

/******************************************************************************
 * Serial USB Driver Interface
 ******************************************************************************/

void* mbim_dss_init( void* drv_ctx, dss_callbacks_t* cbs, const drv_dss_cbs_t* drv_cbs,uint32 type,int iface_index );

#endif /* #ifndef _DRV_SERIAL_MBIM_DSS_H_ */

/** @} END OF FILE */
