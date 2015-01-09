/*************************************************************************************************
 * Copyright (c) 2014, NVIDIA CORPORATION. All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto. Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 *************************************************************************************************
  * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup updater
 * @{
 */

 /**
  * @file globals.h The global definitions for Updater dll
  *
  */

#ifndef GLOBALS_H
#define GLOBALS_H

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#if defined (_MSC_VER)
/** Support for non-ANSI C use of bool in the code. */
# if !defined (__cplusplus)
typedef unsigned char bool;
#  define false 0
#  define true  1
# endif
#else
#include <stdbool.h>        /* Needed for bool type definition. */
#endif

#include <stddef.h>

#ifdef VISUAL_EXPORTS

#define snprintf _snprintf
#define    S_ISREG(m)    (((m) & S_IFMT) == S_IFREG)

#endif

#ifdef _WIN32
#ifndef WINVER
#define WINVER 0x0500 /* From Win2K (included) */
#endif
/* Windows */
#include <windows.h>
#ifdef ICERA_EXPORTS
    #define ICERA_API __declspec(dllexport)
#else
    #define ICERA_API
#endif
#define DEFAULT_DEV             "COM1"

#define DEVCLASS_MODEM_GUID        { 0x2c7089aaL, 0x2e0e, 0x11d1, { 0xb1, 0x14, 0x00, 0xc0, 0x4f, 0xc2, 0xaa, 0xe4 } }
#define DEVCLASS_COMPORT_GUID    { 0x86e0d1e0L, 0x8089, 0x11d0, { 0x9c, 0xe4, 0x08, 0x00, 0x3e, 0x30, 0x1f, 0x73 } }
#define CLASS_MODEM_GUID        { 0x4D36E96DL, 0xE325, 0x11CE, { 0xBF, 0xC1, 0x08, 0x00, 0x2B, 0xE1, 0x03, 0x18 } }
#define CLASS_COMPORT_GUID      { 0x4D36E978L, 0xE325, 0x11CE, { 0xBF, 0xC1, 0x08, 0x00, 0x2B, 0xE1, 0x03, 0x18 } }

#define REG_ENUM            "SYSTEM\\CurrentControlSet\\Enum"
#define REG_SERVICES        "SYSTEM\\CurrentControlSet\\Services"
#define REG_CTRL_CLASS      "SYSTEM\\CurrentControlSet\\Control\\Class"
#define REG_CTRL_DEVCLASS   "SYSTEM\\CurrentControlSet\\Control\\DeviceClasses"

#define DEFAULT_BLOCK_SZ         16384 /* Higher value trigg the watchdog */
#define DEFAULT_MBIM_BLOCK_SZ    4000

#else /* _WIN32 */

/* Linux */
#define ICERA_API
#define DEFAULT_DEV             "/dev/ttyACM1"

#define DEFAULT_BLOCK_SZ         16384 /* Higher value trigg the watchdog */
#define DEFAULT_RAW_IF_BLOCK_SZ  1400  /* For packet socket-based operations it must be smaller than MTU minus header length */

#endif /* _WIN32 */

#define DEFAULT_SPEED       115200

#define DLD_VERSION         "14.07"

#define DEFAULT_DELAY       25

#define MAX_BLOCK_REJECT    3
#define MIN_BLOCK_SZ        1
#define MAX_BLOCK_SZ        65532
#define DEFAULT_SEND_NVCLEAN true
#define DEFAULT_CHECK_PKGV   true

#define EOS                 '\x00'

#define FILE_SEPARATOR      ";"

#define AT_CMD_MODE         "AT%MODE?\r\n"
#define AT_RESPONSE         ": "
#define AT_CMD_MODEx        "AT%%MODE=%d\r\n"

#define AT_CMD_MODE0        "AT%MODE=0\r\n"
#define AT_CMD_MODE1        "AT%MODE=1\r\n"
#define AT_CMD_MODE2        "AT%MODE=2\r\n"
#define AT_CMD_MODE3        "AT%MODE=3\r\n"
#define AT_CMD_MODE13       "AT%MODE=1,3\r\n"
#define AT_CMD_LOAD         "AT%LOAD\r\n"
#define AT_CMD_GMR          "AT+GMR\r\n"
#define AT_CMD_ECHO_OFF     "ATE0\r\n"
#define AT_CMD_ECHO_ON      "ATE1\r\n"
#define AT_CMD_CHIPID       "AT%CHIPID\r\n"
#define AT_CMD_PROG         "AT%%PROG=%d\r\n"
#define AT_CMD_IFLIST       "AT%IFLIST\r\n"
#define AT_CMD_IFLIST_1     "AT%IFLIST=1\r\n"
#define AT_CMD_IFLIST_2     "AT%IFLIST=2\r\n"
#define AT_CMD_IFWR         "AT%IFWR\r\n"
#define AT_CMD_ICOMPAT      "AT%ICOMPAT\r\n"
#define AT_CMD_NVCLEAN      "AT%NVCLEAN\r\n"
#define AT_CMD_IBACKUP      "AT%IBACKUP\r\n"
#define AT_CMD_IRESTORE     "AT%IRESTORE\r\n"
#define AT_CMD_IGETFWID     "AT%IGETFWID\r\n"
#define AT_CMD_IPKGV        "AT%%IPKGV=%s%s%s%s%s%s%s\r\n"
#define AT_CMD_ARCHDIGEST   "AT%%IGETARCHDIGEST=\"%s\"\r\n"
#define AT_CMD_IFULLCOREDMP "AT%IFULLCOREDUMP=0\r\n"


