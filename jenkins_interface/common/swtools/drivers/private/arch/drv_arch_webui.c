/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_webui.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_webui.c WebUi package update utilities
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_arch.h"
#include "drv_fs.h"
#include "unzip.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

#define READ_BUFFER_SIZE (16*1024)
#define MIN(a,b) ((a)<(b)?(a):(b))

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/

typedef struct
{
    uint8 *buffer;
    bool open;
    int fd;
    int offset;
    int size;
} RamfsContext;

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/

/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

static DXP_CACHED_UNI1 RamfsContext *ramfs_ctx_hdl;

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

static void ramfs_init(uint8 *base_addr, int size)
{
    ramfs_ctx_hdl = malloc(sizeof(RamfsContext));
    REL_ASSERT(ramfs_ctx_hdl != NULL);

    ramfs_ctx_hdl->fd = -1;
    ramfs_ctx_hdl->offset = 0;
    ramfs_ctx_hdl->open = 0;
    ramfs_ctx_hdl->size = size;

    if (base_addr)
    {
        ramfs_ctx_hdl->buffer = base_addr;
    }
    else
    {
        DEV_ASSERT(size);
        ramfs_ctx_hdl->buffer = malloc(size);
        REL_ASSERT(ramfs_ctx_hdl->buffer != NULL);
    }
}

static void ramfs_deinit(void)
{
    REL_ASSERT(ramfs_ctx_hdl != NULL);
    free(ramfs_ctx_hdl);
}

static voidpf ramfs_open(voidpf opaque, const char* filename, int mode)
{
    int *fd_p = malloc(sizeof(int));
    REL_ASSERT(fd_p != NULL);
    *fd_p = 1;

    DEV_ASSERT(ramfs_ctx_hdl->open == 0);
    ramfs_ctx_hdl->open = 1;
    ramfs_ctx_hdl->fd = 1;
    ramfs_ctx_hdl->offset = 0;

    return fd_p;
}

static uLong ramfs_read(voidpf opaque, voidpf stream, void* buf, uLong size)
{
    DEV_ASSERT(ramfs_ctx_hdl->open != 0);
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);
    DEV_ASSERT(ramfs_ctx_hdl->offset + size <= ramfs_ctx_hdl->size);

    memcpy(buf, ramfs_ctx_hdl->buffer + ramfs_ctx_hdl->offset, size);

    ramfs_ctx_hdl->offset += size;

    return size;
}

static uLong ramfs_write(voidpf opaque, voidpf stream, const void* buf, uLong size)
{
    DEV_ASSERT(ramfs_ctx_hdl->open != 0);
    DEV_ASSERT(ramfs_ctx_hdl->offset + size <= ramfs_ctx_hdl->size);
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);

    memcpy(ramfs_ctx_hdl->buffer + ramfs_ctx_hdl->offset, buf, size);
    ramfs_ctx_hdl->offset += size;

    return size;
}

static long ramfs_tell(voidpf opaque, voidpf stream)
{
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);
    return ramfs_ctx_hdl->offset;
}

static long ramfs_seek(voidpf opaque, voidpf stream, uLong offset, int origin)
{
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);

    switch (origin)
    {
    case SEEK_SET:
        ramfs_ctx_hdl->offset = offset;
        break;

    case SEEK_CUR:
        ramfs_ctx_hdl->offset += offset;
        break;

    case SEEK_END:
        ramfs_ctx_hdl->offset = ramfs_ctx_hdl->size - offset;
        break;

    default:
        DEV_ASSERT(0);
    }

    return 0;
}

static int ramfs_close(voidpf opaque, voidpf stream)
{
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);

    ramfs_ctx_hdl->open = 0;
    ramfs_ctx_hdl->fd = 0;
    ramfs_ctx_hdl->offset = 0;
    ramfs_ctx_hdl->size = 0;

    free(stream);

    return 0;
}

static int ramfs_error(voidpf opaque, voidpf stream)
{
    DEV_ASSERT(ramfs_ctx_hdl->fd != 0);

    return 0;
}

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

