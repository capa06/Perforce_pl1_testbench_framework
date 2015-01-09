/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2007
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_engineering.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_engineering.c To handle security around
 *       persistent engineering mode.
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/
#include "icera_global.h"

#include "drv_arch.h"
#include "drv_arch_local.h"
#include "asn1_api.h"
#include "drv_fs.h"
#include "drv_security.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/
#define MAX_ENG_PWD_RETRIES 10

/*************************************************************************************************
 * Private type definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Private function declarations (only used if absolutely necessary)
 ************************************************************************************************/

/*************************************************************************************************
 * Private variable definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public variable definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
void drv_arch_EngineeringModeStorePasswdResetCounter(char *passwd, int16 length)
{
    int32 fd, bytes_written;
    int16 counter;

    /* Open engineering mode file */
    fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_RDWR, 0);

    if(fd < 0)
    {
        /* file not found, create it */
        fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_CREAT | O_WRONLY | O_TRUNC, S_IREAD | S_IWRITE | S_IEXEC);
        DEV_ASSERT(fd >= 0);
    }

    /* Store passwd info length */
    bytes_written = drv_fs_Write(fd, &length, sizeof(int16));
    DEV_ASSERT(bytes_written == sizeof(int16));

    /* Store passwd */
    bytes_written = drv_fs_Write(fd, passwd, length);
    DEV_ASSERT(bytes_written == length);

    /* Reset counter retries of passwd */
    counter = MAX_ENG_PWD_RETRIES;
    bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
    DEV_ASSERT(bytes_written == sizeof(int16));

    drv_fs_Close(fd);

    return;
}

bool drv_arch_ReadAndCheckEngineeringModePasswd(void)
{
    bool ret = false;
    int32 fd, bytes_read;
    int16 len;
    char *passwd = NULL;

    do
    {
        /* Open engineering mode file */
        fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_RDONLY, 0);
        if(fd < 0)
        {
            break;
        }

        /* Get passwd length */
        bytes_read = drv_fs_Read(fd, &len, sizeof(int16));
        if(bytes_read != sizeof(int16))
        {
            drv_fs_Close(fd);
            break;
        }

        /* Get passwd */
        passwd = malloc(len);
        REL_ASSERT(passwd != NULL);
        bytes_read = drv_fs_Read(fd, passwd, len);
        if(bytes_read != len)
        {
            drv_fs_Close(fd);
            free(passwd);
            break;
        }

        /* Check passwd */
        if(drv_arch_CheckEngineeringModePasswd(passwd,len) == false)
        {
            drv_fs_Close(fd);
            free(passwd);
            break;
        }

        drv_fs_Close(fd);
        free(passwd);
        ret = true;
    } while(0);

    return ret;
}

bool drv_arch_CheckEngineeringModePasswd(char *passwd, int16 length)
{
    unsigned char i;
    unsigned char pwd_hash[SHA1_DIGEST_SIZE];
    unsigned char Engineering_Key[SHA1_DIGEST_SIZE];
    bool ret = false;
    unsigned char *passwd_copy = NULL;

    passwd_copy = malloc(length + SHA1_DIGEST_SIZE);
    REL_ASSERT(passwd_copy != NULL);
    memcpy(passwd_copy, (unsigned char *)passwd, length);

    /* Add salt to input */
    for (i = 0; i < SHA1_DIGEST_SIZE; i++)
    {
        passwd_copy[length++] = (unsigned char) salt1[i] ^ (unsigned char) salt2[i];
    }
    Sha1(pwd_hash, (unsigned char *) passwd_copy, length);

    cfg_GetEngineeringKey(Engineering_Key, SHA1_DIGEST_SIZE);

    if (!compare_SHA1_digest(pwd_hash, Engineering_Key))
    {
        ret = true;
    }

    free(passwd_copy);

    return ret;
}

