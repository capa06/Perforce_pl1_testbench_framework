/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_clocks.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ClocksDriver
 * @{
 */

/**
 * @file drv_clocks.h functions definitions for Clocks
 *
 */

#ifndef DRV_CLOCKS_H
#define DRV_CLOCKS_H

/******************************************************************************
 * Include Files
 ******************************************************************************/
#ifndef HOST_TESTING
#include "mphal_powerclk.h"
#else
#include <ht_stub.h>
#endif
#include "drv_crpc.h"
#include "drv_mclk_selection.h"

/******************************************************************************
 * Constants
 ******************************************************************************/

#define DRV_CET_CLK_SPEED_HZ   DRV_CET_CLK_SPEED
#define DRV_CET_CLK_SPEED_KHZ (DRV_CET_CLK_SPEED/DRV_CRPC_KHZ)

/* Minimum PLL VCO output frequency */
#define DRV_CLOCKS_MIN_PLL_VCO_OUT_KHZ (680000)

/******************************************************************************
 * Exported macros
 ******************************************************************************/

/******************************************************************************
 * Exported types
 ******************************************************************************/

typedef enum {
    DRV_CLOCK_USIPHY_USIPHY0_DIV  = CRPC_REGS_USI_CLK_SELECT_PHY0_USI_PHY0_DIV,
    DRV_CLOCK_USIPHY_USIPHY1_DIV  = CRPC_REGS_USI_CLK_SELECT_PHY0_USI_PHY1_DIV,
    DRV_CLOCK_USIPHY_USIPHY2_DIV  = CRPC_REGS_USI_CLK_SELECT_PHY0_USI_PHY2_DIV,
    DRV_CLOCK_USIPHY_AUDIO_GUT    = CRPC_REGS_USI_CLK_SELECT_PHY0_AUDIO_GUT
} drv_ClocksUsiPhyClockSelection;

typedef enum {
    DRV_CLOCK_CLKOUTDEBUG_CONV   = CRPC_REGS_CLKOUT_DEBUG_SELECT_CONV,
    DRV_CLOCK_CLKOUTDEBUG_AUDIO  = CRPC_REGS_CLKOUT_DEBUG_SELECT_AUDIO,
    DRV_CLOCK_CLKOUTDEBUG_DFLL   = CRPC_REGS_CLKOUT_DEBUG_SELECT_DFLL,
    DRV_CLOCK_CLKOUTDEBUG_PMU    = CRPC_REGS_CLKOUT_DEBUG_SELECT_PMU,
    DRV_CLOCK_CLKOUTDEBUG_NO_DEBUG_CLOCK
} drv_ClocksClkoutDebugClockSelection;


/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Initializes the Clocks driver
 * BBRF clock is started at speed which is safe for default voltage (240 MHz)
 *
 * @param hib_reinit  0 on cold boot, !=0 on hib power up
 *
 */
extern void drv_ClocksInit( uint32 hib_reinit );

/**
 * BBRF clock is (re)started at high speed (480 MHz)
 * Note: this function is intended to be used at cold/warm boot only
 *       For "on the fly" BBRF switching use drv_ClocksSetupBbrfFrequencyStart/Complete
 *
 */
extern void drv_ClocksBbrfSetHighSpeed(void);

/**
 * Request pre-div B clock
 *
 * @param pll_selection        PLL selection (main/app)
 * @param divider_in_halves    Divider to apply (in 1/2 units)
 *
 */
extern void drv_ClocksRequestPredivBClk(mphalt_PLLKind pll_selection, uint32 divider_in_halves);

/**
 * Request HSIC clock.
 *
 * @param pll_selection        PLL selection (main/app)
 * @param divider_in_halves    Divider to apply (in 1/2 units)
 *
 */
extern void drv_ClocksRequestHsicClk(mphalt_PLLKind pll_selection, uint32 divider_in_halves);

/**
 * Request a specific secondary clock
 *
 * @param output        Select which secondary divisor output to request
 * @param source        Select which source to apply to clock output
 * @param divider       Divider to apply
 *
 */
extern void drv_ClocksRequestSecondaryClock(drv_CrpcSecondaryClockOutputs output,
                                            drv_CrpcSecondaryClockMuxSelections source,
                                            uint32 divider);

/**
 * Temporarily disable a specific secondary clock, to save power.
 * NOTE: This clock must have been initialised prior to calling this function.
 *
 * @param output        Select which secondary divisor output to disable
 */
extern void drv_ClocksDisableSecondaryClock(drv_CrpcSecondaryClockOutputs output);

/**
 * Select a specific USI PHY clock output
 *
 * @param phy_clock_id  Select which USI PHY clock output to select
 * @param source        Select which source to select for specified USI PHY output
 *
 */
extern void drv_ClocksSelectUsiPhyClock(uint32 phy_clock_id, drv_ClocksUsiPhyClockSelection source);

/**
 * Select a debug clock for out clocks
 *
 * @param out_clock_id  Select which CLKOUT clock to select
 * @param source        Select which debug source to select for specified CLKOUT
 *
 */
extern void drv_ClocksSelectClkoutDebugClock(uint32 out_clock_id, drv_ClocksClkoutDebugClockSelection source);

/**
 * Get the speed of CET input clock
 *
 * @return CET input clock speed in Hz
 *
 */
extern uint32 drv_ClocksGetCetInputClockSpeed(void);

/**
 * Start BBRF clock frequency change
 * (including all things that need to be done, like freq floor change)
 * drv_ClocksSetupBbrfFrequencyStart must always be followed by drv_ClocksSetupBbrfFrequencyComplete
 * This function doesn't block
 * Warning: this function will initiate calls to other DXPs
 *
 * @param requested_bbrf_clk_khz Requested BBRF clock speed
 * @return void.
 *
 */
extern void drv_ClocksSetupBbrfFrequencyStart(uint32 requested_bbrf_clk_khz);

/**
 * Query completion / complete BBRF clock frequency change
 * drv_ClocksSetupBbrfFrequencyComplete must always be preceded by drv_ClocksSetupBbrfFrequencyStart
 * This function doesn't block
 *
 * @return 0 if not complete yet. !=0 if complete: actual BBRF clock configured (in kHz)
 *
 */
extern uint32 drv_ClocksSetupBbrfFrequencyComplete(void);

/**
 * Set the SoC clock to an appropriate frequency to be used
 * during customer fusing
 *
 * @return void.
 *
 */
extern void drv_ClocksSelectFusingSocClock(uint32 *pre_div, uint32 *pre_src);

#endif /* #ifndef DRV_CLOCKS_H */

/** @} END OF FILE */
