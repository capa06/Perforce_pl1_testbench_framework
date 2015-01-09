/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_security.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup SecurityDriver Security Services
 * @ingroup HighLevelServices
 */

/**
 * @addtogroup SecurityDriver
 *
 * @{
 */

/**
 * @file drv_security.h Security API definition
 *
 */

#ifndef DRV_SECURITY_H
#define DRV_SECURITY_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "icera_global.h"
#ifdef HOST_TESTING
#include "ht_stub.h"
#else
#include "dxpsha256.h"
#endif


/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
#undef TEST

#define RSA_MODULUS_SIZE    256
#define RSA_EXPONENT_SIZE   8
#define SHA1_BLOCK_SIZE  	64
#define SHA1_DIGEST_SIZE 	20
#define MD5_DIGEST_SIZE     16
#define SHA1_MASK  		    (SHA1_BLOCK_SIZE - 1)
#define CSPRNG_SEED_BLEN    (SHA1_DIGEST_SIZE*8)

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * SHA1 (Secure Hash Algorithm 1) context
 */
typedef struct TagSHA1Context {
  uint32	Count[2];
  uint32	Hash[5];        /* 20 bytes */
  uint32	Buffer[16];     /* 64 bytes */

} SHA1Context;

/**
 * AES (Advanced Encryption Standard) context
 */
typedef struct
{
    uint32 erk[64];     /* encryption round keys */
    uint32 drk[64];     /* decryption round keys */
    int nr;                    /* number of rounds      */
} aes_context;

/**
 * CSPRNG (Cryptography Secure Pseudorandom Number Generator) context
 */
typedef struct
{
    uint8 seed[CSPRNG_SEED_BLEN/8];       /* 256-bit state */
    uint32 bbs;                            /* Bloom Bloom Shub PRNG */
    uint8 rand[CSPRNG_SEED_BLEN/8];       /* 256-bit random output */
} csprng_context;

struct xMD5Context {
	uint32 buf[4];
	uint32 bytes[2];
	uint32 in[16];
};

/**
 * External authentication security states.
 */
enum
{
    EXT_AUTH_LOCKED = 0      /* External authentication required */
    ,EXT_AUTH_UNLOCKED       /* External authentication done */
};

/**
 * Security authentication domains
 */
typedef enum
{
    SEC_DOMAIN_SECCFG = 0,   /**< Secure configuration file domain */
    SEC_DOMAIN_AUTH,         /**< Secure ICE_AUTH authentication domain */
    SEC_DOMAIN_MAX
} DRV_SecurityDomain;

/**
 * Domain authentication errors
 */
enum
{
    SEC_DOMAIN_NO_ERR = 0,
    SEC_DOMAIN_INVALID_DOMAIN,
    SEC_DOMAIN_ALREADY_CHALLENGED,
    SEC_DOMAIN_NO_CHALLENGE,
    SEC_DOMAIN_GENERAL_ERROR
};

/**
 * State of a domain
 */
typedef enum
{
    SEC_DOMAIN_IDLE,
    SEC_DOMAIN_CHALLENGE_ISSUED,
    SEC_DOMAIN_AUTHENTICATED,
} DRV_SecurityDomainState;


typedef union 
{
    SHA1Context          Sha1HashCtx;
    dxpsha256t_HashValue Sha2HashCtx;
} drv_HashCtx;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
extern const uint8 salt1[20];
extern const uint8 salt2[20];

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/

extern void Sha1_init_data(void);

extern void Sha1Begin(SHA1Context *SHA1Context);

extern void Sha1Hash(unsigned char *data,
                     unsigned int len,
                     SHA1Context *SHA1Context);

extern void Sha1End(unsigned char *hval,
                    SHA1Context *SHA1Context);

extern void Sha1(unsigned char *hval,
                 unsigned char *data,
                 unsigned int len);

extern int compare_SHA1_digest(unsigned char * rx_digest,
                               unsigned char * computed_digest);

extern int16 G_RSA_VerifySha1Digest(const uint8  * const Signature,
                                    const uint16         SignatureLen,
                                    const uint8  * const Digest,
                                    const uint16         DigestLen,
                                    const uint8  * const Modulus,
                                    const uint16         ModulusLen,
                                    const uint8  * const PublicExponent,
                                    const uint16         PublicExponentLen);

extern int16 G_RSA_SignSha1Digest(  uint8 * const Signature,
                                    const uint16         SignatureLen,
                                    const uint8   * const Digest,
                                    const uint16         DigestLen,
                                    const uint8   * const Modulus,
                                    const uint16         ModulusLen,
                                    const uint8   * const PrivateExponent,
                                    const uint16         PrivateExponentLen
                                  );

