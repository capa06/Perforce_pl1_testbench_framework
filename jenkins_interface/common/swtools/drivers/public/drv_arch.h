/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2010
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_arch.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup ArchiveDriver Archive Services
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch.h Archive file utilities
 *
 */

#ifndef DRV_ARCH_H
#define DRV_ARCH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#if defined(__dxp__)
#include "dxparchconsts.h"
#endif
#include "drv_hwplat.h"
#include "drv_arch_type.h"
#include "drv_global.h"
#include "drv_shm.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#if defined (TARGET_DXP9140)
#define ARCH_TAG     ARCH_TAG_9140
#elif defined (TARGET_DXP9040)
#define ARCH_TAG     ARCH_TAG_9040
#elif defined (TARGET_GNU_LINUX)
#define ARCH_TAG     ARCH_TAG_8060 //the compilation shall not break in case host test is used
#else
/* Adding this error to keep a trace of dev for next Liv generation integration... */
#error Please update code with valid tag value
#endif

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/
typedef enum
{
    ARCH_BT2_COMPAT_NO_ERR
    ,ARCH_BT2_COMPAT_FLASH_TRAILER_NOT_FOUND
    ,ARCH_BT2_COMPAT_INVALID_FLASH_ARCHIVE
    ,ARCH_BT2_COMPAT_NO_RAM_TRAILER
    ,ARCH_BT2_COMPAT_INVALID_FLASH_TRAILER
    ,ARCH_BT2_COMPAT_INVALID_RAM_TRAILER
    ,ARCH_BT2_COMPAT_INCOMPLETE_FLASH_TRAILER
    ,ARCH_BT2_COMPAT_INCOMPLETE_RAM_TRAILER
    ,ARCH_BT2_COMPAT_FAILURE

}ArchBt2HwplatCompat;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern const tArchFileProperty arch_type[];
extern const uint32            arch_type_max_id;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 *
 *
 * @param in_ram
 * @param arch_start
 * @param file_desc
 * @param hash_digest
 * @param rsa_sig
 * @param key_id
 *
 * @return int
 */
int drv_arch_RSASignVerify(bool in_ram,
                           uint8 *arch_start,
                           tAppliFileHeader * file_desc,
                           uint8 *hash_digest,
                           uint8 *rsa_sig,
                           uint32 *key_id);

/**
 * Verify public platform ID (chip ID or fuse ID) embedded in 
 * data file. 
 *
 * @param arch_start buffer of file data
 * @param file_desc pointer on data file header
 *
 * @return 0 if embedded pcid or pfid matches with platform 
 *         ppid,
 *         -1 if not
 */
int drv_arch_PPIDVerify( uint8 * arch_start, tAppliFileHeader * file_desc);

/**
 * Verify public platform ID (chip ID or fuse ID) from data 
 * buffer.
 *
 * @param ppid buffer with PPID
 * @param type to know type of ID to verify
 *
 * @return 0 if given pcid or pfid matches with platform ppid, 
 *         -1 if not
 */
int drv_arch_PPIDVerifyBuffer( uint8 *ppid, tArchPpidType type);

/**
 * Retreive data from file
 *
 * @param filename path of the data file in file system
 * @param size of the data
 *
 * @return a pointer to the allocated data buffer + fill size
 *         with data size that can be different from file_size
 *         embedded in header in case padding was added: the
 *         data file must be 16bits size aligned to be
 *         downloaded via downloader.
 */
char * drv_arch_GetDataFromFile(char *filename, int *size);

/**
 * Set data in file.
 *
 * Data given as argument is prepended with a valid standard
 * Icera's header.
 *
 * File must be an entry of arch_type table.
 *
 * Only allowed for data files with NO_AUTH or EXT_AUTH level of
 * security.
 *
 * When file has EXT_AUTH level of security, on prod device,
 * security state must be EXT_AUTH_UNLOCKED.
 *
 * @param filename full path of file to create/update
 * @param buf a pointer to the data to write in file.
 * @param len len of data to write
 *
 * @return ArchError
 */