bool drv_arch_CheckEngineeringModeCounter(void)
{
    int32 fd, bytes_read, bytes_written;
    int16 counter;
    int16 passLen;
    bool ret = false;

    do
    {
        /* Open engineering mode file */
        fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_RDONLY, 0);

        if(fd < 0)
        {
            /* file not found, then still no attempt */
            ret = true;
            break;
        }

        /* Get password length */
        bytes_read = drv_fs_Read(fd, &passLen, sizeof(int16));
        DEV_ASSERT(bytes_read == sizeof(int16));

        /* move position in file to passwd counter */
        DEV_ASSERT( drv_fs_Lseek(fd, passLen+sizeof(int16), SEEK_SET ) == passLen+sizeof(int16) );

        /* Get passwd counter retries */
        bytes_read = drv_fs_Read(fd, &counter, sizeof(int16));

        if(bytes_read == sizeof(int16))
        {
            if(counter > 0)
            {
                ret = true;
            }
        }
        else if(bytes_read == 0) /* to keep compatibility with old file structure */
        {
            counter = MAX_ENG_PWD_RETRIES;
            bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
            DEV_ASSERT(bytes_written == sizeof(int16));
            ret = true;
        }

    } while(0);

    if(fd >= 0)
    {
        drv_fs_Close(fd);
    }

    return ret;
}


void drv_arch_EngineeringModeRemovePasswdResetCounter(bool setCounterMax)
{
    int32 fd, bytes_written;
    int16 counter;
    int16 passLen;

    /*delete stored password */
    drv_fs_Remove(ENGINEERING_MODE_FILE);

    /* re-create engineering mode file */
    fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_CREAT | O_WRONLY | O_TRUNC, S_IREAD | S_IWRITE | S_IEXEC);
    DEV_ASSERT(fd >= 0);

    /* set passwd length to 0 */
    passLen = 0;
    bytes_written = drv_fs_Write(fd, &passLen, sizeof(int16));
    DEV_ASSERT(bytes_written == sizeof(int16));

    /* Reset counter retries of passwd */
    if(setCounterMax)
    {
        counter = MAX_ENG_PWD_RETRIES;
    }
    else
    {
        counter = 0;
    }

    bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
    DEV_ASSERT(bytes_written == sizeof(int16));

    drv_fs_Close(fd);
}

bool drv_arch_DecreaseEngineeringModeCounter(void)
{
    int32 fd, bytes_read, bytes_written;
    int16 counter = 0;
    int16 passLen = 0;
    bool ret = true;

    /* Open engineering mode file */
    fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_RDWR, 0);

    if(fd < 0)
    {
        /* file not found, create it */
        fd = drv_fs_Open(ENGINEERING_MODE_FILE, O_CREAT | O_WRONLY | O_TRUNC, S_IREAD | S_IWRITE | S_IEXEC);
        DEV_ASSERT(fd >= 0);

        counter = MAX_ENG_PWD_RETRIES;
        passLen = 0;

        bytes_written = drv_fs_Write(fd, &passLen, sizeof(int16));
        DEV_ASSERT(bytes_written == sizeof(int16));

        counter--;
        bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
        DEV_ASSERT(bytes_written == sizeof(int16));
    }
    else
    {
        /* Get password length */
        bytes_read = drv_fs_Read(fd, &passLen, sizeof(int16));
        DEV_ASSERT(bytes_read == sizeof(int16));

        /* move position in file to passwd counter */
        DEV_ASSERT( drv_fs_Lseek(fd, passLen+sizeof(int16), SEEK_SET ) == passLen+sizeof(int16));

        /* Get passwd counter retries */
        bytes_read = drv_fs_Read(fd, &counter, sizeof(int16));

        if(bytes_read == 0) /* to keep compatibility with old file structure */
        {
            counter = MAX_ENG_PWD_RETRIES;
            bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
            DEV_ASSERT(bytes_written == sizeof(int16));
        }

        if(counter >0)
        {
            /* move position in file to passwd counter */
            DEV_ASSERT( drv_fs_Lseek(fd, passLen+sizeof(int16), SEEK_SET ) == passLen+sizeof(int16));

            counter--;
            bytes_written = drv_fs_Write(fd, &counter, sizeof(int16));
            DEV_ASSERT(bytes_written == sizeof(int16));
        }
        if(!counter)
        {
            ret = false;
        }

    }

    drv_fs_Close(fd);

    return ret;
}


/** @} END OF FILE */
