/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_dld.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_dld.c Driver archive download protocol
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_arch.h"
#include "drv_arch_dld.h"
#include "os_uist_ids.h"
#include "os_abs.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include <string.h>
#include <stdlib.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

/* Error managment */
#define MAX_ERR_CNT             3

/* BLOCK layout related constants */
#define DLD_BLOCK_CHECKSUM_SZ   2
#define DLD_BLOCK_BLKSZ_SZ      2
#define DLD_BLOCK_HEADER_SZ     2

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/

enum
{
    DWL_LNK_FAILED      = -1,
    DWL_LNK_TERMINATED  = 0,
    DWL_LNK_FLAG_HUNT,
    DWL_LNK_FLAG_FOUND,
    DWL_LNK_ESTABLISH_ONGOING,
    DWL_LNK_ESTABLISHED,
};

/* Data mapping of BLOCK-0 */
typedef struct tagDldBlock0
{
    uint8               block_header[2];
    uint16              block_sz;
    tAppliFileHeader    dld_fh;
    uint16              block_checksum;
    uint16              pad;
}
DldBlock0;

/* Internal context */
typedef struct {
    bool               dld_initiated;
    bool               cb_registred;
    bool               src_connected;
    bool               dst_opened;
    DrvArchDldFileInfo *dld_file_info;

    /* Provided by caller */
    DrvArchDldCbs      *usr_cbs;
    void               *usr_cb_hdl;
} PrivDldHdl;

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/

/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/
DXP_CACHED_UNI1 const uint8 ack_msg[2] = { 0xaa, 0x01};    /* Block acknowledge */
DXP_CACHED_UNI1 const uint8 rej_msg[2] = { 0xaa, 0x09};    /* Block reject */

static DXP_CACHED_UNI1 PrivDldHdl    global_dld_ctx = { .dld_initiated = false, .cb_registred  = false,};

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/**
 * Open the data destination
 *
 * @param priv_dld_hdl          The current instance of the arch dld handle
 * @param remain_file_dld_bytes The max amount of bytes to download from file
 * @param file_desc             Pointer to a valid file description (i.e. a file header)
 */
static DrvArchDldErr DstOpen( PrivDldHdl *priv_dld_hdl, int remain_file_dld_bytes, tAppliFileHeader * file_desc )
{
    DrvArchDldErr err = DRV_ARCH_DLD_NO_ERROR;

    DEV_ASSERT(priv_dld_hdl->dst_opened == false);

    if(priv_dld_hdl->usr_cbs->dst_cbs->dst_open != NULL)
    {
        err = priv_dld_hdl->usr_cbs->dst_cbs->dst_open(priv_dld_hdl->usr_cb_hdl,
                                                       remain_file_dld_bytes,
                                                       file_desc);
    }
    if (err == DRV_ARCH_DLD_NO_ERROR) priv_dld_hdl->dst_opened = true;
    return err ;
}

/**
 * Close the data destination
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 */
static DrvArchDldErr DstClose( PrivDldHdl *priv_dld_hdl )
{
    DrvArchDldErr err = DRV_ARCH_DLD_NO_ERROR;

    if( (priv_dld_hdl->dst_opened == true) &&
        (priv_dld_hdl->usr_cbs->dst_cbs->dst_close != NULL))
    {
        err = priv_dld_hdl->usr_cbs->dst_cbs->dst_close(priv_dld_hdl->usr_cb_hdl);
    }
    priv_dld_hdl->dst_opened = false;
    return err ;
}

/**
 * Write data to the destination
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 * @param buffer       Pointer to the data buffer which holds the data to write
 * @param size         Maximum Number of bytes in the buffer
 * @param nb_write     Pointer to a variable which returns number of bytes written
 */
static DrvArchDldErr DstWriteData( PrivDldHdl *priv_dld_hdl, uint8 * buffer, uint16 size, uint32 * nb_write )
{
    DrvArchDldErr err;

    DEV_ASSERT(priv_dld_hdl->dst_opened == true);
    err = priv_dld_hdl->usr_cbs->dst_cbs->dst_write(priv_dld_hdl->usr_cb_hdl,
                                                    buffer,size,
                                                    nb_write);
    return err;
}

/**
 * Connect to the data source
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 *
 */