ArchError drv_arch_SetDataInFile(char *filename, uint8 *buf, int len);

int drv_arch_FlashWrite( tAppliFileHeader *arch_fh_ptr, uint8 *file_data_ptr, void (*FlashProgressCB)(int));

bool drv_arch_IsEnoughSpaceToWriteFile(uint32 arch_id, const uint32 file_size, char ** arch_file_path);

int drv_arch_HeaderVerify( tAppliFileHeader * appl_hd, tZipAppliFileHeader * zip_appl_hd );

uint32 drv_arch_GetLastSignatureWord( uint32 arch_id );

uint32 drv_arch_GetSignatureDigest( uint32 arch_id );

/**
 * Return ARCH_ID corresponding to a given file path.
 *
 * @param path
 *
 * @return ArchId id or -1 if path doesn't match with any known
 *         archive.
 */
ArchId drv_arch_GetIdByPath(char *path);

/**
 * Returns archive's path based on its arch ID.
 *
 * @param arch_id
 *
 * @return char*
 */
char *drv_arch_GetPathById(ArchId arch_id);

/**
 * Indicate if cal file is available in file system.
 * Check for either calibration_0.bin or calibration_1.bin
 * avaibility AND integrity
 *
 * @return int 1 if cal avail, 0 if not.
 */
int drv_arch_CalIsAvailable(void);

/**
 * Check if 1st file programming is allowed during firmnware update.
 *
 * For dev platform, and any config file, we allow this 1st
 * programming.
 * 1st programming is also allowed, through compilation flag,
 * for loader executed during a boot from external memory
 * source.
 *
 * @param arch_id
 * @return 1 if allowed, 0 if not
 */
int drv_arch_AllowedFirstFileProgramming(int arch_id);

/**
 * Perform key revocation mechanism.
 *
 * If the key index corresponding to the key ID of the file to
 * update is strictly lower than the key index corresponding to
 * the key ID of the same file currently in flash then loader
 * will forbid file update.
 *
 * @param arch_id archive ID (BT2/LDR/IFT/MODEM/CUSTCFG...).
 * @param upd_key_index key index of the file use for update.
 * @param krm_enabled to enable/disable key revocation
 *                    mechanism. A disable value is only taken
 *                    into account on a dev. Livanto chip.
 *
 * @return int 1 if OK, 0 if failure.
 */
int drv_arch_CheckUpdateKeyValidity( int arch_id, int upd_key_index, bool krm_enabled);

/**
 * Use key index in key tables (ICE_ICE, ICE_OEM, OEM_FACT) used
 * to sign the given archive to get the corresponding key index
 *
 * @param arch_id archive ID (BT2/LDR/IFT/MODEM/CUSTCFG...).
 * @param key_id 4 1st bytes of the public key used to generate
 *               file signature.
 *
 * @return int corresponding key index
 */
int drv_arch_GetKeyIndex(int arch_id, uint8 *key_id);

/**
 *  Read appli file header
 *
 *  @param fh allocated pointer to a tAppliFileHeader
 *  @param fd archive file descriptor set to the beginning of
 *            the archive header
 *
 *  1st read tag/length data, then fh->length. So read extended
 *  header if present.
 *  The file descriptor is not seek back to the beginning of the
 *  archive.
 *
 *  @return 0 if fail to read header correctly, 1 if success
 *
 */
int drv_arch_ReadHeader(tAppliFileHeader *fh, int fd);

/**
 * Get arch entry in arch_type[] table.
 *
 * @param arch_id archive ID read in archive header
 *
 * @return int entry in table
 */
int drv_archGetTableEntry(int arch_id);

/**
 * Read BT2 trailer in flash if exists
 *
 * @param bt2_ext_trailer
 *
 * @return ArchBt2HwplatCompat , if found, bt2_ext_trailer
 *         updated with found data.
 */
ArchBt2HwplatCompat drv_archGetBt2TrailerFromFlash(ArchBt2ExtTrailer *bt2_ext_trailer);

