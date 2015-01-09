/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_sar_ad7146.h#1 $
 * $Date: 2014/11/13 $
 * $Revision: #1 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup SARDriver SAR Driver
 */

/**
 * @addtogroup SARDriver
 * @{
 */

/**
 * @file drv_sar_ad7146.h SAR Driver interface 
 * 
 */


#ifndef DRV_SAR_AD7146_H
#define DRV_SAR_AD7146_H
/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
//****************************************************************************
//
//                                  DEFINES
//
//****************************************************************************
#define SAR_SLAVE_ADDR                       (0x2C) // 7 bit address
#define SAR_REVISION_CODE                    (0x0)
#define SAR_DEVICE_ID                        (0x149)
#define SAR_DEVICE_ID_REGISTER_EXPECTED_VALUE (0x1490)
#define NUM_BYTES_PER_REGISTER               (2)        
#define NUM_CONTINGUOUS_INTERRUPT_STATUS_REGISTERS  (3)
#define SAR_INTERRUPT_STATUS_SIZE            (NUM_CONTINGUOUS_INTERRUPT_STATUS_REGISTERS * NUM_BYTES_PER_REGISTER)
#define NUM_CONTINGUOUS_INTERRUPT_ENABLE_REGISTERS  (3)
#define SAR_INTERRUPT_ENABLE_SIZE            (NUM_CONTINGUOUS_INTERRUPT_ENABLE_REGISTERS * NUM_BYTES_PER_REGISTER)

#define SAR_NUM_STAGE_CONFIG_REGISTERS       (16)
#define SAR_STAGE_CONFIG_SIZE                (SAR_NUM_STAGE_CONFIG_REGISTERS * NUM_BYTES_PER_REGISTER)
#define SAR_NUM_CONTROL_REGISTERS            (8)
#define SAR_CONTROL_SIZE                     (SAR_NUM_CONTROL_REGISTERS * NUM_BYTES_PER_REGISTER)

//----------------------------------------------------------------------------
//
//                          register addresses
//
//----------------------------------------------------------------------------
#define SAR_POWER_CONTROL_REG                (0x0000)
#define SAR_STAGE_CAL_ENABLE_REG             (0x0001)
#define SAR_AMB_COMP_CTRL0_REG               (0x0002)
#define SAR_AMB_COMP_CTRL1_REG               (0x0003)
#define SAR_AMB_COMP_CTRL2_REG               (0x0004)
#define SAR_STAGE_LOW_INT_ENABLE_REG         (0x0005)
#define SAR_STAGE_HIGH_INT_ENABLE_REG        (0x0006)
#define SAR_STAGE_COMPLETE_INT_ENABLE_REG    (0x0007)
#define SAR_STAGE_LOW_INT_STATUS_REG         (0x0008)
#define SAR_STAGE_HIGH_INT_STATUS_REG        (0x0009)
#define SAR_STAGE_COMPLETE_INT_STATUS_REG    (0x000A)
#define SAR_CDC_RESULT_S0_REG                (0x000B)
#define SAR_CDC_RESULT_S1_REG                (0x000C)
#define SAR_CDC_RESULT_S2_REG                (0x000D)
#define SAR_CDC_RESULT_S3_REG                (0x000E)
#define SAR_CDC_RESULT_S4_REG                (0x000F)
#define SAR_CDC_RESULT_S5_REG                (0x0010)
#define SAR_CDC_RESULT_S6_REG                (0x0011)
#define SAR_CDC_RESULT_S7_REG                (0x0012)
#define SAR_CDC_RESULT_S8_REG                (0x0013)
#define SAR_CDC_RESULT_S9_REG                (0x0014)
#define SAR_CDC_RESULT_S10_REG               (0x0015)
#define SAR_CDC_RESULT_S11_REG               (0x0016)
#define SAR_ID_REG_ADDR                      (0x0017)
#define SAR_PROX_STATUS_REG                  (0x0042)


#define SAR_STAGE0_CONNECTION_CIN_6_0_REG    (0x0080)
#define SAR_STAGE0_CONNECTION_CIN_12_7_REG   (0x0081)
#define SAR_STAGE0_AFE_OFFSET_REG            (0x0082)
#define SAR_STAGE0_SENSITIVITY_REG           (0x0083)
#define SAR_STAGE0_OFFSET_LOW_REG            (0x0084)
#define SAR_STAGE0_OFFSET_HIGH_REG           (0x0085)
#define SAR_STAGE0_OFFSET_HIGH_CLAMP_REG     (0x0086)
#define SAR_STAGE0_OFFSET_LOW_CLAMP_REG      (0x0087)