static DrvArchDldErr SrcConnect( PrivDldHdl *priv_dld_hdl)
{
    DrvArchDldErr err = DRV_ARCH_DLD_NO_ERROR;

    DEV_ASSERT(priv_dld_hdl->src_connected == false);

    if(priv_dld_hdl->usr_cbs->src_cbs->src_conn != NULL)
    {
        err = priv_dld_hdl->usr_cbs->src_cbs->src_conn(priv_dld_hdl->usr_cb_hdl);
    }

    if (err == DRV_ARCH_DLD_NO_ERROR)  priv_dld_hdl->src_connected = true;

    return err;
}

/**
 * Disconnect from the data source
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 *
 */
static DrvArchDldErr SrcDisconnect( PrivDldHdl *priv_dld_hdl)
{
    DrvArchDldErr err = DRV_ARCH_DLD_NO_ERROR;

    if( (priv_dld_hdl->src_connected == true) &&
        (priv_dld_hdl->usr_cbs->src_cbs->src_conn != NULL))
    {
        err = priv_dld_hdl->usr_cbs->src_cbs->src_disc(priv_dld_hdl->usr_cb_hdl);
    }
    priv_dld_hdl->src_connected = false;
    return err;
}

/**
 * Ask for a flow control
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 * @param fc           Flow control to be performed
 */
static void SrcFlowControl( PrivDldHdl* priv_dld_hdl, DrvArchDldSrcFc fc )
{
    DEV_ASSERT(fc < DRV_ARCH_DLD_SRC_FC_MAX_OP);
    DEV_ASSERT(priv_dld_hdl->src_connected == true);

    priv_dld_hdl->usr_cbs->src_cbs->src_fctr(priv_dld_hdl->usr_cb_hdl,fc);
}

/**
 * Send a data buffer
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 * @param msg          the data to send
 * @param msg_lg       length of data to send
 */
static void SrcSendMsg( PrivDldHdl *priv_dld_hdl, void * msg, int sz )
{
    uint32 numch;
    uint8 * src_ptr = (uint8 *)msg;

    DEV_ASSERT(priv_dld_hdl->src_connected == true);

    while (sz > 0)
    {
        priv_dld_hdl->usr_cbs->src_cbs->src_send(priv_dld_hdl->usr_cb_hdl,src_ptr, sz, &numch);
        sz -= numch;
        src_ptr += numch;
    }
}

/**
 * Receive 'cnt' bytes in to destination buffer.
 *
 * @param priv_dld_hdl The current instance of the arch dld handle
 * @param msg          the destination buffer.
 * @param sz           length of data to receive.
 */
static void SrcReceiveMsg( PrivDldHdl* priv_dld_hdl, void * msg, int sz )
{
    uint32 numch;
    uint8 * dest_ptr = (uint8 *)msg;

    DEV_ASSERT(priv_dld_hdl->src_connected == true);

    while (sz > 0)
    {
        priv_dld_hdl->usr_cbs->src_cbs->src_recv(priv_dld_hdl->usr_cb_hdl,dest_ptr, sz, &numch);
        sz -= numch;
        dest_ptr += numch;
    }
}

/**
 * Send block acknowledge to the other side.
 *
 * @param priv_dld_hdl The current instance of the arch dld handle.
 */
static void SrcSendCodeDwlAckMsg( PrivDldHdl* priv_dld_hdl )
{
    SrcSendMsg(priv_dld_hdl, (uint8*)&ack_msg[0], 2);
}

/**
 * Send download reject status to the other side.
 *
 * @param priv_dld_hdl The current instance of the arch dld handle.
 */
static void SrcSendCodeDwlRejMsg( void * priv_dld_hdl )
{
    SrcSendMsg(priv_dld_hdl, (uint8*)&rej_msg[0], 2);
}

/**
 * 16-bit checksum.
 *
 * @param p data pointer
 * @param lg data length
 */
static int ComputeChecksum( uint16 * buf_ptr, uint16 init_val, int lg )
{
    uint16 chksum = init_val;
    uint16 *end = buf_ptr + lg/2;

    while (buf_ptr < end)
    {
        chksum ^= *buf_ptr++;
    }

    return(int)chksum;
}

/** Retrieve the first available dld context (only one managed for the moment). */
static PrivDldHdl * DldCtxAlloc( void )
{
    PrivDldHdl *arch_dld_ctx = &global_dld_ctx;

    /* No malloc, only one ctx managed */
    DEV_ASSERT(arch_dld_ctx->cb_registred  == false);
    DEV_ASSERT(arch_dld_ctx->dld_initiated == false);
    return &global_dld_ctx;
}

