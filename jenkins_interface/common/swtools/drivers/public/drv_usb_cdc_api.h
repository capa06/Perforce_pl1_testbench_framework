/*************************************************************************************************
* Icera Semiconductor
* Copyright (c) 2009
* All rights reserved
*************************************************************************************************
* $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_cdc_api.h#1 $
* $Revision: #1 $
* $Date: 2014/11/13 $
* $Author: joashr $
************************************************************************************************/

/**
 * @defgroup usb bsd module.
 *
 * @{
 */

/**
 * @file drv_usb_cdc_api.h
 *
 */

#ifndef DRV_USB_CDC_API_H
#define DRV_USB_CDC_API_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <stdint.h>

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define UCDC_VENDOR_SET_IFNET   0xF0

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

struct iobuf;

typedef void* cdc_device_t;
typedef void* cdc_class_t;

typedef int (*cdc_read_t)(void* drv_ctx, uint32_t size);
typedef int (*cdc_write_t)(void* drv_ctx, struct iobuf* iob, uint32_t size);
typedef int (*cdc_write_abort_t)(void* drv_ctx,uint32_t serial_id);

typedef enum {
    CDC_TRANSFER_ERROR = -1,
    CDC_TRANSFER_OK = 0,
    CDC_TRANSFER_CANCELLED = 1,
    CDC_TRANSFER_MAX
} cdc_transfer_e;

typedef enum {
    CDC_PRIO_NULL = 0,
    CDC_PRIO_ANY,
    CDC_PRIO_FIRST,
    CDC_PRIO_LAST,
    CDC_PRIO_INVALID
} cdc_priority_e;


typedef struct drv_cdc_cbs {
    cdc_read_t          cdc_read;
    cdc_write_t         cdc_write;
    cdc_write_abort_t   cdc_write_abort;
} drv_cdc_cbs_t;

typedef struct cdc_init_info {
    uint32_t    flags;
} cdc_init_info_t;


typedef int (*cdc_enabled_cb_t) (void* app_ctx);
typedef int (*cdc_disabled_cb_t)(void* app_ctx);
typedef int (*cdc_uninit_cb_t)  (void* app_ctx);
typedef int (*cdc_suspend_cb_t) (void* app_ctx);
typedef int (*cdc_resume_cb_t)  (void* app_ctx);
typedef int (*cdc_sofstart_cb_t)    (void* app_ctx);

typedef void (*cdc_read_complete_cb_t)(void* app_ctx,struct iobuf* iob, uint32_t size, int status);

typedef void (*cdc_write_complete_cb_t)(void* app_ctx,struct iobuf* iob, int status);

typedef int (*cdc_encap_ready_t)(const void* app_ctx, void* vaddr, uint16 size, int error);
typedef int (*cdc_encap_get_response_t)(const void* app_ctx, void** vaddr, uint16* size);
typedef void (*cdc_encap_complete_t)(const void* app_ctx, int error);
typedef void (*cdc_encap_reset_t)(const void* app_ctx);
typedef void (*cdc_dss_read_complete_cd_t)(const void* app_ctx, struct iobuf* iob);
typedef void (*cdc_encap_suspend_t)(const void* app_ctx);
typedef void (*cdc_encap_resume_t)(const void* app_ctx);
typedef void (*cdc_encap_detach_t)(const void* app_ctx);
typedef void (*cdc_encap_sofstart_cb_t)(const void* app_ctx);

typedef int   (*cdc_device_suspended_t)(cdc_device_t dev, bool* suspended);
typedef int   (*cdc_device_remote_wake_t)(cdc_device_t dev,bool* remote_wake);
typedef int   (*cdc_interface_request_t)(cdc_device_t dev, uint8_t request_id, void** response, uint32_t size);
typedef int   (*cdc_encap_response_available_t)(cdc_device_t dev);
typedef int   (*cdc_encap_response_t)(cdc_device_t dev, void *response, uint32 size);
typedef int   (*cdc_cancel_encap_response_t)(cdc_device_t dev);
typedef void* (*cdc_alloc_encap_response_t)(cdc_device_t dev, uint32_t len);
typedef void  (*cdc_free_encap_response_t)(cdc_device_t dev, void* buffer);

/* Upward going callback interface to encap clients from CDC */
typedef struct app_cdc_encap_api {
    cdc_encap_ready_t           cdc_encap_ready; /* Send command complete */
    cdc_encap_get_response_t    cdc_encap_get_response; /* Get response data required (return 0 for no data) */
    cdc_encap_complete_t        cdc_encap_complete; /* Get response completed */
    cdc_encap_reset_t           cdc_encap_reset; /* Reset by host */
    cdc_encap_suspend_t         cdc_encap_suspend; /* Suspend complete */
    cdc_encap_resume_t          cdc_encap_resume; /* Resume complete */
    cdc_encap_detach_t          cdc_encap_detach; /* Device deteched */
    cdc_encap_sofstart_cb_t     cdc_encap_sofstart; /* SOFs detected following resume */

} app_cdc_encap_api_t;

/* Downward going interface from the application to the CDC encap functions */
typedef struct drv_cdc_encap_api {
    cdc_device_suspended_t          cdc_device_suspended; /* query the suspended state of the USB stack */
    cdc_device_remote_wake_t        cdc_device_remote_wake; /* query the state of the function feature REMOTE_WAKE */
    cdc_interface_request_t         cdc_interface_request; /* unknown - something to do with processing Vendor requests? */
    cdc_encap_response_available_t  cdc_encap_response_available; /* Inform CDC that an encap response is ready to be transmitted */
    cdc_cancel_encap_response_t     cdc_cancel_encap_response; /* Cancel one outstanding encap response */
    cdc_alloc_encap_response_t      cdc_alloc_encap_response; /* Allocate a buffer for an encap response */
    cdc_free_encap_response_t       cdc_free_encap_response; /* Free a previously allocated encap buffer */
} drv_cdc_encap_api_t;

/* */
typedef struct cdc_callbacks {

    cdc_enabled_cb_t                    enabled;
    cdc_disabled_cb_t                   disabled;
    cdc_uninit_cb_t                     uninit;
    cdc_suspend_cb_t                    suspended;
    cdc_resume_cb_t                     resumed;
    cdc_sofstart_cb_t                   sofstart;

    cdc_read_complete_cb_t              read_complete;
    cdc_write_complete_cb_t             write_complete;
} cdc_callbacks_t;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/* interface API with CDC */
cdc_device_t
cdc_device_for_interface(const int iface_index);

cdc_device_t
cdc_device_for_interface_index(const cdc_class_t cdc_class,const int iface_index);

cdc_device_t
cdc_encap_register(const int iface_index,const app_cdc_encap_api_t* app_cbs, const void* app_ctx, drv_cdc_encap_api_t* drv_cbs);


cdc_device_t
cdc_encap_register_priority(const int iface_index,const app_cdc_encap_api_t* app_cbs, const void* app_ctx, drv_cdc_encap_api_t* drv_cbs, cdc_priority_e prio);

int
cdc_encap_unregister(cdc_device_t dev,const void* app_ctx);


#endif /* DRV_USB_CDC_API_H */
