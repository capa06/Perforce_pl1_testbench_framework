/*************************************************************************************************
 * Copyright (c) 2014, NVIDIA CORPORATION. All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto. Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/main.br/downloader/updaterlib/private/Updater.cpp#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup updater
 * @{
 *
 */
 /**
 * @file Updater.c Icera archive file downloader via the host
 *       interface.
 *
 */
 /** @} END OF FILE */

/**
 * @addtogroup Comport
 * @{
 *
 */
 /**
 * @file Updater.c Icera archive file downloader via the host
 *       interface.
 *
 */
 /** @} END OF FILE */

 /**
 * @addtogroup ATcmd
 * @{
 *
 */
 /**
 * @file Updater.c Icera archive file downloader via the host
 *       interface.
 *
 */
 /** @} END OF FILE */

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#if !defined(VISUAL_EXPORTS)
#include <unistd.h>
#endif

/*************************************************************************************************
 * Icera Header
 ************************************************************************************************/
#include <ic-socket.h>
#include "Updater.h"
#include "drv_arch_type.h"

#include <string.h>
#include <stdarg.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/stat.h>


#if defined (_WIN32)
#include "ic-at-port-mbim.h"
#include "ic-at-port-winusb.h"
#include "ic-com.h"
#include <ic-mbim.h>
#endif

#include <ic-device-detect.h>
#include <ic-at-port.h>
#include "ic-at-port-socket.h"
#include <ic-log.h>

#ifdef _WIN32

#include <direct.h>
#include <malloc.h>
#include <setupapi.h>

#define DelayInSecond(D)    Sleep((D) * 1000)
#define PATH_SEP            ((char)'\\')
#define COMMAND_LINE        "cmd.exe /C \"\"%s\\%s\"%s\"%s\\%s\"\""
#define PIPE_HANDLE         HANDLE

#else

#include <syslog.h>
#include <assert.h>

#define DelayInSecond(D)    sleep(D)
#define PATH_SEP            ((char)'/')
#define COMMAND_LINE        "\"%s/%s\" %s \"%s/%s\""
#define PIPE_HANDLE         FILE*

#endif /* _WIN32 */

#define COMMAND_LINE_LENGTH (strlen(COMMAND_LINE) - (strlen("%s") * 5))

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/
typedef IcAtPort* COM_Handle;

/**
 * UPD Handle s structure
 */
typedef struct
{
    /* Configuration options */
    int              option_verbose;
    int              option_modechange;
    int              option_speed;
    int              option_delay;
    unsigned short   option_block_sz;
    char             *option_dev_name;
    bool             option_check_mode_restore;
    bool             option_autodetection;
    bool              option_standalone_loader;
    int              log_sys_state;
    int              option_send_nvclean;
    int              option_check_pkgv;

    /* Data */
    /* I/O buffers for download protocol */
    unsigned char    tx_buf[2/* AAxx */ + MAX_BLOCK_SZ + 1/* Data */ + 2/* Checksum */];
    unsigned char    rx_buf[0x400];
    int              com_mode;
    COM_Handle       com_hdl;
    COM_Settings     com_settings;
    struct {
        int         step;
        int         percent;
        int         totalweight;
        struct {
            int      base;
            int      weight;
        }            current;
    }                progress;
    /* Whether we have logged a particular mode or not */
    int logging_done[MODE_LOADER + 1];
    /* convenience buffer for log messages */
    char log_buffer[MAX_LOGMSG_SIZE];
    /* Logging callback */
    log_callback_type log_callback;
    FILE *log_file;
    MUTEX_TYPE  mutex_log;
    #ifdef _WIN32
    /* PNP notification */
    char devicepath[MAX_PATH];
    pnp_callback_type pnp_callback;
    HDEVNOTIFY hdev[MAX_REGISTERED];
    HWND hwnd;
    DWORD threadid;
    UINT timeout;
    #endif /* _WIN32 */

    /* UART server info */
    bool uart_srv_started;
    
    bool disable_full_coredump;
    int used;
    int nvCleanCount;

} UPD_Handle_s;

#define UPD_HANDLE_FIRST (1)
#define UPD_HANDLE_LAST  (10)
#define VALID_HANDLE(h)  (((h) >= UPD_FIRST_HANDLE) && ((h) <= UPD_LAST_HANDLE))
#define DEFAULT_HANDLE   UPD_HANDLE_FIRST

/* Index 0 is used for the case where no handle is used (keep old API working),
 * user level handles start from index 1 (handle 2)
 * Handles start from 1, to be able to use 0 as an invalid handle.
 */
#define HDATA(index) handles[((index) - 1)]

#define FW_NUMBER       "number "
#define FW_VERSION      "version "

#define FW_MODEM        "Modem"

#define TAG_START_NB    "<changelist>"
#define TAG_START_VER   "<versionNumber>"
#define TAG_END_NB      "</changelist>"
#define TAG_END         "</ExtendedHeader>"

#define DIGIT_SET       "0123456789"
#define DIGITS_EXTRA    DIGIT_SET " ."

#define COMMAND_LISTS    2             /* all, modem and loader */

#define MAX_PERCENT_FILE_SIZE   (0x7FFFFFFF / 100)

#ifdef _WIN32
#define OS_TYPE     "windows"
#define IDT_TIMEOUT 333

CONST GUID guids[] = { DEVCLASS_MODEM_GUID, DEVCLASS_COMPORT_GUID };
#define NB_GUIDS    ARRAY_SIZE(guids)
#define GUID_STRING "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}"
#define DEBUG_LOG(M)    OutputDebugString(M)

#else /* _WIN32 */

/* Linux or Android */
#define OS_TYPE         "linux"
#ifndef ANDROID
#define DEBUG_LOG(M)    syslog(LOG_MAKEPRI(LOG_USER, LOG_DEBUG), "%s\n", M)
#else
#define DEBUG_LOG(M)
#endif

#endif /* _WIN32 */

#ifdef ICERA_EXPORTS
extern "C"{
#endif
ICERA_API const int ErrorCode_Error = 0;
ICERA_API const int ErrorCode_Success = 1;
ICERA_API const int ErrorCode_FileNotFound = 2;
ICERA_API const int ErrorCode_DeviceNotFound = 3;
ICERA_API const int ErrorCode_AT = 4;
ICERA_API const int ErrorCode_DownloadError = 5;
ICERA_API const int ErrorCode_ConnectionError = 6;
ICERA_API const int ErrorCode_InvalidHeader = 7;

ICERA_API const int ProgressStep_Error = 0;
ICERA_API const int ProgressStep_Init = 1;
ICERA_API const int ProgressStep_Download = 2;
ICERA_API const int ProgressStep_Flash = 3;
ICERA_API const int ProgressStep_Finalize = 4;
ICERA_API const int ProgressStep_Finish = 5;

ICERA_API const int status_bad_parameter        = -32000;
ICERA_API const int status_no_enough_memory     = -1;
ICERA_API const int status_error                = 0;
ICERA_API const int status_not_found            = 0;
ICERA_API const int status_success              = 1;
ICERA_API const int status_found                = 1;
#ifdef ICERA_EXPORTS
}
#endif

static int debug_level = 0;

/* used along with the legacy (deprecated) API, Updater */
static bool disable_full_coredump = 0;
static bool global_check_mode_restore = true;
#ifdef _WIN32
    static bool m_closeNeeded = true;
#endif

/* Upgrade reasons */
enum
{
    FILE_NO_UPDATE = 0,          /* File does not need to be upgraded */
    FILE_UPDATE_NO_VERSION_DATA, /* File should be upgraded as there is no version number to tell for sure */
    FILE_UPDATE_NEWER            /* File should be upgraded as it is definitely newer than the existing one */
} ;

#define PKGV_EXTENSION ".pkgv"
#define IS_PKGV_FILE(_file) ((strlen((_file)) > (sizeof(PKGV_EXTENSION) - 1)) && (strcmp((_file) + strlen((_file)) - sizeof(PKGV_EXTENSION) + 1, PKGV_EXTENSION) == 0))
#define PKGV_LEN_VERSION    16
#define PKGV_LEN_DATE       20
#define PKGV_LEN_SVN        2
#define PKGV_LEN_FCD        2


#define KILOBYTE            1024
#define MEGABYTE            (KILOBYTE * KILOBYTE)
#define GET_FILE_WEIGHT(F)  (((FileSize(F) / KILOBYTE) + 1) * 2)

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/
#ifndef WIN32
static int min(int a, int b)
{
    return (a<b) ? a:b;
}
#endif

#ifdef ICERA_EXPORTS
extern "C"{
#endif
ICERA_API int SwitchModeEx(UPD_Handle handle, unsigned int mode, bool checkSuccess);

/**
* @details Send command and wait response til receiving "OK" or "ERROR", or timeout.
* @param handle -the handle which is allocated for one port where a device is connected.
* @param cmd : the pointer which indicates the string input for AT command.
* @param timeout_sec : timeout in second for waiting the response.
* @param response : the response for the AT Command.
*/
static int SendCmdAndWaitResponseEx(UPD_Handle handle, const char *cmd, unsigned int timeout_sec, IcAStringList & response);

static int closePort(UPD_Handle handle);
#ifdef ICERA_EXPORTS
}
#endif
/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

/* NOTE: handles should NOT be used directly. Use HDATA() instead. */
static UPD_Handle_s handles[UPD_HANDLE_LAST];

static const tArchFileProperty arch_type[] = DRV_ARCH_TYPE_TABLE_ON_PC;
static const unsigned int arch_type_max_id = ARRAY_SIZE(arch_type);

/* These commands are logged in all modes */
static const char *log_commands_all[] =
{
    AT_CMD_GMR,
    AT_CMD_IFWR
};


/* These commands are logged in loader mode */
static const char *log_commands_ldr[] =
{
    AT_CMD_IFLIST,
    AT_CMD_CHIPID
};

static const char **log_commands[COMMAND_LISTS] =
{
    log_commands_all,
    log_commands_ldr
};

static const unsigned int log_commands_max[COMMAND_LISTS] =
{
    ARRAY_SIZE(log_commands_all),
    ARRAY_SIZE(log_commands_ldr)
};

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/
static void LogTime(UPD_Handle handle)
{
    time_t t;

    time(&t);
    fprintf(HDATA(handle).log_file, "%.24s: ", ctime(&t));
}

static void OutLog(UPD_Handle handle, const char *f, va_list ap)
{
    //mutex_log is valid only when the handle is still used.
    if (!HDATA(handle).used)
    {
        return;
    }

    MUTEX_LOCK(HDATA(handle).mutex_log);
    if (HDATA(handle).log_callback)
    {
        int length = vsnprintf(HDATA(handle).log_buffer, MAX_LOGMSG_SIZE, f, ap);
        if ((length < 0) || (length >= MAX_LOGMSG_SIZE))
        {
            HDATA(handle).log_buffer[MAX_LOGMSG_SIZE - 1] = EOS;
        }
        HDATA(handle).log_callback(HDATA(handle).log_buffer);
    }
    if (HDATA(handle).log_file)
    {
        LogTime(handle);

        if (f)
        {
            /* For the debug log, skip leading newlines */
            while (*f == '\n')
            {
                f++;
            }

            vfprintf(HDATA(handle).log_file, f, ap);
        }

        fflush(HDATA(handle).log_file);

        /* TODO: Do we need to check the size of the file here too ?
         *       It is probably fair enough to assume that not too much
         *       will get added through one run, so if it is fine at the
         *       start, it will be fine to ignore it here.
         */
    }
    MUTEX_UNLOCK(HDATA(handle).mutex_log);
}

static void DebugLog(UPD_Handle handle, int level, const char *f, va_list ap)
{
    if (debug_level >= level)
    {
        int length, offset;
        char message[256];
        if (handle == DEFAULT_HANDLE)
        {
            strcpy(message, "Default: ");
        }
        else
        {
            length = snprintf(message, sizeof(message), "Hdl%d: ", (int)handle);
            if ((length < 0) || ((size_t)length >= sizeof(message)))
            {
                message[sizeof(message) - 1] = EOS;
            }
        }
        offset = strlen(message);
        length = vsnprintf(&message[offset], sizeof(message) - offset, f, ap);
        if ((length < 0) || (length >= (int)(sizeof(message) - offset)))
        {
            message[sizeof(message) - 1] = EOS;
        }
        DEBUG_LOG(message);
    }
}

