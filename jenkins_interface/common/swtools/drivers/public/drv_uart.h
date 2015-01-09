/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_uart.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup UartDriver UART Driver
 * @ingroup  HostCom
 */

/**
 * @addtogroup UartDriver
 * @{
 */

/**
 * @file drv_uart.h UART driver public interface
 *
 */

#ifndef DRV_UART_H
#define DRV_UART_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#if defined(__dxp__)
#include "dxpnk_types.h"
#endif
#include "icera_global.h"
#include "drv_ipm.h"
#include "drv_arch_type.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** UART uses DMA by default */
#define WITH_UART_DMA

/** The maximum number of characters we can send to the UART TX FIFO without perfoming a check
 */
#define UARTDRV_MAX_TX_CHARS (16)

/** The maxium number of characters we can extract from the UART RX FIFO without perfoming a check
 */
#define UARTDRV_MAX_RX_CHARS (16)

#define STE_UART0_NB_RX_DMA_DESC 32
#define STE_UART0_NB_TX_DMA_DESC 32
#define STE_UART1_NB_RX_DMA_DESC 32
#define STE_UART1_NB_TX_DMA_DESC 32
#define STE_UART2_NB_RX_DMA_DESC 32
#define STE_UART2_NB_TX_DMA_DESC 32

/* The maximum allowable number of consecutive protocol failures */
#define MAX_CONSECUTIVE_FAILURES   (3)

/* An invalid message value */
#define UART_BOGUS (0xff)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/** uartdrvt_Handle Handle to the uard drivers
 * Returned from a call to dxpnk_UartOpen. Used to access UART instance
 */
typedef void uartdrvt_Handle;

/** uartdrivt_UartId :
 *   Used to identify a particular UART instance (or not!)
 */
typedef enum {
  UARTDRV_UART0,            /* Identifier for UART instance UART0 */
  UARTDRV_UART1,            /* Identifier for UART instance UART1 */
  UARTDRV_UART2,            /* Identifier for UART instance UART2 */
  UARTDRV_UARTBOGUS         /* No physical UART  */
} uartdrvt_UartId;

/** uartdrivt_Param :
 *   Used to configure the UART device with drv_uart_Ctrl
 */
typedef enum{
  UARTDRV_SET_CHAR_SIZE,     /**< Set the char size (valid values are 5, 6, 7 or 8) */
  UARTDRV_SET_STOP_BITS,     /**< Set number of stop bits (valid values are 1 or 2) */
  UARTDRV_SET_PARITY_ENB,    /**< Enable parity 0=disabled 1=enabled */
  UARTDRV_SET_PARITY_EVEN,   /**< Even/odd parity 0=odd 1=even */
  UARTDRV_SET_PARITY,        /**< Set parity bit to 0 or 1 */
  UARTDRV_SET_BREAK,         /**< Transmit a break condition */
  UARTDRV_SET_BAUD_RATE,     /**< Set the baud rate of the uart */
  UARTDRV_SET_FIFO_ENB,      /**< Enable RX & TX FIFOs */
  UARTDRV_SET_RXFIFO_TRIG,   /**< Set trigger level for RX FIFO (valid values are 1, 4, 8 or 16)*/
  UARTDRV_CLR_RX_FIFO,       /**< Set to 1 to clear all the bytes in the RX FIFO and reset its counter */
  UARTDRV_CLR_TX_FIFO,       /**< Set to 1 to clear all the bytes in the TX FIFO and reset its counter */
  UARTDRV_SET_USE_TX_DMA,    /**< Set to 1 to request the use of Tx DMA implies use of FIFO*/
  UARTDRV_SET_USE_RX_DMA,    /**< Set to 1 to request the use of Rx DMA implies use of FIFO*/
  UARTDRV_SET_DMA_MODE,      /**< Set to 1 so that RxRDY Dma Req is triggered by rx threshold and TXRDY by Tx FIFO empty*/
  UARTDRV_SET_TX_ONLY,       /**< Set to 1 so that the UART ignores the RX int and can cut its clock as soon as Tx is terminated */
} uartdrvt_Param;


/** uartdrvt_Err:
 *   Used to relay error information from the UART device
 */
