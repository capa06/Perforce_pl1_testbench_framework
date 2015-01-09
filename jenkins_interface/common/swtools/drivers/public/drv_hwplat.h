/*************************************************************************************************
 * Icera Inc.
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_hwplat.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup TopHwPlatform
 * @{
 */

/**
 * @file drv_hwplat.h Hardware abstraction interface.
 *
 */

#ifndef DRV_HWPLAT_H
#define DRV_HWPLAT_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_gpio.h"
#include "drv_pinmux.h"
#include "drv_uart.h"
#include "com_machine.h"
#include "drv_rfio.h"
#include "drv_pmic.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_HWPLAT_PINMUX_NUM     (2)
#define DRV_HWPLAT_PADCTRL_NUM    (9 + 1)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Describe the IO type, either Input or Output or does not exist
 */
typedef enum
{
    DRV_GPIO_UNDEF = 0,                 /** IO is not defined, needs to be 0 as non-initialized entries in gpio_desc will be set to 0 */
    DRV_GPIO_INPUT,                     /** IO is an input */
    DRV_GPIO_OUTPUT,                    /** IO is an output */
    DRV_GPIO_INOUT                      /** IO is an input/output */
} drv_HwplatIOType;

/**
 * Define the value to set at startup for an output GPIO
 */
typedef enum
{
    DRV_GPIO_INIT_0 = 0,                /** Initialize output pin to 0 */
    DRV_GPIO_INIT_1,                    /** Initialize output pin to 1 */
    DRV_GPIO_NONINIT                    /** For OUTPUT: do not initialize pin
                                            For INOUT:  leave the pin as input
                                            For INPUT:  Not relevant */
} drv_HwplatIOInit;

/** Interrupt type */
typedef enum
{
    DRV_GPIO_INT_WAKEUP_NONE = 0,
    DRV_GPIO_INT_WAKEUP_EDGE_FALLING,
    DRV_GPIO_INT_WAKEUP_EDGE_RISING,
    DRV_GPIO_INT_WAKEUP_EDGE_BOTH,
    DRV_GPIO_INT_WAKEUP_LEVEL_LOW,
    DRV_GPIO_INT_WAKEUP_LEVEL_HIGH,
} drv_HwplatIoInterruptWakeupType;

/** Callback prototype for Interrupt handling */
typedef void (*drv_HwplatIoIntCB)( void * handle, uint32 data );

/** Pinmux values for a specific configuration */
typedef uint32 drv_HwplatPinmuxValue[ DRV_HWPLAT_PINMUX_NUM ];

/**
 * Individual GPIO pin descriptor structure: definition
 * according to a specific platform
 *
 */
typedef struct tagIoDesc {
    drv_HwplatIOType    type;           /** Pin direction or undefined */
    eDrvGpioId          gpio_bank;      /** GPIO bank this IO is attached to */
    uint8               bit_order;      /** Bit order within the GPIO bank 0..15 */
    bool                is_negated;     /** tells whether the IO is active low */
    bool                is_hco;         /** tells whether the IO has the hardware controlled capability */
    drv_HwplatIOInit    init_value;     /** Value to put on the port pin for an output during initialization: 0/1/NonInit */
} tIoDesc;

