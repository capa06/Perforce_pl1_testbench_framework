/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_gpio.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup GpioDriver GPIO Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup GpioDriver
 * @{
 */

/**
 * @file drv_gpio.h GPIO driver external interface
 *
 */

#ifndef DRV_GPIO_H
#define DRV_GPIO_H

#include "icera_global.h"
#include "drv_hrl.h"

/******************************************************************************
 * Macros
 ******************************************************************************/

/** Number of GPIO banks */
#define DRV_GPIO_NB                 (DRV_GPIO_LAST-DRV_GPIO0+1)

/******************************************************************************
 * Exported types
 ******************************************************************************/

/**
 * Addressed GPIO banks:
 *
 * @note : ICE8040 has 4 possible GPIO banks among which
 *       some can be used or not depending on the pin
 *       multiplexing of a given platform.
 *       Additionally ICE1410 has
 *       a set of GPOP pins.
 *       A set of virtual GPIO banks now exists to abstract
 *       special cases : GPOP0 is treated as such, same goes for
 *       SSP1 CS GPOs bank, PolarPro2 GPOs.
 */
typedef enum
{
    DRV_GPIO_NATURAL_FIRST = 0,
    DRV_GPIO0 = DRV_GPIO_NATURAL_FIRST,
    DRV_GPIO1,
    DRV_GPIO2,
    DRV_GPIO3,
    DRV_GPIO4,
    DRV_GPIO5,    
    DRV_GPOP0,
    DRV_HVOP0,
    DRV_GPIO_NATURAL_LAST = DRV_HVOP0,
    DRV_GPIO_VIRTUAL_FIRST,
    DRV_GPIO_VSSP1 = DRV_GPIO_VIRTUAL_FIRST,
    DRV_GPIO_VPP20,
    DRV_GPIO_VPP21,
    DRV_GPIO_VIRTUAL_LAST = DRV_GPIO_VPP21,
    DRV_GPIOBANK_NB,
    DRV_GPIO_NONE,
#ifdef TARGET_DXP9040
    /* 9040 contains extra 2 GPIO ports outside of PL1 */
    DRV_GPIO_LAST = DRV_GPIO3
#else
    /* PL1 contains 2 GPIO ports */
    DRV_GPIO_LAST = DRV_GPIO1    
#endif
} eDrvGpioId;

/* Externally exported gpio driver handle */
typedef void gpiodrvt_Handle;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Returns interrupt mask for selected IO bank
 *
 * @param gpio_bank_id  id of gpio bank
 * @return interrupt mask
 */
uint16 drv_GpioGetInterruptMask(eDrvGpioId gpio_bank_id);

/**
 * Clear pending interrupts on selected IO bank
 *
 * @param gpio_bank_id  id of gpio bank
 * @param bitmask interrupt mask to clear
 */
void drv_GpioClearInterruptSource(eDrvGpioId gpio_bank_id, uint16 bitmask);

/**
 * Read the GPIO pin direction register of a bank
 *
 *  @param gpio_bank_id
 *
 * @return value of GPIO directions
 */
uint16 drv_GpioGetPinDirection(eDrvGpioId gpio_bank_id);

/**
 * Set up the direction for GPIO (input/output)
 *
 *
 * @note Setting a bit to 1 makes the corresponding IO an output.
 * All GPIOs are inputs at reset. In order to prevent glitches of the IOs the
 * output's initial state must be set prior to calling this function and defining them as such.
 *
 * @param gpio_bank_id
 * @param output_pin_mask: output bits that are set to transition to high (unset bits don't change)
 * @param input_pin_mask: output bits that are set to
 *                       transition to low and become inputs
 *                       (unset bits don't change)
 * @return none
 */
void drv_GpioSetPinDirection(eDrvGpioId gpio_bank_id, uint16 output_pin_mask, uint16 input_pin_mask);

/**
 * Read the GPIO register register of a bank
 *
 *  @param gpio_bank_id
 *
 * @return : bit mask of inputs that are High
 */
uint16 drv_GpioReadPort(eDrvGpioId gpio_bank_id);

/**
 * Write to a GPIO port.
 *
 * The access to the output port is implicitly thread-safe and processor safe thanks to the set/clear fields.
 * @param gpio_bank_id  id of gpio bank
 * @param set_bit_field output bits that are set to transition to high (unset bits don't change)
 * @param clr_bit_field output bits that are set to transition to low  (unset bits don't change)
 * @return none
 */
void drv_GpioWritePort(eDrvGpioId gpio_bank_id, uint16 set_bit_field, uint16 clr_bit_field);

/**
 * Sets up a GPIO output as hardware controlled, ie timed IO.
 *
 * @note This applies to GPIO outputs only
 * @param gpio_bank_id
 * @param set_hco_bit_field: bits of outputs in bank that are granted the hardware controlled attribute
 * @param clr_hco_bit_field: bits of outputs in bank that have the hardware controlled attribute removed
 * @return none
 */
void drv_GpioSetHcoMask(eDrvGpioId gpio_bank_id, uint16 set_hco_bit_field, uint16 clr_hco_bit_field);

/**
 * Initialisation of a GPIO handle
 *
 * @param gpio_bank addressed bank
 *
 */
void drv_GpioStart(eDrvGpioId gpio_bank);

/**
 * Register given GPIO bank handle with IPM driver:
 * initialise pre/post power down callbacks.
 *
 * @param gpio_bank_id
 *
 */
void drv_GpioIpmInit(eDrvGpioId gpio_bank_id);

/**
 * Register all GPIO banks
 *
 */
void drv_GpioHwplatGpioBanksRegister( void );

/**
 * Get a particular pad (by name) GPIO details (bank & bit).
 *
 * @param pad_name  
 * @param gpio_bank  (Output) Gpio Bank pointer (if pad found)
 * @param gpio_bit   (Output) Gpio bit number (if pad found)
 * @return 0 if success, non-zero if not.
 *
 */
int drv_GpioPadLookupGpioDetails(const char *pad_name, eDrvGpioId *gpio_bank, uint32 *gpio_bit);

/**
 * Set a particular pad (by name) as a GPIO.
 *
 * @param pad_name
 * @return 0 if success, non-zero if not.
 *
 */
int drv_GpioPadSelectGPIO(const char *pad_name);


#endif /* #ifndef DRV_GPIO_H */

/** @} END OF FILE */