#define SAR_STAGE1_CONNECTION_CIN_6_0_REG    (0x0088)
#define SAR_STAGE1_CONNECTION_CIN_12_7_REG   (0x0089)
#define SAR_STAGE1_AFE_OFFSET_REG            (0x008A)
#define SAR_STAGE1_SENSITIVITY_REG           (0x008B)
#define SAR_STAGE1_OFFSET_LOW_REG            (0x008C)
#define SAR_STAGE1_OFFSET_HIGH_REG           (0x008D)
#define SAR_STAGE1_OFFSET_HIGH_CLAMP_REG     (0x008E)
#define SAR_STAGE1_OFFSET_LOW_CLAMP_REG      (0x008F)

#define SAR_STAGE2_CONNECTION_CIN_6_0_REG    (0x0090)
#define SAR_STAGE2_CONNECTION_CIN_12_7_REG   (0x0091)
#define SAR_STAGE2_AFE_OFFSET_REG            (0x0092)
#define SAR_STAGE2_SENSITIVITY_REG           (0x0093)
#define SAR_STAGE2_OFFSET_LOW_REG            (0x0094)
#define SAR_STAGE2_OFFSET_HIGH_REG           (0x0095)
#define SAR_STAGE2_OFFSET_HIGH_CLAMP_REG     (0x0096)
#define SAR_STAGE2_OFFSET_LOW_CLAMP_REG      (0x0097)

#define SAR_STAGE3_CONNECTION_CIN_6_0_REG    (0x0098)
#define SAR_STAGE3_CONNECTION_CIN_12_7_REG   (0x0099)
#define SAR_STAGE3_AFE_OFFSET_REG            (0x009A)
#define SAR_STAGE3_SENSITIVITY_REG           (0x009B)
#define SAR_STAGE3_OFFSET_LOW_REG            (0x009C)
#define SAR_STAGE3_OFFSET_HIGH_REG           (0x009D)
#define SAR_STAGE3_OFFSET_HIGH_CLAMP_REG     (0x009E)
#define SAR_STAGE3_OFFSET_LOW_CLAMP_REG      (0x009F)

#define SAR_STAGE4_CONNECTION_CIN_6_0_REG    (0x00A0)
#define SAR_STAGE4_CONNECTION_CIN_12_7_REG   (0x00A1)
#define SAR_STAGE4_AFE_OFFSET_REG            (0x00A2)
#define SAR_STAGE4_SENSITIVITY_REG           (0x00A3)
#define SAR_STAGE4_OFFSET_LOW_REG            (0x00A4)
#define SAR_STAGE4_OFFSET_HIGH_REG           (0x00A5)
#define SAR_STAGE4_OFFSET_HIGH_CLAMP_REG     (0x00A6)
#define SAR_STAGE4_OFFSET_LOW_CLAMP_REG      (0x00A7)

#define SAR_STAGE5_CONNECTION_CIN_6_0_REG    (0x00A8)
#define SAR_STAGE5_CONNECTION_CIN_12_7_REG   (0x00A9)
#define SAR_STAGE5_AFE_OFFSET_REG            (0x00AA)
#define SAR_STAGE5_SENSITIVITY_REG           (0x00AB)
#define SAR_STAGE5_OFFSET_LOW_REG            (0x00AC)
#define SAR_STAGE5_OFFSET_HIGH_REG           (0x00AD)
#define SAR_STAGE5_OFFSET_HIGH_CLAMP_REG     (0x00AE)
#define SAR_STAGE5_OFFSET_LOW_CLAMP_REG      (0x00AF)

#define SAR_STAGE6_CONNECTION_CIN_6_0_REG    (0x00B0)
#define SAR_STAGE6_CONNECTION_CIN_12_7_REG   (0x00B1)
#define SAR_STAGE6_AFE_OFFSET_REG            (0x00B2)
#define SAR_STAGE6_SENSITIVITY_REG           (0x00B3)
#define SAR_STAGE6_OFFSET_LOW_REG            (0x00B4)
#define SAR_STAGE6_OFFSET_HIGH_REG           (0x00B5)
#define SAR_STAGE6_OFFSET_HIGH_CLAMP_REG     (0x00B6)
#define SAR_STAGE6_OFFSET_LOW_CLAMP_REG      (0x00B7)

