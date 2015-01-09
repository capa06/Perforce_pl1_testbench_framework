/*************************************************************************************************
 * Icera Inc
 * Copyright (c) 2005-2008
 * All rights reserved
 *************************************************************************************************
 * $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_audio.h#1 $
 * $Revision: #1 $
 * $Date: 2014/11/13 $
 * $Author: joashr $
 ************************************************************************************************/

/**
 * @defgroup AudioDriver Audio Driver
 *
 */


/**
 * @addtogroup AudioDriver
 * @{
 */

/**
 * @file drv_audio.h non-inlined functions for audio FSI driver
 *
 */
#ifndef DRV_AUDIO_H
#define DRV_AUDIO_H

/*************************************************************************************************
 * Project header files
 ************************************************************************************************/
#include "drv_xte.h"
#include "os_abs.h"
#include "drv_xsi.h"
#include "drv_clocks.h"

/*************************************************************************************************
 * Standard header files (e.g. <string.h>, <stdlib.h> etc.
 ************************************************************************************************/
#include <sys/types.h>

/*************************************************************************************************
 * Macros
 ************************************************************************************************/
/**
 * Number of speech block of 20ms into the audio TX sample
 * buffer
 */
#define NUM_SPEECH_BLOCK_TX             3
/**
 * Number of speech block of 20ms into the audio RX sample
 * buffer
 */
#define NUM_SPEECH_BLOCK_RX             3

/**
 * Number of samples in 20 ms of speech sampled @ 8kHz
 */
#define NUM_SPEECH_SAMPLES_PER_FRAME        160

/**
 * Use-case where AEC reference is computed by application
 * processor and provided to Livanto AEC through UL right
 * channel ( useful if application further process DL stream or
 * mixes DL stream with other stream such as MP3 decoding from 
 * AP) 
 */
#undef AEC_REF_FROM_UL_RIGHT_CHANNEL


/**
 * Use-case where Livanto AEC UL post processed signal is 
 * provided to application processor through DL right channel 
 * ( useful if application needs UL without echo. e,g: voice 
 * call record performed into AP) 
 */
#undef AEC_POST_PROC_TO_DL_RIGHT_CHANNEL

/**
 * Number sample for speech frame in AMR_WB 
 */
#define NUM_SPEECH_SAMPLES_PER_FRAME_16K    320

#define NUM_SPEECH_SAMPLES_PER_FRAME_DATA_PLUS_DUMMY_BITS   240


#define INT_SELECT_MS_RX
#define INT_SELECT_MS_TX

/**
 * Flag to initialise the audio codec only @ 1st voice call
 */
#define INIT_AUDIO_CODEC_1ST_CALL

/**
 * Continuous Audio Synchro by FIFO : use case is serial audio_if (including bulk USB)
 */
#undef AUDIO_FIFO_SYNCHRONIZATION

/**
 * Macro to use timer approach insterd DMA to mantain modem sync 
 * during pause/restart events 
 */
#undef USE_TIMER_2_PAUSE_RESTART

/**
 * Macro to delay (signed, so advance or delay) modem programmed
 * DMA start 
 */
#define DEFAULT_DMA_DELAY               0
#define DEFAULT_DMA_DELAY_AEC           -3000

/**
 * Continuous Audio Synchro by subframes and os clock: use case is PCMIF
 */
/**
 * e.g. 10 IT per 20ms frame = 1IT every 2ms
 * with slave configurations, 10 is the minimum 
 * otherwise, modem detect synchro lost before drift is 
 * corrected 
 */
#define DEFAULT_IT_PER_FRAME            16

/**
 * Size of each element into AIO queue
 */
#define Q_ELEMENT_AIO_SIZE              1

/**
 * Number of element into AIO queue
 */
#define NUM_ELEMENT_AIO_QUEUE           60

/**
 * Size of AIO queue
 */
#define Q_AIO_SIZE                      (NUM_ELEMENT_AIO_QUEUE * Q_ELEMENT_AIO_SIZE)

#undef CHECK_DL_TIMING
#undef CHECK_UL_TIMING
#undef CHECK_UL_TIMING_RX_DRIVER_OUT
#undef CHECK_DL_TIMING_TX_DRIVER_DONE
#undef CHECK_TX_AUDIO_IO_DMA_BUFFER_FILLED

#define     BIT_FIELD(n,width,shift)    (((n) & (width)) << (shift))

#define     BIT_DISABLE(_INDEX) (0L<<(_INDEX))

/* ============ Vulcan macros ============================ */
/**
 * Default mic volume used in Vulcan in dB
 */
#define VULCAN_MIC_VOL             (34)

/**
 * Mic muting used in Vulcan in dB
 */
#define VULCAN_MIC_MUTE            (0)

/**
 * Speaker muting in Vulcan in dB
 */
#define VULCAN_SPK_MUTE            (-24)  /* speaker muting during initialisation */

/**
 * Default speaker volume used in Vulcan in dB
 */
#define VULCAN_SPK_VOL             (6)    /* default speaker volume at call start */

/**
 * Default sidetone volume used in Vulcan in dB
 */
#define VULCAN_SDT_VOL             (-36)    /* use to be -6 */

/**
 * Sidetone muting in Vulcan in dB
 */
#define VULCAN_SDT_MUTE            (-36)

/**
 * WOLFSON WM8753L registers and bit fields
 */

/**
 * BIT WIDTH
 */
#define     BIT_WIDTH_2             0x003
#define     BIT_WIDTH_3             0x007
#define     BIT_WIDTH_4             0x00f
#define     BIT_WIDTH_5             0x01f
#define     BIT_WIDTH_6             0x03f
#define     BIT_WIDTH_7             0x07f
#define     BIT_WIDTH_8             0x0ff
#define     BIT_WIDTH_9             0x1ff
#define     BIT_WIDTH_10            0x3ff
#define     BIT_WIDTH_11            0x7ff

/**
 * Sidetone volume defintions
 */
#define     VOL_ST_PLUS6dB          0x0
#define     VOL_ST_PLUS3dB          0x1
#define     VOL_ST_0dB              0x2
#define     VOL_ST_MINUS3dB         0x3
#define     VOL_ST_MINUS6dB         0x4
#define     VOL_ST_MINUS9dB         0x5
#define     VOL_ST_MINUS12dB        0x6
#define     VOL_ST_MINUS15dB        0x7

/**
 * VDAC volume defintions
 */
#define     VOL_VDAC_PLUS9dB        0x0
#define     VOL_VDAC_PLUS6dB        0x1
#define     VOL_VDAC_PLUS3dB        0x2
#define     VOL_VDAC_0dB            0x3
#define     VOL_VDAC_MINUS3dB       0x4
#define     VOL_VDAC_MINUS6dB       0x5
#define     VOL_VDAC_MINUS9dB       0x6
#define     VOL_VDAC_MINUS12dB      0x7

/**
 * Output volume definitions
 */
#define     VOL_OUT_PLUS6dB         0x7f
#define     VOL_OUT_MINUS73dB       0x30

/**
 * ADC signal path control register and bit field
 */
#define     ADC_CTRL_REG            0x02
#define     DATASEL(data_sel)       BIT_FIELD(datasel, BIT_WIDTH_2, 7)
#define     ADCPOL(polarity)        BIT_FIELD(polarity, BIT_WIDTH_2, 5)
#define     VXFILT_ENABLE           BIT(4)
#define     HPMODE(hp_cut_off)      BIT_FIELD(hp_cut_off, BIT_WIDTH_2, 2)
#define     HPQR_ENABLE             BIT(1)
#define     ADCHPD_ENABLE           BIT(0)

#define     POL_NOT_INV             0x0
#define     L_POL_INV               0x1
#define     R_POL_INV               0x2
#define     LR_POL_INV              0x3

/**
 * ALC control register and bit field
 */
#define     ALC_CTRL_REG1           0x0c
#define     ALCSEL(alc_sel)         BIT_FIELD(alc_sel, BIT_WIDTH_2, 7)
#define     MAXGAIN(max_gain)       BIT_FIELD(max_gain, BIT_WIDTH_3, 4)
#define     ALCL(alc_target)        BIT_FIELD(alc_target, BIT_WIDTH_4, 0)

#define     ALC_OFF                 0x0
#define     ALC_R                   0x1
#define     ALC_L                   0x2
#define     ALC_STEREO              0x3

#define     GAIN_PLUS30dB           0x7
#define     GAIN_PLUS24dB           0x6
#define     GAIN_PLUS18dB           0x5
#define     GAIN_PLUS12dB           0x4
#define     GAIN_PLUS6dB            0x3
#define     GAIN_PLUS0dB            0x2
#define     GAIN_MINUS6dB           0x1
#define     GAIN_MINUS12dB          0x0

#define     ALC_MINUS6dB            0xf

/**
 * MIC preamp enable control register and bit field
 */
#define     MIC_PREAMP_EN_CTRL_REG  0x15
#define     MICAMP1EN               BIT(8)
#define     MICAMP2EN               BIT(7)

/**
 * ADC volume control
 */
#define     VOL_ADC_GAIN_PLUS30dB   0xff
#define     VOL_ADC_GAIN_MUTE       0x00

#define     L_ADC_VOL_CTRL_REG      0x10
#define     LADCVOL(vol_dB)         BIT_FIELD(vol_dB, BIT_WIDTH_8, 0)
#define     LAVU_ENABLE             BIT(8)

#define     R_ADC_VOL_CTRL_REG      0x11
#define     RADCVOL(vol_dB)         BIT_FIELD(vol_dB, BIT_WIDTH_8, 0)
#define     RAVU_ENABLE             BIT(8)

/**
 * ADC input control register and bit field
 */
