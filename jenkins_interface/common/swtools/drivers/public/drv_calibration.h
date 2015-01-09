/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_calibration.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup RfDriverCalibration
 * @{
 */

/**
 * @file drv_calibration.h Calibration Functions
 *
 */

#ifndef DRV_CALIBRATION_H
#define DRV_CALIBRATION_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"                   /* Icera Fundamental definitions. */
#include "drv_nvram.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

// NVRAM_RO id for use in cal load tables to indicate seting the parameter to the size (in
// integers) of the previously loaded parameter.  The load table max_size parameter is ignored.
#define DRV_SIZE_INTS_PREV_NVRAM_PARAM              -1

// value for "invalid_nvram_param_id" to indicate none
#define DRV_NO_INVALID_NVRAM_PARAMS                 -1

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
/**
 * Calibration table map
 */
typedef struct
{
    void *dest;
    int id;
    int max_size;
}
drv_CalTableMap;


/**
 * Calibration table default values
 */
typedef struct
{
    void *dest;
    const void *default_data;
    int size;
}
drv_CalDefaultsMap;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern int invalid_nvram_param_id;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Load a single calibration parameter from RO-NVRAM
 *
 * @return Number of bytes 
 *  
 * @deprecated - use drv_CalLoadInt32() 
 */
extern int drv_CalLoadParam(const drv_CalTableMap *param);

/**
 * Load an int32 calibration parameter from RO-NVRAM
 * 
 * @param id            NVRAM id
 * @param dest          Destination address
 * @param max_size      Max number of int32s
 * 
 * @return              Number of int32s
 */
extern int drv_CalLoadInt32(int id, int32 *dest, int max_size);

/**
 * Load a calibration table from Ro into local memory storage
 *
 * @return true if loaded successfully
 */
extern bool drv_CalLoadTable(const drv_CalTableMap *map_table);

/**
 * Load defaults for undefined calibration table data into local memory storage
 *
 * @return void
 */
extern void drv_CalLoadDefaults(const drv_CalDefaultsMap *defaults_table);

/**
 * Perform a straight line interpolation between points in an array
 *
 * @return true if able to map successfully
 */
static inline int32 interpolate(int32 x, int32 x0, int32 x_step, const int32 *y, int32 num_points)
{
    // clamp the input value to the range of the table
    if (x < x0)
    {
        x = x0;
    }

    int32 offset = x - x0;
    int32 idx1 = offset / x_step;
    int32 rem = offset - idx1 * x_step;

    if (idx1 >= (num_points-1))
    {
        idx1 = num_points - 1;
    }

    int32 idx2 = idx1 + 1;
    if (idx2 >= (num_points-1))
    {
        idx2 = num_points - 1;
    }

    int32 y1 = y[idx1];
    int32 y2 = y[idx2];

    return y1 + ((y2 - y1) * rem) / x_step;
}

#endif

/** @} END OF FILE */