/* Shared with other modules, but not public API */
extern void  OutDebug(UPD_Handle handle, const char *f, ...)
{
    va_list ap;

    va_start(ap, f);
    DebugLog(handle, 1, f, ap);
    va_end(ap);
}

extern void SetUpdaterDebugLevel(int level)
{
    debug_level = level;
}

extern void  OutError(UPD_Handle handle, const char *f, ...)
{
    va_list ap;

    if (HDATA(handle).option_verbose >= VERBOSE_STD_ERR_LEVEL)
    {
        va_start(ap, f);
        vfprintf(stderr, f, ap);
        va_end(ap);
        fflush(stderr);
    }
    va_start(ap, f);
    DebugLog(handle, 2, f, ap);
    va_end(ap);
    /* We always want the output in the debug log */
    va_start(ap, f);
    OutLog(handle, f, ap);
    va_end(ap);
}

extern void OutStandard(UPD_Handle handle, const char *f, ...)
{
    va_list ap;

    if ( (HDATA(handle).option_verbose >= VERBOSE_INFO_LEVEL) && (!HDATA(handle).log_callback) )
    {
        va_start(ap, f);
        vfprintf(stdout, f, ap);
        va_end(ap);
        fflush(stdout);
    }
    va_start(ap, f);
    DebugLog(handle, 3, f, ap);
    va_end(ap);
    /* ABE: I didn't yet find why but this code couldn't be moved above, it breaks Python callback mechanism */
    /* TODO: debug the issue... */
    /* For the moment, please don't try to optimize...*/
    /* We always want the output in the debug log */
    va_start(ap, f);
    OutLog(handle, f, ap);
    va_end(ap);
}

static void printATcmd(UPD_Handle handle, const char* cmd, IcAStringList response)
{
    IcAString str_response;
    response.GetDelimited(str_response, "\n");

    if (HDATA(handle).option_verbose > VERBOSE_SILENT_LEVEL)
    {
        response.GetDelimited(str_response, "\n");
        OutStandard(handle, "%s -> %s\n\n", cmd, str_response.c_str());
    }
    else
    {
        HDATA(handle).option_verbose = VERBOSE_INFO_LEVEL;
        response.GetDelimited(str_response, "\n");
        OutStandard(handle, "%s -> %s\n\n", cmd, str_response.c_str());
        HDATA(handle).option_verbose = VERBOSE_SILENT_LEVEL;
    }
}

static bool FileExists(char* filename)
{
    FILE* file = fopen(filename, "r");
    if (file)
    {
        fclose(file);
        return true;
    }
    return false;
}

static int FileSize(char* filename)
{
    int size = -1;
    FILE* file = fopen(filename, "r");
    if (file)
    {
        fseek(file , 0, SEEK_END);
        size = ftell(file);
        fclose(file);
    }
    return size;
}

static int ReadDebugLevel(void)
{
    int level = 3;
    if (!FileExists(const_cast<char*>("debuglevel.dbg")))
    {
        level--;
        if (!FileExists(const_cast<char*>("debuglevel.err")))
        {
            level--;
            if (!FileExists(const_cast<char*>("debuglevel.std")))
            {
                level--;
            }
        }
    }
    return level;
}

static void InitHandle(UPD_Handle handle)
{
    int idx;

    MUTEX_CREATE(HDATA(handle).mutex_log);
    HDATA(handle).option_verbose            = VERBOSE_DEFAULT_LEVEL;
    HDATA(handle).option_modechange         = MODE_DEFAULT;
    HDATA(handle).option_speed              = DEFAULT_SPEED;
    HDATA(handle).option_delay              = DEFAULT_DELAY;
    HDATA(handle).option_block_sz           = DEFAULT_BLOCK_SZ;
    HDATA(handle).option_dev_name           = NULL;
    HDATA(handle).disable_full_coredump     = 0;
    HDATA(handle).option_check_mode_restore = true;
    HDATA(handle).option_autodetection      = false;
    HDATA(handle).com_hdl                   = 0;
    HDATA(handle).com_settings.flow_control = 1;
    for (idx=0 ; idx<(int)ARRAY_SIZE(HDATA(handle).logging_done) ; idx++)
    {
        HDATA(handle).logging_done[idx] = false;
    }
    HDATA(handle).log_sys_state = 1;
    HDATA(handle).option_send_nvclean = DEFAULT_SEND_NVCLEAN;
    HDATA(handle).option_check_pkgv = DEFAULT_CHECK_PKGV;

    HDATA(handle).used = 1;
    HDATA(handle).nvCleanCount = 0;
}

static void updater_load(void)
{
    int length;
    char message[256];
    char curdir[FILENAME_MAX];

    // Initialization code
    InitHandle(DEFAULT_HANDLE);
    debug_level = ReadDebugLevel();
    message[0] = '\0';
    strncat(message, "Library version ", sizeof(message) - strlen(message) - 1);
    strncat(message, DLD_VERSION, sizeof(message) - strlen(message) - 1);
    strncat(message, " is loaded", sizeof(message) - strlen(message) - 1);
    DEBUG_LOG(message);
    if (getcwd(curdir, sizeof(curdir)))
    {
        DEBUG_LOG(curdir);
    }
    message[0] = '\0';
    length = snprintf(message, sizeof(message) - 1, "Debug level: %d", debug_level);
    message[length == -1 ? (int)sizeof(message) - 1 : length] = EOS;
    DEBUG_LOG(message);
}

static void updater_unload(void)
{
    // free all resources
    for (UPD_Handle handle = UPD_HANDLE_FIRST; handle <= UPD_HANDLE_LAST; handle++)
    {
        if (HDATA(handle).used)
        {
            closePort(handle);
            FreeHandle(handle);
        }
    }
    DEBUG_LOG("Library unloaded");
}

static IUInt32 ComputeChecksum32(void * src, int lg)
{
    IUInt32 *p = (IUInt32 *)src;
    IUInt32 chksum = 0;
    IUInt32 * end = p + lg/sizeof(IUInt32);

    while (p < end)
    {
        chksum ^= *p++;
    }

    return chksum;
}

static bool SplitFilePath(char* filepath, char** path, char** file)
{
    if (filepath)
    {
        char* sep = strrchr(filepath, PATH_SEP);
        if (file)
        {
            *file = strdup(sep ? sep + 1 : filepath);
            if (**file == EOS)
            {
                return false;
            }
        }
        if (path)
        {
            if (sep && (sep > filepath))
            {
                *sep = EOS;
                *path = strdup(filepath);
                *sep = PATH_SEP;
            }
            else
            {
                *path = strdup(".");
            }
        }
        return true;
    }
    return false;
}

static char* JoinFilePath(char* path, char* file)
{
    int length = strlen(path) + sizeof(PATH_SEP) + strlen(file) + 1;
    char* filepath = (char *)malloc(length);
    if (filepath)
    {
        int size = snprintf(filepath, length, "%s%c%s", path, PATH_SEP, file);
        if ((size < 0) || (size >= length))
        {
            free(filepath);
            filepath = NULL;
        }
    }
    return filepath;
}


static int GetArchTableEntry(int arch_id)
{
    unsigned int i;
    int err = -1;

    for(i=0; i< arch_type_max_id; i++)
    {
        if(arch_type[i].arch_id == arch_id)
        {
            return i;
        }
    }
    return err;
}

#ifdef __BIG_ENDIAN__
static  unsigned long endian_swap(unsigned long x)
{
    return (x>>24) |
           ((x<<8) & 0x00FF0000) |
           ((x>>8) & 0x0000FF00) |
           (x<<24);
}

static  unsigned short endian_swap_short(unsigned short x)
{
    return (x>>8) |
           (x<<8);
}

static void convert_endian(void *buffer, int bytes)
{
    unsigned long *long_ptr = (unsigned long *)buffer;

    while ((void *)long_ptr < (void *)((unsigned char *)buffer + bytes))
    {
        *long_ptr = endian_swap(*long_ptr);
        long_ptr++;
    }
}
#endif

/* Note: This function returns the integers in host byte order so the data is usable (it does not change the rfu field) */
static int GetWrappedHeader(UPD_Handle handle, tAppliFileHeader* arch_header, char* file, const char* step)
{
    int arch_entry;
    int arch_file_id;
    int header_sz = 0;
    int size = FileSize(file);

    OutDebug(handle, "%sheader: %s", step ? step : "", file);
    if (size > 0)
    {
        FILE* arch_desc = fopen(file, "rb");
        if (arch_desc)
        {
            do
            {
                memset(arch_header, 0, sizeof(*arch_header));
                OutDebug(handle, "File size: %d", size);
                /* Read Tag and Length */
                if (size < (int)(sizeof(arch_header->tag) + sizeof(arch_header->length)))
                {
                    OutError(handle, "\n#Error: incorrect archive format (size=%d) [%s]\n\n", size, file);
                    break;
                }
                if (fread(arch_header, sizeof(arch_header->tag) + sizeof(arch_header->length), 1, arch_desc) != 1)
                {
                    OutError(handle, "\n#Error: read header error %d\n\n", ferror(arch_desc));
                    header_sz = 0;
                    break;
                }
                #ifdef __BIG_ENDIAN__
                convert_endian(arch_header, sizeof(arch_header->tag) + sizeof(arch_header->length));
                #endif

                /* Check file format */
                OutDebug(handle, "Header size: %d", arch_header->length);
                if ((arch_header->length <= (sizeof(arch_header->tag) + sizeof(arch_header->length))) ||
                    (size < (int)arch_header->length))
                {
                    OutError(handle, "\n#Error: incorrect archive format [%s]\n\n", file);
                    break;
                }
                OutDebug(handle, "Header tag: %08X", arch_header->tag);

                if  ((arch_header->tag != ARCH_TAG_9140)
                     && (arch_header->tag != ARCH_TAG_9040))
                {
                    OutError(handle, "\n#Error: incorrect archive tag %08X [%s] (not a wrapped file?)\n\n", arch_header->tag, file);
                    break;
                }

                /* Read Value field */
                if (fread(&arch_header->file_size, arch_header->length - sizeof(arch_header->tag) - sizeof(arch_header->length), 1, arch_desc) != 1)
                {
                    OutError(handle, "\n#Error: read header error %d\n\n", ferror(arch_desc));
                    header_sz = 0;
                    break;
                }
                #ifdef __BIG_ENDIAN__
                convert_endian(&arch_header->file_size, arch_header->length - sizeof(arch_header->tag) - sizeof(arch_header->length));
                #endif

                /* Check filesize field */
                if (size != (int)(arch_header->file_size + arch_header->length))
                {
                    OutError(handle, "\n#Error: Header has incorrect file size %d instead of %d [%s]\n\n", arch_header->file_size, size - arch_header->length, file);
                    break;
                }

                /* Get file ID */
                arch_file_id = GET_ARCH_ID(arch_header->file_id);
                arch_entry = GetArchTableEntry(arch_file_id);
                if (step)
                {
                    if(arch_entry >= 0)
                    {
                        OutDebug(handle, "%s: Size %d", arch_type[arch_entry].acr,
                                 arch_header->file_size / 1024);
                        OutStandard(handle, "\n%s %s header [%u KB]...\n", step,
                                    arch_type[arch_entry].acr,
                                    arch_header->file_size / 1024);
                    }
                    else
                    {
                        OutDebug(handle, "Arch ID %d: Size %d", arch_file_id,
                                 arch_header->file_size / 1024);
                        OutStandard(handle, "\n%s header ID=%u [%lu KB]...\n", step,
                                    arch_file_id,
                                    arch_header->file_size / 1024);
                    }
                }
                /* Check archive header */
                header_sz = arch_header->length;
                if ( ((arch_header->tag != ARCH_TAG_9140)
                      && (arch_header->tag != ARCH_TAG_9040))
                    || (ComputeChecksum32(arch_header, arch_header->length) != 0) )
                {
                    OutError(handle, "\n#Error: incorrect archive file tag=%08X cks=%08X [%s]\n\n", arch_header->tag,
                             ComputeChecksum32(arch_header, header_sz), file);
                    header_sz = 0;
                    break;
                }

                #ifdef __BIG_ENDIAN__
                /* Need to put this back as it was read from the wire technically, if somebody wanted to interpret it....it's not 32 bit integers
                 * - at the moment it is PER encoded ASN.1 data
                 */
                convert_endian(&arch_header->rfu, arch_header->length - ARCH_HEADER_BYTE_LEN);
                #endif
            }
            while(0);
            fclose(arch_desc);
        }
    }
    OutDebug(handle, "Header size: %d", header_sz);
    return header_sz;
}

