/*************************************************************************************************
 * Icera Semiconductor
 * Copyright (c) 2005
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/private/arch/drv_arch_pubk.c#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @addtogroup ArchiveDriver
 * @{
 */

/**
 * @file drv_arch_pubk.c ICE_OEM  & OEM_FACT Public key
 *       repository.
 *
 * 2048-bit RSA public key for signature verification.
 *
 * Only RSA_KEY_TYPE__DEV information is stored here for each
 * ICE_OEM & OEM_FACT Public key.
 *
 * RSA_KEY_TYPE__PROD information is product dependent and must
 * be stored in drivers/private/arch/<cust>/<product> folder:
 *   -for ICE_OEM pub keys in drv_hwplat_ice_oem_pubk.h
 *   -for OEM_FACT pub keys in drv_hwplat_oem_fact_pubk.h
 *
 * RSA_KEY_TYPE__PROD file template:
 *
 * ,{ RSA_KEY_TYPE__PROD,
 * #include "../../arch/keys/<spec ICE_OEM path>/key.exponent.h"
 * #include "../../arch/keys/<spec ICE_OEM path/key.modulus.h"
 * }
 *
 */

/*************************************************************************************************
 * Project header files. The first in this list should always be the public interface for this
 * file. This ensures that the public interface header file compiles standalone.
 ************************************************************************************************/

#include "icera_global.h"
#include "drv_security.h"
#include "drv_arch_type.h"
#include "drv_arch_pubk.h"
#include "drv_brom_iface.h"
#include "hwplatform.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <string.h>

/*************************************************************************************************
 * Private Macros
 ************************************************************************************************/

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
const RsaPublicKey ice_oem_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ICE_OEM/key0/key.exponent.h"
    #include "keys/dev-ICE_OEM/key0/key.modulus.h"
 }
 #include "drv_hwplat_ice_oem_pubk.h"
};

const RsaPublicKey oem_fact_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-OEM_FACT/key0/key.exponent.h"
    #include "keys/dev-OEM_FACT/key0/key.modulus.h"
 }
#if !defined(ICERA_FEATURE_EXT_AUTH_CUSTCFG_FILE)&&!defined(ICERA_FEATURE_EXT_AUTH_DEVICECFG_FILE)
 #include "drv_hwplat_oem_fact_pubk.h"
#endif
};

const RsaPublicKey ice_fact_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ICE_FACT/key0/key.exponent.h"
    #include "keys/dev-ICE_FACT/key0/key.modulus.h"
 }
 /* These are obsolete */
};

const RsaPublicKey ice_dbg_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ICE_DBG/key0/key.exponent.h"
    #include "keys/dev-ICE_DBG/key0/key.modulus.h"
 }
 #include "drv_hwplat_ice_dbg_pubk.h"
};

const RsaPublicKey oem_field_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-OEM_FIELD/key0/key.exponent.h"
    #include "keys/dev-OEM_FIELD/key0/key.modulus.h"
 }
 #include "drv_hwplat_oem_field_pubk.h"
};

#if defined(ICERA_FEATURE_SOFT_ACTIVATION)
const RsaPublicKey act_act_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ACT_ACT/key0/key.exponent.h"
    #include "keys/dev-ACT_ACT/key0/key.modulus.h"
 }
 #include "drv_hwplat_act_act_pubk.h"
};
#endif

#ifdef EROBUSTA
const RsaPublicKey ice_auth_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ICE_AUTH/key0/key.exponent.h"
    #include "keys/dev-ICE_AUTH/key0/key.modulus.h"
 }
 #include "drv_hwplat_ice_auth_pubk.h"
};

const RsaPublicKey ice_cfg_keys[] =
{
 {
    RSA_KEY_TYPE__DEV,
    #include "keys/dev-ICE_CFG/key0/key.exponent.h"
    #include "keys/dev-ICE_CFG/key0/key.modulus.h"
 }
 #include "drv_hwplat_ice_cfg_pubk.h"
};
#endif /* #ifdef EROBUSTA */