typedef enum
{
  UARTDRV_ERR_NONE,    /* No errors reported in Line Status Register */
  UARTDRV_ERR_OVR,     /* Receive register overrun error detected*/
  UARTDRV_ERR_PAR,     /* Receive data parity error detected */
  UARTDRV_ERR_FRM,     /* Receive data framing error detected */
  UARTDRV_ERR_RXEMPTY, /* Attempt to read from RX FIFO failed because the RX FIFO was empty */
  UARTDRV_ERR_TXFULL   /* Attempt to transmit character failed because TX FIFO was full */
} uartdrvt_Err;

typedef enum
{
  UARTDRV_PARITY_NONE,
  UARTDRV_PARITY_ODD,
  UARTDRV_PARITY_EVEN
} uartdrvt_Parity;

/**
 * UART configuration entry
 */
typedef struct
{
    uint32 apparent_baudrate;    /* baudrate that is programmed by the caller */
    uint32 precomputed_latch_div; /* If this is 0, precompute it on registration from requested_real_baud_rate */
    uint32 precomputed_oversampling_factor; /* If precomputed_latch_div is != 0, this must contain precomputed oversampling factor */
    uint32 requested_real_baud_rate;  /* desired real baud rate */
} tUartCfg;


#define MAX_UART_CFG_ENTRIES 8
/**
 * UART configuration
 */
typedef struct
{
    int nb_entries;
    tUartCfg uart_cfg_tb[MAX_UART_CFG_ENTRIES];
} tUartCfgSet;

/* Callbacks */
typedef void (*drv_Uart_rx_data_ready_cb)(void * data);
typedef void (*drv_Uart_tx_sent_cb)(void * data, int write_complete);
typedef void (*drv_Uart_statusEvent_cb)(void * data, uint32 eventSummary);

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Register uart drivers in the power management controler.
 * This function in called once during the init from drv_init()
 *
 * @param uartId
 */
void drv_UartPmInit(uartdrvt_UartId uartId);

/**
 * Open an instance of the UART driver
 *
 * pre  : Should not be called from interrupt handler
 *        uartId specifies which UART instance to open
 *        nanok_init_handle must have ben set from dxpnk_Init
 *
 * post : If Uart instance isn't already in use (i.e the handle hasn't already been
 *        assigned without a subsequent uartdrv_Close), registers the calling
 *        thread with the UART driver, returns a handle to the UART
 *        instance, configures the UART to the default state (see above) and clears the associated error bits.
 *        Otherwise returns NULL.
 *
 * @param uartID
 *
 * @return uartdrvt_Handle*
 */
uartdrvt_Handle* drv_UartOpen(uartdrvt_UartId uartID);

/**
 * Close the driver
 *
 * pre  : Should not be called from interrupt handler
 *        handle from uartdrv_Open
 * post : Flushes any pending notifications by writing to the registered thread's
 *        message queue. Failed notification writes here are not reattempted.
 *        Closes connection to UART such that a subsequent call to uartdrv_Open
 *        for the associated UART can succeed.
 *        Returns 0 if any of the pending notification writes failed.
 *        != 0 otherwise.
 *
 * @param handle
 *
 * @return int
 */
int drv_UartClose(uartdrvt_Handle *handle);

/**
 * Return the first error
 *
 * pre  : Should not be called from interrupt handler
 *        handle from drv_uart_Open
 * post : Returns the first error not already returned by either drv_uart_GetFirstRecordedError,
 *        drv_uart_Get or drv_uart_Put.
 * NOTES :
 *         Useful for when you've received an async notification of type UARTDRV_ASYNC_RXERR
 *
 * @param void_handle
 *
 * @return uartdrvt_Err
 */
uartdrvt_Err drv_UartGetFirstRecordedError(uartdrvt_Handle *void_handle);

/**
 * Return space free in the Tx FIFO.
 *
 * pre  : Should not be called from interrupt handler
 *        handle from drv_uart_Open
 * post : Returns number of characters for transmission.
 *        Note that when FIFOs are disabled, 0 will be returned if numChars > 1.
 *        When FIFOs are enabled, 0 will be returned if numChars > UARTDRV_MAX_TX_CHARS.
 *
 * @param handle
 *
 * @return int
 */
int drv_UartTxSpace(uartdrvt_Handle *handle);

