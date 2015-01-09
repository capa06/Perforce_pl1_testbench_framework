/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_test.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup TestDriver Debug Services
 * HighLevelServices 
 */

/**
 * @addtogroup TestDriver
 * @{
 */

/**
 * @file drv_test.h Debug interface.
 *
 */

#ifndef DRV_TEST_H
#define DRV_TEST_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "drv_global.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <stdlib.h>

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/** drv_DbgAtSetPinCtrl and drv_DbgAtGetPinCtrl values for value parameter
 */
typedef enum
{
    DRV_DBG_FT_PIN_PULLDOWN,
    DRV_DBG_FT_PIN_PULLUP,
    DRV_DBG_FT_PIN_BOTH,
    DRV_DBG_FT_PIN_NONE,
    DRV_DBG_FT_PIN_DEFAULT,
    DRV_DBG_FT_PIN_INVALID,
} drv_TestPinCtrlState;

/** drv_DbgAtSetPinCtrl and drv_DbgAtGetPinCtrl values for hw_block parameter
 */
typedef enum
{
    DRV_DBG_FT_HWBLOCK_HSIC,
    DRV_DBG_FT_HWBLOCK_I2S,
    DRV_DBG_FT_HWBLOCK_MAX,
} drv_TestHwBlock;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public constant declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/


/**
 * Functions to test HW pins connection  in factory
 */
bool drv_TestAtSetPinCtrl(drv_TestHwBlock hw_block, unsigned int pin, drv_TestPinCtrlState value);
bool drv_TestAtGetPinCtrl(drv_TestHwBlock hw_block, unsigned int pin, drv_TestPinCtrlState* value);

void *drv_TestAtIFlashFSTestRange(void *hdl, char **buf_ptr_adr);
char *drv_TestAtIFlashFSTestAction(void);
bool drv_TestAtIFlashFSTestAssign(int32 type, int32 *params, int32 params_no, int file, void writeCb(void *file,char *buf) );


bool drv_test_misc(int32 type, int32 *params, int32 params_no, int file, void writeCb(void *file,char *buf) );

#endif /* DRV_DBG_H */

/** @} END OF FILE */
