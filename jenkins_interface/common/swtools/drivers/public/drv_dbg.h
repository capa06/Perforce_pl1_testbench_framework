/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2006-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_dbg.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup DbgDriver Debug Services
 * Fault and reboot handling, logging, post-mortem information.
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup DbgDriver
 * @{
 */

/**
 * @file drv_dbg.h Debug interface.
 *
 */

#ifndef DRV_DBG_H
#define DRV_DBG_H

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

#define DRV_DBG_MAX_TPWR_PARAM        4
#define DRV_DBG_DEFAULT_PARAM         0x80000000

/** Size of the loader memory foot print given by &__extmem_size
 * when linking the loader f/w Other applications do not know
 * &__extmem_size from Loader so this shall be hard-coded on
 * the code*/
#define DRV_DBG_LOADER_FW_MEMORY_FOOTPRINT      ( 4 * 1024 *1024 )

/** Maximum value of the first argument of the at%idbgtest=
 *  command
 *  */
#define ATIDBGTEST_PARAM_MASK_MAX      30

#define DRV_DBG_ATIDBGTEST_ASSERT_VALID                     0x927c6a9a
#define DRV_DBG_ATIDBGTEST_ASSERT_START_DRV_INIT            0x38ad7295
#define DRV_DBG_ATIDBGTEST_ASSERT_END_DRV_INIT              0x63db2c84
#define DRV_DBG_ATIDBGTEST_ASSERT_IN_POST_REBOOT_PROCESS    0x83c51baf
#define DRV_DBG_ATIDBGTEST_ASSERT_IN_AFAULT_HANDLER_BEGIN   0x49e2ad17
#define DRV_DBG_ATIDBGTEST_ASSERT_IN_AFAULT_HANDLER_END     0x6a35bb76

#define AT_DBGTEST_PARAMS_MAX 5
#define AT_FFSTEST_PARAMS_MAX 10

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

typedef enum
{
    DRV_DBG_FSI_LOGGING_ENABLE_SHIFT = 0,
    DRV_DBG_SOC_CLK_ON_DXP_IDLE_ENABLE_SHIFT,
} drv_DbgPmConfig;


/* Reboot callback actions */
typedef enum
{
    DRV_DBG_INIT_REBOOT_INFO,
    DRV_DBG_PRE_REBOOT,
    DRV_DBG_POST_REBOOT
} drv_DbgRebootState;


typedef enum
{
    DEBUG_INFO_DISPLAY_LAST,
    DEBUG_INFO_DISPLAY_ALL,
    DEBUG_INFO_DISPLAY_FULL_COREDUMP,
    DEBUG_INFO_DISPLAY_NONINIT,
    DEBUG_INFO_DISPLAY_EVENTS,
} drv_DbgDisplayCfg ;

/** Warning data structure
 *
 * Set of data registered by any layer responsible for handling
 * WARN_ASSERT forwarding to host.
 */
typedef struct
{
    int dxp;
    int (*warn_state)(void);
    int (*warn_handler)(
            const char *filename,
            int line,
            const char *message,
            int n_extra_parameters,
            int *params,
            enum com_DxpInstance dxp);
} DrvDbgWarnData;

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
 * Write debug information from SW module in textual form
 * to the module crash log in the usual printf format
 *
 * @param fmt
 */
extern void drv_DbgCrashLogPrintf(const char *const fmt, ...);


/**
 * Write a pre-formatted buffer containing debug information to the
 * module crash log
 *
 * @param buf   pointer to ASCII buffer (may contain carriage
 *              returns)
 * @param size  size in bytes.
 */
extern size_t drv_DbgCrashLogWrite(char *buf, int size);

/**
 * Write a pre-formatted buffer containing debug information to the
 * dxp events file
 *
 * @param buf  pointer to ASCII buffer (may contain carriage
 *              returns)
 * @param size size in bytes.
 *
 * @return size_t
 */
extern size_t drv_DbgDxpEventsWrite(char *buf, int size);

/**
 * Register a function to be called in the crash handlers.
 * The registered function must not cause any re-scheduling.
 * It may use @see drv_DbgCrashLogPrintf
 * to log additional information in the crash log history.
 *
 * @param shutdown_fct function pointer which take bool
 * value to enable logging
 *
 * @return void
 */
extern void drv_DbgShutDownFctRegister(void (*shutdown_fct)(bool));


/**
 * Power management test associated to
 * the first element of param_array. 0 is returned on success.
 *
 * @param number_of_param
 * @param param_array
 *
 * @return char*
 */
extern char *drv_DebugATCmdTPWR(int32 number_of_param, int32* param_array);


/**
 * Initialise the crash logs and platform information.
 */
extern void drv_DbgCrashLogInit(void);

/**
 * keep on updating the platform information with info from
 * flash.
 */
extern void drv_DbgPlatformInfoUpdate(void);

/**
 * Tell wether we're specifically restarting from a crash that
 * occured in BT2 or BT3.
 *
 *
 * @return bool
 */
extern bool drv_DbgComingFromBootCrash(void);

/**
 * Tell whether we are restarting from a crash
 **/
extern bool drv_DbgComingFromCrash(void);

/**
 * Same than drv_DbgComingFromCrash() but used by bt2 prior to
 * noninit init  so does not contain any trace
 **/
extern bool drv_DbgComingFromCrashLight(void);

/**
 * Check the reboot counter to avoid repeated failure to boot to
 * modem mode. Abort the start-up and switch to LDR mode when
 * rebooting from crash and the DRV_DBG_REBOOT_MAX_COUNT is reached.
 * @return bool true if require to reboot in Loader
 */
extern bool drv_DbgRbtCountCheck();

/******** Full Core Dump functions prototyping *********/

/**
 * Enable the Full Core Dump feature
 *
 * @param void
 * @return bool
 *
 */
extern bool drv_DbgEnableFullCoreDumpFeature(void);


/**
 * Disable the Full Core Dump feature
 * @param void
 * @return void
 */
extern void drv_DbgDisableFullCoreDumpFeature(void);


/**
 * Check whether the full core dump over USB feature is enabled
 * (from AT%ICOREDUMPCFG)
 * @param void
 * @return bool true if the FullCoreDump feature is enabled,
 *         return false otherwise
 */
extern bool drv_DbgIsFullCoreDumpFeatureEnabled(void);


/**
 * Check whether the full core dump over HIF feature is enabled
 * and if a full core dump is available (coming from crash)
 * @param void
 * @return bool true if the FullCoreDump can be retrieved on HIF
 *         (assumes that Running firmware is Loader
 *     return false otherwise
 */
extern bool drv_DbgIsFullCoreDumpAvailable(void);


/**
 * Prevent any further full core dump download of the
 * previous carsh firmware if available
 * @param void
 * @return void
 */
extern void drv_DbgFullCoreDumpReset(void);




/**
 * Sent the string back for the AT%ICOREDUMPCFG=? command in
 * modem mode
 * @return void
 */
extern void drv_DbgAtIdbgCoreDumpCfgExtendedRange(int entity, void (*atprintln)(int entity, char *buf));


/**
 * Sent the string back for the AT%ICOREDUMPCFG command in modem
 * mode
 * @return void
 */
extern void drv_DbgAtIdbgCoreDumpCfgExtendedAction(int entity, void (*atprintln)(int entity, char *buf));


/******** End of Full Core Dump functions prototyping *********/

/**
 * Driver Debug service init.
 */
extern void drv_DbgInit(void);

/**
 * Clear all the debug info
 *
 * @return void
 */
extern void drv_DbgEraseDebugInfo(void);

/**
 * Clear BB events info
 *
 * @return void
 */
extern void drv_DbgEraseEventInfo(void);

/**
 * Return the string for the AT%IDBGTEST command.
 *
 * @return char* pointer to the buffer to be displayed
 */
extern char* drv_DbgAtIdbgExtendedAction();


/**
 * Generate fault to test the assert/afault handler
 *
 * @param type Type of fault
 * @param param1
 * @param param2
 * @param param3
 * @param param4
 *
 * @return bool true if the type is valid
 */
extern bool drv_DbgAtIdbgExtendedAssign(int32 type, int32 *params, int32 params_no, int file, void writeCb(void *file,char *buf) );


/**
 * Return help for AT%IDBGTEST at command
 * To be called with hdl==NULL to start with, then with the
 * previously returned hdl value to continue.
 *
 * The allocated buffer has to be freed by the calling function.
 *
 * @param hdl
 * @param buf_ptr_adr
 *
 * @return void* hdl to be used in the next call. NULL when
 *         finished.
 */
extern void *drv_DbgAtIdbgTestExtendedRange(void *hdl, char **buf_ptr_adr);


/**
 * Return help for AT%DEBUG at command. To be called with
 * hdl==NULL to start with, then with the previously returned
 * hdl value to continue.
 *
 * The allocated buffer has to be freed by the calling function.
 *
 * @param hdl
 * @param buf_ptr_adr
 *
 * @return void* hdl to be used in the next call. NULL when
 *         finished.
 */
extern void *drv_DbgAtDebugExtendedRange(void *hdl, char **buf_ptr_adr);


/**
 * Return the string for the AT%DEBUG at command. To be called
 * with hdl==NULL to start with, then with the previously
 * returned hdl value to continue.
 *
 * The allocated buffer has to be freed by the calling function.
 *
 * @param hdl
 * @param buf_ptr_adr
 * @param display_cfg if true: display all records (otherwise
 *              only new records are shown)
 *
 * @return void*
 */
extern void *drv_DbgAtDebugExtendedAction(void *hdl, char **buf_ptr_adr, drv_DbgDisplayCfg display_cfg);



/**
 * Return the string for the AT%DEBUG= at command. To be called
 * with hdl==NULL to start with, then with the previously
 * returned hdl value to continue.
 *
 * The allocated buffer has to be freed by the calling function.
 *
 * @param hdl
 * @param buf_ptr_adr
 * @param display_all if true: display all records (otherwise
 *              only new records are shown)
 *
 * @return void*
 */
extern void *drv_DbgAtDebugExtendedAssign(void *hdl, char **buf_ptr_adr, drv_DbgDisplayCfg display_all);


/**
 * Start system watchdog timer.
 *
 * @param time_to_bark_usec watchdog timer expiration expressed
 *                          in usec
 *
 * Should be called every system tick.
 */
extern void drv_DbgStartWatchdog(uint32 time_to_bark_usec);

/**
 * Refresh system watchdog timer and reset counter.
 *
 * Should be called at each system tick.
 */
extern void drv_DbgRefreshWatchdog( void );

/**
 * Request a Refresh system watchdog timer and reset counter.
 *
 * Should be called at each system tick.
 */
extern void drv_DbgRefreshWatchdogRequest( void );

/**
 * Get current watchdog trigger value.
 *
 * If trigger value is null, then WDT is not activated.
 *
 * @return the watchdog trigger value.
 */
extern int drv_DbgGetWdtTrigger(void);

/**
 * Power Up Watchdog after hibernation
 *
 */
extern int drv_DbgWdtPowerUp(void);

/**
 * Force an immediate Reset via the watchdog
 *
 */
extern int drv_DbgWdtForceResetNow(void);

/**
 * Power Down Watchdog before hibernation
 *
 */
extern int drv_DbgWdtPowerDown(void);

/**
 * Refresh reset counter.
 *
 * Should be called once the system reboot is completed correctly.
 */
extern void drv_DbgClearResetCounter(void);


/**
 * Perform post reboot actions in modem mode.
 *
 * Check reset counter.
 * Preform application specific reboot actions:
 *  - modem hang-up
 *  - send reboot strings
 *  - close MUX
 */
extern void drv_DbgPostRebootProcess(void);

/**
 * Perform Early post reboot actions
 * Save Crashlogs to file system
 * Initialize non Init debug buffers In Loader, prepare for
 * fullcoredump
 */
extern void drv_DbgEarlyPostRebootProcess(void);

/**
 * Perform post reboot actions in loader mode.
 *
 * Check reset counter.
 * Preform application specific reboot actions:
 */
extern void drv_DbgDoRebootCrashLogProcessing();


/**
 * Notify the debug module from a mode switch.
 * Take appropriate action to avoid a reboot in loader as it
 * could happen from a SW reset
 *  */
extern void drv_DbgModeSwitchIndication( drv_FirmwareRtbMode mode, uint32 requester );

/**
 * Initialise the checksum of the read-only memory and store it in reboot extra info
 * Intended use: to be called during cold boot. The checksum can then be recomputed any time
 * to verify that the read-only memory has not changed since.
 * @see drv_DbgRoMemCheck
 * @return void
 */
extern void drv_DbgRoMemCheckInit(void);


/**
 * Get the status of TTP NVRAM.
 *
 * @return The error code of TTP NVRAM (0 for no error)
 */
int drv_DbgGetTtpNvramErrno(void);


/**
 * Set the status of TTP NVRAM.
 *
 * @param num the error code of TTP NVRAM (0 for no error)
 */
void drv_DbgSetTtpNvramErrno(int num);


/**
 * Clear the recorded status of TTP NVRAM
 */
void drv_DbgClearTtpNvramErrno(void);


/**
 * Override the XDV vector
 */
extern void drv_DbgXDVOverride(void);


/**
 * Override the DBW vector
 */
extern void drv_DbgDBWOverride(void);

/**
 * Enable $SR.PDE
 */
extern void drv_DbgEnablePDE(void);

/**
 * Reset the crash indication
 *
 */
extern void drv_DbgRbtCrashIndReset();

extern bool drv_DbgAtIHifTest(int hif_type, int test_case, int param1, int param2, int param3);
extern int drv_DbgAtIHifTestUsage(const char** usage[]);

/**
 * Check if Engineering mode is enabled
 *
 * @return True if Engineering mode is enabled.
 */
extern bool drv_DbgIsEngineeringModeEnabled(void);

/**
 * Warn the driver module that Engineering mode has just been
 * enabled
 *
 * @return void.
 */
extern void drv_DbgEngineeringModeIsTurnedOn(void);

/**
 * Warn the driver module that Engineering mode has just been
 * disabled
 *
 * @return void.
 */
extern void drv_DbgEngineeringModeIsTurnedOff(void);

/**
 * Return AT commange usage string line for AT%IDATABKPT?
 *
 * @param usage  ditto
 *
 * @return success.
 */
extern int drv_DbgAtIDataBkptTestUsage(const char** usage[]);

/**
 * Lay Data break point at range boundaries (see AT%IDATABKPT)
 *
 * @param dxp_instance  ditto. 3 means both (all) DXPs
 * @param access_type 0: load, 1: store, 2: load/store
 * @param inside_outside 0: inside, 1: outside
 * @param override_ext_dbkpt: replace data breakpoint set in
 *                          external debug mode by the one
 *                          defined by the following range
 * @param low_addr lower boundary of watched range
 * @param hi_addr  upper boundary of watched range
 *
 * @return success.
 */
extern bool drv_DbgAtIDataBkpt(int dxp_instance, int access_type, int inside_outside, bool override_ext_dbkpt, int low_addr, int hi_addr);

/**
 * Lay data breakpoint when writing in other DXP's initialized data section
 *
 * @return success.
 */
extern bool drv_DbgCatchBadCachedInitdata(int dxp_instance_whose_data_section_is_watched);

/**
 * Lay data breakpoint when writing in other DXP's bss data section
 *
 * @return success.
 */
extern bool drv_DbgCatchBadCachedBss(int dxp_instance_whose_bss_section_is_watched);


/**
 * return a pointer to the memory space in NonInit that can be
 * used for the heap of yaffs2  when running the bt2
 *
 * @return int
 */
extern int drv_DbgGetYaffs2HeapBase();

/**
 * Call back to warn any yaffs2 heap top change in bt2
 *
 * @return void
 */
extern void drv_DbgYaffs2HeapTopChange(uint8* heap_top);


/** function used to generate a deliberate assert during Modem
 * initialization in order to test the reset counter mechanism
 * triggered by at%idbgtest=16,x,y AT cmd
 */
extern void drv_DbgCheckDeliberateAssertForTest(int dxp_instance, int assert_location);


/** function used to generate a deliberate assert during Modem
 * initialization in order to test the reset counter mechanism
 * triggered by at%idbgtest=16,x,y AT cmd
 */
extern void drv_DbgSetDeliberateAssertForTest(int param1, int param2);


/** Get the start address of the noninit logging buffer
 * and its  size
 */
extern char* drv_DbgGetNoninitLoggingBuffer(int *buf_size);

/**
 * Data Breakpoint BREAK event treatment
 * @param IN dxp_instance for which we retrive the data breakpoint range
 * @param OUT *low, *hi pointers to pass boundaries of monitored range
 * @param OUT *name pointer to pass name of monitored range if any
 */
extern void drv_DbgGetDBKPTRange(int dxp_instance, uint32 * low, uint32 * hi, char ** name);
/**
 * Set a Data Breakpoint
 * @param dxp_instance_mask  bit filed of addressed DXPs
 * @param load  1: monitor, 0: ignore  reads in interval
 * @param store  1: monitor, 0: ignore  writes in interval
 * @param inside_outside  1: outside, 0: indide range
 * @param override_ext_dbkpt: replace data breakpoint set in
 *                          external debug mode by the one
 *                          defined by the following range
 * @param low_addr lower boundary of watched range
 * @param hi_addr  upper boundary of watched rangeBREAK event treatment
 */
extern bool drv_DbgSetDataBkpt(int dxp_instance_mask, int load, int store, int inside_outside,
                            bool override_ext_debug_dbkpt, int low_addr, int hi_addr);

/**
 * Retrieves the current (momentary) Vdd set by DFLL
 *
 * @return Vdd in mV
 */
extern uint32 drv_DbgDfllGetVdd(void);

void drv_MemProtectionDefaultRangeMonitor(int whoami);

void drv_MemProtectionRangeRegister(int cpu_id, uint32 low_addr, uint32 hi_addr, const char * range_name);

/**
 *  Register a warning handler
 *
 *  This may be used by modem upper layer to handle warn assert as real warnings
 *  If no warning handler is registered, then real assert occurs...
 *
 * The current implementation allows only a single warning handler.
 * Only the most recently registered handler is invoked.
 */
int drv_DbgRegisterWarnAssert(const DrvDbgWarnData *data);

/**
 * Create background test task
 */
void drv_DbgTestInit(void);
void drv_DbgRFMInfoUpdate(void);
void drv_DbgPutRFMInfo(char * rfmboardid,char * rfmbatchid);

/**
 * Register the statistics for the debug module
 */
void drv_DbgStatsInit(void);


void drv_DbgSyslogInit(void);

#endif /* DRV_DBG_H */

/** @} END OF FILE */