/** Platform Specific GPIO mapping, mapped in gpio_desc structure */
typedef enum {
    IO_RTS = 0,
    IO_RI,
    IO_DCD,
    IO_DSR,
    IO_DTR,
    IO_SYS_RDY,
    IO_SIM_VCC_ENABLE,
    IO_SIM2_VCC_ENABLE,
    IO_SIM_LVL_SHFT,
    IO_NORFLASH_WP,
    IO_CHIP_EN_WAKEIN,
    IO_PMIC_SUBADDR,
    IO_LED_WLAN,
    IO_LED_WWAN,
    IO_LED_WPAN,
    IO_LED_4,
    IO_SIM_EN_1V8,
    IO_SIM_EN_3V0,
    IO_PA_DC2DC_EN,
    IO_WWAN_DISABLE_N,
    IO_I2C_SDA,
    IO_I2C_SCL,

    /* Platform specific logical IOs - should be moved to hwplatform */

    /* USB Cypress PHY - PC300 Platform */
    IO_PHY_CS,
    IO_PHY_RST,
    /* debug output toggling with APM clock changes (only if enabled by a compile switch) */
    IO_APM_CLOCK_SWITCH,
    /* PMIC generic core voltage select */
    IO_PMIC_CORE_VDD_SEL,
    /* USB NXP PHY Platform */
    IO_FLASH_ADDRESS_23,
    IO_FLASH_ADDRESS_24,
    IO_USB_INT,
    IO_SIM_VOLTAGE_SEL,
    IO_SIM2_VOLTAGE_SEL,
    IO_SIM_1V8_SEL,
    /* cust04 platform*/
    IO_AP_MODEM_MODE,
    /* cust05_02 platform */
    IO_DPRAM_INTERRUPT,
    IO_FW_SELECT,

    /* PolarPro2 specific IOs */
    IO_PP2_RST,
    IO_PP2_INT,
    IO_PP2_LED1,
    IO_PP2_LED2,
    IO_PP2_LED3,
    IO_PP2_LED4,
    IO_PP2_SD_OE,
    IO_PP2_DREQ,
    IO_PP2_LP_EN,

    /* HSI */
    IO_HSI_WAKE_IN,
    IO_HSI_WAKE_OUT,

    /* Monitor POWER OFF entry/exit through I/Os */
    IO_POWER_OFF_MONITOR,

    IO_AUDIO_FSYNC_DETECT,
    IO_AUDIO_FSYNC_REC_DETECT,

    IO_HOST_WAKE_3G_N,
    IO_3G_WAKE_HOST_N,

    IO_HW_ID_0,
    IO_HW_ID_1,
    IO_HW_ID_2,
    IO_HW_ID_3,
    IO_HW_ID_4,
    IO_PCB_ID_0,
    IO_PCB_ID_1,
    IO_PCB_ID_2,

    IO_WLED_EN_n,
    IO_ANT_DETECT,

    /* Trini Reset */
    IO_TRINI_RSTN,

    /* USB Current limiter */
    IO_USB_CUR_CTRL,

    /* Vcc system select */
    IO_VCC_SYSTEM_SEL,

    /* RF IC reset */
    IO_RFIC_RESET_0,
    IO_RFIC_RESET_1,

    IO_GPS_LDO_EN,
    IO_GPS_nRESET,
    IO_GPS_ON_OFF,
    IO_GPS_WAKEUP,

    /* PA voltage select */
    IO_PA_VOLTAGE,

    IO_UART_SELECT, /* I/O used to force UART usage as HIF */

    /* 8060 PWM enable. */
    IO_PWM_ENABLE,

    /* 8060/9040 USB ULPI */
    IO_USB_ULPI_D0,
    IO_USB_ULPI_D1,
    IO_USB_ULPI_D2,
    IO_USB_ULPI_D3,
    IO_USB_ULPI_D4,
    IO_USB_ULPI_D5,
    IO_USB_ULPI_D6,
    IO_USB_ULPI_D7,
    IO_USB_ULPI_STP,
    IO_USB_ULPI_DIR,
    IO_USB_ULPI_NXT,

    IO_MDM2AP_ACK,
    IO_MDM2AP_ACK2,
    IO_AP2MDM_ACK,
    IO_AP2MDM_ACK2,
    IO_AP2_CLK_REQ,

    /* E450EVT A-GPS */
    IO_PA_BLANK,
    IO_GPS_TSYNC,
    IO_GPS_CLK_REQ,

    /* E450EVT internal/external USB PHY */
    IO_PHY_USB_CS,

    /* Reserved for E450EVT */
    IO_MDMnCOLDBOOT,
    IO_GPIO5_2,
    IO_GPIO4_15,

    /* E450 PA DCDC MODE */
    IO_PA_DC2DC_MODE,

    /* for cust_12*/
    IO_CURRENT_LIMITE_CONTROL,

    /* E450T DCDC1 PWM Control */
    IO_DCDC1_PWM,
    IO_DCDC1_PWM_CLK,

    /* for cust_09*/
    IO_AP_WAKEUP_MODULE,
    IO_MODULE_READY,
    IO_MODULE_POWER_ON,
    IO_AP_READY,
    IO_MODULE_WAKEUP_AP,

    /* TP62361B DC/DC AVS Enable (D-Type CLK input) */
    IO_PMIC_CORE_AVS_ENABLE,

    IO_RF1_TAS,
    IO_RF1_SPI_PD,
    IO_RF1_HRL_INT,

    IO_RF2_TAS,
    IO_RF2_SPI_PD,
    IO_RF2_HRL_INT,

    /* SIM card insertion/ removal detection */
    IO_SIM_DET,
    IO_SIM2_DET,

    /* Proximity sensor(s) detection */
    IO_SAR_DET_0,
    IO_SAR_DET_1,
    IO_SAR_DET_3,

    /* USB/HSIC Mode Select */
    IO_AP_IF_SELECT,

    /* Over Current signal connected to SOC_THERM on AP40*/
    IO_EDP_SOC_THERM_OC,

    /* E1729 new signals */

    IO_ANTCTL0,
    IO_SAR0,
    IO_ANTCTL1,
    IO_ANTCTL2_CAM_FLASH_INHIBIT,
    IO_ANTCTL3_SAR1,
    IO_W_DISABLE_N,
    IO_COEX3_WLAN_PRIORITY,
    IO_COEX1_LTE_TX,
    IO_COEX2_LTE_RX,
    IO_PMIC_INT,
    IO_MDM_WAKE_AP,
    IO_MDM_PWR_REPORT,
    IO_AP_WAKE_MDM,
    IO_SIM_DAT_ENABLE,
    IO_ANTCTL3,

 /* for cust_22*/
    IO_MDMnCOLDBOOT_ALT,
    IO_MDM_TX_IND,
    IO_MDM_SAR_IND,

    /* Enumerated to allow unused GPIOs to be specified so as to have a defined state */
    IO_UNUSED_1,
    IO_UNUSED_2,
    IO_UNUSED_3,
    IO_UNUSED_4,
    IO_UNUSED_5,
    IO_UNUSED_6,
    IO_UNUSED_7,
    IO_UNUSED_8,
    IO_UNUSED_9,
    IO_UNUSED_10,
    IO_UNUSED_11,
    IO_UNUSED_12,
    IO_UNUSED_13,
    IO_UNUSED_14,
    IO_UNUSED_15,
    IO_UNUSED_16,
    IO_UNUSED_17,
    IO_UNUSED_18,
    IO_UNUSED_19,
    IO_UNUSED_20,
    IO_UNUSED_21,
    IO_UNUSED_22,
    IO_UNUSED_23,
    IO_UNUSED_24,
    IO_UNUSED_25,
    IO_UNUSED_26,
    IO_UNUSED_27,
    IO_UNUSED_28,
    IO_UNUSED_29,
    IO_UNUSED_30,
    IO_UNUSED_31,
    IO_UNUSED_32,

    /* Last entry - Do not remove */
    IO_TOTAL_NUMBER
} tGpioMapping;

