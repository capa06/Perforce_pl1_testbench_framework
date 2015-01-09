/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_brom_iface.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_brom_iface.h BROM interface (exported functions and variables)
 *
 */

#ifndef DRV_BROM_IFACE_H
#define DRV_BROM_IFACE_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include "drv_security.h"

#include "bootROM_BootInfo.h"
#include "bootROM_Layout.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

#define BROM_NUM_RSA_KEYS_EXTERNAL  (1)
#define BROM_NUM_RSA_KEYS_INTERNAL  (8)
#define BROM_RSA_MODULUS_SIZE       (256)
#define BROM_RSA_EXPONENT_SIZE      (8)

#define BROM_NUM_RSA_KEYS ( ( drv_ChpcGetBootMode() == 0 ) ? BROM_NUM_RSA_KEYS_EXTERNAL : BROM_NUM_RSA_KEYS_INTERNAL )

#if !defined (HOST_TESTING)
#include "bootROM_ExportedDataLayout.h"
#endif

/** Extracted from BROM: magicNumbers.h */
#define BOOTROM_DRIVE_STRENGTH_USI_UART (6)

/* Extracted from bootROM source code in configurationWords_inlinecode.h
  used to extract external memory source information from config word */
#define CFGWORD_EXTMEMSRC_SHIFT        (3)
#define CFGWORD_EXTMEMSRC_MASK         (0x7)
#define CFGWORD_EXTMEMSRC(cfg_word) ((cfg_word >> CFGWORD_EXTMEMSRC_SHIFT) & CFGWORD_EXTMEMSRC_MASK)

/* Extracted from bootROM source code in configurationWords_inlinecode.h
  used to extract HSI config information from config word */
#define CFGWORD_HSICHANNEL_SHIFT       (11)
#define CFGWORD_HSICHANNEL_MASK        (0x7)

#define CFGWORD_HSICHANNELWIDTH_SHIFT  (14)
#define CFGWORD_HSICHANNELWIDTH_MASK   (0x3)

#define CFGWORD_HSIFRAMED_SHIFT        (16)
#define CFGWORD_HSIFRAMED_MASK         (0x1)

#define CFGWORD_HSIBREAK_SHIFT         (17)
#define CFGWORD_HSIBREAK_MASK          (0x1)

/* Macros to extract HSI config values from config word */
#define CFGWORD_HSICHANNEL(cfg_word) ((cfg_word >> CFGWORD_HSICHANNEL_SHIFT) & CFGWORD_HSICHANNEL_MASK)
#define CFGWORD_HSICHANNELWIDTH(cfg_word) ((cfg_word >> CFGWORD_HSICHANNELWIDTH_SHIFT) & CFGWORD_HSICHANNELWIDTH_MASK)
#define CFGWORD_HSICHANNELFRAMED(cfg_word) ((cfg_word >> CFGWORD_HSIFRAMED_SHIFT) & CFGWORD_HSIFRAMED_MASK)
#define CFGWORD_HSICHANNELBREAK(cfg_word) ((cfg_word >> CFGWORD_HSIBREAK_SHIFT) & CFGWORD_HSIBREAK_MASK)

/* Extracted from bootROM source code in configurationWords_inlinecode.h
  used to extract UART config information from config word */
#define CFGWORD_UARTID_SHIFT           (11)
#define CFGWORD_UARTID_MASK            (0x3)

#define CFGWORD_UARTBAUD_SHIFT         (13)
#define CFGWORD_UARTBAUD_MASK          (0x7)

#if defined (ICE9XXX_USI)
#define CFGWORD_UARTFCTRL_SHIFT        (19)
#endif
#define CFGWORD_UARTFCTRL_MASK         (0x1)

#define CFGWORD_UARTID(cfg_word)     ((cfg_word >> CFGWORD_UARTID_SHIFT) & CFGWORD_UARTID_MASK)
#define CFGWORD_UARTBAUD(cfg_word)   ((cfg_word >> CFGWORD_UARTBAUD_SHIFT) & CFGWORD_UARTBAUD_MASK)
#define CFGWORD_UARTFCTRL(cfg_word)  ((cfg_word >> CFGWORD_UARTFCTRL_SHIFT) & CFGWORD_UARTFCTRL_MASK)

/* Extracted from bootROM source code in configurationWords_inlinecode_ice9x.h
  used to extract USI config information from config word */
#define CFGWORD_USIID_SHIFT            (16)
#define CFGWORD_USIID_MASK             (0x1)

#define CFGWORD_PHYID_SHIFT            (17)
#define CFGWORD_PHYID_MASK             (0x3)

