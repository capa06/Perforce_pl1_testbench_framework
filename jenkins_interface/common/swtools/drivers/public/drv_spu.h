/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_spu.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup SpuDriver
 * @{
 */

/**
 * @file drv_spu.h SPU
 *
 */

#ifndef DRV_SPU_H
#define DRV_SPU_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"                           /** Global Icera Header file */
#ifndef HOST_TESTING
#include "livanto_memmap.h"
#include "livanto_config.h"
#endif
#include "drv_gpio.h"
#include "drv_ipm.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define SPU_SLAVE_CET_DEBUG_NA (-1)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Types of spu slaves
 */
 /* 9xxx */

typedef enum
{
    SPU_SLAVE_GPIO,
    SPU_SLAVE_BBRF,
    SPU_SLAVE_HRL,
    SPU_SLAVE_USI,
    SPU_SLAVE_AMB,
    SPU_SLAVE_DMA
} drv_SpuSlaveType;

typedef struct
{
    int              usi_id;
    int              usi_idx;
} s_drv_SpuSlaveDataUsi;

typedef struct
{
    int              umcd_not_spd;
} s_drv_SpuSlaveDataAmb;

typedef struct
{
    int              fdma_not_sdma;
} s_drv_SpuSlaveDataDma;

typedef struct
{
    eDrvGpioId       gpio_id;
    int              gpio_idx;
}s_drv_SpuSlaveDataGpio;

typedef struct
{
    int              bbrf_tas;
}s_drv_SpuSlaveDataBbRf;

typedef struct
{
    int              hrl_queue;
}s_drv_SpuSlaveDataHrl;

/**
 * Data associated with an SPU_SLAVE type
 * @see s_drv_SpuSlaveData
 */

/* 9xxx */

typedef union
{
    s_drv_SpuSlaveDataHrl   hrl;
    s_drv_SpuSlaveDataBbRf  bbrf;
    s_drv_SpuSlaveDataDma   dma;
    s_drv_SpuSlaveDataGpio  gpio;
    s_drv_SpuSlaveDataUsi   usi;
    s_drv_SpuSlaveDataAmb   amb;
} s_drv_SpuSlaveData;


/**
 * Structure to contain the fsi info for a give spu slave
 * Non-FSI spu slaves have no data associated with the transfer
 * @see s_drv_RfThresholds
 */
typedef struct s_drv_SpuSlaveInfo
{
    drv_SpuSlaveType     type;
    s_drv_SpuSlaveData   data;
} s_drv_SpuSlaveInfo;

/* values that can be written into the ctrl_slave registers */
/* these values can be combined with binary OR to trig a slave from several masters */
typedef enum
{
  SPU_MASTER_CET_THR0 = 0,
  SPU_MASTER_CET_THR1,
  SPU_MASTER_CET_THR2,
  SPU_MASTER_CET_THR3,
  SPU_MASTER_CET_THR4,
  SPU_MASTER_CET_THR5,
  SPU_MASTER_CET_THR6,
  SPU_MASTER_CET_THR7,
  SPU_MASTER_CET_THR8,
  SPU_MASTER_CET_THR9,
  SPU_MASTER_CET_THR10,
  SPU_MASTER_CET_THR11,
  SPU_MASTER_CET_THR12,
  SPU_MASTER_CET_THR13,
  SPU_MASTER_CET_THR14,
  SPU_MASTER_CET_THR15,
  SPU_MASTER_CET_THR16,
  SPU_MASTER_CET_THR17,
  SPU_MASTER_CET_THR18,
  SPU_MASTER_CET_THR19,
  SPU_MASTER_GPT_THR0,
  SPU_MASTER_GPT_THR1,
  SPU_MASTER_GPT_THR2,
  SPU_MASTER_GPT_THR3,
  SPU_MASTER_GPT_THR4,
  SPU_MASTER_GPT_THR5,
  SPU_MASTER_GPT_THR6,
  SPU_MASTER_GPT_THR7,
  SPU_MASTER_ALL
} drv_SpuMaster;


/* CTRL_SLAVE: routing from the SIC masters to the SIC slaves */

 /* 9xxx */

typedef enum
{
    SPU_SLAVE_HRL0 = 0,
    SPU_SLAVE_HRL1,
    SPU_SLAVE_BBRF0,
    SPU_SLAVE_BBRF1,
    SPU_SLAVE_SDMA,
    SPU_SLAVE_FDMA,
    SPU_SLAVE_GPIO_0,
    SPU_SLAVE_GPIO_1,
    SPU_SLAVE_GPIO_2,
    SPU_SLAVE_GPIO_3,
    SPU_SLAVE_GPIO_4,
    SPU_SLAVE_GPIO_5,
    SPU_SLAVE_GPIO_6,
    SPU_SLAVE_GPIO_7,
    SPU_SLAVE_GPIO_8,
    SPU_SLAVE_GPIO_9,
    SPU_SLAVE_GPIO_10,
    SPU_SLAVE_GPIO_11,
    SPU_SLAVE_GPIO_12,
    SPU_SLAVE_GPIO_13,
    SPU_SLAVE_GPIO_14,
    SPU_SLAVE_GPIO_15,
    SPU_SLAVE_USI0_0,
    SPU_SLAVE_USI0_1,
    SPU_SLAVE_USI0_2,
    SPU_SLAVE_USI0_3,
    SPU_SLAVE_USI0_4,
    SPU_SLAVE_USI0_5,
    SPU_SLAVE_USI0_6,
    SPU_SLAVE_USI0_7,
    SPU_SLAVE_USI0_8,
    SPU_SLAVE_USI0_9,
    SPU_SLAVE_USI0_10,
    SPU_SLAVE_USI0_11,
    SPU_SLAVE_SPD,
    SPU_SLAVE_PL1_UNUSED_0,
    SPU_SLAVE_PL1_UNUSED_1,
    SPU_SLAVE_PL1_UNUSED_2,
    SPU_SLAVE_USI1_0,
    SPU_SLAVE_USI1_1,
    SPU_SLAVE_USI1_2,
    SPU_SLAVE_USI1_3,
    SPU_SLAVE_USI1_4,
    SPU_SLAVE_USI1_5,
    SPU_SLAVE_USI1_6,
    SPU_SLAVE_USI1_7,
    SPU_SLAVE_USI1_8,
    SPU_SLAVE_USI1_9,
    SPU_SLAVE_USI1_10,
    SPU_SLAVE_USI1_11,
    SPU_SLAVE_UMCD,
    SPU_SLAVE_VIV_UNUSED_0,
    SPU_SLAVE_VIV_UNUSED_1,
    SPU_SLAVE_VIV_UNUSED_2,
    SPU_SLAVE_ALL
} drv_SpuSlave;


/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern uint32             shadow_spu_slaves[SPU_SLAVE_ALL];
extern s_drv_SpuSlaveInfo drv_SpuSlaveInfos[SPU_SLAVE_ALL];

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Add a route for SIC events
 *
 * Routing a SIC event by connecting a SIC master connection (CET and GPT threshold events)
 * to a SIC slave connection (CGSM, C3G and Audio FSI, IPP and GPIO0).
 *
 * @param spu_master Master connection. (c.f. enum type definition).
 * @param spu_slave Slave connection
 *
 * @return Slave connection. (c.f. enum type definition).
 */
extern void drv_SpuRouteAdd(drv_SpuMaster spu_master, drv_SpuSlave spu_slave);

/**
 * Removing a route for SIC events.
 *
 * Removing a route for a SIC event. It is possible to specify that all routes from a master are
 * disconnected. It is also possible to specify that all routes to a slave are disconnected.
 * Specifying to remove the routes from all masters to all slaves effectively clears the crossbar.
 *
 * @param spu_master Master connection or all masters. (c.f. enum type definition).
 * @param spu_slave Slave connection or all slaves. (c.f. enum type definition).
 *
 * @return void
 */
extern void drv_SpuRouteRemove(drv_SpuMaster spu_master, drv_SpuSlave spu_slave);

/**
 * Returns the Spu Slave Cet debug value.
 *
 * @return The value if CET debug mode enabled, otherwise SPU_SLAVE_CET_DEBUG_NA
 */
extern int8 drv_SpuGetSlaveCetDebug();

/**
 * Returns the address of the target data fifo as a function of the spu slave enum
 *
 * This function return the address of the target data fifo for the supplied spu slave
 * enum
 *
 * @param spu_slave SPU slave as an enum
 * @return uint32 data fifo address
 */
static inline DXP_FORCEINLINE s_drv_SpuSlaveInfo *drv_SpuSlaveInfo(drv_SpuSlave spu_slave)
{
    return &(drv_SpuSlaveInfos[spu_slave]);
}

/**
 * Returns pointer to the name of a SPU slave (for debug/crash logging functions)
 */
extern const char * drv_SpuGetSlaveName(drv_SpuSlave spu_slave);

extern drv_IpmReturnCode drv_SpuIPMPre(drv_Handle driver_handle, drv_IpmPowerMode power_mode);
extern drv_IpmReturnCode drv_SpuIPMPost(drv_Handle driver_handle, bool power_removed);


#endif /* DRV_SPU_H */

/** @} END OF FILE */
