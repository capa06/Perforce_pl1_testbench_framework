/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2004-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dbg_noninit.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup DbgDriver
 * @{
 */

/**
 * @file drv_dbg_noninit.h Non-init variables definitions
 *
 * Give access to Icera and Custom non init data files.
 *
 */

#ifndef DRV_DBG_NONINIT_H
#define DRV_DBG_NONINIT_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"
/* Insert here includes required for drv_dbg_noninit_files.h */

#include "drv_hwplat.h"
#include "drv_usb_config.h"
#include "drv_arch_type.h"

/* end of include list required for drv_dbg_noninit_files.h */

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_DBG_O_RDONLY    		                0x01
#define DRV_DBG_O_WRONLY    		                0x02
#define DRV_DBG_O_RDWR      	                    0x03
#define DRV_DBG_O_WRONLY_APPEND                     0x06
#define DRV_DBG_O_ACCESS_UNDEFINED                  0x00

/* List of Noninit filename macros required in drv_dbg_noninit_files.h */
#define DRV_DBG_RAMLOG                              "ram_log.dmp"
#define DRV_DBG_SOC_DUMP                            "soc.bin"
#define DRV_DBG_PLATFORM_INFO                       "platform_info.txt"
#define DRV_DBG_EVENTS                              "bb_events.txt"
#define DRV_DBG_CRASHLOG_DXP0                       "dxp0_crashlog.txt"
#define DRV_DBG_CRASHLOG_DXP1                       "dxp1_crashlog.txt"
#define DRV_DBG_CRASHLOG_DXP2                       "dxp2_crashlog.txt"
#define DRV_DBG_MODULE_CRASHLOGS_DXP0               "dxp0_SW_crashlogs.txt"
#define DRV_DBG_MODULE_CRASHLOGS_DXP1               "dxp1_SW_crashlogs.txt"
#define DRV_DBG_MODULE_CRASHLOGS_DXP2               "dxp2_SW_crashlogs.txt"
#define DRV_DBG_USB_SWITCHINFO_FILENAME             "switch_info.sav"
#define DRV_DBG_DXP0_UISTS                          "dxp0_uists.dmp"
#define DRV_DBG_DXP1_UISTS                          "dxp1_uists.dmp"
#define DRV_DBG_DXP2_UISTS                          "dxp2_uists.dmp"
#define DRV_DBG_DMEM_FILENAME                       "dmem.bin"
#define DRV_DBG_DMEM2_FILENAME                      "dmem2.bin"
#define DRV_DBG_GMEM_FILENAME                       "gmem.bin"
#define DRV_DBG_HIF_CONFIG                          "hif_config"
#define DRV_DBG_REBOOT_INFO_FILENAME                "reboot_info"
#define DRV_DBG_DEBUG_LOG_FILENAME                  "debug_log.txt"
#define DRV_DBG_YAFFS2_HEAP_FILENAME                "yaff2_heap.bin"
#define DRV_DBG_EXTMEM_CHECKSUM_FILENAME            "extmem_checksum"
#define DRV_DBG_IDBGTEST_VALUE_FILENAME             "idbgtest_value"
#define DRV_DBG_EXTMEM_FILENAME                     "extram.bin"
#define DRV_DBG_PLAT_CFG                            "plat_cfg.bin"
#define DRV_DBG_VER_COMPAT                          "ver_compat.bin"
#define DRV_DBG_UNLOCK                              "unlock.bin"
#define DRV_DBG_SILENT_PIN                          "flat_boot.bin"
#define DRV_DBG_DEVICE_GW_CFG_FILENAME              "device_gw_cfg.bin"
#define DRV_DBG_EXT_HDR                             "ext_header.bin"
#define DRV_DBG_APP_MODE                            "app_mode.bin"
#define DRV_DBG_HIBERNATION                         "hibernation.bin"
#define DRV_DBG_PLATFORM_INFO_CPY                   "platform_info.txt.cpy"
#define DRV_DBG_CRASHLOG_DXP0_CPY                   "dxp0_crashlog.txt.cpy"
#define DRV_DBG_CRASHLOG_DXP1_CPY                   "dxp1_crashlog.txt.cpy"
#define DRV_DBG_CRASHLOG_DXP2_CPY                   "dxp2_crashlog.txt.cpy"

#define DRV_DBG_STACK_DMP_NB                        1500

#define DRV_DBG_PLATFORM_INFO_SIZE                  2000
#define DRV_DBG_EVENTS_SIZE                         8192
#define DRV_DBG_CRASHLOG_DXP0_SIZE                  6000
#define DRV_DBG_CRASHLOG_DXP1_SIZE                  6000
#define DRV_DBG_CRASHLOG_DXP2_SIZE                  6000
#define DRV_DBG_MODULE_CRASHLOGS_DXP0_SIZE          (64*1024)
#define DRV_DBG_MODULE_CRASHLOGS_DXP1_SIZE          (64*1024)
#define DRV_DBG_MODULE_CRASHLOGS_DXP2_SIZE          8000

#define DRV_DBG_DMEM_DUMP_MAX_SIZE                  D_MEM_D_MEM_DXP0_SIZE
#define DRV_DBG_DMEM2_DUMP_MAX_SIZE                 D_MEM_D_MEM_DXP2_SIZE

#define DRV_DBG_GMEM_DUMP_MAX_SIZE                  (384 * 1024) /* TODO: There should be a SDK def */


#define DRV_DBG_MEMORY_RESERVED_FOR_BT2_YAFFS       (1024*192)

#define DRV_DBG_RLG_BUF_SIZE                        (100*(1024))

/**
 * Max size (in bytes) for platform config data stored in
 * noninit during an external boot (i.e. boot from UART,
 * HSI,...) Fix a value here because of noninit file interface
 * that requires it. This is not a limitation and can be
 * increased if needed.
 */
#define DRV_DBG_PLAT_CFG_BUF_SIZE                   1024

/** Max size in bytes for version compatibility info
 *  transmitted (or not) during external boot */
#define DRV_DBG_VER_COMPAT_BUF_SIZE                 sizeof(int)

/** Size in bytes of an unlock certificate is fixed */
#define DRV_DBG_UNLOCK_BUF_SIZE                     568

/** Max size in bytes for extended header */
#define DRV_DBG_EXT_HDR_BUF_SIZE                    ARCH_RFU_FIELD_SZ

#define DRV_DBG_AL_REBOOT_EXTRAINFO_SIZE            sizeof(RebootExtraInfo)

/* Silent PIN size: 10 Bytes ICCID + 10 Bytes PIN */
#define DRV_DBG_SILENT_PIN_SIZE 20

#define DRV_DBG_HIBERNATION_SIZE                    sizeof(int)
/* Invalid file ID */
#define DRV_DBG_INVALID_FILE                        -1

/* Noninit pointer check function */
#define DRV_DBG_NONINIT_VALID_POINTER(a)            ((((int)(a)) != DRV_DBG_INVALID_FILE) && (a))

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Read all the content of a Non init file. If the non init file
 * is not valid (checksum does not match), buffer is filled with
 * zero with the size of the file
 *
 * @param const char *filename_p Name of the file
 * @param int *buffer pointer to the adress of a buffer to fill
 * with the content of the non init file. buffer shall be
 * allocated prior to the call of the function
 */
extern int drv_DbgFreadAll (const char *filename_p,int *buffer, int size);

/**
 * Write a full buffer content to a Non init file. a copy if
 * performed from the buffer to the non init file and a checksum
 * is calculated on top of that.
 *
 * @param const char *filename_p Name of the file
 * @param int *buffer pointer to the adress of a buffer to
 * copy to a non init file. buffer shall be allocated prior to
 * the call of the function
 */
extern int drv_DbgFwriteAll(const char *filename_p,int *buffer);


/**
 * Open a file
 *
 * @param filename_p Name of the file
 * @param flags DRV_DBG_O_WRONLY or DRV_DBG_O_RDONLY
 * @param mode not used
 *
 * The function may return -1 when opening a file for read
 * access and the file is corrupted.
 *
 * @return return a file handle or -1 if it is not possible to
 *         open it.
 */
extern int drv_DbgFopen (const char *filename_p, int flags, int mode);


/**
 * Close a file
 *
 * @param fileHandle file handle
 *
 * @return void
 */
extern void drv_DbgFclose (int fileHandle);


/**
 * Invalidating a file by corrupting its checksum
 * so that opening the file for read access is no longer
 * possible.
 *
 * @param filename_p pointer to file name string
 *
 * @return True if file is removed. False if the file is stil
 *         present (already opened)
 */
bool drv_DbgFremove (const char* filename_p);


/**
 * Read from a file@param fileHandle identifying the file
 * @param dest_ptr pointer to the data to be read
 * @param elt_size size of the element to be read
 *
 * @return number of bytes read
 */
size_t drv_DbgFread (int fileHandle, void *dest_ptr, size_t elt_size);


/**
 * Write a file
 *
 * @param fileHandle identifying the file
 * @param elt_ptr pointer to the element to be written
 * @param elt_size size of the data to be written
 *
 * @return number of bytes written
 */
size_t drv_DbgFwrite (int fileHandle, void *elt_ptr, size_t elt_size);


/**
 * Gives the NonInit Maximum size from drv_DbgNonInitHeader->NonInitTop_p
 *
 * @return NonInit Maximum size
 */
int drv_DbgGetNonInitMaxSize();


/**
 * Returns the current size of a file known by its name.
 *
 * @param name The name of the file.
 *
 * @return file size, 0 if the file is invalid or does not
 *         exist.
 */
extern uint32 drv_DbgFGetfilesize(const char *filename_p);

/**
 * Returns the maximum size of a file known by its name.
 *
 * @param name The name of the file.
 *
 * @return file size, 0 if the file does not exist
 */
extern uint32 drv_DbgFGetfileMaxsize(const char *filename_p);


/**
 * Returns the pointer to the data buffer of a file known by its
 * name. Create the file if it does not exist
 *
 * @param filename_p The name of the file.
 *
 * @return pointer to the buffer, NULL if the file is invalid.
 */
extern uint8 *drv_DbgFGetfileBuffer(const char *filename_p);

/**
 * Copy a non init file content in another noninit file.
 *
 * Will not copy more than data available in src file.
 * May copy less regarding declared max size of dst file (error case...).
 *
 * @param src file name
 * @param dst file name
 *
 * @return int 1 if OK, 0 if fail.
 */
int drv_DbgFcopy(const char *src, const char *dst);

/** Returns the pointer to the external checksum location in
 * NonInit
 *
 * @return pointer to the buffer
 */
int drv_DbgGetExtmemChecksumPointer ( void );


void drv_DbgInitializeNonInit(void);


extern int drv_DbgGetNonInitRebootCount(void);


#endif /* #ifndef DRV_DBG_NONINIT_H */

/** @} END OF FILE */
