/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_flash.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup FlashDriver Flash Driver
 * @ingroup BoardLevelDrv
 */

/**
 * @addtogroup FlashDriver
 * @{
 */

/**
 * @file drv_flash.h Flash Driver external interfaces
 *
 */

#ifndef DRV_FLASH_H
#define DRV_FLASH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include <icera_global.h>

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Flash dump status
 */
enum drv_FlashDumpStatus
{
    DRV_FLASH_DUMP_OK
    ,DRV_FLASH_DUMP_FAILED            /* Failure dumping data */
    ,DRV_FLASH_DUMP_BAD_BLOCK_IN_BT2  /* Bad block found in BT2 */
    ,DRV_FLASH_DUMP_BAD_BLOCK_0        /* Header block 0 is a bad block */
    ,DRV_FLASH_DUMP_BAD_HEADERS       /* More than 1 bad block in BT2 */
};

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialize the Flash memory, either NOR or NAND
 *
 */
void drv_FlashInit( void );

/**
 * Set Read Only operation to the whole flash
 *
 */
void drv_FlashSetRO( void );

/**
 * Allow Read/Write operation to the whole flash
 *
 */
void drv_FlashSetRW( void );

/**
 * Format flash if required.
 * Only active for NAND devices.
 *
 *
 * @return int 0 on failure, 1 on success.
 */
int drv_FlashFormat( void );

/**
 * Erase a given set of partitions.
 * Here, only the partition(s) used through a filesystem.
 *
 */
void drv_FlashErasePartitions( void );

/**
 * Dump flash memory:
 *  - see each function usage for NOR & NAND
 *  - void *dump_handle is used to allow either a dump in file,
 *    or on host interface, etc...
 *
 * @param MemDumpDataCB callback used to dump data read from
 *                      flash
 * @param dump_handle a pointer to dest (FILE *, serial_hdl,...)
 * @param offset offset in flash
 * @param size size to dump
 * @param FlashProgressCB callback to display dump progress
 * @param FlashOutputCB callback to display status
 * @param force_bb_reading (NAND only) to force bad block
 *                         reading.
 *
 * @return int drv_FlashDumpStatus
 */
int drv_FlashDump(int (*MemDumpDataCB) (void *dump_handle, uint8 *data, int data_size),
                  void *dump_handle,
                  uint32 offset,
                  uint32 size,
                  void (*FlashProgressCB)(int, int),
                  void (*FlashOutputCB)(int, const char *str, ...),
                  int force_bb_reading);

/** 
 * Read amount of BT2 data starting at a given offset.
 * 
 * @param buf
 * @param offset
 * @param len
 * 
 * @return int 0 on failure, 1 on success and buf updated with 
 *         required data.
 */
int drv_FlashReadBt2Data(uint8 *buf, int offset, int len);

/** 
 * Program BT2 archive in flash device.
 * 
 * @param hdr_start
 * @param hdr_size
 * @param file_start
 * @param file_size
 * @param FlashProgressCB
 * 
 * @return int
 */
int drv_FlashBt2Prog(uint8 *hdr_start, 
                     int hdr_size, 
                     uint8 * file_start, 
                     int file_size,
                     void (*FlashProgressCB)(int));
#endif /* #ifndef DRV_FLASH_H */

/** @} END OF FILE */
