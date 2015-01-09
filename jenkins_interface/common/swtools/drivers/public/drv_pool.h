/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_pool.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/


/**
 * @addtogroup TopUtil
 * @{
 */


/**
 * @file drv_pool.h Defines the drv_Pool type and methods for managing a pool of
 *       resources
 *
 */

#ifndef DRV_POOL_H
#define DRV_POOL_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "os_swfifo.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <stdlib.h>

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Resource pool element
 */
typedef struct
{
    os_SwFifo fifo;
    uint32 max_addrs;
    uint32 min_addrs;

} drv_Pool;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern void drv_PoolInit(drv_Pool *pool, void **addrs_buffer, void *elements, int num_elements, size_t element_size);
extern void *drv_PoolRead(drv_Pool *pool);
extern bool drv_PoolWrite(drv_Pool *pool, void *addrs);
static inline bool drv_PoolFull(drv_Pool *pool)
{
    return os_SwFifoFull(&pool->fifo);
}

#endif

/** @} END OF FILE */