static void DldCtxFree( PrivDldHdl *arch_dld_ctx )
{
    /* Not a real free because we have only one context in static */
    DEV_ASSERT(arch_dld_ctx ==  &global_dld_ctx);
    memset(arch_dld_ctx, 0, sizeof(PrivDldHdl));
}

static void DldTimerHandler(os_TimerHandle hdl, void *args)
{
    DEV_FAIL("Dld Timer expiracy !");
}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

DrvArchDldHdl drv_arch_DdlInit( DrvArchDldFileInfo *arch_dld_file_info, DrvArchDldCbs * usr_cbs, void * usr_cb_hdl )
{
    PrivDldHdl *priv_dld_hdl =  DldCtxAlloc();

    REL_ASSERT(priv_dld_hdl       != NULL);

    REL_ASSERT(arch_dld_file_info != NULL);
    memset(arch_dld_file_info, 0, sizeof(DrvArchDldFileInfo));
    priv_dld_hdl->dld_file_info = arch_dld_file_info;

    /* Consistency checks on caller cbs */
    REL_ASSERT(usr_cbs                     != NULL);
    REL_ASSERT(usr_cbs->src_cbs            != NULL);
    REL_ASSERT(usr_cbs->src_cbs->src_recv  != NULL);
    REL_ASSERT(usr_cbs->src_cbs->src_send  != NULL);
    REL_ASSERT(usr_cbs->src_cbs->src_fctr  != NULL);
    REL_ASSERT(usr_cbs->dst_cbs            != NULL);
    REL_ASSERT(usr_cbs->dst_cbs->dst_write != NULL);

    /* Registring caller cb related data */
    priv_dld_hdl->usr_cbs      = usr_cbs;
    priv_dld_hdl->usr_cb_hdl   = usr_cb_hdl;
    priv_dld_hdl->cb_registred = true;

    /* Init for our own houskeeping */
    priv_dld_hdl->dld_initiated = false;
    priv_dld_hdl->dst_opened    = false;
    priv_dld_hdl->src_connected = false;

    return (DrvArchDldHdl) priv_dld_hdl;
}

void drv_arch_DdlUninit( DrvArchDldHdl arch_dld_hdl )
{
    PrivDldHdl *priv_dld_hdl = (PrivDldHdl *) arch_dld_hdl;

    DEV_ASSERT(priv_dld_hdl->cb_registred  == true);
    DEV_ASSERT(priv_dld_hdl->dld_initiated == false);
    DEV_ASSERT(priv_dld_hdl->dst_opened    == false);
    DEV_ASSERT(priv_dld_hdl->src_connected == false);

    DldCtxFree(priv_dld_hdl);
}

