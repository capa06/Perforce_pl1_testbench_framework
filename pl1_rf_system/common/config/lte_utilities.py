#-------------------------------------------------------------------------------
# Name:        lte_utilities
# Purpose:
#
# Author:      joashr
#
# Created:     05/06/2014
# Copyright:   (c) joashr 2014
# Licence:
#-------------------------------------------------------------------------------

import sys, os, re

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *

ul_EARFCN_table={
    #FUL_low , Range of Nul(NOffs-UL, Upper EARFN) #

  1 :  [ 1920,   18000,   18599],
  2 :  [ 1850,   18600,   19199],
  3 :  [ 1710,   19200,   19949],
  4 :  [ 1710,   19950,   20399],
  5 :  [ 824,    20400,   20649],
  6 :  [ 830,    20650,   20749],
  7 :  [ 2500,   20750,   21449],
  8 :  [ 880,    21450,   21799],
  9 :  [ 1749.9, 21800,   22149],
 10 :  [ 1710,   22150,   22749],
 11 :  [ 1427.9, 22750,   22999],
 12 :  [ 698,    23000,   23179],
 13 :  [ 777,    23180,   23279],
 14 :  [ 788,    23280,   23379],
 15 :  [ 0,      0,       0],
 16 :  [ 0,      0,       0],
 17 :  [ 704,    23730,   23849],
 18 :  [ 815,    23850,   23999],
 19 :  [ 830,    24000,   24149],
 20 :  [ 832,    24150,   24449],
 21 :  [ 1447.9, 24450,   24599],
 22 :  [ 3410,   24600,   25399],
 23 :  [ 2000,   25500,   25699],
 24 :  [ 1626.5, 25700,   26039],
 25 :  [ 1850,   26040,   26689],
 26 :  [ 814,    26690,   27039],
 27 :  [ 807,    27040,   27209],
 28 :  [ 703,    27210,   27659],
 29 :  [ 0,      0,       0],
 30 :  [ 2305,   27660,   27759],
 31 :  [ 452.5,  27760,   27809],
 32 :  [ 0,      0,       0],
 33 :  [ 1900,   36000,   36199],
 34 :  [ 2010,   36200,   36349],
 35 :  [ 1850,   36350,   36949],
 36 :  [ 1930,   36950,   37549],
 37 :  [ 1910,   37550,   37749],
 38 :  [ 2570,   37750,   38249],
 39 :  [ 1880,   38250,   38649],
 40 :  [ 2300,   38650,   39649],
 41 :  [ 2496,   39650,   41589],
 42 :  [ 3400,   41590,   43589],
 43 :  [ 3600,   43590,   45589],

}

dl_EARFCN_table={
    #FUL_low , Range of Nul(NOffs-UL, Upper EARFN)
  1 : [ 2110,   0,       599],    
  2 : [ 1930,   600,     1199],   
  3 : [ 1805,   1200,    1949],   
  4 : [ 2110,   1950,    2399],   
  5 : [ 869,    2400,    2649],   
  6 : [ 875,    2650,    2749],   
  7 : [ 2620,   2750,    3449],   
  8 : [ 925,    3450,    3799],   
  9 : [ 1844.9, 3800,    4149],   
 10 : [ 2110,   4150,    4749],   
 11 : [ 1475.9, 4750,    4999],   
 12 : [ 728,    5000,    5179],   
 13 : [ 746,    5180,    5279],   
 14 : [ 758,    5280,    5379],   
 15 : [ 0,      0,       0],      
 16 : [ 0,      0,       0],      
 17 : [ 734,    5730,    5849],   
 18 : [ 860,    5850,    5999],   
 19 : [ 875,    6000,    6149],   
 20 : [ 791,    6150,    6449],   
 21 : [ 1495.9, 6450,    6599],   
 22 : [ 3510,   6600,    7399],   
 23 : [ 2180,   7500,    7699],   
 24 : [ 1525,   7700,    8039],   
 25 : [ 1930,   8040,    8689],   
 26 : [ 859,    8690,    9039],   
 27 : [ 852,    9040,    9209],   
 28 : [ 758,    9210,    9659],   
 29 : [ 717,    9660,    9769],   
 30 : [ 2350,   9770,    9869],   
 31 : [ 462.5,  9870,    9919],   
 32 : [ 0,      0,       0],      
 33 : [ 1900,   36000,   36199],  
 34 : [ 2010,   36200,   36349],  
 35 : [ 1850,   36350,   36949],  
 36 : [ 1930,   36950,   37549],  
 37 : [ 1910,   37550,   37749],  
 38 : [ 2570,   37750,   38249],  
 39 : [ 1880,   38250,   38649],  
 40 : [ 2300,   38650,   39649],  
 41 : [ 2496,   39650,   41589],  
 42 : [ 3400,   41590,   43589],  
 43 : [ 3600,   43590,   45589],
} 


