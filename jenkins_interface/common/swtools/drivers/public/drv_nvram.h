/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_nvram.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup NvramDriver NVRAM Driver
 * @ingroup SoCLowLevelDrv
 * The NVRAM driver is the Non Volatile Random Access Memory driver.
 * It reads/writes parameters in the flash memory for the protocol stack
 */

/**
 * @addtogroup NvramDriver
 * @{
 */

/**
 * @file drv_nvram.h Public interfaces for NVRAM driver
 *
 */

#ifndef DRV_NVRAM_H
#define DRV_NVRAM_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"
#ifndef HOST_TESTING
#include "dxpnk_api.h"
#endif

#include "drv_arch_type.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#define DRV_RO_NVRAM__MAX_PARAM_SZ      0x400

/* used in  ftcommands/private/int_cal.c for int_AtSerial function
 * and ttpcom/tplgsm/modem/psnas/atci.mod/src/rvnvram.c for vgAtRdSerial function
 */
#define INT_CAL_SERIAL_LENGTH_MAX       32

#define DRV_NVRAM_KB                              1024
#define DRV_NVRAM_RO__MAX_MIRROR_SIZE   (64*DRV_NVRAM_KB)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Identifiers of RO segment data items.
 */

#define DRV_NVRAM_RO_VERSION(MAJ, MIN)
#define DEF_NVRAM_RO_PARAM(ID, FMT)             ID,
#define DEF_NVRAM_RO_PARAM_(ID, FMT, VAL)       ID=VAL,

typedef enum
{
    #include "drv_nvram_ids.h"
}
drv_NvramRoItem;

#undef DRV_NVRAM_RO_VERSION
#undef DEF_NVRAM_RO_PARAM
#undef DEF_NVRAM_RO_PARAM_

typedef enum
{
    DRV_NVRAM_RO_SEGMENT_STATE__OK,
    DRV_NVRAM_RO_SEGMENT_STATE__BAD_VERSION,
    DRV_NVRAM_RO_SEGMENT_STATE__BAD_SIGNATURE,
    DRV_NVRAM_RO_SEGMENT_STATE__BAD_CRC,
    DRV_NVRAM_RO_SEGMENT_STATE__NOT_FOUND
}
drv_NvramRoSegmentState;

/**
 * NVRAM read-only segment information
 */
typedef struct
{
    int                         allocated_param_count;
    int                         allocated_size;
    drv_NvramRoSegmentState     state;
    uint8                       version[2];
}
drv_NvramRoSegmentInfo;

typedef enum
{
   DRV_NVRAM_CAL_PATCH_SUCCESS =0,
   DRV_NVRAM_CAL_PATCH_CAL0_LOAD_ERROR = 1,
   DRV_NVRAM_CAL_PATCH_INSUPPORTED =2,
   DRV_NVRAM_CAL_PATCH_INVALID_ITEM_ID =3,
   DRV_NVRAM_CAL_PATCH_INVALID_ITEM_SIZE =4,
   DRV_NVRAM_CAL_PATCH_CANNOT_CREATE_ITEM =5,
   DRV_NVRAM_CAL_PATCH_CANNOT_DELETE_ITEM =6,
   DRV_NVRAM_CAL_PATCH_CANNOT_WRITE_ITEM =7,
   DRV_NVRAM_CAL_PATCH_CANNOT_UPDATE_NVFILE =8,
   DRV_NVRAM_CAL_PATCH_NO_ITEM_UPDATED =9
}
drv_NvramPatchResults;

typedef struct drv_VolatileParamTag
{
    int     id;         /* volatile parameter identifier */
    uint32  size;       /* volatile parameter size */
    uint8   *data;      /* volatile parameter data */
}
drv_NvramVolatileParam;

typedef struct drv_NonVolatileParamTag
{
    int     id;         /* non volatile parameter identifier */
    uint32  size;       /* non volatile parameter size */
    uint8   data[];     /* non volatile parameter data */
}
drv_NvramNonVolatileParam;


/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Read a data item in RAM MIRROR
 *
 * If the read fail the buffer pointer by item_data is not modified.
 *
 * @param data_dest      destination buffer of the read.
 * @param item_id        identifier of the data item to read.
 * @param item_offset    offset of the data to read in item.
 * @param item_data_sz   size of data to read.
 *
 * @return 1 if read successful, else 0.
 */