typedef struct {
    bool                init;       /* True if need to initialize the IO according to the settings */
    bool                input;      /* True if need to initialize as input */
    bool                hco;        /* True if controlled by HW */
    drv_HwplatIOInit    init_value;
} drv_HwplatIoSettings;

typedef struct
{
    uint16 input_dir_mask;
    uint16 output_dir_mask;
    uint16 hco_mask_set;
    uint16 hco_mask_clear;
    uint16 output_value_set;
    uint16 output_value_clear;
} tGpioBankSettings;

/**
 * Address/Data pair
 */
typedef struct {
    uint32 address;
    uint32 data;
} drv_HwplatAddrDataPair;

typedef void * drv_HwplatIoData;
typedef struct
{
    void (*init)( tIoDesc * desc, drv_HwplatIoData * data, drv_HwplatIoSettings io_settings );
    void (*set_bit_direction)( drv_HwplatIoData data, bool input );
    void (*set_bit_hw_controlled_output)( drv_HwplatIoData data, bool set );
    uint32 (*read_bit)( drv_HwplatIoData data );
    void (*write_bit)( drv_HwplatIoData data, bool set );
    uint32 (*get_write_bit_info_for_dma)( drv_HwplatIoData data, bool set, drv_HwplatAddrDataPair * addr_word, uint32 size );
    uint32 (*get_set_bit_dir_info_for_dma)( drv_HwplatIoData data, bool input, drv_HwplatAddrDataPair * addr_word, uint32 size );
    void (*register_int_handler)( drv_HwplatIoData data, drv_HwplatIoIntCB cb_fn, void * cb_fn_param, drv_HwplatIoInterruptWakeupType type );
    bool (*enable_int)( drv_HwplatIoData data, bool enable );
    bool (*is_int_pending)( drv_HwplatIoData data );
    void (*enable_wakeup)( drv_HwplatIoData data, uint8 level, bool enable );
    int (*is_wakeup_source)( drv_HwplatIoData data );
    bool (*is_int_handler_registered)( drv_HwplatIoData data );
} drv_HwplatIoOps;