#define SAR_STAGE7_CONNECTION_CIN_6_0_REG    (0x00B8)
#define SAR_STAGE7_CONNECTION_CIN_12_7_REG   (0x00B9)
#define SAR_STAGE7_AFE_OFFSET_REG            (0x00BA)
#define SAR_STAGE7_SENSITIVITY_REG           (0x00BB)
#define SAR_STAGE7_OFFSET_LOW_REG            (0x00BC)
#define SAR_STAGE7_OFFSET_HIGH_REG           (0x00BD)
#define SAR_STAGE7_OFFSET_HIGH_CLAMP_REG     (0x00BE)
#define SAR_STAGE7_OFFSET_LOW_CLAMP_REG      (0x00BF)

#define SAR_STAGE8_CONNECTION_CIN_6_0_REG    (0x00C0)
#define SAR_STAGE8_CONNECTION_CIN_12_7_REG   (0x00C1)
#define SAR_STAGE8_AFE_OFFSET_REG            (0x00C2)
#define SAR_STAGE8_SENSITIVITY_REG           (0x00C3)
#define SAR_STAGE8_OFFSET_LOW_REG            (0x00C4)
#define SAR_STAGE8_OFFSET_HIGH_REG           (0x00C5)
#define SAR_STAGE8_OFFSET_HIGH_CLAMP_REG     (0x00C6)
#define SAR_STAGE8_OFFSET_LOW_CLAMP_REG      (0x00C7)

#define SAR_STAGE9_CONNECTION_CIN_6_0_REG    (0x00C8)
#define SAR_STAGE9_CONNECTION_CIN_12_7_REG   (0x00C9)
#define SAR_STAGE9_AFE_OFFSET_REG            (0x00CA)
#define SAR_STAGE9_SENSITIVITY_REG           (0x00CB)
#define SAR_STAGE9_OFFSET_LOW_REG            (0x00CC)
#define SAR_STAGE9_OFFSET_HIGH_REG           (0x00CD)
#define SAR_STAGE9_OFFSET_HIGH_CLAMP_REG     (0x00CE)
#define SAR_STAGE9_OFFSET_LOW_CLAMP_REG      (0x00CF)

#define SAR_STAGE10_CONNECTION_CIN_6_0_REG    (0x00D0)
#define SAR_STAGE10_CONNECTION_CIN_12_7_REG   (0x00D1)
#define SAR_STAGE10_AFE_OFFSET_REG            (0x00D2)
#define SAR_STAGE10_SENSITIVITY_REG           (0x00D3)
#define SAR_STAGE10_OFFSET_LOW_REG            (0x00D4)
#define SAR_STAGE10_OFFSET_HIGH_REG           (0x00D5)
#define SAR_STAGE10_OFFSET_HIGH_CLAMP_REG     (0x00D6)
#define SAR_STAGE10_OFFSET_LOW_CLAMP_REG      (0x00D7)

#define SAR_STAGE11_CONNECTION_CIN_6_0_REG    (0x00D8)
#define SAR_STAGE11_CONNECTION_CIN_12_7_REG   (0x00D9)
#define SAR_STAGE11_AFE_OFFSET_REG            (0x00DA)
#define SAR_STAGE11_SENSITIVITY_REG           (0x00DB)
#define SAR_STAGE11_OFFSET_LOW_REG            (0x00DC)
#define SAR_STAGE11_OFFSET_HIGH_REG           (0x00DD)
#define SAR_STAGE11_OFFSET_HIGH_CLAMP_REG     (0x00DE)
#define SAR_STAGE11_OFFSET_LOW_CLAMP_REG      (0x00DF)

#define SAR_STAGE0_SF_AMBIENT_REG            (0x00F1)

//----------------------------------------------------------------------------
//
//                          register values
//
//----------------------------------------------------------------------------

// Ideally want raw counts to be 10,000 when nothing is nearby which is 0x2710
// This is because the counts will only get bigger.  Stay way less than half-scale
// = 0x7fff

// stage 0 = proximity pad - CIN12
#define SAR_STAGE0_CIN_6_0_INIT         0x3fff     // register 0x80 
#define SAR_STAGE0_CIN_12_7_INIT        0x0bff     // register 0x81