#define AT_RSP_OK           "\r\nOK\r\n"
#define AT_RSP_ERROR        "\r\nERROR\r\n"

#define VERBOSE_GET_DATA        -1
#define VERBOSE_SILENT_LEVEL    0
#define VERBOSE_INFO_LEVEL      1
#define VERBOSE_STD_ERR_LEVEL   2
#define VERBOSE_DUMP_LEVEL      3

#define VERBOSE_DEFAULT_LEVEL   VERBOSE_INFO_LEVEL

#define MODE_INVALID        -1

#define MODE_MODEM          0
#define MODE_LOADER         1
#define MODE_FACTORY_TEST   2
#define MODE_MASS_STORAGE   3
#define MODE_MAX            4

#define MODE_DEFAULT        MODE_MODEM

#define AT_ERR_SUCCESS      1
#define AT_ERR_FAIL         0
#define AT_ERR_TIMEOUT      -1
#define AT_ERR_IO_WRITE     -2
#define AT_ERR_COM_SPEED    -3
#define AT_ERR_SIGNALS      -4
#define AT_ERR_NOTSUPPORTED -5
#define AT_ERR_CTS          -6

#define AT_SUCCESS(R)       ((R) == AT_ERR_SUCCESS)
#define AT_FAIL(R)          ((R) < AT_ERR_SUCCESS)
#define AT_WARN(R)          ((R) > AT_ERR_SUCCESS)

#define MAX(A, B)           (((A) > (B)) ? (A) : (B))
#define ARRAY_SIZE(A)       (sizeof(A) / sizeof((A)[0]))

#ifndef USE_STDINT_H
/**
 * @defgroup icera_common_types Fundamental types
 *
 * @{
 */

/**
 * Minimum value that can be held by type int8.
 * @see INT8_MAX
 * @see int8
 */
#define INT8_MIN        (-128)
/**
 * Maximum value that can be held by type int8.
 * @see INT8_MIN
 * @see int8
 */
#define INT8_MAX        (127)
/**
 * Maximum value that can be held by type uint8.
 * @see uint8
 */
#define UINT8_MAX       (255)
/**
 * Minimum value that can be held by type int16.
 * @see INT16_MAX
 * @see int16
 */
#define INT16_MIN       (-32768)
/**
 * Maximum value that can be held by type int16.
 * @see INT16_MIN
 * @see int16
 */
#define INT16_MAX       (32767)
/**
 * Maximum value that can be held by type uint16.
 * @see uint16
 */
#define UINT16_MAX      (65535)
/**
 * Minimum value that can be held by type int32.
 * @see INT32_MAX
 * @see int32
 */
#define INT32_MIN       (-2147483648L)
/**
 * Maximum value that can be held by type int32.
 * @see INT32_MIN
 * @see int32
 */
#define INT32_MAX       (2147483647L)
/**
 * Maximum value that can be held by type uint32.
 * @see uint32
 */
#define UINT32_MAX      (4294967295UL)
/**
 * Minimum value that can be held by type int64.
 * @see INT64_MAX
 * @see int64
 */
#define INT64_MIN        (-0x7fffffffffffffffLL-1)
/**
 * Maximum value that can be held by type int64.
 * @see INT64_MIN
 * @see int64
 */
#define INT64_MAX       (0X7fffffffffffffffLL)
/**
 * Maximum value that can be held by type uint64.
 * @see uint64
 */
#define UINT64_MAX      (0xffffffffffffffffULL)

#endif /* USE_STDINT_H */

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * 8 bit signed integer
 * @see INT8_MAX
 * @see INT8_MIN
 */
typedef signed   char int8;
/**
 * 8 bit unsigned integer
 * @see UINT8_MAX
 */
typedef unsigned char uint8;

/**
 * 16 bit signed integer
 * @see INT16_MAX
 * @see INT16_MIN
 */
typedef signed   short int16;
/**
 * 16 bit unsigned integer
 * @see UINT16_MAX
 */
typedef unsigned short uint16;

/**
 * 32 bit signed integer
 * @see INT32_MAX
 * @see INT32_MIN
 */
typedef signed   int int32;

/**
 * 32 bit unsigned integer
 * @see UINT32_MAX
 */
typedef unsigned int uint32;

/**
 * 64 bit signed integer
 * @see INT64_MAX
 * @see INT64_MIN
 */
#if !defined(int64)
typedef signed   long long int64;
#endif

/**
 * 64 bit unsigned integer
 * @see UINT64_MAX
 */
typedef unsigned long long uint64;





/**
 * Structure to hold a pointer into a circular buffer
 *
 * This structure allows the representation of a position in a circular buffer to be managed. The
 * position is managed in atoms
 */
typedef struct circ_ptr_s
{
    void *base;
    uint16 offset;                                                             /**< in atoms */
    uint16 length;                                                             /**< in atoms */
} circ_ptr_s;

#endif /* GLOBALS_H */
/** @} END OF FILE */