extern void G_RSA_STD ( uint8   * const Result,
                        const uint16         ResultLen,
                        const uint8   * const Modulus,
                        const uint16         ModulusLen,
                        const uint8   * const Exponent,
                        const uint16         ExponentLen,
                        const uint8   * const Data,
                        const uint16         DataLen
                        );

void csprng_init(csprng_context *p);
void csprng_nonce(csprng_context *p, unsigned char *nonce, int len);

/**
 * Initialise an MD5 context
 *
 * @param context Pointer to xMD5Content data structure to
 *                initialise
 */
void xMD5Init(struct xMD5Context *context);

/**
 * Update an MD5 context (previously initialised through a call
 * to xMD5Init) with the buffer passed in the parameter list
 *
 * @param context Pointer to the initialised MD5 context
 * @param buf Buffer to update the context with
 * @param len Size (in bytes) of the buffer
 */
void xMD5Update(struct xMD5Context *context, uint8 const *buf, int len);

/**
 * Finalise an MD5 context, previously initialised with a call
 * to xMD5Init() and populated with calls to xMD5Update()
 *
 * @param digest Pointer to a 16-byte buffer that will be
 *               populated with the MD5 hash
 * @param context Pointer to the MD4 context
 */
void xMD5Final(uint8 digest[16], struct xMD5Context *context);

/**
 * Return external authentication security state:
 * EXT_AUTH_UNLOCKED or EXT_AUTH_LOCKED.
 *
 * If no authentication performed, at start-up, default state is
 * EXT_AUTH_LOCKED
 */
int drv_SecurityExtAuthGetState(void);

/**
 * Set external authentication security state.
 *
 * @param state EXT_AUTH_UNLOCKED or EXT_AUTH_LOCKED
 */
void drv_SecurityExtAuthSetState(int state);

/**
 * Start a challenge for the given domain
 *
 * Note that no new challenge will be issued if one is already in progress
 *
 * @param domain The domain to get a challenge for
 * @param challenge Pointer to uint8 receiving the challenge
 * @len challenge size that is limited to NONCE_SIZE.
 * @return relevant error code
 * @note voluntarily won't link if ICERA_FEATURE_DOMAIN_AUTH not defined
 */
int drv_SecurityGetChallenge(DRV_SecurityDomain domain, uint8 *challenge, int len);

/**
 * Submit the response for the challenge for the given domain (either as ascii or binary data)
 *
 * Returns error code if there is no challenge, or the challenge has been answered
 *
 * @param domain The domain to get a challenge for
 * @param response Pointer to the memory containing the response.
 * @param len Length of (possibly partial) response - check will be done when the whole response has been received.
 * @param pubkey_table pointer to the key table to use.
 * @param key_id The key index (of the relevant keyset) in
 *               pubkey_table that has been used to create the
 *               response.
 * @return relevant error code
 * @note voluntarily won't link if ICERA_FEATURE_DOMAIN_AUTH not defined
 */
int drv_SecuritySubmitResponseASCII(DRV_SecurityDomain domain, uint8 *response, int len, uint8 *pubkey_table, int key_index);
int drv_SecuritySubmitResponseBinary(DRV_SecurityDomain domain, uint8 *response, unsigned int len, uint8 *pubkey_table, int key_index);

/**
 * Submit the response for the challenge for the given domain in binary data
 *
 * Returns error code if there is no challenge, or the challenge has been answered
 *
 * @param domain The domain to get a challenge for
 * @param response Pointer to the memory containing the response.
 * @param len Length of (possibly partial) response - check will be done when the whole response has been received.
 * @param pubkey_modulus pointer to the public key modulus to use.
 * @param pubkey_modulus_length public key modulus length.
 * @param pubkey_exponent pointer to the public key exponent to use.
 * @param pubkey_exponent_length public key exponent length.
 * @return relevant error code
 * @note voluntarily won't link if ICERA_FEATURE_DOMAIN_AUTH not defined
 */
int drv_SecuritySubmitResponseKey(DRV_SecurityDomain domain,
                                  uint8 *response,
                                  unsigned int len,
                                  uint8 *pubkey_modulus,
                                  unsigned int pubkey_modulus_length,
                                  uint8 *pubkey_exponent,
                                  unsigned int pubkey_exponent_length);

int drv_SecurityGetState(DRV_SecurityDomain domain);
int drv_SecurityClearState(DRV_SecurityDomain domain);

/**
 * Check if a production platform is unlocked.
 *
 * If this is the case, then production platform will allow:
 *  - running dev binary
 *  - F/W update with dev. binary (key revocation mechanism is
 *    disabled for an unlocked platform.)
 *
 *
 * @return int
 */
int drv_UnlockedPlatform(void);

/**
 *  Compute platform public chip ID.
 *
 *  public_chip_id buffer updated with computed value.
 *
 * @param public_chip_id
 */