/**
 * Internal GPIO description
 */
typedef struct {
    tIoDesc                         desc;               /** IO Description */
    drv_HwplatIoOps                 ops;                /** Operations */
    drv_HwplatIoData                data;               /** Internal Data for Operations handling */
    drv_HwplatIoInterruptWakeupType int_wakeup_type;    /** Interrupt/Wakeup type */
} drv_HwplatIoDesc;

/**
 * Structure used to define all the supported GPIO Configurations for a given platform type
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.pc300.58.Rev.1* */
    char * platform_config;
    /** Table describing the pinmux values for this IO Configuration */
    const drv_HwplatPinmuxValue * pinmux_desc;
    /** Pointer to the table describing the IOs for this IO Configuration */
    const tIoDesc * gpio_desc;
} drv_HwplatIOConfig;

/**
 * Structure used to define SHM config for a given platform type
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.pc300.58.Rev.1* */
    char * platform_config;
    /** SHM channels mapping description */
    void *chan_map_desc;
} drv_HwplatShmConfig;


/**
 * Structure used to define the default Sim to use for a given platform type
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.pc300.58.Rev.1* */
    char * platform_config;
    /** default SIM id to use for the given platform */
    int default_sim_id;
} drv_HwplatSimConfig;



typedef enum
{
    NO_POWER_CLASS_OVERRIDE = 0,
    POWER_CLASS_LIMITED_SET1,

} PowerClassSelectionOverride;

/**
 * HW platform descriptor
 */
typedef struct
{
    /* Clock settings for BT2 */
    uint32 mclk_hz;
    uint32 initial_core_clk_div;
    uint32 pll_nf;
    uint32 pll_nr;
    uint32 pll_od;
    uint32 clkbox_prediv_clka;
    uint32 clkbox_prediv_clkb;
    uint32 soc_clock_div;
    uint32 umcd_clock_div;
#if defined(ICE9XXX_EXT_PLL)
    uint32 ext_pll_in_use;
#endif
    uint32 usi_clock_div;
} drv_Bt2Desc;

/**
 * Type of device
 */
typedef enum {
    DRV_HWPLAT_DEVICE_TYPE_UNKNOWN = 0,
    DRV_HWPLAT_DEVICE_TYPE_EMBEDDED,
    DRV_HWPLAT_DEVICE_TYPE_REMOVABLE,
    DRV_HWPLAT_DEVICE_TYPE_REMOTE,
    DRV_HWPLAT_DEVICE_TYPE_MAX_SUPPORTED
} drv_HwplatDeviceType;


typedef struct
{
  /* clock conf in HW desc available for BT2 only */
  drv_Bt2Desc bt2_params;

  /* Drive Strength Shadow Settings */
  uint32 ioctrl_shadow_settings[DRV_HWPLAT_PADCTRL_NUM];

  /* I2C */
  uint32 i2c_bus_clk;
  uint32 i2c_spike_filter;
  uint32 i2c_scl_delay;

  /* Platform capabilities */
  drv_HwplatDeviceType device_type;

  /* Internal 32K oscillator fitted ? */
  bool use_internal_32K;

  void (*PowerMngtVccCoreColdBootInit)(void);
  bool (*Bt2ForceLoaderMode)(void);
} drv_HwplatDesc;

typedef enum
{
    DRV_HIF_USB,
    DRV_HIF_UART,
    DRV_HIF_HSI,
    DRV_HIF_UNKNOWN
}drv_HwplatHifType;

