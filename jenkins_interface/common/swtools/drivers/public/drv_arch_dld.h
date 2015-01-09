/*************************************************************************************************
 * Nvidia Corp
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch_dld.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_dld.h Archive file download utilities
 *
 */

#ifndef DRV_ARCH_DLD_H
#define DRV_ARCH_DLD_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_arch.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/* 
 * Information on the downloaded file. The hash value is sized for SHA-256 - it can't be easily 
 * dynamically allocated since it is shared between the download and programming stages so there
 * would be no clear owner for the allocated memory
 */
typedef struct {
    bool                info_valid;         /** To tell if the information data structure is valid */
    tAppliFileHeader    dld_file_hdr;       /** Downloaded file header */

    uint32              key_id;             /** Key ID used to sign file */
    uint8               hash[SHA2_DIGEST_SIZE]; /** Hash of downloaded file */
    uint8               rsa_signature[RSA_SIGNATURE_SIZE]; /** RSA signature as read from file */
    uint8               public_platform_id[SHA1_DIGEST_SIZE];  /** PPID from file */
} DrvArchDldFileInfo;

/**
 * ArchDld error codes
 * @Note: When possiblem codes are voluntarily aligned on those of drv_serial_error_e
 *        to simplify error code reading. Error code between 0 and -30 to be mapped with serial err.
 * @see drv_serial_error_e
 */
typedef enum {
    /** No Error */
    DRV_ARCH_DLD_NO_ERROR = 0,

    /** Error when reading data from source */
    DRV_ARCH_DLD_SRC_ERROR_RECEIVE = -15,
    /** Error when writing data to source */
    DRV_ARCH_DLD_SRC_ERROR_SEND = -16,

    /** Error when writing data to source */
    DRV_ARCH_DLD_DST_ERROR_WRITE = -46,

    /** Ram overflow */
    DRV_ARCH_DLD_DST_RAM_OVERFLOW = -61,

    /** File overflow */
    DRV_ARCH_DLD_DST_FILE_OVERFLOW = -62,

    /** Write error */
    DRV_ARCH_DLD_DST_FILE_WRITE_ERROR = -63,

    /** Cannot move file system to write in flash */
    DRV_ARCH_DLD_DST_FILE_FSMOUNT_ERROR = -64,

    /** Not enough space on file system */
    DRV_ARCH_DLD_DST_FILE_NO_SPACE_FS = -65,

    /** Unable to open the file in file system */
    DRV_ARCH_DLD_DST_FILE_OPEN_FAILURE = -66,

    /** Error but no spcified cause - Used for debug */
    DRV_ARCH_DLD_ERROR_UNSPECIFIED = -100,

} DrvArchDldErr;

/******************************
 * Data source types
 ******************************/

/**
 * Source Flow control value
 */
typedef enum {
    DRV_ARCH_DLD_SRC_FC_XOFF = 0,   /**< Src Data flow is not allowed */
    DRV_ARCH_DLD_SRC_FC_XON  = 1,   /**< Src Data flow is allowed */
    DRV_ARCH_DLD_SRC_FC_MAX_OP
} DrvArchDldSrcFc;


/**
 * Protoype of callback functions used to manage flow control.
 * The functions mus be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 * @param fc            Flow control
 *
 * @see                 DrvArchDldSrcFc.
 */
typedef void (*DrvArchDldSrcFlowControlCb)( void * usr_cb_hdl, DrvArchDldSrcFc fc  );

/**
 * Protoype of callback functions used to open / close the source of data to be downloaded.
 * The functions must be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldSrcConnectDisconnectCb)( void * usr_cb_hdl);

/**
 * Prototype of the call back function reading the downloaded data from the source.
 * This is a blocking read.
 * This function must be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 * @param buffer        Pointer to the data buffer which will send / receive the data
 * @param size          Maximum Number of bytes in the buffer
 * @param nb_rw         Pointer to a variable which returns number of bytes read / written
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldSrcSendReceiveDataCb)( void * usr_cb_hdl, uint8 * buffer, uint32 size, uint32 * nb_rw );



/******************************
 * Data destination types
 ******************************/