#define CFGWORD_UARTCLKDIV_SHIFT       (20)
#define CFGWORD_UARTCLKDIV_MASK        ((1 << (31 - CFGWORD_UARTCLKDIV_SHIFT + 1)) - 1)

#define CFGWORD_USIID(cfg_word)        ((cfg_word >> CFGWORD_USIID_SHIFT) & CFGWORD_USIID_MASK)
#define CFGWORD_USIPHYID(cfg_word)     ((cfg_word >> CFGWORD_PHYID_SHIFT) & CFGWORD_PHYID_MASK)
#define CFGWORD_UARTCLKDIV(cfg_word)   ((cfg_word >> CFGWORD_UARTCLKDIV_SHIFT) & CFGWORD_UARTCLKDIV_MASK)

/* Extracted from bootROM source code in configurationWords_inlinecode.h
  used to extract Soc Clock config information from config word */
#define CFGWORD_XTALFREQ_SHIFT         (0)
#define CFGWORD_XTALFREQ_MASK          (0x1)

#define CFGWORD_SOCBASEFREQ_SHIFT      (3)
#define CFGWORD_SOCBASEFREQ_MASK       (0x3)

#define CFGWORD_XTALFREQ(cfg_word) ((cfg_word >> CFGWORD_XTALFREQ_SHIFT) & CFGWORD_XTALFREQ_MASK)
#define CFGWORD_SOCBASEFREQ(cfg_word) ((cfg_word >> CFGWORD_SOCBASEFREQ_SHIFT) & CFGWORD_SOCBASEFREQ_MASK)


/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/* Boot ROM ID: The final 32-bytes of the ROM memory (0x8000BFE0-0x8000BFFF)    */
/* contain a boot-ROM version string.                                           */
extern const char * const bootRom_id_str;

/* Livanto security state / Depends on wether bRom ICE-ICE development keys
   are enabled or not */
typedef enum
{
    SECURITY_STATE__DEV,    /* At least one ice-ice dev key enabled */
    SECURITY_STATE__PROD    /* All ice-ice dev key disabled */
}
LivantoSecurityState;

/* Livanto production state / Depends on whether 2 1st bRom ICE-ICE prod keys
   are enabled or not */
typedef enum
{
    PRODUCTION_STATE_HIGH_END, /* All keys enabled */
    PRODUCTION_STATE_LOW_END   /* Key 2 & 3 disabled */
}
LivantoProductionState;

/* Extracted from bootROM source code in configurationWords.h
   Enumeration for the external memory source. This enumeration is a one-to-one mapping of the
   configuration word field to allow fast decoding of the configuration word (the configuration
   word field is 3-bits wide, all 8 values are covered here.
*/
typedef enum {
  CFGWORD_EXTMEMSRC_UART = 0,
  CFGWORD_EXTMEMSRC_NOR  = 1,
  CFGWORD_EXTMEMSRC_NAND = 2,
  CFGWORD_EXTMEMSRC_HSI  = 3,
  CFGWORD_EXTMEMSRC_SPI  = 4,

  /* The following values are undefined in the configuration word.
  */
  CFGWORD_EXTMEMSRC_UNKNOWN0 = 5,
  CFGWORD_EXTMEMSRC_UNKNOWN1 = 6,
  CFGWORD_EXTMEMSRC_UNKNOWN2 = 7
} BootRomExtMemSrc;


/* Extracted from bootROM source code in configurationWords.h
   Enumeration for the UART ID. This enumeration is a one-to-one mapping of the configuration
   word field to allow fast decoding of the configuration word (the configuration word field
   is 2-bits wide, all 4 values are covered here.
*/
typedef enum {
  CFGWORD_UARTID_0        = 0,
  CFGWORD_UARTID_1        = 1,
  CFGWORD_UARTID_2        = 2,
  CFGWORD_UARTID_DISCOVER = 3
} BootRomUARTID;

/* Extracted from bootROM source code in configurationWords.h
   Enumeration for the UART Baud rate. This enumeration is a one-to-one mapping of the
   configuration word field to allow fast decoding of the configuration word (the configuration
   word field is 3-bits wide, all 8 values are covered here.
*/
typedef enum {
  CFGWORD_UARTBAUD_38P4K   = 0,
  CFGWORD_UARTBAUD_115P2K  = 1,
  CFGWORD_UARTBAUD_230P4K  = 2,
  CFGWORD_UARTBAUD_460P8K  = 3,
  CFGWORD_UARTBAUD_912P6K  = 4,
  CFGWORD_UARTBAUD_1P8432M = 5,
  CFGWORD_UARTBAUD_3P6863M = 6,

  /* The following values are undefined in the configuration word.
  */
  CFGWORD_UARTBAUD_UNKNOWN = 7
} BootRomUARTBaud;

