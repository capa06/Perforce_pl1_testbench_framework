/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2006
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_config.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup UsbDriver
 * @{
 */

/**
 * @file drv_usb_config.h Common definitions and types
 *
 */

#ifndef DRV_USB_CONFIG_H
#define DRV_USB_CONFIG_H


#include "icera_global.h"
#include "drv_usb_profile_ids.h"
#include "drv_global.h"
/******************************************************************************
 * Constants
 ******************************************************************************/
#define MAX_USB_PROFILE_DESC    256

#define CONFIG_0_MAX_POWER      250  /* 500 mA */
#define CONFIG_1_MAX_POWER      250  /* 500 mA */
#define CONFIG_2_MAX_POWER      250  /* 500 mA */

/******************************************************************************
 * Exported macros
 ******************************************************************************/

#define USB_MAX_INSTANCES           8

#define USB_F_COMPOSITE             BIT(0)
#define USB_F_IAD                   BIT(1)
#define USB_F_WHCM                  BIT(2)
#define USB_F_SINGLE_IF             BIT(3)
#define USB_F_WIRELESS              BIT(4)

#define IMMEDIAT_SWITCH             0

#define USB_VID_UNSPECIFIED         0x0000
#define USB_PID_UNSPECIFIED         0x0000

#define SWITCH_DELAY_DEFAULT        10000 /* us */

#define USB_SWITCH_INFO_V1          1

#define MAX_UNICODE_STR_SZ          256
#define MAX_STR_SZ                  (MAX_UNICODE_STR_SZ / 2)

#define MAX_USB_VENDOR_MASS_SIZE    8
#define MAX_USB_PRODUCT_MASS_SIZE   16

#define EOS                         '\0'

#define STRNCPY(T, S)               do { (T)[0] = EOS; strncat((T), (S), sizeof(T) - 1); } while(0)

#define DBG_UIST_STRING(S)          ( ((S)[0] << 24) | ((S)[1] << 16) | ((S)[2] << 8) | (S)[3])

#define ARRAY_SIZE(A)               (sizeof(A) / sizeof((A)[0]))

#define RESTARTED_ON_EJECT(O)       ((O) & USBV_OS_GENERIC_LINUX)

#define OS_DESCRIPTORS_VENDOR_REQUEST_VALUE 2

/******************************************************************************
 * Exported types
 ******************************************************************************/
typedef enum
{
    USBV_OS_UNSPECIFIED,
    USBV_OS_GENERIC_WINDOWS,
    USBV_OS_GENERIC_LINUX,
    USBV_OS_GENERIC_MACOS,
} drv_UsbOsId;

typedef enum
{
    DEVICE_TYPE_NONE,
    DEVICE_TYPE_MSD,
    DEVICE_TYPE_HID,
    DEVICE_TYPE_SERIAL,
    DEVICE_TYPE_LOOPBACK,
    DEVICE_TYPE_TEST,
    DEVICE_TYPE_CDC_WHCM,
    DEVICE_TYPE_CDC_ACM,
    DEVICE_TYPE_CDC_ECM,
    DEVICE_TYPE_CDC_OBEX,
    DEVICE_TYPE_VIDEO,
    DEVICE_TYPE_DFU,
    DEVICE_TYPE_SICD,
    DEVICE_TYPE_VENDOR,
    DEVICE_TYPE_CDC_NCM,
    DEVICE_TYPE_CDC_MBIM,
    DEVICE_TYPE_RNDIS,
} fd_type_t;

typedef enum
{
    USB_FCTID_NONE,
    USB_FCTID_AT,
    USB_FCTID_PPP,
    USB_FCTID_NET,
    USB_FCTID_DIAG,
    USB_FCTID_GPS,
    USB_FCTID_AUDIO,
    USB_FCTID_CDROM,
    USB_FCTID_SDHC,
    USB_FCTID_UDISK,
    USB_FCTID_MUX710,
    USB_FCTID_REMOTE_FS,
    USB_FCTID_AGPS,
    USB_FCTID_MSD,
    USB_FCTID_DSS,
	USB_FCTID_UNDEFINED /* Must be the last function ID and must not over 31 */
} drv_UsbFctId;

#define USB_FCTID_NAMES { \
                 "NONE",     \
                 "AT",      \
                 "PPP",     \
                 "NET",     \
                 "DIAG",    \
                 "GPS",     \
                 "AUDIO",   \
                 "CDROM",   \
                 "SDHC",    \
                 "UDISK",   \
                 "MUX710",  \
                 "RFS",     \
                 "AGPS",    \
                 "MSD",     \
                 "MBIM", \
                 "UNDEFINED"}

