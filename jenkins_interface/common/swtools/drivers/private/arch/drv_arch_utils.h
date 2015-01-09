/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_utils.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 *
 * @{
 */

/**
 * @file drv_arch_utils.h Interface of private functions required by the arch module
 *
 */

#ifndef __DRV_ARCH_UTILS_H__
#define __DRV_ARCH_UTILS_H__

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


/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

/* Correspondance between archive Ids and NOR segment Ids */
extern const int arch_segment_id[];

/*************************************************************************************************
 * Private function declarations
 ************************************************************************************************/
uint8 * GetArchNorSegmentAddress(int arch_id);
int GetArchNorSegmentSize(int arch_id);

#endif /* #ifndef __DRV_ARCH_UTILS_H__ */

/** @} END OF FILE */

