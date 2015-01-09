/*-
 * Copyright (c) 2011 Icera Inc. All rights reserved.
 *
 */
#ifndef DRV_USB_OBEX_API_H
#define DRV_USB_OBEX_API_H

#include "drv_usb_cdc_api.h"

typedef const void* obex_device_t;
typedef void* obex_class_t;

typedef struct drv_obex_cbs {
	drv_cdc_cbs_t					cdc_cbs;
} drv_obex_cbs_t;

typedef struct obex_callbacks {
    cdc_callbacks_t cdc;
} obex_callbacks_t;

void* 
obex_init(void* drv_ctx, obex_callbacks_t *cbs,const drv_obex_cbs_t* cdc_cbs,uint32 type,int iface_index);

obex_device_t
obex_device_for_interface(const int iface_index);

#endif /* DRV_USB_OBEX_API_H */

