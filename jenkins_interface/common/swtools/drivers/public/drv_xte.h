/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2011
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xte.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup XteDriver XTE (DMA) Driver
 * @ingroup SoCLowLevelDrv
 * High level DMA driver complementing the functionality
 * provided by the mphal.
 */

/**
 * @addtogroup XteDriver
 * @{
 */

/**
 * @file drv_xte.h Public interface for driver specific xTE functions
 */

#ifndef DRV_XTE_H
#define DRV_XTE_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"

#if !defined (HOST_TESTING) || defined(HOST_TESTING_INC_DMA)
#include "livanto_memmap.h"

#include "context_cdefs.h"
#include "contextDescriptor_cdefs.h"
#include "livanto_config.h"
#else
#include "ht_stub.h"
#endif
#if !defined (HOST_TESTING) || defined(HOST_TESTING_INC_DMA)
#include "mphal_xte.h"
#endif
#include "drv_ipm.h"
#if !defined (HOST_TESTING) || defined(HOST_TESTING_INC_DMA)
#include <mphal_events.h>
#endif

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#define DRV_XTE_NO_CTXT_AVAIL_OR_NA (-1)

/* Number of XTE Mem Ctxts */
#define DRV_FDMA_CTXT_NUM_MEMCPY             (9)

#define DRV_SDMA_CTXT_HSI_BASE               (DRV_STE_CTXT_ID_HSI0)
#define DRV_SDMA_CTXT_NUM_HSI                (4)

/**
 * Descriptors and chains for MemCopy
 *   - 8 bit unsigned bytes per transfer rounded down to multiple of 32 for burst mode
 *   - 5 bit unsigned transfers per descriptor
 *
 *   - 8040 uses word mode 224*4*31 = 27776 bytes / desc
 */
#ifdef COM_UNFIXED_NVB_1154955_BPT
/* with the 9040 work-around we have 64(bpt)*31(tpd)*40 = 79360 bytes as the largest 
   writes.  For larger buffers we'll need more than this. Note that this is the theoretical
   maximum if the transfer size is modulo 64, for non modulo 64 transfer lengths, the
   descriptor allocation is non optimal, and the maximum size is reduced! */
#define DRV_XTE_NUM_DESC            (10 * 8)
#else
/* this can handle ((255*4) &~31) bpt * 31(tpd) * 20 = 614KBytes as a theoretical maximum.  */
#define DRV_XTE_NUM_DESC            (20)
#endif

/* Max blocks to transfer using drv_XteMultiBlockMemCopy */
#define MAX_XTE_MULTI_BLOCKS        (4)

/**
 * Macros for all hw syncs that are missing from a certain
 * toolchain livanto_config.h version
 */
#define DMA_REQ_EXT_SYNC_0          (116)
#define DMA_REQ_EXT_SYNC_1          (117)
#define DMA_REQ_EXT_SYNC_2          (118)
#define DMA_REQ_EXT_SYNC_3          (119)
#define DMA_REQ_EXT_SYNC_4          (120)
#define DMA_REQ_EXT_SYNC_5          (121)
#define DMA_REQ_EXT_SYNC_6          (122)
#define DMA_REQ_EXT_SYNC_7          (123)
#define DMA_REQ_EXT_SYNC_8          (124)
#define DMA_REQ_EXT_SYNC_9          (125)

#define XTE_LINK_VALID              BIT(0)
#define XTE_WAIT_SIC                BIT(1)
#define XTE_LINK_ADDR_MASK          (~(XTE_LINK_VALID | XTE_WAIT_SIC))

#define XTE_WAITING_SIC             BIT(4)

#define MAX_TPD_MODE0_SZ            ((1<<CTXTDESC_MODE0_TPD_SIZE)-1)
#define MAX_TPD_MODE1_SZ            ((1<<CTXTDESC_MODE1_TPD_SIZE)-1)

#define XTE_DBG_GLOBALS_BIT         (0)
#define XTE_DBG_GLOBAL_DEBUG_BIT    (1)
#define XTE_DBG_CONTEXT_BIT         (2)

/* for 9xxx the livanto_cofig is auto generated so these are not included. */
#define XTE_CONTEXT_STRIDE        0x20
#define XTE_C_2_DELAY             1
#define XTE_DXP_DMA               1
#define XTE_DXP_DEBUG             1
#define XTE_N_CONTEXTS            SDMA_N_CONTEXTS /* SDMA has the most contexts */
#define XTE_N_ENCODED_REQS        0x1f
#define XTE_REQUEST_DECODE        1

/* XTE_N_FLOWS 0x6 */

/* 9xxx: SDMA flow ID allocations.
         Manually assigned to seperate various high priority flows from others.
         Use SDMA_FLOW_ID_GENERAL if in doubt.
 */
#define SDMA_FLOW_ID_RF_TX        MPHALXTE_CONFIG__SDMA_FLOWID_GEN0
#define SDMA_FLOW_ID_RF_RX        MPHALXTE_CONFIG__SDMA_FLOWID_GEN1
#define SDMA_FLOW_ID_GENERAL      MPHALXTE_CONFIG__SDMA_FLOWID_GEN2
#define SDMA_FLOW_ID_APM_HLP      MPHALXTE_CONFIG__SDMA_FLOWID_GEN3


/** Numer of DMA memcpy contexts per DXP */
    #define DRV_XTE_MEMCPY_CTXS_DXP0       (4)
    #define DRV_XTE_MEMCPY_CTXS_DXP1       (4)
    #define DRV_XTE_MEMCPY_CTXS_DXP2       (2)

