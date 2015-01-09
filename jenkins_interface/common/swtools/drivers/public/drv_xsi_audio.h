/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2009
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_xsi_audio.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 * 
 *  Audio protocols
 
 
    DRV_XSI_P_AUDIO_PCM_LEFT:
 
                 LEFT CHANNEL          RIGHT CHANNEL
             _____________________
    LRCLK  _|                     |_______________________|

             _   _   _   _   _   _   _   _   _   _   _   _
    BCLK   _| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| | 
  
             ___ ___ ___ ___       ___ ___ ___ ___ 
    DATA    |___|___|___|___|     |___|___|___|___|
 
 
 
    DRV_XSI_P_AUDIO_PCM_RIGHT:
 
                  LEFT CHANNEL          RIGHT CHANNEL
             _____________________
    LRCLK  _|                     |_______________________|

             _   _   _   _   _   _   _   _   _   _   _   _
    BCLK   _| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| | 
  
                   ___ ___ ___ ___         ___ ___ ___ ___ 
    DATA          |___|___|___|___|       |___|___|___|___|
                  
 
    DRV_XSI_P_AUDIO_I2S_JUSTIFIED:
 
                  LEFT CHANNEL          RIGHT CHANNEL
             _____________________
    LRCLK  _|                     |_______________________|

           _   _   _   _   _   _   _   _   _   _   _   _
    BCLK    |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
  
            <--> ___ ___ ___ ___       ___ ___ ___ ___ 
    DATA        |___|___|___|___|     |___|___|___|___|
                  
 
 
    DRV_XSI_P_AUDIO_DSP_A (STEREO):
             ___
    LRCLK  _|   |_________________________________________|

           _   _   _   _   _   _   _   _   _   _   _   _
    BCLK    |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
  
                 ___ ___ ___ ___ ___ ___ ___ ___ 
    DATA        |___|___|___|___|___|___|___|___|
                 <-------------> <------------->               
                    LEFT CHANNEL   RIGHT CHANNEL
 
 
    DRV_XSI_P_AUDIO_DSP_A (MONO):
             ___
    LRCLK  _|   |_________________________________________|

           _   _   _   _   _   _   _   _   _   _   _   _
    BCLK    |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
  
                 ___ ___ ___ ___ 
    DATA        |___|___|___|___|
                LEFT+RIGHT (MONO)   
 
 
   DRV_XSI_P_AUDIO_DSP_B (STEREO):
             ___
    LRCLK  _|   |_________________________________________|

           _   _   _   _   _   _   _   _   _   _   _   _
    BCLK    |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
  
             ___ ___ ___ ___ ___ ___ ___ ___ 
    DATA    |___|___|___|___|___|___|___|___|
             <-------------> <------------->               
               LEFT CHANNEL   RIGHT CHANNEL

    DRV_XSI_P_AUDIO_DSP_B (MONO):
             ___
    LRCLK  _|   |_________________________________________|

           _   _   _   _   _   _   _   _   _   _   _   _
    BCLK    |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
  
             ___ ___ ___ ___ 
    DATA    |___|___|___|___|
            LEFT+RIGHT (MONO)   
 * 
 * 
 ************************************************************************************************/

/**
 * @defgroup XsiDriver Generic FSI/USI Driver
 *
 * Generic XSI Driver built upon mphal_fsi on 80xx platforms and
 * mphal_usi on 90xx platforms @{ 
 */

/**
 * @file drv_xsi.h Generic FSI/USI driver 
 *
 */

#ifndef DRV_XSI_AUDIO_H
#define DRV_XSI_AUDIO_H

/********************************************************************
  Exported constants/MACROs
 ********************************************************************/

/********************************************************************
 * Exported types
 ********************************************************************/


/* Enumerated types are stored in unsigned char format to improve D-cache efficiency.
*/



/**
 * Audio protocol configuration parameters
 */
typedef struct {

  unsigned char enableMaster;  /* Enable Master Signals Generation (BCLK and LRCLK
                     are outputs if this bit is set, otherwise they
                     are inputs. In master mode, the micro-code uses usi_phyN_clk as
                     input to generate BCLK. */
  unsigned int lrclkPeriod;  /* Number of BCLK pulses during an entire LRCLK period
                   (for DSP modes A and B) or a semi-period (for Audio,
                   PCM Left and PCM Right) */
  unsigned int sampleSize;  /* Significant bits in each sample, where
                   sampleSize <= lrclkPeriod. The equality
                   refers to a back-to-back transmission without gaps. */

} drv_XsiConfigAudio;

/********************************************************************
 * Exported functions
 ********************************************************************/

#endif