extern int drv_NvramRoRead(void *data_dest,
                           int item_id,
                           int item_offset,
                           int item_data_sz);

/**
 * Return a 32-bit parameter from RO NVRAM
 *
 * @param dest
 * @param id
 * @param max_len
 *
 * @return int      : Number of words read
 */
extern int drv_NvramRoGet32(void *dest, int id, int max_len);

/**
 * Get the data size of a paramter.
 *
 * @param item_id item identifier.
 *
 * @return size of the item data field. If the element is not present, the return value is 0.
 */
extern uint16 drv_NvramRoGetSize(int item_id);

/**
 * Create a new item in RAM MIRROR.
 *
 * @param item_id   item identifier.
 * @param data_sz   size of item data.
 *
 * @return 1 if operation successful, else 0.
 */
extern int drv_NvramRoNew(int item_id,
                          uint32 data_sz);

/**
 * Remove an existing item from RAM MIRROR.
 *
 * @param item_id   item identifier.
 *
 * @return 1 if operation successful, else 0.
 */
extern int drv_NvramRoDelete(int item_id);

/**
 * Write data in an existing parameter of the RAM MIRROR
 *
 * @param data_src      write data source.
 * @param item_id       dest item identifier.
 * @param dest_offset   dest offset in item data.
 * @param data_sz       size of data to write.
 *
 * @return 1 if write successful, else 0.
 */
extern int drv_NvramRoWrite(void *data_src,
                            int item_id,
                            int dest_offset,
                            int data_sz);

/**
 * Erase a NVRAM segment.
 *
 * @param id  identifier of the NVRAM segment to erase
 *
 * @return 1 if erase successful, else 0.
 */
extern int drv_NvramRoEraseSegment(int id);

/**
 * Initialise RO data segment.

 * Initialise RO data segment context and internal data.
 */
extern void drv_NvramRoInit(void);

/**
 * Load RAM MIRROR from NVRAM segment.
 *
 * @param id  identifier of the source NVRAM segment
 *
 * @return 1 if load successful, else 0.
 */
extern int drv_NvramRoLoadMirror(int id);

/**
 * Flush a NVRAM segment to RAM MIRROR.
 *
 * @param id  identifier of the destination NVRAM segment
 *
 * @return 1 if flush successful, else 0.
 */
extern int drv_NvramRoFlushMirror(int id);

/**
 * Erase all NVRAM segments, clear out RAM MIRROR.
 *
 * @return 1 if erase successful, else 0.
 */
extern int drv_NvramRoEraseAll(void);

/**
 * Erase NVRAM MIRROR.
 *
 * @return 1 if erase successful, else 0.
 */
extern int drv_NvramRoClearMirror(void);

/**
 * Get number of RO NVRAM segments (statically allocated).
 *
 * @return the number of RO NVRAM segments.
 */
extern int drv_NvramRoGetSegmentCount(void);

/**
 * Get the MIRROR info.
 *
 * @return the info of the MIRROR.
 */
extern drv_NvramRoSegmentInfo *drv_NvramRoGetMirrorInfo(void);

/**
 * Get the NVRAM segment info.
 *
 * @return the info of NVRAM segment 'id'.
 */
extern drv_NvramRoSegmentInfo *drv_NvramRoGetSegmentInfo(int segment_id);

/**
 * This is the function used to patch RO data file
 *
 * @param arch_hdr pointer to the patch header
 * @param arch_start pointer to the remaining of file data.
 *
 * @return int32
 */
extern int drv_NvramRoApplyPatch(tAppliFileHeader *arch_hdr, uint8 *arch_start);

/**
 * Get the ID structure from the MIRROR .
 *
 * @return the ID structure
 */
extern drv_NvramVolatileParam * drv_NvramGetVolatileParam(int id);

/**
 * Check parameter consistency
 *
 * @return true /false
 */
extern int drv_NvramCheckVolatileParam(int id);

#ifndef HOST_TESTING
/**
 * Initialise NVRAM-RW / Create NvramRwTask.
 *
 * @param nanok_handle  handle on nanok instance
 * @param fs considers file system content or not at init.
 *
 * @return 1 if flush successful, else 0.
 */