#if ICERA_SDK_EV_AT_LEAST(4,12,'a')
#define drv_xte_ENCODE_DESCR_LINK(addr) mphalxte_EncodeDescrLink((mphalxtet_Descriptor*)addr, MPHALXTE_LINK__WAIT_SIC_OFF) 
#elif ICERA_SDK_EV_AT_LEAST(4,11,'a')
#define drv_xte_ENCODE_DESCR_LINK(addr) mphalxte_ENCODE_DESCR_LINK((unsigned int*)addr) 
#else
#define drv_xte_ENCODE_DESCR_LINK(addr) mphalxte_ENCODE_DESCR_LINK((tXteDescriptor*)addr) 
#endif

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * DTE Context IDs, in priority order, highest priority at the top of the list.
 */
typedef enum
{
    DRV_FDMA_CTXT_ID_ICELINK0 = 0,             /* IceLink Contexts. Highest priority. */
    DRV_FDMA_CTXT_ID_ICELINK1,
    DRV_FDMA_CTXT_ID_ICELINK2,
    DRV_FDMA_CTXT_ID_ICELINK3,
    DRV_FDMA_CTXT_ID_ICELINK4,
    DRV_FDMA_CTXT_ID_ICELINK5,

    DRV_FDMA_CTXT_NUM                          /* Number of contexts used. */
} drv_XteFdmaLogicalContextIds;

/**
 * STE Context IDs, in priority order, highest priority at the top of the list.
 */
typedef enum
{
/* DXP#0 Contexts */
    DRV_SDMA_CTXT_ID_HRL0,                     /* HRL context used by APM */

    DRV_SDMA_CTXT_ID_USI_READ_CMD,             /* RF driver FSI contexts. */
    DRV_SDMA_CTXT_ID_USI_READ_RSP,
    DRV_SDMA_CTXT_ID_USI_CELL0_DIRECT,
    DRV_SDMA_CTXT_ID_USI_CELL0_HRL,
    DRV_SDMA_CTXT_ID_USI_CELL1_DIRECT,
    DRV_SDMA_CTXT_ID_USI_CELL1_HRL,
    DRV_SDMA_CTXT_ID_USI_MRFFE2,

    DRV_SDMA_CTXT_ID_IQ_DUMP_TX,
    DRV_SDMA_CTXT_ID_IQ_DUMP_RX,
    DRV_SDMA_CTXT_ID_UMCO,
    
    DRV_SDMA_CTXT_ID_HLP0,                    /* HLP (GUT) contexts */
    DRV_SDMA_CTXT_ID_HLP1,
    DRV_SDMA_CTXT_ID_HLP2,
    DRV_SDMA_CTXT_ID_HLP3,

/* DXP#1 Contexts */
    DRV_SDMA_CTXT_ID_AUDIORX,
    DRV_SDMA_CTXT_ID_AUDIOTX,
    DRV_SDMA_CTXT_ID_2ND_AUDIORX,
    DRV_SDMA_CTXT_ID_2ND_AUDIOTX,

    DRV_SDMA_CTXT_ID_UART_CTX0,               /* UART Contexts */
    DRV_SDMA_CTXT_ID_UART_CTX1,
    DRV_SDMA_CTXT_ID_UART_CTX2,
    DRV_SDMA_CTXT_ID_UART_CTX3,
    DRV_SDMA_CTXT_ID_UART_CTX4,
    DRV_SDMA_CTXT_ID_UART_CTX5,

    DRV_SDMA_CTXT_ID_SERIAL_SPI_TX,            /* Serial SPI Contexts */
    DRV_SDMA_CTXT_ID_SERIAL_SPI_RX,

    DRV_SDMA_CTXT_ID_LIVANTO_NATIVE_SDC0_DDP, /* Native SDC Contexts */
    DRV_SDMA_CTXT_ID_LIVANTO_NATIVE_SDC1_DDP,

    DRV_SDMA_CTXT_ID_NWGEN,  /* Used by nwgen to fill packet payloads */

    DRV_SDMA_CTXT_NUM
} drv_XteSdmaLogicalContextIds;
/**
 * Union of the STE and DTE context ID enums.
 */
typedef union
{
    drv_XteFdmaLogicalContextIds fdma;
    drv_XteSdmaLogicalContextIds sdma;
} drv_XteLogicalContextIds;

/**
 * xTE Overlay
 */
typedef enum
{
    DRV_XTE_OVERLAY_NONE = 0,  /**< No overlay. */
    DRV_XTE_OVERLAY_2G,        /**< 2G overlay. */
    DRV_XTE_OVERLAY_3G,        /**< 3G overlay. */
    DRV_XTE_OVERLAY_LTE        /**< LTE overlay */
} drv_XteOverlayId;

/**
 * xTE Instance, allows the driver to support STE and DTE operations from the same function
 * calls.
 */
typedef enum
{
    DRV_XTE_FDMA,               /**< FDMA. */
    DRV_XTE_SDMA,               /**< SDMA. */
    DRV_XTE_INSTANCES,         /**< Number of xTE instances in the system. */
    DRV_XTE_INSTANCES_NA,      /**< To indicate that instance param is not applicable  */
} drv_XteInstance;

/**
 * Memory segment
 */
typedef enum
{
    DRV_XTE_MEM_EXTERNAL,      /**< External Memory. */
    DRV_XTE_MEM_INT_COMMON,    /**< Internal Memory (Common). */
    DRV_XTE_MEM_INT_OVERLAY,   /**< Internal Memory (Overlay). */
    DRV_XTE_MEM_SEGMENT_NB     /**< Number of memory segments. */
} drv_XteMemSegment;