/**
 * Send some data to the Uart
 *
 * pre  : Should not be called from interrupt handler
 *        handle from drv_uart_Open
 *        data contains the values to be written to the UART TX FIFO/buffer.
 *        numChars specifies the number of characters from data to write.
 *        If FIFO mode is disabled, numChars == 1;
 *        If FIFO mode enabled, numChars <= UARTDRV_MAX_TX_CHARS;
 * post : Attempts to write data to the TX FIFO/BUFFER.
 *        Returns UARTDRV_ERR_TXFULL if FIFO/BUFFER is unable to receive all
 *        numChars characters for transmission at this time.
 *        Otherwise returns error status as reported
 *        by Line Status Register.
 *
 * Notes : Normally, efficient transmission would be performed
 *         by arranging for an asysnchronous notification of type
 *         UARTDRV_ASYNC_TXEMPTY to be delivered before the bulk
 *         write is attempted.
 *         Alternatively, you call poll the TX FIFO using drv_uart_TxSpace
 *
 * E.g.    Most efficient way to write to UART:
 *         0. Enable FIFOs
 *         1. Setup async notification for UARTDRV_ASYNC_TXEMPTY
 *         2. Wait for message associated with UARTDRV_ASYNC_TXEMPTY notification
 *         3. Invokde drv_uart_Put, specifying UARTDRV_MAX_TX_CHARS characters
 *         4. Repeat steps 2 and 3 as required.
 *
 *         Similarly, you can use drv_uart_TxSpace to poll the fifo empty flag:
 *         0. Enable FIFOs
 *         1. Call drv_uart_TxSpace until it returns > UARTDRV_MAX_TX_CHARS
 *         2. Invoke drv_uart_Put, specifying UARTDRV_MAX_TX_CHARS characters
 *            repeat steps 1 and 2 as required.
 *
 * @param handle
 * @param data
 * @param numChars
 * @param error
 *
 * @return int
 */
int drv_UartPut(uartdrvt_Handle *handle,
                 uint8 data[], uint32 numChars, uartdrvt_Err *error);

/**
 * Return number of bytes received from the uart
 *
 * pre  : Should not be called from interrupt handler
 *        handle from drv_uart_Open
 * post : Returns 1 if a complete incoming character is available from
 *        the receive buffer register or the RX FIFO. 0 otherwise.
 * Notes: This only check LSR so 1 or 0 is returned !
 *
 * @param handle
 *
 * @return uint32
 */
uint32 drv_UartRxSpace(uartdrvt_Handle *handle);

/**
 * Get the received data
 *
 * pre  : Should not be called from interrupt handler
 *        handle from dxpnk_UartOpen
 *        numChars specifies the number of characters to retrieve.
 *        if FIFO mode is disabled, numChars == 1
 *        if FIFO mode enabled, numChars <= UARTDRV_MAX_RX_CHARS;
 *        data contains enough space for numChars characters
 * post : If RX FIFO/Buffer is empty, returns UARTDRV_ERR_RXEMPTY.
 *        Otherwise attempts to extract numChars characters from the UART RX FIFO/buffer.
 *        If numChars > 1 and that many characters are not available, extracts as many as
 *        possible into data and returns UARTDRV_ERR_RXEMPTY . Otherwise returns error status
 *        as reported by the Line Status Register (no errors will return  UARTDRV_ERR_NONE).
 *
 * Notes : The bulk read is intended as a performance enhancement. The user should ensure that
 *         the RX FIFO contains enough entries to satisfy the request, otherwise it is impossible
 *         to ascertain how many characters were actually retrieved. Normally this would be
 *         done by arranging for an asysnchronous notification of type UARTDRV_ASYNC_RXRDY and
 *         setting the RX FIFO trigger appropriately (using configuration parameter
 *         UARTDRV_SET_RXFIFO_TRIG).
 *
 *
 * @param handle
 * @param data
 * @param numChars
 * @param error
 *
 * @return int
 */
int drv_UartGet(uartdrvt_Handle *handle,
                 unsigned char data[], unsigned int numChars, uartdrvt_Err *error);

