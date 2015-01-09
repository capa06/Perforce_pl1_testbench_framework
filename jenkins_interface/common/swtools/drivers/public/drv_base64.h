/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_base64.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup Base64 Base64 encoder
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup Base64
 *
 * @{
 */

/**
 * @file drv_base64.h Base64 encoder API
 *
 */

#ifndef DRV_BASE64_H
#define DRV_BASE64_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <stdlib.h>

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

typedef enum DBG_Base64AlphabetTag
{
  BASE64_ALPHABET_NULL,
  BASE64_ALPHABET_BASIC,       /* Most common - See RFC 3548 */
  BASE64_ALPHABET_URLFILESAFE, /* Make URL and FILENAME handling safe - See RFC3548 */
  BASE64_ALPHABET_MODIFIED     /* Used in IMAP - See RFC 3501, RFC3548 */
}
DBG_Base64Alphabet;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Small and simple base64 encoder (RFC 4648) using standard
 * alphabet and in-place encoding.
 * The interface is the same as Base64EncodeBuffer but this
 * function doesn't provide the same flexibility. If this is
 * needed, base64.c/h should be included in this module.
 *
 * @param alphabet_unused
 * @param inbuf_ptr
 * @param inbuf_max_size
 * @param inbuf_bytes
 * @param outbuf_ptr
 * @param outbuf_max_size
 * @param generated_bytes_ptr
 */
void drv_Base64EncodeBuffer(DBG_Base64Alphabet const alphabet_unused,
                            uint8 *const inbuf_ptr,
                            uint32 const inbuf_max_size,
                            uint32 const inbuf_bytes,
                            uint8 *const outbuf_ptr,
                            uint32 const outbuf_max_size,
                            uint32 *const generated_bytes_ptr);

#endif

/** @} END OF FILE */

