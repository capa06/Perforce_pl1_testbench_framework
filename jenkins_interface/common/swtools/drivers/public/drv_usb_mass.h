/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_mass.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup MassStorage
 * @{
 */

/**
 * @file drv_usb_mass.h functions definitions for mass-storage interface
 *
 */

#ifndef DRV_USB_MASS_H
#define DRV_USB_MASS_H

/******************************************************************************
 * Include Files
 ******************************************************************************/
#include "icera_global.h"

/******************************************************************************
 * Constants
 ******************************************************************************/
#define MEDIA_ACCESS_UNDEFINED      0
#define MEDIA_ACCESS_READ           1
#define MEDIA_ACCESS_WRITE          2
#define MEDIA_ACCESS_READ_WRITE     (MEDIA_ACCESS_READ | MEDIA_ACCESS_WRITE)
#define MEDIA_ACCESS_WRITE_ONCE     (4 | MEDIA_ACCESS_WRITE)

#define KILOBYTE                    1024UL
#define MEGABYTE                    (KILOBYTE * 1024)

#define CDROM_SECTOR_SIZE           2048
#define DEFAULT_SECTOR_SIZE         512
#define MAX_SECTOR_SIZE             2048

/******************************************************************************
 * Exported macros
 ******************************************************************************/
#define IS_READ_ONLY(A)             (((A) & MEDIA_ACCESS_READ_WRITE) == MEDIA_ACCESS_READ)
#define IS_WRITE_ONLY(A)            (((A) & MEDIA_ACCESS_READ_WRITE) == MEDIA_ACCESS_WRITE)

#define BLN(V)                      ((V) ? true : false)
#define MAX_ARRAY_IDX(V)            (sizeof(V) / sizeof((V)[0]))

/******************************************************************************
 * Exported types
 ******************************************************************************/
typedef void (*rw_media_cb_fct)(void* ctx, uint32 remainder);

/*
    For few commands a treatment is added before to send the response.
    So MASS_NO_OVERLOAD_SUCCESS should be used (instead of MASS_SUCCESS) to be sure that
    no treatment will be done after and then to send the response immediatly.
*/
typedef enum
{
    MASS_SUCCESS,
    MASS_NO_OVERLOAD_SUCCESS,
    MASS_FAILED,
} mass_result;

typedef struct
{
    uint32      sector_size;
    uint32      nb_sectors;
    uint8       access_type;
} drv_usb_mass_set_params;

typedef struct
{
    const char* dirname;
    const char* devname;
    const char* filename;
} drv_usb_mass_get_params;

/******************************************************************************
 * Exported function types
 ******************************************************************************/

/**
 * Get some Media parameters
 *
 * @param ctx               Reference on the Media context
 * @param params            Pointer to parameter structure
 *
 */
typedef void (*get_params_fct)(void* ctx, drv_usb_mass_get_params* params);

/**
 * Set some Media parameters
 *
 * @param ctx               Reference on the Media context
 * @param params            Pointer to parameter structure
 *
 */
typedef void (*set_params_fct)(void* ctx, drv_usb_mass_set_params* params);

/**
 * Get Media "read-only" setting
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  true if Media doesn't support write access else false
 *
 */
typedef bool (*is_read_only_fct)(void* ctx);

/**
 * Get Media "sector-size" value
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  Sector size (in bytes)
 *
 */
typedef uint32 (*get_sector_size_fct)(void* ctx);

/**
 * Get Media "total number of sectors" value
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  Number of sectors
 *
 */
typedef uint32 (*get_nb_sectors_fct)(void* ctx);

/**
 * Unregister Media from the mass-storage
 *
 * @param ctx               Reference on the Media context
 *
 */
typedef void (*unregister_fct)(void* ctx);

/**
 * Get Media status [optional] by default the Media is ready to use when it is mounted successfully
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  true if Media is ready to use else false
 *
 */
typedef bool (*ready_fct)(void* ctx);

/**
 * Mount Media to the device [optional] called if something should be done to mount the Media
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  true if the Media is successfully mounted else false
 *
 */
typedef mass_result (*mount_fct)(void* ctx);

/**
 * Unmount Media from the device [optional] called if something should be done to unmount the Media
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  false to prevent the "No-CD" ejection else true
 *
 */
typedef mass_result (*unmount_fct)(void* ctx);

/**
 * Open Media
 *
 * @param ctx               Reference on the Media context
 * @param rw_media_cb       Read/Write Callback (called when Read or Write operation is terminated)
 * @param rw_media_cb_ctx   Callback Context
 *
 * @return                  true if Media is successfully opened else false
 *
 */
typedef mass_result (*open_fct)(void* ctx, rw_media_cb_fct rw_media_cb, void* rw_media_cb_ctx);

/**
 * Close Media [optional]
 *
 * @param ctx               Reference on the Media context
 *
 * @return                  true if Media is successfully closed else false
 *
 */
typedef mass_result (*close_fct)(void* ctx);

/**
 * Read Media
 *
 * @param ctx               Reference on the Media context
 * @param buffer            Caller allocated buffer, where data read will be put
 * @param offset            Offset from the Media beginning (0 to the max. of Media sectors - 1)
 * @param amount            Number of read sectors
 *
 * @return                  true if Media is successfully read else false
 *
 */
typedef mass_result (*read_fct)(void* ctx, uint8 *buffer, uint32 offset, uint32 amount);

/**
 * Write Media (should be defined even for read-only Media type)
 *
 * @param ctx               Reference on the Media context
 * @param buffer            Caller allocated buffer, where data will be get to be written on the Media
 * @param offset            Offset from the Media beginning (0 to the max. of Media sectors - 1)
 * @param amount            Number of read sectors
 *
 * @return                  true if Media is successfully write else false
 *
 */
typedef mass_result (*write_fct)(void* ctx, uint8 *buffer, uint32 offset, uint32 amount);

/**
 * Cancel Media [optional] Implemented if Media do something when the current read/write operation is aborted
 *
 * @param ctx               Reference on the Media context
 *
 */
typedef void (*cancel_fct)(void* ctx);

/**
 * Flush Media cache [optional] Implemented if Media support cache mechanism
 *
 * @param ctx               Reference on the Media context
 *
 */
typedef void (*flush_fct)(void* ctx);

/**
 * Enable Media cache [optional] Implemented if Media support cache mechanism
 *
 * @param ctx               Reference on the Media context
 * @param allow_cache       true to enable the cache mechanism
 *
 */
typedef void (*vallow_cache_fct)(void* ctx, bool allow_cache);

/**
 * Complete DDP [optional] Implemented if Media supports DDP (Direct Data Path)
 *
 * @param ctx               Reference on the Media context
 * @param success           true if DDP transfer completed OK
 *
 */
typedef void (*complete_ddp_fct)(void* ctx, bool success);

/**
 * Cancel DDP [optional] Implemented if Media supports DDP (Direct Data Path)
 *
 * @param ctx               Reference on the Media context
 *
 */
typedef void (*cancel_ddp_fct)(void* ctx);

/**
 * Raw SCSI Media command [optional] Implemented if Media need to support it
 *
 * @param ctx               Reference on the Media context
 * @param cmd               raw access to the scsi transparent command parameters
 * @param length            If > 0 then it indicates the number of byte returned in the buffer
 * @param buffer            buffer returned (used only if length > 0)
 *
 * @return                  Media command result
 *
 */
typedef mass_result (*transparent_fct)(void* ctx, void *cmd, uint32* length, void *buffer);

typedef struct
{
    /* Mandatory */is_read_only_fct     is_read_only;
    /* Mandatory */get_sector_size_fct  get_sector_size;
    /* Mandatory */get_nb_sectors_fct   get_nb_sectors;
    /* Mandatory */unregister_fct       unregister;
	/* Optional  */ready_fct            ready;
    /* Optional  */mount_fct            mount;
    /* Optional  */unmount_fct          unmount;
    /* Mandatory */open_fct             open;
    /* Optional  */close_fct            close;
    /* Mandatory */read_fct             read;
    /* Mandatory */write_fct            write;
    /* Optional  */cancel_fct           cancel;
    /* Optional  */flush_fct            flush;
    /* Optional  */vallow_cache_fct     vallow_cache;
    /* Optional  */complete_ddp_fct     complete_ddp;
    /* Optional  */cancel_ddp_fct       cancel_ddp;
    /* Optional  */transparent_fct      transparent;
    /* Optional  */get_params_fct       get_params;
    /* Optional  */set_params_fct       set_params;
} media_ops_type;

/******************************************************************************
 * Exported functions
 ******************************************************************************/
typedef bool (*media_register_cb)(media_ops_type* ops, void** media, uint8 index);
typedef void (*media_check_cb)(void *app_ctx, int vlun,media_ops_type* ops);

/**
 * Register a new File-System Media to the mass-storage
 *
 * @param ops               function pointer array for Media access
 * @param media             Reference on the Media context
 * @param index             Media index
 *
 * @return                  true if successfully registered else false
 *
 */
bool drv_usb_fs_register(media_ops_type* ops, void** media, uint8 index);

/**
 * Register a new RAM (volatile - kept only for test) Media to the mass-storage
 *
 * @param ops               function pointer array for Media access
 * @param media             Reference on the Media context
 * @param index             Media index
 *
 * @return                  true if successfully registered else false
 *
 */
bool drv_usb_ram_register(media_ops_type* ops, void** media, uint8 index);

/**
 * Register a new SD card Media to the mass-storage
 *
 * @param ops               function pointer array for Media access
 * @param media             Reference on the Media context
 * @param index             Media index
 *
 * @return                  true if successfully registered else false
 *
 */
bool drv_usb_sd_register(media_ops_type* ops, void** media, uint8 index);

#endif /* !DRV_USB_MASS_H */

