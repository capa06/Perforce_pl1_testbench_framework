/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_crpc_9xxx.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup CrpcDriver CRPC Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup CrpcDriver
 * @{
 */

/**
 * @file drv_crpc.h CRPC interface to provide constants and functions for
 *       Clock Reset and Power Control
 *
 */

#ifndef DRV_CRPC_9XXX_H
#define DRV_CRPC_9XXX_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "mphal_powerclk.h"

/*************************************************************************************************
 * Macros and defines
 ************************************************************************************************/

#define DRV_CRPC_EXTERNAL_PLL ((uint32)(-1))
#define DRV_CRPC_DIV_NOT_PRESENT (0)

/** Converter Clock Source */
typedef enum {
    DRV_CRPC_CETWDT_CLOCK_FROM_BBRF,
    DRV_CRPC_CETWDT_CLOCK_FROM_MCLK
} drv_CrpcCetWdtClockSource;

/** Secondary clock outputs (SoC and DDR not included: they
 *  are managed separately, not through this API) */
typedef enum {
    CRPC_CLKOUT_CLKOUT0 = 0,
    CRPC_CLKOUT_CLKOUT1,
    CRPC_CLKOUT_AUDIO_GUT,
    CRPC_CLKOUT_USI_PHY0,
    CRPC_CLKOUT_USI_PHY1,
    CRPC_CLKOUT_USI_PHY2,
    CRPC_CLKOUT_USI_SEQCR,
    CRPC_CLKOUT_BBRF_TST,
    CRPC_CLKOUT_USB_PHY,
    CRPC_CLKOUT_UMCO,
    CRPC_CLKOUT_NB
} drv_CrpcSecondaryClockOutputs;

/** Secondary clock outputs mux selections */
typedef enum {
    CRPC_CLKOUT_MUX_OFF = 0,
    CRPC_CLKOUT_MUX_PREDIVA,
    CRPC_CLKOUT_MUX_PREDIVB,
    CRPC_CLKOUT_MUX_PREDIVC,
    CRPC_CLKOUT_MUX_MCLK,
    CRPC_CLKOUT_MUX_NB
} drv_CrpcSecondaryClockMuxSelections;

/** Frequency selector */
typedef enum {
    DRV_CRPC_FREQ_PLL,
    DRV_CRPC_FREQ_PLL_APP,
    DRV_CRPC_FREQ_PLL_APP_WITHOUT_NF,
    DRV_CRPC_FREQ_DXP,
    DRV_CRPC_FREQ_DXP_MAX,
    DRV_CRPC_FREQ_CLKA,
    DRV_CRPC_FREQ_CLKB,
    DRV_CRPC_FREQ_CLKC,
    DRV_CRPC_FREQ_BBRF,
    DRV_CRPC_FREQ_SOC,
    DRV_CRPC_FREQ_USI,
    DRV_CRPC_FREQ_DDR
} drv_CrpcFreqSelector;

/** Clock unit selector */
typedef enum {
    DRV_CRPC_HZ = 1,
    DRV_CRPC_KHZ = 1000,
    DRV_CRPC_MHZ = 1000000
} drv_CrpcClockUnitSelector;


/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Checks whether external PLL (aka PLLP) is used
 *
 * @return 'Ext PLL used' flag
 */
extern uint32 drv_CrpcIsExtPllInUse(void);

/**
 * Read back the APP PLL configuration word from CRPC register,
 * replace the NF in the read value with the argument
 * and return the modified value
 *
 * @param nf    : NF to be inserted into the conf word
 *
 * @return Modified PLL conf word
 *
 */
extern uint32 drv_CrpcGetPllConfWordWithNfGiven(uint32 nf);

/**
 * Replace the NF in the conf word given with the argument
 * and return the modified value
 *
 * @param pll_conf_word: Conf word, basis for replacement
 * @param nf    : NF to be inserted into the conf word
 *
 * @return Modified PLL conf word
 *
 */
extern uint32 drv_CrpcReplaceNfWithNfGiven(uint32 pll_conf_word, uint32 nf);

/**
 * Write the new NF to APP PLL conf
 *
 * @param pll_conf_word: Conf word, basis for NF update
 * @param nf: NF to write
 *
 * @return None.
 *
 */
extern void drv_CrpcWriteNewNf(uint32 pll_conf_word, uint32 nf);

/**
 * Return the selected frequency as read from CRPC registers
 *
 * @param freq : Selects the frequency to be returned
 * @param unit : Selects the unit the selected frequency is returned in
 *
 * @return Selected frequency in selected unit
 *
 */
extern uint32 drv_CrpcGetFrequency(drv_CrpcFreqSelector freq, drv_CrpcClockUnitSelector unit);

/**
 * Get information about which register to write and value pattern to change the DXP divisor
 *
 * The 'value_pattern' is the pattern that needs to be updated with the divisor and then written to 'regaddr'
 *
 * @param regaddr :         Pointer where the address of the DXP div reg is written
 * @param value_pattern :   Pointer where the value pattern is written
 *
 * @return none
 *
 */
extern void drv_CrpcGetSetDxpDivisorInfo(uint32 *regaddr, uint32 *value_pattern);

/**
 * Modify the DXP divisor
 *
 * @param value_pattern :   Contents of the reg in which div will be replaced
 * @param dxp_div :         New DXP clock divisor
 *
 * @return none
 *
 */
extern void drv_CrpcSetDxpDivisor(uint32 value_pattern, uint32 dxp_div);

/**
 * Get the DXP div reg word updated with the specified divisor
 *
 * @param value_pattern :   Word to be modified
 * @param dxp_div       :   DXP div the word to be modified with
 *
 * @return Modified word
 *
 */
extern uint32 drv_CrpcGetSetDxpDivisorWordWithDivGiven(uint32 value_pattern, uint32 dxp_div);

/**
 * Save PLL and Clock Division settings before Power Down
 *
 * @return none
 *
*/
extern void drv_CrpcPowerDown(void);

/**
 *
 * Ensure CRPC settings are restored correctly after power down
 *
 * @return none
 *
*/
extern void drv_CrpcPowerUp(void);

/**
 * Returns post-hibernation DXP divisor.
 *
 * @param dxp_div Returns post-hib DXP divisor
 */
extern void drv_CrpcWakeupDiv(uint32 *dxp_div);

/**
 * Configure the CET Clock to be either from BBRF or from an external pin.
 *
 * @param source        CET Clock source
 *
 */
extern void drv_CrpcConfigureCetClock(drv_CrpcCetWdtClockSource source);

/**
 * Configure the WDT Clock to be either from BBRF or from an external pin.
 *
 * @param source        WDT Clock source
 *
 */
extern void drv_CrpcConfigureWdtClock(drv_CrpcCetWdtClockSource source);


#endif /* #ifndef DRV_CRPC_9XXX_H */

/** @} END OF FILE */