/**
 * Configure UART settings using uartdrvt_Param enum
 *
 * pre  : Should not be called from interrupt handler
 * @param handle from drv_uart_Open
 * @param param specifies the control parameter to modify.
 * @param value gives the new value for the given parameter.
 * post : Performs UART control function as specified.
 * @return Returns non-zero value if successful, zero otherwise.
 *
 * Notes : drv_uart_Ctrl performs no checking on the validity
 *         of the values being assigned to parameters - hence
 *         weird things will happen if you specify invalid values.
 *
 * UART Default settings are:
 * ---------------------
 * UARTDRV_SET_CHAR_SIZE   : 7-bits
 * UARTDRV_SET_STOP_BITS   : 1-bit
 * UARTDRV_SET_PARITY_ENB  : 0 (DISABLED)
 * UARTDRV_SET_PARITY_EVEN : 0
 * UARTDRV_SET_PARITY      : 0
 * UARTDRV_SET_BREAK       : 0 (DISABLED)
 * UARTDRV_SET_BAUD_RATE   : 9600
 * UARTDRV_SET_FIFO_ENB    : 0 (DISABLED) and FIFOs cleared
 *
 * Notes : For more information regarding configuration parameters,
 *         refer to the BARCO SILEX M3 UART Specifications document version 1.7
 *
 */
int drv_UartCtrl(uartdrvt_Handle *handle,
                   uartdrvt_Param param, unsigned int value);


/**
 * Return cts line value
 *
 * pre  : Should not be called from interrupt handler
 * @param handle from drv_uart_Open
 *        param specifies the control parameter to modify.
 *        value gives the new value for the given parameter.
 * post :
 *
 * Notes : drv_uart_get_cts return the curent CTS state from MSR
 * returns int cts line value
 */
int drv_UartGetCts(uartdrvt_Handle *handle);


/**
 * Enable hardware flow control
 *
 * pre  : Should not be called from interrupt handler
 * @param handle from drv_uart_Open
 * @param val: value of RTS bit to set in MCR register
 * post :
 *
 * Notes : drv_UartSetHwFc sets RTS state in MCR if val=0 nRTS goes high
 *          otherwise nRTS reacts in accordance to the Rx FIFO trigger level
 */
void drv_UartSetHwFc(uartdrvt_Handle *handle, int val);


/**
 * Disable status interrupt
 * @param handle uart handle
 */
void drv_UartStatusIntDisable(uartdrvt_Handle *handle);

/**
 * Enable status interrupt
 * @param handle uart handle
 */
void drv_UartStatusIntEnable(uartdrvt_Handle *handle);

/**
 * Disable RxRdy interrupt
 * @param handle uart handle
 */
void drv_UartRxRdyIntDisable(uartdrvt_Handle *handle);

/**
 * Enable RxRdy interrupt
 * @param handle uart handle
 */
void drv_UartRxRdyIntEnable(uartdrvt_Handle *handle);

/**
 * Enable TxDone interrupt
 * @param handle uart handle
 */
void drv_UartTxDoneIntDisable(uartdrvt_Handle *handle);

/**
 * Enable TxDone interrupt
 * @param handle uart handle
 */
void drv_UartTxDoneIntEnable(uartdrvt_Handle *handle);

/**
 * Disable all interrupts
 * @param handle uart handle
 */
void drv_UartAllIntDisable(uartdrvt_Handle *handle);

/**
 * Enable all interrupts
 *
 * @param handle uart handle
 */
void drv_UartAllIntEnable(uartdrvt_Handle *handle);

/**
 * Register interrupt call back
 *
 * @param handle
 * @param rxcb   Pointer to the function called when data have been received
 * @param txcb   Pointer to the function called when tx fifo is empty
 * @param statcb Pointer to the function called when status
 * @param data
 */
void drv_UartRegisterIntCallback(uartdrvt_Handle *handle,
                                 drv_Uart_rx_data_ready_cb rxcb,
                                 drv_Uart_tx_sent_cb txcb,
                                 drv_Uart_statusEvent_cb statcb,
                                 void *data );

/**
 * Test if tx FIFO is empty
 * Use for synchronisation.
 * @param handle
 *
 * @return true in the TX FIFO is empty and all the charactere has been transmited
 */
bool drv_UartIsTxEmpty(uartdrvt_Handle *handle);


