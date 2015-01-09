/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_ipm_order.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup IpmDriver
 * @{
 */

/**
 * @file drv_ipm_order.h Definitions of idle power management
 *       pre/post callback orders
 *
 */

#ifndef DRV_IPM_ORDER_H
#define DRV_IPM_ORDER_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_ipm.h"

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* Pre idle callback order on DXP#0 - in chronological order (low number = high priority) */
enum drv_IpmDxp0PreIdleCallbackOrderEnum {
    DRV_IPM_DTE_PREIDLE_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    DRV_IPM_STE0_PREIDLE_CB_ORDER,
    DRV_IPM_FSI_PREIDLE_CB_ORDER,
    DRV_IPM_IPP_PREIDLE_CB_ORDER,
    DRV_IPM_XSI_PREIDLE_CB_ORDER,
    DRV_IPM_SYNC_RTCCET_PREIDLE_CB_ORDER,
    DRV_IPM_GUT_LO_RES_DXP0_PREIDLE_CB_ORDER,
    DRV_IPM_GUT_HI_RES_DXP0_PREIDLE_CB_ORDER,
    DRV_IPM_RF0_PREIDLE_CB_ORDER,
    /* System driver is saving internal memories (DMEM on 8060 and GMEM on 9040)*/
    DRV_IPM_SYSTEM_DXP0_PREIDLE_CB_ORDER,
    DRV_IPM_CHPC_PREIDLE_CB_ORDER,
    DRV_IPM_GPIO_PREIDLE_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP0_PREIDLE_CB_ORDER,
};

/* Pre idle callback order on DXP#1 - in chronological order (low number = high priority) */
enum drv_IpmDxp1PreIdleCallbackOrderEnum {
    DRV_IPM_STE1_PREIDLE_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    DRV_IPM_UART_PREIDLE_CB_ORDER,
    DRV_IPM_AVS_PREIDLE_CB_ORDER,
    DRV_IPM_LL1_GUARD_TIME_PREIDLE_CB_ORDER,
    DRV_IPM_LL1_PREIDLE_CB_ORDER,
    DRV_IPM_GUT_LO_RES_DXP1_PREIDLE_CB_ORDER,
    DRV_IPM_GUT_HI_RES_DXP1_PREIDLE_CB_ORDER,
    DRV_IPM_RF1_PREIDLE_CB_ORDER,
    DRV_IPM_SAR_PREIDLE_CB_ORDER,
    DRV_IPM_I2C_PREIDLE_CB_ORDER,
    DRV_IPM_SPI_PREIDLE_CB_ORDER,
    DRV_IPM_SYSTEM_DXP1_PREIDLE_CB_ORDER,
    DRV_IPM_AUDIO_GUT_DXP1_PREIDLE_CB_ORDER,
    DRV_IPM_HSI_PREIDLE_CB_ORDER,
    DRV_IPM_SHM_PREIDLE_CB_ORDER,
    DRV_IPM_GPIO_SERVICES_PREIDLE_CB_ORDER,
    DRV_IPM_USB_MAC_PREIDLE_CB_ORDER,
    DRV_IPM_DPRAM_PREIDLE_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP1_PREIDLE_CB_ORDER,
};

/* Pre idle callback order on DXP#2 - in chronological order (low number = high priority) */
enum drv_IpmDxp2PreIdleCallbackOrderEnum {
    DRV_IPM_FDMA_DXP2_PREIDLE_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    /* System driver is saving internal memories (DMEM on 8060 and GMEM on 9040)*/
    DRV_IPM_SYSTEM_DXP2_PREIDLE_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP2_PREIDLE_CB_ORDER,
};

/* Post power down callback order on DXP#0 - in chronological order (low number = high priority) */
enum drv_IpmDxp0PostPowerDownCallbackOrderEnum {
    DRV_IPM_GPIO_POSTPOWERDOWN_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    DRV_IPM_SYSTEM_DXP0_BASICS_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_SYSTEM_DXP0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_XSI_DXP0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_DTE_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_STE0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_DXP0_IO_UNFREEZE_POSTPOWERDOWN_CB_ORDER,
    /* On DXP#0, the following Post PowerDown callbacks execute after the IO unfreeze */
    DRV_IPM_RF0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_GUT_HI_RES_DXP0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_SYNC_RTCCET_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_GUT_LO_RES_DXP0_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP0_POSTIDLE_CB_ORDER, /* must remain last one */
};

/* Post power down callback order on DXP#1 - in chronological order (low number = high priority) */
enum drv_IpmDxp1PostPowerDownCallbackOrderEnum {
    DRV_IPM_SYSTEM_DXP1_POSTPOWERDOWN_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    DRV_IPM_RF1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_USB_MAC_POSTPOWERDOWN_PRE_UNFREEZE_CB_ORDER,
    DRV_IPM_GUT_HI_RES_DXP1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_GUT_LO_RES_DXP1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_USIM_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_DPRAM_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_XSI_DXP1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_HSI_POSTIDLE_CB_ORDER,
    DRV_IPM_SHM_POSTIDLE_CB_ORDER,
    DRV_IPM_GPIO_SERVICES_POSTIDLE_CB_ORDER,
    DRV_IPM_UART_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_AUDIO_GUT_DXP1_POSTPOWERDOW_CB_ORDER,
    DRV_IPM_I2C_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_SAR_POSTIDLE_CB_ORDER,
    DRV_IPM_SPI_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_DXP1_IO_UNFREEZE_POSTPOWERDOWN_CB_ORDER,
    /* On DXP#1, the following Post PowerDown callbacks execute after the IO unfreeze */
    DRV_IPM_RF_PMIC_DXP1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_NOR_FLASH_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_NAND_FLASH_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_PP2_POST_POWER_DOWN_CB_ORDER,
    DRV_IPM_SDC_POSTPOWER_DOWN_CB_ORDER,
    DRV_IPM_AVS_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_USB_MAC_POSTPOWERDOWN_POST_UNFREEZE_CB_ORDER,
    DRV_IPM_IPC_TIMER_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_LL1_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_LL1_GUARD_TIME_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP1_POSTIDLE_CB_ORDER, /* must remain last one */
};

/* Post power down callback order on DXP#2 - in chronological order (low number = high priority) */
enum drv_IpmDxp2PostPowerDownCallbackOrderEnum {
    DRV_IPM_SYSTEM_DXP2_POSTPOWERDOWN_CB_ORDER = DRV_IPM_CALLBACK_MAX_ORDER,
    DRV_IPM_FDMA_DXP2_POSTPOWERDOWN_CB_ORDER,
    DRV_IPM_WAKE_SCH_DXP2_POSTIDLE_CB_ORDER, /* must remain last one */
};


/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public Function Definitions
 ************************************************************************************************/

#endif /* #ifndef DRV_IPM_ORDER_H */

/** @} END OF FILE */