typedef enum
{
    DRV_HIF_OS_UNSPECIFIED = 0,
    DRV_HIF_OS_WINDOWS,
    DRV_HIF_OS_LINUX,
    DRV_HIF_OS_MACOS,
    DRV_HIF_OS_ANDROID,
    DRV_HIF_OS_CONF_NOT_READY
} drv_HwplatHifOsType;

/** Host Interface Status */
typedef enum {
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_INACTIVE = 0,
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_ACTIVE,
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_SUSPENDED,
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_RESUMING,
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_RESUMED,
    DRV_HWPLAT_HOST_INTERFACE_STATUS_LINK_REMOTE_WAKEUP,
} drv_HwplatHostInterfaceStatus;

/** Host Interface Status Callback */
typedef void (*drv_HwplatHostInterfaceStatusCB)( void * ctx, drv_HwplatHostInterfaceStatus status );

/** Hwplatform Host Interface Status CB List Link */
typedef struct drv_HwplatHostInterfaceStatusCBLinkStruct
{
    drv_HwplatHostInterfaceStatusCB cb;
    void * data;
    struct drv_HwplatHostInterfaceStatusCBLinkStruct *next;
} drv_HwplatHostInterfaceStatusCBLink;

/** Hwplatform Host Interface Descriptor */
typedef struct
{
  void (*HostInterfaceInit)(void);
  void (*HostInterfaceReInit)(void);
  drv_HwplatHostInterfaceStatus HostInterfaceStatus;
  drv_HwplatHostInterfaceStatusCBLink *HostInterfaceStatusCBList;
  drv_HwplatHifType hif_type;
  drv_HwplatHifOsType os_type;
} drv_HwplatHifDesc;

/**
 * HW platform Uart settings
 */
typedef struct
{
    uint32 baudrate;
    uint8  char_size;
    uint8  stop_bits;
    uartdrvt_Parity  parity;
    bool parity_enable;
} tHwPlatUartDefSettings;

/**
 * Companion Chip Name and Revision
 */
typedef struct {
    char * name;
    uint32 revision;
} drv_HwplatCompanionChipsRevisions;

/**
 * Structure used to confgiure the RF IO for a given platform
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.pc300.58.Rev.1* */
    char * platform_config;
    /** RF IO confgiuration pointer */
    void (*rf_io_func)(void);
} drv_HwplatRFIOConfig;

/**
 * Structure used to store power config for a given platform
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.pc300.58.Rev.1* */
    char * platform_config;
    /** RF power configuration pointer */
    void (*power_func)(drv_PmicCb callback, void * callback_param);
} drv_HwplatPowerConfig;

/**
 * Structure used to store PMIC interface settings for a given
 * platform
 */
typedef struct {
    /** String of a compatible platform config, i.e. icera.e1680* */
    char * platform_config;
    /** PMIC interfaces */
    const drv_PmicInterfaceSettings *pmic_if;
    /** CRPC PWM configuration */
    const drv_PmicCrpcPwmSettings *crpc_pwm_settings;
    /** DFLL settings */
    const drv_PmicDfllSettings *dfll_settings;
} drv_HwplatPmicIfConfig;

/**
 * SPI PMIC Settings
 * Use FSI/USI agnostic types in global scope.
 */
typedef struct {
    unsigned          interface;
    unsigned          chip_select;
} drv_HwplatSpiPmicConfig;

/**
 * Structure used to confgiure power measurement device config
 */
typedef struct {
    /** Name of power measurement point */
    const char * measure_name;
    /** Power measurement device I2c address */
    uint8        i2c_address;
    /** RShunt in mOhms */
    uint16       rshunt;
} drv_HwplatPowerMeasureConfig;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize all GPIOs
 * @param dxp_instance  DXP Instance
 */
void drv_HwplatGpioInitialize( enum com_DxpInstance dxp_instance );

/**
 * lets every specific GPIO bank either natural or virtual
 * register its owns set of IO handling callbacks
 *
 */
void drv_HwplatRegisterGpioBank(eDrvGpioId bank_id, const drv_HwplatIoOps *gpio_ops);

