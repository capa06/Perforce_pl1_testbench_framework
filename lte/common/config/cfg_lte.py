'''
Created on 11 Jul 2013

@author: fsaracino
'''

import os
import sys
import logging

try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))

from CfgError import CfgError
    
# *****************************************************************************
# LTE PARAMETERS
# *****************************************************************************

LTE_DL_IMCS_2_ITBS_QM = { 0:[ 0, 2],  1:[ 1, 2],  2:[ 2, 2],  3:[ 3, 2],  4:[ 4, 2],  5:[ 5, 2],  6:[ 6, 2],  7:[ 7, 2],  8:[ 8, 2],  9:[ 9, 2], 
                         10:[ 9, 4], 11:[10, 4], 12:[11, 4], 13:[12, 4], 14:[13, 4], 15:[14, 4], 16:[15, 4], 
                         17:[15, 6], 18:[16, 6], 19:[17, 6], 20:[18, 6], 21:[19, 6], 22:[20, 6], 23:[21, 6], 24:[22, 6], 25:[23, 6], 26:[24, 6], 27:[25, 6], 28:[26, 6] }                 

LTE_UL_IMCS_2_ITBS_QM = { 0:[ 0, 2],  1:[ 1, 2],  2:[ 2, 2],  3:[ 3, 2],  4:[ 4, 2],  5:[ 5, 2],  6:[ 6, 2],  7:[ 7, 2],  8:[ 8, 2],  9:[ 9, 2], 10:[ 10, 2],
                         11:[10, 4], 12:[11, 4], 13:[12, 4], 14:[13, 4], 15:[14, 4], 16:[15, 4], 17:[16, 4], 18:[17, 4], 19:[18, 4], 20:[19, 4], 
                         21:[19, 4], 22:[20, 4], 23:[21, 4], 24:[22, 4], 25:[23, 4], 26:[24, 4], 27:[25, 4], 28:[26, 4] }                 

LTE_UL_IMCS_2_ITBS_QM_CAT5 = { 0:[ 0, 2],  1:[ 1, 2],  2:[ 2, 2],  3:[ 3, 2],  4:[ 4, 2],  5:[ 5, 2],  6:[ 6, 2],  7:[ 7, 2],  8:[ 8, 2],  9:[ 9, 2], 10:[ 10, 2],
                              11:[10, 4], 12:[11, 4], 13:[12, 4], 14:[13, 4], 15:[14, 4], 16:[15, 4], 17:[16, 4], 18:[17, 4], 19:[18, 4], 20:[19, 4], 
                              21:[19, 6], 22:[20, 6], 23:[21, 6], 24:[22, 6], 25:[23, 6], 26:[24, 6], 27:[25, 6], 28:[26, 6] }                 

LTE_QM_2_MOD = { 2: 'QPSK', 4 : '16QAM', 6 : '64QAM'}

LTE_BW_MHZ             = [ 1.4,   3,    5,    10,    15,    20]
LTE_BW_MHZ_2_CFIMIN    = { 1.4:2, 3:1,  5:1,  10:1,  15:1,  20:1}
LTE_BW_MHZ_2_NPRBMAX   = { 1.4:6, 3:15, 5:25, 10:50, 15:75, 20:100}

LTE_TM_TABLE           = [ 1,          2,                 3,                         4                             ]
LTE_TM_2_NUMTXANTS     = { 1:[1],      2:[ 2,     4]    , 3:[ 2,         4],         4:[ 2,         4]             }
LTE_TM_NUMTXANTS_2_PMI = { 1:{1:[0]},  2:{ 2:[0], 4:[0]}, 3:{ 2:[0,1,2], 4:[0,1,2]}, 4:{ 2:[0,1,2], 4:range(0,16)} }


#FDD 1-30, TDD 33-42
EARFCN_TABLE={
  1:[   0,  599],
  2:[ 600, 1199],
  3:[1200, 1949],
  4:[1950, 2399],
  5:[2400, 2649],
  6:[2650, 2749],
  7:[2750, 3449],
  8:[3450, 3799],
  9:[3800, 4149],
 10:[4150, 4749],
 11:[4750, 4949],
 12:[5010, 5179],
 13:[5180, 5279],
 14:[5280, 5379],
 17:[5730, 5849],
 18:[5850, 5999],
 19:[6000, 6149],
 20:[6150, 6449],
 21:[6450, 6599],
 33:[36000, 36199],
 34:[36200, 36349],
 35:[36350, 36949],
 36:[37950, 37549],
 37:[37550, 37749],
 38:[37750, 38249],
 39:[38250, 38649],
 40:[38650, 39649],
 41:[39650, 41589],
 44:[45590, 46589]
}


# *****************************************************************************
# LTE UTILITIES
# *****************************************************************************
def GetDLModulation(Imcs):
    if Imcs in range(0,10): 
        return 'QPSK'
    elif Imcs in range(10,17):
        return '16QAM'
    elif Imcs in range(17,29):
        return '64QAM'
    else: 
        return 'UNKNOWN_QAM'

def GetULModulation(Imcs, UeCat=4):
    if Imcs in range(0,11): 
        return 'QPSK'
    elif Imcs in range(11,21):
        return '16QAM'
    elif Imcs in range(21,29):
        if UeCat==5:
            return '64QAM'
        else:
            return '16QAM'
    else: 
        return 'UNKNOWN_QAM'    
        
def earfcnDefault(band):
    return int(EARFCN_TABLE[band][0]+0.5*(EARFCN_TABLE[band][1]-EARFCN_TABLE[band][0]+1))


def earfcnMin(band):
    return (EARFCN_TABLE[band][0])

def earfcnMax(band):
    return (EARFCN_TABLE[band][1])


def earfcnRange(band, bwmhz):
    logger=logging.getLogger('earfcnRange')
    # 
    # raster=0.1 [MHz], delta_earfcn=(bwmhz/2)*(1/raster)
    # 
    earfcn_range=[]
    if bwmhz in LTE_BW_MHZ:
        earfcn_min=earfcnMin(band)+int(5*bwmhz)
        earfcn_max=earfcnMax(band)-int(5*bwmhz)+1
        if (earfcn_min>earfcn_max):
            logger.error("earfcnRange:: not enough channels in RF band %s to support BW %s [MHz]. Check 3GPP spec" % (rfband, bwmhz))
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        else:
            earfcn_range=[earfcn_min, earfcn_max]
    return earfcn_range 


def earfcnIntraHHO(band, bwmhz, step):
    #logger=logging.getLogger('earfcnIntraHHO')
    # This function compute the numbers of DL EARFCN to scan given a list of bands and the step
    # Scan resolution is step*size(raster), where raster size is 100 KHz
    earfcn_ihho_min, earfcn_ihho_max=earfcnRange(band, bwmhz)
    earfcn_ihho_l=range(earfcn_ihho_min, earfcn_ihho_max+1, step)
    return earfcn_ihho_l


def earfcnTotal(band_list, step):
    # This function compute the numbers of DL EARFCN to scan given a list of bands and the step
    # Scan resolution is step*size(raster), where raster size is 100 KHz
    import math
    nearfcn=0
    for bd in band_list:
        # +1 because if we have i.e 4.5, it will be rounded to 4, and index will be from 0,1,.,4
        nearfcn += int(math.floor((earfcnMax(bd)-earfcnMin(bd)+1)/float(step))+1)
    return nearfcn 



if __name__ == '__main__':
    pass

        
    