/**
 * XDMA block transfer flow types
 */
typedef enum
{
    DRV_XTE_BLOCK_XFER_NORMAL, 
    DRV_XTE_BLOCK_XFER_COMPRESS,
    DRV_XTE_BLOCK_XFER_DECOMPRESS
} drv_XteBlockTransferType;

/**
 * Memcpy priority level for drv_XteAssignMemcpyCtxPriority (DXP0 & 2 only)
 */
typedef enum
{
  DRV_XTE_MEMCPY_PRIORITY_HIGHEST = 0,
  DRV_XTE_MEMCPY_PRIORITY_0 = DRV_XTE_MEMCPY_PRIORITY_HIGHEST,
  DRV_XTE_MEMCPY_PRIORITY_1,
  DRV_XTE_MEMCPY_PRIORITY_2,
  DRV_XTE_MEMCPY_PRIORITY_3,
  DRV_XTE_MEMCPY_PRIORITY_4,
  DRV_XTE_MEMCPY_PRIORITY_5,
  DRV_XTE_MEMCPY_PRIORITY_LOWEST = DRV_XTE_MEMCPY_PRIORITY_5
} drv_XteMemcpyPriority;

/**
 * XTE MemCopy API callback completion API
 */
typedef void (*drv_XteMemCompletionCB)(void *user_arg);

/**
 * XTE Descriptor.
 * Must be 16 byte aligned
 */
typedef struct
{
    volatile uint32 dma_src_addr;       /**< Source address. */
    volatile uint32 dma_dst_addr;       /**< Destination address. */
    volatile uint32 dma_desc_ctrl;      /**< Descriptor control word. */
    volatile uint32 dma_link;           /**< DMA link address. */
} DXP_A128 tXteDescriptor;

/**
 * XTE descriptor chain
 */
typedef struct
{
    tXteDescriptor *first_desc;/**< Pointer to first descriptor in chain. */
    tXteDescriptor *last_desc; /**< Pointer to last descriptor in chain. */
} tXteDescriptorChain;


/**
 * (9xxx) XTE context register set (32-byte stride)
 */
typedef struct
{
    uint32 dma_reg_ctrl;       /**< Control register. */
    uint32 dma_reg_link_addr;  /**< Link address register. */
    uint32 dma_reg_desc_addr;  /**< Desc register. */
    uint32 dma_reg_byte_count; /**< Byte count register. */
    uint32 dma_reg_reread_link;/**< Force a reread of the last link address for appends */
    uint32 dma_reg_unused1;     /**< Unused register loation,
                                *   needed for padding to 32-byte stridge. */
    uint32 dma_reg_unused2;
    uint32 dma_reg_unused3;
} tXteCtxRegisterSet;


/**
 * XTE Memcopy descriptor chain data.
 */
typedef struct
{
    void       * dest_ptr;
    const void * src_ptr;
    uint32       buffer_size;
} drv_XteMemCopyChain;

/**
 * XTE context specfic handles
 */
typedef struct
{
    void *thrHForContext;                 /**< Handle for this context. */
    int  *thrForContext_queue_overflow;   /**< Set to true if we've run out of space */
    void (*dma_complete_cb)(void *);      /**< This callback must be limited to a thread
                                           *   wakeup call eg. os_QueuePutElement or os_EventSet
                                           */
    tXteDescriptorChain CurrentChain;     /**< 9xxx can perform multiple appends. */
    uint32     volatile *thrInactive;     /**< Pointer to thread inactive indicator for this
                                           *   context.
                                           */
} drv_XteCtxt;

/**
 * XTE handle.
 * We are pointing to the array of contexts so that they can be
 * DXP_CACHED_UNI0 or DXP_CACHED_UNI1 otherwise this qualifier
 * needs to be set in this structure and we'd need two othwise
 * equal structures.
 */
/* 9xxx */
typedef struct
{
    dxpnkt_Handle             *nkH;                  /**< Pointer to the NanoK instance */
    int const                 dxp_instance;          /**< Should not be needed */
    drv_XteInstance const     xte_instance;          /**< Indicates whether handle is for
                                                      *   FDMA or SDMA */
    uint32                    max_ctx_nb;
    uint32 const              intc_mask;             /**< Interrupt control register bit mask. */
    drv_IpmPcuHandle          ipm_pcu_handle;        /**< IPM handle */
    uint32                    ipm_crpc_modules[DRV_IPM_CRPC_MODULES_BANKS]; /**< IPM CRPC modules */
    drv_IpmPcuFuncs           ipm_funcs;             /**< IPM callbacks */
    char                      ipm_id_txt[5];         /**< DTE or STE0 or STE1 */

    /* Number of contexts for XTE instance */
    uint32                    context_mask;
    uint32                    initiated_dma_ctx;     /* shadow mask of currently used contexts */

    tXteCtxRegisterSet *const base_for_contexts; /**< Base address for contexts. */

    /* Context Specific Handles */
    drv_XteCtxt *const        context_ptr[XTE_N_CONTEXTS]; /**< Context pointer. */

} drv_Xte;

typedef void *drv_XteHdl;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/