static int FirmwareDownload(UPD_Handle handle, tAppliFileHeader* arch_header, char* file)
{
    time_t time_start, time_current;
    IUInt32 length;
    unsigned int        n;
    unsigned int        index;
    unsigned int        file_sz;
    unsigned short      chksum16;
    int                 error_cnt;
    int                 progress;
    int                 total_sz;
    int                 ratio_sz;
    char                log_file_name[sizeof("log9999.txt")];
    int                 debug_block_nb  = 0;
    FILE                *log_desc       = NULL;
    int                 logging_on      = 1;
    IcAStringList response;
    IcAString str_response;

    /* Open firmware archive file */
    FILE *arch_desc = fopen(file, "rb");
    OutStandard(handle, "\nOpening [%s] file ... ", file);
    if (arch_desc)
    {
        time(&time_start);
        OutStandard(handle,"Ok\n\n");
        /* Request a firmware download: This command should be sent just before to send the 1rst block */
        HDATA(handle).com_hdl->SendAtCommand(AT_CMD_LOAD,response);
        if (! HDATA(handle).com_hdl->IsAtResponseOk(response))
        {
            OutError(handle, "\n#Error: %s command failed\n\n", AT_CMD_LOAD);
            fclose(arch_desc);
            return 0;
        }
        printATcmd(handle, AT_CMD_LOAD, response);

        /* Even value */
        HDATA(handle).option_block_sz >>= 1;
        HDATA(handle).option_block_sz <<= 1;

        /* Send StartDownload request */
        fseek (arch_desc , arch_header->length, SEEK_SET);
        error_cnt = 0;
        do
        {
            n = 0;

            HDATA(handle).tx_buf[n++] = 0xAA;
            HDATA(handle).tx_buf[n++] = 0x73;

            memcpy(&HDATA(handle).tx_buf[n], &HDATA(handle).option_block_sz, sizeof(HDATA(handle).option_block_sz));
            #ifdef __BIG_ENDIAN__
            /* Swap to little endian on the wire */
            *(unsigned short *)&HDATA(handle).tx_buf[n] = endian_swap_short(*(unsigned short *)&HDATA(handle).tx_buf[n]);
            #endif
            n += sizeof(HDATA(handle).option_block_sz);
            memcpy(&HDATA(handle).tx_buf[n], arch_header, arch_header->length);
            #ifdef __BIG_ENDIAN__
            /* Convert back to little endian the numbers, the rfu (ext header) field has already been done */
            convert_endian(&HDATA(handle).tx_buf[n], ARCH_HEADER_BYTE_LEN);
            #endif
            n += arch_header->length;

            chksum16 = ComputeChecksum16(HDATA(handle).tx_buf, n);
            memcpy(&HDATA(handle).tx_buf[n], &chksum16, sizeof(chksum16));
            n += sizeof(chksum16);
            if (!HDATA(handle).com_hdl->Write(HDATA(handle).tx_buf, n))
            {
                OutError(handle,"\n#Error: Get wrapped header COM_write %d failed [%s]\n\n", n, strerror(errno));
                fclose(arch_desc);
                return 0;
            }



            memset(HDATA(handle).rx_buf, 0, sizeof(HDATA(handle).rx_buf));
            n = 0;
            do
            {
                if (HDATA(handle).com_hdl->Read(HDATA(handle).rx_buf, 2-n, length) == false)
                {
                    OutError(handle,"\n#Error: Get wrapped header COM_read %d failed [%s]\n\n", 2 - n, strerror(errno));
                    fclose(arch_desc);
                    return 0;
                }
                n += length;
            }
            while (n < 2);

            if ((HDATA(handle).rx_buf[0] != 0xAA) || (HDATA(handle).rx_buf[1] != 0x01))
            {
                error_cnt++;
            }

            if (error_cnt == MAX_BLOCK_REJECT)
            {
                OutError(handle,"\n#Error: block rejected [0x%.2X%.2X]\n\n", HDATA(handle).rx_buf[0], HDATA(handle).rx_buf[1]);
                fclose(arch_desc);
                return 0;
            }
        }
        while ((HDATA(handle).rx_buf[0] != 0xAA) || (HDATA(handle).rx_buf[1] != 0x01));
        /* Send Blocks ... */
        file_sz = arch_header->file_size;
        ratio_sz = 1;
        while ((file_sz >> ratio_sz) > MAX_PERCENT_FILE_SIZE) ratio_sz++;
        total_sz = file_sz >> ratio_sz;
        HDATA(handle).progress.current.base = HDATA(handle).progress.percent;
        while (file_sz > 0)
        {
            int read_sz;
            int i;

            /* send block */
            error_cnt = 0;
            debug_block_nb++;
            do
            {
                index = 0;
                read_sz = 0;
                if (error_cnt == 0)
                {
                    /* progress status */
                    progress = ((total_sz - (file_sz >> ratio_sz)) * 100) / total_sz;
                    OutStandard(handle, "%2d%%\r", progress);
                    HDATA(handle).progress.percent = HDATA(handle).progress.current.base + (progress * HDATA(handle).progress.current.weight);
                    HDATA(handle).tx_buf[index++] = 0xAA;
                    HDATA(handle).tx_buf[index++] = 0x00;

                    read_sz = (int)fread(&HDATA(handle).tx_buf[index], sizeof(unsigned char), HDATA(handle).option_block_sz, arch_desc);
                    index += (unsigned int)read_sz;

                    /* One byte of padding (0x00) appended to the data to transmit */
                    /* For 16bits alignment */
                    /* Note: same modification done on platform side when receiving */
                    if ((index % 2) != 0)
                    {
                        index +=1;
                    }

                    chksum16 = ComputeChecksum16(HDATA(handle).tx_buf, index);
                    memcpy(&HDATA(handle).tx_buf[index], &chksum16, sizeof(chksum16));
                    index += sizeof(chksum16);
                }

               
                if (!HDATA(handle).com_hdl->Write(HDATA(handle).tx_buf, index))
                {
                   OutError(handle,"\n#Error: Get wrapped block COM_write %d failed [%s]\n\n", index, strerror(errno));
                   fclose(arch_desc);
                   return 0;
                }
                

                n = 0;
                memset(HDATA(handle).rx_buf, 0, sizeof(HDATA(handle).rx_buf));
                do
                {
                    if (HDATA(handle).com_hdl->Read(HDATA(handle).rx_buf, 2-n, length) == false)
                    {
                        OutError(handle,"\n#Error: Get wrapped block COM_read %d failed [%s]\n\n", 2 - n, strerror(errno));
                        fclose(arch_desc);
                        return 0;
                    }
                    n += length;
                }
                while (n < 2);

                if ((HDATA(handle).rx_buf[0] != 0xAA) || (HDATA(handle).rx_buf[1] != 0x01))
                {
                    int line_nb = 0;
                    int go;

                    /* Open log-file */
                    if (!log_desc && logging_on)
                    {
                        /* Unique-ish file names per handle */
                        int size = snprintf(log_file_name, sizeof(log_file_name), "log%lu.txt", handle);
                        if ((size < 0) || ((size_t)size >= sizeof(log_file_name)))
                        {
                            log_file_name[sizeof(log_file_name) - 1] = EOS;
                        }
                        OutStandard(handle,"Opening [%s] file ... ", log_file_name);
                        log_desc = fopen(log_file_name, "w");
                        if (log_desc == NULL)
                        {
                           OutError(handle,"warning: failed to open [%s] file, errno=%s\n", log_file_name, strerror(errno));
                            logging_on = 0;
                        }
                        OutStandard(handle, "Ok\n");
                    }

                    if (log_desc)
                    {
                        fprintf(log_desc, "BLOCK %d REJECTED [TRY NB %d - STATUS= 0x%.2X%.2X]\n",
                                debug_block_nb, error_cnt, HDATA(handle).rx_buf[0], HDATA(handle).rx_buf[1]);
                    }

                    error_cnt++;

                    /* Bad block is echoed on UART. Get it */
                    memset(HDATA(handle).rx_buf, 0, sizeof(HDATA(handle).rx_buf));
                    IUInt32 length;
                    if (HDATA(handle).com_hdl->Read(HDATA(handle).rx_buf, 0x104, length) == false)
                    {
                        OutError(handle,"\n#Error: Bad block COM_read %d failed [%s]\n\n", 0x104, strerror(errno));
                        fclose(arch_desc);
                        return 0;
                    }

                    /* Dump transmitted and echo blocks */
                    go = log_desc ? 1 : 0;
                    while (go)
                    {
                        for (i = 0; i < 16; i++)
                        {
                            if ((16*line_nb + i) == (int)index)
                            {
                                fprintf(log_desc, "\t\t\t\t\t\t\t\t\t");
                                break;
                            }

                            if (HDATA(handle).tx_buf[16*line_nb + i] != HDATA(handle).rx_buf[16*line_nb + i])
                            {
                                fprintf(log_desc, "%02X+", HDATA(handle).tx_buf[16*line_nb +i]);
                            }
                            else
                            {
                                fprintf(log_desc, "%.2X ", HDATA(handle).tx_buf[16*line_nb + i]);
                            }
                        }
                        fprintf(log_desc, "\t");
                        for (i = 0; i < 16; i++)
                        {
                            if ((16*line_nb +i) == (int)index)
                            {
                                fprintf(log_desc, "\n");
                                go = 0;
                                break;
                            }

                            if (HDATA(handle).tx_buf[16*line_nb + i] != HDATA(handle).rx_buf[16*line_nb + i])
                            {
                                fprintf(log_desc, "%02X+", HDATA(handle).rx_buf[16*line_nb + i]);
                            }
                            else
                            {
                                fprintf(log_desc, "%.2X ", HDATA(handle).rx_buf[16*line_nb + i]);
                            }
                        }

                        fprintf(log_desc, "\n");
                        line_nb++;
                    }

                    if (log_desc)
                    {
                        fprintf(log_desc, "\n");
                        fflush(log_desc);
                    }
                }

                if (error_cnt == MAX_BLOCK_REJECT)
                {
                    OutError(handle, "\n#Error: block rejected %d times. See log.txt.\n\n", error_cnt);
                    if (log_desc)
                    {
                        fclose(log_desc);
                    }
                    fclose(arch_desc);
                    return 0;
                }
            }
            while ((HDATA(handle).rx_buf[0] != 0xAA) || (HDATA(handle).rx_buf[1] != 0x01));
            file_sz -= read_sz;
        }
        HDATA(handle).progress.percent = HDATA(handle).progress.current.base + (100 * HDATA(handle).progress.current.weight);

        fclose(arch_desc);
        time(&time_current);
        OutStandard(handle, "100%%\nDone...[%d seconds]\n\n", time_current - time_start);
        return 1;
    }
    return 0;
}

static bool FirmwareFlash(UPD_Handle handle)
{
    time_t time_start, time_current;
    IcAStringList response,temp;
    IcAString str_response;
    bool received;
    char at_cmd[50];

    HDATA(handle).progress.current.base = HDATA(handle).progress.percent;
    OutStandard(handle, "\n\nPrograming flash...\n");
    /* Programing flash takes a while, so update AT comand timeout ... */
    HDATA(handle).com_hdl->SetReadTimeout(300);
    /* Special OutStandard call back to display progress */
    time(&time_start);
    /* With progress */
    snprintf(at_cmd, sizeof(at_cmd), AT_CMD_PROG, 2);
    OutStandard(handle, "%s ->\n\n", at_cmd );
    HDATA(handle).com_hdl->SendAtCommand(at_cmd);
    time(&time_start);
    do{
        temp.Clear();
        received = HDATA(handle).com_hdl->GetResponse(temp);
        if (received)
        {
            temp.GetDelimited(str_response, "\n");
            OutStandard(handle, "%s \n\n", str_response.c_str());
            response.Add(temp);
            received = temp.Contains("OK") || temp.Contains("ERROR");
        }

        time(&time_current);
    }while (!received && (time_current - time_start < 30) );

    if (! HDATA(handle).com_hdl->IsAtResponseOk(response))
    {
        /* Try without progress if not supported */
        snprintf(at_cmd, sizeof(at_cmd), AT_CMD_PROG, 1);
        HDATA(handle).com_hdl->SendAtCommand(at_cmd);
        OutStandard(handle, "%s ->\n\n", at_cmd);
        time(&time_start);
        do{
            temp.Clear();
            received = HDATA(handle).com_hdl->GetResponse(temp);
            if (received)
            {
                temp.GetDelimited(str_response, "\n");
                OutStandard(handle, "%s \n\n", str_response.c_str());
                response.Add(temp);
                received = temp.Contains("OK") || temp.Contains("ERROR");
            }

            time(&time_current);
        } while (!received && (time_current - time_start < 30));
        if (! HDATA(handle).com_hdl->IsAtResponseOk(response))
        {
            return false;
        }
    }
    time(&time_current);
    HDATA(handle).com_hdl->SetReadTimeout(5);
    /* Restore output call back */
    OutStandard(handle, "\nDone...[%d seconds]\n\n", time_current - time_start);

    HDATA(handle).progress.percent = HDATA(handle).progress.current.base + (100 * HDATA(handle).progress.current.weight);
    return true;
}