#define USB_FCTTYPE_NONE            0
#define USB_FCTTYPE_MASS_MASK       (BIT(USB_FCTID_CDROM) | BIT(USB_FCTID_UDISK) | BIT(USB_FCTID_SDHC))

#define USB_FCTOPTION_DUAL_DIAG     BIT(0)
#define USB_FCTOPTION_AUTH          BIT(1)
/* Limited to 15 by the drv_UsbFct format */
#define USB_FCTOPTION_ALL           0xFFFF

#define MAX_FCTLIST_SIZE            20

typedef struct
{
    uint32      type;
    const char* name;
} drv_UsbFctKind;

typedef struct
{
    int             serial_index;
    uint8           index;
    drv_UsbFctKind  kind;
    uint16          options;
    const char*     name;
} drv_UsbFct;

#define USB_FCT_SET_OPTION(PTR, OPT)    (PTR)->options = (OPT)
#define USB_FCT_ADD_OPTION(PTR, OPT)    (PTR)->options |= (OPT)
#define USB_FCT_RMV_OPTION(PTR, OPT)    (PTR)->options &= ~(OPT)
#define USB_FCT_SET_NAME(PTR, NAM)      (PTR)->kind.name = (NAM)
#define USB_FCT_SET_TYPE(PTR, TYP)      (PTR)->kind.type = (TYP)

#define USB_FCT_INIT_STRUCT(PTR, ID)    (PTR)->options = 0;                                 \
                                        DEV_ASSERT_EXTRA(((ID) <= USB_FCTID_UNDEFINED) &&   \
                                                         "Id out of bounds:", 1, (ID));     \
                                        (PTR)->kind.type = BIT(ID);                         \
                                        (PTR)->kind.name = drv_UsbFctIdNames[(ID)]

extern const char* const drv_UsbFctIdNames[];

//typedef result_t (*fd_init_func_t)(void *ctx);
typedef struct
{
    fd_type_t type;             /* Function driver type */
    unsigned char index_in_profile;
    unsigned char fifo_prio;    /* FIFO priority, 0 is highest priority. */
    /* Use when USB_F_VENDOR to overload standard values */
    uint8 cci_class;            /* Control-if CDC class */
    uint8 cci_subclass;         /* Control-if CDC subclass */
    uint8 cci_protocol;         /* Control-if CDC protocol */
    uint8 dc_class;             /* Data-if CDC class */
    uint8 dc_subclass;          /* Data-if CDC subclass */
    uint8 dc_protocol;          /* Data-if protocol */
    bool no_class_desc;         /* Remove default CDC class descriptor */
    bool vendor;                /* Truen when cci_xxx and eventually dc_xxx fields are used */
    uint8 configs;              /* Bit mask of configs this FD should be used for */
} fd_instance_t;

typedef struct
{
    unsigned char version;
    drv_Firmware firmware_mode;
    drv_UsbProfileId profile;

    unsigned int flags;
    unsigned char num_instances;
    fd_instance_t *fd_instances;

} drv_UsbConfig;

typedef struct
{
    drv_UsbProfileId no_log;    /** profile to be used in modem / non-engineering mode */
    drv_UsbProfileId ldr;       /** related profile when in LDR/IFT mode */

    unsigned int flags;
    unsigned char num_instances;
    fd_instance_t *fd_instances;
    unsigned short pid;
} drv_UsbProfileInfo;

typedef struct
{
    unsigned long       deferred;
    unsigned short      vid;
    unsigned short      pid;
    drv_UsbOsId         os;
    drv_UsbProfileId    profile;
    unsigned char       from_mode;
    unsigned char       version;
} drv_UsbSwitchInfo;

typedef struct
{
    unsigned short  release;
	unsigned long   flashdisk_size;
    bool            flashdisk_readonly;
    char            lun_list[MAX_STR_SZ];
    char            vendor_name[MAX_USB_VENDOR_MASS_SIZE + 1];
    char            default_name[MAX_USB_PRODUCT_MASS_SIZE +1];
    char            sdhc_name[MAX_USB_PRODUCT_MASS_SIZE + 1];
    char            flashdisk_name[MAX_USB_PRODUCT_MASS_SIZE + 1];
} drv_UsbLunInfo;

