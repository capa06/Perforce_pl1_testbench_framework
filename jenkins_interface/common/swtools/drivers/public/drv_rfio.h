/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_rfio.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup RfioDriver RFIO Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup RfioDriver
 * @{
 */

/**
 * @file drv_rfio.h RF IO driver external interface
 *
 */

#ifndef DRV_RFIO_H
#define DRV_RFIO_H

#include "icera_global.h"
#include "drv_temperature.h"

/******************************************************************************
 * Macros
 ******************************************************************************/

#define RFIO_DCXO_FITTED(dcxo)      drv_rfio_DCXOFitted(dcxo)
#define RFIO_THERMISTOR_FITTED(adc) drv_rfio_TemperatureSensorValid(adc)
#define RFIO_3G_SENSOR(band, adc)   drv_rfio_3gTemperatureSensor(band, adc)
#define RFIO_2G_SENSOR(band, adc)   drv_rfio_2gTemperatureSensor(band, adc)
#define RFIO_AFC_SENSOR(adc)        drv_rfio_AfcTemperatureSensor(adc)
#define RFIO_3G_RXTX_DELAY(band, x) drv_rfio_3gRxTxDelay(band, x)
#define RFIO_2G_RXTX_DELAY(x)       drv_rfio_2gRxTxDelay(x)
#define RFIO_2G_RAMP_LINEAR(x)      drv_rfio_2gRampLinear(x)
#define RFIO_3G_PORT(band, port)    drv_rfio_3gPort(band, port)
#define RFIO_2G_PORT(band, port)    drv_rfio_2gPort(band, port)
#define RFIO_TEMP_REF(adc, ref)     drv_rfio_TempRef(adc, ref)
#define RFIO_VOLT_REF(adc, ref)     drv_rfio_VoltRef(adc, ref)
#define RFIO_SYSCLK(x)              drv_rfio_sysclk(x)
#define RFIO_VBAT_CONFIG(adc, scale, shift)      drv_rfio_VbatConfig(adc, scale, shift);
#define RFIO_VSYS_CONFIG(adc, scale, shift)      drv_rfio_VsysConfig(adc, scale, shift);
#define RFIO_2G_VBAT_HEADROOM(headroom)          drv_rfio_2GVBatHeadroom(headroom);
#define RFIO_3G_VBAT_HEADROOM(headroom)          drv_rfio_3GVBatHeadroom(headroom);
#define RFIO_2G_CLASS_PWR_BACKOFF(start, slope)  drv_rfio_2GClassPwrBackoff(start, slope);
#define RFIO_3G_CLASS_PWR_BACKOFF(start, adc_cal_voltage_mV, class_pwr_hysteresis)  drv_rfio_3GClassPwrBackoff(start, adc_cal_voltage_mV, class_pwr_hysteresis);
#define RFIO_3G_VBAT_HYSTERESIS(hysteresis_limit)               drv_rfio_3GVbattHysteresis(hysteresis_limit);
#define RFIO_IO_CONFIG(band, sig, port, pos, width, mask, val)  drv_rfio_RfIoConfigure(band, sig, port, pos, width, mask, val)
#define RFIO_3G_MULTI_RFIC(band, direction, device)             drv_rfio_RfConfigMultiple3GChip(band, direction, device)
#define RFIO_2G_MULTI_RFIC(band, direction, device)             drv_rfio_RfConfigMultiple2GChip(band, direction, device)

#define ADC_NB  2   // max number of ADCs available to configure

/******************************************************************************
 * Exported types
 ******************************************************************************/
 /*
 * RF IO enumerations
 */

/* public enumeration of the RF GSM TX bands */
typedef enum
{
    DRV_RF_GSM_850  = 0,
    DRV_RF_GSM_900,
    DRV_RF_GSM_1800,
    DRV_RF_GSM_1900,
    DRV_RF_GSM_NOT_VALID,
    DRV_RF_GSM_NB = DRV_RF_GSM_NOT_VALID
} drv_RfGsmBandsEnum;

/* public enumeration of the RF GSM paths */
typedef enum
{
    DRV_RF_GSM_PATH_TX_GMSK = 0,
    DRV_RF_GSM_PATH_TX_8PSK,
    DRV_RF_GSM_PATH_RX,
    DRV_RF_GSM_PATH_NB
} drv_RfGsmPathEnum;

/*
 * Public enumeration of 3G bands - same as sys/common/com_3gpp.h so MUST be
 * kept in sync with that type but we cannot have a dependency on sys/common files
 */
typedef enum
{
    DRV_RF_3G_BAND_I = 0,
    DRV_RF_3G_BAND_II,
    DRV_RF_3G_BAND_III,
    DRV_RF_3G_BAND_IV,
    DRV_RF_3G_BAND_V,
    DRV_RF_3G_BAND_VI,
    DRV_RF_3G_BAND_VII,
    DRV_RF_3G_BAND_VIII,
    DRV_RF_3G_BAND_IX,
    DRV_RF_3G_BAND_X,
    DRV_RF_3G_BAND_XI,
    DRV_RF_3G_BAND_XII,
    DRV_RF_3G_BAND_XIII,
    DRV_RF_3G_BAND_XIV,
    DRV_RF_3G_BAND_XV,
    DRV_RF_3G_BAND_XVI,
    DRV_RF_3G_BAND_XVII,
    DRV_RF_3G_BAND_XVIII,
    DRV_RF_3G_BAND_XIX,
    DRV_RF_3G_BAND_XX,
    DRV_RF_3G_BAND_XXI,
/* TDD Bands */
    DRV_RF_3G_BAND_XXXIII,
    DRV_RF_3G_BAND_XXXIV,
    DRV_RF_3G_BAND_XXXV,
    DRV_RF_3G_BAND_XXXVI,
    DRV_RF_3G_BAND_XXXVII,
    DRV_RF_3G_BAND_XXXVIII,
    DRV_RF_3G_BAND_XXXIX,
    DRV_RF_3G_BAND_XL,
    DRV_RF_3G_BAND_XLI,

    DRV_RF_3G_BAND_NOT_VALID,
    DRV_RF_3G_NUM_BANDS = DRV_RF_3G_BAND_NOT_VALID
} drv_Rf3GBandsEnum;

/* public enumeration of the RF signals */
typedef enum
{
    DRV_RF_PA_EN = 0,
    DRV_RF_PA_OFF,
    DRV_RF_PA_HIGH,
    DRV_RF_PA_MID,
    DRV_RF_PA_LOW,
    DRV_RF_PA_VCC_2G,
    DRV_RF_PA_VCC_3G,
    DRV_RF_PA_VCC_EN,
    DRV_RF_PA_VCC_DI,
    DRV_RF_PA_VCC_BIAS,
    DRV_RF_PA_VCC_BIAS2,
    DRV_RF_PA_INIT,
    DRV_RF_MAIN_ANTENNA,
    DRV_RF_MAIN_ANTENNA_TX,
    DRV_RF_DIVERSE_ANTENNA,
    DRV_RF_PMIC_MODE_NORMAL,
    DRV_RF_PMIC_MODE_2G,
    DRV_RF_PMIC_PRE_RAMP_UP,
    DRV_RF_PMIC_PRE_RAMP_DN,
    DRV_RF_ANT_SWAP,
    DRV_RF_ANT_TUNE_VCC,
    DRV_RF_ANT_TUNE_MAIN,
    DRV_RF_ANT_TUNE_DIV,
    DRV_RF_WIFI_COEX_TX,
    DRV_RF_WIFI_COEX_RX,
    DRV_RF_MISC,
    DRV_RF_SIGNALS_NB_3G,

    DRV_RF_TAS,
    DRV_RF_2G_PA_EN_GMSK_LB,
    DRV_RF_2G_PA_EN_8PSK_LB,
    DRV_RF_2G_PA_EN_GMSK_HB,
    DRV_RF_2G_PA_EN_8PSK_HB,
    DRV_RF_2G_PA_EN_OFF,
    DRV_RF_2G_TX_ANTENNA_GMSK,
    DRV_RF_2G_TX_ANTENNA_8PSK,
    DRV_RF_2G_RX_ANTENNA,
    DRV_RF_2G_MISC,
    DRV_RF_DCDC_MODE,
    DRV_RF_SIGNALS_NB
}drv_RfSignalEnum;

/* public enumeration of the RF IO types */
typedef enum
{
    DRV_RF_GPIO0,
    DRV_RF_GPIO1,
    DRV_RF_GPIO2,
    DRV_RF_GPIO3,
    DRV_RF_GPIO4,
    DRV_RF_GPIO0_STRICT,
    DRV_RF_GPIO1_STRICT,
    DRV_RF_GPIO2_STRICT,
    DRV_RF_GPIO3_STRICT,
    DRV_RF_GPIO4_STRICT,
    DRV_RF_PMIC_MRFFE,
    DRV_RF_DAC,
    DRV_RF_FEM,
    DRV_RF_FEM_2,
    DRV_RF_SWT_LSHS3225U8RX,
    DRV_RF_SWT_LMSW6SGM,
    DRV_RF_SWT_SKY18115,
    DRV_RF_SWT_SKY13451,
    DRV_RF_SWT_SKY13452,
    DRV_RF_SWT_SKY13456,
    DRV_RF_SWT_SKY13484,
    DRV_RF_DAC_ONTCC103,
    DRV_RF_SWT_RF7069A,
    DRV_RF_PA_SKY77603,
    DRV_RF_PA_SKY77621,
    DRV_RF_SWT_RF1654A,
    DRV_RF_NB
}drv_RfPortEnum;

/* public enumeration of the tx/rx subsystems */
typedef enum
{
    DRV_RF_SUBSYS_RX_3G,
    DRV_RF_SUBSYS_TX_3G,
    DRV_RF_SUBSYS_RX_GSM,
    DRV_RF_SUBSYS_TX_GMSK,
    DRV_RF_SUBSYS_TX_8PSK,
    DRV_RF_SUBSYS_NB
} drv_RfSubSysEnum;

/* public enumeration of the RF configurable ports */
typedef enum
{
    // tx
    DRV_RF_TXLB =  1,
    DRV_RF_TXHB,
    DRV_RF_TX1,
    DRV_RF_TX2,
    DRV_RF_TX3,
    DRV_RF_TX4,
    DRV_RF_TXLB1,
    DRV_RF_TXLB2,
    DRV_RF_TXLB3,
    DRV_RF_TXLB4,
    DRV_RF_TXHB1,
    DRV_RF_TXHB2,
    DRV_RF_TXHB3,
    DRV_RF_TXHB4,

    // rx main
    DRV_RF_RXLB1,
    DRV_RF_RXLB2,
    DRV_RF_RXLB3,
    DRV_RF_RXMB1,
    DRV_RF_RXMB2,
    DRV_RF_RXHB,
    DRV_RF_RXHB1,
    DRV_RF_RXHB2,
    DRV_RF_RXHB3,
    DRV_RF_RXHB4,
    DRV_RF_RXSB,

    //diversity
    DRV_RF_RXDLB1,
    DRV_RF_RXDLB2,
    DRV_RF_RXDLB3,
    DRV_RF_RXDMB,
    DRV_RF_RXDHB,
    DRV_RF_RXDHB1,
    DRV_RF_RXDHB2,
    DRV_RF_RXDHB3,
    DRV_RF_RXDSB,

    DRV_RF_TX_RX_PORT_NB

} drv_RfTxRxPortEnum;

/* public enumeration of the RF temperature sensors */
typedef enum
{
    DRV_RF_TSENS1 = 0,
    DRV_RF_TSENS2,
    DRV_RF_TSENS_NB
} drv_RfTsensEnum;

/* public enumeration of the RFIC ADC Ref voltages */
typedef enum
{
    DRV_RF_ADC_REF_1V7  = 1,
    DRV_RF_ADC_REF_2V65,
    DRV_RF_ADC_REF_NB
}drv_RfAdcRefEnum;

/* public enumeration of the RFIC SYSCLK options */
typedef enum
{
    /* output scaling */
    DRV_RF_SYSCLK_700MV_32M_POLE  =  (0x1<<0),
    DRV_RF_SYSCLK_700MV_80M_POLE  =  (0x1<<1),
    DRV_RF_SYSCLK_800MV_32M_POLE  =  (0x1<<2),
    DRV_RF_SYSCLK_800MV_80M_POLE  =  (0x1<<3),
    DRV_RF_SYSCLK_900MV_32M_POLE  =  (0x1<<4),
    DRV_RF_SYSCLK_900MV_80M_POLE  =  (0x1<<5),
    DRV_RF_SYSCLK_1000MV_32M_POLE =  (0x1<<6),
    DRV_RF_SYSCLK_1000MV_80M_POLE =  (0x1<<7),

    /* output enabling */
    DRV_RF_SYSCLK_NO_CLK_ON_SYSCLKEN    =  (0x1<<8),
    DRV_RF_SYSCLK_CLK2_ON_SYSCLKEN      =  (0x1<<9),
    DRV_RF_SYSCLK_CLK3_ON_SYSCLKEN      =  (0x1<<10),
    DRV_RF_SYSCLK_CLK2CLK3_ON_SYSCLKEN  =  (0x1<<11),

    DRV_RF_SYSCLK_NB
}drv_RfSysClkEnum;

typedef enum
{
    DRV_RFIC_0=0,
    DRV_RFIC_1=1,
    //DRV_RFIC_0_AND_1=2,
    DRV_RFIC_NB
}dev_RficEnum;
/*
 * RF IO control structures
 */

/* base structure to configure RF IO configuration for HVOP/GPOP/GPIO */
typedef struct
{
    drv_RfSignalEnum io_signal;
    drv_RfPortEnum   io_port;
    uint32           pos;
    uint32           width;
    uint32           mask;
    uint32           val;

} drv_RfIoSignal;

/* stucture to control non-band specific controls, LNAs, ADCs, etc. */
typedef struct
{
    bool dcxo_fitted;
    bool linear_pa_2g;
    bool adc_valid[ADC_NB];

    uint32 adc_3g[DRV_RF_3G_NUM_BANDS];
    uint32 adc_2g[DRV_RF_GSM_NB];
    uint32 adc_afc;

    int32 rx_tx_delay_3g[DRV_RF_3G_NUM_BANDS];
    uint32 rx_tx_delay_2g;

    uint32 port_3g_tx[DRV_RF_3G_NUM_BANDS];
    uint32 port_2g_tx[DRV_RF_GSM_NB];

    uint32 port_3g_rx[2][DRV_RF_3G_NUM_BANDS];
    uint32 port_2g_rx[DRV_RF_GSM_NB];

    uint8 rfic_3g_tx[DRV_RF_3G_NUM_BANDS];
    uint8 rfic_3g_rx[DRV_RF_3G_NUM_BANDS];
    uint8 rfic_2g_tx[DRV_RF_GSM_NB];
    uint8 rfic_2g_rx[DRV_RF_GSM_NB];

    drv_RfIoSignal dcdc_mode;

} drv_RfIoCommonControls;

/* structure to configure 3G RF IO configuration for HVOP/GPOP/GPIO */
typedef struct
{
    drv_RfIoSignal io_signal_3g[DRV_RF_3G_NUM_BANDS+1][DRV_RF_SIGNALS_NB_3G]; // DRV_RF_3G_NUM_BANDS+1 to allow for non-band specific control (DRV_RF_3G_BAND_NOT_VALID)
} drv_RfIo3g;

/* structure to configure 2G RF IO configuration for HVOP/GPOP/GPIO */
typedef struct
{
    drv_RfIoSignal antenna_2g[DRV_RF_GSM_NB+1][DRV_RF_GSM_PATH_NB];  // GSM antenna controlled, DRV_RF_GSM_NB+1 to allow for non-band specific control (DRV_RF_GSM_NOT_VALID)
    drv_RfIoSignal pa_en_mode_band[4];              // GSM PA enable, mode (GMSK/8PSK), band (low/high)
    drv_RfIoSignal pa_di;                           // GSM PA disable
    drv_RfIoSignal misc_2g[DRV_RF_GSM_NB+1];        // GSM misc control signal, DRV_RF_GSM_NB+1 to allow for non-band specific control (DRV_RF_GSM_NOT_VALID)
} drv_RfIo2g;

/* structure to configure RF VBatt parameters */
typedef struct
{
    int start_backoff;
    int backoff_slope;
    int headroom;
    int hysteresis_limit;
    int adc_cal_voltage_mV;
    int class_pwr_hysteresis;
    bool headroom_cfg_enabled; // headroom is a valid parameter only if this flag is true

} drv_RfVBatConfig;

/* stucture to control RF IC configuration */
typedef struct
{
    drv_RfAdcRefEnum temp_ref[DRV_RF_ADC_TEMP_INP_NUM];
    drv_RfAdcRefEnum volt_ref[DRV_RF_ADC_VOLT_INP_NUM];
    int vbat_adc;
    int vbat_scale;
    int vbat_shift;
    int vsys_adc;
    int vsys_scale;
    int vsys_shift;
    int sysclk;

} drv_RfIoRfIc;

/* master structure to configure RF IO */
typedef struct
{
    drv_RfIoCommonControls  common;
    drv_RfIo3g              io3g;
    drv_RfIo2g              io2g;
    drv_RfIoSignal          tas;
    drv_RfIoRfIc            rfic;
    drv_RfVBatConfig        vbat_3gcfg;
    drv_RfVBatConfig        vbat_2gcfg;

} drv_RfIo;

extern DXP_UNCACHED drv_RfIo drv_hwplat_rfio_desc;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/
/*****************************************/
/* Public RF IO configuration functions. */
/* Allow the customer to configure thier */
/* RF IO configuration                   */
/*****************************************/
extern void drv_rfio_DCXOFitted(bool dcxo);
extern void drv_rfio_TemperatureSensorValid(int adc);
extern void drv_rfio_3gTemperatureSensor(drv_Rf3GBandsEnum band, int adc);
extern void drv_rfio_2gTemperatureSensor(drv_RfGsmBandsEnum band, int adc);
extern void drv_rfio_AfcTemperatureSensor(int adc);
extern void drv_rfio_3gLnaSwitchable(bool switchable);
extern void drv_rfio_3gRxTxDelay(drv_Rf3GBandsEnum band, int delay);
extern void drv_rfio_2gRxTxDelay(int delay);
extern void drv_rfio_2gRampLinear(bool linear);
extern void drv_rfio_RfConfigMultiple3GChip(drv_Rf3GBandsEnum band, drv_RfSubSysEnum direction, dev_RficEnum device);
extern void drv_rfio_RfConfigMultiple2GChip(drv_RfGsmBandsEnum band, drv_RfSubSysEnum direction, dev_RficEnum device);
extern void drv_rfio_RfIoConfigure(drv_Rf3GBandsEnum band, drv_RfSignalEnum sig, drv_RfPortEnum port, uint32 pos, uint32 width, uint32 mask, uint32 val);
extern void drv_rfio_FemConfigure(int band, drv_RfSubSysEnum subsys, uint32 value);
extern void drv_rfio_3gPort(drv_Rf3GBandsEnum band, drv_RfTxRxPortEnum port);
extern void drv_rfio_2gPort(drv_RfGsmBandsEnum band, drv_RfTxRxPortEnum port);
extern void drv_rfio_TempRef(drv_RfADCTempInput adc, drv_RfAdcRefEnum ref);
extern void drv_rfio_VoltRef(drv_RfADCVoltInput adc, drv_RfAdcRefEnum ref);
extern void drv_rfio_VbatConfig(drv_RfADCVoltInput adc, int scale, int shift);
extern void drv_rfio_VsysConfig(drv_RfADCVoltInput adc, int scale, int shift);
extern void drv_rfio_2GClassPwrBackoff(int start, int slope);
extern void drv_rfio_3GClassPwrBackoff(int start, int adc_cal_voltage_mV, int class_pwr_hysteresis);
extern void drv_rfio_2GVBatHeadroom(int headroom);
extern void drv_rfio_3GVBatHeadroom(int headroom);
extern void drv_rfio_3GVbattHysteresis(int hysteresis_limit);
extern void drv_rfio_sysclk(drv_RfSysClkEnum clock_option);


#endif /* #ifndef DRV_GPRFIO_H */

/** @} END OF FILE */
