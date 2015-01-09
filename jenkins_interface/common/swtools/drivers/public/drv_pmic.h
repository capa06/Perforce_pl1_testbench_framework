/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_pmic.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup PmicDriver PMIC Driver
 * @ingroup BoardLevelDrv
 */

/**
 * @addtogroup PmicDriver
 * @{
 */

/**
 * @file drv_pmic.h PMIC driver public interface
 *
 */

#ifndef DRV_PMIC_H
#define DRV_PMIC_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "os_abs.h"
#include "drv_xsi.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
/* Default Power amplifier levels */
#define DRV_PMIC_VCC_RF_PA_LOW_DEFAULT  3400
#define DRV_PMIC_VCC_RF_PA_HIGH_DEFAULT 3750

#define VCC_CORE_DONT_INITIALISE_DAC (0xffffffff)

#define DRV_SIG_PWR_MNGT_BASE_REQ 0x110 // TODO
#define DRV_SIG_PWR_MNGT_BASE_CNF 0x120 // TODO

#define DRV_PMIC_STATUS_OK (0)
#define DRV_PMIC_STATUS_NOK (10)

#define DRV_PMIC_DEFAULT_CB_VALUE ((uint32)-1)

/* LED params PMIC-independent shifts */
#define DRV_PMIC_LED_RATE_SHIFT (0)
#define DRV_PMIC_LED_DUTY_CYCLE_SHIFT (8)
#define DRV_PMIC_LED_PWM_SHIFT (16)
#define DRV_PMIC_LED_ON_SHIFT (24)
#define DRV_PMIC_LED_PARAM_MASK (0xff)

/* PMIC flags */
#define DRV_PMIC_FLAG_FORCE_DISABLE_AVS_ON_STARTUP           BIT(0)
#define DRV_PMIC_FLAG_FORCE_DISABLE_APM_ON_STARTUP           BIT(1)
#define DRV_PMIC_FLAG_AVS_STARTUP_WAIT_FOR_RF_DRIVER         BIT(2)
#define DRV_PMIC_FLAG_AVS_NO_INITIAL_MEASUREMENT             BIT(3)
#define DRV_PMIC_FLAG_EXTEND_APM_LOW_INTERVAL_SAFETY_MARGIN  BIT(4)
#define DRV_PMIC_FLAG_RESTORE_FULL_SPEED_ON_HIB_WAKEUP_EARLY BIT(5)

#define DRV_PMIC_DCDC(x)          (x)
#define DRV_PMIC_LDO(x)           ((x) | (1<<16))
#define DRV_PMIC_IS_LDO(x)        ((x) & (1<<16))
#define DRV_PMIC_IS_DCDC(x)       (!((x) & (1<<16)))
#define DRV_PMIC_LDO_DCDC_NUM(x)  (((x) & ~(1<<16))-1)
#define DRV_PMIC_LDO_DCDC_MAX     (16)
#define DRV_PMIC_VOLT_DEFAULT     (-1)

/** Platform specific PMIC flags.
    These options maybe PMIC specific. */
#define DRV_PMIC_FLAG_ECO_MODE                    (1 << 0)  /** ECO mode always on */
#define DRV_PMIC_FLAG_ECO_SLEEP_PWR_REQ           (1 << 1)  /** ECO mode on when SLEEP defined by PWR_REQ = L */
#define DRV_PMIC_FLAG_ECO_SLEEP_CLK_REQ           (1 << 2)  /** ECO mode on when SLEEP defined by CLK_REQ = L */
#define DRV_PMIC_FLAG_AUTO_PFM_MODE               (1 << 3)  /** DCDC in auto PFM/PWM mode */
#define DRV_PMIC_FLAG_FORCE_PWM_MODE              (1 << 4)  /** DCDC PWM mode forced always on */
#define DRV_PMIC_FLAG_BYPASS_ON_GSM               (1 << 5)  /** DCDC bypass mode when using GSM */
#define DRV_PMIC_FLAG_PFM_IN_3G_PWM_IN_GSM        (1 << 6)  /** DCDC in auto PFM mode in 3G, forced PWM mode in GSM */

