/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_usb.h#1 $
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

#ifndef DRV_SERIAL_USB_H
#define DRV_SERIAL_USB_H

#if defined (__dxp__)
#include "dxpnk_types.h"
#endif
#include "icera_global.h"
#include <stdlib.h>
#include "iobuf.h"
#include "iopool.h"
#include "iopool_static.h"
#include "drv_usb_config.h"

#include <dxp_bsd/sys/cdefs.h>
#define __packed    __attribute__((__packed__))

#define _INTPTR_T_DECLARED
#include <dev/usb/usb_endian.h>
#include <dev/usb/usb_cdc.h>

#include "drv_usb_obex_api.h"
#include "drv_usb_acm_api.h"

/******************************************************************************
 * Exported types
 ******************************************************************************/

/** Serial Port Callbacks Enable/Disable */
typedef struct
{
    /** Data Read Callback Enable */
    bool data_read_cb_enable;
    /** Indicates a Read event has occured when interrupt was disabled */
    bool data_read_cb_triggered;

    /** Data Write Callback Enable */
    bool data_write_cb_enable;
    /** Indicates a Write event has occured when interrupt was disabled */
    bool data_write_cb_triggered;

    /** Status Callback Enable */
    bool status_cb_enable;
    /** Indicates a Status event has occured when interrupt was disabled */
    bool status_cb_triggered;

    /** DTR Callback Enable */
    bool dtr_cb_enable;
    /** Indicates a DTR event has occured when interrupt was disabled */
    bool dtr_cb_triggered;

} drv_serial_usb_cbs_enable_t;

typedef struct 
{
    /** Number of bytes requested in the put function */
    uint32 write_bytes_req;
    /** Number of bytes acknowledged in the put function */
    uint32 write_bytes_ack;
    /** Number of bytes acknowledged in the CB function */
    uint32 write_bytes_ack_cb;
    /** Number of write requests queued */
    uint32 write_queued;
    /** Number of times Write Complete Callback is called */
    uint32 write_complete_count;

    /** Number of bytes requested in the read function */
    uint32 read_bytes_req;
    /** Number of bytes acknowledged in the read function */
    uint32 read_bytes_ack;
    /** Number of bytes acknowledged in the read function */
    uint32 read_bytes_ack_cb;
    /** Number of read requests queued */
    uint32 read_queued;
    /** Number of times Read Complete Callback is called */
    uint32 read_complete_count;

    /** Number of times Data Read Event is handled */
    uint32 data_read_event_count;
    /** Number of times Data Read Event is handled */
    uint32 data_write_event_count;
    /** Number of times Data Read Event is handled */
    uint32 status_event_count;
    /** Number of times DTR Event is handled */
    uint32 dtr_event_count;
   
} drv_serial_usb_stats_t;

typedef struct dte_signals {
    /* DTE signals (from the host) */
    int rts;    /* DTE asks DCE to prepare to accept data from the host */
                /* set high, when CDC class is enabled */
    int dtr;    /* DTE is ready to be connected */
                /* set high when a SetLineCoding is received with DTR=1 (for ACM) */
                /* set high when CDC class is enabled (OBEX) */

    /* DCD signals (from the device) */
    int cts;    /* DCE acknowledges RTS and allows DTE to transmit */
    int dcd;    /* DCE is connected to telephone */
                /* set to high when PPP session is established */
    int dsr;    /* DCE is ready to receive commands or data */
    int ri;     /* DCE has detected ring signal on the telephone line  */
    int brk;    
} dte_signals_t;

struct drv_serial_usb_softc;

typedef struct xmit_release_element
{
    struct xmit_release_element* next;
    unsigned char *   buffer;     /*The start of the buffer */
} xmit_release_element_t;

/** USB Serial driver Handle */
typedef struct drv_serial_usb_softc
{
    /* transmit queue */
    volatile int num_writes;
    int max_writes;
    int xfers_per_write;
    com_stq_head_t xmit_q;
    int xmit_locked;
#define NUM_XMIT_RELEASE_BUFFERS 16
    xmit_release_element_t release_buffers[NUM_XMIT_RELEASE_BUFFERS];
    com_stq_head_t xmit_release_free_q;
    com_stq_head_t xmit_release_busy_q;
    int multiple_write_mode;
    int multiple_write_release_block;

    /** Event for Blocking Write operations */
    os_EventHandle write_event;

    /* receive queue */
    com_stq_head_t recv_q;

    /** Event for Blocking Read operations */
    os_EventHandle read_event;

    char name[8];

    /** USB CDC Context */
    void* drv_ctx;

    drv_serial_index_e serial_index;

    /** TX Mode */
    drv_serial_tx_mode_e tx_mode;
    /** RX Mode */
    drv_serial_rx_mode_e rx_mode;

    /** Application Callbacks */
    drv_serial_cbs_t cbs;
    /** Application Callbacks Enable/Disable*/
    drv_serial_usb_cbs_enable_t cbs_enable;
    drv_acm_cbs_t               drv_cbs;
    drv_serial_usb_stats_t stats;

    /** CDC-OBEX flow control state */
    drv_serial_fc_t fc_state;
    int baudrate;
    fd_type_t fd_type;
    drv_UsbFctId fct_type;
    /** Line Coding */
    acm_line_coding_t line_coding;

    /* DTE signals (from the host) */
    dte_signals_t       dte;

    uint32 ul_payload_size;
    iopool_static_t dl_pool;
    void* dl_pool_handle;
    int opened; /* set to high when application opens the serial port */
    int fct_index;
    uint32 phy_index;

} drv_serial_usb_softc_t;

/******************************************************************************
 * Serial USB Driver Interface
 ******************************************************************************/
cdc_init_info_t* drv_serial_usb_caps(void* app_ctx,cdc_init_info_t* info);

int drv_serial_usb_init( void* drv_ctx, cdc_callbacks_t* cbs,const drv_cdc_cbs_t* drv_cbs,drv_serial_usb_softc_t* sc );

#endif /* #ifndef _DRV_SERIAL_USB_H_ */

/** @} END OF FILE */