int32 drv_arch_UpdateWebUiPackage(tAppliFileHeader *arch_hdr, uint8 *arch_start)
{
    int res;

    zlib_filefunc_def zlib_filefunc_def;

    zlib_filefunc_def.zopen_file    = ramfs_open;
    zlib_filefunc_def.zread_file    = ramfs_read;
    zlib_filefunc_def.zwrite_file   = ramfs_write;
    zlib_filefunc_def.ztell_file    = ramfs_tell;
    zlib_filefunc_def.zseek_file    = ramfs_seek;
    zlib_filefunc_def.zclose_file   = ramfs_close;
    zlib_filefunc_def.zerror_file   = ramfs_error;
    zlib_filefunc_def.opaque        = NULL;

    ramfs_init(arch_start, arch_hdr->file_size);

    DEV_ASSERT(arch_hdr->file_id == ARCH_ID_WEBUI_PACKAGE);

    uint8 *read_buffer = malloc(READ_BUFFER_SIZE);
    REL_ASSERT(read_buffer != NULL);

    if (!drv_fs_DeviceIsMounted(DRV_FS_DEVICE_NAME_ZERO_CD))
    {
        res = drv_fs_Mount(DRV_FS_DIR_NAME_ZERO_CD, DRV_FS_DEVICE_NAME_ZERO_CD, drv_fs_GetFsName());
        DEV_ASSERT(res);
    }

    unzFile unzf = unzOpen2(NULL, &zlib_filefunc_def);
    REL_ASSERT(unzf != NULL);

    res = unzGoToFirstFile(unzf);
    DEV_ASSERT_EXTRA(res == UNZ_OK,1,res);

    drv_fs_RmDirRecursive(DRV_FS_WEBUI_DIR_NAME);
    do
    {
        unz_file_info current_file_info;
        char current_file_name[MAX_FILENAME_LENGTH];
        uint8 extra_field_buffer[MAX_FILENAME_LENGTH];
        char current_file_comment[MAX_FILENAME_LENGTH];
        char absolute_file_path[MAX_FILENAME_LENGTH];
        int is_dir_path = 0;

        res = unzGetCurrentFileInfo(unzf,
                         &current_file_info,
                         current_file_name,
                         sizeof(current_file_name),
                         extra_field_buffer,
                         sizeof(extra_field_buffer),
                         current_file_comment,
                         sizeof(current_file_comment));
        DEV_ASSERT_EXTRA(res == UNZ_OK, 1, res);

        res = snprintf(absolute_file_path, sizeof(absolute_file_path), "%s%s%s",
                       DRV_FS_WEBUI_DIR_NAME, DRV_FS_SEPARATOR, current_file_name);
        DEV_ASSERT_EXTRA(res < sizeof(absolute_file_path), 4, res, strlen(DRV_FS_WEBUI_DIR_NAME),
                         strlen(DRV_FS_SEPARATOR), strlen(current_file_name));

        char* filename = strrchr(absolute_file_path, *DRV_FS_SEPARATOR);
        if(*(filename + 1) == '\0')
        {
            /* It is a directory */
            is_dir_path = 1;
        }

        /* Ensure that folder tree is created */
        *filename = '\0';
        if (drv_fs_Mkdirs(absolute_file_path, S_IRWXU) != 0)
        {
            DEV_FAIL_EXTRA("mkdirs errno", 1, drv_fs_GetLastError(drv_fs_GetFsName()));
        }
        *filename = *DRV_FS_SEPARATOR;

        if (!is_dir_path)
        {
            /* Create unflatted file */
            int fd = drv_fs_Open(absolute_file_path, O_CREAT | O_WRONLY, S_IREAD | S_IWRITE);
            DEV_ASSERT(fd != -1);

            res = unzOpenCurrentFile(unzf);
            DEV_ASSERT_EXTRA(res == UNZ_OK, 1, res);

            int remaining_read_size = current_file_info.uncompressed_size;

            while (remaining_read_size)
            {
                int bytes_to_read = MIN(remaining_read_size, READ_BUFFER_SIZE);

                res = unzReadCurrentFile(unzf, read_buffer, bytes_to_read);
                DEV_ASSERT_EXTRA(res == bytes_to_read, 2, res, bytes_to_read );

                res = drv_fs_Write(fd, read_buffer, bytes_to_read);
                DEV_ASSERT(res == bytes_to_read);

                remaining_read_size -= bytes_to_read;
            }

            res = unzCloseCurrentFile(unzf);
            DEV_ASSERT_EXTRA(res == UNZ_OK, 1, res);

            res = drv_fs_Close(fd);
            DEV_ASSERT(res == 0);
        }

        res = unzGoToNextFile(unzf);
        DEV_ASSERT_EXTRA((res == UNZ_OK) || (res == UNZ_END_OF_LIST_OF_FILE), 1, res);
    }
    while (res != UNZ_END_OF_LIST_OF_FILE);

    free(read_buffer);

    res = unzClose(unzf);
    DEV_ASSERT_EXTRA(res == UNZ_OK,1,res);

    ramfs_deinit();

    return 0;
}

/** @} END OF FILE */