/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/**
 * Logging function of the DMA descriptor chain in uncached memory.
 *
 * pre:
 * @param dxp_number to state which DXP desc chain to be logged.
 * @param desc_chain the descriptor chain to be logged.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Get the current timestamp for the requested DXP and point log DMA descriptor pointers to
 *      the right place.
 *   2. If a descriptor chain has been provided:
 *     a. Start at the first descriptor in the chain.
 *     b. Process all descriptors in the chain up to the log size limit.
 *     c. Extract descriptor information.
 *     d. Move to the next descriptor in the chain if there is one and the link to it is valid.
 *     e. If we have a continuous chain (ie. circular), stop when we find a descriptor which links
 *        back to the first descriptor in the chain.
 *   3. If there is no descriptor chain, we cannot do any logging.
 */
void drv_XteRecordDmaDesc(uint32 dxp_number,  tXteDescriptorChain *desc_chain);

/**
 * Wrapper around MPHAL to configure a descriptor control word
 * Serves 2 purposes:
 * 1. Hides toolchain verion variation making the code neater.
 * 2. And/ors out fields rather than just oring
 *
 */
extern uint32 drv_Xte_ENCODE_DESCR_CONFIG_BASICS(int srcInc,
                                                 int destInc,
                                                 int intEn,
                                                 int hwSync,
                                                 int flowId,
                                                 int pWidth,
                                                 int configMode);

#if defined (__dxp__)
/**
 * Wrapper around MPHAL to configure a descriptor control word
 * Serves 2 purposes:
 * 1. Hides toolchain verion variation making the code neater.
 * 2. And/ors out fields rather than just or'ing
 *
 */
extern uint32 drv_Xte_ENCODE_DESCR_CONFIG_TXSIZE_INFO(
                                         int config,
                                         int transfersPerDesc,
                                         int bytesPerTransfer,
                                         int configMode);
#endif

/**
 * Link two descriptor chains.
 * The two chains are only linked, not merged into a single chain. They will have to be
 * freed individually.
 *
 * pre:
 * @param chain1_ptr
 * @param chain2_ptr
 * @param force : Override last DMA link address (of chain1) if necessary
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. If the first chain is empty (ie. no descriptors), copy the first and last descriptor
 *      pointers from chain2 to chain1.
 *   2. Otherwise, if force == true or the link valid bit is not set in the last descriptor of
 *      chain1 (ie. end of chain and not continuous), link chain2 onto the end of chain1 and update
 *      the last descriptor pointer for chain1.
 *
 * @return void
 */
extern void drv_XteLinkChains(tXteDescriptorChain *chain1_ptr,
                              tXteDescriptorChain *chain2_ptr,
                              bool                 force);

/**
 * Link an additional descriptor to end of the descriptor chain.
 *
 * NOTE: The chain can be empty.
 * NOTE: Can only link to non-continuous chains.
 *
 * pre:
 * @param chain_ptr
 * @param desc_ptr
 * @param force : Override last dma link address (of chain) if necessary
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. If chain is empty, new descriptor becomes the first in the chain.
 *   2. If there is already a chain, and force == true or the chain is not continuous, link the
 *      new descriptor to the end of the chain and update the chain pointers appropriatley.
 *
 * @return void
 */
static inline DXP_FORCEINLINE void drv_XteAppendDescToChain(
                                       tXteDescriptorChain *chain_ptr,
                                       tXteDescriptor      *desc_ptr,
                                       bool                 force)
{
    /* 1. If chain is empty, new descriptor becomes the first in the chain. */
    if (NULL == chain_ptr->last_desc)
    {
        chain_ptr->first_desc = chain_ptr->last_desc = desc_ptr;
    }
    /* 2. If there is already a chain, and force == true or the chain is not continuous, link the
     *    new descriptor to the end of the chain and update the chain pointers appropriatley.
     */
    else
    {
        if (force || !(XTE_LINK_VALID & (chain_ptr->last_desc)->dma_link))
        {
            /* Can only link to non-continuous chains */
            uint32 link                             =  drv_xte_ENCODE_DESCR_LINK(desc_ptr);
            (chain_ptr->last_desc)->dma_link        = link;
            chain_ptr->last_desc                    = desc_ptr;
        }
    }
}

static inline DXP_FORCEINLINE void drv_XteAppendPausedDescToChain(
                                       tXteDescriptorChain *chain_ptr,
                                       tXteDescriptor      *desc_ptr)
{
    DEV_ASSERT(chain_ptr->last_desc != NULL);

    /* Can only link to non-continuous chains */
    uint32 link                             = ((uint32)desc_ptr) | XTE_LINK_VALID | XTE_WAIT_SIC;
    (chain_ptr->last_desc)->dma_link        = link;
    chain_ptr->last_desc                    = desc_ptr;
}

/**
 * Link additional descriptor to front of descriptor chain
 *
 * NOTE: The chain can be empty
 * NOTE: The chain must not be continuous (not checked).
 *
 * pre:
 * @param chain_ptr
 * @param desc_ptr
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. If the chain is curently empty, add the new descriptor as the start of the chain.
 *   2. Otherwise, link the new first descriptor to the old first descriptor and point the chain's
 *      first descriptor pointer to the new first descriptor.
 * @return void
 */
static inline DXP_FORCEINLINE void drv_XtePrependDescToChain(
                                       tXteDescriptorChain *chain_ptr,
                                       tXteDescriptor      *desc_ptr)
{
    /* 1. If there is no chain yet, simply add the new descriptor. */
    if (NULL == chain_ptr->first_desc)
    {
        chain_ptr->first_desc = chain_ptr->last_desc = desc_ptr;
    }
    /* 2. Link new first descriptor to old first descriptor, and link chain's first descriptor
     *    pointer to new first descriptor.
     */
    else
    {
        /* NOTE: Can only link to non-continuous chains */
        uint32 link           = drv_xte_ENCODE_DESCR_LINK(chain_ptr->first_desc);
        desc_ptr->dma_link    = link;
        chain_ptr->first_desc = desc_ptr;
    }
}

