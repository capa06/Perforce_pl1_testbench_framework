#-------------------------------------------------------------------------------
# Name:        wcdma test_plan
# Purpose:
#
# Author:      joashr
#
# Created:     19/11/2013
# Copyright:   (c) joashr 2013
#               CMW Test Plan (3G)
#-------------------------------------------------------------------------------

from umts_utilities import *
"""
supported RMC date rates, as follows
dl_R12K2_ul_R12K2
dl_R12K2_ul_R64K
dl_R12K2_ul_R144k
dl_R12K2_ul_R384k
dl_R12K2_ul_R768k
dl_R64K_ul_R12K2
dl_R64K_ul_R64K
dl_R64K_ul_R144k
dl_R64K_ul_R384k
dl_R64K_ul_R768k
dl_R144k_ul_R12K2
dl_R144k_ul_R64K
dl_R144k_ul_R144k
dl_R144k_ul_R384k
dl_R144k_ul_R768k
dl_R384k_ul_R12K2
dl_R384k_ul_R64K
dl_R384k_ul_R144k
dl_R384k_ul_R384k
dl_R384k_ul_R768k
"""

test_plan_master= {
0  : {   'TESTTYPE'   : 'BLER_PERF',
         'DATARATE'   : ['dl_R12k2_ul_R12k2', 'dl_R64K_ul_R64K',
                         'dl_R144k_ul_R144k', 'dl_R384k_ul_R384k'],
         'RFBAND'     : [1],
         'UARFCN'     : { 1: [default_uarfcn(band=1)] },
         'CHTYPE'     : ['None'],
         'SNR'        : [30],
         'RFPOWER'    : [-50],
         'TXANTS'     : [1]

    },


1  : {   'TESTTYPE'          : 'HSPA_BLER_PERF',
         'DATARATE'          : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
         'RFBAND'            : [1],
         'UARFCN'            : { 1: [default_uarfcn(band=1)] },
         'CHTYPE'            : ['None'],
         'SNR'               : [30],
         'RFPOWER'           : [-57],
         'TXANTS'            : [1],
         'SCHEDTYPE'         : ['UDCH'],
         'INTER_TTI'         : [1],   # note that this will not be looped
         'NUM_HARQ_PROC'     : [6],   # note that this will not be looped
         'Ki'                : [62],
         'NUM_HSDSCH_CODES'  : [5, 10, 15],
         'MODULATION'        : ['QPSK', '16-QAM', '64-QAM'], # supported modulations QPSK, 16-QAM, 64-QAM
       },


2  : {   'TESTTYPE'            : 'DCHSDPA_BLER_PERF',
         'DATARATE'            : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
         'RFBAND'              : [1], # separation between carriers is fixed at 5 MHz
         'UARFCN'              : { 1: [default_uarfcn(band=1)] },
         'CHTYPE'              : ['None'],
         'SNR_1'               : [30],
         'SNR_2'               : [30],
         'RFPOWER_1'           : [-54],
         'RFPOWER_2'           : [-54],
         'TXANTS'              : [1],
         'SCHEDTYPE'           : ['UDCH'],
         'INTER_TTI_1'         : [1],   # note that this will not be looped
         'INTER_TTI_2'         : [1],   # note that this will not be looped
         'NUM_HARQ_PROC'       : [6],   # note that this will not be looped
         'Ki_1'                : [62],
         'Ki_2'                : [62],
         'NUM_HSDSCH_CODES_1'  : [15],
         'NUM_HSDSCH_CODES_2'  : [15],
         'MODULATION_1'        : ['64-QAM'], # supported modulations QPSK, 16-QAM, 64-QAM
         'MODULATION_2'        : ['64-QAM'] # supported modulations QPSK, 16-QAM, 64-QAM
       },


10 :{    'TESTTYPE'   : 'BLER_PERF',
         'DATARATE'   : ['dl_64kbps_ul_64kbps', 'dl_R12k2_ul_R12k2'],
         'RFBAND'     : [1],
         'UARFCN'     : { 1: [default_uarfcn(band=1)], 5:[default_uarfcn(band=5)]},
         'CHTYPE'     : ['None'],
         'SNR'        : [30],
         'RFPOWER'    : [-70],
         'TXANTS'     : [1]
    },



11  : {   'TESTTYPE'   : 'BLER_PERF',
         'DATARATE'   : ['dl_12kbp_ul_12kbps'],
         'RFBAND'     : [1],
         'UARFCN'     : { 1: [default_uarfcn(band=1)]},
         'CHTYPE'     : ['None'],
         'SNR'        : [30, 20],
         'RFPOWER'    : [-70],
         'TXANTS'     : [1]
       },


101 : {  'TESTTYPE'          : 'HSPA_FADING_PERF',
         'DATARATE'          : ['dl_Hsdpa_ul_R12k2'],               # note that this will not be looped
         'RFBAND'            : [1,2,5],
         'UARFCN'            : {1: [10563], 2: [9663], 5: [4358]},
         'CHTYPE'            : ['PA3','PB3','VA30','VA12'],         # Fading profile (Channel type) PA3, PB3, VA30, VA12
         'SNR'               : [30,25,20,15,10,5,0,-5],
         'RFPOWER'           : [-60],
         'TXANTS'            : [1],
         'SCHEDTYPE'         : ['FOLLOW_CQI'],
         'INTER_TTI'         : [1],                                 # note that this will not be looped
         'NUM_HARQ_PROC'     : [6],                                 # note that this will not be looped
         'CPICH_POWER'       : [-10],
         'HSPDSCH_POWER'     : [-6]
       },


201 : {  'TESTTYPE'   : 'BLER_INTRAHO_ALL',
         'DATARATE'   : ['dl_R12k2_ul_R12k2'],
         'RFBAND'     : [1],
         'UARFCN'     : { 1: [default_uarfcn(band=1)]},
         'CHTYPE'     : ['None'],
         'SNR'        : [30],
         'RFPOWER'    : [-50],
         'TXANTS'     : [1]
       },

    #HHO to a selection of uarfcn within the band specified
    #mid - > bot
    #bot -> mid
    #mid -> bot
    #bot -> top
    #top -> bot
    #bot -> mid
    #mid -> top
    #top -> mid


202 : {  'TESTTYPE'   : 'BLER_INTRAHO_DEFAULT',
         'DATARATE'   : ['dl_R12k2_ul_R12k2'],
         'RFBAND'     : [2],
         'UARFCN'     : { 2: [default_uarfcn(band=2)]},
         'CHTYPE'     : ['None'],
         'SNR'        : [30],
         'RFPOWER'    : [-50],
         'TXANTS'     : [1]
       },


203  : {   'TESTTYPE'          : 'HSPA_BLER_INTRAHO_DEFAULT',
           'DATARATE'          : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
           'RFBAND'            : [1],
           'UARFCN'            : { 1: [default_uarfcn(band=1)] },
           'CHTYPE'            : ['None'],
           'SNR'               : [30],
           'RFPOWER'           : [-57],
           'TXANTS'            : [1],
           'SCHEDTYPE'         : ['UDCH'],
           'INTER_TTI'         : [1],   # note that this will not be looped
           'NUM_HARQ_PROC'     : [6],   # note that this will not be looped
           'Ki'                : [62],
           'NUM_HSDSCH_CODES'  : [5],
           'MODULATION'        : ['QPSK'], # supported modulations QPSK, 16-QAM, 64-QAM
       },


204  : {   'TESTTYPE'          : 'HSPA_BLER_INTRAHO_ALL',
           'DATARATE'          : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
           'RFBAND'            : [1],
           'UARFCN'            : { 1: [default_uarfcn(band=1)] },
           'CHTYPE'            : ['None'],
           'SNR'               : [30],
           'RFPOWER'           : [-57],
           'TXANTS'            : [1],
           'SCHEDTYPE'         : ['UDCH'],
           'INTER_TTI'         : [1],   # note that this will not be looped
           'NUM_HARQ_PROC'     : [6],   # note that this will not be looped
           'Ki'                : [62],
           'NUM_HSDSCH_CODES'  : [5],
           'MODULATION'        : ['QPSK'], # supported modulations QPSK, 16-QAM, 64-QAM
       },


205  : {    'TESTTYPE'            : 'DCHSDPA_BLER_INTRAHO_DEFAULT',
            'DATARATE'            : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
            'RFBAND'              : [1], # separation between carriers is fixed at 5 MHz
            'UARFCN'              : { 1: [default_uarfcn(band=1)] },
            'CHTYPE'              : ['None'],
            'SNR_1'               : [30],
            'SNR_2'               : [30],
            'RFPOWER_1'           : [-57],
            'RFPOWER_2'           : [-57],
            'TXANTS'              : [1],
            'SCHEDTYPE'           : ['UDCH'],
            'INTER_TTI_1'         : [1],   # note that this will not be looped
            'INTER_TTI_2'         : [1],   # note that this will not be looped
            'NUM_HARQ_PROC'       : [6],   # note that this will not be looped
            'Ki_1'                : [62],
            'Ki_2'                : [62],
            'NUM_HSDSCH_CODES_1'  : [15],
            'NUM_HSDSCH_CODES_2'  : [15],
            'MODULATION_1'        : ['64-QAM'], # supported modulations QPSK, 16-QAM, 64-QAM
            'MODULATION_2'        : ['64-QAM'] # supported modulations QPSK, 16-QAM, 64-QAM
       },


206  : {   'TESTTYPE'            : 'DCHSDPA_BLER_INTRAHO_ALL',
           'DATARATE'            : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
           'RFBAND'              : [1], # separation between carriers is fixed at 5 MHz
           'UARFCN'              : { 1: [default_uarfcn(band=1)] },
           'CHTYPE'              : ['None'],
           'SNR_1'               : [30],
           'SNR_2'               : [30],
           'RFPOWER_1'           : [-57],
           'RFPOWER_2'           : [-57],
           'TXANTS'              : [1],
           'SCHEDTYPE'           : ['UDCH'],
           'INTER_TTI_1'         : [1],   # note that this will not be looped
           'INTER_TTI_2'         : [1],   # note that this will not be looped
           'NUM_HARQ_PROC'       : [6],   # note that this will not be looped
           'Ki_1'                : [62],
           'Ki_2'                : [62],
           'NUM_HSDSCH_CODES_1'  : [15],
           'NUM_HSDSCH_CODES_2'  : [15],
           'MODULATION_1'        : ['64-QAM'], # supported modulations QPSK, 16-QAM, 64-QAM
           'MODULATION_2'        : ['64-QAM'] # supported modulations QPSK, 16-QAM, 64-QAM
        },

        # HHO to a selection of uarfcn within the bands configured for the device
        # cycles from bottom for band X to top of band Y then
        # from top of Band Y to bottom of band Z


220  : {   'TESTTYPE'          : 'BLER_INTERBAND_DEFAULT',
           'DATARATE'          : ['dl_Hsdpa_ul_Hsupa'], # note that this will not be looped
           'RFBAND'            : [1, 2, 3, 4, 5, 6, 7, 8],
           'CHTYPE'            : ['None'],
           'SNR'               : [30],
           'RFPOWER'           : [-57],
           'TXANTS'            : [1],
           'SCHEDTYPE'         : ['UDCH'],
           'INTER_TTI'         : [1],   # note that this will not be looped
           'NUM_HARQ_PROC'     : [6],   # note that this will not be looped
           'Ki'                : [62],
           'NUM_HSDSCH_CODES'  : [5],
           'MODULATION'        : ['QPSK'], # supported modulations QPSK, 16-QAM, 64-QAM
       },

}


test_plan = test_plan_master.copy()

if __name__ == '__main__':
    testID_list = sorted(test_plan.keys())
    print "testIDs = %s" % testID_list

    for testID in testID_list:
        print "----------------------------"
        print "testID = %s" % testID
        print " --> %s" % test_plan[testID]

