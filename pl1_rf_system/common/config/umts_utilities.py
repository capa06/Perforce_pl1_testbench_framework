#-------------------------------------------------------------------------------
# Name:        umts_utilities
# Purpose:
#
# Author:      joashr
#
# Created:     05/06/2014
# Copyright:   (c) joashr 2014
# Licence:
#-------------------------------------------------------------------------------

import sys, os, re

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *


dl_UARFCN_table={
    #FDL_Offset, FDL_low, FDL_High #
  1:[0, 2112.4, 2167.6],
  2:[0,	1932.4,	1987.6],
  3:[1575, 1807.4, 1877.6],
  4:[1805, 2112.4, 2152.6],
  5:[0, 871.4, 891.6],
  6:[0, 877.4, 882.6],
  7:[2175, 2622.4, 2687.6],
  8:[340, 927.4, 957.6],
  9:[0, 1847.4, 1877.4],
 10:[1490, 2112.4, 2167.6],
 11:[736, 1478.4, 1493.4],
 12:[-37, 731.4, 743.6],
 13:[-55, 748.4, 753.6],
 14:[-63, 760.4, 765.6],
 19:[735, 877.4, 887.6],
 20:[-109, 793.4, 818.6],
 21:[1326, 1498.4, 1508.4],
 22:[2580, 3512.4, 3587.6],
 25:[910, 1932.4, 1992.6],
 26:[-291, 861.4, 891.6]
}

ul_UARFCN_table={
    #FUL_Offset, FUL_low, FUL_High #
  1:[0, 1922.4, 1977.6],
  2:[0,	1852.4,	1907.6],
  3:[1525, 1712.4, 1782.6],
  4:[1450, 1712.4, 1752.6],
  5:[0, 826.4, 846.6],
  6:[0, 832.4, 837.6],
  7:[2100, 2502.4, 2567.6],
  8:[340, 882.4, 912.6],
  9:[0, 1752.4, 1782.4],
 10:[1135, 1712.4, 1767.6],
 11:[733, 1430.4, 1445.4],
 12:[-22, 701.4, 713.6],
 13:[21, 779.4, 784.6],
 14:[12, 790.4, 795.6],
 19:[770, 832.4, 842.6],
 20:[-23, 834.4, 859.6],
 21:[1358, 1450.4, 1460.4],
 22:[2525, 3412.4, 3487.6],
 25:[875, 1852.4, 1912.6],
 26:[-291, 816.4, 846.6]
}

dl_additional_freqs={
2: [1932.5, 1937.5, 1942.5, 1947.5, 1952.5, 1957.5, 1962.5, 1967.5, 1972.5, 1977.5, 1982.5, 1987.5],
4: [2112.5, 2117.5, 2122.5, 2127.5, 2132.5, 2137.5, 2142.5, 2147.5, 2152.5],
5: [871.5, 872.5, 876.5, 877.5, 882.5, 887.5],
6: [877.5, 882.5],
7: [2622.5, 2627.5, 2632.5,
    2637.5, 2642.5, 2647.5,
    2652.5, 2657.5, 2662.5,
    2667.5, 2672.5, 2677.5,
    2682.5, 2687.5],
10: [2112.5, 2117.5, 2122.5, 2127.5, 2132.5, 2137.5, 2142.5, 2147.5, 2152.5, 2157.5, 2162.5, 2167.5],
12: [731.5, 736.5, 737.5, 742.5, 743.5],
13: [748.5, 753.5],
14: [760.5, 765.5],
19: [877.5, 882.5, 887.5],
25: [1932.5, 1937.5, 1942.5, 1947.5, 1952.5, 1957.5, 1962.5, 1967.5, 1972.5, 1977.5, 1982.5, 1987.5, 1992.5],
26: [861.5, 866.5, 871.5, 872.5, 876.5, 877.5, 881.5, 882.5, 886,5, 887.5, 891.5 ]
}