int drv_arch_Download( DrvArchDldHdl arch_dld_hdl)
{
    PrivDldHdl *priv_dld_hdl = (PrivDldHdl *) arch_dld_hdl;
    tAppliFileHeader *dld_file_header = NULL;

    /* Machine state vars */
    int     state            =  DWL_LNK_FLAG_HUNT;
    int     error_credit_cnt  = MAX_ERR_CNT;
    int     error;

    /* Donwload protocol vars */
    uint16      dld_blk_sz =  0;
    int         dld_remain_file_sz = 0;
    uint8       dld_one_byte;
    DldBlock0   dld_block0;

    /* Tmp rx buf vars */
    uint8   *rx_buf       = NULL;
    int     rx_buf_sz   = 0;

    /* Misc */
    uint32  nb_write_dst = 0;

    REL_ASSERT(priv_dld_hdl                != NULL);
    DEV_ASSERT(priv_dld_hdl->cb_registred  == true);
    DEV_ASSERT(priv_dld_hdl->dld_initiated == false);

    priv_dld_hdl->dld_initiated = true;

    dld_file_header =  &(priv_dld_hdl->dld_file_info->dld_file_hdr);

    if (SrcConnect(priv_dld_hdl) != DRV_ARCH_DLD_NO_ERROR)
    {
        state = DWL_LNK_FAILED;
    }
    else
    {
        SrcFlowControl(priv_dld_hdl,DRV_ARCH_DLD_SRC_FC_XON);
    }

    os_TimerHandle timer_hdl = os_TimerCreateEx("archDldTimer");
    while ((state != DWL_LNK_FAILED) && (state != DWL_LNK_TERMINATED))
    {
        /* Start/Re-start a 12s timer */
        if (os_TimerIsRunning(timer_hdl))
        {
            os_TimerStop(timer_hdl);
        }
        os_TimerStart(timer_hdl,
                      DldTimerHandler,
                      NULL,
                      12000000,
                      0);
        switch (state)
        {

        case DWL_LNK_FLAG_HUNT:

            dld_one_byte = 0;
            while (dld_one_byte != 0xAA)
            {
                SrcReceiveMsg(priv_dld_hdl, &dld_one_byte, 1);
            }

            memset(&(dld_block0), 0, sizeof(dld_block0));
            dld_block0.block_header[0] = dld_one_byte;
            state = DWL_LNK_FLAG_FOUND;

            break;

        case  DWL_LNK_FLAG_FOUND:

            SrcReceiveMsg(priv_dld_hdl, &dld_one_byte, 1);

            if (dld_one_byte == 0x73)
            {
                dld_block0.block_header[1] = dld_one_byte;
                state = DWL_LNK_ESTABLISH_ONGOING;
            }
            else
            {
                /* BAD BLOCK-0 header -> restart download process */

                OS_UIST_SMARKER( DRVARCH_UIST_DLD_BLOCK0_REJECTED );

                if (--error_credit_cnt == 0)
                {
                    state = DWL_LNK_FAILED;
                }
                else
                {
                    state = DWL_LNK_FLAG_HUNT;
                }
            }

            break;

        case DWL_LNK_ESTABLISH_ONGOING:

            error = false;

            /* Wait for: block0 size + archive Tag end Length fields first */
            SrcReceiveMsg(priv_dld_hdl,
                        &(dld_block0.block_sz),
                        DLD_BLOCK_BLKSZ_SZ + SIZEOF_TLV_TAG + SIZEOF_TLV_LENGTH);

            /* Receive remaining data */
            SrcReceiveMsg(priv_dld_hdl,
                        &(dld_block0.dld_fh.file_size),
                        dld_block0.dld_fh.length - SIZEOF_TLV_TAG - SIZEOF_TLV_LENGTH);

            /* Copying downloaded file header in the file info struct */
            memcpy(dld_file_header,&(dld_block0.dld_fh),dld_block0.dld_fh.length);
            OS_UIST_SVALUE( DRVARCH_UIST_ID_ARCH_HEADER_LENGTH, dld_file_header->length);

            /* Receive BLOCK 0 checksum */
            SrcReceiveMsg(priv_dld_hdl, &(dld_block0.block_checksum), DLD_BLOCK_CHECKSUM_SZ);

            /* Verify BLOCK 0 consistency*/
            if ((ComputeChecksum((uint16*) &(dld_block0), 0, sizeof(dld_block0)) != 0) ||
                (drv_arch_HeaderVerify(dld_file_header,SKIP_ZIP_ARCH_CHECK) != 0))
            {
                /* BAD checksum or BAD archive header */
                OS_UIST_SMARKER( DRVARCH_UIST_DLD_BAD_CHECKSUM );
                error = true;
            }

            /* Open data destination.
             * Could take time if caller must mount a file system.
             * Disabling our own timer to let the caller manage his if he wants.
             */
            os_TimerStop(timer_hdl);
            if ( !error )
            {
                /* Report the file identifier we are going to download */
                OS_UIST_SVALUE( DRVARCH_UIST_DLD_FILE_ID, dld_file_header->file_id );

                /* RX buffer size then 16bits aligned
                 * Note: same modification done on host side when transmitting
                 */
                dld_remain_file_sz = dld_file_header->file_size;
                if ((dld_remain_file_sz % 2) != 0)
                {
                    dld_remain_file_sz +=1;
                }

                dld_blk_sz            = dld_block0.block_sz;

                if (DstOpen(priv_dld_hdl, dld_remain_file_sz, dld_file_header) == DRV_ARCH_DLD_NO_ERROR)
                {
                    /* Allocating memory to download the file */
                    rx_buf_sz    = dld_blk_sz + DLD_BLOCK_CHECKSUM_SZ;
                    rx_buf       = (uint8 *)malloc(rx_buf_sz);
                    REL_ASSERT(rx_buf != NULL);
                }
                else
                {
                    error = true;
                }
            }
            /* Start/Re-start a 12s timer */
            os_TimerStart(timer_hdl,
                          DldTimerHandler,
                          NULL,
                          12000000,
                          0);

            /* Send ACK or REJect */
            if(!error)
            {
                /* Send BLOCK 0 ACK */
                SrcSendCodeDwlAckMsg(priv_dld_hdl);
                /* reset error counter */
                error_credit_cnt = MAX_ERR_CNT;

                REL_ASSERT(rx_buf != NULL);
                OS_UIST_SVALUE( DRVARCH_UIST_DLD_BLK_START, (uint32)rx_buf);
                OS_UIST_SVALUE( DRVARCH_UIST_DLD_REMAIN_FILE_SIZE, dld_remain_file_sz);
                OS_UIST_SVALUE( DRVARCH_UIST_DLD_RX_BUFFER_SIZE, rx_buf_sz);
                state = DWL_LNK_ESTABLISHED;
            }
            else
            {
                OS_UIST_SMARKER( DRVARCH_UIST_DLD_BLOCK0_REJECTED );

                /* Send BLOCK 0 REJECT */
                SrcSendCodeDwlRejMsg(priv_dld_hdl);

                /* Update error counter */
                if (--error_credit_cnt == 0)
                {
                    state = DWL_LNK_FAILED;
                }
                else
                {
                    state = DWL_LNK_FLAG_HUNT;
                }
            }
            break;

        case DWL_LNK_ESTABLISHED:

            error = false;

            dld_blk_sz = dld_remain_file_sz > dld_blk_sz ? dld_blk_sz : dld_remain_file_sz;

            /* Wait for block header */
            uint16 blk_hdr = 0;
            DEV_ASSERT(sizeof(blk_hdr) == DLD_BLOCK_HEADER_SZ);
            SrcReceiveMsg(priv_dld_hdl, &blk_hdr, DLD_BLOCK_HEADER_SZ);

            /* Wait BLOCK-n data */
            int cnt = dld_blk_sz + DLD_BLOCK_CHECKSUM_SZ;
            REL_ASSERT( rx_buf != NULL );
            SrcReceiveMsg(priv_dld_hdl, rx_buf, cnt);

            /* Check BLOCK-n header (reception is big-endian!) */
            if (blk_hdr != (uint16)0x00AA)
            {
                state = DWL_LNK_FLAG_HUNT;
                error = true;
            }

            /* Check BLOCK-n checksum */
            if (!error && (ComputeChecksum((uint16 *)rx_buf, blk_hdr, cnt) != 0))
            {
                OS_UIST_SMARKER( DRVARCH_UIST_DLD_BAD_CHECKSUM );
                error = true;
            }

            if (!error)
            {
                if (DstWriteData(priv_dld_hdl,rx_buf,dld_blk_sz,&nb_write_dst) != DRV_ARCH_DLD_NO_ERROR)
                {
                    error = true;
                }
                REL_ASSERT(nb_write_dst == dld_blk_sz);
            }

            if (!error)
            {
                dld_remain_file_sz -= dld_blk_sz;
                /* Reset error counter */
                error_credit_cnt = MAX_ERR_CNT;

                /* End of file reached ? */
                if (dld_remain_file_sz <= 0)
                {
                    /* No more data to receive from src, forbiding src to send us something else */
                    SrcFlowControl(priv_dld_hdl,DRV_ARCH_DLD_SRC_FC_XOFF);
                    /* ACK the last block */
                    state = DWL_LNK_TERMINATED;
                }

                /* Send ACK BLOCK-n */
                SrcSendCodeDwlAckMsg(priv_dld_hdl);
            }
            else
            {
                /* ERROR managment */

                OS_UIST_SMARKER( DRVARCH_UIST_DLD_ERROR );

                /* Send REJECT BLOCK-n */
                SrcSendCodeDwlRejMsg(priv_dld_hdl);

                /* Try to send back bad block */
                SrcSendMsg(priv_dld_hdl, &blk_hdr, sizeof(blk_hdr));
                SrcSendMsg(priv_dld_hdl, rx_buf, cnt);

                if (--error_credit_cnt == 0)
                {
                    SrcFlowControl(priv_dld_hdl,DRV_ARCH_DLD_SRC_FC_XOFF);
                    state = DWL_LNK_FAILED;
                }
            }
            break;

        default:
            SrcFlowControl(priv_dld_hdl,DRV_ARCH_DLD_SRC_FC_XOFF);
            state = DWL_LNK_FAILED;
            break;
        }
    }
    os_TimerDelete(timer_hdl);

    /* Housekeeping */
    SrcDisconnect(priv_dld_hdl);
    DstClose(priv_dld_hdl);
    if(rx_buf        != NULL)
    {
        free(rx_buf);
        rx_buf = NULL;
    }

    priv_dld_hdl->dld_initiated = false;

    return state;
}
/** @} END OF FILE */
