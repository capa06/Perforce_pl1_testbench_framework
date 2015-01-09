/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $dummy$
 * $dummy$
 * $dummy$
 * $dummy$
 ************************************************************************************************/

 /**
  * @addtogroup RfDriver
  *
  * @{
  */

 /**
  * @file drv_pmic_rf.h   API for RF Driver PMIC functionality
  *
  */

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#ifndef DRV_PMIC_RF_H
#define DRV_PMIC_RF_H

#include "drv_pmic.h"
#include "drv_rf_ext.h"

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
 * Public function declarations
 ************************************************************************************************/
/**
 * Open SPI channel to device
 *
 * @return none
 */
extern void drv_RfPaPmicChannelOpen(void);

/**
 * Close SPI channel to device
 *
 * @return none
 */
extern void drv_RfPaPmicChannelClose(void);

/**
 * Read vendor ID and reset registers to default
 *
 * @return none
 */
extern void drv_RfPaPmicChannelInit(void);

/**
 * Define IO signal as a specific sequence of SPI words
 *
 * @ param pmic_signal  Signal for IO configuration
 * @param io        Reference to the pointer to first configuration in the configuration sequence
 * @param n_cfg     Reference to the number of configurtion settings
 * @param n_dat     Reference to the number of actual data settings
 * @param shift     Shift required for data
 * @param device    Device access handle
 * @param bus       RFFE bus
 *
 */
extern void drv_RfRegisterPaPmicCtrl(
                                     int pmic_signal,
                                     drv_RfSeqTfrRequest *io,
                                     int                  *n_cfg,
                                     int                  *n_dat,
                                     int                  *gpio_default_state,
                                     int                  *data_shift,
                                     drv_RfDeviceAccess  **device,
                                     int                  bus,
                                     int                  slave_addr);

/**
 * Send PMIC configuration list
 *
 * @param option   Purpose of the configuration
 *
 */
extern void drv_SeqPaPmicCfg(int t_rel, tPmicEvents option);

/**
 *
 *
 *
 * @return int
 */
int drv_RfPaPmicSpiSpeed(void);

/**
 * Read out the number of SPIs used to program the 3G PA Vcc
 *
 * @return num_spi Number of SPI words
 */
extern int drv_RfPaPmicNumSpi3G(void);

/**
 * Check whether PMIC SPI control is used
 *
 * @return flag   If true, SPI control is used for PMIC
 */
extern bool drv_RfPaPmicSpiControl(void);

/**
 * Turn on ECO mode
 *
 * @param t_rel   Time to send the SPI words
 *
 */
extern void drv_RfPaPmicEcoOn(int t_rel);

/**
 * Turn off ECO mode
 *
 * @param t_rel   Time to send the SPI words
 *
 */
extern void drv_RfPaPmicEcoOff(int t_rel);

/**
 * Get Pa Voltage in mV
 *
 * @param dac_val
 *
 * @return int
 */
extern int drv_RfPaVoltage(int dac_val);

/**
 * Get DAC word for PA Voltage setting
 *
 * @param val_mV
 *
 * @return int
 */
extern int drv_RfPaVoltageDac(int val_mV);

/**
 * Return max PMIC VCON input voltage expected
 *
 *
 * @return int
 */
extern int  drv_RfPmicGetVconBias(void);

/**
 *  Initialize the RF PMIC
 *
 *  @param slave_addr
 */

extern void drv_RfPaPmicInit(bool use_default_vcon_offset);

#endif //DRV_PMIC_RF_H