// stage 1 = guard trace = CIN11
#define SAR_STAGE1_CIN_6_0_INIT         0x3fff     // register 0x88 
#define SAR_STAGE1_CIN_12_7_INIT        0x0eff     // register 0x89

// stage 2 = not used except as a dummy delay to slow
// down the stage complete interrupt timing
#define SAR_STAGE2_CIN_6_0_INIT         0x3fff     // register 0x90
#define SAR_STAGE2_CIN_12_7_INIT        0x0fff     // register 0x91

// stage 3 = not used except as a dummy delay to slow
// down the stage complete interrupt timing
#define SAR_STAGE3_CIN_6_0_INIT         0x3fff     // register 0x98 
#define SAR_STAGE3_CIN_12_7_INIT        0x0fff     // register 0x99

// stage 4 = not used except as a dummy delay to slow
// down the stage complete interrupt timing
#define SAR_STAGE4_CIN_6_0_INIT         0x3fff    // register 0xa0 
#define SAR_STAGE4_CIN_12_7_INIT        0x0fff     // register 0xa1

// stage 5 = not used except as a dummy delay to slow
// down the stage complete interrupt timing
#define SAR_STAGE5_CIN_6_0_INIT         0x3fff     // register 0xa8 
#define SAR_STAGE5_CIN_12_7_INIT        0x0fff     // register 0xa9

// Note below: AFE offset is zeroed out.  It has to be set
// to factory cal values.

// sensor pad #1 
#define SAR_STAGE0_AFE_OFFSET           0x1d00     // register 0x82
#define SAR_STAGE0_SENSITIVITY          0x2626     // register 0x83

// sensor pad #2
#define SAR_STAGE1_AFE_OFFSET           0x1700     // register 0x8a
#define SAR_STAGE1_SENSITIVITY          0x2626     // register 0x8b

// sensor pad #3
#define SAR_STAGE2_AFE_OFFSET           0x0000     // register 0x8a
#define SAR_STAGE2_SENSITIVITY          0x2626     // register 0x8b

// sensor pad #4
#define SAR_STAGE3_AFE_OFFSET           0x0000     // register 0x8a
#define SAR_STAGE3_SENSITIVITY          0x2626     // register 0x8b

// sensor pad #5
#define SAR_STAGE4_AFE_OFFSET           0x0000     // register 0x8a
#define SAR_STAGE4_SENSITIVITY          0x2626     // register 0x8b

// sensor pad #6
#define SAR_STAGE5_AFE_OFFSET           0x0000     // register 0x8a
#define SAR_STAGE5_SENSITIVITY          0x2626     // register 0x8b


#define POWER_MODE_MASK                  0x0000000f
#define SLOW_POLL                        0x0000000e
#define FAST_POLL                        0x00000000

// 2 pads: 1 prox pad + 1 temp/humidity pad
#define SAR_POWER_CONTROL_FASTPOLL      0xc050     // register 0
#define SAR_POWER_CONTROL               SAR_POWER_CONTROL_FASTPOLL
#define SAR_ENABLE                      SAR_POWER_CONTROL_FASTPOLL
#define SAR_DISABLE                     0xc053

#define SAR_SOFTWARE_RESET              0xc400     // register 1
#define DRV_SAR_AD7146_RESET_VALUE      0xC4
#define SAR_STAGE_CAL_DISABLE           0x0000     // register 1
#define SAR_STAGE_CAL_ENABLE            0x0001     // register 1
#define SAR_AMB_COMP_CTRL0              0x3230     // register 2 
#define SAR_AMB_COMP_CTRL1              0x0419     // register 3 
#define SAR_AMB_COMP_CTRL2              0x0832     // register 4 
#define SAR_STAGE_LOW_INT_DISABLE       0x0000     // register 5
#define SAR_STAGE_HIGH_INT_DISABLE      0x0000     // register 6
#define SAR_STAGE_HIGH_INT_ENABLE       0x0001     // register 6

#define SAR_STAGE_COMPLETE_INT_DISABLE  0x0000     // register 7
#define SAR_STAGE_COMPLETE_INT_ENABLE   0x0020     // register 7

// Golden cal values
#define SAR_GOLDEN_VALUE_SF_AMBIENT     0x21c5    // register 0xF1

