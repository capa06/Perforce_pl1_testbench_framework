/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_vendor.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup UsbDriver
 * @{
 */

/**
 * @file drv_usb_common.h Common definitions and types
 *
 */

#ifndef DRV_USB_VENDOR_H
#define DRV_USB_VENDOR_H

#include "icera_global.h"
#include "drv_usb_config.h"

/******************************************************************************
 * Constants
 ******************************************************************************/
#define IS_USB_CTRL_READ_TYPE(R)    (((R) & 0x80) == 0x80)

/******************************************************************************
 * Exported macros
 ******************************************************************************/
/* Not necessary because only USB_PROFILE_DEFAULT could be ovvereded by CustomConfig  */
//#define USBV_F_NO_PROFILE_OVERRIDE    BIT(0)

/******************************************************************************
 * Exported types
 ******************************************************************************/

/*
 * All fields are in little endian.
 *
 * To switch to one profile using sg_raw command on Windows PC:
 *
 * v0:                B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF
 * sg_raw.exe -r 0 E: FF 00 00 00 00 00 00 pp 00 00 00 00 00 00 00 00  !!! From now this one always take the default profile (see hwplatform.h)
 *                    |  |  |              X
 *     opcode --------+  |  |              X
 *     version ----------+  |              X
 *     profile ----------------------------+
 *
 * v1:                B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF
 * sg_raw.exe -r 0 E: FF 01 01 00 00 00 1C 00 00 00 00 00 00 00 00 00
 *                    |  |  |     |     |     |  |  |  |  |  |  |  |
 *     opcode --------+  |  |     |     |     |  |  |  |  |  |  |  |
 *     version ----------+  |     |     |     |  |  |  |  |  |  |  |
 *     flags ---------------+     |     |     |  |  |  |  |  |  |  |
 *     os ------------------------+     |     |  |  |  |  |  |  |  |
 *     profile -------------------------+     |  |  |  |  |  |  |  |
 *     pid -----------------------------------+--+  |  |  |  |  |  |
 *     vid -----------------------------------------+--+  |  |  |  |
 *     delay_in_ms ---------------------------------------+--+--+--+
 * 
 *  Here we force the switching to profile 0x1C
 *
 */

struct scsi_switch_hdr {

        /* Should be 0xFF */
    unsigned char opcode;

        /* Command version 0 or 1*/
    unsigned char version;
};


struct scsi_switch_cmd_v0 {

    struct scsi_switch_hdr  hdr;

        /* Padding, should be 0 */
    unsigned char pad0[5];

        /* Profile identifier as defined in drv_usb_profile_ids.h
         * USB_PROFILE_DEFAULT is allowed
         */
    unsigned char profile;
};

struct scsi_switch_cmd_v1 {

    struct scsi_switch_hdr  hdr;

        /* Not yet used
         */
    unsigned short flags;

        /* OS identifier as defined in drv_UsbOsId.
         * USBV_OS_UNSPECIFIED is allowed.
         */
    unsigned short os;

        /* Profile identifier as defined in drv_usb_profile_ids.h
         * USB_PROFILE_DEFAULT is allowed
         */
    unsigned short profile;

        /* Product identifier
         * USB_PRODUCT_ID_DEFAULT is allowed
         */
    unsigned short pid;

        /* Product identifier
         * USB_VENDOR_ID_DEFAULT is allowed
         */
    unsigned short vid;

        /* Delay before to switch (in ms)
         */
    unsigned long delay_in_ms;
};

typedef struct _scsi_lun_info {
        void*           context;
        char*           configname;     /* Name specified by the MASS_CONFIG_LIST label     */
        unsigned char   lun;            /* Lun number (zero-based)                          */
        unsigned char   options;        /* b0=1: zero-cd, b1=1: removable                   */
        unsigned char   index;          /* Index in the fs_desc/sd_desc or ram_desc array   */
        bool            inserted;       /* true when medium is present and ready to access  */
} scsi_lun_info;

typedef union {
    struct scsi_switch_hdr  hdr;
    struct scsi_switch_cmd_v0 v0;
    struct scsi_switch_cmd_v1 v1;
} scsi_switch_cmd_t;

typedef struct
{
    void* param1;
    unsigned char param2;
} vendor_req_ctx;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/** 
 * Called by vendor part (inside usb_vendor_command_dispatch) to get data after setup
 *  
 * @param context       Given by the drv_UsbCtrlDispatch function
 * @param buffer        Buffer that contains byte to be sent to the Host
 * @param bufferlength  Size of the buffer
 * @param length        Maximal size to be sent (given by the setup)
 *
 * return true when the command is unsupported or failed
 *
 */
bool drv_UsbCtrlSend(vendor_req_ctx context, void* buffer, unsigned short bufferlength, unsigned short length);

/** 
 * Called by the USB stack when an USB request is received
 *  
 * @param context       Opaque context used by drv_UsbCtrlSend function
 * @param bRequestType  See USB specification
 * @param bRequest      See USB specification
 * @param wValue        See USB specification
 * @param wIndex        See USB specification
 * @param wLength       See USB specification
 *
 * return true when the command is unsupported or failed
 *
 */
bool drv_UsbCtrlDispatch(vendor_req_ctx context, unsigned char bRequestType, unsigned char bRequest,
                         unsigned short wValue, unsigned short wIndex, unsigned short wLength);

/** 
 * Unmount all drives and switch to the requested mode
 *  
 * @param lun_info          Structure given by the vtransparent_cb callback
 * @param command           Buffer of the scsi command (First byte == command token itself)
 * @param response          Buffer of the scsi response (optional)
 * @param response_length   Max byte-length of response buffer (in) and used length (out)
 *
 * return true when scsi command is failed
 *
 */
bool drv_UsbScsiCommand(scsi_lun_info* lun_info, unsigned char* command,
                        unsigned char* response, unsigned long* response_length);

/** 
 * Unmount all drives and switch to the requested mode
 *  
 * @param info      Describe switch conditions
 *
 */
bool drv_UsbUnmountAndSwitch( drv_UsbSwitchInfo* info);

/** 
 * Enable to override the default functionality assignment of each USB channel
 *  
 * @param profile       Current USB profile used
 * @param type          Channel type
 * @param function      Enable to override channel functionality: type, name
 *  
 */
void drv_UsbFunctionTypeOverride(drv_UsbProfileId profile, fd_type_t type, drv_UsbFct* function);

/** 
 * Enable to override the default class/subclass/protocol fields located in the USB device descriptor and eventually remove all CDC class descriptors
 *  
 * @param profile       Current USB profile used
 * @param function      Channel interface functionality: type, name, index (eventually overrided by usb_vendor_function_override)
 * @param fd_instance   Enable to override class/subclass/protocol fields located in the USB interface descriptor and remove CDC class descriptor
 *
 */
void drv_UsbInterfaceClassOverride(drv_UsbProfileId profile, drv_UsbFct function, fd_instance_t* fd_instance);

/** 
 * Enable to choose the profile that it will be used
 *  
 * @param profile       Current USB profile used
 *
 * return profile (eventually overrided)
 *
 */
drv_UsbProfileId drv_UsbProfileOverride(drv_UsbProfileId profile);
/** 
 * swiitch to specified profile name with a delay
 *  
 * @param profileName       USB profile used
 *
 * return success/fail
 *
 */
bool drv_UsbProfileSwitchByName(char *profileName, unsigned long deferredTimeInus);
/** 
 * swiitch to specified profile id with a delay
 *  
 * @param profileId       USB profile used
 *
 * return success/fail
 *
 */
bool drv_UsbProfileSwitchById(uint32 profileId, unsigned long deferredTimeInus);

#endif /* #ifndef DRV_USB_VENDOR_H */

/** @} END OF FILE */
