/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_spiflash.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/********************************************************************
 * 
 * Brief:
 *        The spi flash memory library consists of a set of DXP 
 *        specific functions used to communicate with SPI Flash 
 *        memory devices via an FSI. 
 *        This library is not a Hardware-Abstraction-Layer. It is 
 *        concerned with the implementation of a communcation protocol 
 *        rather than 'banging registers'. 
 *        However, it does require use of the FSI MPHAL.
 *
 ********************************************************************/

/**
 * @defgroup SpiFlashDriver SPI Flash Driver
 * 
 * @{
 */

/**
 * @file drv_spiflash.h YAFFS interface to SPI FLASH including Serial Flash Memory Read/Write routines
 *
 * IMPORTANT NOTE FOR CUSTOMERS: this source code is EXTENDABLE. It means that:
 *                                                                                 
 *   - the original source code is FIXED and MUST NOT BE CHANGED FOR PRODUCTION DEVICES
 *   - the original source code can be extended provided that it                   
 *     does not affect the original source code                                 
 *   - any bug fix made to the original source code must be reported back to Icera
 */

#ifndef DRV_SPIFLASH_H
#define DRV_SPIFLASH_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/

#include <icera_global.h>
#include "mphal_fsi.h"
/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/

/* Bit position of the READY/WriteInProgress bit within the status register
   This bit is polled whenever a write is performed to detect the end of a
   write cycle.
*/
#define DRV_SPIFLASH_SR_RDY_BITPOS (0)


/* Bit position of the Write Enable Latch bit within the status register
   This bit is used to detect whether or not a WRITE ENABLE command has 
   succeeded.
*/
#define DRV_SPIFLASH_SR_WEL_BITPOS (1)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/* drv_spiflasht_Instruction
     The instruction opcodes used to communicate with the 
     SPI FLASH memory device.
     Provided here for information
*/
typedef enum {
  DRV_SPIFLASH_WREN = 0x06,
  DRV_SPIFLASH_WRDI = 0x04,
  DRV_SPIFLASH_RDSR = 0x05,
  DRV_SPIFLASH_READ = 0x03,
  DRV_SPIFLASH_PROGRAM = 0x02,

  /* Example instruction opcodes to be used with _Erase function
  */
  DRV_SPIFLASH_ATMEL_CHIP_ERASE = 0x62,
  DRV_SPIFLASH_STM_BULK_ERASE    = 0xc7,
    
  /* Example instruction opcodes to be used with _ReadID function
  */
  DRV_SPIFLASH_ATMEL_RDID = 0x15,
  DRV_SPIFLASH_STM_RDID    = 0x9f
} drv_spiflasht_Instruction;

/* drv_spiflasht_Handle
     Main handle
*/
typedef struct {
  /* Public fields
  */
  mphalfsit_Handle fsi; /* Exported to allow fine-tune configuration */
  
  /* Private fields - DO NOT TOUCH!
  */
  mphalfsit_Channel channel;
  mphalfsit_ChipSelect chipSelect;
} drv_spiflasht_Handle;


/**
 * Identifiers of SPI flash code/data segments
 */
enum drv_SpiFlashMapSegmentId
{
    DRV_SPIFLASH_MAP_SEGMENT_ID__BT2,                /** BT2 storage partition */
    DRV_SPIFLASH_MAP_SEGMENT_ID__PARTITION_1,        /** First VFS partition  */
    DRV_SPIFLASH_MAP_SEGMENT_ID__LAST
};

/**
 * SPI flash device type identifier 
 */
typedef enum 
{
    DRV_SPI_FLASH_DEVICE_TYPE__UNDEFINED = 0,
    DRV_SPI_FLASH_DEVICE_TYPE__NUMONYX_N25Q128,
    DRV_SPI_FLASH_DEVICE_TYPE__MAX
} drv_SpiFlashDeviceType;

/**
 * Board specific SPI Flash configuration details
 */
struct drv_SpiFlashConfiguration
{
    /* SPI Flash Device Type */
    drv_SpiFlashDeviceType          device;

    /* SPI FSI Setup */
    mphalfsit_FsiID             interface;
    mphalfsit_Channel           channel;
    mphalfsit_ChipSelect        chip_select;
};

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/

/**
 * Board specific SPI Flash configuration details (defined in appropriate drv_hwplat_flash.c)
 */
extern const struct drv_SpiFlashConfiguration hwplat_spi_flash_config;

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

