/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial.h#1 $
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

#ifndef DRV_SERIAL_H
#define DRV_SERIAL_H

#if defined (__dxp__)
#include "dxpnk_types.h"
#endif
#include "icera_global.h"
#include <stdlib.h>

/******************************************************************************
 * Exported types
 ******************************************************************************/
/** Serial Port index */
typedef enum {
    DRV_SERIAL_PORT_0 = 0,
    DRV_SERIAL_PORT_1,
    DRV_SERIAL_PORT_2,
    DRV_SERIAL_PORT_3,
    DRV_SERIAL_PORT_4,
    DRV_SERIAL_PORT_5,
    DRV_SERIAL_PORT_6,
    DRV_SERIAL_PORT_7,
    DRV_SERIAL_PORT_8,
    DRV_SERIAL_PORT_9,
    DRV_SERIAL_PORT_10,
    DRV_SERIAL_PORT_11,
    DRV_SERIAL_PORT_12,
    DRV_SERIAL_PORT_13,
    DRV_SERIAL_PORT_NB,
    DRV_SERIAL_PORT_INVALID,
} drv_serial_index_e;

/** Serial Port Error */
typedef enum {
    /** No Error */
    DRV_SERIAL_NO_ERROR = 0,
    /** Error while registering Serial Port */
    DRV_SERIAL_ERROR_REGISTERING = -1,
    /** Error while opening a Serial Port */
    DRV_SERIAL_ERROR_OPENING = -2,
    /** Error while closing a Serial Port */
    DRV_SERIAL_ERROR_CLOSING = -3,
    /** Control Operation Not Supported */
    DRV_SERIAL_ERROR_CONTROL = -4,
    /** OverRun Error Detected */
    DRV_SERIAL_ERROR_OVERRUN = -5,
    /** Parity Error Detected */
    DRV_SERIAL_ERROR_PARITY = -6,
    /** Framing Error Detected */
    DRV_SERIAL_ERROR_FRAMING = -7,
    /** Receive Error */
    DRV_SERIAL_ERROR_RECEIVE = -8,
    /** Transmit Error */
    DRV_SERIAL_ERROR_TRANSMIT = -9,
    /** Transmit Error Timeout*/
    DRV_SERIAL_ERROR_TRANSMIT_TIMEOUT = -10,
    /** Transmit path not empty */
    DRV_SERIAL_ERROR_TX_NOT_EMPTY = -11,
    /** Invalid Baudrate Value */
    DRV_SERIAL_ERROR_INVALID_BAUDRATE = -12,
    /** TX DMA is not ongoing */
    DRV_SERIAL_ERROR_TX_DMA_NOT_ONGOING = -13,
    /** TX/RX Mode wrong */
    DRV_SERIAL_ERROR_TX_RX_INVALID_MODE = -14,
    /** Error when reading data */
    DRV_SERIAL_ERROR_READING = -15,
    /** Error when writing data */
    DRV_SERIAL_ERROR_WRITING = -16,
    /** DMA Mode is not supported */
    DRV_SERIAL_ERROR_DMA_MODE_NOT_SUPPORTED = -17,
    /* Rx timeout in blocking mode */
    DRV_SERIAL_ERROR_RX_TIMEOUT = -18,
    /* serial is using multiple write buffers */
    DRV_SERIAL_BUFFER_FREE = -19,

} drv_serial_error_e;

/** Serial Port TX Mode */
typedef enum {
    /** Blocking Mode (function will return once the buffer has been transmitted) */
    DRV_SERIAL_TX_MODE_BLOCKING = 0,
    /** Posted Mode without local copy (buffer has to remain valid until callback received) */
    DRV_SERIAL_TX_MODE_POSTED_NOCOPY,
    /** Posted Mode with local copy (buffer can be reused after call to drv_serial_write) */
    DRV_SERIAL_TX_MODE_POSTED_COPY,
    /** End Enum */
    DRV_SERIAL_TX_MODE_END
} drv_serial_tx_mode_e;

/** Serial Port RX Mode */
typedef enum {
    /** Blocking Mode (function will return once the buffer has been received) */
    DRV_SERIAL_RX_MODE_BLOCKING = 0,
    /** Posted Mode (buffer has to remain valid until callback received) */
    DRV_SERIAL_RX_MODE_POSTED,
    /** End Enum */
    DRV_SERIAL_RX_MODE_END
} drv_serial_rx_mode_e;