static char *parse_pkgv_line(char *buf, int len, FILE *f)
{
    char buffer[80];

    char *data = fgets(buffer, sizeof(buffer), f);

    if (data)
    {
        int skip = 0;
        int length = 0;

        /* Look for end of line */
        char *end_of_line = strchr(buffer, '\n');

        /* If there was no \n read, skip to the \n or end of file/error */
        if (!end_of_line)
        {
            while (!feof(f) && !ferror(f))
            {
                if ('\n' == fgetc(f))
                {
                    break;
                }
            }
        }

        skip = strspn(buffer, " \t\r\n");
        length = strcspn(buffer + skip, " \t\r\n");
        length = min(len - 1, length);
        memcpy(buf, buffer + skip, length);
        buf[length + 1] = '\0';

        data = &buf[0];
    }
    return data;
}

static int UpdatePackageVersion(UPD_Handle handle, char *file)
{
    /* Read parameters from file, then write it with AT%IPKGV= */
    char package_version[PKGV_LEN_VERSION + 1] = {0};
    char package_date[PKGV_LEN_DATE + 1] = {0};
    char package_svn[PKGV_LEN_SVN + 1] = {0};
    char package_fcd[PKGV_LEN_FCD + 1] = {0};
    IcAStringList response;
    int status = 1;
    char at_cmd[50];

    FILE *package_desc = fopen(file, "rb");
    OutStandard(handle, "\nOpening [%s] file ... ", file);
    if (package_desc)
    {
        parse_pkgv_line(package_version, sizeof(package_version), package_desc);
        parse_pkgv_line(package_date, sizeof(package_date), package_desc);
        parse_pkgv_line(package_svn, sizeof(package_svn), package_desc);
        parse_pkgv_line(package_fcd, sizeof(package_fcd), package_desc);

        snprintf(at_cmd, sizeof(at_cmd), AT_CMD_IPKGV,
                            package_version,
                            strlen(package_date)?",":"", package_date,
                            strlen(package_svn)?",":"", package_svn,
                            strlen(package_fcd)?",":"", package_fcd);
        if (! HDATA(handle).com_hdl->SendAtCommand(at_cmd))
        {
            OutError(handle, "\n#Error: Could not send IPKGV command\n\n");
        }
        else
        {
            HDATA(handle).com_hdl->GetResponse(response);
            printATcmd(handle, at_cmd, response);
            status = 1;
        }
        fclose(package_desc);
        OutStandard(handle, "\nFile [%s] closed", file);
    }
    return status;
}

static int closePort(UPD_Handle handle)
{
    if(HDATA(handle).com_hdl)
    {
        HDATA(handle).com_hdl->Close();
        HDATA(handle).com_hdl = 0;
        OutDebug(handle, "Device closed, handle %d\n", HDATA(handle).com_hdl);
#ifdef _WIN32
        if (m_closeNeeded == true)
        {
            CoUninitialize();
        }
#endif
    }
    return 1;
}


static int openPort(UPD_Handle handle, const char* dev_name)
{
    int result = 0; /* Failure */
    if (!HDATA(handle).com_hdl)
    {        
#ifdef _WIN32
        // COM class 
        HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);
        if (FAILED(hr) && hr != RPC_E_CHANGED_MODE)
        {
            // failure
            IcLogError(IcT("Failed to initialise COM (%d)."), hr);
        }
        else if (hr == RPC_E_CHANGED_MODE)
        {
            // Someone else will close
            m_closeNeeded = false;
        }
        const  IcDeviceInfo * currentDev = NULL;
        const  IcInterfaceInfo * atPort = NULL;
        static IcAtPortMbim   mbimPort;
        static IcAtPortWinusb winUSBPort;
        static IcDeviceDetect devDetect;
#endif
        static IcAtPortSocket socketPort;
        static IcAtPortSerial serialPort;

        /* Look for 1st field in dev_name, taking ":" as delimiter
        If socket open required, then dev name should be formatted as follow:
        tcp:<port_num>:<ip_addr>

         2nd field of deb_name always considered as a port number.
         3rd field of dev_name always considered as an IP addr.
         If no <ip_addr>, 127.0.0.1 taken as default
         If no <port_num>, 32768 taken as default

         Ex:
         if dev_name = "tcp:" : socket opened on 127.0.0.1:32768
         if dev_name = "tcp:3456" : socket opened on 127.0.0.1:3456
         if dev_name = "tcp:3456:192.168.48.2" : socket opened on 192.168.48.2:3456 
        */

        char *dev=NULL;
        char *sock;
        dev = strdup(dev_name);
        sock = strtok(dev, ":");
        if(memcmp(sock, "tcp", strlen("tcp")) == 0)
        {
            char *addr = NULL;
            int port = 0;
            HDATA(handle).com_hdl = &socketPort;
            socketPort.Close();
            sock = strtok(NULL, ":");
            if(sock)
            {
                /* 2nd sock field is port */
                port = atoi(sock);                        
            }
            port = port ? port:32768; /* default to 32768 */
            port = port > 65535 ? 32768:port; /* max port number is 65535 */

            sock = strtok(NULL, ":");
            if(sock)
            {
                /* 3rd sock field is addr */
                addr = (char *)malloc(strlen(sock));
                strcpy(addr, sock);
            }

            addr ? socketPort.Configure(port,addr):socketPort.Configure(port);
            if (socketPort.Open())
                result = 1;

            if(addr)
            {
                free(addr);
            }
        }
#ifdef _WIN32
#ifndef IC_NO_MBIM
        else if (strstr(strupr(dev), "MBIM"))
        {
            //char *interfaceId = strtok(NULL, ":");
            HDATA(handle).com_hdl = &mbimPort;

            devDetect.Refresh();
            atPort = devDetect.FindFirst(IC_IT_MBIM, IC_IF_AT);
            if (atPort != NULL){
                mbimPort.Close();
                mbimPort.Configure(atPort->m_serialName.c_str(), atPort->m_serialDev.c_str()); 
                Sleep(1000);
                if (mbimPort.Open()){
                    result = 1;
                    SetBlockSize(handle, DEFAULT_MBIM_BLOCK_SZ);
                }
            }
        }
#endif //IC_NO_MBIM
#ifndef IC_NO_WINUSB
        else if (strstr(strupr(dev), "WINUSB"))
        {
            HDATA(handle).com_hdl = &winUSBPort;
            devDetect.Refresh();
            atPort = devDetect.FindFirst(IC_IT_WINUSB, IC_IF_AT);
            if (atPort != NULL){
                winUSBPort.Close();
                winUSBPort.Configure(atPort->m_serialName.c_str());    
                Sleep(1000);
                if (winUSBPort.Open())
                    result = 1;
            }
        }
#endif //IC_NO_WINUSB
#else  //if !(_Win32)
        else if(memcmp(sock, "raw", strlen("raw")) == 0)
        {
            char *ifName = NULL;
            HDATA(handle).com_hdl = &socketPort;
            socketPort.Close();

            sock = strtok(NULL, ":");
            if(sock)
            {
                /* 2nd sock field is ifName */
                ifName = (char *)malloc(strlen(sock));
                strcpy(ifName, sock);

                socketPort.Configure(ifName);
                if (socketPort.Open())
                {
                    result = 1;
                    SetBlockSize(handle, DEFAULT_RAW_IF_BLOCK_SZ);
                }
                if(ifName)
                {
                    free(ifName);
                }
            }
        }
#endif // _WIN32
        else
        {
            HDATA(handle).com_hdl = &serialPort;
            serialPort.Close();
            serialPort.Configure(dev_name);
            if (serialPort.Open())
                result = 1;
        }

        if(dev)
        {
            free(dev);
        }
        //HDATA(handle).com_hdl = hdl;        
    }

        return result;
}

static int GetCurrentMode(UPD_Handle handle)
{
    size_t start;
    const char *find;
    IcAStringList response;
    if (HDATA(handle).com_hdl->SendAtCommand(AT_CMD_MODE,response))
    {
        printATcmd(handle, AT_CMD_MODE, response);
        start = response.Find(AT_RESPONSE,false);
        
        if (start != IcString::npos){
            const char* str=response.Get(start)->c_str();
            find = strstr(str,AT_RESPONSE);
            if (find != NULL)
                return atoi(&find[strlen(AT_RESPONSE)]);
        }
    }
    return MODE_INVALID;
}

static bool LogSystemState(UPD_Handle handle)
{
    unsigned int i = 0;
    int current_mode = 0;
    IcAStringList response;


    if (HDATA(handle).com_hdl)
    {
        if(HDATA(handle).log_sys_state)
        {
            current_mode = GetCurrentMode(handle);
            OutStandard(handle, "\n\nGetCurrentMode current_mode: %d \n\n",current_mode);
            if (current_mode == MODE_INVALID)
            {
                return false;
            }
            if (current_mode < (int)ARRAY_SIZE(HDATA(handle).logging_done))
            {
                if (HDATA(handle).logging_done[current_mode] == false)
                {
                    /* For both modem or loader mode */
                    for (i = 0; i < log_commands_max[0]; i++)
                    {
                        HDATA(handle).com_hdl->SendAtCommand(log_commands[0][i],response);
                        printATcmd(handle, log_commands[0][i], response);
                    }
                    /* Depend on current mode */
                    if ( current_mode == 1 ){
                        for (i = 0; i < log_commands_max[current_mode]; i++)
                        {
                            HDATA(handle).com_hdl->SendAtCommand(log_commands[current_mode][i], response);
                            printATcmd(handle, log_commands[current_mode][i], response);
                        }
                        HDATA(handle).logging_done[current_mode] = true;
                    }
                }
            }
        }
    }
    return true;
}

static int RestoreSettings(UPD_Handle handle)
{
    int error = ErrorCode_Success;
    IcAStringList response;



    if (HDATA(handle).disable_full_coredump)
    {
        if (!HDATA(handle).com_hdl->SendAtCommand(AT_CMD_IFULLCOREDMP, response))
        {
            printATcmd(handle, AT_CMD_IFULLCOREDMP, response);
            // retry again
            HDATA(handle).com_hdl->SendAtCommand(AT_CMD_IFULLCOREDMP, response);
            printATcmd(handle, AT_CMD_IFULLCOREDMP, response);
        }
    }

    error = SwitchModeEx(handle, HDATA(handle).option_modechange, HDATA(handle).option_check_mode_restore);

    /* Bgz53996 or bgz051430: In any cases we leave the CM to detect the device even if port resource has been changed */
    if ((ErrorCode_ConnectionError == error) || (ErrorCode_Error == error))
    {
        return ErrorCode_Success;
    }
    return error;
}

static void DisableEcho(UPD_Handle handle)
{
    IcAStringList response;
    /* Set echo OFF */
    HDATA(handle).com_hdl->SendAtCommand(AT_CMD_ECHO_OFF, response);
    printATcmd(handle, AT_CMD_ECHO_OFF, response);

}

static int PrepareLoader(UPD_Handle handle)
{
    int error = ErrorCode_Success;
    DisableEcho(handle);
    unsigned int current_mode = GetCurrentMode(handle);
    if (current_mode != MODE_LOADER)
    {
        /* Won't actually switch if we're already in MODE_LOADER */
        error = SwitchModeEx(handle, MODE_LOADER, HDATA(handle).option_check_mode_restore);
        if (error != ErrorCode_Success)
            return error;
    }


    /* Set echo OFF (in case we have really change the `mode`) */
    DisableEcho(handle);

    return error;
}