ul_additional_freqs={
2: [1852.5, 1857.5, 1862.5, 1867.5, 1872.5, 1877.5, 1882.5, 1887.5, 1892.5, 1897.5, 1902.5, 1907.5],
4: [1712.5, 1717.5, 1722.5, 1727.5, 1732.5, 1737.5, 1742.5, 1747.5, 1752.5],
5: [826.5, 827.5, 831.5, 832.5, 837.5, 842.5],
6: [832.5, 837.5],
7: [2502.5, 2507.5, 2512.5,
    2517.5, 2522.5, 2527.5,
    2532.5, 2537.5, 2542.5,
    2547.5, 2552.5, 2557.5,
    2562.5, 2567.5],
10: [1712.5, 1717.5, 1722.5, 1727.5, 1732.5, 1737.5, 1742.5, 1747.5, 1752.5, 1757.5, 1762.5, 1767.5],
12: [701.5, 706.5, 707.5, 712.5, 713.5],
13: [779.5, 784.5],
14: [790.5, 795.5],
19: [832.5, 837.5, 842.5],
25: [1852.5, 1857.5, 1862.5,1867.5, 1872.5, 1877.5, 1882.5, 1887.5, 1892.5, 1897.5, 1902.5, 1907.5, 1912.5],
26: [816.5, 821.5, 826.5, 827.5, 831.5, 832.5, 836.5, 837.5, 841.5, 842.5, 846.5]
}



# UARFCN formula offset for additional channels
dl_uarfcn_offset={
2: 1850.1,
4: 1735.1,
5: 670.1,
6: 670.1,
7: 2105.1,
10: 1430.1,
12: -54.9,
13: -64.9,
14: -72.9,
19: 720.1,
25: 674.1,
26: -325.9
}

ul_addChs_uarfcn_offset={
2: 1850.1,
4: 1380.1,
5: 670.1,
6: 670.1,
7: 2030.1,
10: 1075.1,
12: -39.9,
13: 11.1,
14: 2.1,
19: 755.1,
25: 639.1,
26: -325.9
}

dl_uarfcn_mid_range={
1:10700,
2:9800,
3:1337,
4:1675,
5:4400,
6:4400,
7:2400,
8:3013,
9:9312,
10:3250,
11:3750,
12:3870,
13:4030,
14:4130,
19:812,
20:4575,
21:887,
22:4850,
25:4962,
26:4382
}

ul_uarfcn_mid_range={
1:9750,
2:9400,
3:1112,
4:1450,
5:4175,
6:4175,
7:2175,
8:2788,
9:8837,
10:3025,
11:3525,
12:3645,
13:3805,
14:3905,
19:412,
20:4350,
21:487,
22:4625,
25:5037,
26:4157
}

def min_dl_UARFCN(band):
    print"band is %s" %band
    fdl_low = dl_UARFCN_table[band][1]
    fdl_offset = dl_UARFCN_table[band][0]

    uarfcn = 5.0 * ( fdl_low - fdl_offset)
    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))
    return uarfcn

def min_ul_UARFCN(band):
    print"band is %s" %band
    ful_low = ul_UARFCN_table[band][1]
    ful_offset = ul_UARFCN_table[band][0]

    uarfcn = 5.0 * ( ful_low - ful_offset)
    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))
    return uarfcn

def max_dl_UARFCN(band):
    fdl_high = dl_UARFCN_table[band][2]
    fdl_offset = dl_UARFCN_table[band][0]

    uarfcn = 5.0 * ( fdl_high - fdl_offset)
    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))
    return uarfcn

def max_ul_UARFCN(band):
    ful_high = ul_UARFCN_table[band][2]
    ful_offset = ul_UARFCN_table[band][0]

    uarfcn = 5.0 * ( ful_high - ful_offset)
    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))
    return uarfcn

def get_dl_uarfcn(freq, band):
    fdl = freq

    uarfcn = float(0)


    fdl_offset = dl_UARFCN_table[band][0]

    if band in dl_additional_freqs:
        m_obj = re.search(r'(\d+\.5)', str(freq), re.I)

        if m_obj:
            # i.e. additional channels
            fdl_offset = dl_uarfcn_offset[band]

    uarfcn = 5.0 * ( fdl - fdl_offset )

    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))

    return uarfcn