/******************************************************************************
 * Exported Functions
 ******************************************************************************/

/**
 * Get USB profile given its name
 * The name can be either "USB_PROFILE_xxx" or simply "xxx".
 *
 * @return          USB profile id
 *
 */
drv_UsbProfileId drv_UsbGetProfileByName(char *name);

/**
 * Get USB profile name, given its id.
 *
 * @return          NULL or "USB_PROFILE_xxx"
 *
 */
const char *drv_UsbGetProfileName(drv_UsbProfileId id);

/**
 * Update USB configuration and perform a firmware mode switch.
 *
 * @param info      Describe switch conditions
 *
 */
void drv_UsbModeSwitch(drv_UsbSwitchInfo* info);

/** 
 * Update USB configuration with specific profile and perform a firmware mode switch.
 *
 * @param info      Desribe the profile to switch to
 *
 * @return false if profile is not valid
 */
bool drv_UsbProfileSwitchById(uint32 profileId, unsigned long deferredTimeInus);

void
drv_UsbModeSwitchDirect( drv_UsbProfileId profile,unsigned short pid);

/**
 * Update USB configuration with specific profile and perform a firmware mode switch.
 *
 * @param info      Desribe the profile to switch to
 *
 * @return false if profile is not valid
 */
bool drv_UsbProfileSwitchByName(char *profileName, unsigned long deferredTimeInus);

/**
 * Return boolean that tests if USB enumeration type is:
        1:USB_F_COMPOSITE, 2:USB_F_IAD, 4:USB_F_WHCM, 8:USB_F_SINGLE_IF
 */
bool drv_UsbIsEnumType(unsigned char enumtype);

/**
 * Returns number of function instances
 ** for the current profile
 */
unsigned char drv_UsbGetNbFunctions();

/**
 * Returns number of function instances
 * for the given profile if
 */
unsigned char drv_UsbGetNbFunctionsForProfile(uint32 profileId);

/**
 * Returns number of function instances of a given type
 */
unsigned char drv_UsbGetNumInstancesByType(fd_type_t type);

/**
 * Returns whether the Dynamic functions (DSS) are enabled 
 */
bool drv_UsbIncludeDynamicFunctions(void);

/**
 * Returns FIFO priority associated to the given function instance number
 */
unsigned char drv_UsbFunctionPriority(unsigned char fd_number);

/**
 * Returns type of the given function instance number
 */
fd_type_t drv_UsbFunctionType(unsigned char fd_number);
/**
 * Returns type of the given function instance number
 * for the given profile
 */
fd_type_t drv_UsbFunctionTypeForProfile(uint32 profileId,unsigned char fd_number);
/**
 * Returns the interfaces used by given type
 */
int drv_UsbNumInterfacesForType(fd_type_t type);
/**
 * Returns the number of extra alt interfaces used by given type
 */
int drv_UsbNumAltInterfacesForType(fd_type_t type);

/**
 * Returns the function index for the given interface 
 */
int drv_UsbFunctionIndexByInterface(unsigned char iface_index);
/**
 * Returns true when a interface is found that matches the 
 * type paramter. 
 * returns false when no interface is found that matches the
 * type parameter.
 * When interface has been matched and the iface_idx paramter 
 * is none-NULL, it is set with the index of the found interface.
 */
bool drv_UsbInterfaceForType(const fd_type_t type, uint32* iface_idx);
/**
 * Returns true when a interface is found that matches the 
 * type paramter. 
 * returns false when no interface is found that matches the
 * type parameter.
 * When interface has been matched and the iface_idx paramter 
 * is none-NULL, it is set with the index of the found interface.
 */
bool drv_UsbInterfaceForFctId(const drv_UsbFctId fct_id, uint32* iface_idx);
/**
 * Returns the drv_UsbFctId type for the given index
 */
uint32 drv_UsbFctTypeByFunctionIndex(int fd_number);

/**
 * Returns the drv_UsbFctId  description string for the given index
 */
const char* drv_UsbFctDescByFunctionIndex(int fd_number);

/**
 * Returns the customized function name string for the given index
 */
const char* drv_UsbFctNameByFunctionIndex(int fd_number);
/**
 * Returns pointer of the given function instance number
 */
const fd_instance_t* drv_UsbFunction(unsigned char fd_number);

/**
 * Returns the current profile enables remote wake
 */
bool drv_UsbIsRemoteWakeEnabled(void);

/**
 * Set the Remote Wakeup Test parameters
 */
