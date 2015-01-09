/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_led.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup PmicDriver
 * @{
 */

/**
 * @file drv_led.h LED driver
 *
 */

#ifndef DRV_LED_H
#define DRV_LED_H

#include "drv_pmic.h"

#define LED_INTENSITY_FULL  0
#define LED_INTENSITY_7_8th 1
#define LED_INTENSITY_6_8th 2
#define LED_INTENSITY_5_8th 3
#define LED_INTENSITY_4_8th 4
#define LED_INTENSITY_3_8th 5
#define LED_INTENSITY_2_8th 6
#define LED_INTENSITY_1_8th 7

#define LED_BLINK_NONE        0
#define LED_BLINK_RATE_512ms  1
#define LED_BLINK_RATE_1024ms 2
#define LED_BLINK_RATE_2048ms 3



#define LED_DUTY_CYCLE_50percent   3      /* 1/2  */
#define LED_DUTY_CYCLE_25percent   2      /* 1/4  */
#define LED_DUTY_CYCLE_12p5percent 1      /* 1/8  */
#define LED_DUTY_CYCLE_6p25percent 0      /* 1/16 */


#define LED_GREEN1   0
#define LED_RED1     1
#define LED_GREEN2   2
#define LED_RED2     3

#define LED_WWAN     0
#define LED_WLAN     1
#define LED_WPAN     2
#define LED_4        3

/* for PP2 we don't have the same concept of LED blinks so define them as patterns instead */
#define LED_PATTERN_SET1        0
#define LED_PATTERN_SET2        1
#define LED_PATTERN_SET3        2
#define LED_PATTERN_SET4        3

#define LED_SUB_PATTERN1        0
#define LED_SUB_PATTERN2        1
#define LED_SUB_PATTERN3        2
#define LED_SUB_PATTERN4        3

extern int drv_led_actuate(uint8 which_led, uint32 on_off,  uint32 duty_cycle, uint32 pwm_ctrl, uint32 rate,
			               drv_PmicCb callback, void * callback_param);

extern void drv_led_actuate_poll(uint8 which_led, uint32 on_off,  uint32 duty_cycle, uint32 pwm_ctrl, uint32 rate);

#endif
/** @} END OF FILE */
