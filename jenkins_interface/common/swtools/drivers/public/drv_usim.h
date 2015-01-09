/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usim.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup UsimDriver USIM Driver
 * The USIM driver module handles the interface between SIM manager of the TTPcom L2/L3 and the
 * ARM PrimeCell Smart Card Interface (PL131). It includes also the transport layer to the
 * UICC smart card as defined in the TS 102.221 standard.
 *
 * The physical protocol is handled by the PL131 macrocell.
 * The level of the signals from the PL131 to the USIM is adapted by level shifters in the
 * Trinitario analog chip.
 * The USIM power supply is provided by the Power Management IC.
 *
 * The USIM driver interacts mostly with the protocol stack, so it is running on the DXP1.
 * Nevertheless, the USIM driver communicates with the Trinitario SPI driver how is running on DPX0.
 *
 */

/**
 * @defgroup UsimDriverTask Usim Driver Task
 * @ingroup  UsimDriver
 *
 * This task is interfacing the driver with the SIM manager of the protocol stack.
 * It communicates with other drivers for powering the UICC (@see RfDriverAPI).
 */

/**
 * @defgroup UsimDriverTrans Usim Transport Layer
 * @ingroup  UsimDriver
 */

/**
 * @defgroup UsimDriverArmPl131 Low Level Driver
 * For the ARM PL131 Smart Card Interface
 * @ingroup  UsimDriver
 */

/**
 * @addtogroup UsimDriverTask
 * @{
 */

/**
 * @file drv_usim.h  External Interface of the USIM driver
 *
 */


#ifndef DRV_USIM_H
/**
 * A description of TEMPLATE_H, used to protect against recursive inclusion.
 */
#define DRV_USIM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "l1si_sig.h"
#include "l1ut_sig.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/


/** Compute the number of elements in an array */
#define NB_ELT(_X) (sizeof(_X)/sizeof((_X)[0]))

/** USIM driver task id */
#define DRV_USIM_TASK_ID       L1_SD_QUEUE_ID

//TODO replace by  appropriate ID
#define DRV_TRINI_TASK_ID      0x123456
#define DRV_PWR_TASK_ID        0x123457


/** Default clock value that works for ISO7816 and GSM authentication  */
#define DRV_USIM_3_25_MHZ       3250000

/** Initial Maximun USIM clock frequency in Hz */
#define DRV_USIM_DEFAULT_FMAX   DRV_USIM_3_25_MHZ /* Should be in 1-5MHz range accoring to ISO 7816*/

/** Additional checking for unitest */
#define DRV_USIM_UNITTEST_OPTION 0

/** Option to simulate IRQ when running in dxprun simulation environment */
#define OPTION_SIMULATE_IRQ      0

/** Option to support T=1 Protocol */
#define DRV_USIM_OPTION_SUPPORT_T1      1

/** Option to support T=1 CRC epilogue */
#define DRV_USIM_OPTION_SUPPORT_T1_CRC  0

/** Option for the stop clock feature */
#define DRV_USIM_OPTION_STOP_CLOCK   1

/** Additional genie trace */
#define DRV_USIM_OPTION_EXTRA_TRACE  0

/* following comment converted from doxygen comment to normal code comment */
/* Workaround to fix issue with nortel sim iot issues */
/* Set to 1 to enable */
/* Note this WA breaks SIM test ETSI TS 102 230 (digital), 7.2.5 (Warning) */

#define DRV_USIM_NORTEL_SIM_WORKAROUD  1

/* allow USIM OS logging */
//#define ENABLE_USIM_LOGPOINTS

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef enum
{
    DRV_USIM_ID_0,      /* SIM0 */
    DRV_USIM_ID_1,      /* SIM1 */
    DRV_USIM_ID_INVALID
}DrvUsimId;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**  USIM driver task entry
 *
 */
extern void L1SimDriverTask (void);

/**
 * USIM Power Management Init interface
 * @return void
 */
extern void drv_UsimPmInit();

/**
 * USIM cold boot initialisation performed by drv_init:
 *  - Disable level shifter by default
 *  - Power Management registration
 *
 * NOTE:
 * Remaining USIM initialization is done by L1SimDriverTask on
 * reception og SIG_INITIALISE signal.
 */
extern void drv_UsimInit(void);

/**
 * Return the sim currently being used
 */
extern int drv_UsimGetSimInUse(void);


/**
 * Enable crash on SIM removal feature
 */
extern void drv_UsimCrashOnSimRemoval(bool enabled);

/**
 * Enable crash on SIM controller error feature
 */
extern void drv_UsimCrashOnSimError(bool enabled);

/**
 * For test purpose: indicate if SIM overrun was reached or not.
 */
void drv_UsimTransDbgTestIndicateSimOverrun(int value);

/**
 * For test purpose: get ind if SIM overrun was reached or not
 */
extern int drv_UsimTransDbgTestGetSimOverrunInd(void);

/**
 *  Trigger a SIM controller RX block timeout h/w error - for test purpose.
 */
extern void drv_UsimTriggerRxBlockTimeoutError(void);

/**
 * Update CardState state
 *
 * inserted true when USIM is inserted and false when it is removed
 */
extern void drv_UsimSetCardState(bool inserted);

#endif

/** @} END OF FILE */