/* DFLL platform-specific settings, special values */
#define DRV_PMIC_DFLL_SETTINGS_DEFAULT (-1)
#define DRV_PMIC_DFLL_SETTINGS_DEFAULT_VDD_STEP_SCALED (-2)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Power amplifier levels
 */
typedef enum
{
    DRV_PMIC_PA_LOW_LEVEL,
    DRV_PMIC_PA_HIGH_LEVEL
} drv_PmicPaLevel;

/**
 * RF DCDC
 */
typedef enum
{
    DRV_PMIC_RF_1V7,
    DRV_PMIC_RF_2V7
} drv_PmicRfDcDc;

/**
 * RF DCDC modes
 */
typedef enum
{
    DRV_PMIC_RF_MODE_PWM,
    DRV_PMIC_RF_MODE_PFM,
    DRV_PMIC_RF_MODE_UNKNOWN
} drv_PmicRfMode;

/**
 * Core voltage selection
 */
typedef enum
{
    DRV_PMIC_VCC_CORE_REQ_A,
    DRV_PMIC_VCC_CORE_REQ_B,
    DRV_PMIC_VCC_CORE_LEVELS
} drv_PmicVccCoreSel_t;


/**
 * ADC selection (max 8 ADC IDs)
 */
typedef enum
{
    DRV_PMIC_ADC_UNUSED0 = 0,
    DRV_PMIC_ADC_UNUSED1,
    DRV_PMIC_ADC_UNUSED2,
    DRV_PMIC_ADC_GSM_TEMP,
    DRV_PMIC_ADC_UNUSED4,
    DRV_PMIC_ADC_WCDMA_TEMP,
    DRV_PMIC_ADC_UNUSED6,
    DRV_PMIC_ADC_UNUSED7,
    DRV_PMIC_ADC_NUM,
    DRV_PMIC_ADC_PREVIOUSLY_REFERENCED = DRV_PMIC_ADC_NUM
} drv_PmicAdcId;


typedef enum
{
    SelVccRf,
    SelVcc3g1Rx,
    SelVcc3g2Rx,
    SelVccGsmRx,
    SelVcc3gTx,
    SelVccGsmTx,
    SelVccAnalog,
    SelVccVcxo,
    SelVccAux
} eSelRfVcc;


typedef enum
{
    DRV_PMIC_INIT_SEQ_DEFAULT = 0,
    DRV_PMIC_INIT_SEQ_COREVCC,
    DRV_PMIC_INIT_SEQ_PLATFORM,
    DRV_PMIC_INIT_SEQ_SIM,
    DRV_PMIC_INIT_SEQ_LED,
    DRV_PMIC_INIT_SEQ_RF,
    DRV_PMIC_INIT_SEQ_ADC,
    DRV_PMIC_INIT_SEQ_SDHC,
    DRV_PMIC_INIT_SEQ_PA,
    DRV_PMIC_INIT_SEQ_EFUSE
} tPowerMngtInitSequenceStage;


typedef enum
{
    DRV_PMIC_HIB_TYPE_PRE,
    DRV_PMIC_HIB_TYPE_POWER_UP,
    DRV_PMIC_HIB_TYPE_POST_FAILED_HIB,
    DRV_PMIC_HIB_TYPE_NB
} tPowerMngtHibCallType;


typedef enum
{
    /* 'treat' interface use */
    drv_powerMngtSetVccCoreReqA = DRV_SIG_PWR_MNGT_BASE_REQ,
    drv_powerMngtSetVccCoreReqB,
    drv_powerMngtSetSimVccReq,   /* voltage value in mV */
    drv_powerMngtPmicStartReq,
    drv_powerMngtGetAdcMeasureReq,
    drv_powerMngtSelectAdcMeasureReq,
    drv_powerMngtPollAdcComplete,
    drv_powerMngtLedReq,
    drv_powerMngtHibReq,
    /* 'query' interface use */
    drv_powerMngtQueryVccCoreParams,
    drv_powerMngtQueryVccCoreDacInitialSetting,
    drv_powerMngtQueryLdoConfigParams,
    drv_powerMngtQueryAbortVccCoreUpdate,
    drv_powerMngtSetSdhcVdd, /* voltage value in mV */
    drv_powerMngtConfigPa,   /* param1: high PA voltage in mV, param2: low PA voltage in mV */
    drv_powerMngtSetPa,      /* param1: 0 --> apply low voltage level, 1 --> apply high level voltage */
    drv_powerMngtSetPaVcc,    /* voltage value in mV */
    drv_powerMngtSetRfVoltage, /* param1: required DCDC param2: voltage in mV */
    drv_powerMngtSetRfMode,    /* param1: required DCDC param2: PWM/PFM mode */
    drv_powerMngtSetEfuseVcc,    /* turns on the efuse voltage to specified value */
    drv_powerMngtSetUsbPhySynopsysVcc, /* turns on/off the USB PHY Synopsys voltages */
    drv_powerMngtSetUsbPhyHsicVcc     /* turns on/off the USB HSIC voltage */
} tPowerMngtReqPrim;