/**
 * Initializes the pinmux_desc and gpio_desc according to the value stored in the Platform Config file
 * Uses the default pattern "*" to match the configuration if VFS is not initialized.
 *
 * @param vfs_initialized   True if Virtual File System has been initialized
 *
 */
void drv_HwplatInitPinmuxGpioDescFromPlatformCfg( bool vfs_initialized );

/**
 * Read the value of an IO
 *
 * @param io        Logical number of the IO to read
 *
 * @return          Value of the GPIO
 *
 */
int drv_HwplatGpioReadPin( tGpioMapping io);

/**
 * Write a value to an IO
 *
 * @param io        Logical number of the IO to read
 * @param val       Value to write to the GPIO
 *
 * @return          0 if successful or negative value otherwise
 *
 */
int drv_HwplatGpioWritePin( tGpioMapping io, int val);

/**
 * Retrieve the address and data to write in order to write a value to a Hardware Platform defined IO.
 *
 * @param io        Logical number of the IO to read
 * @param val       Value to write to the GPIO
 * @param addr_word Pointer to an array of address/data pairs that will hold the necessary values to write by DMA
 * @param size      Size of the array
 *
 * @return          Number of address/data pairs written into the array
 *
 */
uint32 drv_HwplatGpioGetWritePinInfoForDma( tGpioMapping io, uint32 val, drv_HwplatAddrDataPair * addr_word, uint32 size );

/**
 * Set the direction of the selected GPIO
 *
 * @param io        IO to initialize
 * @param dir       Direction to set, valid entries are: DRV_GPIO_INPUT, DRV_GPIO_OUTPUT
 *
 */
void drv_HwplatGpioSetPinDir( tGpioMapping io, drv_HwplatIOType dir );

/**
 * Retrieve the address and data to write in order to set the direction of a Hardware Platform defined IO.
 *
 * @param io        Logical number of the IO to set direction
 * @param dir       Direction to set, valid entries are: DRV_GPIO_INPUT, DRV_GPIO_OUTPUT
 * @param addr_word Pointer to an array of address/data pairs that will hold the necessary values to write by DMA
 * @param size      Size of the array
 *
 * @return          Number of address/data pairs written into the array
 *
 */
uint32 drv_HwplatGpioGetSetPinDirInfoForDma( tGpioMapping io, drv_HwplatIOType dir, drv_HwplatAddrDataPair * addr_word, uint32 size );

/**
 * Check if an interrupt handler has been registered on an IO
 *
 * @param io            Logical number of the IO to set direction
 *
 * @return              ture if registered, false if not
 *
 */
bool drv_HwplatGpioIsInterruptHandlerRegistered( tGpioMapping io);

/**
 * Register an interrupt handler on an IO
 *
 * @param io            Logical number of the IO to set direction
 * @param cb_fn         Callback function to be called upon interrupt
 * @param cb_fn_param   Parameter passed to the callback function
 * @param type          Interrupt type: Edge/Level driven
 *
 */
void drv_HwplatGpioRegisterInterruptHandler( tGpioMapping io, drv_HwplatIoIntCB cb_fn, void * cb_fn_param, drv_HwplatIoInterruptWakeupType type );

/**
 * Enable/Disable interrupt on an IO. The pending interrupts are cleared in both cases.
 *
 * @param io            Logical number of the IO to set direction
 * @param enable        True if need to enable. False if need to disable
 *
 * @return              true in case the callback has been called: in case GPIO was already active and interrupt type level
 *
 */
bool drv_HwplatGpioEnableInterrupt( tGpioMapping io, bool enable );

/**
 * Indicate if an interrupt is pending on the IO
 *
 * @param io            Logical number of the IO to set direction
 *
 * @ return true if an interrupt is pending
 *
 */
bool drv_HwplatGpioIsInterruptPending( tGpioMapping io );

/**
 * Enable/Disable wakeup on an IO
 *
 * @param io            Logical number of the IO to set direction
 * @param enable        True if need to enable
 *
 */
void drv_HwplatGpioEnableWakeup( tGpioMapping io, bool enable );

/**
 * Indicate if IO is the source of the wakeup
 *
 * @param io            Logical number of the IO to set direction
 *
 * @ return 1 if source of wakeup, 0 if not source of wakeup and -1 if IO is not wake capable.
 *
 */