/** Serial Port Status */
typedef enum {
    /** TBD */
    DRV_SERIAL_STATUS_NONE = 0,
    DRV_SERIAL_STATUS_ENABLED,
    DRV_SERIAL_STATUS_DISABLED,

} drv_serial_status_e;

typedef enum {
    DRV_SERIAL_NOTIFY_NONE = 0,
    DRV_SERIAL_NOTIFY_REGISTERED,
    DRV_SERIAL_NOTIFY_DISCONNECTED,

} drv_serial_notify_e;

struct drv_serial_ops_t;
typedef int (*drv_serial_notify_cb_t)( void * handle, drv_serial_notify_e reason,void*arg);

typedef struct
{
    drv_serial_notify_cb_t  cb;
    void*                   ctx;
} drv_serial_notify_t;

/** Serial Port Handle */
typedef struct {
    /** Serial Port index */
    drv_serial_index_e                  index;

    /** Operation for this Serial Port */
    struct drv_serial_ops_t *           ops;

    /** Internal Serial Port Handle */
    void *                              priv_handle;

    /** Internal Serial Port Index */
    uint32                              priv_index;

    /** named serial port*/
    char                                name[20];
    /** lazy registration*/
    uint32                              locked;
    drv_serial_notify_t                 notify;

} drv_serial_struct_t;
typedef drv_serial_struct_t * drv_serial_handle_t;


typedef enum {
    DRV_SERIAL_FC_XOFF = 0,     /* Need to stop transmission */
    DRV_SERIAL_FC_XON = 1       /* Data flow is allowed */
} drv_serial_fc_t;

/** COM Port IO Control Operations */
typedef enum {
    DRV_SERIAL_CONTROL_GET_BAUDRATE = 0,        /* Return Baudrate Value - Output Parameter as (uint32 *) */
    DRV_SERIAL_CONTROL_GET_BAUDRATE_DEFAULT,    /* Return Default Baudrate Value - Output Parameter as (uint32 *) */
    DRV_SERIAL_CONTROL_SET_BAUDRATE,            /* Set Baudrate Value - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_CHECK_BAUDRATE,          /* Check if input Baudrate Value is valid - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_CHAR_SIZE,           /* Set Character Size in Bits - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_STOP_BITS,           /* Set Number of Stop Bits - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_PARITY_ENABLE,       /* Enable Parity Check - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_PARITY_EVEN,         /* Configure Parity Check for Even Parity - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_PARITY,              /* Set the Parity bit - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_RX_DMA_ENABLE,       /* Enable/Disable RX DMA - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_TX_DMA_ENABLE,       /* Enable/Disable TX DMA - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_CHECK_DMA_MODE,          /* Check if DMA Mode is supported - No Parameter */
    DRV_SERIAL_CONTROL_SET_DMA_MODE,            /* RxRDY Dma Req is triggered by rx threshold and TXRDY by Tx FIFO empty - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_CHECK_TX_DMA,            /* Check if TX DMA is ongoing - No Parameter */
    DRV_SERIAL_CONTROL_GET_DTR,                 /* Get DTR State - Output Parameter as (uint32 *) */
    DRV_SERIAL_CONTROL_SET_CTS,                 /* Set/Clear CTS - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_GET_CTS,                 /* Get CTS State - Output Parameter as (uint32 *) */
    DRV_SERIAL_CONTROL_SET_DCD,                 /* Set/Clear DCD - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_DSR,                 /* Set/Clear DSR - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_RI,                  /* Set/Clear Ring Indicator - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_HW_FC,               /* Set/Clear Hardware Flow Control - Input Parameter as (uint32) @see drv_serial_fc_t */
    DRV_SERIAL_CONTROL_SET_BREAK,               /* Set/Clear Break - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_CBS,                 /* Register Interrupt Callbacks - Input Parameter as (drv_serial_cbs_t *) */
    DRV_SERIAL_CONTROL_DISABLE_CBS,             /* Disable all Interrupt Callbacks - No Parameter */
    DRV_SERIAL_CONTROL_SET_DATA_READ_CB_ENABLE, /* Enable/Disable Data Read Completion Callback - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_DATA_WRITE_CB_ENABLE,/* Enable/Disable Data Write Completion Callback - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_STATUS_CB_ENABLE,    /* Enable/Disable Status Callback - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_DTR_CB_ENABLE,       /* Enable/Disable Data Terminal Ready Callback - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_CHECK_TX_EMPTY,          /* Check that send pipe is empty - No Parameter */
    DRV_SERIAL_CONTROL_SET_FIFO_ENABLE,         /* Enable/Disable RX/TX FIFOs - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_RX_FIFO_TRIGGER,     /* Configures RX FIFO Trigger - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_CLEAR_RX_FIFO,           /* Clear the RX FIFO - No Parameter */
    DRV_SERIAL_CONTROL_CLEAR_TX_FIFO,           /* Clear the TX FIFO - No Parameter */
    DRV_SERIAL_CONTROL_SET_TX_MODE,             /* Set TX Posted/Blocking mode - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_SET_RX_MODE,             /* Set RX Posted/Blocking mode - Input Parameter as (uint32) */
    DRV_SERIAL_CONTROL_TX_ONLY,                 /* Declare that the serial port is Tx way only - No Parameter */
    DRV_SERIAL_CONTROL_TX_REQ,                  /* enum description template*/
    DRV_SERIAL_CONTROL_START_TX_TIMEOUT,        /* enum description template*/
    DRV_SERIAL_CONTROL_START_RX_TIMEOUT,        /* enum description template*/
    DRV_SERIAL_CONTROL_STOP_TX_TIMEOUT,         /* enum description template*/
    DRV_SERIAL_CONTROL_STOP_RX_TIMEOUT,         /* enum description template*/

} drv_serial_control_ops_e;