#define     ADC_INPUT_CTRL_REG      0x2e
#define     MONOMIX(input_mode)     BIT_FIELD(input_mode, BIT_WIDTH_2, 5)
#define     RADCSEL(r_adc_in)       BIT_FIELD(r_adc_in, BIT_WIDTH_2, 2)
#define     LADCSEL(l_adc_in)       BIT_FIELD(l_adc_in, BIT_WIDTH_2, 0)

#define     STEREO_MIX              0x0
#define     ANALOG_MONO_MIX_L_ADC   0x1
#define     ANALOG_MONO_MIX_R_ADC   0x2
#define     DIGITAL_MONO_MIX        0x3

#define     PGA                     0x0
#define     LINE1_2ORRXP_RXN        0x1
#define     L_R_MONO_MIXORLINE1     0x2
#define     UNUSED                  0x3

/**
 * OUTPUT control register and bit field
 */
#define     OUT_CTRL_REG            0x2d
#define     MONO2SW(output)         BIT_FIELD(output, BIT_WIDTH_2, 7);
#define     HPSWEN_ENABLE           BIT(6)
#define     HPSWPOL_ENABLE          BIT(5)
#define     TSDEN_ENABLE            BIT(4)
#define     VROI_ENABLE             BIT(3)
#define     ROUT2INV_ENABLE         BIT(2)
#define     OUT3SW(output)          BIT_FIELD(output, BIT_WIDTH_2, 0);

#define     OUT_VREF                0x0
#define     ROUT2                   0x1
#define     LMIX_RMIX_DIV2          0x2

#define     INV_MONO                0x0
#define     L_MIX_DIV2              0x1
#define     R_MIX_DIV2              0x2
#define     L_R_MIX_DIV2            0x3

/**
 * MIC preamp gain control register and bit field
 */
#define     MIC_PREAMP_CTRL_REG     0x2f
#define     MIC2BOOST(gain)         BIT_FIELD(gain, BIT_WIDTH_2, 7)
#define     MIC1BOOST(gain)         BIT_FIELD(gain, BIT_WIDTH_2, 5)

#define     MIC_PREMP_GAIN_12dB     0x0
#define     MIC_PREMP_GAIN_18dB     0x1
#define     MIC_PREMP_GAIN_24dB     0x2
#define     MIC_PREMP_GAIN_30dB     0x3

/**
 * ALC mix and MIC mux input control register and bit field
 */
#define     INPUT_CTRL_REG          0x30
#define     RXMSEL(input_type)      BIT_FIELD(input_type, BIT_WIDTH_2, 6)
#define     MIXMUX(sidetone_sel)    BIT_FIELD(sidetone_sel, BIT_WIDTH_2, 4)
#define     LINEALC_ENABLE          BIT(3)
#define     MIC2ALC_ENABLE          BIT(2)
#define     MIC1ALC_ENABLE          BIT(1)
#define     RXALC_ENABLE            BIT(0)

/**
 * Input channel PGA control register and bit field
 */
#define     L_CH_PGA_CTRL_REG       0x31
#define     R_CH_PGA_CTRL_REG       0x32
#define     LIVU_ENABLE             BIT(8)
#define     LINMUTE_ENABLE          BIT(7)
#define     LZCEN_ENABLE            BIT(6)
#define     LINVOL(vol_dB)          BIT_FIELD(vol_dB, BIT_WIDTH_6, 0)
#define     RIVU_ENABLE             BIT(8)
#define     RINMUTE_ENABLE          BIT(7)
#define     RZCEN_ENABLE            BIT(6)
#define     RINVOL(vol_dB)          BIT_FIELD(vol_dB, BIT_WIDTH_6, 0)

#define     LINEVOL_0dBdB           0x17
#define     LINEVOL_MINUS0p75dB     0x16
#define     LINEVOL_MIMUS1p5dB      0x15
#define     LINEVOL_MINUS2p25dB     0x14
#define     LINEVOL_MINUS3dB        0x13

/**
 * Left Mixer Control Output register 1 and fields values
 */
#define     L_MIX_CTRL_REG1         0x22
#define     LD2LO_ENABLE            BIT(8)
#define     LM2LO_ENABLE            BIT(7)
#define     LM2LOVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)

/**
 * Left Mixer Control Output register 2 and fields values
 */
#define     L_MIX_CTRL_REG2         0x23
#define     VXD2LO_ENABLE           BIT(8)
#define     ST2LO_ENABLE            BIT(7)
#define     ST2LOVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)
#define     VXD2LOVOL(vol_dB)       BIT_FIELD(vol_dB, BIT_WIDTH_3, 0)

/**
 * Right Mixer Control Output register 1 and fields values
 */
#define     R_MIX_CTRL_REG1         0x24
#define     RD2RO_ENABLE            BIT(8)
#define     RM2RO_ENABLE            BIT(7)
#define     RM2ROVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)

/**
 * Right Mixer Control Output register 2 and fields values
 */
#define     R_MIX_CTRL_REG2         0x25
#define     VXD2RO_ENABLE           BIT(8)
#define     ST2RO_ENABLE            BIT(7)
#define     ST2ROVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)
#define     VXD2ROVOL(vol_dB)       BIT_FIELD(vol_dB, BIT_WIDTH_3, 0)

/**
 * Mono Mixer Control Output register 1 and bit fields
 */
#define     MONO_MIX_CTRL_REG1      0x26
#define     LD2MO_ENABLE            BIT(8)
#define     MM2MO                   BIT(7)
#define     MM2MOVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)

/**
 * Mono Mixer Control Output register 2 and bit field
 */
#define     MONO_MIX_CTRL_REG2      0x27
#define     RD2MO_ENABLE            BIT(8)
#define     ST2MO_ENABLE            BIT(7)
#define     ST2MOVOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_3, 4)
#define     VXD2MO_ENABLE           BIT(3)
#define     VXD2MOVOL(vol_dB)       BIT_FIELD(vol_dB, BIT_WIDTH_3, 0)

/**
 * Left Output Volume control register and bit field
 */
#define     LEFT_OUT_CTRL_REG       0x28
#define     LO1VU_ENABLE            BIT(8)
#define     LO1ZC_ENABLE            BIT(7)
#define     LOUT1VOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_7, 0)

/**
 * Right Output Volume control register and bit field
 */
#define     RIGHT_OUT_CTRL_REG      0x29
#define     RO1VU_ENABLE            BIT(8)
#define     RO1ZC_ENABLE            BIT(7)
#define     ROUT1VOL(vol_dB)        BIT_FIELD(vol_dB, BIT_WIDTH_7, 0)

/**
 * Digital Voice Audio Interface format control register and bit field
 */
#define     VOICE_AUDIO_CTRL_REG    0x03
#define     ADCDOP_ENABLE           BIT(8)
#define     VXCLKINV_ENABLE         BIT(7)
#define     PMS_ENABLE              BIT(6)
#define     MONO_ENABLE             BIT(5)
#define     PLRP_ENABLE             BIT(4)
#define     PWL(word_lenght)        BIT_FIELD(word_lenght, BIT_WIDTH_2, 2)
#define     PFORMAT(format)         BIT_FIELD(format, BIT_WIDTH_2, 0)

#define     BITS32_WORD             0x3
#define     BITS24_WORD             0x2
#define     BITS20_WORD             0x1
#define     BITS16_WORD             0x0

#define     DSP_MODE                0x3
#define     I2S_MODE                0x2
#define     LEFT_JUSTIFIED          0x1
#define     RIGHT_JUSTIFIED         0x0

/**
 * Audio Interface format register and bit field
 */
#define     AUDIO_IF_FORMAT_REG       0x04
#define     BCLKINV_ENABLE            BIT(7)
#define     MASTER_ENABLE             BIT(6)
#define     LRSWAP_ENABLE             BIT(5)
#define     LRP_ENABLE                BIT(4)
#define     WORDLEN(wl_value)         BIT_FIELD(wl_value, BIT_WIDTH_2, 2)
#define     BUS_FORMAT(format_value)  BIT_FIELD(format_value, BIT_WIDTH_2, 0)

/**
 * Audio Interface control register and bit field
 */
#define     AUDIO_IF_CTRL_REG       0x05
#define     VXCLKTRI_ENABLE         BIT(7)
#define     BCLKTRI_ENABLE          BIT(6)
#define     VXDTRI_ENABLE           BIT(5)
#define     ADCDTRI_ENABLE          BIT(7)
#define     IFMODE(ifmode)          BIT_FIELD(ifmode, BIT_WIDTH_2, 2)
#define     VXSFOE_ENABLE           BIT(1)
#define     LRCOE_ENABLE            BIT(0)

/**
 * Sample Rate control register and bit field
 */
#define     SAMPLE_RATE_CTRL_REG    0x06
#define     SRMODE_ENABLE           BIT(8)
#define     PSR_ENABLE              BIT(7)
#define     SR(sr_value)            BIT_FIELD(sr_value, BIT_WIDTH_5, 1)
#define     USB_ENABLE              BIT(0)

/**
 * Clock Control register and bit field
 */
#define     CLK_CTRL_REG            0x34
#define     PCMDIV(value)           BIT_FIELD(value, BIT_WIDTH_3, 6)
#define     MCLKSEL_ENABLE          BIT(4)
#define     PCMCLKSEL_ENABLE        BIT(3)
#define     CLKEQ_ENABLE            BIT(2)
#define     GP1CLK1SEL_ENABLE       BIT(1)
#define     GP2CLK2SEL_ENABLE       BIT(0)

#define     DIV1                    0x0
#define     DIV3                    0x2
#define     DIV5p5                  0x3
#define     DIV2                    0x4
#define     DIV4                    0x5
#define     DIV6                    0x6
#define     DIV8                    0x7

/**
 * PLL1 Control register and bit field
 */
#define     PLL1_CTRL_REG           0x35
#define     CLK1SEL_ENABLE          BIT(5)
#define     CLK1DIV2_ENABLE         BIT(4)
#define     MCLK1DIV2_ENABLE        BIT(3)
#define     PLL1DIV2_ENABLE         BIT(2)
#define     PLL1RB_ENABLE           BIT(1)
#define     PLL1EN_ENABLE           BIT(0)

