/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_global.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup BoardLevelDrv Board Low Level Drivers
 */

/**
 * @defgroup SoCLowLevelDrv SoC Low Level Drivers
 */

/**
 * @defgroup PwrMgt Power Management Sub-System
 */

/**
 * @defgroup HighLevelServices High Level Services
 */

/**
 * @defgroup Top Global Settings and Initialisations
 */

/**
 * @defgroup TopHwPlatform Hardware Platform Specifications
 * @ingroup  Top
 */

/**
 * @defgroup TopUtil Utility Functions
 * @ingroup  Top
 */

/**
 * @defgroup UsbDriver USB Driver
 * @ingroup  HostCom
 */


/**
 * @addtogroup Top
 * @{
 */

/**
 * @file drv_global.h Initialisations and inter-DXP
 *       synchronisation
 *
 */

#ifndef DRV_GLOBAL_H
#define DRV_GLOBAL_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* Test if running as Modem */
#define IS_MODEM_FIRMWARE()         ( likely  ( drv_CurrentRunningFirmware == DRV_FIRMWARE_MODEM ) )
/* Test if running as Loader or Tertiary boot */
#define IS_LOADER_FIRMWARE()        ( unlikely( (drv_CurrentRunningFirmware == DRV_FIRMWARE_LOADER) || (drv_CurrentRunningFirmware == DRV_FIRMWARE_TERTIARY_BOOT) ) )
/* Test if running as Tertiary boot */
#define IS_BT3_FIRMWARE()           ( unlikely( drv_CurrentRunningFirmware == DRV_FIRMWARE_TERTIARY_BOOT ) )
/* Test if running as Secondary-Boot */
#define IS_BT2_FIRMWARE()           ( unlikely( drv_CurrentRunningFirmware == DRV_FIRMWARE_SECONDARY_BOOT ) )
/* Test if running as Soft Activation */
#define IS_ACT_FIRMWARE()           ( unlikely( drv_CurrentRunningFirmware == DRV_FIRMWARE_ACTIVATION ) )

/* Retrieve the current running firmware id */
#define GET_CURRENT_FW()            ( drv_CurrentRunningFirmware )

/*#include "drv_rf_ext.h"*/
#include "drv_evt_dispatch.h"

typedef enum
{
    RF_INIT_DEFAULT_VALUES=0,
    RF_INIT_CROSS_DXP1_QUEUE_INITIALISE, /* set by DXP1: indicate DXP0, cross DXP event queue available on DXP1 */
    RF_INIT_RF_IO_INITIALISE,            /* set by DXP0: indicate DXP1 RF I/O initialization */
    RF_INIT_PMIC_INITIALISE,             /* set by DXP1: indicate DXP0 PMIC initialization */
    RF_INIT_RF_INITIALISE,               /* set by DXP0: indicate DXP1, full RF initialization */
} rf_init_state;

/* This gives the current mode of the modem firmware*/
typedef enum
{
    MODEM_MODE_NULL = 0,
    MODEM_MODE_MASS_ZEROCD,
    MODEM_MODE_MODEM,
    MODEM_MODE_INVALID
} drv_ModemMode;

/* This is the value entered by the user in AT%MODE=n (see drv_CurrentRunningFirmware below) */
typedef enum
{
    DRV_FIRMWARE_MODEM = 0,
    DRV_FIRMWARE_LOADER,
    DRV_FIRMWARE_FACTORY_TEST,
    DRV_FIRMWARE_SECONDARY_BOOT,
    DRV_FIRMWARE_FLASHPROG,
    DRV_FIRMWARE_TERTIARY_BOOT,
    DRV_FIRMWARE_ACTIVATION,
    DRV_FIRMWARE_UNSUPPORTED
} drv_Firmware;

/* This is the value used by the RTB wakeup register */
typedef enum
{
    DRV_FIRMWARE_RTB_MODE_NULL = 0,
    DRV_FIRMWARE_RTB_MODE_MODEM,
    DRV_FIRMWARE_RTB_MODE_LOADER,
    DRV_FIRMWARE_RTB_MODE_FACTORY_TEST,
    DRV_FIRMWARE_RTB_MODE_UNSUPPORTED
} drv_FirmwareRtbMode;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/**
 *  Current running firmware defined in the application init.c file.
 *  It should be use to know in which FW we are
 **/
extern const drv_Firmware DXP_MULTI drv_CurrentRunningFirmware;
/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern void drv_init(int dxp_instance);

extern void drv_InitEnableApm(void);

extern void drv_Dxp1WaitForDxp0RfInit(void);

extern void drv_Dxp0WaitForDxp1PmicInit(void);

extern void drv_Dxp0WaitForDxp1EventQueueInit(void);

extern rf_init_state drv_GetInterDxpSyncState(void);

extern void drv_SignalInterDxpSynchStateChange(rf_init_state new_state);

extern void drv_TopUnusedPeripheralsDisable(void);

extern int32 drv_InitPaVccSetting(drv_EvtDispatchEventCode event,void *bufin, uint32 bufin_size, void *bufout, uint32 bufout_size);

extern int32 drv_PaVccSetting(drv_EvtDispatchEventCode event,void *bufin, uint32 bufin_size, void *bufout, uint32 bufout_size);

extern bool drv_ModemFirmwareModeTest(drv_ModemMode mode);

extern int drv_ModemFirmwareMode(void);
#endif /* #ifndef DRV_GLOBAL_H */

/** @} END OF FILE */
