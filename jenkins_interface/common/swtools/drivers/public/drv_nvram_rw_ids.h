/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_nvram_rw_ids.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup NvramDriver
 * @{
 */

/**
 * @file drv_nvram_rw_ids.h Definition of NVRAM RW paramters identifiers.
 *
 * ALL NVRAM RW PARAMETERS IDENTIFIERS MUST BE DEFINED IN THIS FILE ONLY.
 *
 */

enum
{
    // VCO parameters
    DRV_NVRAM_RW__VCO_AGEING_OFFSET = DRV_NVRAM_RO__MAX_PARAM_COUNT,
    DRV_NVRAM_RW__VCO_AGEING_NUM_UPDATES,
    DRV_NVRAM_RW__DCXO_TEMP_CURVE_MIN,
    DRV_NVRAM_RW__DCXO_TEMP_CURVE_STEP,
    DRV_NVRAM_RW__DCXO_TEMP_CURVE_DATA,

     // AFC parameters accessed by LL1
    DRV_NVRAM_RW__LL1_AFC_LOCKED,
    DRV_NVRAM_RW__LL1_AFC_TEMPERATURE
};

/** @} END OF FILE */



