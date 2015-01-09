/*-
 * Copyright (c) 2011 Icera Inc. All rights reserved.
 *
 */
#ifndef DRV_USB_ACM_API_H
#define DRV_USB_ACM_API_H

#include "drv_usb_cdc_api.h"

struct usb_cdc_abstract_state;
struct usb_cdc_line_state;

typedef const void* acm_device_t;
typedef int (*acm_notify_serial_state_t)(void* drv_ctx,uint16 serial_state);

typedef struct acm_line_coding {
    uint32	dte_rate;    
    uint8	char_format;  
    uint8	parity_type;  
    uint8	data_bits;    
} acm_line_coding_t;

typedef struct drv_acm_cbs {
	drv_cdc_cbs_t					cdc_cbs;
	acm_notify_serial_state_t		acm_notify_serial_state;

} drv_acm_cbs_t;

typedef struct acm_capabilities {
	uint8	cm;
	uint8	acm;
} acm_capabilities_t;

typedef struct acm_init_info {
    cdc_init_info_t cdc;          /* Info relevant for all CDC modules */
    acm_capabilities_t capabilities;
} acm_init_info_t;

typedef int (*acm_comm_feature_cb_t)(int selector,struct usb_cdc_abstract_state* status, void* app_ctx);
typedef int (*acm_comm_feature_clear_cb_t)(int selector,void* app_ctx);
typedef int (*acm_line_coding_cb_t)(acm_line_coding_t* coding, void* app_ctx);
typedef int (*acm_control_line_state_cb_t)(uint16 line_state, void* app_ctx);
typedef int (*acm_break_send_cb_t)(uint16 break_duration, void* app_ctx);


typedef struct acm_callbacks {
    /* Basic CDC handlers */
    cdc_callbacks_t				cdc;
        
    /* ACM Host to device */
    acm_comm_feature_cb_t       comm_feature_set;
    acm_comm_feature_cb_t       comm_feature_get;
    acm_comm_feature_clear_cb_t comm_feature_clear;
    acm_line_coding_cb_t        line_coding_set;
    acm_line_coding_cb_t        line_coding_get;
    acm_control_line_state_cb_t	line_state_set;
    acm_break_send_cb_t         break_send;
} acm_callbacks_t;

void* 
acm_init(void* drv_ctx, acm_callbacks_t* acm_cbs,const drv_acm_cbs_t* drv_cbs,uint32 type,int iface_index );
acm_init_info_t* 
acm_caps_get(void* app_ctx,acm_init_info_t* info);
acm_device_t
acm_device_for_interface(const int iface_index);

#endif /* DRV_USB_ACM_API_H */
