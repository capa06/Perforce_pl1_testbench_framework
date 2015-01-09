/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup XsiDriver XSI Driver
 *
 * Generic XSI Driver built upon mphal_fsi on 80xx platforms and
 * mphal_usi on 90xx platforms @{ 
 */

/**
 * @file drv_xsi.h Generic FSI/USI driver 
 *
 */

#ifndef DRV_XSI_H
#define DRV_XSI_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#ifndef HOST_TESTING
#include "livanto_memmap.h"
#include "livanto_config.h"
#endif
#include "os_abs.h"

#include "drv_xte.h"
#include "drv_spu.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_XSI_ZERO_RETRY_LATENCY  (-1)
    
/**
 * Macro defining depth of XSI transfer Q
 */
#ifdef MODULE_TEST
#define DRV_XSI_QLENGTH 4
#else
#define DRV_XSI_QLENGTH 30
#endif

/**
 * RF (RFFE / SPI) FIFO Depth
 */
/* 9xxx configurable on USI */
#define DRV_XSI_RF_FIFO_DEPTH     8


/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
 
/** 
 *  XSI device identifier
 *  
 *   FSI: the device identifier maps a real FSI block
 *  
 *   USI: device identifier is mapped to a USI block + SIP +
 *   base channel number.
 *  
 */
typedef enum {
    DRV_XSI_NONE = 0,   
    DRV_XSI_RFFE,
    DRV_XSI_SPI_RF0,
    DRV_XSI_SPI_RF1,
    DRV_XSI_UART_GPS,
    DRV_XSI_UART_BOOT,
    DRV_XSI_SPI_PMIC,
    DRV_XSI_I2C,
    DRV_XSI_AUDIO0,
    DRV_XSI_AUDIO1,
    DRV_XSI_AUDIO2,
    DRV_XSI_AUDIO3,
    DRV_XSI_HSI,

	DRV_XSI_SIP0,	/* USI0 PHY0 */
	DRV_XSI_SIP1,	/* USI0 PHY1 */
	DRV_XSI_SIP2,	/* USI0 PHY2 */
	DRV_XSI_SIP3,	/* USI0 PHY3 */
	DRV_XSI_SIP4,	/* USI1 PHY0 */
	DRV_XSI_SIP5,	/* USI1 PHY1 */
	DRV_XSI_SIP6,	/* USI1 PHY2 */
	DRV_XSI_SIP7,	/* USI1 PHY3 */

    DRV_XSI_NUM_DEVICES,
    
    /* Aliases for 8060 */
    DRV_XSI_SSP0 = DRV_XSI_RFFE,        /* RF PMIC */
    DRV_XSI_SSP1 = DRV_XSI_SPI_PMIC,    /* PMIC */
    DRV_XSI_C3G = DRV_XSI_SPI_RF0,      /* Configure 3G */
    DRV_XSI_CGSM = DRV_XSI_SPI_RF1,     /* Configure GSM */
    
    /* Aliases for BBC1 */
    DRV_XSI_AHUB_TX0 = DRV_XSI_AUDIO0,  /* BBC -> AP */
    DRV_XSI_AHUB_RX0 = DRV_XSI_AUDIO1,  /* BBC <- AP */
    DRV_XSI_AHUB_TX1 = DRV_XSI_AUDIO2,  /* BBC -> AP */
    DRV_XSI_AHUB_RX1 = DRV_XSI_AUDIO3,  /* BBC <- AP */
    
} drv_XsiDeviceId;

/**
 * drv_XsiChannelId 
 *  specifies communication channel.
 *  FSI: direct mapping with FSI channel.
 *  USI: mapping is relative to the base channel of the virtual
 *  device.
 */
typedef enum {
    DRV_XSI_CHANNEL0 = 0,
    DRV_XSI_CHANNEL1 = 1,
    DRV_XSI_CHANNEL2 = 2,
    DRV_XSI_CHANNEL3 = 3,
    DRV_XSI_CHANNEL4 = 4,
    DRV_XSI_CHANNEL5 = 5,
    DRV_XSI_CHANNEL6 = 6,
    DRV_XSI_CHANNEL7 = 7,
    DRV_XSI_CHANNEL8 = 8,
    DRV_XSI_CHANNEL9 = 9,
    DRV_XSI_CHANNEL10 = 10,
    DRV_XSI_CHANNEL11 = 11,
    DRV_XSI_CHANNELALL,
    DRV_XSI_NUM_CHANNELS = DRV_XSI_CHANNELALL
} drv_XsiChannelId;


/**
 * Base protocols
 */
typedef enum {
    /* Audio HUB protocol */
    DRV_XSI_P_AHUB_TX = 0,
    DRV_XSI_P_AHUB_RX,

    /* Audio protocols */
    DRV_XSI_P_AUDIO_PCM_LEFT,
    DRV_XSI_P_AUDIO_PCM_RIGHT,
    DRV_XSI_P_AUDIO_I2S,
    DRV_XSI_P_AUDIO_DSP_A,
    DRV_XSI_P_AUDIO_DSP_B,
    DRV_XSI_P_AUDIO_TDM_LEFT,
    DRV_XSI_P_AUDIO_TDM_RIGHT,
    DRV_XSI_P_AUDIO_TDM_I2S,

    DRV_XSI_P_GPIO,
    DRV_XSI_P_I2C,
    DRV_XSI_P_SPI,
    DRV_XSI_P_SPI_EVEREST_CPOL0_CPHA0,
    DRV_XSI_P_SPI_EVEREST_CPOL1_CPHA1,
    DRV_XSI_P_UART,
    DRV_XSI_P_RFFE,
    DRV_XSI_P_MIPI,
    DRV_XSI_P_UWIRE,
    DRV_XSI_P_LOOPBACK,
    DRV_XSI_P_SPI_OLYMPUS_DUAL_CS,
    DRV_XSI_NUM_PROTOCOLS,
} drv_XsiProtocolId;

/**
 * Chip selects.
 *  FSI: direct mapping with CS definitions.
 *  USI: mapped to a logical channel id.
 */
typedef enum {
    DRV_XSI_CS0,
    DRV_XSI_CS1,
    DRV_XSI_CS2,
    DRV_XSI_CS3,
    DRV_XSI_CS4,
    DRV_XSI_CS5,
    DRV_XSI_CS6,
    DRV_XSI_CS7,
    DRV_XSI_CSFROMCHANNEL,
    DRV_XSI_CS8,
    DRV_XSI_CS9,
    DRV_XSI_CS10,
    DRV_XSI_CS11,
    DRV_XSI_CS_BCAST,
    DRV_XSI_NUM_CS,
} drv_XsiChipSelectId;


/**
 * Chip select aliases for RFFE (9xxx only)
 */
#define DRV_XSI_CS_RFFE1            DRV_XSI_CS0
#define DRV_XSI_CS_RFFE2            DRV_XSI_CS1

/**
 * XSI Operational Modes
 */
typedef enum {
    DRV_XSI_MODE_IDLE,
    DRV_XSI_MODE_NORMAL,
    DRV_XSI_MODE_DATAPUMP,
} drv_XsiOpMode;

/**
 * Bit ordering for message transmission
 */
typedef enum {
    DRV_XSI_LSB_FIRST = 0,
    DRV_XSI_MSB_FIRST = 1
} drv_XsiBitOrder;

/**
 * Specifies chip-select polarity
 */
typedef enum {
    DRV_XSI_ACTIVE_LOW = 0,
    DRV_XSI_ACTIVE_HIGH = 1
} drv_XsiCsPolarity;

/**
 * Specifies Tx/Rx bit clock polarity inversion
 */
typedef enum {
    DRV_XSI_CLOCK_NO_INVERT = 0,
    DRV_XSI_CLOCK_INVERT = 1
} drv_XsiClkPolarity;


/**
 * Specifies bit clock phase
 */
typedef enum {
    DRV_XSI_PHASE_DELAY = 0,
    DRV_XSI_PHASE_NO_DELAY = 1
} drv_XsiClkPhase;

/**
 * Specifies direction (RX or TX)
 */
typedef enum {
    DRV_XSI_TX = 0,
    DRV_XSI_RX = 1,
} drv_XsiDirection;


/**
 * FIFO Threshold specifier
 */
typedef enum {
    DRV_XSI_THRESHOLD_NONE  = 0,
    DRV_XSI_THRESHOLD_READY = 1,
    DRV_XSI_THRESHOLD_HALF  = 2,
    DRV_XSI_THRESHOLD_FULL  = 3,
    DRV_XSI_THRESHOLD_EMPTY = DRV_XSI_THRESHOLD_FULL
} drv_XsiThreshold;


/* drv_XsiPacking
     Specifies the data format used for Put/Get
*/
typedef enum {
  DRV_XSI_PACK_8 = 0,  /* Data arranged/packed as array of bytes */
  DRV_XSI_PACK_16, /* Data arranged/packed as array of 16-bit values */
  DRV_XSI_PACK_32  /* Data arranged/packed as array of 32-bit values */
} drv_XsiPacking;

/* drv_XsiClkSrc
     CLK source enumeration (specific to USI or FSI)
*/
typedef enum { 
  DRV_XSI_CLK_DEFAULT,
  /* 80xx specific */
  DRV_XSI_CLK_80XX_SOC, 
  DRV_XSI_CLK_80XX_RXCLK, 
  DRV_XSI_CLK_80XX_TXCLK, 
  DRV_XSI_CLK_80XX_CRPC,
  /* 90xx specific */
  DRV_XSI_CLK_9XXX_USIPHY0_DIV,
  DRV_XSI_CLK_9XXX_USIPHY1_DIV,
  DRV_XSI_CLK_9XXX_USIPHY2_DIV,
  DRV_XSI_CLK_9XXX_AUDIO_GUT,
} drv_XsiClkSrc;


/* drv_XsiArbMode
     Tx FIFO arbitration modes (as per mphalfsit_ArbMode)
*/
typedef enum {
  DRV_XSI_ARB_ROUND_ROBIN = 0,
  DRV_XSI_ARB_FIXED = 1
} drv_XsiArbMode;

/**
 * Function type for XSI Callbacks
 */
typedef void (*drv_XsiTransferCB)(void *callback_arg, uint32 *data_out, uint32 *data_in, int transfers);

/**
 * Function type for Xsi Error Callback
 */
typedef void (*drv_XsiErrorCB)(void *callback_arg, uint32 error);

/**
 * Opaque structure for XSI channel
 */
struct drv_XsiTarget;

/**
 * Handle to XSI channel
 */
typedef struct drv_XsiTarget drv_XsiHandle;


#include "drv_xsi_spi.h"
#include "drv_xsi_ahub.h"
#include "drv_xsi_everest.h"
#include "drv_xsi_i2c.h"
#include "drv_xsi_loopback.h"
#include "drv_xsi_audio.h"
#include "drv_xsi_uart.h"
#include "drv_xsi_rffe.h"
#include "drv_xsi_olympus_dual_cs.h"

/**
 * Protocol and channel configuration
 */
typedef struct  {
    
    drv_XsiProtocolId       protocolId;          /** XSI protocol identifier */

    drv_XsiChipSelectId     chipSelect;          /** Chip select used */

    drv_XsiPacking          packing;             /** data packing format (8/16/32 Bit)*/

    int                     retryLatency;        /** Retry latency for rx/tx FIFO level
                                                    (us or DRV_XSI_ZERO_RETRY_LATENCY) */

    /* !0 = SIC triggered FIFO control. 0 = sic trigger disabled */
    int                     enableSicTrigger;

    /* Transmit arbitration mode */
    drv_XsiArbMode          arbMode; 

    /* Per protocol configuration */
    union {
        drv_XsiConfigSPI spi;
        drv_XsiConfigEverest everest;
        drv_XsiConfigOlympusDualCs olympusDualCs;
        drv_XsiConfigI2C i2c;
        drv_XsiConfigLoopback loopback;
        drv_XsiConfigAHUB ahub;
        drv_XsiConfigAudio audio;
        drv_XsiConfigUART uart;
        drv_XsiConfigRFFE rffe;
    } proto;


    /* Private fields - DO NOT TOUCH! */
    struct
    {
        /* Used by xSI(FSI) driver to identify which drv_XsiConfig owns general & chip
           select settings and which drv_XsiConfig's are secondary and should only
           apply channel specific settings on calling drv_XsiOpen */
        int primaryConfig;
    } priv;
    
} drv_XsiConfig;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize XSI module
 */
extern void drv_XsiInit();

/**
 * XSI Driver Target Open
 * Create a XSI Target configuration for a particular external peripheral.
 * pre :
 *        @param xsi:         XSI instance index (Refer to mphal_xsi.h).
 *        @param channel:     XSI channel index  (Refer to mphal_xsi.h).
 *        @param cs:          XSI chip select index (Refer to mphal_xsi.h).
 *        @param protocolId:  identifies the protocol to be used.
 *
 * post:
 *        @param config :      default protocol configuration.
 *
 *        If this is the first target to be opened on an xsi instance the general, per channel and
 *        per chip select configuration will be applied to the XSI instance. However if the XSI is
 *        already active no configuration will be altered. The handle will be returned from the
 *        static table stored in the XSI driver locally. If this XSI instance has already been
 *        opened on the other DXP, an ancillary connection to the XSI instance will be used,
 *        otherwise a shared principal connection will be used.
 *
 *        @return drv_Xsi: XSI Target Handle
 */
extern drv_XsiHandle *drv_XsiOpen(drv_XsiDeviceId deviceId, 
                                  drv_XsiChannelId channelId, 
                                  drv_XsiChipSelectId cs,
                                  drv_XsiProtocolId protocolId, 
                                  drv_XsiConfig *config);
								  
/**
 * XSI Driver Target Close
 * Close an XSI target
 *
 * pre:
 *      Must be run from same dxpInstance as target was opened
 *
 *      @param handle: drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *
 * post:
 *      Will mark the channel as inactive in the private handle stored in the XSI driver.
 *      If all channels are inactive will allow further configuration changes to be applied.
 *      Before a principal connection to the XSI can be closed, all ancillary connections must first
 *      be closed.
 *
 *      @return void
 */
extern void drv_XsiClose(drv_XsiHandle *handle);

/** 
 * Apply common defaults for selected protocol.
 * Structure xsiConfig will have all settings re-written (or zero'd).
 * It is not a requirement to call this function if you intend to rewrite all 'xsiConfig' entries.
 * 
 * @param xsiProtocolId     xSI Protocol Id
 * @param xsiConfig         xSI config structure
 * 
 * @return void
 */
extern void drv_XsiApplyDefaults(drv_XsiProtocolId xsiProtocolId, drv_XsiConfig *xsiConfig);

/**
 * XSI Driver Target Apply
 * Apply drv_Xsi Target configuration to hardware
 *
 * pre:
 *     Must be run from same dxpInstance as target was opened
 *
 *     Appropriate changes to the state stored in the channel_h, cs_h and xsi_h accessable via
 *     the target handle must have been made by the user. No driver API provided for this.
 *     For details of the configurations Refer to mphal_xsi.h and XSI functional spec.
 *
 *     @param handle: drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *
 * post:
 *     If only target on an XSI instance new configuration will be applied to hardware via
 *     mphalxsi_ApplyGeneralConfig (drv_XsiHandle *handle) otherwise modifications to XSI
 *     general config are ignored.
 *
 *     If cs for target is currently unused new configuration will be applied to hardware via
 *     mphalxsi_ApplyCSConfig (drv_XsiHandle *handle, drv_XsiChipSelect chipSelect,
 *     const drv_XsiCSConfig *config); otherwise modifications to XSI cs config are ignored.
 *
 *     Attempting to violate the above conditions is unchecked and the users risk, the software
 *     visable config may not match the actual hardware config. This is viewed as a driver
 *     architecture issue and not protected in the XSI driver.
 *
 *     Channel config modifications are always applied to the hardware via
 *     mphalxsi_ApplyChannelConfig (drv_XsiHandle *handle, drv_XsiChannel channel,
 *     const drv_XsiChannelConfig *config);
 *
 *     @return void
 */
extern void drv_XsiApply(drv_XsiHandle *handle, drv_XsiConfig *config);
 
/** 
 * XSI Get FIFO mode.
 * 
 * @param target_h drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 * @param direction Rx or Tx             (Refer to mphal_xsi.h)
 * 
 * @return int normal/datapump or idle
 */
extern int drv_XsiGetMode(drv_XsiHandle *handle, drv_XsiDirection direction);


/**
 * XSI Set FIFO Mode (normal/datapump)
 * pre:
 *      Mode switch can only be activated on an XSI target that has already been opened and applied.
 *
 *      @param handle    : drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *      @param direction : Rx or Tx             (Refer to mphal_xsi.h)
 *      @param mode      : idle / normal / datapump
 *
 * post:
 *      Summary:
 *      This function will wait until the XSI is IDLE and the FIFOs are empty before attempting to
 *      switch modes.
 *
 *      Mode switch may result in rx/tx FIFO being enabled (datapump) or disbaled (idle, normal)
 *      and the DMA threshold trigger being enabled to the level defined in the target channel
 *      config and the FIFO pint threshold being disabled (datapump) or the FIFO pint threshold
 *      being to the level defined in the target channel config and the DMA threshold trigger being
 *      disabled (normal) or all threshold being disabled (idle).
 *
 *      Actions:
 *      When invoked, this function performs the following actions:
 *      1. Wait for the XSI to be idle and the transfer queue to be empty.
 *      2. Configure XSI Tx mode:
 *        a. Place Tx into IDLE mode. In this mode, Tx is disabled on this channel.
 *        b. Place Tx into NORMAL mode. In this mode, Tx is placed into in FIFOPINT mode (although
 *           PINTs are not used) and then the channel FIFO is disabled.
 *        c. Place Tx into DATAPUMP mode.  In this mode, Tx is placed into DMA mode and then the
 *           channel is enabled.
 *      3. Configure XSI Rx mode:
 *        a. Place Rx into IDLE mode. In this mode, Rx is disabled on this channel.
 *        b. Place Rx into NORMAL mode. In this mode, Rx is placed into in FIFOPINT mode (although
 *           PINTs are not used) and then the channel FIFO is disabled.
 *        c. Place Rx into DATAPUMP mode.  In this mode, Rx is placed into DMA mode and then the
 *           channel is enabled.
 *
 *      @return void
 */
extern void drv_XsiMode(drv_XsiHandle     *handle,
                        drv_XsiDirection  direction,
                        drv_XsiOpMode     mode);

/**
 * XSI DMA request control
 *
 * Sets the XSI DMA request threshold (or switches off DMA requests entirely)
 *
 *      @param handle    : drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *      @param direction : Rx or Tx             (Refer to mphal_xsi.h)
 *      @param threshold : Threshold to be applied to DMA request generation
 *                         (use MPHALXSI_THRESHOLD_NONE to turn off requests)
 *
 *      @return void
 */
extern void drv_XsiDmaReqControl(drv_XsiHandle       *handle,
                                 drv_XsiDirection  direction,
                                 drv_XsiThreshold  threshold);

/**
 * XSI Driver Transfer
 * Shift transfers number of packets (dependent on packing defined for FstTarget) from *dataOut
 * receiving transfers number of packets (dependent on packing defined for FstTarget) into *data_in.
 *
 * pre:
 *    All data buffers must be statically allocated by the user. No effort to copy the data to a
 *    thread safe location will be attempted. Data corruption is viewed as the users responsibility.
 *
 *    It is not required to block on the transfer. The driver has a set depth FIFO for transfers to
 *    be queued. However this will assert on FIFO overflow.
 *
 *    @param handle    : drv_Xsi Target Handle          (provided by valid drv_XsiOpen(..))
 *    @param data_out  : Pointer to TxData             (allocated by user)
 *    @param data_in   : Pointer to RxData             (allocated by user)
 *    @param transfers : Number of packets to transfer (in size defined by traget config)
 *    @param callback  : Transfer Complete Callback    (can be NULL)
 *
 * post:
 *    Yielding thread associated with the XSI target will have new entry in the messageQ. Once the
 *    message is processed the task will enable Tx FIFO (if NULL != data_out) and the Rx FIFO
 *    (if NULL != data_in) and ping-pong Tx to Rx in single transfers, observing FIFO level, until
 *    all data is transfered.
 *
 *    Once transfer has completed driver will wait for rx/tx FIFO to be empty then disable the
 *    FIFOs and call the callback. The callback will be called with the data_in, data_out and
 *    transfers variables as parameters.
 *
 *    If no callback is provided, the call to this function completes the transfer without messaging
 *    the Yielding thread and blocks until the transfer is complete.  This functionality is provided
 *    to allow driver operation within atomic sections, which would otherwise not be possible as the
 *    main thread is not able to deschedule to allow the Yielding thread to run, thus we would end
 *    up waiting for ever for the transfer to complete.
 *
 *    @return void
 */
extern void drv_XsiTransfer(drv_XsiHandle     *handle,
                            void              *data_out,
                            void              *data_in,
                            int                transfers,
                            drv_XsiTransferCB  callback, 
                            void *             callback_arg);


/**
 * For this xSI instance, configure clock source & divisor.
 *
 * pre:
 *      Must be run from same dxpInstance as target was opened
 *  
 *      For USI, it allows to select the clock source for
 *      usi_phyN_clk, when micro-code uses it to generate output
 *      clock on the link (like for I2S).
 *
 *      @param handle: drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *
 * post:
 *      Clock source & divisor will be configured (if applicable on this variant)
 *
 *      @return void
 */
extern void drv_XsiConfigureClock(drv_XsiHandle *handle, drv_XsiClkSrc src, unsigned int div);

/**
 * For this xSI instance, mark required CLK (variant dependant) as needing to be 'always on'.
 * CLK enable state will not block hibernate and it is the responsibility
 * of calling driver to block hibernate when drv_Xsi may be in-use.
 *
 * pre:
 *      Must be run from same dxpInstance as target was opened
 *
 *      @param handle: drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *
 * post:
 *      For this xSI instance, mark CLK as needing to be 'always on' and
 *      force on now.
 *
 *      @return void
 */
extern void drv_XsiForceSocClkAlwaysOn(drv_XsiHandle *handle);


/**
 * XSI Channel Active Status
 *
 * Report whether an XSI channel instance is currently active
 *
 * NOTE: This is a temporary function. PM Driver should allow user to set a
 *       pre/post idle function.
 *       These functions would then be called on a per target basis.
 * pre:
 *    Module clock to XsiTarget must be active.
 *
 *    @param xsi_id  : MPHal XSI id enumerated type.
 *    @param channel : Channel instance to be checked.
 *
 * post:
 *    When invoked, this function performs the following actions:
 *    1. Setup inactive_mask:
 *      a. Configure inactive_mask for situations where Tx is enabled on this channel.
 *      b. Configure inactive_mask for situations where Rx is enabled on this channel.
 *      Note: We need to configure the mask to handle situations where either Rx or Tx may be disabled
 *            on this channel but enabled on another channel, because the status bits are global.
 *    2. Compare the inactive_mask with the status register contents, if any bits are set in both
 *       then the channel is active.  Channels which are not marked as principal or ancillary must
 *       be inactive.
 *
 *    @return int : 0 = Inactive
 *
 */
extern int drv_XsiChannelActive(drv_XsiDeviceId   xsi_id, drv_XsiChannelId channel);

/**
 * XSI Active Status
 *
 * Report whether an XSI instance is currently active
 *
 * NOTE: This is a temporary function. PM Driver should allow user to set a
 *       pre/post idle function.
 *       These functions would then be called on a per target basis.
 * pre:
 *    Module clock to XsiTarget must be active.
 *
 *    @param xsi_id : MPHal XSI id enumerated type.
 *
 * post:
 *    @return int : 0 = Inactive
 *
 */
extern int drv_XsiActive(drv_XsiDeviceId XsiDeviceId);


/**
 * Returns FIFO address for an XSI channel.
 *
 * pre:
 *    XSI target must be open.
 *
 *    @param handle:           drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *    @param direction:        Rx/Tx (Refer to mphal_xsi.h)
 *
 * post:
 *    @return uint32 : FIFO address for the handle given.
 *
 */
extern uint32 drv_XsiFifoAddress(drv_XsiHandle       *handle,
                                 drv_XsiDirection  direction);

								 
/**
 * Returns FIFO address for an XSI given its Xsi Id and Channel Id.
 *
 * pre:
 *    XSI target must be open.
 *
 *    @param xsi_id   : MPHal XSI id enumerated type.
 *    @param channel  : Channel instance to be checked.
 *    @param direction: Rx/Tx (Refer to mphal_xsi.h)
 *
 * post:
 *    @return uint32 : FIFO address for the handle given.
 *
 */
extern uint32 drv_XsiIdFifoAddress(drv_XsiDeviceId      XsiDeviceId,
                                   drv_XsiChannelId  channelId,
                                   drv_XsiDirection  direction);


/**
 * Returns SPU Slave ID for particular XSI Id & Channel
 *
 * pre:
 *
 *    @param xsi_id   : XSI id enumerated type.
 *    @param channel  : Channel instance to be checked.
 *
 * post:
 *    @return drv_SpuSlave : SPU_SLAVE_xxxx
 *
 */
extern drv_SpuSlave drv_XsiGetSpuSlave(drv_XsiDeviceId id, drv_XsiChannelId channel);

								   
/**
 * Returns DMA HW sync for an XSI channel.
 *
 * pre:
 *    XSI target must be open.
 *
 *    @param handle:           drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *    @param direction:        Rx/Tx (Refer to mphal_xsi.h)
 *
 * post:
 *    @return uint32 : DMA HW sync for the handle given.
 *
 */
extern uint32 drv_XsiDmaHwSync(drv_XsiHandle       *handle,
                               drv_XsiDirection  direction);


/**
 * Returns DMA HW sync for an XSI given its Xsi Id and Channel Id
 *
 * pre:
 *    XSI target must be open.
 *
 *    @param xsi_id   : MPHal XSI id enumerated type.
 *    @param channel  : Channel instance to be checked.
 *    @param direction: Rx/Tx (Refer to mphal_xsi.h)
 *
 * post:
 *    @return uint32 : DMA HW sync for the handle given.
 *
 */
extern uint32 drv_XsiDeviceIdDmaHwSync(drv_XsiDeviceId      XsiDeviceId,
                                 drv_XsiChannelId  channelId,
                                 drv_XsiDirection  direction);

/**
 * Allocate and construct a linked descriptor chain for XSI transfers
 *
 * pre:
 *     XSI target must be open, applied and in datapump mode with 32Bit Packing
 *
 *     @param handle:           drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *     @param direction:        Rx/Tx (Refer to mphal_xsi.h).
 *     @param buffer            Address of source/destination buffer in memory (alloacted by user)
 *     @param buffer_size       Size of the buffer (in bytes).
 *     @param xte_chain         Structure in which to record descriptors for chain
 *                               (allocated by user).
 *     @param data_width        Data width of transfers.
 *     @param continuous        In continuous mode, the last descriptor is liked to first
 *                              descriptor in the list.
 *     @param int_en            Interrupt enabled after last descriptor transfer completed.
 *
 * post:
 *     XSI driver will create the chain for STE or DTE depending on the memory location of the
 *     buffer with descriptors taken from a static pool of external descriptors allocated in the
 *     XSI driver. If this pool underflows the XSI driver will assert. Once created the chain is
 *     the users responsibility.
 *     For continuous rx/tx the user should manually link the last descriptor to the first.
 *
 *     @return void
 *
 */
extern void drv_XsiCreateChain(drv_XsiHandle       *handle,
                               drv_XsiDirection  direction,
                               const void          *buffer,
                               int                  buffer_size,
                               tXteDescriptorChain *xte_chain,
                               int                  data_width,
                               bool                 continuous,
                               bool                 int_en);

/**
 * Append a linked chain of descriptors to an existing chain
 *
 * pre:
 *     XSI target must be open, applied and in datapump mode with 32Bit Packing
 *
 *     @param handle:           drv_Xsi Target Handle (provided by valid drv_XsiOpen(..))
 *     @param direction:        Rx/Tx (Refer to mphal_xsi.h).
 *     @param buffer            Address of source/destination buffer in memory (alloacted by user)
 *     @param buffer_size       Size of the buffer (in bytes).
 *     @param xte_chain         Structure in which to record descriptors for chain
 *                               (allocated by user).
 *     @param data_width        Data width of transfers.
 *     @param continuous        In continuous mode, the last descriptor is liked to first
 *                              descriptor in the list.
  *     @param int_en            Interrupt enabled after last descriptor transfer completed.
 *
 * post:
 *     XSI driver will create the chain for STE or DTE depending on the memory location of the
 *     buffer with descriptors taken from a static pool of external descriptors allocated in the
 *     XSI driver. If this pool underflows the XSI driver will assert. Once created the chain is
 *     the users responsibility.
 *     For continuous rx/tx the user should manually link the last descriptor to the first.
 *
 *     @return void
 *
 */
extern void drv_XsiAppendToChain(drv_XsiHandle       *handle,
                         drv_XsiDirection  direction,
                         const void          *buffer,
                         int                  buffer_size,
                         tXteDescriptorChain *xte_chain,
                         int                  data_width,
                         bool                 continuous,
                         bool                 int_en);
				
						 
/**
 * De-allocate chain for XSI transfers
 *
 * pre:
 *    Chain must have been created via drv_XsiCreateChain(...) so all pre-conditions of that
 *    function must be adhered to.
 *
 *    @param xte_chain        Structure from which to free descriptor chain  (allocated by user)
 *
 * post:
 *     Function blocks until all descriptors have been de-allocated.
 *     @return void
 *
 */
extern void drv_XsiFreeChain(tXteDescriptorChain *xte_chain);

/**
 * Register all XSI GPIO banks 
 * (only on 80xx)
 *
 */
extern void drv_GpioXsiHwplatGpioBanksRegister( void );

/**
 * Enable XSI interrupts.
 *
 * pre: Driver must be opened.
 *
 * post: Default set of XSI interrupts are enabled.  Overflow/Underflow interrupts are not enabled
 * for the AUDIO FSI.
 */
extern void drv_XsiEnableInterrupts(drv_XsiHandle *handle);

/**
 *  Register XSI error interrupts (per xsi instance)
 *  Should be called after XsiOpen()
 *  @param drv_XsiDeviceId xsi instance indec
 *  @param drv_XsiErrorCB  function pointer to error callback
 *  @param void *          user data pointer for error callback
 */
extern void drv_XsiRegisterError(drv_XsiDeviceId XsiDeviceId, drv_XsiErrorCB cb, void *data);

/**
 * Clear XSI Rx and Tx FIFO.
 *
 * pre: 
 *      Driver must be opened.
 *  
 *      @param target_h     drv_XsiHandle handle
 *
 * post: 
 *      Tx and Rx Fifo are cleared.
 *  
 *      @return void
 */
extern void drv_XsiClearFifo(drv_XsiHandle *handle);

/**
 * Functions that provide quick access to FIFO Rx status
 *
 * pre: 
 *      Driver must be opened.
 *  
 *      @param handle     drv_XsiHandle handle
 *
 * post: 
 *      Returns Rx FIFO Empty/Ready status
 *  
 *      @return int (1 = ready, 0 = not ready)
 */
extern int drv_XsiRxFifoReady (drv_XsiHandle *handle);
extern int drv_XsiRxFifoEmpty (drv_XsiHandle *handle);

/**
 * Functions that provide quick access to FIFO Tx  status
 *
 * pre: 
 *      Driver must be opened.
 *  
 *      @param handle     drv_XsiHandle handle
 *
 * post: 
 *      Returns Tx FIFO Empty/Ready status 
 *  
 *      @return int (1 = empty, 0 = not empty/busy)
 */
extern int drv_XsiTxFifoReady (drv_XsiHandle *handle);
extern int drv_XsiTxFifoEmpty (drv_XsiHandle *handle);


#ifdef MODULE_TEST
extern void drv_XsiCreateRxLoopbackChain(drv_XsiHandle *rx_handle,
                                  drv_XsiHandle       *tx_handle,
                                  const void          *buffer,
                                  int                  buffer_size,
                                  tXteDescriptorChain *xte_chain,
                                  int                  data_width,
                                  bool                 continuous,
                                  bool                 int_en);
#endif


bool drv_IUsiDebug(unsigned long *param, int fd, int (*_write)(int fd, char *buf, int len));

#endif

/** @} END OF FILE */

