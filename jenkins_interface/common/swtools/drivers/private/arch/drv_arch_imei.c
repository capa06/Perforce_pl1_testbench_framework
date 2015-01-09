/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_imei.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_imei.c IMEI file utilities
 *
 * IMEI is stored in a secured file in filesystem containing
 * also public platform chip ID and SHA1/RSA signed. File path 
 * in filesystem: see SECURED_IMEI_FILE definition in 
 * drv_fs_cfg.h 
 */ 

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"

#include "drv_fs.h"
#include "drv_arch.h"
#include "drv_arch_local.h"
#include "drv_security.h"
#include "os_uist_ids.h"
#include "drv_arch_imei.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include <string.h>
#include <stdlib.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/

/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
extern int drv_ArchGetImeiFromFile(char *const imei_ptr, const char *const default_imei_ptr, const int default_imei_size)
{
    int ret = 0;
    char *imei_data = NULL;
    int imei_length = 0;
    int imei_data_size = 0;
    int i = 0;

    imei_data = drv_arch_GetDataFromFile(SECURED_IMEI_FILE, &imei_data_size);
    if (imei_data == NULL)
    {
        OS_UIST_SMARKER(DRVARCH_UIST_INVALID_IMEI_FILE);
        ret = -1;   
    }
    else
    {
        /* BGZ11686 : check the IMEI is valid, else use default one */
        for(i=0;i<IMEI_LENGTH;i++)
        {
          if (imei_data[i] > 9)
          {
            ret = -1;
            break;
          }
        }

        if (ret != -1 )
        {
          memcpy(imei_ptr, imei_data, IMEI_LENGTH);
          free(imei_data);
          imei_length = IMEI_LENGTH;
          ret = 0;
        }
    }

    if (ret == -1)
    {
        REL_ASSERT(default_imei_ptr != NULL);
        memcpy(imei_ptr, default_imei_ptr, default_imei_size);
        imei_length = IMEI_LENGTH;
    }

    return imei_length;
}

extern ArchError drv_ArchSetImeiInFile(uint8 *imei_ptr, int imei_len)
{
    DEV_ASSERT_EXTRA(imei_len == IMEI_LENGTH, 1, imei_len);    

    return drv_arch_SetDataInFile(SECURED_IMEI_FILE, imei_ptr, imei_len);
}

extern int drv_arch_HaveValidImeiFile()
{
    int ret = 0;
    char *imei_data = NULL;
    int imei_data_size = 0;
    int i = 0;

	imei_data = drv_arch_GetDataFromFile(SECURED_IMEI_FILE, &imei_data_size);
    if (!imei_data) return 0;
    if (imei_data_size == IMEI_LENGTH)
    {
        for (i=0; i<IMEI_LENGTH; i++)
        {
            if (imei_data[i] > 9) 
            {
                ret = 0;
                break;
            }
            if (imei_data[i] > 0)
            {
                ret = 1;
            }
        }
    }

    free(imei_data);
    return ret;
}


extern int drv_arch_DeleteImeiFile()
{
#if defined (ICERA_FEATURE_ENCRYPTED_IMEI_FILE)
  return(drv_fs_Remove(SECURED_IMEI_FILE));
#else
  /* Operation is not done, so return -1 */
  return (-1);
#endif
}

/** @} END OF FILE */
