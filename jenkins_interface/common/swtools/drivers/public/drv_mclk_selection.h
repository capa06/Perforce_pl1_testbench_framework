/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_mclk_selection.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup Clocks Clocks
 * @ingroup  Clocks
 */

/**
 * @addtogroup Clocks
 * @{
 */

/**
 * @file drv_mclk_selection.h MCLK/CET selection depending on platform
 *
 */

#ifndef DRV_MCLK_SELECTION_H
#define DRV_MCLK_SELECTION_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_3gpp.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* selection of MCLK frequency for the platform */

/* 38.4 MHz is the default and only (at the moment) MCLK speed for 9xxx */
#define DRV_CLK_PLATFORM_MCLK (38400000)

/* Quarter-chips rate (in Hz) */
#define DRV_CLK_QCHIPS_RATE (4*COM_3G_CHIPS_PER_SECOND)

/* select CET input clock and CET clock (CET tick rate) speeds */

#if defined (USE_MCLK_FOR_CET_CLK)

#define DRV_CET_INPUT_CLK_SPEED  (DRV_CLK_PLATFORM_MCLK)
#define DRV_CET_CLK_PRESCALE 1

#else /* defined (USE_MCLK_FOR_CET_CLK) */

#ifdef ICERA_INTERNAL_LTE20MHZ
#define DRV_CET_INPUT_CLK_SPEED  (2*DRV_CLK_QCHIPS_RATE)
#define DRV_CET_CLK_PRESCALE 2
#else
#define DRV_CET_INPUT_CLK_SPEED  DRV_CLK_QCHIPS_RATE
#define DRV_CET_CLK_PRESCALE 1
#endif

#endif /* defined (USE_MCLK_FOR_CET_CLK) */

#define DRV_CET_CLK_SPEED  (DRV_CET_INPUT_CLK_SPEED / DRV_CET_CLK_PRESCALE)

/* Macro converting qchips to CET ticks */
#define DRV_QCHIPS_TO_CETTICKS(qchips) (((((DRV_CET_CLK_SPEED / 1000) * 2) / (DRV_CLK_QCHIPS_RATE / 1000)) * (qchips)) / 2)


/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

#endif /* DRV_MCLK_SELECTION_H */

/** @} END OF FILE */