static void DoNvclean(UPD_Handle handle, char *file)
{
    IcAStringList response;
    if (HDATA(handle).option_send_nvclean)
    {
        tAppliFileHeader    arch_header;

        /* If we're updating a modem (ARCH_ID_APP), productConfig (ARCH_ID_PRODUCTCFG) or
        deviceConfig(ARCH_ID_DEVICECFG), we need to send AT%NVCLEAN */
        if (GetWrappedHeader(handle, &arch_header, file, NULL) > 0)
        {
            if ((ARCH_ID_APP == GET_ARCH_ID(arch_header.file_id)) 
                || (ARCH_ID_PRODUCTCFG == GET_ARCH_ID(arch_header.file_id))
                || (ARCH_ID_DEVICECFG == GET_ARCH_ID(arch_header.file_id)))
            {
                HDATA(handle).com_hdl->SendAtCommand(AT_CMD_NVCLEAN, response);
                printATcmd(handle, AT_CMD_NVCLEAN, response);

                HDATA(handle).nvCleanCount++;
            }
        }
    }
}

static bool PublicChipId(UPD_Handle handle)
{
    IcAStringList response;
    /* Request PCID */
    HDATA(handle).com_hdl->SendAtCommand(AT_CMD_CHIPID,response);
    if (! HDATA(handle).com_hdl->IsAtResponseOk(response))
    {
        return false;
    }

    printATcmd(handle, AT_CMD_CHIPID, response);

    return true;
}

static bool SendIbackup(UPD_Handle handle)
{
    bool result = true;
    IcAStringList response;

    HDATA(handle).com_hdl->SetReadTimeout(60);
    HDATA(handle).com_hdl->SendAtCommand(AT_CMD_IBACKUP,response);
    result = HDATA(handle).com_hdl->IsAtResponseOk(response);

    printATcmd(handle, AT_CMD_IBACKUP, response);
    HDATA(handle).com_hdl->SetReadTimeout(5);

    return result;
}

static bool SendIrestore(UPD_Handle handle)
{
    bool result = true;
    IcAStringList response;

    HDATA(handle).com_hdl->SetReadTimeout(60);
    HDATA(handle).com_hdl->SendAtCommand(AT_CMD_IRESTORE);
    HDATA(handle).com_hdl->GetResponse(response);
    printATcmd(handle, AT_CMD_IRESTORE, response);

    result = HDATA(handle).com_hdl->IsAtResponseOk(response);

    HDATA(handle).com_hdl->SetReadTimeout(5);

    return result;
}

static int GetMode(char* line)
{
    int offset = 0;
    if ((strlen(line) == strlen("modeX")) && !strncmp(&line[offset], "mode", strlen("mode")))
    {
        offset += strlen("mode");
        if (strspn(&line[offset], DIGIT_SET) == 1)
        {
            return (int)(MODE_MODEM + line[offset] - '0');
        }
    }
    return MODE_INVALID;
}

static int GetWait(char* line)
{
    int offset = 0;
    if ((strlen(line) <= strlen("waitXXX")) && !strncmp(&line[offset], "wait", strlen("wait")))
    {
        offset += strlen("wait");
        if (strspn(&line[offset], DIGIT_SET) > 0)
        {
            return atoi(&line[offset]);
        }
    }
    return 0;
}

static bool IsIbackup(char* line)
{
    return !strncmp(line, "ibackup", sizeof("ibackup") - 1);
}

static bool IsIrestore(char* line)
{
    return !strncmp(line, "irestore", sizeof("irestore") - 1);
}

static char* OverrideByMethodFile(UPD_Handle handle, char *filelist)
{
    int size;
    tAppliFileHeader arch_header;
    char* filepath;
    char* files = NULL;
    char* path = NULL;
    char* filesdup = strdup(filelist);
    if (filesdup)
    {
        char* tmpfilename = NULL;
        size = strlen(filelist);
        filepath = strtok(filesdup, FILE_SEPARATOR);
        if (filepath)
        {
            if (SplitFilePath(filepath, &path, NULL))
            {
                tmpfilename = JoinFilePath(path, const_cast<char *>("update.mtd"));
                if (tmpfilename)
                {
                    OutDebug(handle, "Method file: %s", tmpfilename);
                    size = FileSize(tmpfilename);
                    if (size > 0)
                    {
                        FILE* file = fopen(tmpfilename, "rb");
                        if (file)
                        {
                            char* content = (char *)malloc(size + 1);
                            if (content)
                            {
                                int length = fread(content, 1, size, file);
                                content[size] = 0;
                                if (length == size)
                                {
                                    int count = 0;
                                    char* backup = strdup(content);
                                    if (backup)
                                    {
                                        char* line = content;
                                        OutDebug(handle, "Content: %s", backup);
                                        while (line && (line < (content + size)))
                                        {
                                            line = strtok(line, "\x0D\x0A");
                                            if (strlen(line) > 0)
                                            {
                                                OutDebug(handle, "Command: %s", line);
                                                if ((GetWait(line) <= 0) && (GetMode(line) == MODE_INVALID) && (!IsIbackup(line)) && (!IsIrestore(line)))
                                                {
                                                    free(tmpfilename);
                                                    tmpfilename = JoinFilePath(path, line);
                                                    if (!tmpfilename)
                                                    {
                                                        OutDebug(handle, "JoinFilePath error: %s+%s", path, line);
                                                        count = 0;
                                                        break;
                                                    }
                                                    if (FileExists(tmpfilename))
                                                    {
                                                        count++;
                                                    }
                                                }
                                            }
                                            line += strlen(line) + 1;
                                        }
                                        if (count)
                                        {
                                            int listsize = size + (count * (strlen(path) + sizeof(PATH_SEP))) + strlen(FILE_SEPARATOR);
                                            files = (char *)malloc(listsize);
                                            if (files)
                                            {
                                                /* Build new file list with path */
                                                files[0] = EOS;
                                                line = backup;
                                                while (line && (line < (backup + size)))
                                                {
                                                    int offset = strlen(files);
                                                    line = strtok(line, "\x0D\x0A");
                                                    if ((GetWait(line) <= 0) && (GetMode(line) == MODE_INVALID) && (!IsIbackup(line)) && (!IsIrestore(line)))
                                                    {
                                                        length = snprintf(&files[offset], listsize - offset, "%s%c%s%s", path, PATH_SEP, line, FILE_SEPARATOR);
                                                    }
                                                    else
                                                    {
                                                        length = snprintf(&files[offset], listsize - offset, "%s%s", line, FILE_SEPARATOR);
                                                    }
                                                    if ((length < 0) || (length >= (listsize - offset)))
                                                    {
                                                        OutDebug(handle, "snprintf error %d/%d: \"%s\"", length, listsize - offset, line);
                                                        free(files);
                                                        files = NULL;
                                                        break;
                                                    }
                                                    line += strlen(line) + 1;
                                                }
                                                if (files)
                                                {
                                                    files[strlen(files) - strlen(FILE_SEPARATOR)] = EOS;
                                                    OutDebug(handle, "Override: %s", files);
                                                }
                                            }
                                        }
                                        free(backup);
                                    }
                                }
                                free(content);
                            }
                        }
                    }
                    free(tmpfilename);
                }
                else
                {
                    OutDebug(handle, "JoinFilePath error: %s+update.mtd", path);
                }
            }
            else
            {
                OutDebug(handle, "SplitFilePath error: %p, %s", path, filepath);
            }
        }
        free(filesdup);
    }
    HDATA(handle).progress.totalweight = 0;
    if (!files)
    {
        files = strdup(filelist);
        OutDebug(handle, "No override");
    }
    if (files)
    {
        filesdup = strdup(files);
        if (filesdup)
        {
            int pkgv = 0;
            size = strlen(filesdup);
            filepath = filesdup;
            while (filepath && (filepath < (filesdup + size)))
            {
                filepath = strtok(filepath, FILE_SEPARATOR);
                if ((GetWait(filepath) <= 0) && (GetMode(filepath) == MODE_INVALID) && (!IsIbackup(filepath)) && (!IsIrestore(filepath)))
                {
                    OutDebug(handle, "File: %s", filepath);
                    if (FileExists(filepath))
                    {
                        if (IS_PKGV_FILE(filepath))
                        {
                            pkgv++;
                            if (pkgv > 1)
                            {
                                OutError(handle, "\n#Error: More than one PKGV file, download aborted\n\n");
                                free(files);
                                files = NULL;
                                break;
                            }
                        }
                        else
                        {
                            if (GetWrappedHeader(handle, &arch_header, filepath, "Check ") > 0)
                            {
                                int weight = GET_FILE_WEIGHT(filepath);
                                HDATA(handle).progress.totalweight += weight;
                                OutDebug(handle, "Add %s, weight %d/%d", filepath, weight, HDATA(handle).progress.totalweight);
                            }
                        }
                    }
                }
                else
                {
                    OutDebug(handle, "GetWait: %d", GetWait(filepath));
                    OutDebug(handle, "GetMode: %d", GetMode(filepath));
                }
                filepath += strlen(filepath) + 1;
            }
            free(filesdup);
        }
        else
        {
            OutDebug(handle, "strdup error: %d", strlen(files));
            free(files);
            files = NULL;
        }
    }
    return files;
}

static int FirmwareUpdate(UPD_Handle handle, char *filelist, int pcid, int flash)
{
    int error = ErrorCode_Success;
    time_t time_start, time_current;
    tAppliFileHeader arch_header;
    IcAStringList response;
    IcAString str_response;
    char at_cmd[50];

    do
    {
        char* files;

        if (filelist != NULL)
        {
            error = PrepareLoader(handle);
            if (error != ErrorCode_Success)
                break;
        }
        if (pcid)
        {
            if (!PublicChipId(handle))
            {
                error = ErrorCode_AT;
                break;
            }
            if (filelist == NULL)
            {
                break;
            }
        }
        files = OverrideByMethodFile(handle, filelist);
        if (files)
        {
            int size = strlen(files);
            char* filepath = files;

            HDATA(handle).progress.step = flash ? ProgressStep_Flash : ProgressStep_Download;
            while (filepath && (filepath < (files + size)))
            {
                filepath = strtok(filepath, FILE_SEPARATOR);
                if (filepath)
                {
                int wait = GetWait(filepath);
                if (wait > 0)
                {
                    OutDebug(handle, "Wait: %d second", wait);
                    DelayInSecond(wait);
                }
                else
                {
                    int mode = GetMode(filepath);
                    if (mode != MODE_INVALID)
                    {
                        OutDebug(handle, "Switch to mode: %d", mode);
                        error = SwitchModeEx(handle, mode, HDATA(handle).option_check_mode_restore);
                        if (error != ErrorCode_Success)
                        {
                            OutError(handle, "SwitchMode %d failed: %d", mode, error);
                            break;
                        }
                    }
                    else if(IsIbackup(filepath))
                    {
                        if (!SendIbackup(handle))
                        {
                            error = ErrorCode_Error;
                            OutError(handle, "IBACKUP failed");
                            break;
                        }
                    }
                    else if (IsIrestore(filepath))
                    {
                        if (!SendIrestore(handle))
                        {
                            error = ErrorCode_Error;
                            OutError(handle, "IRESTORE failed");
                            break;
                        }
                    }
                    else
                    {
                        /* Assuming this comes after an actual file update */
                        if (IS_PKGV_FILE(filepath))
                        {
                            OutDebug(handle, "Pkgv: %s", filepath);
                            if (!UpdatePackageVersion(handle, filepath))
                            {
                                error = ErrorCode_AT;
                                break;
                            }
                            OutStandard(handle, "\nPackage version updated\n");
                        }
                        else
                        {                                
                            if (GetWrappedHeader(handle, &arch_header, filepath, NULL) > 0)
                            {
                                int arch_entry = GetArchTableEntry(GET_ARCH_ID(arch_header.file_id));
                                bool one_shot = (arch_entry >= 0) ? arch_type[arch_entry].write_file_during_auth : false;
                                HDATA(handle).progress.current.weight = GET_FILE_WEIGHT(filepath);
                                if (!one_shot && flash)
                                {
                                    HDATA(handle).progress.current.weight /= 2;
                                }
                                OutDebug(handle, "Download: %s, Weight: %d/%d", filepath, HDATA(handle).progress.current.weight, HDATA(handle).progress.totalweight);
                                if (!FirmwareDownload(handle, &arch_header, filepath))
                                {
                                    OutStandard(handle, "FirmwareDownload");
                                    error = ErrorCode_DownloadError;
                                    break;
                                }
                                /* Archive signature check / Firmware update */
                                if (flash)
                                {
                                    OutDebug(handle, "Flash: %s, Weight: %d/%d", filepath, HDATA(handle).progress.current.weight, HDATA(handle).progress.totalweight);
                                    if (!FirmwareFlash(handle))
                                    {
                                        error = ErrorCode_AT;
                                        break;
                                    }
                                    /* Download is successful and we've programmed the new binary -
                                     * check if we need to do NVCLEAN
                                     */
                                    if (HDATA(handle).nvCleanCount == 0){
                                        DoNvclean(handle, filepath);
                                    }
                                }
                                else
                                {
                                    OutStandard(handle, "\n");
                                    snprintf(at_cmd, sizeof(at_cmd),AT_CMD_PROG, 0);
                                    HDATA(handle).com_hdl->SendAtCommand(at_cmd);
                                    time(&time_start);
                                    do{
                                    HDATA(handle).com_hdl->GetResponse(response);
                                    response.GetDelimited(str_response,"\n");
                                    time(&time_current);
                                    }while (str_response.IsEqual("") && (time_current - time_start < 300) );
                                    OutStandard(handle, "%s -> %s\n\n", at_cmd, str_response.c_str());
                                    if (! HDATA(handle).com_hdl->IsAtResponseOk(response))
                                    {
                                        error = ErrorCode_AT;
                                        break;
                                    }

                                    OutStandard(handle, "Archive signature ... OK\n");
                                    break;
                                }
                            }
                            else
                            {
                               OutError(handle, "\nInvalid header file: [%s] is ignored\n", filepath);
                            }
                        }
                    }
                }
                    filepath += strlen(filepath) + 1;
                }
            }

            free(files);
        }
        else
        {
            OutError(handle, "\nNo file to update\n");
            error = ErrorCode_DownloadError;
            break;
        }
        HDATA(handle).progress.step = ProgressStep_Finalize;
        HDATA(handle).progress.percent = HDATA(handle).progress.totalweight * 100;
    }
    while(0);
    OutStandard(handle, "\nFirmware upgrade done: %d\n", error);
    if (error == ErrorCode_Success && filelist != NULL)
    {
        error = RestoreSettings(handle);
    }
    return error;
}