/**
 * XTE Driver Open
 * Create DEV thread, clean up and idle threads for driver if not already created
 *
 * pre:
 * @param nkH          : NanoK Handle
 * @param xte_instance : XTE instance
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Check that a handle to this xTE instance has not already been opened.
 *   2. If a NanoK handle has not been created yet, create one (3-7).
 *   3. Configure callback functions, thread names and interrupt handlers based on the requested
 *      xte_instance.
 *   4. If interrupts are required, set them up:
 *     a. Create a device thread for the xTE.
 *     b. Enable interrupts.
 *     c. Register transfer complete callback functions.
 *   5. Create the threads.
 *   6. Register for Idle Power Management.
 *   7. Initialise the overlay (DTE only).
 *
 * @return xte Driver Handle
 */
extern drv_XteHdl drv_XteOpen(dxpnkt_Handle *nkH, drv_XteInstance xte_instance);

/**
 * Query DTE or STE activity status for a specific context
 *
 * @return true the context is active.
 */
extern bool drv_XteContextActive(drv_XteInstance xte_instance, int ctxt_id);

/**
 * Query DTE or STE activity status for a specific context to determine if it is waiting for a SIC trigger.
 * It will set "link" to the link address of the currently loaded descriptor.
 *
 * @return true the context is waiting for a SIC.
 */
extern bool drv_XteSicWaiting(drv_XteInstance xte_instance, int ctxt_id, uint32 *link);

/**
 * Query DTE or STE as to whether a new descriptor chain can be appended to a particular context
 *
 * @return true if a new chain can be appended on the specified context.
 */
extern bool drv_XteContextAppendable(drv_XteInstance xte_instance, int ctxt_id);

/**
 * XTE Driver Close
 * Disable interrupts as threads cannot be destroyed
 * @param handle       : XTE Driver Handle
 * @return void
 */
extern void drv_XteClose(drv_XteHdl handle);

/**
 * Function to register a thread for a particular XTE context interrupt
 * The specified thread will be passed the completed context number as the msgQ message
 * on the registered thread when the XTE interrupt for the context fires.
 * @param handle  : xte driver handle
 * @param context : context number
 * @param thread  : Nanok thread for callback
 * @param overflow: Flag for msgQ overflow
 */
extern void drv_XteRegisterThread(drv_XteHdl           handle,
                                  int                  context,
                                  dxpnkt_ThreadHandle *thread,
                                  int                 *overflow);

/**
 * Function to pause/unpause a context in STE or DTE
 *
 * @param xte_instance : Specifies DTE or STE.
 * @param context      : Context to be (un)paused.
 * @param pause        : Set = 1 to pause context and 0 to unpause.
 * @return void
 */
extern void drv_XtePauseContext(drv_XteInstance xte_instance, int context, int pause);

/**
 * Function to set/clear the STE or DTE global pause bit.
 * NOTE: Intended for debug use only.
 *
 * @param xte_instance : Specifies DTE or STE.
 * @param pause        : Set = 1 to pause xTE and 0 to unpause.
 * @return void
 */
extern void drv_XtePause(drv_XteInstance xte_instance, int pause);

/**
 * Function to retrieve the XTE context id corresponding to a a logical context id.
 *
 * @param logical_context : DTE or STE logical context
 * @param xte_instance : Specifies DTE or STE.
 * @return DRV_XTE_INVALID_CTXT if no context available, otherwise the real allocated XTE context 
 * @see drv_XteDteContextIds
 * @see drv_XteSteContextIds
 */
extern int drv_XteGetAllocatedCtxt(drv_XteInstance xte_instance, int logical_context);

/**
 * Function to retrieve the maximum number of available XTE contexts (STE or DTE).
 *
 * @param xte_instance : Specifies DTE or STE.
 * @return the max number of DTE or STE real context
 */
extern int drv_XteGetNumRealCtx(drv_XteInstance xte_instance);


/**
 * Function to initiate a transfer on a specific context on an xTE instance.
 * The last descriptor should be interrogated to see if an interrupt is set to trigger on
 * completion and/or if it is a circular transfer. If it is not circular with no interrupt it
 * is the driver's resposibily to maintain if a context is active and should therefore append
 * the transfer with an extra descriptor marking the end of the transfer.
 *
 * pre:
 * @param handle             : xTE driver handle
 * @param dma_desc_chain_ptr : Descriptor chain to transfer
 * @param context            : Context to use
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Check that the requested context is not currently active.  If it is active, something bad
 *      has happened, so we pause the STE and the DTE at this point, to assist debugging.
 *   1. If this context is not already active, then clean up after the last transfer and start a
 *      new one.
 *     a. Append the "inactive descriptor" to the end of the chain, this will mark the chain as
 *        complete when it completes, by writing to thrInactive.
 *     b. Mark this context as ACTIVE.
 *     c. Initiate the transfer.
 *   2. If the context is already marked as ACTIVE, then we can append the new transfer.
 *     a. Update the last appended chain and check that the new chain exists.
 *     b. Check that there are no appended transfers already waiting in the DTE (can only have one
 *        appended transfer pending at a time, this is not checked by the MPHAL function).
 *     c. Append the transfer.
 *   3. xTE append feature is only available on 8040 platforms, so assert if we try to initiate a
 *      new transfer on a platform which is already active on 8020 platforms.
 *
 * @return success
 */