/**
 * PMIC callback (not the same as I2C callback anymore)
 *
 * ctx: Its first argument is the context passed to PMIC driver with the callback
 * error: if 0 request was executed ok, otherwise an error  has occured
 * value: value returned for PMIC reads, -1 for PMIC writes
 */
typedef void (*drv_PmicCb)(void *ctx, int error, uint32 value);

/**
 * Params returned on core voltage query
 * voltages in mV
 * slew rates in 1/10th of mV/us
 * latencies in us
 * vdd step  in 1/10th of mV
 */
typedef struct
{
    uint32 min_voltage;
    uint32 max_voltage;
    uint32 vdd_step;
    uint32 slew_rate_up;
    uint32 slew_rate_down;
    uint32 additional_latency_full_channel;
    uint32 additional_latency_fast_channel;
    uint32 pmic_info_flags;
    char *pmic_description;
} drv_PmicCoreVoltageQueryParams;

/**
 * Params returned on LDO configuration query
 * voltages in mV
 */
typedef struct
{
    uint32 eco_mode;
    uint32 enabled;
    uint32 voltage;
    int    result;
} drv_PmicLdoConfigQueryParams;

typedef struct
{
    uint32 pmic_power_mgmt_dummy;
} tPowerMngtData;

typedef enum
{
    DRV_PMIC_MAXIM8994,
    DRV_PMIC_RD5T531,
    DRV_PMIC_TPS65912X,
    DRV_PMIC_TPS65912X_RF,
    DRV_PMIC_RD5T532,
    DRV_PMIC_TPS65712,
    DRV_PMIC_RT5017,
    DRV_PMIC_DISCRETE,
    DRV_PMIC_DUMMY,
    DRV_PMIC_AP_MAX77660,
    DRV_PMIC_AP_TPS80036,
    DRV_PMIC_CRPCPWM,
    DRV_PMIC_MAX
} tPmicId;

typedef enum
{
    DRV_PMIC_OUTPUT_DEFAULT,      /** Unchanged default for PMIC */
    DRV_PMIC_OUTPUT_OFF,          /** LDO / DCDC forced off */
    DRV_PMIC_OUTPUT_ON,           /** LDO / DCDC forced on */
    DRV_PMIC_OUTPUT_ON_CLK_REQ,   /** LDO / DCDC on with CLK_REQ (if supported by PMIC) */
    DRV_PMIC_OUTPUT_ON_PWR_REQ    /** LDO / DCDC on with PWR_REQ (if supported by PMIC) */
} tPowerMngtOutputEnable;

typedef struct {

  /* DCDC / LDO to be configured */
  int                     pmic_output;

  /* Enabled / Disabled / Enabled on PWR_REQ / Enabled on CLK_REQ */
  tPowerMngtOutputEnable  enable;

  /* Voltage A / Voltage H */
  int                     voltage_a;

  /* Voltage B / Voltage L (if supported by PMIC for this LDO/DCDC) */
  int                     voltage_b;

  /* Optional additional info flags */
  uint32                  flags;

} drv_PmicPlatformSettings;

/** PMIC Events API */
typedef enum
{
    DRV_PMIC_EVENT_SWITCH_GSM,
    DRV_PMIC_EVENT_SWITCH_3G,
    DRV_PMIC_EVENT_NUM,
} tPmicEvents;

/**
 *  Struct to set PMIC settings for a given platform: for
 *  each kind of supported treat order is associated a
 *  tPmicId.
 *  Such structure to be used at least once per platform in
 *  drivers/private/hwplatform/xxx/drv_hwplat_power.c in
 *  order to be shared with PMIC drivers at init.
 */
