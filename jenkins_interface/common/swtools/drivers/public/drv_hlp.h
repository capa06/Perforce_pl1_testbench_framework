/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_hlp.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 *
 * @defgroup HlpDriver HSI Link Protocol Driver
 * @{
 */

/**
 * @file drv_hlp.h HLP Interface.
 *
 */ 

#ifndef DRV_HLP_H
#define DRV_HLP_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "icera_global.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/**  Enable HLP power management */
#define DRV_HLP_POWER_MANAGEMENT

/** Num of available serial channels through HLP (including
 *  local & remote loopback channels) */
#define DRV_HLP_SERIAL_NUMCHANNELS          9 

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * Enumeration of channel types
 */
typedef enum
{
    DRV_HLP_CHANNEL_TYPE_CONTROL,  /** control channel */
    DRV_HLP_CHANNEL_TYPE_SERIAL ,  /** serial channel */
    DRV_HLP_CHANNEL_TYPE_NWIF      /** network interface channel */
} drv_HlpChannelType;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/** 
 * 
 * 
 */
void drv_HlpPlatFlush(int signal);

/** 
 * 
 * 
 */
void drv_HlpPlatWakeup ();

/** 
* Initialize the HSI Link Protocol Layer
*  
* @see drv_hlp.h 
*/ 
void drv_HlpPlatInit(int channel);

/** 
 * Initialize serial HLP layer 
 * 
 */
void drv_HlpSerialInitialize();

/** 
* @return HLP platform-specific TX frame size
*/ 
int drv_HlpPlatGetTxSize(void);

#endif /* #ifndef DRV_HLP_H */

/** @} END OF FILE */
