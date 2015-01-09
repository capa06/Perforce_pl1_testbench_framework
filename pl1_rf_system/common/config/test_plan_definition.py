#-------------------------------------------------------------------------------
# Name:        test_plan_definition
# Purpose:     test plan definition for RF system regression tests
#
# Author:
#
# Created:
# Copyright:
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

from pl1_rf_system.common.config.umts_utilities import *
from pl1_rf_system.common.config.lte_utilities import *

import pl1_rf_system.common.rf_common_functions as rf_cf

# Test execution is contained within rat/dir specific files -- common/testtype/wcdma_tx.py etc
# Test ID's should be unique across all tests - used to search/index these test maps
# Test Map values are the test function names within the specified File. These functions take a set of
# paramters which are defined as parameter dictionaries in the test plan below

wcdma_tx_test_map =      { 'File':'wcdma_tx.py',
                           'UTX1':'driver_mode_uplink_pattern_test',
                           'UTX2':'direct_mode_uplink_pattern_test',
                           'UTX3':'dc_uplink_pattern_test',
                           'UTX4':'sine_uplink_pattern_test',
                           'GEN1':'temperature_sensor_test',
                         }

lte_tx_test_map =        { 'File':'lte_tx.py',
                           'ETX1':'modulated_uplink_pattern_test',
                           'ETX2':'modulated_uplink_pattern_tdd_test',
                           'ETX3':'dc_uplink_pattern_test',
                           'ETX4':'sine_uplink_pattern_test',
                           'ETX5':'tx_switch_channel',
                           'ETX6':'direct_mode_test',
                           'ETX7':'tx_switch_band',
                           'ETX8':'tx_switch_bandwidth',
                         }

general_purpose_test_map = { 'File':'general_purpose.py',
                             'RX1':'auto_agc_verification',
                             'RFICTM1':'rfic_test_mode_basic_check',
                             'RX2':'frequency_change',
                             'RX3':'auto_agc_and_manual',
                             'IPRPR':'basic_iprpr',
                             'ETDIRECT':'envelope_tracking_at_cmds_only',
                             'RXABBSWEEP':'receiver_filter_characterization'
                           }