extern bool drv_XteInitiateTransfer(drv_XteHdl           handle,
                                    tXteDescriptorChain *dma_desc_chain_ptr,
                                    int                  context);

/**
 * As per above but start DMA transfer paused (waiting on SIC)
 */
extern bool drv_XteInitiateTransferPaused(drv_XteHdl           handle,
                                    tXteDescriptorChain *dma_desc_chain_ptr,
                                    int                  context);

/**
 * Function to kill a transfer on a specific context on a specific xTE instance and
 * release the context.
 *
 * pre:
 * @param handle      : xte driver handle
 * @param context     : context to use
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Kill the transfer.
 *   2. Clear the xTE transfer complete bit.
 *   3. Release the context by unhooking the chain pointer and marking it as inactive.
 * @return number of bytes that occured prior to transfer
 *         kill
 */
extern int drv_XteKillTransfer(drv_XteHdl handle, int context);

/**
 * Function to kill a transfer on a specific context on a specific xTE instance and
 * release the context, first of all sending a SW SIC trigger to release the context.
 *
 * pre:
 * @param handle      : xte driver handle
 * @param context     : context to use
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   0. Send SW SIC trigger.
 *   1. Kill the transfer.
 *   2. Clear the xTE transfer complete bit.
 *   3. Release the context by unhooking the chain pointer and marking it as inactive.
 * @return number of bytes that occured prior to transfer
 *         kill
 */
extern int drv_XteKillSicWaitingTransfer(drv_XteHdl handle, int context);

/**
 * Function to clear a transfer complete on a specific context 
 * on a specific xTE instance  
 *
 * pre:
 *
 * @param xte_instance: FDMA/SDMA 
 * @param dxp_instance: which DXP 
 * @param contextId     : context identifier to clear
 *
 * post:
 *   When invoked, this function clears the xTE transfer
 *   complete bit.
 * @return none
 */
void drv_XteClearCompletedTransfer(drv_XteInstance xte_instance, int dxp_instance, int contextId);

/**
 * Function to return the current byte count of a context on a specific xTE instance
 *
 * pre:
 * @param handle      : xTE driver handle
 * @param context     : context to use
 *
 * post:
 * @return int        : Current byte count
 */
extern int drv_XteByteCount(drv_XteHdl handle, int context);


/**
 * Function to trigger an overlay switch.
 *
 * pre:
 * @param overlayId : Overlay identifier
 * @param savePrevOvlyData: save data in the overlay for later restore
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Wait for any outstanding xTE memcpys to complete.  This is done without deschdeuling, as it
 *      shouldn't take too long because all of the memcpys are not hardware sync'd.
 *   2. Clear the completed DTE transfer settings, so it can be used again.
 *   3. Map the requested overlay.
 *   4. Update the active overlay ID.
 *
 * @return bool success
 */
extern int drv_XteOverlay(int overlayId, bool savePrevOvlyData);

/**
 * Function to perform pre-hibernate overlay save operations.
 * On 80xx, this may not perform any action.
 * On 9xxx, this function will save currently mapped overlays and should be called by each DXP.
 */
extern void drv_XteSaveOverlays(void);

/**
 * Save currently mapped overlays.
 * On 8xxx, this function is used to restore the bit of 3G IMEM that lives between the end of the
 * always-resident IMEM and the 8k boundary.
 * On 9xxx, this function will reload all previously mapped overlays and should be called by each DXP.
 */
extern void drv_XteLoadOverlays(void);

/**
 * Function to initiate a DMA memcpy.
 * On 80xx, this is limited to external to/from internal.
 * On 9xxx, there are no source / dest limits.
 */
extern int32 drv_DteMemCopy(void       *dest_ptr,
                            const void *src_ptr,
                            uint32      buffer_size);

/**
 * Function to terminate currently active DTE DMA.
 *
 * pre:
 * @param context_id : DTE Context to Kill.
 */
extern void drv_DteMemCopyKill(uint32 context_id);

/**
 * Function to check on completion status of DTE DMA
 * @param context_id : the DTE context ID to check for activity
 * @return success - if DTE memcpy is in progress
 */
extern bool drv_DteMemCopyIsActive(int32 context_id);

extern void drv_SteMemCopy(void   *dest_ptr,
                           void   *src_ptr,
                           uint32  buffer_size);

extern void drv_SteMemCopyKill(void);

/**
 * Allocate & setup a chained memcpy context for use with drv_XteChainedMemCopy.
 * This function can be called on 80xx but has no function (it won't allocate a context).
 * This allows a memcpy context to be permanently allocated for a specific user until 
 * drv_XteFreeChainedMemCopy releases it.
 *
 * pre:
 * @param descriptors  : [Optional / 9xxx only] User specified pool of descriptors. Can be NULL to use driver pool.
 * @param max_desc     : [Optional / 9xxx only] Size of 'descriptors' if specified.
 * @param completionCB : [Optional / 9xxx only] Callback function to be called on completion of transfer (uses PINT).
 * @param cb_arg       : [Optional / 9xxx only] Callback function argument.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Find a free XTE/XDMA context and remove it from the available pool of memcpy contexts.
 *   2. Return the memcpy context ID.
 *
 * @return context id or -1 if none available.
 */
extern int32 drv_XteAllocateChainedMemCopy(tXteDescriptor *       descriptors,
                                           int                    max_desc,
                                           drv_XteMemCompletionCB completionCB,
                                           void *                 cb_arg);