/**
 * PLL1 frequency ratio control registers and bit field
 */
#define     PLL1_FREQ_CTRL_REG1     0x36
#define     PLL1_FREQ_CTRL_REG2     0x37
#define     PLL1_FREQ_CTRL_REG3     0x38
#define     PLL1N(n)                BIT_FIELD(n, BIT_WIDTH_4, 5)
#define     PLL1KPART1(k1)          BIT_FIELD(k1, BIT_WIDTH_4, 0)
#define     PLL1KPART2(k2)          BIT_FIELD(k2, BIT_WIDTH_9, 0)
#define     PLL1KPART3(k3)          BIT_FIELD(k3, BIT_WIDTH_9, 0)

/**
 * PLL2 Control register and bit field
 */
#define     PLL2_CTRL_REG           0x39
#define     CLK2SEL_ENABLE          BIT(5)
#define     CLK2DIV2_ENABLE         BIT(4)
#define     MCLK2DIV2_ENABLE        BIT(3)
#define     PLL2DIV2_ENABLE         BIT(2)
#define     PLL2RB_ENABLE           BIT(1)
#define     PLL2EN_ENABLE           BIT(0)

/**
 * PLL2 frequency ratio control registers and bit field
 */
#define     PLL2_FREQ_CTRL_REG1     0x3a
#define     PLL2_FREQ_CTRL_REG2     0x3b
#define     PLL2_FREQ_CTRL_REG3     0x3c
#define     PLL2N(n)                BIT_FIELD(n, BIT_WIDTH_4, 5)
#define     PLL2KPART1(k1)          BIT_FIELD(k1, BIT_WIDTH_4, 0)
#define     PLL2KPART2(k2)          BIT_FIELD(k2, BIT_WIDTH_9, 0)
#define     PLL2KPART3(k3)          BIT_FIELD(k3, BIT_WIDTH_9, 0)

/**
 * WOLFSON WM8991 registers and bit fields
 */

/**
 * Power Management register 1 
 */
#define     PWR_REG1                0x01
#define     SPK_ENABLE              BIT(12)
#define     SPK_DISABLE             BIT_DISABLE(12)
#define     OUT3_ENABLE             BIT(11)
#define     OUT4_ENABLE             BIT(10)
#define     LOUT_ENABLE             BIT(9)
#define     ROUT_ENABLE             BIT(8)
#define     MICBIAS_ENABLE          BIT(4)
#define     VMID_MODE(n)            BIT_FIELD(n, BIT_WIDTH_2, 1)
#define     VREF_ENABLE             BIT(0)

/**
 * Power Management register 2 
 */
#define     PWR_REG2                0x02
#define     PLL_ENABLE              BIT(15)
#define     TSHUT_ENABLE            BIT(14)
#define     TSHUT_OPDIS             BIT(13)
#define     OPCLK_ENABLE            BIT(11)
#define     AINL_ENABLE             BIT(9)
#define     AINR_ENABLE             BIT(8)
#define     LIN34_ENABLE            BIT(7)
#define     LIN12_ENABLE            BIT(6)
#define     RIN34_ENABLE            BIT(5)
#define     RIN12_ENABLE            BIT(4)
#define     ADCL_ENABLE             BIT(1)
#define     ADCR_ENABLE             BIT(0)
/** 
 * Power Management register 3 
 */
#define     PWR_REG3                0x03
#define     LON_ENABLE              BIT(13)
#define     LOP_ENABLE              BIT(12)
#define     RON_ENABLE              BIT(11)
#define     ROP_ENABLE              BIT(10)
#define     SPKPGA_ENABLE           BIT(8)
#define     LOPGA_ENABLE            BIT(7)
#define     ROPGA_ENABLE            BIT(6)
#define     LOMIX_ENABLE            BIT(5)
#define     ROMIX_ENABLE            BIT(4)
#define     DACL_ENABLE             BIT(1)
#define     DACR_ENABLE             BIT(0)

/**
 * Audio Interface 1 
 */
#define     AUDIO_IF_REG1           0x04
#define     AIFADCL_SRC             BIT(15)
#define     AIFADCR_SRC             BIT(14)
#define     AIFADC_TDM              BIT(13)
#define     AIFADC_TDM_CHAN         BIT(12)
#define     AIF_BCLK_INV            BIT(8)
#define     AIF_LRCLK_INV           BIT(7)
#define     AIF_WL(n)               BIT_FIELD(n, BIT_WIDTH_2, 5)
#define     AIF_FMT(n)              BIT_FIELD(n, BIT_WIDTH_2, 3)                  

/**
 * Audio Interface 2
 */
#define     AUDIO_IF_REG2           0x05
#define     DACL_SRC                BIT(15)
#define     DACR_SRC                BIT(14)
#define     AIFDAC_TDM              BIT(13)
#define     AIFDAC_TDM_CHAN         BIT(12)
#define     DAC_BOOST(n)            BIT_FIELD(n, BIT_WIDTH_2, 10)
#define     DAC_COMP                BIT(4)
#define     DAC_COMP_MODE           BIT(3)
#define     ADC_COMP                BIT(2)
#define     ADC_COMP_MODE           BIT(1)
#define     LOOPBACK_ENABLE         BIT(0)
/**
 * Clocking register 1 
 */
#define     CLOCKING_REG1           0x06
#define     TOCLK_RATE              BIT(15)
#define     TOCLK_ENABLE            BIT(14)
#define     OPCLK_DIV(n)            BIT_FIELD(n, BIT_WIDTH_4, 9)
#define     DCLK_DIV(n)             BIT_FIELD(n, BIT_WIDTH_3, 6)
#define     BCLK_DIV(n)             BIT_FIELD(n, BIT_WIDTH_4, 1)
/**
 * Clocking register 2
 */
#define     CLOCKING_REG2           0x07
#define     MCLK_SRC                BIT(15)
#define     SYSCLK_SRC              BIT(14)
#define     CLK_FORCE               BIT(13)
#define     MCLK_DIV(n)             BIT_FIELD(n, BIT_WIDTH_2, 11)
#define     MCLK_INV                BIT(10)
#define     ADC_CLKDIV(n)           BIT_FIELD(n, BIT_WIDTH_3, 5) 
#define     DAC_CLKDIV(n)           BIT_FIELD(n, BIT_WIDTH_3, 2) 

/**
 * Audio Interface register 3
 */
#define     AUDIO_IF_REG3           0x08
#define     AIF_MSTR1               BIT(15)
#define     AIF_MSTR2               BIT(14)
#define     AIF_SEL                 BIT(13)
#define     ADCLRC_DIR              BIT(11)
#define     ADCLRC_RATE(n)          BIT_FIELD(n, BIT_WIDTH_11, 0)
/**
 * Audio Interface register 4
 */
#define     AUDIO_IF_REG4           0x09
#define     ALRCGPIO1               BIT(15)
#define     ALRCBGPIO6              BIT(14)
#define     AIF_TRIS                BIT(13)
#define     DACLRC_DIR              BIT(11)
#define     DACLRC_RATE(n)          BIT_FIELD(n, BIT_WIDTH_11, 0) 
/**
 * DAC Control register
 */
#define     DAC_CTRL_REG            0x0A
#define     DAC_SDMCLK_RATE         BIT(12)
#define     AIF_LARCLK_RATE         BIT(10)
#define     DAC_MONO                BIT(9)
#define     DAC_SB_FILT             BIT(8)
#define     DAC_MUTE_RATE           BIT(7)
#define     DAC_MUTE_MODE           BIT(6)
#define     DEEMP(n)                BIT_FIELD(n, BIT_WIDTH_2, 4)
#define     DAC_MUTE                BIT(2)
#define     DAC_UNMUTE              BIT_DISABLE(2)
#define     DACL_DATINV             BIT(1)
#define     DACR_DATINV             BIT(0)

/**
 * Left DAC digital Volume register
 */
#define     L_DAC_CTRL_VOL_REG      0x0B
#define     DACL_VU                  BIT(8)
#define     DACL_VOL(n)             BIT_FIELD(n, BIT_WIDTH_8, 0)
/**
 * Right DAC digital Volume register
 */
#define     R_DAC_CTRL_VOL_REG      0x0C
#define     DACR_VU                  BIT(8)
#define     DACR_VOL(n)             BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * ADC Control register
 */
#define     L_R_ADC_CTRL_REG        0x0E
#define     ADC_HPF_ENABLE          BIT(8)
#define     ADC_HPF_CUT(n)          BIT(n, BIT_WIDTH_2, 5)
#define     ADCL_DATAINV            BIT(1)
#define     ADCR_DATAINV            BIT(0)

/**
 * Left ADC Digital volume register
 */
#define     L_ADC_CTRL_VOL_REG      0x0F
#define     ADC_VU                  BIT(8)
#define     ADCL_VOL(n)             BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * Right ADC Digital volume register
 */
#define     R_ADC_CTRL_VOL_REG      0x10
#define     ADCR_VOL(n)             BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * GPIO Control register 1
 */
#define     GPIO_CTRL_REG1          0x12
#define     IRQ                     BIT(12)
#define     TEMPOK                  BIT(11)
#define     MICSHRT                 BIT(10)
#define     MICDET                  BIT(9)
#define     PLL_LCK                 BIT(8)
#define     GPIO_STATUS(n)          BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * GPIO1 & GPIO2
 */
#define     GPIO1_GPIO2             0x13

/**
 * LIN12 Input PGA volume
 */
#define     LIN12_PGA_VOL_REG1      0x18
#define     IPVU0                   BIT(8)
#define     LI12MUTE                BIT(7)
#define     LI12ZC                  BIT(6)
#define     LIN12VOL(n)             BIT_FIELD(n, BIT_WIDTH_5, 0) 
/**
 * Left Headphone Output volume
 */