/* Extracted from bootROM source code in configurationWords.h
   Enumeration for UART hardware flow control. This enumeration is a one-to-one mapping of the
   configuration word field to allow fast decoding of the configuration word.
*/
typedef enum {
  CFGWORD_UARTFCTRL_DISABLED = 0,
  CFGWORD_UARTFCTRL_ENABLED = 1
} BootRomUARTFCtrl;

/* Extracted from bootROM source code in configurationWords.h
   Enumeration for the XTAL frequency. This enumeration is a one-to-one mapping of the
   configuration word field to allow fast decoding of the configuration word
   (the configuration word field is 3-bits wide, all 8 values are covered here).
*/
typedef enum {
  CFGWORD_XTALFREQ_26MHZ    = 0,
  CFGWORD_XTALFREQ_38P4MHZ  = 1,
} BootRomXTALFreq;

/* Extracted from bootROM source code in configurationWords.h
   The number of valid XTAL frequencies (this is used to size the XTAL lookup table).
*/
#define NUMBER_OF_CFGWORD_XTALFREQ (CFGWORD_XTALFREQ_38P4MHZ + 1)

/* Extracted from bootROM source code in configurationWords.h
   Enumeration for the SoC base frequency. This enumeration is a one-to-one mapping of the
   configuration word field to allow fast decoding of the configuration word
   (the configuration word field is 2-bits wide, all 4 values are covered here).
*/
typedef enum {
  CFGWORD_SOCBASEFREQ_80MHZ  = 0,
  CFGWORD_SOCBASEFREQ_100MHZ = 1,
  CFGWORD_SOCBASEFREQ_133MHZ = 2,
  CFGWORD_SOCBASEFREQ_166MHZ = 3
} BootRomSoCBaseFreq;

/* Extracted from bootROM source code in configurationWords.h
   The number of valid SoC frequencies (this is used to size the XTAL lookup table).
*/
#define NUMBER_OF_CFGWORD_SOCBASEFREQ (CFGWORD_SOCBASEFREQ_166MHZ + 1)

/* Extracted from bootROM source code in clockCfg.h
   Data structure to hold clock configuration for a given XTAL and SoC base frequency.
*/
typedef struct
{
  unsigned int pllR;
  unsigned int pllF;
  unsigned int pllClockOD;
  unsigned int socDivider;
} xtalt_ClockConfiguration;


/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

extern const uint8 brom_public_exponent_ext[BROM_NUM_RSA_KEYS_EXTERNAL][8];
extern const uint8 brom_rsa_modulus_ext[BROM_NUM_RSA_KEYS_EXTERNAL][RSA_MODULUS_SIZE];

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Read Livanto config word in order to know which memory source
 * has been used by bootROM for BT2 acquisition.
 *
 * @return BootRomExtMemSrc memory boot source info.
 */
static inline BootRomExtMemSrc brom_GetMemBootSource(bootROMt_BootInfo *bootInfo)
{
    return (BootRomExtMemSrc)CFGWORD_EXTMEMSRC(bootInfo->configWord);
}

/**
 * Return a pointer to DMEM bootRom boot info
 *
 * @return bootROMt_BootInfo*
 */
static inline bootROMt_BootInfo *brom_GetBootInfo(void)
{
    return (bootROMt_BootInfo *)BOOT_ROM_BOOT_INFO_START;
}


/**
 * Get Livanto chip production state from efuse.
 *
 * Either on a dev or prod device, check if all production keys are enabled.
 *
 * @return LivantoProductionState PRODUCTION_STATE_HIGH_END if all keys are enabled, PRODUCTION_STATE_LOW_END if not.
 */
LivantoProductionState brom_GetLivantoProductionState( void );

LivantoSecurityState brom_GetLivantoSecurityState( void );

extern uint32 brom_ReadEFUSEPLLBypass( void );

extern uint32 brom_ReadEFUSEAuthEnable( void );

extern uint32 brom_ReadEFUSERSAKeyDisable( void );

/**
 * Get pointer to BT2 keys modulus in BROM.
 *
 * @return uint8*
 */
extern uint8 *brom_GetBt2KeyModulus(void);

/**
 * Get pointer to BT2 keys exponent in BROM.
 *
 * @return uint8*
 */
extern uint8 *brom_GetBt2KeyExponent(void);

#endif /* #ifndef DRV_BROM_IFACE_H */

/** @} END OF FILE */