/**
 * Protoype of callback function used to open the data storing location.
 * The functions must be implemented by the caller.
 *
 * @param usr_cb_hdl            Private call back handle provided by drv_arch_DdlRegisterCbs
 * @param remain_file_dld_bytes The max amount of bytes to download from file
 * @param file_desc            File header containing the whole file description
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldDstOpenCb)( void * usr_cb_hdl, int remain_file_dld_bytes, tAppliFileHeader * file_desc);

/**
 * Protoype of callback function used to close the data storing location.
 * The functions must be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldDstCloseCb)( void * usr_cb_hdl);

/**
 * Prototype of the call back function writing downloaded data do the destination.
 * This is a blocking write.
 * This function must be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 * @param buffer        Source buffer of the write
 * @param size          Maximum Number of bytes to write
 * @param nb_write      Pointer to a variable which returns number of bytes actually written
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldDstWriteDataCb)( void * usr_cb_hdl, uint8 * buffer, uint32 size, uint32 * nb_write );


/**
 * Protoype of callback functions used to open / close the source of data to be downloaded.
 * The functions mus be implemented by the caller.
 *
 * @param usr_cb_hdl    Private call back handle provided by drv_arch_DdlRegisterCbs
 *
 * @return              Error Status
 *
 */
typedef DrvArchDldErr (*DrvArchDldWdtInitUninitCb)( void * usr_cb_hdl);

/******************************
 * Arch Dld types
 ******************************/

/** Arch download call back functions to handle the data source.
 *  All the call back functions must be implemented by the caller.
 *  See call back prototypes for details.
 *  @see DrvArchDldSrcConnectDisconnectCb
 *  @see DrvArchDldSrcSendReceiveDataCb
 */
typedef struct {
    /** Connection to the data src */
    DrvArchDldSrcConnectDisconnectCb            src_conn;
    /** Blocking read to the data src  */
    DrvArchDldSrcSendReceiveDataCb              src_recv;
    /** Blocking write to the data src */
    DrvArchDldSrcSendReceiveDataCb              src_send;
    /** Disconnection to the data src */
    DrvArchDldSrcConnectDisconnectCb            src_disc;
    /** Flowcontrol of the data src */
    DrvArchDldSrcFlowControlCb                  src_fctr;
} DrvArchDldSrcCbs;

/** Arch download call back functions to handle the data destination.
 *  All the call back functions must be implemented by the caller.
 *  See call back prototypes for details.
 *  @see DrvArchDldDstOpenCloseCb
 *  @see DrvArchDldDstWriteDataCb
 */
typedef struct {
    /** Opening data dest */
    DrvArchDldDstOpenCb                         dst_open;
    /** Blocking wrtie to the data source  */
    DrvArchDldDstWriteDataCb                    dst_write;
    /** Closing data dest */
    DrvArchDldDstCloseCb                        dst_close;
} DrvArchDldDstCbs;

typedef struct {
    DrvArchDldSrcCbs  *src_cbs;
    DrvArchDldDstCbs  *dst_cbs;
} DrvArchDldCbs;

/** Type for internal private ArchDld handle */
typedef void * DrvArchDldHdl;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Performs the required init before running drv_arch_Download()
 *
 * @param arch_dld_file_info Pointer to a variable which returns information on the downloaded file
 * @param usr_cbs            Pointer to a set of ArchDld call backs
 * @param usr_cb_hdl         Common handler (opaque for ArchDld service) to be passed in argument to any user cb
 *
 * @return A handle if successful registration, otherwise a NULL pointer
 *
 * @see    drv_arch_Download()
 *
 */
DrvArchDldHdl drv_arch_DdlInit( DrvArchDldFileInfo *arch_dld_file_info, DrvArchDldCbs * usr_cbs, void * usr_cb_hdl);

/**
 * Uninit the Unregister a set of call backs registered by drv_arch_DdlRegisterCbs() and used by drv_arch_Download()
 *
 * @param arch_dld_hdl The handle provided by drv_arch_DdlRegisterCbs()
 *
 * @see   drv_arch_DdlRegisterCbs()
 * @see   drv_arch_Download()
 *
 */
void drv_arch_DdlUninit( DrvArchDldHdl arch_dld_hdl );

/**
 * Download a file from a source. The source of data is managed through callbacks to be provided to the
 * system with drv_arch_DdlRegisterCbs().
 *
 * @param arch_dld_hdl The handle provided by drv_arch_DdlRegisterCbs()
 *
 * @return             0 if the load was successful otherwise a non null value
 *
 * @see drv_arch_DdlRegisterCbs()
 *
 */
int drv_arch_Download(DrvArchDldHdl arch_dld_hdl);

#endif /* #ifndef DRV_ARCH_DLD_H */

/** @} END OF FILE */
