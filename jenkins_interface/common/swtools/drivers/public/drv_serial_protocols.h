/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_serial_protocols.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @file drv_serial_protocols.h Protocol used on serial
 *       interface for file acquisition or coredump
 *       transmission.
 *
 */

#ifndef DRV_SERIAL_PROTOCOLS_H
#define DRV_SERIAL_PROTOCOLS_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_arch_type.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/** Protocols messages. */
#define SERIAL_MSG_START                (0xaa)
#define SERIAL_REQ_OPEN                 (0x7c) /** Different from REQOPEN sent by boot ROM which is 0x7f... */
#define SERIAL_RESP_OPEN                (0x73)
#define SERIAL_RESP_OPEN_EXT            (0x74) /** Extended RESPOPEN containg h/w plat config info */
#define SERIAL_RESP_OPEN_EXT_VER        (0x75) /** Extended RESPOPEN containg h/w plat config info
                                                * & transmitted app compatibility version number */
#define SERIAL_REQ_DEBUG                (0x7b)
#define SERIAL_REQ_DEBUG_ACCEPT         (0x61)
#define SERIAL_REQ_DEBUG_REJECT         (0x69)
#define SERIAL_REQ_DEBUG_SIZE           (0x76)
#define SERIAL_REQ_DEBUG_BLOCK          (0x02)
#define SERIAL_REQ_DEBUG_BLOCK_ACCEPT   (0x51)
#define SERIAL_REQ_DEBUG_BLOCK_REJECT   (0x59)
#define SERIAL_RESP_BLOCK               (0x00)
#define SERIAL_REQ_BLOCK_ACCEPT         (0x01)
#define SERIAL_REQ_BLOCK_REJECT         (0x09)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**  */
typedef enum
{
    SERIAL_16_BITS   /** */
    ,SERIAL_32_BITS  /** */
} SerialDataAlign;

/** Handle of used serial interface during file acquisition
 *  or coredump retreival */
typedef void SerialProtoHifHandle;

/** Callback for get and wait action used by acquisition or
 *  debug protocol */
typedef int (*SerialProtoHifGetAndWait)(SerialProtoHifHandle *handle, uint8 *buf, uint32 len);

/** Callback for put and wait action used by acquisition or
 *  debug protocol */
typedef int (*SerialProtoHifPutAndWait)(SerialProtoHifHandle *handle, uint8 *buf, uint32 len);

/** Callback for REQOPEN sending */
typedef int (*SerialProtoHifSendReqOpen)(SerialProtoHifHandle *handle);

/**
 *
 */
typedef struct
{
    SerialProtoHifHandle *hif;             /** */
    SerialProtoHifGetAndWait getAndWait;   /** */
    SerialProtoHifPutAndWait putAndWait;   /** */
    SerialProtoHifSendReqOpen sendReqOpen; /** */

    int maxConsecutiveFailures;           /** */
    int msg_offset;                       /** */
    int msg_size;                         /** */
    SerialDataAlign align;                /** */
} SerialProtoHandle;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Return the compatibilty version number shared between
 * applications and flash interface layer daemon.
 * Can be either a value stored in non init at boot time or a
 * value set in runi session with: set_ver_compat <value>
 * dxp-run command.
 *
 * @return uint32
 */
uint32 drv_SerialProtoGetCompatibilityVersion(void);

/**
 * Coredump transmission target protocol.
 *
 * Used to send on any given serial link the entire image of
 * external RAM.
 *
 *
 * @param hdl
 * @param accepted
 *
 * @return int
 */
int drv_SerialProtoDbgProtocol(SerialProtoHandle *hdl,
                               int *accepted);

/**
 * Application transmission protocol.
 *
 * @param hdl
 * @param arch_header
 * @param data_size
 * @param hash_digest
 * @param ver_compat
 * @param boot_buffer
 * @param boot_buffer_len
 * @param otf_computing compute sha (and inflate when required)
 *                      "on the fly" when each block is
 *                      received. Set 0 to do this extra
 *                      computing when the whole application has
 *                      been received: OTF computing disabled
 *                      when flow control problem is detected on
 *                      th eserial link.
 *
 * @return uint8*
 */
uint8 *drv_SerialProtoAcqProtocol(SerialProtoHandle *hdl,
                                  tAppliFileHeader *arch_header,
                                  uint32 *data_size,
                                  uint8 *hash_digest,
                                  uint32 *ver_compat,
                                  uint8 **boot_buffer,
                                  uint32 *boot_buffer_len,
                                  int otf_computing);

/**
 *
 *
 * @param hdl
 *
 * @return int
 */
int drv_SerialProtoHifDiscoverProtocol(SerialProtoHandle *hdl);

#endif /* #ifndef DRV_SERIAL_PROTOCOLS_H */

/** @} END OF FILE */

