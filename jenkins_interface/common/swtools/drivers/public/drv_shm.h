
/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_shm.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DrvShm Shared Memory (IPC) driver
 * @ingroup  Driver
 */

/**
 * @addtogroup DrvShm
 * @{
 */

/**
 * @file drv_shm.h Driver Shared Memory interface
 *       This driver can be used to manage/monitor driver
 *       statistics
 */

#ifndef DRV_SHM_H
#define DRV_SHM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_machine.h"                /* machine definitions */

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** enable for test mode */
#undef DRV_SHM_TEST_MODE

/* IPC MSG format */
#define DRV_SHM_IPC_MSG_SHIFT             16
#define DRV_SHM_IPC_MSG_MASK              0xFFFF

/** Generate IPC MSG */
#define DRV_SHM_IPC_MESSAGE(id)           (((~(id)) << DRV_SHM_IPC_MSG_SHIFT) | id)

/** Extract IPC ID */
#define DRV_SHM_IPC_ID(msg) (msg & DRV_SHM_IPC_MSG_MASK)

/** Secured zone at RAM start when booting from DRAM:
 *  4KB + 32bytes for specific 64bytes alignment (BT2 header
 *  is considered with fixed 32bytes size...) */
#define DRV_SHM_SECURED_ZONE_SIZE      ((4<<10) + 32)

/** Private window size (64MB)   */
#define DRV_SHM_PRIVATE_WINDOW_SIZE    (64<<20)

/** Start addr for boot buffer of data when booting from DRAM:
 *  right after secured zone */
#define DRV_SHM_BOOT_BUFFER_ADDR       (SEG_EXTUNCACHED_EXT_SDRAM_BASE + DRV_SHM_SECURED_ZONE_SIZE)

/** Start addr for APP f/w: 128KB DRAM start (e.g, 128KB
 *  reserved for secured zone, BT2 & boot config buffer */
#define DRV_SHM_BOOT_APP_START_ADDR    (SEG_EXTUNCACHED_EXT_SDRAM_BASE + (128<<10))

/** Addr for IPC mailbox Set to DRV_SHM_PRIVATE_WINDOW_SIZE from start of SDRAM as in
 *  BROM - TODO: take this from SDK... */
#define DRV_SHM_IPC_BASE_ADDR   (SEG_EXTUNCACHED_EXT_SDRAM_BASE + DRV_SHM_PRIVATE_WINDOW_SIZE)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/** IPC mailbox messages ids */
typedef enum
{
	/** Boot status */
	DRV_SHM_IPC_BOOT_COLD_BOOT_IND=0x01,  /** AP2BROM: Cold boot indication */
	DRV_SHM_IPC_BOOT_FW_REQ,              /** BROM2AP: BROM request F/W at cold boot */
	DRV_SHM_IPC_BOOT_RESTART_FW_REQ,      /** BROM2AP: BROM request F/W after crash
                                       * (e.g IPC_BOOT_COLD_BOOT_IND not found in mailbox) */
	DRV_SHM_IPC_BOOT_FW_CONF,             /** AP2BROM: F/W ready confirmation */
	DRV_SHM_IPC_READY,                    /** BB2AP: runtime IPC state after successfull boot */

	/** Boot errors */
	DRV_SHM_IPC_BOOT_ERROR_BT2_HDR=0x1000,/** BROM2AP: BROM found invalid BT2 header */
	DRV_SHM_IPC_BOOT_ERROR_BT2_SIGN,      /** BROM2AP: BROM failed to SHA1-RSA authenticate BT2 */
	DRV_SHM_IPC_BOOT_ERROR_HWID,          /** BT22AP:  BT2 found invalid H/W ID */
	DRV_SHM_IPC_BOOT_ERROR_APP_HDR,       /** BT22AP:  BT2 found invalid APP header */
	DRV_SHM_IPC_BOOT_ERROR_APP_SIGN,      /** BT22AP:  BT2 failed to SHA1-RSA authenticate APP */
	DRV_SHM_IPC_BOOT_ERROR_INFLATE,       /** BT22AP:  BT2 failed to inflate APP */

	DRV_SHM_IPC_MAX_MSG=0xFFFF            /** Max ID for IPC mailbox message */
}DrvShmIpcMailboxMsgId;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Init function for the Shared Memory module to be called before anything else
 *
 * This function must be called on DXP1
 */
void drv_ShmEarlyInit(void);

/**
* Init function for the Shared Memory module
*
* This function must be called on DXP1
*/
void drv_ShmInit(void);

/**
* Write to Shared Memory mailbox
*
* @param id Message to write to mailbox
*/
void drv_ShmMailboxWrite(DrvShmIpcMailboxMsgId id);

/**
 * Raise BB -> AP IRQ
 */
void drv_ShmDownlinkIrq(void);

/**
 * Handle platfrom s/w reset
 */
void drv_ShmSwReset(void);

/**
 * Initialize serial SHM layer
 *
 */
void drv_ShmSerialInitialize();

/**
 * Return Serial index associated with SHM id
 */
int drv_ShmSerialGetSerialId(int shm_id);

/**
 * SHM Test bench
 */
extern void drv_ShmTestBench(void);

/**
 * SHM mailbox writting.
 *
 * @param id
 */
extern void drv_ShmTestMailboxWrite(DrvShmIpcMailboxMsgId id);

/**
 * SHM IRQ enabling
 *
 */
extern void drv_ShmEnableIrq(void);

/**
 * SHM IRQ clear
 *
 */
extern void drv_ShmClearIrq(void);

/**
 * SHM Flush coalescing buffer
 *
 */
extern void drv_ShmFlushCoalescingBuffer(void);
#endif /* #ifndef DRV_SHM_H */

/** @} END OF FILE */

