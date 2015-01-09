/*-
 * Copyright (c) 2011 Icera Inc. All rights reserved.
 *
 */
#ifndef DRV_USB_ECM_API_H
#define DRV_USB_ECM_API_H

#include "drv_usb_cdc_api.h"

typedef const void* ecm_device_t;

struct connection_speed {
	uint32 USBitRate;
	uint32 DSBitRate;
} __packed;
typedef struct connection_speed connection_speed_t;

ecm_device_t
ecm_device_for_interface(const int iface_index);

#endif /* DRV_USB_ECM_API_H */