/**
 * Function to retrieve real hardware DMA context info from logical memcpy ctx number.
 * @param memcpy_context - context id or -1 if none available.
 * @return hardware DMA context ID (or -1 if failed)
 */
extern int32 drv_XteMemCopyCtxToRealCtx(int32 memcpy_context);

/**
 * Function to enable / disable memcpy logging
 * @param memcpy_context - context id
 */
extern void drv_XteEnableMemCopyLogging(int32 context_id, int enabled);

/**
 * Function to initiate a DMA memcpy. 
 * On 80xx, there are limitations as to the source/dest locations as well as which DXP this can 
 * be run from.
 * On 9xxx, there are no limitations to the source/dest locations or originating DXP.
 *
 * pre:
 * @param chain_ptr    : Pointer to an array containing descriptor chain source and destination
 *                       addresses.
 * @param chain_length : Number of elements in chain_ptr array.
 * @param context_id   : Memcpy context number allocated by drv_XteAllocateChainedMemCopy or -1 if
 *                       drv_XteChainedMemCopy should allocate a temp context itself.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Create a new DMA chain from information provided in chain_ptr and chain_length.
 *   2. If context_id is -1, find a free XTE/XDMA context.
 *   3. If the xTE driver is open on FDMA/DTE and we found a free context, initiate a memory copy.
 *   4. Return the context the memcopy was started on or -1 if unsuccesful.
 *
 * @return context id or -1 if memcpy is unsuccessful.
 */
extern int32 drv_XteChainedMemCopy(drv_XteMemCopyChain * chain_ptr,
                                   uint32                chain_length,
                                   int32                 context_id);

/**
 * Function to initiate a DMA memset.
 * On 80xx, there are limitations as to the source/dest locations as well as which DXP this can
 * be run from.
 * On 9xxx, there are no limitations to the source/dest locations or originating DXP.
 *
 * If the context allocated is already active, then the memset is appended to the end of the
 * current operation.
 *
 * pre:
 * @param chain_ptr    : Pointer to an array containing descriptor chain source and destination
 *                       addresses.
 * @param chain_length : Number of elements in chain_ptr array.
 * @param context_id   : Memcpy context number allocated by drv_XteAllocateChainedMemCopy or -1 if
 *                       drv_XteChainedMemCopy should allocate a temp context itself.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Create a new DMA chain from information provided in chain_ptr and chain_length.
 *   2. If context_id is -1, find a free XTE/XDMA context.
 *   3. If the xTE driver is open on FDMA/DTE and we found a free context, initiate a memory set.
 *   4. Return the context the memset was started on or -1 if unsuccessful.
 *
 * @return context id or -1 if memset is unsuccessful.
 */
extern int32 drv_XteChainedMemSet(drv_XteMemCopyChain * chain_ptr,
                                  uint32                chain_length,
                                  int32                 context_id);

/**
 * Function to append a new chain of MemCopies to an existing and already running MemCopy.
 * On 80xx, this can only be done once per call to drv_XteChainedMemCopy.
 * On 9xxx, this limitation does not exist (but there are a limited number of descriptors in the pool).
 *
 * pre:
 * @param chain_ptr    : Pointer to an array containing descriptor chain source and destination
 *                       addresses.
 * @param chain_length : Number of elements in chain_ptr array.
 * @param context_id   : ID of the DMA context to append to.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Create new DMA chain from provided information in chain_ptr and chain_length.
 *   2. Append new DMA chain using xTE hardware append feature.
 *   3. Return the context the memcopy was started on or -1 if unsuccesful.
 *
 * NOTE: The caller must ensure that there is never more than one outstanding appended transfer at
 *       any given time.  This function does not check if this restriction is violated.
 * @return context id or -1 if memcpy is unsuccessful.
 */
extern int32 drv_XteAppendMemCopy(drv_XteMemCopyChain * chain_ptr,
                                  uint32                chain_length,
                                  int32                 context_id);

/**
 * Function to free allocated chained DMA memcpy context.
 * This does nothing on 80xx.
 *
 * @param context_id   : Memcpy context number allocated by drv_XteAllocateChainedMemCopy
 * @return None
 */
extern void drv_XteFreeChainedMemCopy(int32 context_id);

/**
 * A compressing/decompressing memcpy with optional set on completion flag (must be uncached).
 * This function asserts on 80xx where it is not available.
 *
 * @param src_ptr            : Source buffer
 * @param dest_ptr           : Dest buffer
 * @param buffer_size        : Size of transfer (use uncompressed size)
 * @param compress           : Compress (true) or Decompress (false)
 * @param completion_flag    : [Optional] Pointer to flag which is set on DMA transfer completion
 * @return None
 */
extern int32 drv_XteCompressableMemCopy(void         *dest_ptr,
                                        const void   *src_ptr,
                                        uint32       buffer_size,
                                        bool         compress,
                                        bool         *completion_flag);


/**
 * A normal/compressing/decompressing memcpy which can transfer n blocks of the same size.
 * On 8xxx, only DRV_XTE_BLOCK_XFER_NORMAL is accepted as the selected flow_type.
 * If context_id is -1, a free context will be allocated, if not -1, DMA xfer will append.
 *
 * @param context_id         : Existing context ID (or -1)
 * @param src_ptr            : Source address array
 * @param dest_ptr           : Dest address array
 * @param blocks             : Number of blocks (entries in dest_ptr & src_ptr)
 * @param buffer_size        : Size of transfer (use uncompressed size)
 * @param flow_type          : Transfer type - DRV_XTE_BLOCK_XFER_NORMAL/COMPRESS/DECOMPRESS
 * @return DMA context ID or -1 if failure
 */