/**
 * Perform hardware platform compatibility check between a BT2 image in
 * RAM and BT2 image in flash if exists.
 *
 * @param arch_start buffer of BT2 data in RAM
 *
 * @return ArchBt2HwplatCompat
 */
ArchBt2HwplatCompat drv_archCheckBt2ExtendedTrailer(uint8 *arch_start);

/**
 * Create a file to store engineering mode passwd and reset
 * counter information in filesystem.
 *
 * @param passwd
 * @param length
 */
void drv_arch_EngineeringModeStorePasswdResetCounter(char *passwd, int16 length);

/**
 * Read (if exists) engineering mode file in filesystem and
 * authenticate its content.
 *
 * @return bool true if passwd is authenticated in filesystem.
 */
bool drv_arch_ReadAndCheckEngineeringModePasswd(void);

/**
 * Check a passwd against info stored in custom config file.
 *
 * @param passwd
 * @param length
 *
 * @return bool true if passwd matches.
 */
bool drv_arch_CheckEngineeringModePasswd(char *passwd, int16 length);

/**
 * Check counter retires of engineering mode passwd.
 *
 *
 * @return bool true if passwd matches.
 */
bool drv_arch_CheckEngineeringModeCounter(void);

/**
 * Remove stored passwd and reset counter retires of engineering
 * mode .
 *
 * @param setCounterMax: set counter to Max or to 0
 *
 * @return  - none
 */
void drv_arch_EngineeringModeRemovePasswdResetCounter(bool setCounterMax);

/**
 * Decrease counter retires of engineering mode passwd.
 *
 *
 * @return - false if max retries reached
 */
bool drv_arch_DecreaseEngineeringModeCounter(void);

/**
 * Build a data file header.
 *
 * @param data_len to fill file_size field, other sizes are
 *                 constants
 * @param file_header file header buffer
 * @param arch_id file arch id
 */
void drv_arch_BuildDataFileHeader(int data_len, tAppliFileHeader *file_header, int arch_id);

/**
 * Return handler to apply patch on archive.
 *
 * If file in arch_table is a patch then it should have a
 * corresponding patch handler used to update original archive.
 *
 * @param arch_id arch ID of the patch file.
 *
 * @return drv_archPatchHandler pointer to the patch handler.
 */
drv_archPatchHandler drv_arch_GetPatchHandler(ArchId arch_id);

/**
 * Handler used by loader to update SSL certificate.
 *
 * @param arch_hdr pointer to archive header
 * @param arch_start pointer to archive data
 *
 * @return int32
 */
int32 drv_arch_UpdateSslCert(tAppliFileHeader *arch_hdr, uint8 *arch_start);

/**
 * Handler for WebUi package update.
 *
 * @param arch_hdr pointer to archive header
 * @param arch_start pointer to archive data
 *
 * @return int32
 */
int32 drv_arch_UpdateWebUiPackage(tAppliFileHeader *arch_hdr, uint8 *arch_start);

/**
 * Turn an archive string acronym into an achive ID
 *
 * @param str pointer to a NULL delimited string containing an archive acronym (eg MDM, LDR)
 *
 * @return uint16
 */
ArchId drv_ArchIdFromAcronym(char* str);


/**
 * Store given arch ID in noninit.
 *
 * @param arch_id
 */
void drv_archSetRequiredModeToNoninit(ArchId arch_id);

/**
 * Return arch ID read from noninit.
 *
 *
 * @return ArchId value read from noninit or default modem arch
 *         ID.
 */
ArchId drv_archGetRequiredModeFromNoninit(void);

/**
 * Returns the temporary audio config filename to be used by the platform
 *
 * @return The filename of the temmporary audio file
 */
extern const char * drv_archGetTempAudioConfigFilename(void);

/**
 * Returns maximum available Archive ID
 *
 * @return maximum  ArchID
 */
uint32 drv_arch_GetMaxArchId(void);

/**
 * Returns Archive properties for a given Archive ID
 *
 * @return Archive properties struct pointer
 */
const tArchFileProperty *drv_archGetArchProperties(uint32 arch_id);
#endif /* #ifndef DRV_ARCH_H */

/** @} END OF FILE */