extern void drv_NvramRwInit(dxpnkt_Handle *nanok_handle, bool fs);

/**
 * Create a new item in NVRAM-RW.
 *
 * @param item_id  identifier of the item to be created
 * @param data_sz  item data size
 *
 * @return 1 if item created, else 0.
 */
extern int drv_NvramRwNew(int item_id,
                          int data_sz);

/**
 * Delete an existing item from NVRAM-RW.
 *
 * WARNING: BLOCKS until the NVRAM is available.
 *
 * @param item_id  identifier of the item to be deleted
 *
 * @return 1 if item deleted, else 0.
 */
extern int drv_NvramRwDelete(int item_id);

/**
 * Get NVRAM-RW item size.
 *
 * @param item_id  identifier of the item
 *
 * @return the item data size, 0 if item does not exist
 */
extern uint16 drv_NvramRwGetSize(int item_id);

/**
 * Read item data from NVRAM-RW.
 *
 * WARNING: read BLOCKS until NVRAM-RW is available and
 * the read request is done.
 *
 * @param data_dest     read buffer pointer
 * @param item_id       item from which we read data
 * @param item_offset   offset in item data from which we read data
 * @param data_size     size of data to read
 *
 * @return 1 if read successful, else 0.
 */
extern int drv_NvramRwRead(void *data_dest,
                           int item_id,
                           int item_offset,
                           int data_size);

/**
 * Get a 32-bit parameter from RW-NVRAM
 *
 * @param dest
 * @param id
 * @param max_len
 *
 * @return int  : Number of words read
 */
extern int drv_NvramRwGet32(void *dest, int id, int max_len);

/**
 * Write a 32-bit parameter to RW-NVRAM
 *
 * @param src
 * @param id
 * @param len
 *
 * @return bool     :   true if write successful
 */
extern bool drv_NvramRwPut32(void *src, int id, int len);

/**
 * Write data to NVRAM-RW item.
 *
 * WARNING: write DOES NOT BLOCK. The write is sent to the NvramRwTask
 * which has the lowest priority. Note that, no confirmation is signaled when the
 * write request has been served by the NvramRwTask.
 *
 * @param data_src      write buffer pointer
 * @param item_id       item identifier of the item
 * @param item_offset   offset in item data in which we write data
 * @param data_size     size of data to write
 *
 * @return 1 if write request ok, else 0.
 */
extern int drv_NvramRwWrite(void *data_src,
                            int item_id,
                            int item_offset,
                            int data_size);

/**
 * Erase the NVRAM-RW segment.
 *
 * WARNING: BLOCKS until the NVRAM is available.
 *
 * @return 1 if erase successful, else 0.
 */
extern int drv_NvramRwEraseSegment(void);

/**
 * Attempt to lock the NVRAM.
 *
 * Return true if we could lock (NVRAM previously unlock) false
 * if we could not lock  (NVRAM previously locked)
 *
 * @return 1 if we could lock it, else 0
 */
extern int drv_NvramTryLock(void);

/**
 * Lock NVRAM. This is a blocking lock.
 */
extern void drv_NvramLock(void);

/**
 * Unlock NVRAM.
 */
extern void drv_NvramUnLock(void);

/**
 * Wait until all NVRAM-RW requests (enqueued) are served.
 * This function will deschedule the calling thread.
 */
extern void drv_NvramRwSync(void);

/**
 * Find out whether a NVRAM-RW parameter can be written
 * without triggering a GC
 *
 * @param   data_size size of the data of the chunk we want to
 *                    write.
 *
 * @return 1 if GC is needed, else 0
 */
extern int drv_NvramRwNeedGC(int data_size);

/**
 * Get NVRAM-RW last error
 *
 * Warning: this function clears the last error value
 *
 * @return last error
 */
extern int drv_NvramRwGetLastError(void);

void drv_NvramRoRestoreAndLoadDefault(void);

/**
 * Get max NVRAM ID
 *
 * @param   void
 *
 * @return  max NVRAM ID
 */
extern int drv_NvramMaxParam(void);

#endif
#endif

/** @} END OF FILE */

