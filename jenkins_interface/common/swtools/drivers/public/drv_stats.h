
/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_stats.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DrvStats Driver Statistics
 * @ingroup  Driver
 */

/**
 * @addtogroup DrvStats
 * @{
 */

/**
 * @file drv_stats.h Driver Statistics interface. 
 *       This driver can be used to manage/monitor driver
 *       statistics
 */

#ifndef DRV_STATS_H
#define DRV_STATS_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "com_machine.h"                /* machine definitions */
#include "drv_stats_ids.h"
#include "drv_stats.h"                  /* statistics */
#include "drv_stats_ids.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define DRV_STATS_LAST_ITEM { DRV_STATS_ID_LAST_ITEM_ID,     NULL,      DRV_STATS_TYPE_INVALID,      0,   NULL }

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 *  enumeration of statistical item types
 */
typedef enum 
{
    DRV_STATS_TYPE_DICT=0,   /** dictionary */
    DRV_STATS_TYPE_INT,      /** integer */  
    DRV_STATS_TYPE_INT_ARR,  /** array of integers */
    DRV_STATS_TYPE_STR,      /** string */  
    DRV_STATS_TYPE_STR_ARR,  /** array of strings */
    DRV_STATS_TYPE_INVALID,  /** invalid item */
} drv_StatsItemType; 

/**
 *  enumeration of enable values
 */
typedef enum 
{
    DRV_STATS_EVT_FAULT=BIT(0),   /** Fault (assert, ...) */  
    DRV_STATS_EVT_AT=BIT(1)     /** AT-command */
} drv_StatsEvents; 

/**
 *  enumeration of return codes
 */
typedef enum 
{
    DRV_STATS_OK=0,       /** success */
    DRV_STATS_ERROR       /** failure */  
} drv_StatsRetCode; 

/**
 *  enumeration of actions
 */
typedef enum 
{
    DRV_STATS_ACTION_SET_EVENT_MASK=0,
    DRV_STATS_ACTION_RESET_ITEM=1,
    DRV_STATS_ACTION_DUMP_MODULES_STATS,
    DRV_STATS_ACTION_SHOW_MODULES_INFO,
} drv_StatsActionCode; 


/**
 * Type definition for a Driver handle
 *
*/
typedef void *drv_StatsHandle;

/**
 * Type definition for the user callback that returns an item 
 * integer value
 *
 * @param driver_handle The driver handle (returned at init 
 *                      time)
 * @param item_id       Item ID 
 * @param int_value     Pointer to a 32-bit variable receiving 
 *                      the item value
 */
typedef void (*drv_StatsIntItemCb)(drv_StatsHandle driver_handle, drv_StatsItemId item_id, int32 *int_value);

/**
 * Type definition for the user callback that returns an item 
 * integer array value 
 *
 * @param driver_handle       The driver handle (returned at 
 *                            init time)
 * @param item_id             Item ID 
 * @param int_array_value     Array of 32-bit values receiving 
 *                            item value
 * @param array_len           Length of the array pointed to by 
 *                            int_array_value
 * @return Number of values returned
 */
typedef int32 (*drv_StatsIntArrayItemCb)(drv_StatsHandle driver_handle, drv_StatsItemId item_id, int32 *int_array_value, int32 array_len);

/**
 * Type definition for the user callback that returns an item 
 * string value 
 *
 * @param driver_handle       The driver handle (returned at 
 *                            init time)
 * @param item_id             Item ID 
 * @param str_value           Pointer to a string receiving the 
 *                            string value
 * @param str_len             Length of the string pointed to by
 *                            str_value
 */
typedef void (*drv_StatsStrItemCb)(drv_StatsHandle driver_handle, drv_StatsItemId item_id, char *str_value, int32 str_len);

/**
 * Type definition for the user callback that returns an item 
 * string array value 
 *
 * @param driver_handle       The driver handle (returned at 
 *                            init time)
 * @param item_id             Item ID 
 * @param str_array_value     Array of strings receiving the 
 *                            item value
 * @param str_len             Length of the string pointed to by
 *                            str_value
 * @return Number of values returned
 */
typedef int32 (*drv_StatsStrArrayItemCb)(drv_StatsHandle driver_handle, drv_StatsItemId item_id, char **str_array_value, int32 str_len, int32 array_len);

/**
 * Type definition for the user callback to perform some action 
 * on an item (enable, disable, reset).
 *
 * @param driver_handle       The driver handle (returned at 
 *                            init time)
 * @param item_id             Item ID 
 * @param action              The action to perform 
 * @param event_mask          Item Event mask 
 */