/**
 * Data Read Callback. Called when a read request has been completed.
 *
 * @param handle        Handle to Serial Port.
 *
 */
typedef void (*drv_serial_data_read_cb_t)( void * handle );

/** drv_serial_data_write_cb_t
 * Data Write Callback. Called when a write request has been completed.
 *
 * @param handle        Handle to Serial Port.
 * @param write_complete called from write complete interrupt
 *
 */
typedef void (*drv_serial_data_write_cb_t)( void * handle , int write_complete);

/**
 * Status Callback. Called when the status of the Serial Port has changed
 *
 * @param handle        Handle to Serial Port.
 * @param status        Status returned
 *
 */
typedef void (*drv_serial_status_cb_t)( void * handle, drv_serial_status_e status );

/**
 * DTR Callback. Called when a change on DTR has occured.
 *
 * @param handle        Handle to Serial Port.
 *
 */
typedef void (*drv_serial_dtr_cb_t)( void * handle );

/** Serial Port Callbacks - Per COM Port */
typedef struct {
    /** Data Read Callback */
    drv_serial_data_read_cb_t           data_read_cb;
    /** Data Write Callback */
    drv_serial_data_write_cb_t          data_write_cb;

    /** Status Callback */
    drv_serial_status_cb_t              status_cb;

    /** DTR Callback */
    drv_serial_dtr_cb_t                 dtr_cb;

    /** Data passed as a parameter to the callbacks */
    void *                              data;

} drv_serial_cbs_t;

/**
 * Serial Port operation prototype, see drv_serial_register description
 *
 */
typedef drv_serial_index_e (*drv_serial_init_t)( drv_serial_index_e port_index, uint32 phy_index );

/**
 * Serial Port operation prototype, see drv_serial_open description
 *
 */
typedef void * (*drv_serial_open_t)( uint32 phy_index);

/**
 * Serial Port operation prototype, see drv_serial_close description
 *
 */
typedef drv_serial_error_e (*drv_serial_close_t)( drv_serial_handle_t handle );

/**
 * Serial Port operation prototype, see drv_serial_read description
 *
 */
typedef drv_serial_error_e (*drv_serial_read_t)( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_read );

/**
 * Serial Port operation prototype, see drv_serial_write description
 *
 */
typedef drv_serial_error_e (*drv_serial_write_t)( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_write );

/**
 * Serial Port operation prototype, see drv_serial_control description
 *
 */
typedef drv_serial_error_e (*drv_serial_control_t)( drv_serial_handle_t handle, drv_serial_control_ops_e op, uint32 data );

/** Serial Port Operations */
typedef struct {
    /** Init a Serial port for use [optional] */
    drv_serial_init_t                   init;

    /** Opens a Serial port for use */
    drv_serial_open_t                   open;
    /** Closes an opened Serial port */
    drv_serial_close_t                  close;

    /** Read data from Serial port */
    drv_serial_read_t                   read;
    /** Write data to Serial port */
    drv_serial_write_t                  write;

    /** Serial Port Control */
    drv_serial_control_t                control;

} drv_serial_ops_t;

