/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dfc.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

#ifndef DRV_DFC_H
#define DRV_DFC_H
/**
 * @addtogroup DfcDriver
 * @{
 */

#include "drv_thread_priorities.h"

/**
 * @file drv_dfc.h deferred function call services definitions
 *
 */
#define DRV_DFC_PRIORITY            DFC_PRIORITY            /* PRIO = 147 */

typedef void* dfc_handle;

typedef struct
{
    void (*callback)(void* dfc_args);
    void* ctx;
} dfc_client_struct;

dfc_handle drv_dfc_init(const char* name, uint8 index, os_Priority priority);
void drv_dfc_uninit(dfc_handle handle);
bool drv_dfc_schedule(dfc_handle handle, dfc_client_struct* client, bool single);
bool drv_dfc_remove(dfc_handle handle, dfc_client_struct* client);

#endif /* DRV_DFC_H */