/* I2C sizes */
#define DRV_SAR_AD7146_MAX_TRANSFERT   4
/* standard write size (2 bytes address + 2 bytes data)*/
#define DRV_SAR_AD7146_WRITE_SIZE  2 

/* I2C sequence table max size */
#define DRV_SAR_AD7146_SEQUENCE_TABLE_MAX_SIZE (100)

/* Events bit field */
#define DRV_SAR_AD7146_INT_FIRED         BIT(0)
#define DRV_SAR_AD7146_SAR_ENABLE        BIT(1)
#define DRV_SAR_AD7146_SAR_DISABLE       BIT(2)
#define DRV_SAR_AD7146_I2C_ACCESS        BIT(3)
#define DRV_SAR_AD7146_INIT              BIT(4)
#define DRV_SAR_AD7146_T40_TRIG_ENABLE   BIT(5)
#define DRV_SAR_AD7146_T40_TRIG_DISABLE  BIT(6)
#define DRV_SAR_AD7146_HUMAN_DET_ENABLE  BIT(7)
#define DRV_SAR_AD7146_HUMAN_DET_DISABLE BIT(8)
#define DRV_SAR_AD7146_BACKOFF_ENABLE    BIT(9)
#define DRV_SAR_AD7146_BACKOFF_DISABLE   BIT(10)
#define DRV_SAR_AD7146_TRIGGER_NOTIF_ENABLE  BIT(11)
#define DRV_SAR_AD7146_TRIGGER_NOTIF_DISABLE BIT(12)
#define DRV_SAR_AD7146_I2C_READ              BIT(13)
#define DRV_SAR_AD7146_I2C_WRITE             BIT(14)
#define DRV_SAR_AD7146_SAR_ALGO_ENABLE       BIT(15)
#define DRV_SAR_AD7146_SAR_ALGO_DISABLE      BIT(16)
#define DRV_SAR_AD7146_SAR_AUTO_TUNE         BIT(17)
#define DRV_SAR_AD7146_SAR_GET_SAR_CONFIG    BIT(18)
#define DRV_SAR_AD7146_SAR_FORCE_ALGO        BIT(19)
#define DRV_SAR_AD7146_SAR_FORCE_TX_BACKOFF  BIT(20)



/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  Type definition for the SAR detect notification callback
 *
 *  The notification callback is called when the SAR condition changes
 *  It is called in the context of an interrupt service routine and must *NOT* block.
 *
 *  @param value     one if SAR condition detected, else zero
 */
typedef void (*drv_sarAd7146SarDetCallback)(uint32 value);

typedef enum
{
  DRV_SAR_AD7146_INIT_NOT_PERFORMED,
  DRV_SAR_AD7146_INIT_SUCCESS,
  DRV_SAR_AD7146_INIT_FAIL,
  DRV_SAR_AD7146_INIT_NO_CAL, 
  DRV_SAR_AD7146_INIT_SAR_DISABLED
} drv_sarAD7146_init_state_t;


typedef enum
{
  DRV_SAR_AD7146_NO_EVENT_ID = 0,
  DRV_SAR_AD7146_INIT_STATUS_ID,
  DRV_SAR_AD7146_SAR_ALGO_ENABLE_ID,
  DRV_SAR_AD7146_SAR_ALGO_DISABLE_ID,
  DRV_SAR_AD7146_T40_TRIG_DISABLE_ID,
  DRV_SAR_AD7146_T40_TRIG_ENABLE_ID,
  DRV_SAR_AD7146_HUMAN_DET_ENABLE_ID,
  DRV_SAR_AD7146_HUMAN_DET_DISABLE_ID,
  DRV_SAR_AD7146_BACKOFF_ENABLE_ID,
  DRV_SAR_AD7146_BACKOFF_DISABLE_ID,
  DRV_SAR_AD7146_TRIGGER_NOTIF_ENABLE_ID,
  DRV_SAR_AD7146_TRIGGER_NOTIF_DISABLE_ID,
  DRV_SAR_AD7146_I2C_READ_ID,
  DRV_SAR_AD7146_I2C_WRITE_ID,
  DRV_SAR_AD7146_DETECT_SAR_ON_ID,
  DRV_SAR_AD7146_DETECT_SAR_OFF_ID,
  DRV_SAR_AD7146_SAR_AUTO_TUNE_ID,
  DRV_SAR_AD7146_SAR_GET_SAR_CONFIG_ID,
  DRV_SAR_AD7146_SAR_FORCE_ALGO_ID,
  DRV_SAR_AD7146_SAR_REPORT_ERROR_ID,
  DRV_SAR_AD7146_SAR_FORCE_TX_BACKOFF_ID
}drv_sarAd7146_event_type;