void drv_GetPublicChipId(uint8 *public_chip_id);

/**
 *  Determines wether Fuse ID is programmed or not
 *
 * @return Returns 1 when programmed, else 0.
 */
int  drv_IsFuseIdProgrammed(void);

/**
 *  Compute platform public fuse ID.
 *
 *  public_fuse_id buffer updated with computed value.
 *
 * @param public_fuse_id
 */
void drv_GetPublicFuseId(uint8 *public_fuse_id);

/**
 * Check hard coded PCID whitelist and compare with current
 * platform public chip ID.
 *
 * If current platform in whitelist, then it is set
 * as a dev platform for current runtime session.
 *
 */
void drv_CheckChipIdInWhitelist(void);

/**
 *  Compute platform derived private chip ID.
 *
 *  derived_chip_id buffer updated with computed value.
 *
 * @param derived_chip_id
 */
void drv_GetDerivedPrivateChipId(uint8 *derived_chip_id);


/**
 *  Manage the security of NVRAM RW encrypted files
 *
 *  drv_nvramDigestAndEncryptBuffer.
 *  drv_nvramEncryptionBufferRelease.
 *  drv_nvramCheckAndDecryptBuffer.
 *  drv_nvramClearBufferRelease.
 *
 */

/**
*  This function computes a SHA1 then an AES CBC with 128 bits key encryption on
*   the input buffer. It returns the resulting buffer (starting with the 16 bytes IV) with
*   the corresponding size.
*
*  @param inputBuffer_p pointer to the clear buffer to process
*  @param inputBufferSize input buffer size
*  @param returnedBufferSize_p output buffer size
*  @return uint8* pointer to the output buffer (this is a dynamic allocated buffer to be free by
*                        drv_nvramEncryptionBufferRelease() function)
*
*/
uint8* drv_nvramDigestAndEncryptBuffer(uint8 *inputBuffer_p,
								 uint32  inputBufferSize,
								 uint32 *returnedBufferSize_p);

/**
*  This function  releases the buffer returned by drv_nvramDigestAndEncryptBuffer().
*  The use of this function is paired with drv_nvramDigestAndEncryptBuffer().
*
*  @param buffer_p pointer to the buffer to free
*
*/
void drv_nvramEncryptionBufferRelease(void   *buffer_p);

/**
* This function  decrypt the input buffer (AES CBC with 128 bits key) then check the
* SHA1 digest. It returns the resulting clear buffer with the corresponding size.
*
*  @param inputBuffer_p pointer to the encrypted buffer to process
*  @param inputBufferSize input buffer size
*  @param returnedBufferSize_p output buffer size
*  @return uint8* pointer to the output buffer (this is a dynamic allocated buffer to be free by
*						 drv_nvramClearBufferRelease() function)
*
*/
uint8* drv_nvramCheckAndDecryptBuffer(uint8 *inputBuffer_p,
							     uint32  inputBufferSize,
								 uint32 *returnedBufferSize_p);


/**
*  This function  releases the buffer returned by drv_nvramCheckAndDecryptBuffer().
*  The use of this function is paired with drv_nvramCheckAndDecryptBuffer().
*
*  @param buffer_p pointer to the buffer to free
*
*/
void drv_nvramClearBufferRelease(void *buffer_p);

/**
 * Check platform hw product ID with the one assigned to the
 * f/w.
 *
 * @param prod_id instanciated with prod_id read from fuses
 *
 * @return int 1 if prod_id matches defined h/w prod ID or
 *         default value, 0 if not
 */
int drv_CheckHwProdId(uint16 *prod_id);

/**
 *
 *
 * @param ctx
 */
void drv_HashBegin(drv_HashCtx *ctx);

/**
 *
 *
 * @param ctx
 * @param data
 * @param len
 */
void drv_Hash(drv_HashCtx *ctx, void *data, int len);

/**
 *
 *
 * @param ctx
 * @param hash_digest
 */
void drv_HashEnd(drv_HashCtx *ctx, uint8 *hash_digest);

/**
 *
 *
 * @param buffer
 * @param len
 * @param digest
 */
void drv_HashBuffer(unsigned char *buffer,
                    int len,
                    unsigned char *digest);

/**
 *
 *
 * @param rsa_sig
 * @param hash
 * @param modulus
 * @param exponent
 *
 * @return int
 */
int drv_HashRSAVerify(uint8 *rsa_sig,
                      void *hash,
                      uint8 *modulus,
                      uint8 *exponent);

/**
 * Get size of digest used for SHA/RS signing
 * May vary regarding if SH1/RSA or SHA2/RSA is used.
 *
 * @return int size of digest in bytes.
 */
int drv_HashGetDigestSize(void);
#endif /* #ifndef DRV_SECURITY_H */

/** @} END OF FILE */