const uint32 num_of_ice_oem_keys    = sizeof(ice_oem_keys)/sizeof(RsaPublicKey);
const uint32 num_of_oem_fact_keys   = sizeof(oem_fact_keys)/sizeof(RsaPublicKey);
const uint32 num_of_ice_fact_keys   = sizeof(ice_fact_keys)/sizeof(RsaPublicKey);
const uint32 num_of_ice_dbg_keys    = sizeof(ice_dbg_keys)/sizeof(RsaPublicKey);
const uint32 num_of_oem_field_keys  = sizeof(oem_field_keys)/sizeof(RsaPublicKey);
#if defined(ICERA_FEATURE_SOFT_ACTIVATION)
const uint32 num_of_act_act_keys    = sizeof(act_act_keys)/sizeof(RsaPublicKey);
#endif
#ifdef EROBUSTA
const uint32 num_of_ice_auth_keys   = sizeof(ice_auth_keys)/sizeof(RsaPublicKey);
const uint32 num_of_ice_cfg_keys    = sizeof(ice_cfg_keys)/sizeof(RsaPublicKey);
#endif /* #ifdef EROBUSTA */

const uint8 brom_public_exponent_ext[BROM_NUM_RSA_KEYS_EXTERNAL][8] =
{
#if defined (TARGET_DXP9040)
    #include "keys/dev-ICE_ICE/9xxx/9040/key0/key.exponent.h"
#elif defined (TARGET_DXP9140)
    #include "keys/dev-ICE_ICE/9xxx/9140/key0/key.exponent.h"
#else
#error "Unsupported DXP target for security."
#endif
};

const uint8 brom_rsa_modulus_ext[BROM_NUM_RSA_KEYS_EXTERNAL][RSA_MODULUS_SIZE] =
{
     /* ICE-ICE NON-PRODUCTION Key 0 for verification only - not for production */
     /* Copied from bootRom A1 code                                             */
#if defined (TARGET_DXP9040)
    #include "keys/dev-ICE_ICE/9xxx/9040/key0/key.modulus.h"
#elif defined (TARGET_DXP9140)
    #include "keys/dev-ICE_ICE/9xxx/9140/key0/key.modulus.h"
#endif

};

/*************************************************************************************************
 * Private function definitions
 ************************************************************************************************/

/*************************************************************************************************
 * Public function definitions (Not doxygen commented, as they should be exported in the header
 * file)
 ************************************************************************************************/
int drv_arch_GetPublicKeyInfo(unsigned char *key_id,
                              unsigned char **pub_key_modulus,
                              unsigned char **pub_key_exponent,
                              const RsaPublicKey *pubkey_table,
                              int num_of_keys,
                              tSigKeySet key_set)
{
    int i, result = 0, j;

    DEV_ASSERT(key_set != ARCH_ICE_ICE_KEY_SET);

    for (i = 0; i < num_of_keys; i++)
    {
        result = 0;
        /* For each public key in table, compare 4 1st bytes with key_id  */
        for (j = 0; j< sizeof(int); j++)
        {
            if (*(key_id + j) != pubkey_table[i].rsa_modulus[j])
            {
                result = -1;
                /* No need to continue after a wrong comparison */
                break;
            }
        }

        if (result == 0)
        {
            *pub_key_modulus = (unsigned char *)&pubkey_table[i].rsa_modulus[0];
            *pub_key_exponent = (unsigned char *)&pubkey_table[i].public_exponent[0];

            /* Use of dev keys is prohibited on production chips */
            if (brom_GetLivantoSecurityState() == SECURITY_STATE__PROD)
            {
                if (pubkey_table[i].type != RSA_KEY_TYPE__PROD)
                {
                    if((key_set == ARCH_ICE_OEM_KEY_SET)  ||
                       (key_set == ARCH_OEM_FACT_KEY_SET) ||
                       (key_set == ARCH_OEM_FIELD_KEY_SET))
                    {
                        /*  We have to check if this is an unlocked platform */
                        if(!drv_UnlockedPlatform())
                        {
                            /* force invalid key index */
                            result = -1;
                        }
                    }
                    else
                    {
                        /* force invalid key index */
                        result = -1;
                    }
                }
            }
        }

        if (result == 0)
        {
            /* Found a public key matching key_id, no need to continue */
            break;
        }
    }

    return result;
}
/** @} END OF FILE */