#define     LOUT_VOL_REG            0x1C
#define     OPVU0                   BIT(8)
#define     LOZC                    BIT(7)
#define     LOUTVOL(n)              BIT_FIELD(n, BIT_WIDTH_7, 0) 

/**
 * Right Headphone Output volume
 */
#define     ROUT_VOL_REG            0x1D
#define     OPVU1                   BIT(8)
#define     ROZC                    BIT(7)
#define     ROUTVOL(n)              BIT_FIELD(n, BIT_WIDTH_7, 0) 

/**
 * Line Output volume
 */
#define     LO_VOL_REG              0x1E
#define     LONMUTE                 BIT(6)
#define     LOPMUTE                 BIT(5)
#define     LOATTN                  BIT(4)
#define     RONMUTE                 BIT(2)
#define     ROPMUTE                 BIT(1)
#define     ROATTN                  BIT(0)

/**
 * OUT3/4 Volume
 */
#define     OUT34_VOL_REG           0x1F
#define     OUT3MUTE                BIT(5)
#define     OUT3ATTN                BIT(4)
#define     OUT4MUTE                BIT(1)
#define     OUT4ATTN                BIT(0)

/**
 * LOPGA volume
 */
#define     LOPGA_VOL_REG           0x20
#define     OPVU2                   BIT(8)
#define     LOPGAZC                 BIT(7)
#define     LOPGAVOL(n)             BIT_FIELD(n, BIT_WIDTH_7, 0)

/**
 * ROPGA volume
 */
#define     ROPGA_VOL_REG           0x21
#define     OPVU3                   BIT(8)
#define     ROPGAZC                 BIT(7)
#define     ROPGAVOL(n)             BIT_FIELD(n, BIT_WIDTH_7, 0)

/**
 * Speaker Volume
 */
#define     SPK_VOL_REG             0x22
#define     SPK_ATTN(n)             BIT_FIELD(n, BIT_WIDTH_2, 0)

/**
 * Class D Control register 1
 */
#define     CLASS_D_CTRL_REG1       0x23
#define     CDMODE                  BIT(8)

/**
 * Class D Control register 3
 */
#define     CLASS_D_CTRL_REG3       0x25
#define     DC_GAIN(n)              BIT_FIELD(n, BIT_WIDTH_3, 3)
#define     AC_GAIN(n)              BIT_FIELD(n, BIT_WIDTH_3, 0)

/**
 * Class D Control register 4
 */
#define     CLASS_D_CTRL_REG4       0x26
#define     SPKZC                   BIT(7)

/**
 * Input Mixer register 2
 */
#define     IN_MIXER_REG2           0x28
#define     LMP4                    BIT(7)
#define     LMN3                    BIT(6)
#define     LMP2                    BIT(5)
#define     LMN1                    BIT(4)
#define     RMP4                    BIT(3)
#define     RMN3                    BIT(2)
#define     RMP2                    BIT(1)
#define     RMN1                    BIT(0)

/**
 * Input Mixer register 3
 */
#define     IN_MIXER_REG3           0x29
#define     L34MNB                  BIT(8)
#define     L34MNBST                BIT(7)
#define     L12MNB                  BIT(5)
#define     L12MNBST                BIT(4)
#define     LDBVOL(n)               BIT_FIELD(n, BIT_WIDTH_3, 0)

/**
 * Output Mixer register 1         
 */
#define     OUT_MIXER_REG1          0x2D
#define     LRBLO                   BIT(7)
#define     LLBLO                   BIT(6)
#define     LRI3LO                  BIT(5)
#define     LLI3LO                  BIT(4)
#define     LR12LO                  BIT(3)
#define     LL12LO                  BIT(2)
#define     LDLO                    BIT(0)
#define     LDLO_DISABLE            BIT_DISABLE(0)

/**
 * Output Mixer register 2         
 */
#define     OUT_MIXER_REG2          0x2E
#define     RLBRO                   BIT(7)
#define     RRBRO                   BIT(6)
#define     RLI3RO                  BIT(5)
#define     RRI3RO                  BIT(4)
#define     RL12RO                  BIT(3)
#define     RR12RO                  BIT(2)
#define     RDRO                    BIT(0)
#define     RDRO_DISABLE            BIT_DISABLE(0)

/**
 * OUT3/4 Mixer
 */
#define     OUT34_MIX_REG           0x33
#define     VSEL(n)                 BIT_FIELD(n, BIT_WIDTH_2, 7)
#define     LI4O3                   BIT(5)
#define     LPGAO3                  BIT(4)
#define     RI4O3                   BIT(1)
#define     RPGAO3                  BIT(0)

/**
 * Speaker output mixer
 */
#define     SPK_OUT_MIX_REG         0x36
#define     LB2SPK                  BIT(7)
#define     RB2SPK                  BIT(6)
#define     LI2SPK                  BIT(5)
#define     RI2SPK                  BIT(4)
#define     LOPGASPK                BIT(3)
#define     ROPGASPK                BIT(2)
#define     LDSPK                   BIT(1)
#define     RDSPK                   BIT(0)
#define     LDSPK_DISABLE           BIT_DISABLE(1)
#define     RDSPK_DISABLE           BIT_DISABLE(0)

/**
 * PLL control register 1
 */
#define     PLL_CTRL_REG1           0x3C
#define     SDM                     BIT(7)
#define     PRESCALE                BIT(6)
#define     PLLN(n)                 BIT_FIELD(n, BIT_WIDTH_4, 0)
/**
 * PLL control register 2
 */
#define     PLL_CTRL_REG2           0x3D
#define     PLLK1(n)                BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * PLL control register 3
 */
#define     PLL_CTRL_REG3           0x3E
#define     PLLK2(n)                BIT_FIELD(n, BIT_WIDTH_8, 0)

/**
 * I2C device identifier code for WM8753L
 */
#define I2CDEV_WOLFSON_CODEC            0x1a

/**
 * I2C device identifier code for WM8991
 */
#define I2CDEV_WOLFSON_WM8991_CODEC     0x1a 

/** 
 *  Value of the delay to start DMA in 8kHz speech samples
 */
#define SAMPLES_TO_MICROSECONDS(x) ((x)*125)

/** 
 *  Value of the delay to start DMA in 16kHz speech samples
 */
#define SAMPLES_TO_MICROSECONDS_16K(x) (((x)*125)/2)

/**
 * Ticks in os time stamp unit (15.36 MHz) or (38.4 Mhz)
 */
#define NB_TICKS_20_MS      (DRV_CET_CLK_SPEED_HZ/(50))    //(307200)
#define NB_TICKS_5_MS       (DRV_CET_CLK_SPEED_HZ/(200))   //(76800)
#define NB_TICKS_2_5_MS     (DRV_CET_CLK_SPEED_HZ/(400))   //(38400)
#define NB_TICKS_2_MS       (DRV_CET_CLK_SPEED_HZ/(500))   //(30720)
#define NB_TICKS_125_uS     (DRV_CET_CLK_SPEED_HZ/(8000))  //(1920)
#define NB_TICKS_25_US      (DRV_CET_CLK_SPEED_HZ/(40000)) //(384)

/**
 * Macro to indicate start of both DMA status
 */
#define START_BOTH_DMA 0

/**
 * Macro to indicate start of TX DMA status
 */
#define START_TX_DMA   1

/**
 * Macro to indicate start of RX DMA status
 */
#define START_RX_DMA   2

/**
 * Macro to indicate restart of both DMA status
 */
#define RESTART_BOTH_DMA 3

/**
 * Macro to indicate start of GSC Audio transfer (i.e. USB not
 * ISO)
 */
#define START_AUDIO_GSC 4

/**
 * Macro to indicate start 2nd audio stream
 */
#define START_2ND_DL_DMA 5

/**
 * Macro to indicate start 2nd audio stream
 */
#define START_2ND_UL_DMA 6

/**
 * Macro to enable systematically dual microphone AEC algorithm 
 * input data in stereo or mono. In mono case data will be 
 * duplicated on stereo input buffer provided to dual mic AEC, 
 * beamforer should be disabled (NVoice). 
 */
#define DUAL_MIC_INPUTS

/**
 * Macro to handle mono <-> stereo handling
 */
#define EXTRACT_UPPER_16_BIT(x)        ((   (x)    & 0xFFFF0000)>>16)
#define EXTRACT_LOWER_16_BIT(x)        (    (x)    & 0x0000FFFF     )
#define INSERT_UPPER_16_BIT(y, x)      y = (((y) & 0x0000FFFF) | ( (x)<<16 ))
#define INSERT_LOWER_16_BIT(y, x)      y = (((y) & 0xFFFF0000) | (  x  &   0x0000FFFF   ))

/**
 * Macro to extract 16 bit words from 32 bits as a function of 
 * FSI I2S configuration. Out processor in little endian. 
 *  
 * Standard I2S reads Left channel first, Inverse I2S does the 
 * opposite. Dual mic AEC is expecting this order. 
 *  
 * Given that first word read is endian (lower) and second read
 * word is upper, behaviour is as follows 
 *  
 * Normal I2S : 
 * Acquisition | Right Channel | Left Channel | 
 * AEC Input   | Right Channel | Left Channel |  so no swap 
 *  
 * Inverted I2S: 
 * Acquisition | Left Channel  | Right Channel | 
 * AEC Input   | Right Channel | Left Channel  |  so swap is 
 * needed 
 *  
 */
#define SWAP_UPPER_LOWER(y)                     \
    {                                           \
      short temp;                               \
      temp = EXTRACT_LOWER_16_BIT(y);           \
      y    = EXTRACT_UPPER_16_BIT (y);          \
      INSERT_UPPER_16_BIT(y, temp);             \
    }

