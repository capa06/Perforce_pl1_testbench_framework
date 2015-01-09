/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_gpio_services.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup GpioDriver
 * @{
 */

/**
 * @file drv_gpio_services.h - GPIO debounce, ext-wake, notification framework.
 *                             Derived from drv_wireless_disable.c but now generic.
 */

#ifndef DRV_GPIO_SERVICES_H
#define DRV_GPIO_SERVICES_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_hwplat.h"
#include "drv_sync_rtc_cet.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** 
 * when an edge is detected on the I/O, a timer is started to
 * later check the state of the I/O in order to filter glitches out.
 * The following setting is the duration (in milliseconds) of
 * the timer.
 */ 
#define DRV_GPIO_SVC_DEBOUNCE_LATENCY_MS (30)

/** when a bounce is detected a new timer is started. Every
 *  bounce causes the timeout to be multiplied by two up to a
 *  certain limit, defined by the below identifier
 */ 
#define DRV_GPIO_SVC_MAX_BOUNCE_DOUBLES (7)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

struct drv_GpioSrvc;
typedef struct drv_GpioSrvc drv_GpioSrvcHandle;

/**
 *  Type definition for the I/O toggle notification callback.
 *
 *  The notification callback is called when the I/O toggles.
 *  It is called in the context of an interruptservice routine 
 *  and must *not* block.
 * 
 *  @param id        The I/O id
 *  @param value     zero or non-zero value, depending on the
 *                   I/O state
 */   
typedef void (*drv_GpioServicesCallback)(uint32 id, uint32 value);

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

/**
 * Initialise the extended I/O services driver
 *  
 * This configures the I/O, enables extWake events on the I/O 
 * and registers an interrupt handler to dispatch I/O toggle 
 * notifications to a registered listener
 *  
 * @see drv_GpioServicesRegisterNotificationCallback() 
 * @param io I/O input to use
 * @param enable_extwake Enable external wake from hibernate on this pin
 * @param enable_debounce Enable debounce filtering on input
 * @param non_default_debounce Start with I/O interrupt disabled if not using 
                               default debounce settings
 * @return I/O services handle 
 */
extern drv_GpioSrvcHandle* drv_GpioServicesInit(tGpioMapping io, bool enable_extwake, bool enable_debounce, bool non_default_debounce);

/**
 * Configure non-default debounce settings (& then enable interrupt)
 *  
 * @see drv_GpioServicesCallback 
 * @param handle I/O services handle
 * @param debounce_latency_ms See DRV_GPIO_SVC_DEBOUNCE_LATENCY_MS
 * @param max_bounce_doubles See DRV_GPIO_SVC_MAX_BOUNCE_DOUBLES
 * @return none 
 */
extern void drv_GpioServicesConfigureDebounce(drv_GpioSrvcHandle* handle, uint32 debounce_latency_ms, uint32 max_bounce_doubles);

/**
 * Register a notification callback for the I/O
 *  
 * @see drv_GpioServicesCallback 
 * @param handle I/O services handle
 * @param callback Pointer to the notification callback 
 * @return none 
 */
extern void drv_GpioServicesRegisterNotificationCallback(drv_GpioSrvcHandle* handle, drv_GpioServicesCallback callback);

/** 
 *  Returns the state of the I/O
 *  @param handle I/O services handle
 *  @return state of the I/O (zero or non-zero)
 */ 
extern int drv_GpioServicesGetState(drv_GpioSrvcHandle* handle);

#endif /* #ifndef DRV_GPIO_SERVICES_H */
/** @} END OF FILE */


