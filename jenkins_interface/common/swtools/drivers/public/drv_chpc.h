/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008-2013
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_chpc.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup ChpcDriver CHPC Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup ChpcDriver
 * @{
 */

/**
 * @file drv_chpc.h CHPC interface to provide basic functions
 *       for Chip control
 *
 */

#ifndef DRV_CHPC_H
#define DRV_CHPC_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_ipm.h"
#include "drv_ipm_order.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* Defines for the EFUSE blowing code */
#define CHPC_NUM_EFUSE_SHADOW_REGS         (32)
#define CHPC_NUM_EFUSE_SHADOW_BYTES        (CHPC_NUM_EFUSE_SHADOW_REGS * 4)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Return code for customer fuse programming.
 */
 typedef enum
 {
    DRV_CHPC_FUSE_OK = 0,           /* Success. */
    DRV_CHPC_FUSE_INVAL,            /* Invalid argument(s). */
    DRV_CHPC_FUSE_OEM_LOCKED,       /* Oem locked fuse blown. */
    DRV_CHPC_FUSE_NO_CRC,           /* No crc locations available. */
    DRV_CHPC_FUSE_HIB_ENABLED,      /* Hibernation still enabled. */
 } drv_ChpcCustomerFuseReturnCode;

/**
 * Data structure used to hold customer fuse information.
 */
typedef struct
{
    /** debug_0 1-bit field */
    uint32 debug_0;

    /** debug_1 1-bit field */
    uint32 debug_1;

    /** oem_lock 1-bit field */
    uint32 oem_lock;

    /** cfg_word_13 32-bit field */
    uint32 cfg_word_13;

    /** device_fid 32-bit field */
    // Previously called cfg_word_15.
    uint32 device_fid;

    /** ice_ice_key_disable 7-bit field */
    uint32 ice_ice_key_disable;

    /** product_id 32-bit field */
    uint32 product_id;

} drv_ChpcCustomerFuseData;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize Pinmux shadow register value
 *
 */
extern void drv_ChpcInitializePinmuxResetValue(uint32 * pinmux_value_store);

/**
 * Initialise drive-strength according to hardware platform specific values
 */
extern void drv_ChpcSetDriveStrength(uint32 *p_ioctrl_shadow);

/**
 * Adjust ICELINK drive-strengths (as per CHPC spec).
 * @return 1 = ok, 0 = error
 */
extern int drv_ChpcSetIcelinkDriveStrength(uint32 bbrfDrv, uint32 bbrfD1drv);

/**
 * Read boot mode from eFuse
 *
 * @return 1 for internal, 0 for external
 */
extern uint32 drv_ChpcGetBootMode(void);

#if defined (TARGET_DXP9140)
/**
 * Read "low Vdd capable" efuse
 * (valid for T148-A01 only)
 *
 * @return 1 "low Vdd capable", 0 otherwise
 */
extern uint32 drv_ChpcGetBbcLowVmin(void);

/**
 * Read "LTE category" efuse
 * (valid for T148 only)
 *
 * @return 0 if tested to 1666 MHz, 1 is tested to 1720 MHz
 */
extern uint32 drv_ChpcGetBbcIncreasedMaxSpeed(void);
#endif

/**
 * Query pin freeze status.
 */
extern int drv_ChpcIsIOFrozen(void);

/**
 * CHPC driver IPM pre idle callback
 *
 * Done by DXP#0 when power off is about to be performed.
 *
 * @param driver_handle
 * @param power_mode
 *
 * @return drv_IpmReturnCode
 */
extern drv_IpmReturnCode drv_ChpcPreCb(drv_Handle driver_handle,drv_IpmPowerMode power_mode);

/**
 * CHPC driver IPM post power down callback
 *
 * Done by DXP#1 if power off was performed:
 * only USIM & USB drivers (running on DXP#1) need I/O frozen
 * during their post power down processing.
 *
 * @param driver_handle
 * @param power_lost
 *
 * @return drv_IpmReturnCode
 */
extern drv_IpmReturnCode drv_ChpcPostCb(drv_Handle driver_handle, bool power_lost);

/**
 * CHPC driver power management init function
 *
 * CHPC driver must be synced with PM framework to handle I/O
 * freeze/unfreeze during power off cycles cause some drivers
 * need to work with I/O frozen during their post power down
 * processing.
 *
 */
extern void drv_ChpcPmInit(void);

/**
 * Unfreezes pads that should be unfrozen on cold boot
 *
 */
extern void drv_ChpcColdBootUnfreeze(void);

/**
 * After this function is called, any AFAULT source will fault
 * both DXPs
 */
void drv_ChpcEnableAFAULTHandlingOnBothDXPs(void);

/**
 * This will attempt to program the product ID into the EFUSES
 */
void drv_ChpcProgramProductID_dxp0(void);
void drv_ChpcProgramProductID_dxp1(void);

/**
 * Check customer fuse programming values are valid
 *
 * This will check the customer fuse program values to make sure
 * they are all within their valid ranges
 *
 * @param fuse_data pointer to the structure containg the fuse data
 *                  to write to the efuses
 *
 * @return drv_ChpcCustomerFuseReturnCode
 *
 */
drv_ChpcCustomerFuseReturnCode drv_ChpcCheckCustomerFuseData(drv_ChpcCustomerFuseData * fuse_data);

/**
 * Check if customer fuse programming is possible
 *
 * This will check the current state of the customer
 * programmable fuses to determine if fusing is possible
 *
 * @return drv_ChpcCustomerFuseReturnCode
 */
drv_ChpcCustomerFuseReturnCode drv_ChpcIsProgrammingCustomerFusesPossible(void);

/**
 * Program customer fuses
 *
 * This will attempt to program the customer programmable EFUSES
 *
 * @param fuse_data pointer to the structure containg the fuse data
 *                  to write to the efuses
 *
 * @return drv_ChpcCustomerFuseReturnCode
 *
 * Note: After fuse programming has completed, an unconditional device
 *       reset will occur and this function will not return.
 */
void drv_ChpcProgramCustomerFuses(drv_ChpcCustomerFuseData * fuse_data);

/**
 * Read customer fuses
 *
 * This will read the customer programmable EFUSES
 *
 * @param fuse_data pointer to the sturcture used to return the fuse data
 *                  read from the efuses
 */
void drv_ChpcReadCustomerFuses(drv_ChpcCustomerFuseData * fuse_data);

/**
 * Apply default fusing settings if required.
 *
 * If ICERA_FEATURE_AUTOFUSING defined, this function is called
 * at init and should run once to apply default eFuse settings:
 *  - disable dev keys
 *  - set product ID
 *
 * Following calls to the function are with no effect.
 */
void drv_ChpcDefaultAutoFuse(void);

/**
 * Read EFUSE platform product ID
 *
 *
 * @return uint16 16bits product ID
 */
uint16 drv_ChpcGetProductId(void);

/**
 * Are the (non-DDR) I/O pins currently frozen?
 * On 80xx, this is between CHPC pre-hibernate handler & post-hibernate calls.
 * On 90xx, this is between successful hibernate & post-hibernate CHPC IPM handler call.
 *
 * @return 1 if I/O frozen, 0 if not.
 */
int drv_ChpcIsIOFrozen(void);

/**
 * Read all efuses
 *
 * Populates the array provided with the current contents of the efuse shadow registers.
 * Array must be created by the caller and should contain DRV_CHPC_NUM_EFUSES elements.
 *
 * ChipID and CRC fields are masked out for security purposes.
 */
void drv_ChpcReadFuses(unsigned int * fuse_data);

#endif /* #ifndef DRV_CHPC_H */

/** @} END OF FILE */