#define DUPLICATE_BOTH_LEFT(y)                  \
    {                                           \
      short temp;                               \
      temp = EXTRACT_LOWER_16_BIT(y);           \
      INSERT_UPPER_16_BIT(y, temp);             \
    }

/*************************************************************************************************
 * Public Types
 ************************************************************************************************/

/**
 * AUDIO PROTOCOLS
 */
typedef enum
{
    AUDIO_PROTOCOL_FSI_PCM_MONO_B = 0,
    AUDIO_PROTOCOL_FSI_I2S = 1,
  
    AUDIO_PROTOCOL_I2S = 1,
    AUDIO_PROTOCOL_DSP_A,
    AUDIO_PROTOCOL_DSP_B,
    AUDIO_PROTOCOL_TDM_LEFT,
    AUDIO_PROTOCOL_TDM_RIGHT,
    AUDIO_PROTOCOL_TDM_I2S,
    AUDIO_PROTOCOL_PCM_LEFT,
    AUDIO_PROTOCOL_PCM_RIGHT, 
    AUDIO_PROTOCOL_AHUB_TX,
    AUDIO_PROTOCOL_AHUB_RX,
    AUDIO_PROTOCOL_LOOPBACK,
}
drv_audio_protocol_t;

/**
 * AUDIO IF identifiers
 */
typedef enum
{
    AUDIO_IF_TX,
    AUDIO_IF_RX,
    AUDIO_IF_TX_MIX,
    AUDIO_IF_RX_AEC,
    AUDIO_IF_MAX,
  
} drv_audio_if_id_t;

typedef enum {
    AUDIO_LINK_AUDIO0 = 0,
    AUDIO_LINK_AUDIO1,
    AUDIO_LINK_AUDIO2,
    AUDIO_LINK_AHUB_TX0,
    AUDIO_LINK_AHUB_TX1,
    AUDIO_LINK_AHUB_RX0,
    AUDIO_LINK_AHUB_RX1, 
    AUDIO_NUM_LINKS,
} drv_audio_link_id_t;



typedef enum
{
#ifdef ICE9XXX_USI
    AUDIO_DIR_TX = DRV_XSI_TX,
    AUDIO_DIR_RX = DRV_XSI_RX,
#else
    AUDIO_DIR_TX = MPHALFSI_TX,
    AUDIO_DIR_RX = MPHALFSI_RX,
#endif
} drv_audio_direction_t;

/**
 * Opaque AUDIO LINK structure.
 */
struct drv_audio_if;
typedef struct drv_audio_if drv_audio_if_t;

 /**
 * AUDIO codec status 
 */
typedef enum
{
    CODEC_OFF = 0,
    CODEC_ON,
    NUM_AUDIO_CODEC_STATES
} audio_codec_s;

/**
 * AUDIO Sidetone parameters
 */
typedef struct
{
    bool           st_enable;       /**< sidetone enable flag */
    short          *p_rd;           /**< Pointer to specify where to add ST info into the linear buffer in DL*/
    int32          *p_rd_stereo;    /**< Pointer to specify where to add ST info into the linear stereo buffer in DL*/
    uint8          *p_rd_comp;      /**< Pointer to specify where to add ST info into the companded buffer in DL */
    uint32         index;           /**< buffer index within all audio sample buffer range */      
    uint32         sub_frame;       /**< buffer subframe index which change to each DMA transfer*/  
    short          sidetone_gain;   /**< gain to be applied to sidetone samples */
    bool           sidetone_phase;  /**< flag to indicate if sidetone phase change is needed */
    short          sidetone_shift;  /**< phase value */
} sidetone_param_s;

/**
 * AUDIO STE thread parameters
 */
typedef struct ste_Thread
{
    os_RecursiveMutexHandle steMutexHandle; 
    os_TaskHandle       steYieldThread;         /**< audio task handle */
    os_QueueHandle      steYieldQ;              /**< audio task queue */
    int                 steYieldQOverflow;      /**< flag to indicate if overflow is occured */
    drv_XteHdl          ste_hdl;                /**< STE handle */
    int                 ste_context;            /**< STE context value */
    uint32              index;                  /**< buffer index within all audio sample buffer range */
    uint32              sub_frame;              /**< buffer subframe index which change to each DMA transfer*/
    uint32              tot_sub_frames;         /**< total number of subframes */
    uint32              size;                   /**< size in byte of each DMA transfer */
    uint32              old_size;               /**< size ib byte of each DMA transfer before to change fs */
    uint8               freq_sample;            /**< frequency sample rate */
    uint32              old_speech_block_size;  /**< number of sample in each speech block of 20ms before to change fs */
    uint32              speech_block_size;      /**< number of sample in each speech block of 20ms */
    uint32              bit_rate;               /**< FSI bit rate transfer */
    uint32              word_width;             /**< FSI word widht */
    bool                audioSampleRate16K;     /**< audio sample rate front-end - replace PCM_AUDIO_WB CF */
    bool                rf_loop_active;         /**< flag to indicate if any of RF loop (A,B,C etc.) are active */
    bool                useGsc;                 /**< flag to indicate routing to/from USB bulk endpoint */
    bool                master_not_slave;       /**< flag to indicate if PCM IF is master or slave */
    bool                short_not_long;         /**< flag to indicate if frame sync is short or long */
    bool                multislot;              /**< flag to indicate to use PCM IF in SPI mode (i.e. multislot) */
    bool                raising_not_falling;    /**< flag to indicate to start of frame sync on raisng edfe of bit clk */
    uint16              bits_to_right_justify_pcm; /**< number of bits to be right justified in each sample word */
    bool                stereo_mode;            /**< flag to indicate if stereo mode is used */
    bool                previous_stereo_mode;   /**< flag to store old stereo mode status */
    uint16              used_fsi_protocol;      /**< fsi protocol type in used*/
    bool                call_dropped;           /**< Checked by DMA to handle new DMA transfer: true whenever DMA is used */
    bool                force_dma;              /**< True in case no modem but DMA still needed */
    bool                is_dma_started;         /**< Flag to indicate that DMA is started */
    bool                kill_dma;               /**< Flag to indicate that DMA is already freed */
    bool                ap_is_in_voice_call;    /**< check if call is on by AP */
    bool                resync_audio;           /**< Flag to indicate a resync is requested */
    bool                filter_dma_cb;          /**< flag to prevent CBs associated to DMA interrupt completion are executed */
    os_TimerHandle      audioUpdateTimerHandle; /**< Timer to be used during pause to continue modem sync */
    bool                vulcan_codec;           /**< Flag to indicate if Vulcan is in use */
    uint16              sent_frame_counter;     /**< It counts frame not sent/received by modem */
    short               **p_wr;                 /**< pointer to write buffer in DL */
    int32               **p_wr_stereo;          /**< pointer to write stereo buffer in DL */
    uint8               **p_wr_comp;            /**< pointer to write buffer for companded data in DL*/
    uint16              comp_type;              /**< compandig mode: A-LAW, M-LAw or Linear */
    void                (*p_enc) (uint16     ,  /**< function pointer to G711 encoder function */
                                  int16     *,
                                  uint32     ,
                                  uint8     *,
                                  uint32    *);
    void                (*p_dec) (uint16     ,  /**< function pointer to G711 decoder function */
                                  uint8     *,
                                  uint32     ,
                                  int16     *);
    sidetone_param_s    sidetone_cfg;           /**< sidetone parameters structure */
    bool call_being_stopped;                    /**< flag to signal that DMA is already stopped during fadeout algo */
    short number_of_faded_subframe;             /**< fadout counter */

    void (*timeout)(struct ste_Thread *sc); /**< handler for audio update timeout */
    void (*done)(struct ste_Thread *sc);    /**< handler for DMA done */
    drv_audio_if_id_t id;

} ste_Thread_struct;


/**
 * AUDIO TX call parameters
 */
typedef struct
{
    short *p_rd;                /**< Side tone 5ms writing pointer */
    short *p_wr;                /**< Speech 20ms writing pointer */
    int32 *p_rd_stereo;         /**< Side tone 5ms writing pointer to stereo buffer */
    int32 *p_wr_stereo;         /**< Speech 20ms writing pointer to stereo buffer */
    uint8 *p_rd_comp;           /**< Side tone 5ms writing pointer into the companded buffer*/
    uint8 *p_wr_comp;           /**< Speech 20ms writing pointer into the companded buffer */
    bool call_dropped;          /**< inform that DMA TX has been stopped */
    bool call_initiated;        /**< check that DMA TX is active for audio I/O */
    bool call_suspended;        /**< check that DMA TX is suspended for audio I/O */
    bool st_enable;             /**< Sidetone enable flag */
    uint32 size;                /**< Size number of bytes per interrupt */
    ste_Thread_struct *audio_tx_thread; /**< Pointer to audio tx thread */
} tx_call_struct;

/**
 * AUDIO RX call parameters
 */
typedef struct
{
    short *p_rd;                /**< Reading pointer buffer */
    bool call_dropped;          /**< Flag to indicated call hang-up */
    bool call_initiated;        /**< Used to check that RX DMA is not already active to start RX DMA in case of voice call only */
    bool call_suspended;        /**< Flag to indicated call suspended */
    ste_Thread_struct *audio_rx_thread; /**< Ponter to audio rx thread */
} rx_call_struct;

/**
 * AUDIO Subsystem signal event
 */