def get_ul_uarfcn(freq, band):
    ful = freq

    uarfcn = float(0)

    f_ul_low = ul_UARFCN_table[band][1]
    f_ul_high = ul_UARFCN_table[band][2]

    if ful < f_ul_low or ful >f_ul_high :
        errMsg = ("freq %s for band %s is outside the carrier freq range %s : %s "
                  %(ful, band, f_ul_low, f_ul_high))
        raise ExUtilities(errMsg)

    ful_offset = ul_UARFCN_table[band][0]

    if band in ul_additional_freqs:
        m_obj = re.search(r'(\d+\.5)', str(freq), re.I)

        if m_obj:
            # i.e. additional channels
            ful_offset = ul_addChs_uarfcn_offset[band]

    uarfcn = 5.0 * ( ful - ful_offset )

    uarfcn = str(uarfcn)
    uarfcn = int(float(uarfcn))

    return uarfcn

def get_all_supported_dl_freq(band):
    minFreq = dl_UARFCN_table[band][1]
    maxFreq = dl_UARFCN_table[band][2]
    freq = minFreq

    freqList = []
    while freq < maxFreq + 0.2 :
        freq=float(str(freq))
        freqList.append(freq)
        freq = freq + 0.2

    if band in dl_additional_freqs:
        for add_freq in dl_additional_freqs[band]:

            add_freq=float(str(add_freq))

            freqList.append(add_freq)
        freqList = sorted(freqList)

    return (freqList)

def get_all_supported_ul_freq(band):
    minFreq = ul_UARFCN_table[band][1]
    maxFreq = ul_UARFCN_table[band][2]
    freq = minFreq

    freqList = []
    while freq < maxFreq + 0.2 :
        freq=float(str(freq))
        freqList.append(freq)
        freq = freq + 0.2

    if band in ul_additional_freqs:
        for add_freq in ul_additional_freqs[band]:

            add_freq=float(str(add_freq))

            freqList.append(add_freq)
        freqList = sorted(freqList)

    return (freqList)

def display_dl_uarfcn_freq(band):
    freqList = get_all_supported_dl_freq(band)

    bandList = []
    for freq in freqList:
        print "%s\t\t%s" %(get_dl_uarfcn(freq, band), freq)

def display_ul_uarfcn_freq(band):
    freqList = get_all_supported_ul_freq(band)

    bandList = []
    for freq in freqList:
        print "%s\t\t%s" %(get_ul_uarfcn(freq, band), freq)

def create_dl_uarfcn_freq_band_map_dic():
    uarfcn_freq_band_dict = {}
    bandList = dl_UARFCN_table.keys()
    for band in bandList:
        freqList = get_all_supported_dl_freq(band)
        min_uarfcn = get_dl_uarfcn(dl_UARFCN_table[band][1],band)
        for freq in freqList:
            uarfcn = get_dl_uarfcn(freq, band)
            uarfcn_freq_band_dict[uarfcn] = {}
            uarfcn_freq_band_dict[uarfcn]['freq'] = freq
            uarfcn_freq_band_dict[uarfcn]['band'] = band
            uarfcn_freq_band_dict[uarfcn]['index'] = uarfcn - min_uarfcn

    return uarfcn_freq_band_dict

def create_ul_uarfcn_freq_band_map_dic():
    uarfcn_freq_band_dict = {}
    bandList = ul_UARFCN_table.keys()
    for band in bandList:
        freqList = get_all_supported_ul_freq(band)
        min_uarfcn = get_ul_uarfcn(ul_UARFCN_table[band][1],band)
        for freq in freqList:
            uarfcn = get_ul_uarfcn(freq, band)
            uarfcn_freq_band_dict[uarfcn] = {}
            uarfcn_freq_band_dict[uarfcn]['freq'] = freq
            uarfcn_freq_band_dict[uarfcn]['band'] = band
            uarfcn_freq_band_dict[uarfcn]['index'] = uarfcn - min_uarfcn

    return uarfcn_freq_band_dict


def get_umts_dl_freq(uarfcn):
    # from uarfcn get channel freq
    look_up_dict = create_dl_uarfcn_freq_band_map_dic()
    freq = 0
    try:
        freq = look_up_dict[uarfcn]['freq']
        band = look_up_dict[uarfcn]['band']
    except KeyError:
        print "uarfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(dl_UARFCN_table.keys())
        return freq

    return freq

def get_umts_ul_freq(uarfcn):
    # from uarfcn get channel freq
    look_up_dict = create_ul_uarfcn_freq_band_map_dic()
    freq = 0
    try:
        freq = look_up_dict[uarfcn]['freq']
        band = look_up_dict[uarfcn]['band']
    except KeyError:
        print "uarfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(ul_UARFCN_table.keys())
        return freq

    return freq

