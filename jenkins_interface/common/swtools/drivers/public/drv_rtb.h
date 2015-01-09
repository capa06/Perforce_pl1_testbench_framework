/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_rtb.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup RtbDriver RTC-CET Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup RtbDriver
 * @{
 */

/**
 * @file drv_rtb.h RTC-CET public interface
 *
 */

#ifndef DRV_RTB_H
#define DRV_RTB_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"
#ifndef HOST_TESTING
#include "mphal_gut.h"
#endif
#include "drv_global.h"

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define WAKEUP_REG_RAM_RAMCFG_WIDTH             (3)
#define WAKEUP_REG_RAM_RAMCFG_SHIFT             (0)
#define WAKEUP_REG_RAMCFG_MASK          ((1<< WAKEUP_REG_RAM_RAMCFG_WIDTH)-1)

#define WAKEUP_REG_RAM_SDRAM_MASK (1<<2)            /* if 0 SDRAM, if 1 CRAM */

#define WAKEUP_REG_SDRAM_RSVD       (0)             /* no known RAM Cold boot */
#define WAKEUP_REG_SDRAM_16BITS     (1)             /* SDRAM 16 bits */
#define WAKEUP_REG_SDRAM_32BITS     (2)             /* SDRAM 16 bits */
#define WAKEUP_REG_SDRAM_DDR_16BITS (3)             /* DDR SDRAM 16 bits */

#define WAKEUP_REG_CRAM_16BITS_NON_MUXED    (4)     /* CRAM 16 bits non-muxed*/
#define WAKEUP_REG_CRAM_16BITS_MUXED        (5)     /* CRAM 16 bits muxed*/
#define WAKEUP_REG_CRAM_32BITS_MUXED        (6)     /* CRAM 32 bits: muxed */
#define WAKEUP_REG_CRAM_RSVD                (7)     /* reserved */

#define WAKEUP_REG_XTAL_FREQ_WIDTH              (3)
#define WAKEUP_REG_XTAL_FREQ_SHIFT  (WAKEUP_REG_RAM_RAMCFG_WIDTH+WAKEUP_REG_RAM_RAMCFG_SHIFT)
#define WAKEUP_REG_XTAL_FREQ_MASK   ((1<< WAKEUP_REG_XTAL_FREQ_WIDTH)-1)

#define WAKEUP_REG_XTAL_FREQ_26MHZ      (0)
#define WAKEUP_REG_XTAL_FREQ_15P36MHZ   (1)
#define WAKEUP_REG_XTAL_FREQ_19P2MHZ    (2)
#define WAKEUP_REG_XTAL_FREQ_38P4MHZ    (3)
#define WAKEUP_REG_XTAL_FREQ_52MHZ      (4)

#define WAKEUP_REG_DXP_FREQ_WIDTH               (2)
#define WAKEUP_REG_DXP_FREQ_SHIFT       (WAKEUP_REG_XTAL_FREQ_WIDTH+WAKEUP_REG_XTAL_FREQ_SHIFT)
#define WAKEUP_REG_DXP_FREQ_MASK        ((1<< WAKEUP_REG_DXP_FREQ_WIDTH)-1)

#define WAKEUP_REG_DXP_FREQ_300MHZ (0)
#define WAKEUP_REG_DXP_FREQ_312MHZ (1)
#define WAKEUP_REG_DXP_FREQ_332MHZ (2)

#define WAKEUP_REG_SOC_DIV_INC_WIDTH            (2)
#define WAKEUP_REG_SOC_DIV_INC_SHIFT    (WAKEUP_REG_DXP_FREQ_SHIFT+WAKEUP_REG_DXP_FREQ_WIDTH)
#define WAKEUP_REG_SOC_DIV_INC_MASK     ((1<< WAKEUP_REG_SOC_DIV_INC_WIDTH)-1)

#define WAKEUP_REG_CAS_LATENCY_WIDTH            (3)
#define WAKEUP_REG_CAS_LATENCY_MASK     ((1<< WAKEUP_REG_CAS_LATENCY_WIDTH)-1)
#define WAKEUP_REG_CAS_LATENCY_SHIFT    (WAKEUP_REG_SOC_DIV_INC_SHIFT+WAKEUP_REG_SOC_DIV_INC_WIDTH)

#define WAKEUP_REG_DRAM_COL_W_WIDTH             (2)
#define WAKEUP_REG_DRAM_COL_W_MASK      ((1<< WAKEUP_REG_DRAM_COL_W_WIDTH)-1)
#define WAKEUP_REG_DRAM_COL_W_SHIFT     (WAKEUP_REG_CAS_LATENCY_SHIFT+WAKEUP_REG_CAS_LATENCY_WIDTH)

#define WAKEUP_REG_DRAM_ROW_W_WIDTH             (2)
#define WAKEUP_REG_DRAM_ROW_W_MASK      ((1<< WAKEUP_REG_DRAM_ROW_W_WIDTH)-1)
#define WAKEUP_REG_DRAM_ROW_W_SHIFT     (WAKEUP_REG_DRAM_COL_W_SHIFT+WAKEUP_REG_DRAM_COL_W_WIDTH)

#define WAKEUP_REG_DRAM_BRCnRBC_WIDTH           (1)
#define WAKEUP_REG_DRAM_BRCnRBC_MASK    ((1<< WAKEUP_REG_DRAM_BRCnRBC_WIDTH)-1)
#define WAKEUP_REG_DRAM_BRCnRBC_SHIFT   (WAKEUP_REG_DRAM_ROW_W_SHIFT+WAKEUP_REG_DRAM_ROW_W_WIDTH)

#define WAKEUP_REG_CFG_INDEX_WIDTH              (3)
#define WAKEUP_REG_CFG_INDEX_MASK       ((1<<WAKEUP_REG_CFG_INDEX_WIDTH)-1)
#define WAKEUP_REG_CFG_INDEX_SHIFT      (WAKEUP_REG_DRAM_BRCnRBC_SHIFT + WAKEUP_REG_DRAM_BRCnRBC_WIDTH)

#define WAKEUP_REG_BOOT_SIGNIFICANT_WIDTH   (WAKEUP_REG_CFG_INDEX_SHIFT+WAKEUP_REG_CFG_INDEX_WIDTH)
#define WAKEUP_REG_BOOT_SIGNIFICANT_MASK    ((1<<WAKEUP_REG_BOOT_SIGNIFICANT_WIDTH)-1)

/* WakeUp[30:31] */
#define WAKEUP_REG_SW_RESET_REQ_WIDTH           (2)
#define WAKEUP_REG_SW_RESET_REQ_MASK    ((1<<WAKEUP_REG_SW_RESET_REQ_WIDTH)-1)
#define WAKEUP_REG_SW_RESET_REQ_SHIFT           (30)

/** Rough conversion from 32kHz ticks to µs, safe on a 32-bit variable containing a 20-bit value */
#define DRV_RTB_ROUGH_20BIT_TS_TO_US(x) (((x) * 3906) >> 7)

/** External Wakeup Offsets */
enum eDrvRtbExtWake
{
    DRV_RTB_EXTWAKE0,
    DRV_RTB_EXTWAKE1,
    DRV_RTB_EXTWAKE2,
    DRV_RTB_EXTWAKE3,
    DRV_RTB_EXTWAKE4,
    DRV_RTB_EXTWAKE5,
    DRV_RTB_EXTWAKE6,
    DRV_RTB_EXTWAKE7,
    DRV_RTB_EXTWAKE8,
    DRV_RTB_EXTWAKE9,
    DRV_RTB_EXTWAKE10,
    DRV_RTB_EXTWAKE11,
    DRV_RTB_EXTWAKE12,
    DRV_RTB_EXTWAKE13,
    DRV_RTB_EXTWAKE14,
    DRV_RTB_EXTWAKE15,
    DRV_RTB_EXTWAKE16,
    DRV_RTB_EXTWAKE17,
    DRV_RTB_EXTWAKE18,
    DRV_RTB_EXTWAKE19,
    DRV_RTB_EXTWAKE20,
    DRV_RTB_EXTWAKE21,
    DRV_RTB_EXTWAKE22,
    DRV_RTB_EXTWAKE23,
    DRV_RTB_EXTWAKE24,
    DRV_RTB_EXTWAKE25,
    DRV_RTB_EXTWAKE26,
    DRV_RTB_EXTWAKE27,
    DRV_RTB_EXTWAKE28,
    DRV_RTB_EXTWAKE29,
    DRV_RTB_EXTWAKE30,
    DRV_RTB_EXTWAKE31,
    DRV_RTB_EXTWAKE32
};

#if defined (ICE9XXX_PMSS)
/**    9040 External Wakes. */
#define DRV_RTB_EXTWAKE_NONE                    DRV_RTB_EXTWAKE32
#endif

/** External Wakeup Polarity active Low - Need to be shifted by according offset */
#define DRV_RTB_EXTWAKE_ACTIVE_LOW              (1)
/** External Wakeup Polarity active High */
#define DRV_RTB_EXTWAKE_ACTIVE_HIGH             (0)

/* The counter width and maximum count for RTC-LSB.
*/
#define DRV_RTB_LSB_COUNTER_WIDTH     (20)
#define DRV_RTB_LSB_MAX_COUNTER_VALUE ((1 << DRV_RTB_LSB_COUNTER_WIDTH) - 1)

/*
 * The RTC-LSB threholds which can be configured to raise a SIC trigger or a WAKE.
*/
#define DRV_RTB_LSB_SIC_THRESHOLD  (0)
#define DRV_RTB_LSB_WAKE_THRESHOLD (1)
#ifdef ICE9XXX_BBMCI
#define DRV_RTB_LSB_MEMREQSOON_THRESHOLD (2)
#endif

/**
 * Approximate RTC freq - actual frequency varies with temp,
 * etc.
 */
#define DRV_RTB_FREQ (32768)

/**
 * Approximate ms -> RTB LSB ticks
 */
#define DRV_RTB_MS_TO_TICKS(ms)           (((ms) * DRV_RTB_FREQ) / 1000)

 /**
  * Approximate us -> RTB LSB ticks
  */
 #define DRV_RTB_US_TO_TICKS(us)           (((us) * DRV_RTB_FREQ) / 1000000)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Warm boot information
 */
typedef struct
{
    int ram_type;
    int xtal_freq_code;
    int fvco_freq_code;
    int extra_soc_div;
    int sdram_row_width;
    int sdram_col_width;
    int sdram_cas_latency;
    int sdram_brc_nrbc;
    int efuse_config_index;
} tMinimalWarmBootData;

/**
 * Last reset causes
 */
typedef enum
{
    DRV_RTB_RESET_SRC_RTB = 0,  /* Last reset source was RTB reset pin (RTB_ON) */
    DRV_RTB_RESET_SRC_POR = 1,  /* Last reset source was SYSTEM reset pin (POR_N) */
    DRV_RTB_RESET_SRC_WDT = 2,  /* Last reset source was Watchdog Timer */
    DRV_RTB_RESET_SRC_TAP = 3,  /* Last reset source was TAP port (not used on Vivalto) */
    DRV_RTB_RESET_SRC_CRPC = 4, /* Last reset source was CRPC (hibernate) */
    DRV_RTB_RESET_SRC_NUM
} drv_RtbLastResetSrc;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
#ifndef HOST_TESTING
extern mphalgutt_Handle DXP_UNCACHED *drv_rtb_rtblsb;
#endif

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize RTB driver
 *
 */
void drv_RtbInit(void);

/**
*   drv_RtbLsbCheckWrap
*
*   The RTC 32768Hz is configured to wrap at the maximum RTC counter value (2^20) and will consequently
*   wrap every 32 seconds. When a wrap occurs, the 64-bit RTC timestamps must be increased by 2^20 ticks.
*   This function must be called periodically, with a period shorter than 32 seconds, in order to check
*   for a RTC counter wrap. This scheme is preferred to registering a RTC wrap interrupt handler as it
*   does not rely on an interrupt to fire and does not preempt/delay high-priority processing in PL1
*
*   pre  : called as part of a GUT 10ms tick handler
*   post : no return value
*/
void drv_RtbLsbCheckWrap(void);

/**
*   drv_RtbLsbGet20BitTimestamp
*
*   Return the 20-bit RTC timestamp, this function
*   can be called on any DXP
*
*   pre  :
*   post : 20-bit timestamp (wraps every 32 seconds!)
*/
uint32 drv_RtbLsbGet20BitTimestamp(void);

/**
*   drv_RtbLsbGet64BitTimestamp
*
*   Return the 64-bit RTC timestamp, this function
*   must be called on DXP0 only
*
*   pre  :
*   post : 64-bit timestamp
*/
uint64 drv_RtbLsbGet64BitTimestamp(void);

/**
 * drv_RtbLsbGet64BitTimestampSafe
 *
 * Multiple DXP safe version of drv_RtbLsbGet64BitTimestamp which will return 0
 * on error (if no RTB GUT handle is open).
 */
uint64 drv_RtbLsbGet64BitTimestampSafe(void);

/**
 * drv_RtbLsbGetThreshold
 *
 * Return the value of the specified threshold
 *
 * @param threshold Threshold ID
 */
uint32 drv_RtbLsbGetThreshold(uint32 threshold);

/**
 * drv_RtbLsbSetThreshold
 *
 * @param count Counter value to set threshold to
 * @param threshold Threshold ID
 */
void drv_RtbLsbSetThreshold(uint32 count, uint32 threshold);

/**
 * drv_RtbLsbSetEventMask
 *
 * @param mask Value event mask to set
 */
void drv_RtbLsbSetEventMask(uint32 set_mask);

/**
 * drv_RtbLsbSetEvent
 *
 * @param mask threshold Threshold ID
 */
void drv_RtbLsbSetEvent(uint32 threshold);

/**
 * drv_RtbLsbClearEventMask
 *
 * @param mask Value event mask to clear
 */
void drv_RtbLsbClearEventMask(uint32 clear_mask);

/**
 * drv_RtbLsbSetSICMask
 *
 * @param index SIC index
 * @param enableNotDisable set to !0 to enable
 */
void drv_RtbLsbSetSICMask(uint32 index, uint32 enableNotDisable);

/**
 * drv_RtbLsbSetInterruptEnable
 *
 * @param threshold ID of threshold to enable/disable
 * @param enableNotDisable set to !0 to enable
 */
void drv_RtbLsbSetInterruptEnable(uint32 threshold, uint32 enableNotDisable);

/**
 * Initialize RTB Wake on External Event
 *
 * @param io                  I/O offset (use
 *                            DRV_RTB_EXTWAKEx_xxx definitions)
 * @param enable              zero: disable, non-zero value:
 *                            enable
 * @param level               Polarity for wakeup
 *
 */
void drv_RtbSetupExtwakeEvent(  uint8 io,
                                uint8 enable,
                                uint8 level);

/**
 * Get the current RTB Extwake active events
 *
 * @return The currently active RTB ExtWake events
 *
 */
uint32 drv_RtbGetActiveEvents( void );

/**
 * Get the current RTB Extwake active events at power up,
 * i.e. immediately after hibernate
 *
 * @return The active RTB ExtWake events immediately after
 *         hibernate
 *
 */
uint32 drv_RtbGetActiveEventsAtPowerUp( void );

/**
 * Enable Wakeup on external event
 *
 * @param io                  I/O offset (use
 *                            DRV_RTB_EXTWAKEx_xxx definitions)
 */
void drv_RtbWaitExtwakeEventEnable( uint8 io );

/**
 * Disable Wakeup on external event
 *
 * @param io                  I/O offset (use
 *                            DRV_RTB_EXTWAKEx_xxx definitions)
 */
void drv_RtbWaitExtwakeEventDisable( uint8 io );

/**
 * Set Paging timeout
 * @param timout_us
 * @return void
 */
void drv_RtcLsbSetPagingTimeout(int timout_us);

/**
 * Set CET Ctrl timeout
 * @param timout_us
 * @return void
 */
void drv_RtcLsbSetCetCtrlTimeout(int timout_us);

/**
 * Set wake control parameters
 *
 * @param soc_reset_enable
 * @param clk_req_enable
 * @param pwr_req_enable
 * @param pwr_wake_b4_clk_wake
 * @param freeze_by_rtb_allowed
 */
void drv_RtbWakeCtrl(int soc_reset_enable,
                     int clk_req_enable,
                     int pwr_req_enable,
                     int pwr_wake_b4_clk_wake,
                     int freeze_by_rtb_allowed);

/**
 * Read External Wake input Control register
 *
 * @return      External wake input control register
 *
 */
uint32 drv_RtbGetExtWakeCtrl(void);

/**
 * Set the indicated RTB_HOST_WAKEUP_CTRL bits
 * 1 sets the bit
 * 0 leaves the bit as it is
 *
 * @param soc_reset_enable
 * @param clk_req_enable
 * @param pwr_req_enable
 * @param pwr_wake_b4_clk_wake
 * @param freeze_by_rtb_allowed
 *
 * @return void
 */
void drv_RtbWakeCtrlSet(int soc_reset_enable,
                        int clk_req_enable,
                        int pwr_req_enable,
                        int pwr_wake_b4_clk_wake,
                        int freeze_by_rtb_allowed);

/**
 * Clear the indicated RTB_HOST_WAKEUP_CTRL bits
 * 1 clears the bit
 * 0 leaves the bit as it is
 *
 * @param soc_reset_enable
 * @param clk_req_enable
 * @param pwr_req_enable
 * @param pwr_wake_b4_clk_wake
 * @param freeze_by_rtb_allowed
 *
 * @return void
 */
void drv_RtbWakeCtrlClear(int soc_reset_enable,
                          int clk_req_enable,
                          int pwr_req_enable,
                          int pwr_wake_b4_clk_wake,
                          int freeze_by_rtb_allowed);

/**
 * Programs 32kHz RTB clock
 *
 * @param clkout32k_en      TBD
 * @param clkout32k_filter  TBD
 *
 */
void drv_Rtb32khzCtrl(int clkout32k_en,
                      int clkout32k_filter);

/**
 * Determine whether we restarted from cold boot or not.
 * @return true when coming from cold boot
 */
bool drv_RtbComingFromColdBoot(void);

/**
 * RTB_HOST_WAKEUP_REG_RD
 *
 * @return Wakeup Register value (Read-Only)
 */
uint32 drv_RtbReadWakeupRoReg(void);

/**
 * RTB_HOST_WAKEUP_REG
 *
 * @return register
 */
uint32 drv_RtbReadWakeupReg(void);

/**
 * write RTB_HOST_WAKEUP_REG
 * @param val Value to write to Wakeup register
 * @return
 */
void drv_RtbWriteWakeupReg(uint32 val);

/**
 * Is non-DDR I/O frozen?
 * 90xx only.
 * @return 1 if I/O frozen, 0 if not.
 */
#ifdef ICE9XXX_PMSS
int drv_RtbIsIoFrozen(void);
#endif

/**
 * Request wakeup mode and reset
 *
 * @param mode      Firmware mode to switch to
 */
void DXP_NEVER_RETURNS drv_RtbForceWakeupToFirmwareMode( drv_FirmwareRtbMode mode );

/**
 * Returns wakeup register value to be set.
 *
 * @param       firmware value
 * @return      wakeup register value
 */
drv_FirmwareRtbMode drv_RtbFirmwareModeToRtbMode( drv_Firmware firmware );

/**
 * Set the SW_RESET field in the RTB_HOST_WAKEUP_REG
 *
 */
void drv_RtbSetWakeupSWReset( uint32 value );

/**
 * Return the SW_RESET field in the RTB_HOST_WAKEUP_REG
 *
 */
uint32 drv_RtbGetWakeupSWReset(void);

/**
 * Initiate HW reset
 * @return
 */
void DXP_NEVER_RETURNS drv_RtbHwReset(void);

/**
 * Initiate SW reset
 * @param keep_core_pw keep core powered during reset
 * @return
 */
void DXP_NEVER_RETURNS drv_RtbSwReset(int keep_core_pw);

/**
 * write RTB_HOST_WAKEUP_REG
 * @param power_or_clk_timer
 * @param dxp_out_of_reset_timer
 * @param pll_locked_reset
 * @param wait_for_32kHz_domain_write
 * @return
 */
void drv_RtbWutSetTimer(    int power_or_clk_timer,
                               int dxp_out_of_reset_timer,
                               int pll_locked_reset,
                               bool wait_for_32kHz_domain_write) ;

/**
 * Initialise SW Reset lock
 *
 * @return
 */
void drv_RtbInitSwResetLock(void);

/**
 * Powers down RTB module
 *
 */
void drv_RtbPowerDown(void);

/**
 * Powers up RTB module
 *
 */
void drv_RtbPowerUp(void);

/**
 * Returns last reset source
 * @return Last reset source
 */
drv_RtbLastResetSrc drv_RtbGetLastResetSrc(void);

/**
 * Setup the RTB WAKEUP GUT
 * @param cold_boot - Is this being done on cold-boot
 */
void drv_RtbSetupWakeupGut(int cold_boot);

/**
 * Setup the RTB HOST WAKEUP Control register
 * @param value - Register value
 */
void drv_RtbSetupHostWakeupCtrl(uint32 value);

#endif /* #ifndef DRV_RTB_H */

/** @} END OF FILE */
