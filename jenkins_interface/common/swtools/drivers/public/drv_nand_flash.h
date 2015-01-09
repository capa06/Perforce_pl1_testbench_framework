/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_nand_flash.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup NandFlashDriver Nand Flash Driver
 * @ingroup BoardLevelDrv
 */

/**
 * @addtogroup Nand FlashDriver
 * @{
 */

/**
 * @file drv_nand_flash.h Nand Flash Driver external interfaces
 *
 */

#ifndef DRV_NAND_FLASH_H
#define DRV_NAND_FLASH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_mphal_nand.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef struct
{
    const int  manufacturer_id;
    const int  device_id;
    const int  eccID;
    const int  eccSel;
    const int  x16;
    const int  page_size;
    const int  page_per_block;
    const int  block_count;
    const int  random_read_write_support;
    const mphalnandt_InitialBadBlockKind bad_block_scheme;
    const char name[32];
} NandDeviceDesc;

typedef struct
{
    mphalnandt_Handle *mphal_nand_handle;
    const NandDeviceDesc *nand_device_desc;
} DrvNandHandle;

/**
 * Identifiers of NAND flash code/data partitions
 */
enum drv_NandMapPartId
{
    DRV_NAND_MAP_PARTITION_ID__BT2               /** BT2 storage partition */
    ,DRV_NAND_MAP_PARTITION_ID__PARTITION_1	     /** First VFS partition  */
    ,DRV_NAND_MAP_PARTITION_ID__BACKUP_PARTITION /** VFS backup partition */
    ,DRV_NAND_MAP_PARTITION_ID__PARTITION_2      /** Second VFS partition */
    ,DRV_NAND_MAP_PARTITION_ID__RFU_CUST         /** RFU for customer partition */
    ,DRV_NAND_MAP_PARTITION_ID__LAST
};

/**
 * NAND partition definition structure. Contains details of each ICERA defined memory partitions.
 */
struct NandPartition
{
    int                 start_block;  /**< Partition start block */
    int                 block_count;  /**< Partition size in blocks */
};

/**
 * NAND map definition structure. Contains mapping details for a
 * fixed geometry NAND device.
 *
 * partition_ptr indicates start block of the mapping table
 * max_id indicates the number of partitions for this table.
 *
 */
struct NandMap
{
    struct NandPartition *partition_ptr;
    int max_id;
};

/**
 * NAND map table deinition structure. Contains all the mapping
 * details for all existing NAND device geometry if supported.
 *
 */
struct NandMapTable
{
    struct NandMap map_128K_256MB;
    struct NandMap map_128K_128MB;
    struct NandMap map_16K_128MB;
    struct NandMap map_16K_64MB;
};

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern DrvNandHandle *drv_nand_handle;

/**
 * NAND mapping is platform dependant. Each h/w platform defines
 * its own struct NandMapTable that will contain all supported geometry
 * struct NandMap.
 *
 */
extern const struct NandMapTable hwplat_nand_map_table;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 *  Format NAND device: build Icera NAND headers with NAND bad block bitmap.
 *
 * @return int 1 if ok
 */
int drv_NandFormat(void);

/**
 *  Erase main file system partition and additional zero-cd
 *  partition if required.
 *
 */
void drv_NandErasePartitions(void);

/**
 * Initialize the NAND Flash memory
 *
 */
void drv_NandInitDevice( void );

/**
 * Initialize the NAND Flash partition mapping
 *
 * @param nand_device_desc
 */
void drv_NandInitMap(const NandDeviceDesc *nand_device_desc);

/**
 * Get partition start block
 *
 * @param segment_id
 *
 * @return uint32 start block
 */
uint32 drv_NandGetPartitionStartBlock(enum drv_NandMapPartId partition_id);

/**
 * Get partition num of blocks
 *
 * @param partition_id
 *
 * @return uint32 block count
 */
uint32 drv_NandGetPartitionBlockCount(enum drv_NandMapPartId partition_id);

/**
* Register NAND driver to IPM framework
*/
void drv_NandPmInit(void);

/**
 * Dump full NAND device image.
 *
 *  MemDumpDataCB to perform dump data and use void dump_handle
 *  to be either a file descriptor, a serial handle, etc... So
 *  that dump_handle must point to an open file, an initialised
 *  host interface, etc...
 *
 *  Full flash image is automatically dumped disregarding
 *  start_chunk and end_chunk indication.
 *
 *  Flash dump image is built skipping source bad blocks and
 *  replacing them with:
 *  - 0xFF formatted block in normal usage. (force_bb_reading ==
 *    0)
 *  - 0x00 formatted block for debug purpose and better bad
 *    block identification. (force_bb_reading == 1)
 *
 *  If force_bb_reading = 0 and bad block found in BT2, then
 *  dump is stopped and error reported.
 *
 * @param MemDumpDataCB
 * @param dump_handle
 * @param start_chunk
 * @param end_chunk
 * @param FlashProgressCB
 * @param FlashOutputCB
 * @param force_bb_reading
 *
 * @return int drv_FlashDumpStatus
 */
int drv_NandDump(int (*MemDumpDataCB) (void *dump_handle, uint8 *data, int data_size),
                 void *dump_handle,
                 uint32 start_chunk,
                 uint32 end_chunk,
                 void (*FlashProgressCB)(int, int),
                 void (*FlashOutputCB)(int, const char *str, ...),
                 int force_bb_reading);

/**
 * Program the bt2 wrapped file into the NAND flash device.
 *
 * @param hdr_start pointer to BT2 header
 * @param hdr_size BT2 header size
 * @param file_start pointer to BT2 data start (header excluded)
 * @param file_size Size of BT2 data (header excluded)
 *
 * @return int 1 if OK, 0 if FAIL
 */
int drv_NandBt2Prog(uint8 * hdr_start, int hdr_size, uint8 * file_start, int file_size);

/** 
 * Read BT2 data at a given offset for a given BT2 copy. 
 *  
 * Can be used to read entire file (or huge buf) since it 
 * it is not limited to read in one page only. 
 *  
 * @param buf
 * @param offset
 * @param len
 * @param bt2_copy
 * 
 * @return int 0 on failure, 1 on success
 */
int drv_NandReadBt2Data(uint8 *buf, int offset, int len, int bt2_copy);

#endif /* DRV_NAND_FLASH_H */

/** @} END OF FILE */
