#-------------------------------------------------------------------------------
# Name:        afc_test
# Purpose:
#
# Author:      joashr
#
# Created:     04/07/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

try:
    os.environ['PL1_RF_SYSTEM_ROOT']
except KeyError:
    os.environ['PL1_RF_SYSTEM_ROOT'] = os.sep.join(cmdpath.split(os.sep)[:-1])
    print ">> os.environ['PL1_RF_SYSTEM_ROOT']=%s" % os.environ['PL1_RF_SYSTEM_ROOT']
    sys.path.append(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]))

from addSystemPath import AddSysPath

AddSysPath(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['instr']))

from rf_modem import *
import cmu200 as cmu
import cmw500 as cmw500
from measurementClass import MeasurementClass
from user_exceptions import *


def get_freq_err_info_tuple(instrObj, evmObj, instr_name):

    if instr_name == "CMW500":
        (meas_array, limit_array)=instrObj.wcdma_tx.get_evm_meas(num_cycles=5)
    else:
        (meas_array, limit_array)=instrObj.get_evm_meas(num_cycles=5)

    evmObj.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
    meas_desc = "Carrier Frequency Error (Hz)"
    dict_s = {3:'Carrier_freq_err'}

    meas_desc = "Carrier Frequency Error (Hz)"
    evmObj.set_subTestTitle(subTestTitle = meas_desc)
    selected_2d_array, selected_limit_2d_array = evmObj.get_selected_2d_array(selectedRowDict=dict_s)
    freq_err_lim_str = selected_limit_2d_array[0][0]
    try:
        lim_desc = evmObj.dictKeysValidLim[freq_err_lim_str]
        freq_err_Hz = float (selected_2d_array[0][0])
    except KeyError:
            keysStr = ', '.join(evmObj.dictKeysValidLim.keys())
            raise ExGeneral('%s indicates invalid measurement. Expected values are : %s'
                            %(freq_err_lim_str, keysStr))

    return freq_err_Hz, freq_err_lim_str


def main():
    from enableLogging import enable_logging
    enable_logging(loglevel = "debug")

    instr_name = "CMW500"
    instr_name = "CMU200"

    cmwip = '10.21.141.209'

    cmuip = "10.21.140.230"

    cmu_gpib = "20,1"


    if instr_name == "CMW500":

        instr=cmw500.CmwControl(name="cmw500", ip_addr=cmwip)

    else:

        instr=cmu.CmuControl(cmu_name=instr_name,
                             cmu_gwip=cmuip,
                             cmu_gpib=cmu_gpib)

    # rows and columns for EVM

    rowDict_EVM = {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',
                   3:'Carrier_freq_err', 4:'Peak_Code_Dom_err', 5:'UEpower'}

    colDict_EVM = {0:'Current', 1:'Average', 2:'Max/Min'}

    evm = MeasurementClass(rowDict=rowDict_EVM,
                           colDict=colDict_EVM,
                           instrName=instr_name)


    modemObj = serialComms(timeout = 2)

    loggerDisplay = logging.getLogger(__name__)

    afc_val = modemObj.get_afc_val()

    afc_val = int(afc_val)

    loggerDisplay.info('Current afc value is %s' %afc_val)

    instr.setup_3g_tx_test(freq=1950,
                           cable_loss_dB=0.5)

    """
    if instr_name == "CMW500":
        instr.wcdma_tx.instrObj.write('CONFigure:WCDMa:MEAS:MEValuation:SCOunt:MODulation 5')
    """

    freq_err_Hz, freq_err_lim_str = get_freq_err_info_tuple(instrObj=instr,
                                                            evmObj=evm,
                                                            instr_name=instr_name)


    LOWER_FREQ_LIM_HZ = -200

    UPPER_FREQ_LIM_HZ = abs(LOWER_FREQ_LIM_HZ)

    AFC_STEP_SIZE = 100

    MAX_NUM_AGC_ITER = 10

    if freq_err_lim_str in ['ULEL', 'NMAU']:
        iteration = 0
        while freq_err_Hz < LOWER_FREQ_LIM_HZ and iteration < MAX_NUM_AGC_ITER:
            afc_val = afc_val - AFC_STEP_SIZE
            modemObj.set_afc_val(afc_val)
            loggerDisplay.info('Iteration %s' %(iteration+1))
            loggerDisplay.info("%s will try with new AFC value %s"
                                %(evm.dictKeysValidLim[freq_err_lim_str], afc_val))
            freq_err_Hz, freq_err_lim_str = get_freq_err_info_tuple(instrObj=instr,
                                                                    evmObj=evm,
                                                                    instr_name=instr_name)
            iteration += 1
        if iteration < MAX_NUM_AGC_ITER:
            loggerDisplay.info("Carrier Frequency Error %s is within the required tolerance, Converged AFC value is %s after %s iterations"
                   %(freq_err_Hz, afc_val, iteration))
        else:
            loggerDisplay.info("Carrier Frequency Error %s is outside the required tolerance after %s iterations"
                               %(freq_err_Hz, iteration))
            loggerDisplay.info("Will use AFC value %s" %afc_val)

    elif freq_err_lim_str in ['ULEU', 'NMAL']:
        iteration = 0
        while freq_err_Hz > UPPER_FREQ_LIM_HZ and iteration < MAX_NUM_AGC_ITER:
            afc_val = afc_val + AFC_STEP_SIZE
            modemObj.set_afc_val(afc_val)
            loggerDisplay.info('Iteration %s' %(iteration+1))
            loggerDisplay.info("%s will try with new AFC value %s"
                                %(evm.dictKeysValidLim[freq_err_lim_str], afc_val))
            freq_err_Hz, freq_err_lim_str = get_freq_err_info_tuple(instrObj=instr,
                                                                    evmObj=evm,
                                                                    instr_name=instr_name)
            iteration += 1

        if iteration < MAX_NUM_AGC_ITER:
            loggerDisplay.info("Carrier Frequency Error %s is within the required tolerance, Converged AFC value is %s after %s iterations"
                   %(freq_err_Hz, afc_val, iteration))
        else:
            loggerDisplay.info("Carrier Frequency Error %s is outside the required tolerance after %s iterations"
                               %(freq_err_Hz, iteration))
            loggerDisplay.info("Will use AFC value %s" %afc_val)

    elif freq_err_lim_str.upper() == "OK":

        loggerDisplay.info("Carrier Frequency Error %s is within the required tolerance, AFC value is %s"
                           %(freq_err_Hz, afc_val))

    """
    evm.display_selected_meas()
    evm.display_limit_selected_meas()
    evm.display_end_title()
    """

    instr.close()
    instr = None

    """
    modemObj = serialComms(timeout = 2)
    afc_val = modemObj.get_afc_val()
    if afc_val:
        print afc_val
    else:
        print "AFC extraction error"
    modemObj.close()
    """

if __name__ == '__main__':
    main()