typedef enum                /* Remark: These signals feed different state machines: to be furhter commented */
{
    SIG_NO_DATA = 0,
    SIG_FAR_IN,
    SIG_NEAR_IN,
    SIG_NEAR_OUT,
    SIG_STOP_UL_DL_IND,
    SIG_START_BOTH_DMA,
    SIG_RESTART_BOTH_DMA,
    SIG_START_GSC_AUDIO,
    SIG_START_EXTERNAL_LOOP,
    SIG_STOP_DL_DMA,
    SIG_DL_DMA_LAST_SUBFRAME_BEFORE_UNDERFLOW,
    SIG_START_TX_DMA,
    SIG_START_RX_DMA,
    SIG_FREQ_SAMPLE_SETUP,
    SIG_WOLFSON_CODEC,
    SIG_VULCAN_CODEC,
    SIG_UPDATE_AEC_DELAY_LINE,
    SIG_CHANGE_2PCM_IF,
    SIG_REQUEST_RESYNC,
    SIG_START_2ND_TX_DMA,
    SIG_START_2ND_RX_DMA,
    SIG_STOP_2ND_DL_DMA,
    SIG_STOP_2ND_UL_DMA,
    SIG_NEAR_IN_REF,
    SIG_FRAME_EDGE,
    MAX_NUM_AEC_TYPE
} aec_data_type;

/**
 * AUDIO AIO element queue
 */
typedef struct
{
    aec_data_type data_type;    /**< data type received to distingush different sources*/
    uint32        index;        /**< buffer index within all audio sample buffer range */
    uint32        sub_frame;    /**< buffer subframe index which change to each DMA transfer*/
    int16         *data;        /**< pointer to audio sample buffer */
} aio_element_queue;

/**
 * AUDIO AEC element queue
 */
typedef struct
{
    aec_data_type data_type;        /**< data type received to distingush different sources */
    int           *dual_mic_data;   /**< pointer to stereo sample buffer */
    short         *data;            /**< pointer to audio sample buffer */
} aec_element_queue;

/**
 * Stop audio DL callback
 */
typedef void (*drv_audio_dl_stop_cb_t)( void );

typedef struct AudioSyncLockRestartCbTag {
    void (*LockSynchronousRestart)( void );
    void (*UnlockSynchronousRestart)( void );
} AudioSyncLockRestartCb_t;

/*************************************************************************************************
 * Public variable declarations
 ************************************************************************************************/
/**
 * Sine table for testing purpose: 1kHz, 20ms @ Fs = 8kHz
 */
extern const int16 DXP_UNCACHED sine_table_160[NUM_SPEECH_SAMPLES_PER_FRAME];

/**
 * AEC queue handle
 */
extern os_QueueHandle DXP_CACHED_UNI1 AIO_Queue;

/**
 * Audio Samples Buffer in DL, FSI tx
 */
extern short DXP_UNCACHED DXP_A32 data_tx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME];

/**
 * Audio Samples Buffer in UL, FSI rx
 */
extern short DXP_UNCACHED DXP_A32 data_rx[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME];

/** 
 * Audio Samples Stereo Buffer in DL, FSI tx
 */
extern int32 data_stereo_tx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples Stereo Buffer in UL, FSI rx
 */
extern int32 data_stereo_rx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples Mono Buffer 16k in DL, FSI tx
 */