typedef void (*drv_StatsItemActionCb)(drv_StatsHandle driver_handle, drv_StatsItemId item_id, drv_StatsActionCode action, uint32 event_mask);

/** 
 * Type definition for the stats callback 
 *  
 * The "value" callbacks are mandatory for all item types that 
 * the module registers for. 
 *  
 * Example: if the module registers "int" items only, then only 
 * the intValCb must be provided, all other callbacks may be set 
 * to NULL 
 *  
 * The actionCb is optional and can be used to perform the 
 * necessary houseworking to enable/disable/reset an item. 
 * Enabling/disabling items is taken care of by the stats 
 * framework but the callback is invoked in order to allow 
 * for the registered driver to perform some action. 
 */
typedef struct drv_StatsCallbacksTag
{
    drv_StatsIntItemCb intValCb;
    drv_StatsIntArrayItemCb intArrValCb;
    drv_StatsStrItemCb strValCb;
    drv_StatsStrArrayItemCb strArrValCb;
    drv_StatsItemActionCb actionCb;
} drv_StatsCallbacks;

/**
 * Type definition for a statistical item 
 *  
 * Naming conventions: please name your items after valid Python 
 * names. Avoid hyphens, spaces, accents, brackets, etc. 
 *  
 * Also, the following names are reserved keywords: 
 * id, event_mask, state, type 
 *
*/
typedef struct drv_StatsItemTag
{
    int32 id;                /** item id */
    char *name;              /** item name */
    drv_StatsItemType type;  /** item type */
    uint32 event_mask;       /** event mask (c.f. drv_StatsEvents) */
    struct drv_StatsItemTag *subnodes; /** array of subnodes - this must be NULL terminated */
} drv_StatsItem;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/** 
* Init function for the stats module
* 
* This function must be called on both DXPs
*/
void drv_StatsInit(void);

/** 
* Module registration
* 
* Modules may call this function to register to the stats 
* driver. They must provide a pointer to their root statistical 
* item (which may be a dictionary if the module needs to export 
* more than 1 item). Modules must also provide a pointer to 
* their functional interface. 
* 
* @param top_level_item Top-level item 
* @param callbacks Functional interface for the module 
* @return handle 
*/
drv_StatsHandle drv_StatsRegister(drv_StatsItem *top_level_item, const drv_StatsCallbacks *callbacks);

/** 
* Function called when user types in "AT%IDRVSTAT?" 
*  
* @param file file handle of the file to write to
* @param writeCb Callback function to write to file
* @return boolean to indicate success/failure 
*  
*/
bool drv_StatsExtendedQuery(int file, void writeCb(void *file,char *buf));

/** 
* Function called when user types in "AT%IDRVSTAT" 
*  
* @param file file handle of the file to write to
* @param writeCb Callback function to write to file
* @return boolean to indicate success/failure 
*  
*/
bool drv_StatsExtendedAction(int file, void writeCb(void *file,char *buf));

/** 
* Function called when user types in "AT%IDRVSTAT=action,id" 
*  
* @param action The action to perform 
* @param id The ID of the item to perform the action on 
* @param event_mask Event mask (in case 
*                   action==DRV_STATS_ACTION_SET_EVENT_MASK)
* @param file file handle of the file to write to
* @param writeCb Callback function to write to file
* @return boolean to indicate success/failure 
*  
*/
bool drv_StatsExtendedAssign(unsigned int action, int id, unsigned int event_mask, int file, void writeCb(void *file,char *buf));

/** 
* Return histogram index of a sample, given the min value, max 
* value and number of bins. Clipping is performed if the sample 
* value falls outside the [min, max] range 
*  
* @param sample The sample value 
* @param min The min value 
* @param max The max value 
* @param bins The number of bins 
* @return 
*  
*/
uint32 drv_StatsHistIndex(int32 sample, int32 min, int32 max, uint32 bins);

/** 
* Return integer log (base 2) of rescaled sample. Clipping is 
* performed is log2 falls outside [0, max]
*  
* @param sample The sample value 
* @param prescale Scaling factor to apply to sample before 
*              computing log2 value
* @param max   Max value 
* @return 
*  
*/
uint32 drv_StatsLog2(int32 sample, double prescale, uint32 max );


#endif /* #ifndef DRV_STATS_H */

/** @} END OF FILE */