/******************************************************************************
 * Serial Driver Interface
 ******************************************************************************/

/**
 * Initializes the Serial Port(s), not defined in the Serial Driver, has to be implemented in the application.
 * The function should initialize internally all needed peripherals/drivers and register the available
 * serial port using the drv_serial_register function.
 *
 */
void drv_serial_initialize( void );

/**
 * Register a set of Operations for the specified Serial Port.
 *
 * @param index         Serial Port to register operations with
 * @param priv_index    Internal Serial Port index
 * @param ops           Pointer to Serial Port operations
 * @param name          Unique port name
 *
 * @return              port index or DRV_SERIAL_PORT_NB on error
 *
 */
drv_serial_index_e drv_serial_register( uint32 priv_index, drv_serial_ops_t * ops, const char* name );

/**
 * UnRegister a set of Operations for the specified Serial Port.
 *
 * @param index         Serial Port to register operations with
 *
 * @return              0 or negative error.
 *
 */
drv_serial_error_e drv_serial_unregister( drv_serial_index_e index );

/**
 * Open a Serial port.
 *
 * @param index         Serial port to open
 *
 * @return              Returns handle to Serial port or NULL if error.
 *
 */
drv_serial_handle_t drv_serial_open( drv_serial_index_e index, drv_serial_notify_cb_t notify_cb, void* ctx );

/**
 * Close an open Serial port.
 *
 * @param handle        Handle to Serial Port.
 *
 * @return              0 or negative error.
 *
 */
drv_serial_error_e drv_serial_close( drv_serial_handle_t handle );

/**
 * Control of the Serial Port.
 *
 * @param handle        Handle to Serial Port.
 * @param op            Control operation to perform
 * @param data          Input/Output Value used for Control operation - See drv_serial_control_ops_e for details
 *
 * @return              value returned depends on control operation
 *
 */

static inline drv_serial_error_e drv_serial_control( drv_serial_handle_t handle, drv_serial_control_ops_e op, uint32 data )
{
    drv_serial_error_e error = DRV_SERIAL_NO_ERROR;
    if (handle) {
        if (handle->ops) {
            error = ((drv_serial_ops_t *)handle->ops)->control( handle, op, data );
        }
    }
    return error;
}

/**
 * Read data from the Serial Port. The function will return the number of bytes that were actually read.
 *
 * @param handle        Handle to Serial Port.
 * @param buffer        Pointer to the data buffer which will receive the data
 * @param size          Maximum Number of bytes in the buffer
 * @param nb_read       Pointer to a variable which returns number of bytes read
 *
 * @return              Error Status
 *
 */
static inline drv_serial_error_e drv_serial_read( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_read )
{
    drv_serial_error_e error = DRV_SERIAL_NO_ERROR;
    DEV_ASSERT( nb_read != NULL );
    if (handle) {
        if (handle->ops) {
            error = ((drv_serial_ops_t *)handle->ops)->read( handle, buffer, size, nb_read );
        }
    }

    return error;
}

/**
 * Write data to the Serial Port. The function will return the number of bytes that were actually written.
 *
 * @param handle        Handle to Serial Port.
 * @param buffer        Pointer to the data buffer which holds the data to transmit
 * @param size          Maximum Number of bytes in the buffer
 * @param nb_write      Pointer to a variable which returns number of bytes written
 *
 * @return              Number of bytes written
 *
 */
static inline drv_serial_error_e drv_serial_write( drv_serial_handle_t handle, uint8 * buffer, uint32 size, uint32 * nb_write )
{
    drv_serial_error_e error = DRV_SERIAL_NO_ERROR;
    DEV_ASSERT( nb_write != NULL );
    if (handle) {
        if (handle->ops) {
            error = ((drv_serial_ops_t *)handle->ops)->write( handle, buffer, size, nb_write );
        }
    }

    return error;
}

/**
 * Returns the handle of a Serial Port
 *
 * @param index         Serial port to retrieve handle
 *
 * @return              Returns handle to Serial port or NULL if not registered.
 *
 */
drv_serial_handle_t drv_serial_get_handle( drv_serial_index_e index );

/** drv_serial_get_host_port
 * Returns the handle of a "Host" Serial Port
 *
 * @return              Returns index of "Host" serial port.
 *
 */
drv_serial_index_e drv_serial_get_host_port( void );

#endif /* #ifndef _DRV_SERIAL_H_ */

/** @} END OF FILE */
