/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_reg_access.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup TopUtil
 * @{
 */

/**
 * @file drv_reg_access.h  Register access functions
 *
 */

#ifndef DRV_REG_ACCESS_H
#define DRV_REG_ACCESS_H

#include "icera_global.h"

/******************************************************************************/
/*  Defines                                                                   */
/******************************************************************************/

// These MACROs use a BYTE offset - i.e. the values provided by the
// auto-generated header files (from the register spreadsheets).
#define SOC_REG_ADDR(_BASE, _OFFSET) ((_BASE) + (_OFFSET))
#define SOC_REG(_BASE, _OFFSET) (*((volatile uint32 *)SOC_REG_ADDR(_BASE, _OFFSET)))


/******************************************************************************/
/*  Types                                                                     */
/******************************************************************************/

/******************************************************************************/
/*  Variables                                                                 */
/******************************************************************************/

/******************************************************************************/
/*  Basic read/write functions                                                */
/******************************************************************************/

static inline uint32 drv_reg_MemRead(uint32 addr)
{
    volatile uint32 *x;
    x = (volatile uint32 *)addr;
    return *x;
}


/**** Function separator ******************************************************/

static inline void drv_reg_MemWrite(uint32 addr, uint32 val)
{
    volatile uint32 *x;
    x = (volatile uint32 *)addr;
    *x = val;
}


/******************************************************************************/
/*  Field access functions                                                    */
/******************************************************************************/

static inline uint32 drv_reg_GetField(uint32 input_reg_val, uint32 shift, uint32 mask)
{
    uint32 ret_val;

    ret_val = input_reg_val >> shift;
    ret_val &= mask;

    return ret_val;
}


/**** Function separator ******************************************************/

static inline uint32 drv_reg_ReplaceField(uint32 input_reg_val, uint32 field_val, uint32 shift, uint32 mask)
{
    uint32 ret_val;
    uint32 smask;

    smask = mask << shift;

    ret_val = input_reg_val & ~smask;
    ret_val |= (field_val << shift) & smask;

    return ret_val;
}


/**** Function separator ******************************************************/

static inline uint32 drv_reg_OrField(uint32 input_reg_val, uint32 field_val, uint32 shift, uint32 mask)
{
    uint32 ret_val;

    ret_val = input_reg_val | ((field_val & mask) << shift);

    return ret_val;
}


/**** Function separator ******************************************************/

static inline uint32 drv_reg_ClearField(uint32 input_reg_val, uint32 shift, uint32 mask)
{
    uint32 ret_val;

    ret_val = input_reg_val & ~(mask << shift);

    return ret_val;
}


/**** Function separator ******************************************************/

static inline uint32 drv_reg_SetField(uint32 input_reg_val, uint32 shift, uint32 mask)
{
    uint32 ret_val;

    ret_val = input_reg_val | (mask << shift);

    return ret_val;
}


#endif
/** @} END OF FILE */