test_plan = {

'Jenkins'   : [ 'UTX1' , [{'uarfcn':9750, 'powerdBm':-10}],

                'UTX2' , [{'uarfcn':9750}],

                'UTX3' , [{'uarfcn':9750}],

                'UTX4' , [{'uarfcn':9750}],

                'ETX1' , [{'earfcn':18900,'bwMhz':20,'powerdBm':-10},
                          {'earfcn':18500,'bwMhz':5,'powerdBm':-10},
                          {'earfcn':18900,'bwMhz':10,'powerdBm':-10},
                          {'earfcn':18500,'bwMhz':15,'powerdBm':-10},
                         ],

                'ETX3' , [{'earfcn':18500,'bwMhz':5}],

                'ETX4' , [{'earfcn':18500,'bwMhz':5,'powerdBm':-10}],

                'RX1'  , [{'rat':'LTE','arfcn':300, 'powerdBm':-80},
                          {'rat':'3G','arfcn':10700,'powerdBm':-60}],

                'GEN1' , [{}],

                'RFICTM1', [{}],

                'IPRPR', [{}],
              ],

'RX_AGC'   :  [ 'RX1'  , [{'rat':'LTE','arfcn':300, 'powerdBm':-80},
                          {'rat':'LTE','arfcn':300, 'powerdBm':-70},
                          {'rat':'LTE','arfcn':300, 'powerdBm':-60},
                          {'rat':'3G','arfcn':10700,'powerdBm':-60},
                          {'rat':'3G','arfcn':10700,'powerdBm':-50}],
             ],

'Lte_Tx'   :  [ 'ETX1' , [{'earfcn':18500,'bwMhz':5,'powerdBm':-10},
                          {'earfcn':18900,'bwMhz':10,'powerdBm':-10},
                          {'earfcn':18500,'bwMhz':15,'powerdBm':-10},
                          {'earfcn':18900,'bwMhz':20,'powerdBm':-10}],

                'ETX2' , [{'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':1,'sf_sweep':True},
                          {'earfcn':38000,'bwMhz':10,'powerdBm':-10,'ud_config':2,'sf_sweep':True},
                          {'earfcn':38000,'bwMhz':15,'powerdBm':-10,'ud_config':3,'sf_sweep':True}],

                'ETX3' , [{'earfcn':18500,'bwMhz':5}],

                'ETX4' , [{'earfcn':18500,'bwMhz':5,'powerdBm':-10}],
             ],

'pl1_dev_Lara':[
                'RX1'  , [
                          {'rat':'LTE','arfcn':38000,'powerdBm':-80,'ud_config':'TEST0'},
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':0},
                          {'rat':'LTE','arfcn':38000,'powerdBm':-70,'ud_config':6,'with_tx':True},
                         ],
                'RX2'  , [
                          {'rat':'LTE','arfcn':38000,'powerdBm':-80,'ud_config':'TEST0','iterations':1},
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':0,'iterations':2},
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':1,'with_tx':True,'iterations':2},
                          {'rat':'LTE','arfcn':300,'powerdBm':-60,'iterations':1},
                         ],
                'RX3'  , [
                          {'rat':'LTE','arfcn':38000,'powerdBm':-80,'ud_config':'TEST0','iterations':1},
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':1,'iterations':2},
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':0,'with_tx':True,'iterations':2},
                          {'rat':'LTE','arfcn':300, 'powerdBm':-80,'iterations':1},
                          {'rat':'3G','arfcn':10700,'powerdBm':-60,'iterations':1},
                         ],
                'ETX2' , [
                          {'earfcn':38000,'bwMhz':5,'powerdBm':-10,'ud_config':1},
                          {'earfcn':39150,'bwMhz':5,'powerdBm':-10,'ud_config':2,'sf_sweep':True,'with_rx':True},
                          {'earfcn':38100,'bwMhz':5,'powerdBm':-10,'ud_config':3,'with_rx':True},
                          {'earfcn':38100,'bwMhz':5,'powerdBm':-10,'ud_config':'TEST1'},
                         ],
                'ETX5' , [
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':0,'iterations':2},
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':1,'with_rx':True,'iterations':2},
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1','iterations':1},
                         ],
                'ETX6' , [
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':0,'ud_config':1},
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':2,'sf_sweep':True,'with_rx':True},
                          {'earfcn':38000,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1'},
                         ],
                'ETX7' , [
                          {'band1':38,'band2':40,'bwMhz': 5,'powerdBm':-10,'ud_config':0},
                          {'band1':38,'band2':40,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1'},
                         ],
               ],

'pl1_dev_Lara_nightly' : 
             [ 
                'RX1'  , [
                          {'rat':'LTE','arfcn':39150,'powerdBm':-60,'ud_config':0,'special_sf_config':special_sf_config,'with_tx':with_tx}
                          for special_sf_config in [0,4] for with_tx in [False, True]
                         ],
                'RX2'  , [
                          {'rat':'LTE','arfcn':300,'powerdBm':-60,'iterations':1,'with_tx':True},
                          {'rat':'LTE','arfcn':300,'powerdBm':-60,'iterations':1},
                          {'rat':'3G','arfcn':10700,'powerdBm':-60,'iterations':5},
                          {'rat':'3G','arfcn':10700,'powerdBm':-60,'iterations':5,'with_tx':True},
                         ],
                'ETX1' , [
                          {'earfcn':18500,'bwMhz':5,'powerdBm':-10,'with_rx':True},
                          {'earfcn':18900,'bwMhz':3,'powerdBm':-10},    # 3 MHz bw works in band 2
                          {'earfcn':18900,'bwMhz':1.4,'powerdBm':-10},  # 1.4 MHz bw works in band 2
                         ],
                'ETX2' , [
                          {'earfcn':38100,'bwMhz':5,'powerdBm':-10,'ud_config':1,'special_sf_config':special_sf_config,'sf_sweep':True,'with_rx':with_rx} 
                          for special_sf_config in [0,4] for with_rx in [False, True]
                         ]+[
                          {'earfcn':38100,'bwMhz':5,'powerdBm':-10,'ud_config':1,'with_rx':True,'ul_timing_advance':ul_timing_advance}
                          for ul_timing_advance in [-200, 1500, 3000]
                         ],
                'ETX5' , [
                          {'earfcn':300,'bwMhz': 5,'powerdBm':-10,'with_rx':True},
                          {'earfcn':300,'bwMhz': 5,'powerdBm':-10},
                         ],
                'ETX7' , [
                          {'band1':38,'band2':40,'bwMhz': 5,'powerdBm':-10,'ud_config':0},
                          {'band1':38,'band2':40,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1'},
                          {'band1':1,'band2':2,'bwMhz': 5,'powerdBm':-10},
                          {'band1':1,'band2':38,'bwMhz': 5,'powerdBm':-10,'ud_config':1},
                          {'band1':1,'band2':38,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1'},
                          {'band1':40,'band2':1,'bwMhz': 5,'powerdBm':-10,'ud_config':1},
                          {'band1':40,'band2':1,'bwMhz': 5,'powerdBm':-10,'ud_config':'TEST1'},
                         ],
                'ETX8' , [
                          # 1.4 & 3 MHz bw work in band 2
                          {'earfcn':18900,'bwMhz_list':[1.4, 3, 5, 10, 15, 20, 5]},
                          {'earfcn':18900,'bwMhz_list':[20, 15, 10, 5, 3, 1.4],'with_rx':True},

                          {'earfcn':38000,'ud_config':1},
                          {'earfcn':38000,'ud_config':0,'with_rx':True},
                          {'earfcn':38000,'ud_config':'TEST1'},
                         ],      
             ],

'dev'       : [ 'IPRPR'   , [{}],
                'ETDIRECT'   , [{}],
             ],

'ABB'       : [ 'RXABBSWEEP',[ {'rat':'3G','bwMhz':5,'arfcn':10700,'offsetkhz':10000,'stepkHz':100,'powerdBm':-60},
                               {'rat':'LTE','bwMhz':5,'arfcn':300,'offsetkhz':10000,'stepkHz':100,'powerdBm':-60},
                               {'rat':'LTE','bwMhz':10,'arfcn':300,'offsetkhz':20000,'stepkHz':200,'powerdBm':-60},
                               {'rat':'LTE','bwMhz':15,'arfcn':300,'offsetkhz':30000,'stepkHz':300,'powerdBm':-60},
                               {'rat':'LTE','bwMhz':20,'arfcn':300,'offsetkhz':40000,'stepkHz':400,'powerdBm':-60},
                             ]
             ],

}


def testFilefromID (test_id):

    if test_id in wcdma_tx_test_map:
        return wcdma_tx_test_map['File']
    elif test_id in lte_tx_test_map:
        return lte_tx_test_map['File']
    elif test_id in general_purpose_test_map:
        return general_purpose_test_map['File']
    else:
        raise ExGeneral('Test ID %s not found' % test_id)

def testFuncfromID (test_id):

    if test_id in wcdma_tx_test_map:
        return wcdma_tx_test_map[test_id]
    elif test_id in lte_tx_test_map:
        return lte_tx_test_map[test_id]
    elif test_id in general_purpose_test_map:
        return general_purpose_test_map[test_id]
    else:
        raise ExGeneral('Test ID %s not found' % test_id)


if __name__ == '__main__':

    jenkins_tp_list = test_plan['Jenkins']
    list_len = len(jenkins_tp_list)
    ID_index = range(0,list_len,2)
    print "ID Index", ID_index

    for id_idx in ID_index:
        print "Test ID: %s, Params[0]:%s" % (str(jenkins_tp_list[id_idx]), str(jenkins_tp_list[id_idx+1][0]))