typedef struct
{
    tPmicId corevcc;
    tPmicId sim;
    tPmicId led;
    tPmicId rf;
    tPmicId adc;
    tPmicId sdhc;
    tPmicId pa;
    tPmicId efuse;
    tPmicId hsic;
    tPmicId synopsys;
} drv_PmicInterfaceSettings;

/**
 *  CRPC PWM settings
 */
typedef struct
{
    uint32 crpc_pwm_reverse_pwm_offset_direction;
    uint32 crpc_pwm_base_vdd_mv;
    uint32 crpc_pwm_vdd_step_10ths_of_mv;
} drv_PmicCrpcPwmSettings;

/**
 *  DFLL settings
 */
typedef struct
{
    int32 cg;
    int32 ci;
    int32 cf;
} drv_PmicDfllSettings;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 *  Initialise the PMIC driver
 */
extern void drv_pmic_start(void);

/**
 *  Initialise LEDs controlled by the PMIC driver.
 */
extern void drv_pmic_start_leds(void);

/*
    functions below always return 0 and always call the callback provided (if provided)
    note that the callback may be called with non-OK error status
    note also that if a callback isn't provided, the caller has no status info
*/


extern int drv_PowerMngtTrimVccCoreA(uint32 core_voltage, uint32 hib_voltage,
                                     drv_PmicCb callback, void * callback_param);
extern int drv_PowerMngtTrimVccCoreB(uint32 core_voltage,
                                     drv_PmicCb callback, void * callback_param);
extern int drv_PowerMngtAbortVccCore(uint32 *aborted);
extern int drv_PowerMngtVccCoreQuery(drv_PmicCoreVoltageQueryParams *core_vdd_params);
extern int drv_PowerMngtVccCoreDacInitialSettingQuery(uint32 * dac_initial_setting);
extern int drv_PowerMngtLdoConfigQuery(int ldo_id, drv_PmicLdoConfigQueryParams *ldo_config_params);

extern int drv_PowerMngtSetSimVcc(uint32 sim_voltage, uint32 simcp_support_voltage,
                                  drv_PmicCb callback, void *callback_param);

extern int drv_PowerMngtSetEfuseVcc(uint32 efuse_voltage, drv_PmicCb callback, void *callback_param);
extern int drv_PowerMngtSetUsbPhySynopsysVcc(uint32 enable, drv_PmicCb callback, void *callback_param);
extern int drv_PowerMngtSetUsbPhyHsicVcc(uint32 enable, drv_PmicCb callback, void *callback_param);

extern int drv_PowerMngtGetAdcMeasure(drv_PmicAdcId adc_id,
                                      drv_PmicCb callback, void *callback_param);

extern int drv_PowerMngtSelectAdc(drv_PmicAdcId adc_id, uint32 measurement_phase,
                                  drv_PmicCb callback, void *callback_param);

extern int drv_PowerMngtPollAdcComplete(drv_PmicCb callback, void *callback_param);

extern void drv_PmicHibernate(tPowerMngtHibCallType hib_call_type, tPowerMngtInitSequenceStage stage);

extern int drv_PowerMngtSetSdhcVdd(uint32 sdhc_voltage, drv_PmicCb callback, void *callback_param);

/**
 * If platform Power Amplifier is handled through PMIC.
 * Indicate here 2 voltage levels: high & low.
 *
 * PA voltage ouput is not modified.
 * Only level settings are stored.
 *
 * @param high_voltage_mv
 * @param low_voltage_mv
 *
 * @return int
 */
extern int drv_PowerMngtConfigPaVoltage(uint32 high_voltage_mv, uint32 low_voltage_mv);

/**
 * If platform Power Amplifier is handled through PMIC.
 * Set required output voltage: high or low previously set with
 * drv_PowerMngtConfigPaVoltage
 *
 * @param level DRV_PMIC_PA_LOW_LEVEL or DRV_PMIC_PA_HIGH_LEVEL
 * @param callback
 * @param callback_param
 *
 * @return int
 */
extern int drv_PowerMngtSetPaVoltage(uint32 level, drv_PmicCb callback, void * callback_param);

