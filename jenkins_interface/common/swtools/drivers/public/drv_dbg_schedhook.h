/*************************************************************************************************
 * Copyright (c) 2013, NVIDIA CORPORATION.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dbg_schedhook.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DbgDriver Scheduler Hook
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup DbgDriver
 * @{
 */

/**
 * @file drv_dbg.h Debug interface.
 *
 */

#ifndef DRV_DBG_SCHEDHOOK_H
#define DRV_DBG_SCHEDHOOK_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public constant declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize the scheduler hook
 *
 * @param fmt
 */
extern void drv_DbgSchedHookInit(void);

#endif /* DRV_DBG_SCHEDHOOK_H */

/** @} END OF FILE */
