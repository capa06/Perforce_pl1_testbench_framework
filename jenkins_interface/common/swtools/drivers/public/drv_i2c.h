/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_i2c.h#1 $
 * $Date: 2014/11/13 $
 * $Revision: #1 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup I2CDriver I2C Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup I2CDriver
 * @{
 */

/**
 * @file drv_i2c.h I2C Driver interface
 *
 * This is the I2C Driver interface designed to provide a set of
 * I2C primitives so as to interact with I2C devices. The I2C
 * driver assumes a Master only role.
 *
 */

/* Comment removed from doxygen comment above: see rtl/856 gnat */

#ifndef DRV_I2C_H
#define DRV_I2C_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/**
 * The I2C_DEV_ADDR_10_BITS tells the format of the aimed device address.
 * Depending on this bit, the mask that is applied on the device address is either 10 bits
 * (if 1) or 7 bits (if 0). All upper bits of the address are masked out.
 *   10 bit device address: 1xxxxxxxxxxxxxxxxxxxxxaaaaaaaaaa
 *
 *    7 bit device address: 0xxxxxxxxxxxxxxxxxxxxxxxxaaaaaaa
 */
#define I2C_DEV_ADDR_10_BITS BIT(31)

/** Return codes */
#define I2C_MORE_DATA           (1)
#define I2C_OK                  (0)
#define I2C_NOK                 (-1)
#define I2C_ALLOC_FAIL          (-1)
#define I2C_Q_PUT_FAIL          (-2)
#define I2C_NO_EVENT_ERR        (-3)
#define I2C_NO_ACK              (-4)

/** Keep old names for compatibility */
#define ST_I2C_MORE_DATA        I2C_MORE_DATA
#define ST_I2C_OK               I2C_OK
#define ST_I2C_NOK              I2C_NOK
#define ST_I2C_ALLOC_FAIL       I2C_ALLOC_FAIL
#define ST_I2C_Q_PUT_FAIL       I2C_Q_PUT_FAIL
#define ST_I2C_NO_EVENT_ERR     I2C_NO_EVENT_ERR
#define ST_I2C_NO_ACK           I2C_NO_ACK


/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

typedef enum
{
    I2C_MSG_WRITE_REQ,
    I2C_MSG_READ_REQ,
    I2C_MSG_VANILLA_READ_REQ
} eDrvI2CReq;

/**
 *  Who owns the memory for tDrvI2CMsg & tDrvI2CMsg.user_data?
 */
typedef enum
{
    I2C_CALLER_OWNED_MEM,   /** Caller of drv_i2c_send_request frees memory */
    I2C_DRIVER_OWNED_MEM    /** I2C driver frees memory */
} eDrvI2CMemOwner;

/**
 * tResp_cb is the callback function pointer to be passed by an I2C user that wishes to be called on
 * request completion.
 *
 * This Callback is dependant upon the synchronisation that the user thread has chosen.
 * It can be for instance a function that releases a Semaphore that the User thread has taken.
 *
 * ctx: Its first argument is the context to recall, for instance a semaphore Handle
 * status : if 0 request was executed ok, otherwise an error  has occured
 * resp_msg: tDrvI2CMsg pointer on response: contains the received message for an I2C READ order.
 */
typedef void (*tResp_cb)(void *ctx, int status,  void * resp_msg);

/**
 * Structure produced by user thread. Used in drv_i2c_send_request
 *
 */
typedef struct
{
    uint32 msg_type;     /** among eDrvI2CReq */
    tResp_cb cb;         /** User thread callback to be invoked post trasaction  */
    void * cb_ctx;       /** User thread context parameter to bc callback (e.g.the handle on a semaphore to release) */
    int32 lg;            /** Length of the transaction in bytes including data[1] */
    uint32 device_addr;  /** the I2C device address */
    uint16 id;           /** device identifier (internal use only) */
    uint16 header;       /** I2C 7-bit or 10-bit header (internal use only) */
    eDrvI2CMemOwner mem_owner; /* Who owns the memory for tDrvI2CMsg & tDrvI2CMsg.user_data? */
    uint8 *user_data;    /** User provided alternative data buffer */    
    uint8 data[1];       /** first byte of data (should contain a i2c device register address) */
} tDrvI2CMsg;

/** Public handle to the i2c driver */
typedef void i2cdrvt_Handle;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/


/**
 * Initialize the I2C driver
 *
 * @note This call creates a DEV thread as well as its EXPYIELD companion thread if the ISR bit is set
 * it unregisters the interrupt if it is changes from true to false.
 *
 * @param isr   : set to true to use the driver with interrupts, set to false if polling method chosen
 * @param i2c_bus_clk :  up to 400hHz
 * @param i2c_spike_filter : 1 to  15
 * @param i2c_scl_delay:
 *
 * @return I2C driver handle if successful, NULL otherwise
 */
extern i2cdrvt_Handle* drv_i2c_start(bool isr, uint32 i2c_bus_clk, uint32 i2c_spike_filter, uint32 i2c_scl_delay);


/**
 * Send out an I2C request to the I2C thread
 *
 * @note This call blocks indefinitely until an element is available.
 * @param i2c_req_buf   A pointer on a tDrvI2CMsg buffer built by the user thread
 *                      The actual tDrvI2CMag is usually larger than sizeof(tDrvI2CMsg)
 * @param i2c_prim      I2C_MSG_WRITE_REQ / I2C_MSG_READ_REQ
 * @param user_data:    [Optional] User provided alternative data buffer (can be NULL).
                        If NULL, i2c_prim.data[0] should be used with extra data being
                        contiguous to the end of 'i2c_prim'.
 * @param i2c_mem_o..p: Are 'i2c_prim' & 'user_data' caller owned / freed memory (I2C_CALLER_OWNED_MEM) or
 *                      should the I2C driver free the memory on completion (I2C_DRIVER_OWNED_MEM).
 * @param origCB_ctx:   pointer on context of the originator of the request
 * @param origCB_ack:   callback to be called to notify user thread of completion of request
 *                      This callback is called in the context of the I2C Thread
 * @return 0 if successful, -1: if allocation failed, -2 if put to I2C Thread queue failed
 */
int drv_i2c_send_request(tDrvI2CMsg*      i2c_req_buf, 
                         eDrvI2CReq       i2c_prim,
                         eDrvI2CMemOwner  i2c_mem_ownership,
                         uint8 *          user_data,
                         void *           origCB_ctx, 
                         tResp_cb         origCB_ack);

/**
 * I2C driver write by polling
 *
 * @note This routine polls status until completion of the I2C write order
 * @param i2c_dev_addr   : I2C slave device address
 * @param reg_addr :
 * @param reg_val :
 *
 * @return none
 */
extern void drv_i2c_RegPollWrite(uint32  i2c_dev_addr, uint8 reg_addr, uint8 reg_val);


#endif

/** @} END OF FILE */