typedef enum
{
  DRV_SAR_AD7146_ERR_REP_NO_CALIBRATION_FILE    = BIT(0),
  DRV_SAR_AD7146_ERR_REP_CRC_ERROR_CAL_FILE     = BIT(1),
  DRV_SAR_AD7146_ERR_REP_CORRUPTED_CAL_FILE 	  = BIT(2),
  DRV_SAR_AD7146_ERR_REP_SPARE_1 	              = BIT(3),
  DRV_SAR_AD7146_ERR_REP_SPARE_2                = BIT(4),
  DRV_SAR_AD7146_ERR_REP_I2C_WRITE_FAILURE      = BIT(5),
  DRV_SAR_AD7146_ERR_REP_RAW_COUNT_VAL_OVERFLOW = BIT(6),
  DRV_SAR_AD7146_ERR_REP_CAL_AFE_OVERFLOW	      = BIT(7),
  DRV_SAR_AD7146_ERR_REP_AD7146_COMM_ERROR 	    = BIT(8),
  
} drv_sarAd7146_error_t;

typedef enum
{
  DRV_SAR_AD7146_FAILED,
  DRV_SAR_AD7146_SUCCESS,
}drv_sarAd7146_operation_status;

typedef struct 
{
  uint16 reg_addr;
  uint16 reg_value;
} drv_sarAd7146_register_list;

#define DRV_SAR_AD7146_MAX_REGISTER_LIST_SIZE (20)
#define DRV_SAR_AD7146_MAX_AFE_REGISTER_LIST_SIZE (12)

typedef struct 
{
  uint16 number_of_reg;
  bool   isLastList;
  drv_sarAd7146_register_list list[DRV_SAR_AD7146_MAX_REGISTER_LIST_SIZE];
} drv_sarAd7146_read_register_list;

typedef enum
{
  DRV_SAR_AD7146_NO_MODE_SELECTED,
  DRV_SAR_AD7146_FREE_SPACE,
  DRV_SAR_AD7146_ACTIVE_TUNING,
  DRV_SAR_AD7146_RETURN_TUNE_VALUES
}drv_sarAd7146_auto_tune_mode_t;


typedef struct 
{
  drv_sarAd7146_auto_tune_mode_t lastModeRequested;
  drv_sarAd7146_register_list afeList[DRV_SAR_AD7146_MAX_AFE_REGISTER_LIST_SIZE];
  uint32 proximity;
  uint32 compensation;
  uint32 proximity_gain;
  uint32 static_threshold;
} drv_sarAD7146_tune_values_t;

typedef struct 
{
  drv_sarAd7146_register_list afeList[DRV_SAR_AD7146_MAX_AFE_REGISTER_LIST_SIZE];
  uint32 proximity;
  uint32 compensation;
  uint32 proximity_gain;
  uint32 static_threshold;
} drv_sarAD7146_calibration_data_t;

typedef enum
{
  DRV_SAR_AD7146_CAL_OP_NOP,
  DRV_SAR_AD7146_CAL_OP_WRITE_SUCCESS,
  DRV_SAR_AD7146_CAL_OP_READ_SUCCESS,
  DRV_SAR_AD7146_CAL_OP_WRITE_ERR,
  DRV_SAR_AD7146_CAL_OP_WRITE_CLOSE_ERR,
  DRV_SAR_AD7146_CAL_OP_WRITE_OPEN_ERR,
  DRV_SAR_AD7146_CAL_OP_READ_CRC_ERR,
  DRV_SAR_AD7146_CAL_OP_READ_ERR,
  DRV_SAR_AD7146_CAL_OP_READ_DATA_ERR,
  DRV_SAR_AD7146_CAL_OP_READ_CLOSE_ERR,
  DRV_SAR_AD7146_CAL_OP_READ_OPEN_ERR
}drv_sarAd7146_calibration_status_t;

