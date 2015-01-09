

/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2004
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch_loader.h#1 $
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
  * @file drv_arch_loader.h entry points for loader code shared with modem and loader
  *
  */

#ifndef DRV_ARCH_LOADER_H
#define DRV_ARCH_LOADER_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern int drv_arch_nverase(bool eraseSimLockFile);
extern int drv_arch_perform_programming(tAppliFileHeader *dld_fh_ptr, bool in_flash, 
                                        bool check_even_in_flash, uint8 *update_key_id, 
                                        uint8 *file_hash, uint8 *file_signature, 
                                        uint8 *file_ppid, uint8 *temp_buffer, size_t temp_buffer_size, 
                                        uint32 do_flash_update, void(*special_print)(const char*, ...), 
                                        void (*flashCB)(int));
extern uint8 *file_storage_start;
#endif /* DRV_ARCH_LOADER_H */

/** }@ END OF FILE */