/* spiflash_Open
   pre  : fsiID indicates which FSI instance the SPI Flash is attached to
          chipSelect specifies the chip-select used to select the SPI Flash
          channel specifies which of the FSI channels to use for communication
          with the SPI Flash.
          handle is non-initialised
   post : Returns NULL on failure.
          Otherwise, initialises and returns handle.
          The specified FSI instance / chip-select and channel are configured
          as so:
           
            o  Basic SPI protocol (see FSI functional spec)
            o  FSI acting as master
            o  Fixed arbitration mode
            o  32-bit transactions (basic data width)
            o  MSB first bit order
            o  SoC clock provides bit clock
            o  Clock divider is 32 (so SCK is 5MHz if SoC running at 166MHz)

  Note: Configuration changes may be applied using the public fsi handle using the FSI MPHAL.
        No configuration changes should be necessary, other than decreasing
        the clock divider to obtain a faster bit clock (SCK)

*/
drv_spiflasht_Handle *drv_spiflash_Open
  (mphalfsit_FsiID fsiID, mphalfsit_Channel channel, mphalfsit_ChipSelect chipSelect, 
   drv_spiflasht_Handle *handle);


/* spiflash_Close
   pre  : handle from spiflash_Open
   post : Connection to FSI closed. 
*/
void drv_piflash_Close(drv_spiflasht_Handle *handle);


/* spiflash_Read
   pre  : handle from spiflash_Open
          address specifies first byte address to be read
          numBytes specifies the number of bytes to be read
          buffer has enough capacity for numBytes worth of data
   post : Returns the number of bytes read into buffer (always <= numBytes).

   NOTES:
          The SPI flash is read using a number of SPIFLASH_READ instructions.
          This 'driver' does not use the xTE engines to drive the FSI FIFOs.

          The shortest READ transaction performed is 64-bits (32-bits for the READ
          instruction and 3-bytes of address + 32-bits of data).

          The maximum length of a read transaction depends on the FIFO DEPTH of the FSI.
          For example, an FSI with FIFO_DEPTH n will allow ((n - 1) * 4) bytes to be 
          read in each transaction. 
          Usually the FIFO DEPTH is 4, so each read will contain 12-bytes of data.
 
*/
int drv_spiflash_Read(drv_spiflasht_Handle *handle, unsigned int address, int numBytes, 
                                    unsigned char *buffer);


/* spiflash_Write
   pre  : handle from spiflash_Open
          address specifies the first byte address to write to
          numBytes gives the number of bytes to write ** AND numBytes MUST be a multiple of 4 **
          buffer contains data to be written.
   post : Returns the number of bytes written.
          The function returns once the final write-cycle is complete.

  NOTE: 
        This routine is sub-optimal and is only intended for verification purposes.
        The routine can only write 4-bytes at a time and does so by issuing a SPIFLASH_WREN instruction
        followed by a SPIFLASH_PROGRAM instruction.
 
*/
int drv_spiflash_Write(drv_spiflasht_Handle *handle, unsigned int address, int numBytes, 
                                     unsigned char *buffer);


/* spiflash_Erase
   pre  : handle from spiflash_Open
          eraseInstruction gives the 8-bit opcode to use as an erase instruction (it differs between
          devices). Use SPIFLASH_ATMEL_CHIP_ERASE for ATMEL devices.
          timeoutInSecs gives a timeout for returning from this function.
   post : The function returns either when the status-register indicates that the erase-cycle
          is over, or when the timeout exprires.
 
  NOTES: Erasing a SPI memory can take a very long time (10s of seconds)

*/
int drv_spiflash_Erase(drv_spiflasht_Handle *handle, unsigned char eraseInstruction, int timeoutInSecs);


/* spiflash_EraseSector
   pre  : handle from spiflash_Open
          eraseInstruction gives the 8-bit opcode to use as an erase sector instruction (it differs between
          devices).
          address gives the sector to erase's address
          timeoutInSecs gives a timeout for returning from this function.
   post : The function returns either when the status-register indicates that the erase-cycle
          is over, or when the timeout exprires.

*/
int drv_spiflash_EraseSector(drv_spiflasht_Handle *handle, unsigned char eraseInstruction, 
                                           unsigned int address, int timeoutInSecs);


/* spiflash_ReadStatus
   pre  : handle from spiflash_Open
   post : Transmits a SPIFLASH_RDSD instruction to the SPI flash are returns the 8-bit response
          (i.e. the value of the status register)
*/
unsigned char drv_spiflash_ReadStatus(drv_spiflasht_Handle *handle);


/* spiflash_ReadID
   pre  : handle from spiflash_Open
          readIDInstruction specifies the 8-bit RDID instruction to be used.
          Use SPIFLASH_ATMEL_RDID for ATMEL devices, SPIFLASH_ST_RDID for STM devices.
   post : returns 1st byte received from device 
          (normally the Manufacturer ID)

   NOTE: The manufacturer ID *must* be the first byte returned by the device on receiving 
         the RDID instruction. It is this first byte that is returned by the function.

*/
unsigned char drv_spiflash_ReadID(drv_spiflasht_Handle *handle, unsigned char readIDInstruction);