typedef struct 
{
	/*
	 * Enable / Disable the MDM_SAR_IND GPIO toggling. Can be overwritten by PC or %ISARCONTROL
	 */
	bool T40Notification;
	/*
	 * Enable / Disable the Human Detection algo. Can be overwritten by PC or %ISARCONTROL
	 */
	bool SARHumanDetection;
	/*
	 * Enable / Disable the Backoff Signalling to Protocol Stack. Can be overwritten by PC or %ISARCONTROL
	 */ 
	bool SARBackoff;
	/*
	 * Enable / Disable the %ISARDETECT unsolicited triggering. Can be overwritten by PC or %ISARCONTROL
	 */ 
	bool SARTriggerDetect;
	/*
	 * Enable / Disable the SAR Algo and mask AD7146 Interrupts. Can be overwritten %ISARCONTROL
	 */   
	int SARAlgoControl;
	/*
	 * Active / deactivate the Tx Backoff (current state). Can be overwritten %ISARCONTROL
	 */  
	bool backoff_on;

} drv_sarAD7146_sar_config_t;

typedef union
{
  drv_sarAd7146_read_register_list read_register_list;
  drv_sarAD7146_init_state_t       init_state;
  drv_sarAD7146_tune_values_t      tune_values;
  drv_sarAD7146_sar_config_t       config;
  uint32                           error_reporting;
} drv_sar1d7146_operation_params;

typedef struct 
{
  drv_sarAd7146_operation_status operationStatus;  
  drv_sar1d7146_operation_params params;
}drv_sarAd7146_ack_params;


typedef void (*drv_sarAd7146SarAckCallback)(drv_sarAd7146_event_type event_type, 
	                                               drv_sarAd7146_ack_params *params);

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * Initialise the SAR detect I/O driver
 *
 * This configures the I/O, enables extWake events on the I/O
 * and registers an interrupt handler to dispatch I/O toggle
 * notifications to a registered listener
 *
 * @see drv_SarDetRegisterNotificationCallback()
 * @return none
 */
extern void drv_sarAd7146Init(void);
extern void drv_sarAd7146ReInit(void);

extern void drv_sarAd7146Reset(void);

extern void drv_sarAd7146EnableSar(void);
extern void drv_sarAd7146DisableSar(void);
extern void drv_sarAd7146TxIndication(int val);

extern void drv_sarAd7146ReadI2C(uint16 reg_addr, uint16 *data_out, uint8 length);
extern void drv_sarAd7146WriteI2C(uint16 reg_addr, uint16 reg_val);

/**
 * Register a notification callback for the SAR detect I/O
 *
 * @see drv_SarDetCallback
 * @param callback Pointer to the notification callback
 * @return none
 */
extern void drv_SarDetRegisterNotificationCallback_Ad7146(drv_sarAd7146SarDetCallback callback);

extern void drv_SarDetRegisterAcknowledgementCallback_Ad7146(drv_sarAd7146SarAckCallback callback);

extern void drv_sarAd7146EnableT40TriggerNotif(void);

extern void drv_sarAd7146DisableT40TriggerNotif(void);

extern void drv_sarAd7146EnableHumanDetection(void);

extern void drv_sarAd7146DisableHumanDetection(void);

extern void drv_sarAd7146EnableControlBackoff(void);

extern void drv_sarAd7146DisableControlBackoff(void);

extern void drv_sarAd7146EnableTriggerNotification(void);
	
extern void drv_sarAd7146DisableTriggerNotification(void);

extern bool drv_sarAd7146PerfomReadI2cSequence(uint16 reg_addr, uint16 reg_number);

extern bool drv_sarAd7146PerfomWriteI2cSequence(uint16 reg_addr, uint16 reg_value);

extern void drv_sarAd7146EnableSarAlgo(void);

extern void drv_sarAd7146DisableSarAlgo(void);

extern uint8 drv_sarAd7146getInterruptValue(void);

extern bool drv_sarAd7146RunAutoTune(drv_sarAd7146_auto_tune_mode_t mode);

extern void drv_sarAd7146GetSarConfig(void);

extern void drv_sarAd7146ForceSarAlgo(void);

extern drv_sarAd7146_calibration_status_t drv_sarAd7146WriteCalibrationData(drv_sarAD7146_calibration_data_t *data);

extern drv_sarAd7146_calibration_status_t drv_sarAd7146ReadCalibrationData(drv_sarAD7146_calibration_data_t* data_p);

extern bool drv_sarAd7146ForceTxBackoff(bool on);

extern void drv_sarAd7146RemoveCalibrationData(void);
#endif

/** @} END OF FILE */
