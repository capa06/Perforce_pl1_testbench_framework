/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_thread.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup SerialDriver
 * @{
 */

/**
 * @file drv_serial_thread.h Header file for Serial Thread implementation
 * 
 */

#ifndef DRV_SERIAL_THREAD_H
#define DRV_SERIAL_THREAD_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "os_abs.h"
#include "drv_serial.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef enum {
    DRV_SERIAL_EVENT_RX_DONE,
    DRV_SERIAL_EVENT_TX_DONE,
    DRV_SERIAL_EVENT_STATUS,
    DRV_SERIAL_EVENT_ERROR,
    DRV_SERIAL_EVENT_DTR,
    DRV_SERIAL_EVENT_ASYNC_WRITE,
    DRV_SERIAL_EVENT_USER_WRITE,
	DRV_SERIAL_EVENT_UNREGISTER,
} e_SerialEvent;

typedef struct {
    void (*rx_cb)(void *dev_ctx);
    void (*tx_cb)(void *dev_ctx, int write_complete); 
    void (*status_cb)(void *dev_ctx);
    void (*error_cb)(void *dev_ctx);
    void (*dtr_cb)(void *dev_ctx);
    void (*async_write_cb)(void *dev_ctx);
} drv_SerialThrCbs;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern os_EventHandle drv_SerialGetEventHandle(drv_serial_index_e index);
extern void drv_SerialThrInitialise( drv_serial_index_e index );
extern void drv_SerialThrUnRegisterCB(drv_serial_index_e index, void *dev_ctx);
extern void drv_SerialThrRegisterCB(drv_serial_index_e index, drv_SerialThrCbs *cbs, void *dev_ctx);

static inline void drv_SerialThrRaiseEvent(drv_serial_index_e index, e_SerialEvent ev)
{
    os_EventSet(drv_SerialGetEventHandle(index), BIT(ev));
}

static inline void  Serial_UserWriteReqEvent( drv_serial_index_e serial_index)
{
    drv_SerialThrRaiseEvent(serial_index, DRV_SERIAL_EVENT_USER_WRITE);
}

e_SerialEvent drv_SerialWriteComplete2WriteDrvSerialEvent(int write_complete);

#endif
/** @} END OF FILE */

     
