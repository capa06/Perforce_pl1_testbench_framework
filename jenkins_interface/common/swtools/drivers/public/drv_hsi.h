/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_hsi.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup HsiDriver HSI Driver 
 * @ingroup HostCom 
 */

/**
 * @addtogroup HsiDriver
 * @{
 */

/**
 * @file drv_hsi.h Public interface for HSI driver, providing
 *       access to low level HSI functionality
 */

#ifndef DRV_HSI_H
#define DRV_HSI_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include "dxpnk_types.h"
#include "icera_global.h"

#include "drv_serial.h"

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
/** Blocking mode */
#define HSI_MODE_BLK (0)
/** Non blocking copy mode */
#define HSI_MODE_NB (1)
/** Non blocking no copy mode */
#define HSI_MODE_NB_NOCP (3)

/** HSI Power Management */
#define HSI_POWER_MANAGEMENT

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * HSI configuration parameter
 */
typedef struct
{
    /** Number of channels from 1 to 8 */
    uint32 num_channels;
    /** Tx clock in bit/s */
    uint32 TxClock;
    /** Rx timeout in nanosecond Must be compliant with Tx Clock settings*/
    uint32 RxTimeout;
    /** Tail timeout in nanosecond Must be compliant with Tx Clock settings */
    uint32 TailTimeout;
    /** Activate framing mode */
    bool frame;
    /** Activate pipeline mode */
    bool pipeline;
    /** Burst Frame counter value */
    uint32 FrameBurst;
} drv_HsiConf;

typedef enum
{
    /** mode for Rx - param is mode */
    DRV_HSI_RX_MODE = 0,
    /** mode for Tx - param is mode */
    DRV_HSI_TX_MODE,
    /** define Rx callback - param is cb */
    DRV_HSI_RX_CB,  
    /** define Tx callback - param is cb */
    DRV_HSI_TX_CB,
    /** define timeout callback - param is cb */
    DRV_HSI_TIMEOUT_CB,
    /** Morph frame into BREAK frame  - param is value enable/disable */
    DRV_HSI_BREAK,
    /** Resync mode  - param is value enable/disable */
    DRV_HSI_RESYNC,
    /** Clear RX FIFO  - param is chan */
    DRV_HSI_CLEAR_RX_FIFO,
    /** Clear TX FIFO  - param is chan */
    DRV_HSI_CLEAR_TX_FIFO,
    /** Check if TX FIFO is empty  - param is chan */
    DRV_HSI_CHECK_TX_EMPTY,
    /** Enable RX DMA  - param is chan */
    DRV_HSI_RX_DMA_ENABLE,
    /** Enable TX DMA  - param is chan */
    DRV_HSI_TX_DMA_ENABLE,
    /** Specify RX timeout DMA  - param is value expressed in nanoseconds (default to 1ms) */
    DRV_HSI_RX_DMA_TIMEOUT,
    DRV_HSI_LAST_CMD
} drv_HsiCommand;

typedef void (*drv_HsiCb_t)(void *userdata);

/** 
 * HSI callback information
 */
typedef struct
{
    /** Callback function pointer */
    drv_HsiCb_t cb;    
    /** Data passed to callback function */
    void *userdata;
} drv_HsiCbs_t;

/** 
 * Parameter for drv_HsiControl 
 */ 
typedef struct
{
    union 
    {
        /** Channel parameter */
        int chan;
        /** Mode parameter */
        int mode;       
        /** Numeric value parameter */
        int value;
        /** Callback parameter */
        drv_HsiCbs_t cb;        
    } cmd;
} drv_HsiComParam;

typedef void * drv_HsiHandle;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize HSI driver subsystem
 *
 * Should be only called once at startup
 *
 *
 * @return 0 if successfull
 */
extern int drv_HsiInit(void);

/**
 * Configure HSI driver
 *
 * All HSI parameters are changed with new values
 * All channels must be closed before applying new configuration
 * All remaining data will be lost
 *
 * @param conf Pointer to configuration parameters
 *
 * @return 0 if configuration is successfully applied or -1 if not.
 */
extern int drv_HsiConfigure(drv_HsiConf *conf);

/**
 * Open HSI channel
 *
 * Channel must be a valid value
 *
 * @param chan Channel to open
 *
 * @return hsi handle if success  -1 otherwise
 */
extern drv_HsiHandle drv_HsiOpen(int chan);


/**
 * Close HSI channel
 *
 * @param handle Channel handle to close
 *
 * @return 0 if success -1 otherwise
 */
extern int drv_HsiClose(drv_HsiHandle handle);

/**
 * Read from HSI channel
 *
 * @param handle  Channel handle 
 * @param buffer  Buffer of word 
 * @param nwords  Number of word 
 *
 * Non blocking read returns words effectively readable or 0 if no data is present
 * When function returns 0 a read callback will be issued when some data are available
 * When DMA is activated reads are no longed synchronized to API call 
 * and are subject to a user definable timeout value
 *
 * @return number of word read or negative value in case of error
 */
extern int drv_HsiRead(drv_HsiHandle handle, int *buffer, int nwords);

/**
 * Write to HSI channel
 *
 * @param handle  Channel handle 
 * @param buffer  Buffer of word 
 * @param nwords  Number of word 
 *
 * In non blocking mode the function returns the number of words queued for write
 * a call to write callback will be issued when all data pending are effectively written
 *
 * @return number of word written or negative value in case of error
 */
extern int drv_HsiWrite(drv_HsiHandle handle, int *buffer, int nwords);

/**
 * Issue command to HSI channel
 *
 * @param handle  Channel handle 
 * @param com  Command to issue 
 * @param param  Parameter structure related to command 
 *
 *
 * @return 0 if success -1 otherwise
 */
extern int drv_HsiControl(drv_HsiHandle handle, drv_HsiCommand com, drv_HsiComParam *param);

#endif

/** @} END OF FILE */

