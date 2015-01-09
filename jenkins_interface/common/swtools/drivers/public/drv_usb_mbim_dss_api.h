/*************************************************************************************************
* Icera Semiconductor
* Copyright (c) 2009
* All rights reserved
*************************************************************************************************
* $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_mbim_dss_api.h#1 $
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
 * @file drv_usb_mbim_dss_api.h 
 *
 */

#ifndef DRV_USB_MBIM_DSS_API_H
#define DRV_USB_MBIM_DSS_API_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_usb_cdc_api.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define MBIM_MAX_OUTSTANDING_COMMANDS  15
#define MBIM_DSS_SESSIONS_MAX   10

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

struct iobuf;

typedef enum {
    MBIM_TYPE_LOOPBACK,
    MBIM_TYPE_PACKET_FILTER,
    MBIM_TYPE_SESSION_ID_MAPPING,
    MBIM_TYPE_NULL,
} req_type_e;

typedef enum {
    MBIM_CMD_SET,
    MBIM_CMD_GET,
    MBIM_CMD_ADD,
    MBIM_CMD_RETRIEVE,
    MBIM_CMD_NULL,
} req_cmd_e;

typedef struct {
    int         index;
    int         size;
    uint8*      filter;
    uint8*      mask;
} packet_filter_params_t;

typedef enum
{
    CONFIG_RESULT_SUCCESS = 0,
    PACKET_FILTER_INVALID_SESSION,
    CONFIG_RESULT_INVALID_INDEX,
    CONFIG_RESULT_INVALID_SIZE,
    CONFIG_RESULT_DATA_PATH_NOT_SET_UP,
    CONFIG_RESULT_ERROR
} config_result_t;

typedef void* mbim_device_t;
typedef void* mbim_class_t;

typedef void* app_mbim_handle_t;
typedef void* app_mbim_dss_handle_t;

typedef void (*mbim_reset_t)(const app_mbim_handle_t app_ctx);
typedef int (*mbim_control_t)(void *drv_ctx, req_type_e type, req_cmd_e cmd, int if_nb, void* arg,config_result_t* result);

typedef struct app_mbim_api {
    mbim_reset_t	mbim_reset;
} app_mbim_api_t;

typedef struct app_drv_api {
    mbim_control_t  mbim_control;
} drv_api_t;

typedef struct {
    int		data_if_max_nb;
    int		data_if_nb;
}   mbim_params_t;

/* MBIM DSS driver cbs to open / close a DSS session */
typedef struct drv_dss_cbs {
	/*
	cdc_read_t			cdc_read;
	cdc_write_t			cdc_write;
	cdc_write_abort_t	cdc_write_abort;
	*/
	drv_cdc_cbs_t	cdc_cbs;
} drv_dss_cbs_t;

typedef struct dss_callbacks {
	/*
    cdc_enabled_cb_t              		enabled;
    cdc_disabled_cb_t             		disabled;
    cdc_uninit_cb_t               		uninit;
    cdc_suspend_cb_t              		suspended;
    cdc_resume_cb_t               		resumed;

    cdc_read_complete_cb_t				read_complete;
    cdc_write_complete_cb_t				write_complete;
	*/
	cdc_callbacks_t cdc;
} dss_callbacks_t;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/* interface API with MBIM */

mbim_device_t
mbim_register( const app_mbim_api_t* mbim_cbs, const void* mbim_ctx, drv_api_t* drv_cbs, mbim_params_t* mbim_params);

mbim_device_t 
mbim_dss_register( dss_callbacks_t* app_dss_cbs, void* app_dss_ctx, drv_dss_cbs_t* drv_dss_cbs);

#endif /* DRV_USB_MBIM_DSS_API_H */