/* spiflash_WriteRegister
   pre  : handle from spiflash_Open
          addr contains the SPI Flash register to write to (->byte 0 of transfer)
          data contains the contents to write (->byte 1,2,3 of transfer)
   post : Provides write access for purposes of misc chip specific functions such as sector unlock/global chip 
          lock control.
          Returns 1 for success, else 0
*/
int drv_spiflash_WriteRegister(drv_spiflasht_Handle *handle, unsigned char addr, unsigned int data);

/**
 * Initialise SPI flash device access
 */
extern void drv_SpiFlashInitDevice(void);

/**
 * SPI Flash PM init
 *
 * This is where we register a post power down callback in
 * order to restore the state of the SPI Flash device
 */
extern void drv_SpiFlashPmInit(void);

/**
 * Read SPI flash memory.
 *
 * @param dest  Destination address where data is copied to
 * @param src   Source address (offset) to copy from
 * @param size  Size of the copy
 */
extern int drv_SpiFlashRead(void *dest, const void *src, int size);

/**
 * Write a buffer to SPI flash.
 *
 * @param dst  Write destination.
 * @param src  Write source.
 * @param size Write size.
 *
 * @return 1 if write ok, else 0.
 */
extern int drv_SpiFlashWrite(void *dst, const void *src, int size);

/**
 * Erase a memory area in SPI flash.
 *
 * WARNING: The erase granularity is 'sector'. The memory area to
 *          be erased is extended to fit one or more sectors.
 *
 * @param base  The base address of the memory area to be erased.
 * @param size  The size of the memory area to be erased.
 *
 * @return 1 if erase ok, else 0.
 */
extern int drv_SpiFlashEraseArea(void *base, int size);

/** 
 * Return full SPI Flash memory size.
 * 
 * 
 * @return int
 */
extern int drv_SpiFlashGetSize(void);

/**
 * Get the size of the sector pointed to by 'addr'.
 *
 * @param addr Address within a sector.
 *
 * @return The size of the sector.
 */
extern int drv_SpiFlashGetSectorSize(uint8 * addr);

/**
 * Get the address of a SPI flash segment.
 *
 * @param segment_id Identifier of the segment.
 *
 * @return The address of the SPI flash segment.
 */
extern uint8 *drv_SpiFlashGetSegmentAddress(enum drv_SpiFlashMapSegmentId segment_id);

/**
 * Get the size of a SPI flash segment.
 *
 * @param segment_id Identifier of the segment.
 *
 * @return The size of the NOR flash segment.
 */
extern uint32 drv_SpiFlashGetSegmentSize(enum drv_SpiFlashMapSegmentId segment_id);

/** 
 * Read in SPIFLASH_MAP_SEGMENT_ID__BT2 at a given offset a given len 
 * of bytes. 
 *  
 * Can be used to read entire BT2 file as soon as size is known.
 *  
 * Asserts no read attempt outside segment...
 * 
 * @param buf
 * @param offset
 * @param len
 */
extern void drv_SpiFlashReadBt2Data(uint8 *buf, int offset, int len);

/** 
 * Program BT2 application in SPI flash.
 * 
 * @param hdr_start
 * @param hdr_size
 * @param file_start
 * @param file_size
 * @param FlashProgressCB
 * 
 * @return int
 */
extern int drv_SpiFlashBt2prog(uint8 *hdr_start, 
                          int hdr_size, 
                          uint8 * file_start, 
                          int file_size,
                          void (*FlashProgressCB)(int));

/** 
 * Dump range of SPI flash memory. 
 *  
 *  MemDumpDataCB to perform dump data and use void dump_handle
 *  to be either a file descriptor, a serial handle, etc... So
 *  that dump_handle must point to an open file, an initialised
 *  host interface, etc...
 *  
 *  size bytes are dumped from offset offset.
 *  
 * @param MemDumpDataCB
 * @param dump_handle
 * @param offset
 * @param size
 * @param FlashProgressCB
 * @param FlashOutputCB
 * 
 * @return int
 */
extern int drv_SpiFlashDump(int (*MemDumpDataCB) (void *dump_handle, uint8 *data, int data_size),
                       void *dump_handle,
                       uint32 offset, 
                       uint32 size, 
                       void (*FlashProgressCB)(int, int),
                       void (*FlashOutputCB)(int, const char *str, ...));


#endif

/** @} END OF FILE */