int drv_HwplatGpioIsWakeupSource( tGpioMapping io );

/**
 * Retrieve the GPIO descriptor for a given IO
 *
 * @param gpio_id   GPIO to retrieve
 *
 * @return          Pointer to GPIO Descriptor of the IO if exists. NULL if not defined.
 *
 */
tIoDesc *drv_HwplatGetGpioDescriptor(tGpioMapping gpio_id);

/**
 * Check that a GPIO is defined for the platform
 *
 * @param gpio_id   GPIO to check
 *
 * @return          True if GPIO is defined
 *
 */
bool drv_HwplatCheckGpio( tGpioMapping gpio_id );

/**
 * Retrieve the current pinmux configuration
 *
 * @param pinmux_cfg : index of value to program hwplat dependant
 * @param index      : which pinmux register (0-2).
 *
 * @return uint32 : value of pinmux register
 */
uint32 drv_HwplatGetPinmuxValue(enum DrvPinmuxCfgId pinmux_cfg, int index);

/**
 * Retrieves a pointer to the hardware platform descriptor
 *
 * @return          Pointer to Hardware Platform Descriptor
 *
 */
drv_HwplatDesc * drv_HwplatGetDesc(void);

/* AVS platform dependent stuff */
/**
 * Returns platform-specific AVS frequency margin
 *
 * @return Frequency margin
 *
 */
int drv_hwplat_getHwplatAvsMargin(void);
/**
 * Returns platform-specific AVS frequency floor
 *
 * @return Frequency floor (0 means "don't apply custom frequency floor")
 *
 */
int drv_hwplat_getHwplatAvsFrequencyFloor(void);
/**
 * Returns platform-specific AVS MHz target for silicon speed calculations.
 *
 * @return SiSpeed target (0 means "don't apply custom SiSpeed target")
 *
 */
int drv_hwplat_getHwplatSiSpeedTarget(void);

void drv_Nor_WriteProtect(int state);

/**
 * Configure Vcc Core settings at Cold Boot
 *
 */
void drv_HwplatPowerMngtVccCoreColdBootInit(void);

void drv_usim_set_levelShifterDisable(int val);

void drv_rf_clear_rf_ios(void);

void drv_wait_xtal_ticks(uint32 nb_ticks);

/**
 * Give the HeadInfo Size in bytes.
 *
 * @note This function shall be implemented in the
 * hwplatform/<cust_plat>/drv_hwplat_flash.c if required.
 *
 * @return int info size
 */
int drv_HwplatGetHeadInfoSizeInBytes(void);

/**
 * Read HeadInfo in the specified NAND area.
 *
 * Either 6th page of the last block and if not available,
 * always try to read the 6th page of the next to last block.
 *
 * Data is considered available and copied in hi_buf as soon as
 * HEAD_INFO_MAGIC is found in the 4 1st bytes of the read page.
 *
 * Data is stored with ECC information but block used is marked
 * bad during gang_programming. We bypass bad block check when
 * reading NAND.
 *
 * @param hi_buf to store data if found. Must be non NULL and at
 *               least allocated for 250 bytes of data.
 *
 * @note This function shall be implemented in the
 * hwplatform/<cust_plat>/drv_hwplat_flash.c if required.
 *
 * @return int 0 if data available in hi_buf, -1 if not.
 */
int drv_HwplatGetHeadInfo(uint8 *hi_buf);

/**
 * Retrieves a pointer to the hardware platform host interface descriptor
 *
 * @return          Pointer to Hardware Platform HIF Descriptor
 *
 */
drv_HwplatHifDesc * drv_HwplatGetHifDesc(void);

/**
 * Returns DXP instance used to initialize Host interface.
 */
enum com_DxpInstance drv_HwplatHostInterfaceInitialisedOn(void);

/**
 * Starts the Host Interface.
 * Invoked at startup
 *
 */
void drv_HwplatHostInterfaceInitialize( void );

/**
 * Re-Initialize the Host Interface after power down (usually clocks).
 *
 */
void drv_HwplatHostInterfaceReInitialize(void);

/**
 * Register a function to indicate Host Interface status
 *
 * @param cb        Status Callback
 * @param cb_data   Status Callback data
 *
 */