extern int32 drv_XteMultiBlockMemCopy(int32        context_id,
                                      uint8        *dest_ptr[MAX_XTE_MULTI_BLOCKS],
                                      uint8        *src_ptr[MAX_XTE_MULTI_BLOCKS],
                                      int          blocks,
                                      uint32       block_size,
                                      drv_XteBlockTransferType flow_type);


/**
 * Return available number of descriptors associated with any particular context?
 *
 * @param context_id         : DMA memcpy context ID
 * @return                     Number of available descriptors
 */
extern int drv_XteMemCopyFreeDescriptorCount(int32 context_id);

/**
 * Function to register a callback function for a specific XTE
 * context when a DMA transfer finished
 *
 * @param handle       : XTE handle
 * @param context      : XTE context (between 1 and 32)
 * @param complete_cb  : callback function to run once DMA tranfer ends
 * @param ctx_handle   : handle on the serial context (use drv_SerialGetEventHandle)
 * @return void
 *
 */
extern void drv_XteRegisterUserCB(drv_XteHdl  handle,
                                  int         context,
                                  void        (complete_cb)(void*),
                                  void       *ctx_handle);

/**
 * Function to change high/low priority assigned to contexts
 *
 * @param xte_instance : XTE instance
 * @param ctxs_to_hp   : bitmap - all contexts with '1' will be set to high priority
 * @param ctxs_to_lp   : bitmap - all contexts with '1' will be set to low priority
 * @return void
 *
 */
extern void drv_XteSetHighPriorityContexts(drv_XteInstance xte_instance,
                                           int             ctxs_to_hp,
                                           int             ctxs_to_lp);


/**
 * Perform a blocking memory copy using DTE 
 * (only on DXP0) 
 *  
 * dst and src should both be uncached and 32-bit 
 * aligned 
 *  
 * @param dst          : destination address 
 * @param src          : source address 
 * @param numBytes     : number of bytes to copy
 */
extern void drv_XteBlockingDTEMemcpy(void *          dst,
                                     void *          src,
                                     int             numBytes);

/**
 * Function to extract *an approximation of* the address of the start of the current block of
 * memory being read by the DMA.
 *
 * WARNING:  The information returned by this function is likely to be out of date, before this
 *           function returns, especially if small xTE descriptors are in use.
 *
 * WARNING:  Only minimal checking is performed on the supplied context, to ensure that an AFAULT
 *           will not occur when trying to read the specified descriptor, to obtain it's link
 *           address.  If the link address register contents are invalid, a memory AFAULT is likely
 *           to occur.
 *
 * pre:
 *   @prarm handle    : xTE handle
 *   @param context   : xTE Context to check.
 *
 * post:
 *   When invoked, this function performs the following actions:
 *   1. Read the context link address register associated with the supplied xTE handle.
 *   2. Use the information gathered in (1.) to extract information from the current DMA
 *      descriptor:
 *    a. Read the source address field.
 *    b. Read the link valid bit.
 *   3. If the link valid bit is set, then this descriptor is probably not one of the special extra
 *      descriptors used by the xTE driver to keep track of when DMAs complete.  If the link valid
 *      bit not set, we are at the end of a DMA chain, in the transfer complete descriptor, so we
 *      cannot return any meaningful information.
 *
 *   @return A pointer to the source address for the current DMA decriptor, or NULL if an error
 *           occurs.
 */
extern uint32 * drv_XteGetCurrentDescriptorReadPointer(
                                           drv_XteHdl *handle,
                                           int         context);


/**
 * Return active overlay ID: can be called only if IMEM is loaded
 */
extern int drv_XteActiveOverlay(void);

/**
 * Return active overlay ID 
 * @param DXP to retrieve active overlay of 
 * @param current overlay (see enum tOverlayId) 
 */
extern int drv_XteActiveOverlayExt(enum com_DxpInstance dxp_instance);

/**
 * This function returns the first DMA physical context ID for the current DXP.
 * No check is made as to whether this context is in-use or not.
 *
 * WARNING: ONLY FOR POST HIBERNATE PATH, NOT GENERAL USE!
 *
 * @param  dxp_instance    From which DXP instance's allocation
 * @return Physical first DMA context ID for this DXP
 *
 */
int32 drv_XteFirstRealContextId(int dxp_instance);

/**
 * Adjust memcpy context priorities (for DXP0 & DXP2 only).
 *
 * @param priorities - Array of priorities for this DXPs memcpy contexts where context 0 = highest, 5 = lowest
 * @param count - Number of priorities to change (should be the number of contexts on this DXP)
 */
extern void drv_XteAssignMemcpyCtxPriorities(drv_XteMemcpyPriority priorities[], int count);

/**
 * Retrieve Spurious DMA interrupt statistic . 
 *
 * @param handle 
 * @return spurious interrupt number since last cleared 
 */
extern uint32 drv_XteGetSpuriousCount(drv_XteHdl handle);

/**
 * Retrieve Total Spurious DMA interrupt statistic . 
 *
 * @param handle 
 * @return total spurious interrupt number since last cleared 
 */
extern uint32 drv_XteGetSpuriousTotalCount(drv_XteHdl handle);

/**
 * Retrieve numer of transferred byte in  current (or previous 
 * transfer)
 * @param handle 
 * @return number of bytes since last cleared 
 */
extern int drv_XteBytesTransferred(drv_XteHdl handle, int context);

#endif /* #ifndef DRV_XTE_H */

/** @} END OF FILE */