static int DelayedSwitchMode(UPD_Handle handle, char *command, int size, int mode, bool checkSuccess)
{
    int timeout,  length;
    time_t start,current;
    IcAStringList response;

    OutDebug(handle, "DelayedSwitchMode: %d", mode);
   
    length = snprintf(command, size, AT_CMD_MODEx, mode);
    if ((length < 0) || (length >= size))
    {
        command[size - 1] = EOS;
    }

    if (mode == MODE_LOADER && !HDATA(handle).option_standalone_loader)
    {
        /* There is no re-enumeration when switching from Modem to Loader */
        if (AT_ERR_SUCCESS != SendCmdAndWaitResponseEx(handle, command, HDATA(handle).option_delay, response))
        {
            closePort(handle);
            return ErrorCode_AT;
        }
    }
    else
    {
        if (mode == MODE_LOADER && HDATA(handle).option_standalone_loader){
            command = strdup(AT_CMD_MODE13);
        }
        /* The device will reset when switching back to Modem mode, so we may miss the "OK" response */
        if (!HDATA(handle).com_hdl->SendAtCommand(command))
        {
            closePort(handle);
            return ErrorCode_AT;
        }
        HDATA(handle).com_hdl->GetResponse(response);
        printATcmd(handle, command, response);
        closePort(handle);

        if (checkSuccess)
        {
            OutStandard(handle, "Waiting for device re-enumeration...\n\n");
            timeout = HDATA(handle).option_delay < 1 ? 1 : HDATA(handle).option_delay;
            time(&start);
            OutDebug(handle, "time: %d", start);
            DelayInSecond(10);
            do
            {
                if (HDATA(handle).option_autodetection){

                    DelayInSecond(1);
                    char** port_list;
                    char** port_detail_list;
                    int type_mask = DETECT_SERIAL_TYPE_MASK | DETECT_MBIM_TYPE_MASK | DETECT_WINUSB_TYPE_MASK; 
                    int func_mask = ( 
                    #if defined (__linux__)    
                                        DETECT_UNKNOWN_FUNCTION_MASK |
                    #endif                                     
                        DETECT_MODEM_FUNCTION_MASK | DETECT_AT_FUNCTION_MASK);
                    int port_count = PortDetect(type_mask|func_mask, &port_list, &port_detail_list);
                    if ( port_count != 0)
                    {
                        //Wait few seconds before re-opening the comPort
                        DelayInSecond(5);
                        if (openPort(handle, strdup(port_list[0])))
                        {
                            freePortList(port_list, port_count);
                            freePortList(port_detail_list, port_count);
                            OutDebug(handle, "success");      
                            DelayInSecond(5);
                            return ErrorCode_Success;
                        }
                    }                    
                    time(&current);
                    OutDebug(handle, "time: %d", current);

                }else{
                    DelayInSecond(1);
                    if ( openPort(handle, HDATA(handle).option_dev_name))
                    {
                        OutDebug(handle, "success");
                        DelayInSecond(5);
                        return ErrorCode_Success;
                    }
                    closePort(handle);
                    time(&current);
                    OutDebug(handle, "time: %d", current); 
                }
            }
            while(current - start < timeout);
            time(&current);
            OutDebug(handle, "failed: %d", current);
            return ErrorCode_DeviceNotFound;
        }
    }
    
    return ErrorCode_Success;

}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/* Handle functions (create, free, set parameters) */
#ifdef ICERA_EXPORTS
extern "C"{
#endif
ICERA_API UPD_Handle CreateHandle(void)
{
    UPD_Handle handle = 0;

    /* Find unused handle, set initial values. Start at 1 to allow a default handle */
    for (UPD_Handle i = UPD_HANDLE_FIRST; i <= UPD_HANDLE_LAST; i++)
    {
        if ( !HDATA(i).used)
        {
            handle = i;
            break;
        }
    }
    if (handle != 0)
    {
        InitHandle(handle);
    }
    return handle;
}

ICERA_API void FreeHandle(UPD_Handle handle)
{
    /* In any cases callback should be freed */
    if (HDATA(handle).used)
    {
        SetLogCallbackFuncEx(handle, NULL);
        if (HDATA(handle).option_dev_name)
        {
            free(HDATA(handle).option_dev_name);
            HDATA(handle).option_dev_name = NULL;
        }
        MUTEX_DESTROY(HDATA(handle).mutex_log);
        HDATA(handle).used = 0;
    }
}

ICERA_API void freePortList(char** ptr, int port_count)
{
    if (!ptr || port_count == 0)
    {
        return;
    }
    for (int i =0; i<port_count; i++)
    {
        if (ptr[i])
        {
           free(ptr[i]);
        }
    }
    free(ptr);
}

ICERA_API int  SetModeChange(UPD_Handle handle, int modechange)
{
    if ((modechange > MODE_INVALID) && (modechange < MODE_MAX))
    {
        HDATA(handle).option_modechange = modechange;
        return ErrorCode_Success;
    }

    return ErrorCode_Error;
}

ICERA_API int SetSpeed(UPD_Handle handle, int speed)
{
    if (speed > 0)
    {
        HDATA(handle).option_speed = speed;
        return ErrorCode_Success;
    }

    return ErrorCode_Error;
}

ICERA_API int SetDelay(UPD_Handle handle, int delay)
{
    if (delay > 0)
    {
        HDATA(handle).option_delay = delay;
        return ErrorCode_Success;
    }

    return ErrorCode_Error;
}

ICERA_API int SetBlockSize(UPD_Handle handle, int block_sz)
{
    if (block_sz > 0)
    {
        if (block_sz <= MIN_BLOCK_SZ)
        {
            block_sz = MIN_BLOCK_SZ + 1;
        }
        HDATA(handle).option_block_sz = (unsigned short)block_sz;
        return ErrorCode_Success;
    }

    return ErrorCode_Error;
}

ICERA_API int SetDevice(UPD_Handle handle, const char *dev_name)
{
    if (HDATA(handle).com_hdl)
    {
        closePort(handle);
        if (HDATA(handle).option_dev_name)
        {
            free(HDATA(handle).option_dev_name);
            HDATA(handle).option_dev_name = NULL;
        }
    }
    if (openPort(handle, dev_name))
    {
        HDATA(handle).option_dev_name = strdup(dev_name);
        return ErrorCode_Success;
    }
    return ErrorCode_Error;
}


/* I/O, logging */
ICERA_API void SetLogCallbackFuncEx(UPD_Handle handle, log_callback_type callback)
{
    OutDebug(handle, "SetLogCallbackFunc: %p, handle used=%d", callback, HDATA(handle).used);
    //mutex_log is valid only when the handle is still used.
    if (!HDATA(handle).used)
    {
        return;
    }

    MUTEX_LOCK(HDATA(handle).mutex_log);
    HDATA(handle).log_callback = callback;
    MUTEX_UNLOCK(HDATA(handle).mutex_log);
}

ICERA_API void UpdaterLogToFileEx(UPD_Handle handle, char *file)
{
    FILE* log_file = NULL;
    struct stat stat_info;
    char *new_file_name;

    if (file)
    {
        OutDebug(handle, "UpdaterLogToFileEx [%s]", file);
    }
    MUTEX_LOCK(HDATA(handle).mutex_log);
    if (HDATA(handle).log_file)
    {
        fclose(HDATA(handle).log_file);
        HDATA(handle).log_file = NULL;
    }
    MUTEX_UNLOCK(HDATA(handle).mutex_log);
    if (file)
    {
        /* Check that the file hasn't got too big */
        memset(&stat_info, 0, sizeof (stat_info));
        if (stat(file, &stat_info) == 0)
        {
            /* Check if file is too big */
            if (stat_info.st_size > MAX_LOGFILE_SIZE)
            {
                /* Space for old name + .old */
                new_file_name = (char *)alloca(strlen(file) + 4 + 1);

                if (new_file_name != NULL)
                {
                    strcpy(new_file_name, file);
                    strcat(new_file_name, ".old");
                    remove(new_file_name);
                    rename(file, new_file_name);
                }
            }
        }
        log_file = fopen(file, "a");
        if (log_file)
        {
            MUTEX_LOCK(HDATA(handle).mutex_log);
            HDATA(handle).log_file = log_file;
            fprintf(HDATA(handle).log_file, "\n");
            LogTime(handle);
            fprintf(HDATA(handle).log_file, "DLL version: %s\n\n", DLD_VERSION);
            fflush(HDATA(handle).log_file);
            MUTEX_UNLOCK(HDATA(handle).mutex_log);
        }
    }
}

ICERA_API void SetLogSysState(UPD_Handle handle, int state)
{
    HDATA(handle).log_sys_state = state;
}

ICERA_API void SetSendNvclean(UPD_Handle handle, int enable)
{
    HDATA(handle).option_send_nvclean = enable;
}

/* Legacy (deprecated) API */
ICERA_API void SetGlobalDisableFullCoredumpSetting(bool disable_full_coredump_required)
{
    disable_full_coredump = disable_full_coredump_required;
}

ICERA_API void SetDisableFullCoredumpSetting(UPD_Handle handle, bool disable_full_coredump_required)
{
    HDATA(handle).disable_full_coredump = disable_full_coredump_required;
}

/* Legacy (deprecated) API */
ICERA_API void SetGlobalCheckModeRestore(bool check)
{
    global_check_mode_restore = check;
}

ICERA_API void SetCheckModeRestore(UPD_Handle handle, bool check)
{
    HDATA(handle).option_check_mode_restore = check;
}

ICERA_API void SetAutodetection(UPD_Handle handle, bool check)
{
    HDATA(handle).option_autodetection = check;
}

ICERA_API void SetLoaderMode(UPD_Handle handle, bool standalone_loader)
{
    HDATA(handle).option_standalone_loader = standalone_loader;
}


static int CompareArchHashValue(UPD_Handle handle, const char* arch_type, const char* arch_hash_value, bool *is_same)
{
    int error = ErrorCode_Success;
    *is_same = false;
    IcAStringList response;
    IcAString str_response;

    do
    {
        if (!handle)
        {
            error = ErrorCode_Error;
            break;
        }
        char at_cmd[sizeof(AT_CMD_ARCHDIGEST) + 40];
        snprintf(at_cmd, sizeof(at_cmd), AT_CMD_ARCHDIGEST, arch_type);


        SendCmdAndWaitResponseEx(handle, at_cmd, 10, response);
 
        if (!HDATA(handle).com_hdl->IsAtResponseOk(response))
        {
            OutError(handle, "\n#Error: Sending AT command failed: %s\n\n", at_cmd);
            error = ErrorCode_AT;
            break;
        }

        response.GetDelimited(str_response,"\n");

        int hashStart = 0, hashEnd = 0;
        const char *start = strstr(str_response.c_str(), "IGETARCHDIGEST: ");
        if (start)
        {
            sscanf(start, "IGETARCHDIGEST: %n%*[A-Fa-f-0-9]%n", &hashStart, &hashEnd);
        }
        if (hashStart && hashEnd)
        {
            size_t hashLength = hashEnd - hashStart;
            if ( (strlen(arch_hash_value) == hashLength) && 
                 !strncmp(arch_hash_value, start + hashStart, hashLength) )
            {
                *is_same = true;
                break;           
            }
        }
    } while(0);
    
    return error;

}

ICERA_API int CompareArchHashValues(UPD_Handle handle, const char* arch_hash_values, bool *is_same)
{
    int error = ErrorCode_Success;

    do
    {
        char *hash_values = strdup(arch_hash_values);

        if (!hash_values)
        {
            error = ErrorCode_Error;
            break;
        }
        /* Disable Echo in case it's not yet done. */
        DisableEcho(handle);

        *is_same = true;
        char* arch_type = strtok(hash_values, ";");

        while (arch_type)
        {
            bool same_hash;
            char *arch_type_end = strstr(arch_type, "=");
            if (!arch_type_end)
            {
                error = ErrorCode_Error;
                break;
            }
            *arch_type_end = '\0';

            char * arch_hash = arch_type_end + 1;

            error = CompareArchHashValue(handle, arch_type, arch_hash, &same_hash);

            if (error != ErrorCode_Success)
            {
                break;
            }
            if (!same_hash)
            {
                *is_same = false;
                break;
            }
            
            arch_type = strtok(NULL, ";");
        }
        if (error != ErrorCode_Success)
        {
            *is_same = false;
        }
        free(hash_values);
    }
    while(0);
    return error;
}

ICERA_API int GetFwid(UPD_Handle handle, char *buffer, size_t buffer_size, size_t *required_size)
{
    int error = ErrorCode_Success;
    IcAStringList response;
    IcAString str_response;

    do
    {
        if (!handle || !required_size)
        {
            error = ErrorCode_Error;
            break;
        }
        SendCmdAndWaitResponseEx(handle, AT_CMD_IGETFWID, 1, response);
 
        if (!HDATA(handle).com_hdl->IsAtResponseOk(response))
        {
            OutError(handle, "\n#Error: Sending AT command failed: %s\n\n", AT_CMD_IGETFWID);
            error = ErrorCode_AT;
            break;
        }

        response.GetDelimited(str_response,"\n");

        int idStart = 0, idEnd = 0;
        size_t idLength = 0;
        const char *start = strstr(str_response.c_str(), "IGETFWID: ");
        if (start)
        {
            sscanf(start, "IGETFWID: %n%*[^\r\n]%n", &idStart, &idEnd);
        }
        if (idStart && idEnd)
        {
            idLength = idEnd - idStart;
        }
        if (idLength == 0)
        {
            OutError(handle, "\n#Error: Invalid Firmware ID Length 0 \n\n");
            error = ErrorCode_Error;
            break;
        }

        *required_size = idLength + 1 /* for '\0' */;
        if (buffer && buffer_size)
        {
            strncpy(buffer, start + idStart, min(idLength, buffer_size));
            if (buffer_size > idLength)
            {
                buffer[idLength] = '\0';
            } 
        }
    } while(0);

    return error;
}

ICERA_API int PortDetect(int filter, char*** port_list, char*** port_detail_list)
{
    // Show available ports
    IcDeviceDetect  devDetect;
    IcString        displayName;
    IcString        fullDisplayName;
    IcInterfaceTree itfTree;
    int             portCount;

    // Get interfaces
    devDetect.Refresh();
    devDetect.GetTree().Get(itfTree, filter); 
    const IcInterfaceList &  itfList = itfTree.GetFlatList();
    portCount = itfTree.GetFlatList().size();
    if (portCount == 0)
    {
        return 0;
    }

    // Allocate string arrays for port name and detailed info list
    (*port_list) = (char**)malloc(portCount * sizeof(char*));
    (*port_detail_list) = (char**)malloc(portCount * sizeof(char*));
    assert( (*port_list != NULL) && (*port_detail_list != NULL) );

    // Copy fetched strings into above arrays
    for (int ii = 0; ii < portCount; ii++)
    {
        const IcInterfaceInfo * currItf = itfList[ii];
        displayName.Clear();
        fullDisplayName.Clear();

        // Add type
        switch(currItf->m_type)
        {
        case IC_IT_SERIAL:  displayName = "Serial";   break;
        case IC_IT_OBEX:    displayName = "ObexUSB";  break;
        case IC_IT_NET:     displayName = "Net";      break;
        case IC_IT_MBIM:    displayName = "MBIM";     break;
        case IC_IT_WINUSB:  displayName = "WinUSB";   break;
        default:            displayName = "UNKNOWN";  break;
        }
        fullDisplayName = "(" + displayName;
        fullDisplayName += ")";

        // Add function
        switch(currItf->m_func)
        {
        case IC_IF_MODEM:   fullDisplayName += " (MODEM)";   break;
        case IC_IF_AT:      fullDisplayName += " (AT)";      break;
        case IC_IF_DIAG:    fullDisplayName += " (DIAG)";    break; 
        case IC_IF_DIAG_0:  fullDisplayName += " (DIAG0)";   break; 
        case IC_IF_DIAG_1:  fullDisplayName += " (DIAG1)";   break; 
        case IC_IF_NET:     fullDisplayName += " (NET)";     break; 
        default:            fullDisplayName += " (UNKNOWN)"; break;
        }

        // Add serial name
        if (currItf->m_type == IC_IT_SERIAL)
        {
            displayName = currItf->m_serialName.c_str();
            fullDisplayName += " ";
            fullDisplayName += displayName;
        }

        // Add friendly name if not empty
        if (currItf->m_usbFriendlyName.IsEmpty() == false)
        {
            fullDisplayName += " ";
            fullDisplayName += currItf->m_usbFriendlyName.c_str();
        }

        // Duplicat display name by strdup which does malloc internally so we don't do that again
        (*port_list)[ii] = strdup(displayName.c_str());
        (*port_detail_list)[ii] = strdup(fullDisplayName.c_str());
    }

    return portCount;
}

ICERA_API UPD_Handle Open(const char *dev_name)
{
    /* Get a new handle and go */
    UPD_Handle handle = CreateHandle();
    if (handle)
    {
        if (ErrorCode_Success != SetDevice(handle, dev_name))
        {
            OutError(handle, "\n#Error: openPort [%s] failed [%s]\n\n", dev_name, strerror(errno));
            FreeHandle(handle);
            handle = 0;
        }
    }
    return handle;
}

ICERA_API int Close(UPD_Handle handle)
{
    int result = closePort(handle);
    if (HDATA(handle).option_dev_name)
    {
        free(HDATA(handle).option_dev_name);
        HDATA(handle).option_dev_name = NULL;
    }
    FreeHandle(handle);
    return result;
}

ICERA_API bool Write(UPD_Handle handle, void *buffer, int size)
{

    return (HDATA(handle).com_hdl->Write((const IUInt8*)buffer, size));
}

ICERA_API int Read(UPD_Handle handle, void *buffer, int size)
{
    IUInt32 lengthRead;
    HDATA(handle).com_hdl->Read((IUInt8 *)buffer, (IUInt32)size, lengthRead);
    return lengthRead;
    
}

ICERA_API int SetFlowControl(UPD_Handle handle, int value)
{
    return AT_ERR_SUCCESS;
}

ICERA_API int SetBaudrate(UPD_Handle handle, int speed)
{
        return AT_ERR_SUCCESS;
}

/* AT functions */
ICERA_API void SetCommandTimeout(UPD_Handle handle, long timeout)
{
    HDATA(handle).com_hdl->SetReadTimeout(timeout);
}

ICERA_API int SendCmd(UPD_Handle handle, const char* format,  va_list arg)
{
    char at_cmd[50];

	vsnprintf(at_cmd, sizeof(at_cmd), format, arg);
    OutStandard(handle, "%s", at_cmd);
    if (HDATA(handle).com_hdl->SendAtCommand(at_cmd))
    {    
        return AT_ERR_SUCCESS;
    } else {
        return AT_ERR_FAIL;
    }
    
}

static int SendCmdAndWaitResponseEx(UPD_Handle handle, const char *cmd, unsigned int timeout_sec, IcAStringList & response)
{
    time_t time_start, time_current;
    IcAStringList temp;

    response.Clear();
    time(&time_start);
    if (!HDATA(handle).com_hdl->SendAtCommand(cmd))
    {
        return AT_ERR_IO_WRITE;
    }

    bool received; 
    /* Wait AT response until it contains ok or error string */
    do{
        temp.Clear();
        received = HDATA(handle).com_hdl->GetResponse(temp);
        if (received)
        {
            response.Add(temp);
            received = temp.Contains("OK") || temp.Contains("ERROR");
        }
        time(&time_current);
    }while (!received && ((unsigned int)(time_current - time_start) < timeout_sec) );
    if (received)
    {
        printATcmd(handle, cmd, response);
        return AT_ERR_SUCCESS;
    }
    else
    {
        OutError(handle, "#ERROR: timeout\n\n");
        return AT_ERR_TIMEOUT;
    }

}

ICERA_API int SendCmdAndWaitResponse(UPD_Handle handle, const char *ok, const char *error, const char *format, va_list arg)
{
    time_t time_start, time_current;
    char at_cmd[50];
    IcAStringList response;
    IcAString str_response;

    snprintf(at_cmd, sizeof(at_cmd), format, arg);
    OutStandard(handle, "%s", at_cmd);
    time(&time_start);
    HDATA(handle).com_hdl->SendAtCommand(at_cmd);

    
    /* Wait AT response until it contains ok or error string */
    if ((ok != NULL) && (error != NULL))
    {
        do{
            HDATA(handle).com_hdl->GetResponse(response);
            response.GetDelimited(str_response,"\n");
            time(&time_current);
        }while (str_response.IsEqual("") && (time_current - time_start < 10) );
        OutStandard(handle, "-> %s \n\n",at_cmd, str_response.c_str());
        if (time_current - time_start > 10)
        {
            OutError(handle, "#ERROR: timeout\n\n");
            return AT_ERR_TIMEOUT;
        }
    }
    return AT_ERR_SUCCESS;
}

ICERA_API const char *GetResponseEx(UPD_Handle handle)
{
    IcAStringList response;
    IcAString str_response;
	const char * full_response;

    HDATA(handle).com_hdl->GetResponse(response);
    response.GetDelimited(str_response,"\n");
	full_response = strdup(str_response.c_str());
    return full_response;
}

/* Updater */
ICERA_API int UpdaterEx(UPD_Handle handle, char* archlist, int flash, int pcid)
{
    int result = ErrorCode_Error;
    bool systemState=false;
    HDATA(handle).com_hdl->IsOpen();

    HDATA(handle).progress.step = ProgressStep_Init;
    HDATA(handle).progress.percent = 0;

    OutDebug(handle, "Updater");
    OutDebug(handle, "DLL version: %s", DLD_VERSION);
    if (archlist != NULL || pcid)
    {
        if (archlist != NULL)
        {
            OutDebug(handle, "Upload%s %d:%s", flash ? " and flash" : "", strlen(archlist), archlist);
        /* Assume that we can talk to the modem, so lets log what state it's in */
            systemState = LogSystemState(handle);
        }
        if (systemState || pcid)
        {
            result = FirmwareUpdate(handle, archlist, pcid, flash);
            if (result == ErrorCode_Success)
            {
                HDATA(handle).progress.step = ProgressStep_Finish;
                if (archlist != NULL)
                    LogSystemState(handle);
            }
            else
            {
                OutError(handle, "\n#Error: Upgrade failure: %d\n\n", result);
                HDATA(handle).progress.step = ProgressStep_Error;
            }
        }
    }
    return result;
}

ICERA_API void ProgressEx(UPD_Handle handle, int* step, int* percent)
{
    OutDebug(handle, "ProgressEx");
    if (HDATA(handle).progress.totalweight)
    {
        *step = HDATA(handle).progress.step;
        *percent = HDATA(handle).progress.percent / HDATA(handle).progress.totalweight;
        OutDebug(handle, "Step %d: %d%%", *step, *percent);
    }
    else
    {
        *step = ProgressStep_Init;
        *percent = 0;
    }
}

ICERA_API int VerboseLevelEx(UPD_Handle handle, int level)
{
    if (level > VERBOSE_GET_DATA)
    {
        HDATA(handle).option_verbose = level;
    }

    return HDATA(handle).option_verbose;
}


ICERA_API char* GetLibVersion(char* version, int size)
{
    if (strlen(DLD_VERSION) < (size_t)size)
    {
        strcpy(version, DLD_VERSION);
        return version;
    }
    return NULL;
}

/* Legacy (deprecated) API */
ICERA_API int Updater(char* archlist, char *dev_name, int speed, int delay, unsigned short block_sz, int flash, int verbose, int modechange, int pcid)
{
    int res = ErrorCode_Error;

    if (dev_name && archlist)
    {
        OutDebug(DEFAULT_HANDLE, "Update%s on %s: [%s], Speed=%d, Delay=%d, BlockSize=%d, LastMode=%d, ChipID=%s", flash ? " and flash" : "", dev_name, archlist, speed, delay, block_sz, modechange, pcid ? "yes" : "no");

        InitHandle(DEFAULT_HANDLE);

        /* Open port - note that the Open() API will also set the output callback so no need to do that if using Open() */
        if (ErrorCode_Success == SetDevice(DEFAULT_HANDLE, dev_name))
        {
            /* Note, dev_name only valid while this function's stack is valid - but should not be a problem, nobody
             * should depend on it being valid after the function returns, as this function opens and closes the port
             */
            VerboseLevelEx(DEFAULT_HANDLE, verbose);
            SetModeChange(DEFAULT_HANDLE, modechange);
            SetCheckModeRestore(DEFAULT_HANDLE, global_check_mode_restore);
            SetSpeed(DEFAULT_HANDLE, speed);
            SetDelay(DEFAULT_HANDLE, delay);
            SetBlockSize(DEFAULT_HANDLE, block_sz);
            SetDisableFullCoredumpSetting(DEFAULT_HANDLE, disable_full_coredump);
            res = UpdaterEx(DEFAULT_HANDLE, archlist, flash, pcid);
            closePort(DEFAULT_HANDLE);
            free(HDATA(DEFAULT_HANDLE).option_dev_name);
            HDATA(DEFAULT_HANDLE).option_dev_name = NULL;
        }
        else
        {
            res = ErrorCode_DeviceNotFound;
        }
    }
    else
    {
        OutError(DEFAULT_HANDLE, "\n#Error: Null pointer [%p, %p]\n\n", dev_name, archlist);
    }
    return res;
}



/* TODO: Can make the method public if required. 
 *       Also, it's assumed the PNP events are good for serial ports, 
 *       so checkSuccess has no effect when the mode is COM_MODE_SERIAL */
ICERA_API int SwitchModeEx(UPD_Handle handle, unsigned int mode, bool checkSuccess)
{
    char command[20];
    int status = ErrorCode_Success;
    unsigned int current_mode =  GetCurrentMode(handle);

    if((int)current_mode == MODE_INVALID)
    {
        OutError(handle, "Switch mode: failed to get current mode\n");
        return ErrorCode_AT;
    }
    if (mode != current_mode)
    {
        status = ErrorCode_Error;
        do
        {
           {
                status = DelayedSwitchMode(handle, command, sizeof(command), mode, checkSuccess);
                if (status != ErrorCode_Success)
                {
                    OutError(handle, "Delayed switch mode failure %d\n", status);
                }
            }
            if(status == ErrorCode_Success)
            {
                if (HDATA(handle).com_hdl == 0)
                {
                    status = ErrorCode_ConnectionError;
                    break;
                }
            }
        } while(0);
    }
    return status;
}

#ifdef _WIN32

LRESULT CALLBACK WinProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    int result = FALSE;
    UPD_Handle idx;

    if (msg == WM_DEVICECHANGE)
    {
        for (idx = UPD_HANDLE_FIRST; idx <= UPD_HANDLE_LAST; idx++)
            if (hwnd == HDATA(idx).hwnd)
                break;
        assert((VALID_HANDLE(idx)) && HDATA(idx).pnp_callback);
        if (HDATA(idx).pnp_callback)
            result = HDATA(idx).pnp_callback((unsigned int)wParam, (unsigned char *)lParam, idx);
        if (result == TRUE)
            PostThreadMessage(HDATA(idx).threadid, WM_QUIT, 0, 0);
        return (LRESULT)TRUE;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

ICERA_API int UnregisterPnpEventByInterface(UPD_Handle handle, int register_handle)
{
    BOOL result;

    if (handle <= DEFAULT_HANDLE)
        handle = DEFAULT_HANDLE;
    if (register_handle < 0)
    {
        OutError(handle, "\nBad parameter 2: should be higher or equal to 0\n\n");
        return -1;
    }
    if (!HDATA(handle).hdev[register_handle])
    {
        OutError(handle, "\nAlready unregistered: %d\n\n", register_handle);
        return -2;
    }
    result = UnregisterDeviceNotification(HDATA(handle).hdev[register_handle]);
    HDATA(handle).hdev[register_handle] = NULL;
    return (int)result;
}

ICERA_API int RegisterPnpEventByInterface(UPD_Handle handle, GUID* guid)
{
    unsigned long idx;
    DEV_BROADCAST_DEVICEINTERFACE notifyFilter;

    if (handle <= DEFAULT_HANDLE)
        handle = DEFAULT_HANDLE;
    if (!HDATA(handle).hwnd)
    {
        OutError(handle, "\nStartPnpEvent function should be called before\n\n");
        return -1;
    }
    memset(&notifyFilter, 0, sizeof(notifyFilter));
    notifyFilter.dbcc_size = sizeof(notifyFilter);
    notifyFilter.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
    memcpy(&notifyFilter.dbcc_classguid, guid, sizeof(GUID));
    for (idx = 0 ; idx < MAX_REGISTERED ; idx++)
        if (!HDATA(handle).hdev[idx])
            break;
    if (idx == MAX_REGISTERED)
    {
        OutError(handle, "\nMaximum registered GUID has been reached: %d\n\n", MAX_REGISTERED);
        return -2;
    }
    HDATA(handle).hdev[idx] = RegisterDeviceNotification(HDATA(handle).hwnd, &notifyFilter, DEVICE_NOTIFY_WINDOW_HANDLE);
    if (!HDATA(handle).hdev[idx])
    {
        OutError(handle, "\nRegisterDeviceNotification error: %08X\n\n", GetLastError());
        return -3;
    }
    return idx;
}

ICERA_API int StopPnpEvent(UPD_Handle handle)
{
    if (handle <= DEFAULT_HANDLE)
        handle = DEFAULT_HANDLE;
    if (!HDATA(handle).hwnd)
        return FALSE;
    return PostThreadMessage(HDATA(handle).threadid, WM_QUIT, 0, 0);
}

ICERA_API int StartPnpEvent(UPD_Handle handle, pnp_callback_type pnp_callback, HWND* hwnd)
{
    int size;
    char className[18 + 1]; /* Max: UpdaterPnPEvent255 */
    WNDCLASSA wc;
    memset(&wc, 0, sizeof(wc));
    wc.hInstance = GetModuleHandle(0);
    wc.lpszClassName = className;
    wc.lpfnWndProc = WinProc;

    if (handle <= DEFAULT_HANDLE)
    {
        handle = DEFAULT_HANDLE;
    }
    size = snprintf(className, sizeof(className), "UpdaterPnPEvent%d", (int)handle);
    if ((size < 0) || (size >= (int)sizeof(className)))
    {
        OutError(handle, "\nStartPnpEvent:snprintf function failed: %d\n\n", size);
        return 0;
    }
    if (HDATA(handle).hwnd)
    {
        OutError(handle, "\nStopPnpEvent function should be called before\n\n");
        return 0;
    }
    if (!RegisterClass(&wc))
    {
        OutError(handle, "\nRegisterClass error: %08X\n\n", GetLastError());
        return 0;
    }
    HDATA(handle).pnp_callback = NULL;
    HDATA(handle).hwnd = CreateWindowEx(WS_EX_TOPMOST, className, className, 0, 0, 0, 0, 0, HWND_MESSAGE, 0, 0, 0);
    if (!HDATA(handle).hwnd)
    {
        OutError(handle, "\nCreateWindowEx error: %08X\n\n", GetLastError());
        return 0;
    }
    HDATA(handle).pnp_callback = pnp_callback;
    if (hwnd)
        *hwnd = HDATA(handle).hwnd;
    return 1;
}

ICERA_API int WaitPnpEvent(UPD_Handle handle, unsigned int timeout_in_ms, unsigned long* threadid)
{
    int size;
    MSG msg;
    char className[18 + 1]; /* Max: UpdaterPnPEvent255 */

    if (handle <= DEFAULT_HANDLE)
    {
        handle = DEFAULT_HANDLE;
    }
    size = snprintf(className, sizeof(className), "UpdaterPnPEvent%d", (int)handle);
    if ((size < 0) || (size >= (int)sizeof(className)))
    {
        OutError(handle, "\nWaitPnpEvent:snprintf function failed: %d\n\n", size);
        return 0;
    }    if (!HDATA(handle).hwnd)
    {
        OutError(handle, "\nStartPnpEvent function should be called before\n\n");
        return 0;
    }
    assert(HDATA(handle).pnp_callback);
    HDATA(handle).threadid = GetCurrentThreadId();
    if (threadid)
        *threadid = HDATA(handle).threadid;
    HDATA(handle).timeout = timeout_in_ms;  /* 0 == infinite */
    if (HDATA(handle).timeout)
    {
        if (!SetTimer(HDATA(handle).hwnd, IDT_TIMEOUT, HDATA(handle).timeout, NULL))
        {
            OutError(handle, "\nSetTimer function failed\n\n");
            DestroyWindow(HDATA(handle).hwnd);
            UnregisterClass(className, GetModuleHandle(0));
            HDATA(handle).hwnd = NULL;
            return 0;
        }
    }
    while (TRUE)
    {
        BOOL bRet = GetMessage(&msg, NULL, 0, 0);
        if ((bRet == 0) || (bRet == -1) || (msg.message == WM_QUIT) || (msg.message == WM_TIMER))
            break;
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    if (HDATA(handle).timeout)
    {
        PeekMessage(&msg, HDATA(handle).hwnd, WM_TIMER, WM_TIMER, PM_REMOVE);
        KillTimer(HDATA(handle).hwnd, IDT_TIMEOUT);
    }
    DestroyWindow(HDATA(handle).hwnd);
    UnregisterClass(className, GetModuleHandle(0));
    HDATA(handle).hwnd = NULL;
    if (msg.message == WM_TIMER)
    {
        OutError(handle, "Exit on timeout\n");
        return 2;
    }
    /* Success */
    return 1;
}

#endif /* _WIN32 */
#ifdef ICERA_EXPORTS
}
#endif

extern unsigned short ComputeChecksum16(void * p, int lg)
{
    unsigned short *ptr = (unsigned short *)p;
    unsigned short chksum = 0;
    unsigned short * end = ptr + lg/2;

    while (ptr < end)
    {
        chksum ^= *ptr++;
    }

    return chksum;
}

#ifdef _WIN32

#ifdef ICERA_EXPORTS
// GetProcAddress to have access to any funtions
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
#else
BOOL WINAPI Updater_Initialize(DWORD fdwReason)
#endif
{
    switch (fdwReason)
    {
    case DLL_PROCESS_ATTACH: // Called by LoadLibrary
        updater_load();
        break;
    case DLL_PROCESS_DETACH: // Called by FreeLibrary
        updater_unload();
        break;
    }
    return TRUE;
}
#else
#ifndef ANDROID
// dlsym to have access to any funtions
// On Android, we build Updater.c statically to be linked in downloader:
//  the fact of having below symbols in binary is preventing downloader
//  to correctly return at exit...
static void __attribute__ ((constructor)) library_load(void) // Called by dlopen()
{
    updater_load();
}

static void __attribute__ ((destructor)) library_unload(void) // Called by dlclose()
{
    updater_unload();
}
#endif
#endif


// ----------------------------------------------------------