void drv_HwplatHostInterfaceRegisterStatusCB( drv_HwplatHostInterfaceStatusCB cb, void * cb_data );

/**
 * Change the current Host Interface status
 *
 * @param status    New Host Interface Status
 *
 */
void drv_HwplatHostInterfaceSetStatus( drv_HwplatHostInterfaceStatus status );

/**
 * Store required HIF type in noninit.
 *
 * HIF type can become persistent to power cycle storing it in
 * file system in HIF_CONFIG_FILE.
 *
 * @param hif_type   DRV_HIF_UART or DRV_HIF_USB
 * @param persistent true to make hif_type persistent to power
 *                   cycle.
 */
void drv_HwplatHostInterfaceSetType(drv_HwplatHifType hif_type, bool persistent);

/**
 * Retrieve the companion chips revisions and names
 *
 * @param chips_revisions       Pointer to a variable that will hold a pointer to a structure of names and revisions. Need to be freed after use.
 *
 * @return                      Number of names/revisions
 *
 */
uint32 drv_HwplatGetCompanionChipsRevisions( drv_HwplatCompanionChipsRevisions ** chips_revisions );

/**
 * Retrieve the platform revision string
 *
 * @return the platform revision string
 *
 */
const char *drv_HwplatGetPlatformRevisionString(void);

/**
 * Initializes the RF IO according to the value stored in the
 * Platform Config file.
 */
void drv_HwplatInitRfIoFromPlatformCfg( void );

/**
 * Answers the question where host interface memory should be allocated:
 *  in *uncached* or *cached* area (depends on on the host interface properties)
 * (USB profile and 8060 scatter/gather support).
 *
 *
 * @return          1 if HIF needs cached memory, 0 otherwise
 *
 */
int drv_HwplatHifCached(void);

/**
 * Indicates which OS is expected to run on host side. This
 * value is WINDOWS by default. It can be overriden in
 * platformConfig. It can also be updated by ZEROCD
 * feature.
 *
 * @return          os type.
 *
 */
drv_HwplatHifOsType drv_HwplatGetHifOsType(void);

/**
 * Overrides current OS type.
 *
 * @return void
 */
void drv_HwplatSetHifOsType(drv_HwplatHifOsType osType);

/**
 * Initialize any platform specific power settings
 *
 * @param callback        callback function for PMIC
 * @param callback_param  pointer to callback function params
 *
 * @return void
 */
void drv_HwplatInitPowerFromPlatformCfg( drv_PmicCb callback, void * callback_param );


/**
 * Resize HostInterface klog/plog buffers for loader and bt3 applications
 *
 * @param  downsize_klogs   divide preset max entries values by 16
 *
 * @return void
 */
void drv_HwplatHostInterfaceKlogResizing(bool downsize_klogs);

/**
 * Return the AT%IHIFCONFIG command usage.
 *
 */
int drv_HwplatHifConfigUsage(const char** text[]);

/**
 * Return by AT%IHIFCONFIG command the current host interface configuration.
 *
 */
int drv_HwplatHifConfigCurrent(char* buffer, size_t buffersize);

/**
 * Set by AT%IHIFCONFIG command the current host interface configuration and restart the modem.
 *
 */
bool drv_HwplatHifConfigSet(int action, int param1, int param2, int param3, int param4);

/**
 * Get SHM configuration based on platform config content.
 *
 * @return drv_HwplatShmConfig*
 */
drv_HwplatShmConfig *drv_HwplatGetShmConfigFromPlatformCfg(void);

/**
 * Get PMIC interfaces config based on platform config content.
 *
 * @return drv_HwplatPowerConfig*
 */
drv_HwplatPmicIfConfig *drv_HwplatGetPmicIfConfigFromPlatformCfg(void);

/**
 * Get default Sim id based on platform config content.
 *
 * @return int
 */
int drv_HwplatGetDefaultSimIdFromPlatformCfg(void);

/**
 * Check if H/W platform is LTE Cat4 capable
 *
 * @return bool
 */
bool drv_HwplatLteCat4Capable(void);
#endif /* #ifndef DRV_HWPLAT_H */

/** @} END OF FILE */
