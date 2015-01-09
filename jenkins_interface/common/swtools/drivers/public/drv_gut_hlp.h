/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2012
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_gut_hlp.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup drv_gut GUT HLP Driver
 * @ingroup SoCLowLevelDrv
 */

/**
 * @addtogroup drv_gut
 * @{
 */

/**
 * @file drv_gut_hlp.h Gut driver HLP extensions (9xxx)
 *
 */

#ifndef DRV_GUT_HLP_H
#define DRV_GUT_HLP_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#include "livanto_config.h"
#include "drv_spu.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
/* 

NOTES:
    - An extra threshold should be appended to the list of thresholds to schedule.
    - The SIC word is offset to the threshold expiring (taken from next entry).
    - The last threshold required should be unique.
    - The dummy threshold added at the end to contain the last SIC word should be last threshold + 1 with SIC MASK of 0.
    - Each threshold should be unique and increasing time order.
        
        THRESHOLD       SIC MASK        SIC WORD
        entry0            1                X
        entry1            1               sic0
        entry2            1               sic1
        entry3            1               sic2
        entry4            1               sic3
        entry5            1               sic4    (entry 5 threshold should be unique)
        dummy (entry5+1)  0               sic5

EXAMPLE:

// Array of threshold / sic word values
// Must be in memory which can be DMA'd from (non-cached) and whose contents
// survive past the non-blocking call to drv_GutHlpScheduleMultiple()
static DXP_COMMONIDATA drv_GutHlpEntry _entries[];

void schedule(int t0_offset, int t0_sic_word, int t1_offset, int t1_sic_word, int t2_offset, int t2_sic_word)
{
    uint64 now = drv_GutGetTimeStamp(gut);

    // Threshold 0
    _entries[0].threshold = DRV_GUT_HLP_THRESHOLD_FIELD(now + t0_offset);
    _entries[0].ctrl    = DRV_GUT_HLP_CTRL_FIELD(1, 0);
    
    // Threshold 1 + SIC word for T0
    _entries[1].threshold = DRV_GUT_HLP_THRESHOLD_FIELD(now + t1_offset);
    _entries[1].ctrl    = DRV_GUT_HLP_CTRL_FIELD(1, t0_sic_word);

    // Threshold 2 + SIC word for T1
    _entries[2].threshold = DRV_GUT_HLP_THRESHOLD_FIELD(now + t2_offset);
    _entries[2].ctrl    = DRV_GUT_HLP_CTRL_FIELD(1, t1_sic_word);

    // (Threshold 2 + 1) + SIC word for T2 [Dummy entry]
    _entries[3].threshold = DRV_GUT_HLP_THRESHOLD_FIELD(now + t2_offset + 1);
    _entries[3].ctrl    = DRV_GUT_HLP_CTRL_FIELD(0, t2_sic_word);

    uint64 latest_time = now + t2_offset + 1;

    // Schedule block of 3 thresholds + dummy entry
    drv_GutHlpScheduleMultiple(0, _entries, 4, latest_time);
}

*/

/* Threshold mask */
#define DRV_GUT_HLP_CET_COUNTER_MASK                  ((uint64)(BIT(CET_N_COUNTBITS)-1))

/* Used for creating drv_GutHlpEntry.ctrl */
#define DRV_GUT_HLP_CTRL_FIELD(sic_mask, sic_word)    ( (sic_mask ? (GUT_HLP_CTRL_SIC_MASK_MASK << GUT_HLP_CTRL_SIC_MASK_SHIFT) : 0) | \
                                                      ((sic_word & GUT_HLP_CTRL_SIC_WORD_MASK) << GUT_HLP_CTRL_SIC_WORD_SHIFT) )
/* 
  Current GUT HLP only works with prescale = 1.
  Used for creating drv_GutHlpEntry.threshold
*/
#define DRV_GUT_HLP_THRESHOLD_FIELD(threshold)    ((uint32)((threshold) & DRV_GUT_HLP_CET_COUNTER_MASK))

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

typedef struct
{
    /* Word 0: 20-bit threshold (formed by DRV_GUT_HLP_THRESHOLD_FIELD) */
    uint32 threshold;
    /* Word 1: Control field (formed by DRV_GUT_HLP_CTRL_FIELD) */
    uint32 ctrl;
} drv_GutHlpEntry;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Initialise the HLP driver.
 * Required before calling drv_GutHlpScheduleMultiple.
 * NOTE: DXP0 Only!
 */
extern void drv_GutHlpInit(void);

/**
 * Configure DMA for transfer to HLP channel a number of threshold/ctrl pairs.
 * NOTE: DXP0 Only!
 *
 * @param hlp_channel       - Which HLP channel to use (0 - max DRV_GUT_HLP_MAX_CHANNELS-1)
 * @param entries           - Array of threshold/ctrl pairs in sorted time order
 * @param count             - Number of threshold/ctrl pairs
 * @param latest_entry_time - The last entry's time value (absolute / 64-bit value)
 * @return                    Returns request index (circular buffer index)
 */
extern int drv_GutHlpScheduleMultiple(int hlp_channel, drv_GutHlpEntry *entries, int count, uint64 latest_entry_time);

/**
 * Schedule a single trigger event.
 * It is recommended that drv_GutHlpScheduleMultiple is used instead as this is a costly way
 * to schedule a threshold event.
 * NOTE: DXP0 Only!
 *
 * @param hlp_channel       - Which HLP channel to use (0 - max DRV_GUT_HLP_MAX_CHANNELS-1) 
 * @param absolute_time     - Absolute threshold time
 * @param sic_word          - SIC word to be generated by trigger
 * @return                    Returns request index (circular buffer index)
 */
extern int drv_GutHlpScheduleSingle(int hlp_channel, uint64 absolute_time, uint8 sic_word);

/**
 * Configure SPU slave target for a particular HLP channel.
 * NOTE: DXP0 Only!
 *
 * @param hlp_channel       - Which HLP channel to use (0 - max DRV_GUT_HLP_MAX_CHANNELS-1)
 * @param spu_slave         - Single SPU slave to be the target for this HLP channel
 */
extern void drv_GutHlpConfigureSpuSlave(int hlp_channel, drv_SpuSlave spu_slave);

/**
 * Is the DMA context used by HLP active?
 * NOTE: DXP0 Only!
 *
 * @param hlp_channel       - Which HLP channel to use (0 - max DRV_GUT_HLP_MAX_CHANNELS-1)
 * @return                    Returns true if active
 */
extern int drv_GutHlpIsDmaActive(int hlp_channel);

/**
 * Get the number of HLP channels enabled in this build.
 */
extern int drv_GutHlpNumberOfChannels(void);

#endif

/** @} END OF FILE */