void drv_UsbSetRemoteWakeTest(bool enabled, uint32 timeout_ms);

/**
 * Get the Remote Wakeup Test parameters
 */
void drv_UsbGetRemoteWakeTest(bool *enabled, uint32 *timeout_ms);

/**
 * Returns whether bus or self powered
 */
bool drv_UsbIsSelfPowered(void);
/**
 *  Returns the max usb power
 */
unsigned char drv_UsbMaxPower(void);
/**
 * Returns the current profile
 */
drv_UsbProfileId drv_UsbGetUsbCurrentProfile(void);

/*
 * Get PID+Profile default values (eventually overrided by the CustomConfig USB section)
 */
void drv_UsbGetProfileFromCC(drv_UsbSwitchInfo* info,drv_Firmware firmware);

/**
 * Get default LUN information (eventually overrided by the CustomConfig USB section)
 */
void drv_UsbGetLunInfo(drv_UsbLunInfo* info);

/**
 * Test purpose: Connect/disconnect USB bus
 */
void drv_UsbBusState(int time_in_ms, bool connect);

/**
 * Return a filtered list of functions
 */
size_t drv_UsbGetFctList(uint32 masktype, drv_UsbFct* list, size_t listsize);

/** 
 * Return the function related to a given index.
 * 
 * @param index the function index in the profile
 * @param fct pointer to the function descriptor structure
 * 
 * @return int <0 in case of failure.
 */
int drv_UsbGetFct(int index, drv_UsbFct *fct);

int drv_UsbGetFctElement(int index, drv_UsbFct** fct);

const char* drv_UsbGetVendorName(void);

drv_UsbOsId drv_UsbGetHostType(void);

void drv_UsbSetHostType(drv_UsbOsId determined_type, bool determined_by_host_itself);

/**
 * Get the Maximum number of data path in drivers. Modem can not 
 * set up more PDP context than this value. 
 * 
 * @param max_data_path_allowed 
 */
int drv_UsbGetNbMaxDataPath(void);

/**
 * Return Device docking mode
 *
 * @return true if the device is a "Docking" device.
 */
bool drv_UsbDockingMode(void);

/**
 * Return Profile info structure
 *
 * @param profile the profile ID
 *
 * @return Return pointer on the drv_UsbProfileInfo structure that match with the given profile ID.
 */
drv_UsbProfileInfo* drv_UsbGetProfileInfo(drv_UsbProfileId profile);

/**
 * Compare profile
 *
 * @param profile1 the first profile ID to be compared
 * @param profile2 the second profile ID to be compared
 *
 * @return Return true if profiles are identical (even if their ID was not)
 */
bool drv_UsbIfCmp(drv_UsbProfileId profile1, drv_UsbProfileId profile2);

/**
 * Return the current USB product ID used
 *
 * @return USB PID
 */
unsigned short drv_UsbGetPid(void);

/**
 * Return the current USB vendor ID used
 *
 * @return USB VID
 */
unsigned short drv_UsbGetVid(void);
/**
 * copy into passed string length chars of
 * the chip ID. convert to HEX characters
 *
 * @return number of characters copied
 */
int drv_UsbGetMacAddressString(uint8* buffer,uint8 size);
int drv_UsbGetSerialNumberString(uint8* buffer,uint8 size);
int drv_UsbGetManufacturerString(uint8* buffer,uint8 size);
int drv_UsbGetProductNameString(uint8* buffer,uint8 size);

int drv_UsbGetFunctionNameString(uint8* buffer, uint8 size, int fd_number);

/**
 * Returns the Maximum allowed Modem interfaces per USB network 
 * interfaces 
 *  
 * @return int 
 */
int drv_UsbGetMaxModemIfPerUsbIf(void);

/**
 * Return the number of network interface in the USB profile
 * 
 * @author ncollonville (1/31/2014)
 * 
 * @return int 
 */
int drv_UsbGetNetworkIfNumber(void);

/**
 * Returns the Preferred MTU size from config
 *  
 * @return int 
 */
int drv_UsbGetPreferredMTU(void);
/**
 * 
 *  
 * 
 */
void drv_UsbDynamicFunctionsReset(void);
/**
 *  add a interface function at runtime
 *  
 *  @return int -1 on error, otherwise 0
 */
int drv_UsbDynamicFunctionsAdd(int serial_index, uint32 type,const char*name);

#endif /* #ifndef DRV_USB_CONFIG_H */

/** @} END OF FILE */