def get_umts_dl_freq_band(uarfcn):
    # from uarfcn get channel freq
    look_up_dict = create_dl_uarfcn_freq_band_map_dic()
    freq = 0
    band = 0
    try:
        freq = look_up_dict[uarfcn]['freq']
        band = look_up_dict[uarfcn]['band']
    except KeyError:
        print "uarfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(dl_UARFCN_table.keys())
        return freq,band

    return freq,band

def get_umts_ul_freq_band(uarfcn):
    # from uarfcn get channel freq
    look_up_dict = create_ul_uarfcn_freq_band_map_dic()
    freq = 0
    band = 0
    try:
        freq = look_up_dict[uarfcn]['freq']
        band = look_up_dict[uarfcn]['band']
    except KeyError:
        print "uarfcn %s is not supported by the script" %(uarfcn)
        print "current supported band list is %s" %(ul_UARFCN_table.keys())
        return freq,band

    return freq,band



def default_dl_uarfcn(band):
    try:
        uarfcn = dl_uarfcn_mid_range[band]
    except KeyError:
        return (-1)

    return uarfcn

def default_ul_uarfcn(band):
    try:
        uarfcn = ul_uarfcn_mid_range[band]
    except KeyError:
        return (-1)

    return uarfcn

def get_umts_ul_dl_freq_band (uarfcn):
    dl_look_up_dict = create_dl_uarfcn_freq_band_map_dic()
    ul_look_up_dict = create_ul_uarfcn_freq_band_map_dic()
    freq_ul = 0
    freq_dl = 0
    band = 0

    if uarfcn in dl_look_up_dict.keys():
        freq_dl = dl_look_up_dict[uarfcn]['freq']
        band = dl_look_up_dict[uarfcn]['band']
        idx = dl_look_up_dict[uarfcn]['index']

        for key in ul_look_up_dict.keys():
            if idx == ul_look_up_dict[key]['index'] and band == ul_look_up_dict[key]['band']:
                freq_ul = ul_look_up_dict[key]['freq']

    elif uarfcn in ul_look_up_dict.keys():
        freq_ul = ul_look_up_dict[uarfcn]['freq']
        band = ul_look_up_dict[uarfcn]['band']
        idx = ul_look_up_dict[uarfcn]['index']

        for key in dl_look_up_dict.keys():
            if idx == dl_look_up_dict[key]['index'] and band == dl_look_up_dict[key]['band']:
                freq_dl = dl_look_up_dict[key]['freq']

    else:
        raise ValueError("UARFCN not found")

    return band,freq_ul,freq_dl

def main():
    try:
        band = 1
        dl_uarfcn = get_dl_uarfcn(freq=2500, band=7)
        print "dl uarfcn is %s" %dl_uarfcn

        ul_freqMHz = 1950
        band = 1
        ul_uarfcn = get_ul_uarfcn(freq=ul_freqMHz, band=band)
        print "ul uarfcn for freq %s for band %s is %s" %(ul_freqMHz, band, ul_uarfcn)

        ul_uarfcn = 9750
        freq = get_umts_ul_freq(uarfcn=ul_uarfcn)
        print "UL UARFCN : %s" %freq
        exit()

        #display_dl_uarfcn_freq(19)
        display_ul_uarfcn_freq(1)

        get_all_supported_dl_freq(band)
        for band_idx in dl_UARFCN_table.keys():
            dl_uarfcn = default_dl_uarfcn(band_idx)
            if dl_uarfcn == -1:
                continue
            print "band: %s, uarfcn: %s, freq (MHz):%s" %(band_idx, dl_uarfcn, get_umts_dl_freq(dl_uarfcn))

        min_dl_uarfcn = min_dl_UARFCN(band)
        print min_dl_uarfcn
        max_dl_uarfcn = max_dl_UARFCN(band)
        print max_dl_uarfcn
        print get_dl_uarfcn(2112.6, band)
        print min_dl_uarfcn
        print max_dl_uarfcn
        uarfcnList = range(min_dl_uarfcn, max_dl_uarfcn, 1)
        print uarfcnList

    except ExUtilities as X:
        print X.message

if __name__ == '__main__':
    #main()

    band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(10700)
    print "Band %d, Freq_UL %f, Freq_DL %f" % (band,freq_ul,freq_dl)