/**
 * If platform Power Amplifier is handled through PMIC.
 * Set required output voltage defined by voltage_mv
 *
 * @param voltage_mv
 * @param callback
 * @param callback_param
 *
 * @return int
 */
extern int drv_PowerMngtSetPaVoltageDirect(uint32 voltage_mv, drv_PmicCb callback, void * callback_param);

/**
 * Change RF DCDC mode.
 *
 * @param dcdc   valid drv_PmicRfDcDc
 * @param mode   valid drv_PmicRfMode
 * @param callback
 * @param callback_param
 *
 * @return int 0, status given to callback "error" parameter:
 *         DRV_PMIC_STATUS_NOK or DRV_PMIC_STATUS_OK
 */
extern int drv_PowerMngtSetRfMode(drv_PmicRfDcDc dcdc, drv_PmicRfMode mode, drv_PmicCb callback, void * callback_param);

/**
 * Change RF voltage for a given DCDC.
 *
 * @param dcdc  valid drv_PmicRfDcDc
 * @param voltage_mv
 * @param callback
 * @param callback_param
 *
 * @return int 0, status given to callback "error" parameter:
 *         DRV_PMIC_STATUS_NOK or DRV_PMIC_STATUS_OK
 */
extern int drv_PowerMngtSetRfVoltage(drv_PmicRfDcDc dcdc, uint32 voltage_mv, drv_PmicCb callback, void * callback_param);

/**
 * Set the required Efuse voltage
 *
 * @param efuse_mv
 * @param callback
 * @param callback_param
 *
 * @return int
 */
extern int drv_PowerMngtSetEfuseVoltage(uint32 efuse_mv, drv_PmicCb callback, void * callback_param);

/**
 * Some PMICs allow adjustment of the PA voltage which is to be controlled from RF driver (DXP0).
 * For SPI devices, the data to be sent for a voltage request can be generated using this function
 * and then sent on a secondary FSI channel to the SPI PMIC from the RF driver.
 * This function must take very little time.
 *
 * @param vccSel    Which voltage level (low / high) value (0 or 1) is this request for.
 * @param mV        Voltage request in mV.
 * @return          32-bit Spi word for register write command.
 */
extern uint32 drv_PowerMngtGeneratePaVoltageCommand(int vccSel, uint32 mV);

/**
 * For SPI PMICs which allow adjustment of the PA voltage, retrieve the high priority
 * FSI FIFO address.
 *
 * @return          Address of SPI FIFO.
 */
extern uint32 drv_PowerMngtGetSpiFifoAddr(void);

/**
 * Get the ID of the FSI interface in use.
 * Safe from DXP0 or DXP1
 *
 * @return              : mphalfsit_FsiID
 */
extern drv_XsiDeviceId drv_PowerMngtGetSpiFsiId(void);

/**
 * Apply platform/board rev specific PMIC DCDC/LDO settings.
 * 'table' is the configuration table which contains the platform specific
 * settings which may contain one or more PMIC specific setup tables.
 *
 * @param table           Configuration table
 * @param callback        pmic callback
 * @param callback_param  callback parameters
 */
extern void drv_PmicApplyPlatformSettings(const drv_PmicPlatformSettings table[][DRV_PMIC_LDO_DCDC_MAX],
                                   drv_PmicCb callback, void * callback_param);

/**
 * Build a list of SPI writes to perform a specific action.
 * DXP0 & DXP1 safe.
 *
 * @param ev            Event to generate writes for
 * @param buffer        Target buffer to fill
 * @param maxWrites     Max number of words to write to buffer
 *
 * @return int:         Number of 32-bit words in buffer
 */
extern int drv_PmicGenerateEventSpiWrites(tPmicEvents ev, uint32 *buffer, int maxWrites);

/**
 * Debug register read access.
 *
 * @param addr            Register address
 * @return                Register contents
 */
extern uint32 drv_PmicDebugReadRegister(uint32 addr);

/**
 * Debug register write access.
 *
 * @param addr            Register address
 * @param value           Register value to write
 */
extern void drv_PmicDebugWriteRegister(uint32 addr, uint32 value);

/**
 * Initiate a PMIC shutdown
 */
extern void drv_PmicShutdown(void);

#endif
/** @} END OF FILE */