extern short data_tx_16k[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples mono Buffer 16k in UL, FSI rx
 */
extern short data_rx_16k[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples Stereo Buffer 16k in DL, FSI tx
 */
extern int32 data_stereo_tx_16k[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples Stereo Buffer 16k in UL, FSI rx
 */
extern int32 data_stereo_rx_16k[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

extern short second_port_data_tx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;
extern short second_port_data_rx[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;
extern int32 second_port_data_stereo_tx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;
extern int32 second_port_data_stereo_rx[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME] DXP_UNCACHED DXP_A32;
extern short second_port_data_tx_16k[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;
extern short second_port_data_rx_16k[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;
extern int32 second_port_data_stereo_tx_16k[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;
extern int32 second_port_data_stereo_rx_16k[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

/** 
 * Audio Samples Buffer in DL, FSI tx for Vulcan Codec
 */
extern short DXP_UNCACHED DXP_A32 data_tx_vulcan[NUM_SPEECH_BLOCK_TX][5*NUM_SPEECH_SAMPLES_PER_FRAME];

/**
 * Audio Samples Buffer in UL, FSI rx for Vulcan codec
 */
extern short DXP_UNCACHED DXP_A32 data_rx_vulcan[NUM_SPEECH_BLOCK_RX][5*NUM_SPEECH_SAMPLES_PER_FRAME]; 

extern short data_tx_vulcan_16k[NUM_SPEECH_BLOCK_TX][5*NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;
extern short data_rx_vulcan_16k[NUM_SPEECH_BLOCK_RX][5*NUM_SPEECH_SAMPLES_PER_FRAME_16K] DXP_UNCACHED DXP_A32;

/**
 * Audio Samples Buffer in DL, FSI tx for 8 bit companding mode
 * m-law or a-law
 */
extern uint8 DXP_UNCACHED DXP_A32 data_tx_comp[NUM_SPEECH_BLOCK_TX][NUM_SPEECH_SAMPLES_PER_FRAME];

/**
 * Audio Samples Buffer in UL, FSI rx for 8 bit companding mode
 * m-law or a-law
 */
extern uint8 DXP_UNCACHED DXP_A32 data_rx_comp[NUM_SPEECH_BLOCK_RX][NUM_SPEECH_SAMPLES_PER_FRAME];

/*************************************************************************************************
 * Public function declarations
 ************************************************************************************************/
/**
 * Audio driver init.
 *
 * This function will create and initialise mutex to be used when sending I2C cmd to Wolfson.
 * It will also plug DMA context handlers and eventually Plug Frame Sync detection
 *
 * @param multislot             true if PCM IF is multislot
 * @param master_not_slave      true if PCM IF is master
 * @param used_fsi_protocol     true if PCM IF is I2S
 * @param audio_dl_stop_cb      CB function pointer to stop DL audio
 *
 * @return void.
 */
extern void drv_audio_init (bool multislot, 
                            bool master_not_slave,
                            bool used_fsi_protocol, 
                            drv_audio_dl_stop_cb_t audio_dl_stop_cb,
                            drv_audio_dl_stop_cb_t second_audio_dl_stop_cb,
                            bool *hf_swap_channel,
                            bool *two_mics_swap
                            );

/**
 * Audio FSI init.
 *
 * This function will check that fsync detection interrupt 
 * handler has to be plugged and will plug it if not yet plugged
 *
 * @param multislot             true if PCM-IF is multislot, false 
 *                              otherwise
 *  
 * @param master_not_slave      true if PCM-IF is master, false 
 *                              otherwise
 *
 * @return void.
 */
extern void drv_audio_plug_fsync_detection (bool multislot, bool master_not_slave, bool used_fsi_protocol);

/**
 * Audio FSI init.
 *
 * This function will set the IT_PER_FRAME value.
 *
 * @param itPerFrame: new value
 *
 * @return void.
 */
extern void drv_audio_set_it_per_frame (uint8 itPerFrame);

/**
 * PCM LOOP enabling on driver side to ensure DMA transfer 
 * reprogrammed when pcm loop is active 
 *
 * This function will set the IT_PER_FRAME value.
 *
 * @param enable: true if to be enabled
 *
 * @return void.
 */
extern void drv_audio_enable_pcm_loop(bool enable);
/**
 * Wolfson codec initialisation function
 *
 * This function is responsible to initialise wolfson codec as
 * well as to program bclk,fs on audio FSI if Livanto works in
 * master mode. If Livanto works in slave mode then it will be
 * also responsible to setup blk and fs generation in Wolfson
 *
 * @param fs: frequency sample rate in Hz 
 * @param stereo_mode: flag to indicate if stereo mode has to be 
 *                   used
 * @param bclk: bit clock value in kHz to be choose between the 
 *            following 192, 256, 384, 512 , 640, 768, 1024,
 *            2048.
 *
 * @return bit_rate: bit_rate corresponding to numbers of bits 
 *         between two subsequent frames sync.
 */
extern uint32 drv_audio_init_wolfson(int fs,
                                     bool stereo_mode,
                                     int bclk);
#ifdef MODULE_TEST
extern uint32 drv_audio_init_wolfson_test(int fs,
                                          bool stereo_mode,
                                          int bclk);
#endif

/**
 * Wolfson codec FS function
 *
 * This function is responsible to initialise wolfson codec as 
 * well as to program bclk,fs on audio FSI if Livanto works in 
 * master mode. If Livanto works in slave mode then it will be 
 * also responsible to setup blk and fs generation in Wolfson 
 *
 * @param fs: frequency sample rate in Hz 
 * @param stereo_mode: specify if stereo mode has to be used 
 * @param bclk: bit clock value in kHz to be choose between the
 *            following 192, 256, 384, 512 , 640, 768, 1024,
 *            2048.
 *
 * @return bit_rate: bit_rate corresponding to numbers of bits
 *         between two subsequent frames sync.
 */
extern uint32 drv_audio_fs_select_wolfson(int fs,
                                          bool stereo_mode,
                                          int bclk,
                                          bool is_speakerphone,
                                          bool is_master
                                          );

/** 
 * Wolfson WM8991 speaker mode setup
 *  
 * This function is used to enable/disable speakerphone mode. 
 * Only for WM8991 can be used. 
 *  
 * @param is_speakerphone: of true it activates speakerphone 
 *                       mode
 */
extern void drv_audio_speaker_mode_select_wolfson(bool is_speakerphone);

/** 
 * Wolfson WM8991 master/slave PCM IF selection
 *  
 * This function is used to configure the PCM to work in 
 * master/slave mode. It also return the bit_rate providing fs 
 * and bit_clk 
 *  
 * @param fs
 * @param is_master 
 * @param stereo_mode 
 * @param bit_clk
 * 
 * @return int
 */
extern int drv_audio_master_slave_select_wolfson(int fs, 
                                                 bool is_master,
                                                 bool stereo_mode,
                                                 bool is_speakerphone,
                                                 int bit_clk);

/**
 * Wolfson sidetone activation
 *
 * This function is responsible to send I2C cmd to Wolfson which
 * allow internal sidetone generation. Sidetone volume is
 * fixed.
 *
 * @param void.
 *
 * @return void.
 */
extern void drv_wolfson_start_sidetone_on(void);

/**
 * Wolfson sidetone de-activation
 *
 * This function is responsible to send I2C cmd to Wolfson which
 * allow internal sidetone de-activation.
 *
 * @param void.
 *
 * @return void.
 */
extern void drv_wolfson_start_sidetone_off(void);

/**
 * Wolfson microphone volume setup
 *
 * This function is responsible to send I2C cmd to Wolfson which
 * allow to setup mic volume.
 *
 * @param in_volume_dB desired mic volume in dB.
 *
 * @return void.
 */
extern void drv_wolfson_set_mic_volume(int8 in_volume_dB);

/**
 * Wolfson speaker volume setup
 *
 * This function is responsible to send I2C cmd to Wolfson which
 * allow to setup speaker volume.
 *
 * @param in_volume_dB desired speaker volume in dB.
 *
 * @return void.
 */
extern void drv_wolfson_set_speaker_volume(int8 in_volume_dB);

/**
 * Vulcan audio codec support capability
 *
 * This function tells if the current audio driver supports 
 * vulcan audio codecs.
 *
 * @return true if supported otherwise false.
 */
extern bool drv_audio_vulcan_supported(void);

/**
 * stop fadeout support capability
 *
 * This function tells if the current audio driver supports the 
 * stop fadeout feature. 
 *
 * @return true if supported otherwise false.
 */
extern bool drv_audio_stop_fadeout_supported(void);

/** 
 * pause/restart by timer capability
 *  
 * This function tells if the current audio driver supports the 
 * pause/restart procedure using timer instead of DMAs IT 
 * 
 * @return bool
 */
extern bool drv_audio_is_pause_restart_by_timer(void);

/**
 * Vulcan audio codec initialisation
 *
 * This function is responsible to program audio fsi bclk and fs
 * when used in conjunction with vulcan (bclk=1280kHz and
 * fs=40000) as well as to initialse Vulcan from cold start.
 *
 * @param fs: frequecy sample rate
 * @param word_length
 *
 * @return void.
 */
extern void drv_audio_init_vulcan(int fs, int word_length);

/**
 * Vulcan audio codec start
 *
 * This function is responsible to program audio fsi bclk and fs
 * when used in conjunction with vulcan (bclk=1280kHz and
 * fs=40000) as well as to setup mic and speaker volume for
 * vulcan audio codec. To be used at beginnig of each speech
 * call.
 *
 * @param fs: frequecy sample rate
 * @param word_length
 *
 * @return void.
 */
extern void drv_audio_start_vulcan(int fs, int word_length);

/**
 *  Vulcan audio codec volume setup
 *
 * This function is responsible to setup mic volume for Vulcan.
 *
 * @param volume_dB desired mic volume in dB.
 *
 * @return void.
 */
extern void drv_audio_vulcan_mic_vol(int8 volume_dB);

/**
 * Vulcan audio codec speaker volume setup
 *
 * This function is responsible to setup speaker volume for
 * Vulcan.
 *
 * @param volume_dB desired speaker volume in dB.
 *
 * @return void.
 */
extern void drv_audio_vulcan_speaker_vol(int8 volume_dB);

/**
 * Vulcan audio codec sidetone volume setup
 *
 * This function is responsible to setup sidetone volume for
 * Vulcan.
 *
 * @param volume_dB desired sidetone volume in dB.
 *
 * @return void.
 */
extern void drv_audio_vulcan_sidetone_vol(int8 volume_dB);

/**
 * Vulcan audio codec level shifter enable
 *
 * This function is responsible to enable level shifer in
 * Vulcan. In this way Livanto can control switching on of
 * secondary PCM interface.
 *
 * @param void.
 *
 * @return void.
 */
extern void drv_audio_vulcan_ls_enable(void);
/**
 * Vulcan audio codec level shifter disable
 *
 * This function is responsible to disable level shifer in
 * Vulcan. In this way Livanto can control switching off of
 * secondary PCM interface.
 *
 * @param void.
 *
 * @return void.
 */
extern void drv_audio_vulcan_ls_disable(void);

/**
 * Vulcan audio codec mute secondary pcm flow
 *
 * This function is responsible to switch off secondary PCM
 * interface.
 *
 * @param void.
 *
 * @return void.
 */
extern void drv_audio_mute_bt_pcm(void);

/**
 * Vulcan audio codec unmute secondary pcm flow
 *
 * This function is responsible to switch on secondary PCM
 * interface.
 *
 * @param in_volume_dB to be used in the case we control an
 *                     external codec (i.e. Wolfson).
 *
 * @return void.
 */
extern void drv_audio_unmute_bt_pcm(int8 in_volume_dB);

/**
 * Vulcan audio codec disable
 *
 * This function is responsible to turn off audio codec within
 * Vulcan
 *
 * @param void
 *
 * @return void.
 */
extern void drv_audio_disable_vulcan(void);

/**
 * Chain descriptor creator for audio DMA access
 *
 * This function is responsible to create a chain of descriptors
 * associate to a buffer. In this way DMA access can start
 * to/from the specified buffer 
 *
 * @param id: Audio audio_if identifer (which also defines the 
 * direction of the transfer, as a audio_if is unidirectional). 
 * @param *buffer: audio buffer address where audio samples are
 *        stored to be txed/rxed
 * @param buffer_size: DMA transfer buffer size in bytes
 * @param word_width_16_not_8: it specifies if we transfer 16 or
 *                           8 bits words.
 * @param speech_block_size: total number of samples to be
 *                         transfered for each speech frame.
 *
 * @return number of elements in DMA chain
 */
int drv_audio_if_create_chain(drv_audio_if_id_t id,
                                 void *buffer,
                                 int buffer_size,
                                 bool word_width_16_not_8,
                                 bool stereo_mode,
                                 int speech_block_size,
                                 int num_speech_blocks);

/**
 * drv_audio_if_start_dma
 * 
 * Start DMA transfer on a given audio_if, starting from index.
 * 
 * @param id : audio audio_if identifier 
 * @param xte_handle : handle to XTE
 * @param index : element in DMA chain to start
 * @param xte_context : XTE context.
 */
void drv_audio_if_start_dma(drv_audio_if_id_t id, 
                              drv_XteHdl xte_handle,
                              int index,
                              int xte_context);

/**
 * drv_audio_if_stop_dma
 * 
 * Stop current DMA transfer on specified audio audio_if. 
 * The function uses the xte_handle and xte_context 
 * that were used to start the DMA transfer. 
 * 
 * @param id : audio audio_if identifier 
 */
void drv_audio_if_stop_dma(drv_audio_if_id_t id);

/**
 * Audio chain descriptors de-allocator for audio DMA
 *
 * This function is responsible to de-allocate audio descriptors
 * for audio DMA. Descriptors must be allocated with 
 * drv_audio_if_create_chain.
 *
 * @param id: Audio audio_if identifier. 
 *
 * @return void
 */
void drv_audio_if_free_chain(drv_audio_if_id_t id);


/**
 * drv_audio_if_lock 
 * drv_audio_if_unlock 
 * 
 * Locking functions to protect audio interface 
 * TX and RX can share the same mutex
 *  
 * @param id: audio interface identifier. 
 *  
 * @see drv_audio_if_init 
 */
void drv_audio_if_lock(drv_audio_if_id_t id);
void drv_audio_if_unlock(drv_audio_if_id_t id);

void drv_audio_if_init();

/**
 * Task creator to control end of a DMA transfer
 *
 * This function is responsible to create tasks to control end
 * of each audio DMA transfers.
 *
 * @param tx_not_rx: it specifies if the created Task will
 *                 control a audio DMA tx/rx transfer
 *
 * @return *ste_Thread_struct: pointer to task.
 */
extern ste_Thread_struct * drv_audio_register_dma_thread(bool tx_not_rx);

/** 
 * Task creator to control end of a DMA transfer to/from SSP1
 *
 * This function is responsible to create tasks to control end
 * of each audio DMA transfers.
 * 
 * 
 * @param tx_not_rx
 * 
 * @return ste_Thread_struct*
 */
extern ste_Thread_struct * drv_audio_register_dma_second_port_thread(bool tx_not_rx);

/**
 * Start audio DMA in tx 
 *
 * This function is responsible to start audio DMA in tx
 *
 * @param *tx_call_config: pointer to call config structure for
 *        tx
 *
 * @return void
 */

/**
 * Enable DRIFT_COMPENSATION 
 *
 * This function is responsible to enable drift compensation
 *
 * @param enable_drift: bit field for enabling : Tx2-Rx2-Tx1-Rx1
 *
 * @return void
 */
extern void drv_audio_enable_drift_compensation(uint8 enable_drift);

/**
 * Enable PPM_ESTIMATION
 *
 * This function is responsible to enable ppm estimation
 *
 * @param estimate_ppm: bit field for enabling : Tx2-Rx2-Tx1-Rx1
 *
 * @return void
 */
extern void drv_audio_enable_ppm_estimation(uint8 estimate_ppm);

/**
 * Enable USI_FS_ESTIMATION
 *
 * This function is responsible to enable usi fs estimation
 *
 * @param estimate_usi_fs: bit field for enabling : Tx2-Rx2-Tx1-Rx1
 *
 * @return void
 */
extern void drv_audio_enable_usi_fs_estimation(uint8 estimate_usi_fs);

extern void drv_audio_start_tx_dma(tx_call_struct *tx_call_config);

/**
 * Start audio DMA in tx for 2nd audio port
 *
 * This function is responsible to start audio DMA in tx for 2nd audio port
 *
 * @param *tx_call_config: pointer to call config structure for
 *        tx
 *
 * @return void
 */
extern void drv_audio_start_tx_dma_second_port(tx_call_struct *tx_call_config);

/** 
 * Send event to start 2nd audio port for recording: used only 
 * on t148 case 
 * 
 * @param tx_call_config
 */
extern void drv_audio_send_start_tx_dma_second_port(tx_call_struct *tx_call_config);

/**
 * Start audio DMA in rx
 *
 * This function is responsible to start audio DMA in rx
 *
 * @param *rx_call_config: pointer to call config structure for
 *        rx
 *
 * @return void
 */
extern void drv_audio_start_rx_dma(rx_call_struct *rx_call_config);

/** 
 * Start audio DMA in rx fpr 2nd audio port
 *
 * This function is responsible to start audio DMA in rx using 
 * 2nd audio port 
 * 
 * 
 * @param rx_call_config
 */
extern void drv_audio_start_rx_dma_second_port(rx_call_struct *rx_call_config);

/**
 * Stop audio DMA in tx
 *
 * This function is responsible to stop audio DMA in tx
 *
 * @param *tx_call_config: pointer to call config structure for
 *        tx
 *
 * @return void
 */
extern void drv_audio_stop_tx_dma(tx_call_struct *tx_call_config);

/**
 * Stop audio DMA in tx for 2nd audio port
 *
 * This function is responsible to stop audio DMA in tx
 *
 * @param *tx_call_config: pointer to call config structure for
 *        tx
 *
 * @return void
 */
extern void drv_audio_stop_tx_dma_second_port(tx_call_struct *tx_call_config);

/**
 * Stop audio DMA in rx
 *
 * This function is responsible to stop audio DMA in rx
 *
 * @param *rx_call_config: pointer to call config structure for
 *        rx
 *
 * @return void
 */
extern void drv_audio_stop_rx_dma(rx_call_struct *rx_call_config);

/** 
 * Stop audio DMA in rx for 2nd audio port
 *
 * This function is responsible to stop audio DMA in rx
 * 
 * @param rx_call_config
 */
extern void drv_audio_stop_rx_dma_second_port(rx_call_struct  *rx_call_config);

/**
 * Audio chain descriptors de-allocator for audio DMA in tx
 *
 * This function is responsible to de-allocate audio descriptors
 * for audio tx DMA
 *
 * @param buffer_size: audio DMA transfer size in byte 
 * @param stereo_mode: flag to indicate if in stereo mode 
 * @param speech_block_size: speech frame size 
 *
 * @return void
 */
extern void drv_audio_free_tx_chain(int buffer_size,
                                    bool stereo_mode,   
                                    int speech_block_size);
/** 
 * Audio chain descriptors de-allocator for 2nd audio DMA in tx
 *
 * This function is responsible to de-allocate audio descriptors
 * for 2nd audio tx DMA
 * 
 * 
 * @param buffer_size
 * @param stereo_mode
 * @param speech_block_size
 */
extern void drv_audio_free_tx_chain_second_port(int buffer_size,
                                             bool stereo_mode,
                                             int speech_block_size);

extern void drv_audio_free_rx_chain(int buffer_size,
                                    bool stereo_mode,   
                                    int speech_block_size);

/** 
 * Audio chain descriptors de-allocator for 2nd audio DMA in rx
 *
 * This function is responsible to de-allocate audio descriptors
 * for 2nd audio rx DMA
 * 
 * @param buffer_size
 * @param stereo_mode
 * @param speech_block_size
 */
void drv_audio_free_rx_chain_second_port(int buffer_size,
                                      bool stereo_mode,
                                      int speech_block_size);

/**
 * Audio FSI open function for Vulcan
 *
 * This function is responsible to program audio FSI interface 
 * to deal with Vulcan PCM flow (i.e. bclk = 32*fs kHz and
 * fs=5*processing sampling frequency, due to oversampling in 
 * Vulcan audio codec) 
 *
 * @param void
 * @return void
 */
extern void drv_audio_open_vulcan(int fs);

/**
 * Audio FSI open function for Wolfson (i.e. secondary PCM flow
 * intended for BT device)
 *
 * This function is responsible to to program and open audio FSI
 * interface to deal with external BT device. Since the external
 * audio codec could is unknown this interface can be programmed
 * specifying desired bit_rate and word_width
 *
 * @param bit_rate: pcm flow bit rate in kbit/s (24, 32, 48, 64,
 *                80, 96, 128, 256)
 * @param word_width: word width in bit (8 or 16)
 * @param short_not_long: it specifies short or long frame sync
 * @param master_not_slave: it specifies if livanto PCM if acts
 *                        as master or slave
 *
 * @return void
 */
extern void drv_audio_open_wolfson(uint32 bit_rate,
                                   uint32 word_width,
                                   bool short_not_long,
                                   bool master_not_slave,
                                   tx_call_struct *tx_dma_config,
                                   rx_call_struct *rx_dma_config,
                                   bool start_tx_dma,
                                   bool start_rx_dma,
                                   uint8 freq_sample
                                   );
/** 
 * 2nd audio FSI open function using SSP1 port (i.e. for voice 
 * call recording) 
 * 
 * @param tx_dma_config
 * @param rx_dma_config
 */
extern void drv_audio_fsi_open_wolfson_second_port(tx_call_struct *tx_dma_config,
                                                   rx_call_struct *rx_dma_config,
                                                   bool start_tx_dma,
                                                   bool start_rx_dma);
/**
 * Audio FSI close
 *
 * This function is responsible close audio FSI
 *
 * @param void
 * @return void
 */
extern void drv_audio_fsi_close(void);

/**
 * Audio tasks creator
 *
 * This function is responsible to create AudioProcessing_Task
 * and AudioIO_task and their respective queues AudioAec_Queue
 * and AudioIO_Queue.
 *
 * @param void
 * @return void
 */
extern void audio_CreateAudioTask(void);

/**
 * drv_audio_os_uist_time
 *
 * To be used with dxp_run_time_reading.m that enables to plot
 * timing instants and compute drift
 *
 * This function is responsible to uist the current time based
 * on on 15.36 MHz clock ticks
 *
 * @param uist_tag : tag to identify timing location 
 * @param delay : to add delay in reported time 
 *
 *
 * @return void
 */
extern void drv_audio_os_uist_time(uint16 uist_tag, uint16 delay) ;

/**
 * drv_audio_os_uist_block
 *
 * To be used with dxp_run_block_reading.m that enables to
 * collect parameters and plot them
 *
 * This function is responsible uist a block of parameters with
 * os_uist. First line displays handle, second line size, other
 * lines parameters
 *
 * @param handle : handle to block
 * @param size   : size of block (nb of parameters)
 * @param *param : parameters pointer
 *
 *
 * @return void
 */
extern void drv_audio_os_uist_block(int handle, int size, int *param);

/**
 * drv_audio_uist_dl_frame_written
 *
 * This function is responsible to update timing logs for DL
 *
 * @param pad_of_samples: dl pad which will be converted in delay
 * @param update_delay: control delay line update every 20ms
 * @return none
 */
extern void drv_audio_uist_dl_frame_written(short pad_of_samples, bool update_delay);

/**
 * drv_audio_update_2g_timing
 *
 * This function is responsible to update timing for audio
 * synchro control thanks to 2g modem information
 *
 * @param uplink_audio_delay : 20ms DMA relative edge in UL
 * @param downlink_audio_delay: 20ms DMA relative edge in DL
 * @return none
 */
extern void drv_audio_update_2g_timing(uint16 uplink_audio_delay, uint16 downlink_audio_delay);

/**
 * drv_audio_update_3g_timing
 *
 * This function is responsible to update timing for audio
 * synchro control thanks to 3g modem information
 *
 * @param next_timing : absolute time of DMA edge or reference 
 *                    to start with
 * @param take_reference: tell if reference to be taken
 * @return none
 */
extern void drv_audio_update_3g_timing(uint32 next_timing, bool take_reference);

/**
 * drv_ola_audio_sub_frames
 *
 * Generic function that Overlapp Adds audio subframes for time
 * re-scaling
 *
 * @param pdest : destination subframe pointer
 *                   loss
 * @return void
 */
extern void drv_audio_ola_sub_frames(short*pdest, short* pfadeout, short* pfadein, uint8 nb_of_sub, uint8 Fs);

/**
 * drv_ola_audio_sub_frames_stereo
 *
 * Generic function that Overlapp Adds audio subframes for time
 * re-scaling
 *
 * @param pdest : destination subframe pointer
 *                   loss
 * @return void
 */
extern void drv_audio_ola_sub_frames_stereo(int32 *pdest_stereo, int32* pfadeout_stereo, int32* pfadein_stereo, uint8 nb_of_sub, uint8 Fs);

/**
 * drv_audio_positive_delta_time
 *
 * Function that computes positive uint32 time difference
 * including uint32 wrapping
 *
 * @param new_time : bigger time
 *
 * @param old_time : smaller time
 *
 * @return positive time difference
 */
extern uint32 drv_audio_positive_delta_time(uint32 new_time, uint32 old_time);

extern void drv_audio_uist_dl_frame_written_second_port(short pad_of_samples, bool update_delay);
extern void drv_audio_second_fsi_close();
extern void drv_audio_second_fsi_ul_close();
extern void drv_audio_second_fsi_dl_close();
extern void drv_audio_bitclk();
#ifdef MODULE_TEST
extern void drv_audio_gut_open(int bclk);
#endif

/** 
 * drv_audio_open_rx
 *  
 * Hack to ensure AHUB RX asserts READY signal before the first call.
 */
extern void drv_audio_open_rx(uint32 bit_rate,
                       uint32 word_width,
                       bool short_not_long,
                       bool master_not_slave,
                       tx_call_struct *tx_dma_config,
                       rx_call_struct *rx_dma_config,
                       bool start_tx_dma,
                       bool start_rx_dma,
                       uint8 freq_sample
                       );

extern void drv_audio_registerSyncLockCb(const AudioSyncLockRestartCb_t * const cb);

#endif
/** @} END OF FILE */