/*
 * pre  :
 *        uartId : UART on which to apply (does not require uart handle returned bu drv_uart_Open)
 *        on_noff gives the new value for the given parameter.
 * post :
 *
 * @param handle on uart context
 * @param on_off value to set
 *
 * Notes : drv_uart_set_rts does pretty much the same as drv_uart_set_hw_fc which is kept for
 *          backward compatibity
 *         Sets RTS state in MCR if val=0 nRTS goes high
 *          otherwise nRTS reacts in accordance to the Rx FIFO trigger level
 */
void drv_UartSetCts(uartdrvt_Handle *handle, int on_off);

/**
 * Re-open uart.
 *
 * Close uart (if needed) and reopen it.
 *
 * @param uartId the UART identifier.
 *
 * @return the uart handle.
 */
uartdrvt_Handle *drv_UartReOpen(uartdrvt_UartId uartId);

/**
 * Get UART current baud rate.
 *
 * @param handle on uart context
 *
 * @return the uart baud rate.
 */
uint32 drv_UartGetBaudRate(uartdrvt_Handle *handle);

/**
 * Check whether a baud rate is valid for a given Uart ID
 * @param uart_id the UART identifier.
 *
 * @param baudrate the string of the baud rate to be checked in
 *       this UART configuration
 *
 *
 * @return whether the baudrate is valid for this UART
 */
bool drv_UartCfgBaudrateAuthorized(uartdrvt_UartId uart_id, uint32 baudrate);

/**
 * Get handle to the Uart
 * @param handle on uart context
 *
 * @return Id of this UART
 */
uartdrvt_UartId drv_UartGetIdPerHandle(uartdrvt_Handle *handle);

/**
 * Start UART discovery.
 *
 * Send 3 consecutive REQOPEN on UART and wait for a valid
 * RESPOPEN.
 * Wait timeout currently hard coded in drv_uart_client.c.
 * Assumption is that a host UART server is listening for
 * REQOPEN.
 *
 * If return is OK then UART can be used as HIF.
 *
 * @return int 1 if a server answered, 0 on "failure"
 */
int drv_UartDiscover(void);

/******************************************************************************************
 * Private internal API
 ******************************************************************************************/

/**
 * Set Uart Tx DMA interrupt
 * @param handle
 * @param on
 */
void drv_UartSetTxDmaInt(uartdrvt_Handle *handle, int on);

/**
 * Set Uart Rx DMA interrupt
 * @param handle
 * @param on
 */
void drv_UartSetRxDmaInt(uartdrvt_Handle *handle, int on);

/**
 * Set Uart Rx DMA trigger
 * @param handle
 * @param location
 */
void drv_UartSetRxDmaTrigger(uartdrvt_Handle *handle, uint32 location);

/**
 * Set Uart baud rate constraint
 * @param uart_id
 */
void drv_UartSetBaudrateConstraint(uartdrvt_UartId uart_id);


/**
 * Set the list of supported baudrate called by drv_init
 *
 * @param uartId
 * @param cfg
 */
void drv_UartRegisterBaudrateConstraint(uartdrvt_UartId uartId, const tUartCfgSet * cfg);

/**
 * Get TX dma state: called to determine whether to reenable the Tx interrupt
 *
 * @param handle from drv_uart_Open.
 *
 * @return the flag that keeps the tx DMA active state.
 */
bool drv_UartGetOngoingTxDma(uartdrvt_Handle *handle);

/**
 * Return whether DMA mode is supported or not.
 *
 * @param handle from drv_uart_Open.
 *
 * @return true if DMA mode is supported
 */
bool drv_UartDmaModeSupported(uartdrvt_Handle *handle);

/**
 *  Called by the PreIdle callback in order to determine whether
 *  a given UART is ready to go to sleep.
 *  This will return false only when the UART Rx is declared as
 *  unused
 *
 * @param uartId  UART whose activity to poll
 */
bool drv_UartActive(uartdrvt_UartId uartId);


/**
 * Only used for test purpose
 *
 * Sets the flag so the SOC clock will be released in the
 * pre-idle callback of the UART driver
 * @param mask
 */
void drv_UartPowerOff(int mask);

/**
 * Returns RX fifo data available
 *
 */
bool drv_UartGpsRxCharAvail(void );

/**
 * Returns TX fifo empty status
 *
 */
bool drv_UartGpsTxEmpty(void);

#endif /* #ifndef DRV_UART_H */

/** @} END OF FILE */