def ul_Default_EARFCN(band):
    return ( ul_EARFCN_table[band][1] + ul_EARFCN_table[band][2] + 1 ) * 0.5

def dl_Default_EARFCN(band):
    return ( dl_EARFCN_table[band][1] + dl_EARFCN_table[band][2] + 1 ) * 0.5


def get_ul_freq(earfcn, band):

    ful = ul_EARFCN_table[band][0] + 0.1 * (earfcn - ul_EARFCN_table[band][1])

    return ful

def get_dl_freq(earfcn, band):

    fdl = dl_EARFCN_table[band][0] + 0.1 * (earfcn - dl_EARFCN_table[band][1])

    return fdl


def create_dl_earfcn_freq_band_map_dic():
    earfcn_freq_band_dict = {}
    bandList = dl_EARFCN_table.keys()
    for band in bandList:
        earfcn_min = dl_EARFCN_table[band][1]
        earfcn_curr = dl_EARFCN_table[band][1]
        earfcn_max = dl_EARFCN_table[band][2]
        while earfcn_curr <= earfcn_max:
            freq = get_dl_freq(earfcn_curr,band)
            earfcn_freq_band_dict[earfcn_curr] = {}
            earfcn_freq_band_dict[earfcn_curr]['freq'] = freq
            earfcn_freq_band_dict[earfcn_curr]['band'] = band
            earfcn_freq_band_dict[earfcn_curr]['index'] = earfcn_curr - earfcn_min
            earfcn_curr += 1

    return earfcn_freq_band_dict

def create_ul_earfcn_freq_band_map_dic():
    earfcn_freq_band_dict = {}
    bandList = ul_EARFCN_table.keys()
    for band in bandList:
        earfcn_min = ul_EARFCN_table[band][1]
        earfcn_curr = ul_EARFCN_table[band][1]
        earfcn_max = ul_EARFCN_table[band][2]
        while earfcn_curr <= earfcn_max:
            freq = get_ul_freq(earfcn_curr,band)
            earfcn_freq_band_dict[earfcn_curr] = {}
            earfcn_freq_band_dict[earfcn_curr]['freq'] = freq
            earfcn_freq_band_dict[earfcn_curr]['band'] = band
            earfcn_freq_band_dict[earfcn_curr]['index'] = earfcn_curr - earfcn_min
            earfcn_curr += 1

    return earfcn_freq_band_dict

def get_lte_ul_dl_freq_band (earfcn):
    dl_look_up_dict = create_dl_earfcn_freq_band_map_dic()
    ul_look_up_dict = create_ul_earfcn_freq_band_map_dic()
    freq_ul = 0
    freq_dl = 0
    band = 0

    if earfcn in dl_look_up_dict.keys():
        freq_dl = dl_look_up_dict[earfcn]['freq']
        band = dl_look_up_dict[earfcn]['band']
        idx = dl_look_up_dict[earfcn]['index']

        for key in ul_look_up_dict.keys():
            if idx == ul_look_up_dict[key]['index'] and band == ul_look_up_dict[key]['band']:
                freq_ul = ul_look_up_dict[key]['freq']

    elif earfcn in ul_look_up_dict.keys():
        freq_ul = ul_look_up_dict[earfcn]['freq']
        band = ul_look_up_dict[earfcn]['band']
        idx = ul_look_up_dict[earfcn]['index']

        for key in dl_look_up_dict.keys():
            if idx == dl_look_up_dict[key]['index'] and band == dl_look_up_dict[key]['band']:
                freq_dl = dl_look_up_dict[key]['freq']

    else:
        raise ValueError("EARFCN not found")

    return band,freq_ul,freq_dl

def get_lte_dl_freq_band(earfcn):
    # from uarfcn get channel freq
    look_up_dict = create_dl_earfcn_freq_band_map_dic()
    freq = 0
    band = 0
    try:
        freq = look_up_dict[earfcn]['freq']
        band = look_up_dict[earfcn]['band']
    except KeyError:
        print "earfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(dl_UARFCN_table.keys())
        return freq,band

    return freq,band

def get_lte_ul_freq_band(earfcn):
    # from uarfcn get channel freq
    look_up_dict = create_ul_uarfcn_freq_band_map_dic()
    freq = 0
    band = 0
    try:
        freq = look_up_dict[earfcn]['freq']
        band = look_up_dict[earfcn]['band']
    except KeyError:
        print "earfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(ul_UARFCN_table.keys())
        return freq,band

    return freq,band

if __name__ == '__main__':

    band,freq_ul,freq_dl = get_lte_ul_dl_freq_band(8366)
    print "Band %d, Freq_UL %f, Freq_DL %f" % (band,freq_ul,freq_dl)
