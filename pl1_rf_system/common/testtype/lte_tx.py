#-------------------------------------------------------------------------------
# Name:        lte_tx
# Purpose:     execute the LTE Tx tests
#
# Author:      joashr
#
# Created:     16/07/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, traceback, logging


try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

import pl1_rf_system.common.config.lte_utilities as lte_util
from pl1_rf_system.common.rf_modem import *
import pl1_rf_system.instr.cmu200 as cmu
import pl1_rf_system.instr.cmw500 as cmw500
from pl1_rf_system.common.user_exceptions import *
from pl1_rf_system.instr.measurementLteClass import MeasurementLteClass
from pl1_rf_system.common.verdict import Verdict
import pl1_rf_system.common.rf_common_functions as rf_cf
import pl1_rf_system.common.rf_common_functions as rf_cf
import pl1_rf_system.common.rf_common_globals as rf_global
import pl1_rf_system.common.rf_common_functions as rf_cf
from pl1_rf_system.common.report.csv.CsvReport import CsvReport
from pl1_rf_system.instr.cmw_lte_meas import Lte_meas
from pl1_rf_system.common.testtype.wcdma_tx import Wcdma_tx
from serial import SerialException
#from pl1_jenkins.instr.psu_control import check_output_state_on, switch_on_psu, switch_off_psu
#from pl1_testbench_framework.common.instr.PsuBench import PsuBenchOn, PsuBenchOff

def check_supported(check_val_list, valid_meas_dic):
    """
    check to ensure that the values in check_val_list are key
    entries into valid_meas_dic
    """
    invalid_list = []

    for val in check_val_list:
        try:
            dummy = valid_meas_dic[val]
        except KeyError:
            invalid_list.append(val)

    if invalid_list:
        errMsg = ("The following is unsupported %s" %invalid_list)
        errMsg = errMsg + ("\nThe list of valid values is %s" %valid_meas_dic.keys())
        raise ExGeneral(errMsg)

def sf_is_uplink(ud_config, sf):
    config_table = {0: "DSUUU"*2,
                    1: "DSUUD"*2,
                    2: "DSUDD"*2,
                    3: "DSUUUDDDDD",
                    4: "DSUUDDDDDD",
                    5: "DSUDDDDDDD",
                    6: "DSUUUDSUUD",
                    'TEST0': "D"*10,
                    'TEST1': "U"*10,
                    }
    return config_table[ud_config][sf] == 'U'

class LTE_rf_config(object):
    def __init__ (self, bwMHz=5):
        bw_num_rbs_dict = {1.4:6,3:15,5:25,10:50, 15:75, 20:100}
        num_rbs = bw_num_rbs_dict[bwMHz]
        self.num_rbs = num_rbs
        self.rb_len = num_rbs
        self.rb_offset = 0

    def check_config(self):
        if self.rb_offset + self.rb_len > self.num_rbs:
            raise ExGeneral("rb_offset + rb_len = %s cannot exceed %s"%(self.rb_offset+self.rb_len, self.num_rbs))

class Lte_tx(Wcdma_tx):

    def __init__ (self, testID, testConfig_s, results_f, test_func, test_params, test_rat, final_test, unittest_enabled):

        func_name = sys._getframe(0).f_code.co_name

        loggerTest = logging.getLogger(__name__ + func_name)

        self.testConfig = testConfig_s

        self.test_func = test_func

        self.test_params = test_params

        self.test_rat = test_rat

        self.testID = testID

        self.modemObj = None

        self.instr = None

        self.FinalTest = final_test

        self.results_f = results_f

        self.set_bw(bwMHz=0)
        self.set_band(band=0)

        # this corresponds to the row index measurement type mapping of
        # results returned from get_evm_meas of cmw_lte_meas
        self.rowDict_EVM = {0:'EVM_RMSlow', 1:'EVM_RMShigh', 2:'EVMpeakLow',
                            3:'EVMpeakHigh', 4:'EVM_DMRSl', 5:'EVM_DMRSh',
                            6:'IQoffset', 7:'FreqError', 8:'TimingError',
                            9:'TXpower', 10:'PeakPower'}

        self.colDict_EVM = {0:'Current', 1:'Average', 2:'Extreme'}

        self.evm = MeasurementLteClass(rowDict=self.rowDict_EVM,
                                       colDict=self.colDict_EVM)

        # rows and columns for Phase error
        self.rowDict_PERR = {0:'PhaseErr_peak', 1:'PhaseErr_rms', 2:'IQ_origin_offset',
                             3:'Carrier_freq_err', 4:'Peak_Code_Dom_err'}

        self.colDict_PERR = self.colDict_EVM

        self.phase_err = MeasurementLteClass(rowDict=self.rowDict_PERR,
                                             colDict=self.colDict_PERR)

        self.rowDict_Overview = {}

        # interchange key, value from dictionary
        # dictionary key corresponds to zero index row number e.g.

        # this corresponds to the row index measurement type mapping of
        # results returned from get_mod_overview_results of cmw_lte_meas
        self.rowDict_Overview= {0:'EVM_RMSlow', 1: 'EVM_RMShigh', 2:'EVMpeakLow', 3: 'EVMpeakHigh',
                                4: 'MErr_RMSlow', 5:'MErr_RMShigh', 6: 'MErrPeakLow', 7: 'MErrPeakHigh',
                                8: 'PErr_RMSlow', 9:'PErr_RMSh', 10:'PErrPeakLow', 11:'PErrPeakHigh',
                                12:'IQoffset', 13:'FreqError', 14: 'TimingError', 15: 'TXpowerMin',
                                16:'TXpowerMax', 17:'PeakPowerMin', 18:'PeakPowerMax', 19:'RBpowerMin',
                                20:'RBpowerMax', 21: 'EVM_DMRSl',  22:'EVM_DMRSh',
                                23: 'MErr_DMRSl', 24:'MErr_DMRSh', 25:'PErr_DMRSl', 26:'PErr_DMRSh',
                                27: 'GainImbal', 28: 'QuadError'}

        for key in sorted(self.rowDict_Overview.keys()):
            loggerTest.debug ("%s => %s" %(key, self.rowDict_Overview[key]))


        self.colDict_Overview = self.colDict_EVM


        self.lte_overview = MeasurementLteClass(rowDict=self.rowDict_Overview,
                                                colDict=self.colDict_Overview)

        self.set_meas("Init - no measurment set")

        self.verdictObj = Verdict()

        self.instr_sw_version = ""

        self.unittest_enabled = unittest_enabled

        self.start_time=time.localtime()

        self.ud_config = None
        self.meas_sf = None


    def set_bw(self, bwMHz):
        self.bwMHz = bwMHz

    def get_bw(self):
        return self.bwMHz

    def set_band(self, band):
        self.band = band

    def get_band(self):
        return self.band

    def get_start_time(self):

        return self.start_time

    def get_duplex_mode(self):
        return "FDD" if self.band < 33 else "TDD"

    def set_ud_config(self, ud_config):
        self.ud_config = ud_config

    def get_ud_config(self):
        return self.ud_config

    def set_meas_sf(self, meas_sf):
        self.meas_sf = meas_sf

    def get_meas_sf(self):
        return self.meas_sf

    def _get_tx_pwr_meas(self, exp_power_dBm, num_cycles, tol_dB):
        print "Performing modem Tx power measurement, please be patient ..."
        print "\n"
        meas_desc = "UE Tx Power(dBm) %sMHz, band %s" %(self.get_bw(), self.get_band())
        heading_len = len(self.evm.get_col_title_str())
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_evm_meas(num_cycles)
        self.evm.populate_2d_array(meas_val_list=meas_array)
        self.evm.get_meas_2d_array()

        self.display_ue_tx_power_heading(subTestTitle=meas_desc, total_len=heading_len)
        ue_tx_power_dBm = self.get_ue_tx_power()

        verdictStr = self.get_ue_tx_pwr_verdict(exp_power_dBm=exp_power_dBm,
                                               measured_power_dBm=ue_tx_power_dBm,
                                               tol_dB=tol_dB)

        print "%s: %s" %(meas_desc, verdictStr)

        return verdictStr


    def get_agc_pwr_meas(self, expected_pwr_dBm, tol_dB=2.0):
        num_cycles = 50

        verdictStr = self._get_tx_pwr_meas(exp_power_dBm=expected_pwr_dBm,
                                           num_cycles = num_cycles,
                                           tol_dB=tol_dB)

        self.recordVerdict(verdictStr=verdictStr.upper())

        heading_len = len(self.evm.get_col_title_str())
        print "*" * heading_len
        print "\n"

    def get_ue_tx_power(self):

        dict_s = {9:'TXpower'}

        selected_2d_array, dummy = self.evm.get_selected_2d_array(selectedRowDict=dict_s)

        cur_power, avg_power, max_power = selected_2d_array[0]

        avg_power_dBm = '%.2f' % float(avg_power)
        print "UE Power average Tx Power : %6s dBm "    % avg_power_dBm
        return avg_power_dBm

    def display_ue_tx_power_heading(self, subTestTitle, total_len):

        # centre the subTestTitle text e.g. ==== DUMMY =====
        subTestTitle = " " + subTestTitle + " "
        len_subTestTitle = len(subTestTitle)
        first_part_len = (total_len - len_subTestTitle)/2
        last_part_len = total_len - first_part_len - len_subTestTitle
        if len_subTestTitle < total_len:
            title_heading = '{0:>{1}s}{2:>{3}s}{4:>{5}s}'.format('*'*first_part_len, first_part_len,
                                                                 subTestTitle, len_subTestTitle,
                                                                 '*'*last_part_len, last_part_len)
        else:
            title_heading = '{0:>10s}{1:>{2}s}{3:>10s}'.format('*'*10,subTestTitle,len(subTestTitle),'*'*10)

        print title_heading


    def get_ue_tx_pwr_verdict(self, exp_power_dBm, measured_power_dBm, tol_dB):
        # see if exepceted power is within the +/- tol_dB of expected power
        # and set the verdict accordingly
        verdict = "FAIL"
        print "expected power : %s" %exp_power_dBm

        upper_limit = 1.0 * float(exp_power_dBm) + tol_dB
        lower_limit = 1.0 * float(exp_power_dBm) - tol_dB

        if float(measured_power_dBm) <= upper_limit and float(measured_power_dBm) >= lower_limit:
            print "Ue Tx power is within the expected range %s : %s" %(lower_limit, upper_limit)
            verdict = "PASS"
        else:
            print "Ue Tx power is outside the expected range %s : %s" %(lower_limit, upper_limit)
            verdict = "FAIL"

        return verdict

    def recordVerdict(self, verdictStr):

        ud_config = self.get_ud_config()
        ud_config_str = ", ud_config=%s" % ud_config if ud_config is not None else ""

        meas_sf = self.get_meas_sf()
        meas_sf_str = ", meas_sf=%s" % meas_sf if meas_sf is not None else ""

        meas_ref = "%-15s (%sMHz, band=%s%s%s)" %(self.get_meas(), self.get_bw(), self.get_band(), ud_config_str, meas_sf_str)
        if verdictStr.upper() == "PASS":
            self.verdictObj.CheckPassed(meas_id=meas_ref, info="Pass")
        else:
            self.verdictObj.CheckFailed(meas_id=meas_ref, info="Fail")


    def display_rows_from_evm_meas(self, descrption, row_dict_s):

        self.evm.set_subTestTitle(subTestTitle = descrption)
        self.evm.get_selected_2d_array(selectedRowDict=row_dict_s)
        self.evm.display_selected_meas(rowIdx_rowDesc_dict=row_dict_s)
        self.evm.display_limit_selected_meas(rowIdx_rowDesc_dict=row_dict_s)
        # not closed loop system (reduced signalling) therefore
        # frequency will drift and should not impact the results
        freqInMeas = False
        verdictStr = self.evm.getTestVerdict(array_2d_val=self.evm.get_selected_limit_2d_array())
        for key in row_dict_s.keys() :
            if row_dict_s[key] == 'FreqError' :
                print ("%s will not be included in results!"
                        %row_dict_s[key])
                freqInMeas = True

        # do not record verdict if FreqError is included in the results
        if not freqInMeas :
            verdictStr = self.evm.getTestVerdict(array_2d_val=self.evm.get_selected_limit_2d_array())
            self.recordVerdict(verdictStr=verdictStr)
            print "%s: %s" %(descrption, verdictStr)

        self.evm.display_end_title()


    def display_rows_from_mod_meas(self, descrption, row_dict_s):

        self.lte_overview.set_subTestTitle(subTestTitle = descrption)
        self.lte_overview.get_selected_2d_array(selectedRowDict=row_dict_s)
        self.lte_overview.display_selected_meas(rowIdx_rowDesc_dict=row_dict_s)
        self.lte_overview.display_limit_selected_meas(rowIdx_rowDesc_dict=row_dict_s)
        verdictStr = self.lte_overview.getTestVerdict(array_2d_val=self.lte_overview.get_selected_limit_2d_array())
        self.recordVerdict(verdictStr=verdictStr)
        print "%s: %s" %(descrption, verdictStr)
        self.evm.display_end_title()

    def get_freq_err_meas(self, num_cycles=20):
        print "Performing LTE frequency error measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_evm_meas(num_cycles)
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "Frequency Error(Hz), %sMHz, band=%s" %(self.get_bw(), self.get_band())

        #dict_s = {7:'FreqError'}
        selected_meas = 'FreqError'
        dict_s = self.get_row_dict(meas_param_key_list=[selected_meas], index_meas_mapping_dict=map_dict)

        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)


    def get_IQ_offset_meas(self, num_cycles=50):
        print "Performing I/Q offset measurement, please be patient ..."
        print "\n"
        map_dict={}
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_evm_meas(num_cycles)
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "I/Q Origin Offset(dB) %sMHz, band=%s" %(self.get_bw(), self.get_band())
        selected_meas = 'IQoffset'
        dict_s = self.get_row_dict(meas_param_key_list=[selected_meas], index_meas_mapping_dict=map_dict)
        #dict_s =  {6:'IQoffset'}
        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)


    def get_row_dict(self, meas_param_key_list, index_meas_mapping_dict={}):
        # get row => meas_param_key dictionary
        # enables the selection of the correct row

        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + " " + func_name)

        dict_s = {}
        if index_meas_mapping_dict:
            index_meas_dict = index_meas_mapping_dict
        else:
            index_meas_dict = self.rowDict_Overview.copy()
        for meas in meas_param_key_list:
            for key in index_meas_dict.keys():
                if index_meas_dict[key] == meas:
                    if self.testConfig.instr_name == "CMW500":
                        #dict_s = {key:index_meas_dict[key]}
                        dict_s[key] = meas
                    else:
                        #dict_s = {key:index_meas_dict[key]}
                        dict_s[key] = meas
                    break
        if dict_s:
            for key in dict_s.keys():
                loggerDisplay.debug ("%s => %s" %(key, dict_s[key]))

            return dict_s
        else:
            errMsg = "Meas param %s cannot be found. Valid key list is %s" %(meas_param_key, index_meas_dict.values())
            raise ExGeneral(errMsg)

    def get_IQ_imbalance_meas(self):
        print "Performing I/Q imbalance measurement, please be patient ..."
        print "\n"
        map_dict={}
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_mod_overview_results()
        self.lte_overview.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "I/Q Imbalance (dB) %sMHz, band=%s" %(self.get_bw(), self.get_band())
        selected_meas = 'GainImbal'
        dict_s = self.get_row_dict(meas_param_key_list=[selected_meas], index_meas_mapping_dict=map_dict)
        self.lte_overview.set_subTestTitle(subTestTitle = meas_desc)
        self.lte_overview.get_selected_2d_array(selectedRowDict=dict_s)
        self.lte_overview.display_selected_meas(rowIdx_rowDesc_dict=dict_s)
        self.lte_overview.display_limit_selected_meas(rowIdx_rowDesc_dict=dict_s)
        verdictStr = self.lte_overview.getTestVerdict(array_2d_val=self.lte_overview.get_selected_limit_2d_array())
        print "%s: %s" %(meas_desc, verdictStr)
        self.recordVerdict(verdictStr=verdictStr)
        self.lte_overview.display_end_title()

    def get_quad_error_meas(self):
        print "Performing I/Q imbalance measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_mod_overview_results()
        self.lte_overview.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "Quad Error (deg) %sMHz, band=%s" %(self.get_bw(), self.get_band())
        selected_meas = 'QuadError'
        dict_s = self.get_row_dict(meas_param_key_list=[selected_meas], index_meas_mapping_dict=map_dict)
        self.lte_overview.set_subTestTitle(subTestTitle = meas_desc)
        self.lte_overview.get_selected_2d_array(selectedRowDict=dict_s)
        self.lte_overview.display_selected_meas(rowIdx_rowDesc_dict=dict_s)
        self.lte_overview.display_limit_selected_meas(rowIdx_rowDesc_dict=dict_s)
        verdictStr = self.lte_overview.getTestVerdict(array_2d_val=self.lte_overview.get_selected_limit_2d_array())
        print "%s: %s" %(meas_desc, verdictStr)
        self.recordVerdict(verdictStr=verdictStr)
        self.lte_overview.display_end_title()


    def get_modem_evm_meas(self):
        print "Performing modem EVM measurement, please be patient ..."
        print "\n"
        map_dict={}
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_evm_meas()
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "EVM Selected Measurements %sMHz, band=%s" %(self.get_bw(), self.get_band())

        select_meas_l = {'EVM_RMSlow','EVM_RMShigh','EVMpeakLow',
                         'EVMpeakHigh','EVM_DMRSl', 'EVM_DMRSh'}
        dict_s = self.get_row_dict(meas_param_key_list=select_meas_l, index_meas_mapping_dict=map_dict)
        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)

    def get_phase_err_meas(self):
        # get phase measurements
        print "Performing phase error measurement, please be patient ..."
        print "\n"
        map_dict={}
        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_mod_overview_results()
        self.lte_overview.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "Phase Measurements %sMHz, band=%s" %(self.get_bw(), self.get_band())

        select_meas_l = {'PErr_RMSlow', 'PErr_RMSh', 'PErrPeakLow', 'PErrPeakHigh',
                         'PErr_DMRSl', 'PErr_DMRSh'}
        dict_s = self.get_row_dict(meas_param_key_list=select_meas_l, index_meas_mapping_dict=map_dict)

        self.display_rows_from_mod_meas(descrption=meas_desc, row_dict_s=dict_s)


    def get_freq_err_info_tuple(self):
        """
        get "current" carrier ferequency error and carrier frequency limit
        error
        """
        num_cycles = 20

        (meas_array, limit_array, map_dict)=self.instr.lte_tx.get_evm_meas(num_cycles)

        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)

        #dict_s = {7:'FreqError'}
        selected_meas = 'FreqError'
        dict_s = self.get_row_dict(meas_param_key_list=[selected_meas], index_meas_mapping_dict=map_dict)

        meas_desc = "Frequency Error (Hz)"
        self.evm.set_subTestTitle(subTestTitle = meas_desc)
        selected_2d_array, selected_limit_2d_array = self.evm.get_selected_2d_array(selectedRowDict=dict_s)
        freq_err_lim_str = selected_limit_2d_array[0][0]
        try:
            lim_desc = self.evm.dictKeysValidLim[freq_err_lim_str]
            freq_err_Hz = float (selected_2d_array[0][0])
            print freq_err_Hz

        except KeyError:
                keysStr = ', '.join(self.evm.dictKeysValidLim.keys())
                raise ExGeneral('%s indicates invalid measurement. Expected values are : %s'
                                %(freq_err_lim_str, keysStr))

        return freq_err_Hz, freq_err_lim_str

    def set_test_afc_val(self):
        """
        set afc values so that carrier frequency error is within the required
        range for test purposes
        """

        MAX_NUM_AGC_ITER = 10
        MAX_CHANGE = 2000
        afc_per_hz = 0.28   #Reasonable starting factor

        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        afc_val = self.modemObj.get_afc_val()
        assert(afc_val is not None)
        afc_val = int(afc_val)
        loggerDisplay.info('Current afc value is %s' %afc_val)
        freq_err_Hz, freq_err_lim_str = self.get_freq_err_info_tuple()

        iteration = 0
        while freq_err_lim_str.upper() != "OK" and iteration < MAX_NUM_AGC_ITER:
            if freq_err_lim_str.upper() not in ['ULEL', 'NMAU', 'ULEU', 'NMAL']:
                loggerDisplay.info('Unexpected response; %s' %freq_err_lim_str.upper())
                loggerDisplay.info('Will continue with current afc value')
                break

            afc_change = int(freq_err_Hz * afc_per_hz)
            afc_change = min(afc_change, MAX_CHANGE)
            afc_change = max(afc_change, -MAX_CHANGE)
            afc_val += afc_change

            self.modemObj.set_afc_val(afc_val)
            loggerDisplay.info('Iteration %s' %(iteration+1))
            loggerDisplay.info("freq_err_Hz=%s, %s will try with new AFC value %s change %s"
                                %(freq_err_Hz, self.evm.dictKeysValidLim[freq_err_lim_str], afc_val, afc_change))
            old_freq_err_Hz = freq_err_Hz
            freq_err_Hz, freq_err_lim_str = self.get_freq_err_info_tuple()
            try:
                afc_per_hz = afc_change/(old_freq_err_Hz-freq_err_Hz)
            except ZeroDivisionError:
                afc_per_hz = 0.2
            if afc_per_hz < 0:
                afc_per_hz = 0.2  #It got worse, go back to something safe
            if afc_per_hz > 1:
                afc_per_hz = 1
            loggerDisplay.debug("afc_per_hz=%s" %(afc_per_hz))
            iteration += 1

        if iteration < MAX_NUM_AGC_ITER:
            loggerDisplay.info("Carrier Frequency Error %s is within the required tolerance, Converged AFC value is %s after %s iterations"
                   %(freq_err_Hz, afc_val, iteration))
        else:
            loggerDisplay.info("Carrier Frequency Error %s is outside the required tolerance after %s iterations"
                               %(freq_err_Hz, iteration))
            loggerDisplay.info("Will use AFC value %s" %afc_val)
            raise ExGeneral("Fail: AFC correction did not converge to a frequency error within tolerance.")


    def executeTest(self,instr_control):

        func_name = sys._getframe(0).f_code.co_name

        logger_test = logging.getLogger(__name__ + func_name)

        modeminfo = ""

        modeminfo = query_build_info_from_modem()

        self.instr= instr_control

        self.set_instr_sw_version(version=self.instr.get_sw_version())

        self.instr.set_verdictObj(self.verdictObj)

        self.set_csvSummaryReport(results_f=self.results_f, modeminfo=modeminfo,
                                  instrswinfo=self.get_instr_sw_version())

        try:

            test_function = getattr(self,self.test_func)
            test_function(**self.test_params)

            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr = None

            self.set_meas(meas="")
            verdictStr = self.verdictObj.GetSummaryVerdict(col_len=80)
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except (IOError,SerialException) as err:
            # communication error with modem, likely assert
            print traceback.format_exc()
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None

            # capture core dump and close modem connection
            if self.modemObj:
                rf_cf.pause(duration_s=20, poll_time_sec=2, desc="short pause prior to modem crash detection!!")
                if self.modemObj.check_for_crash():
                    self.capture_core_dump()
                else:
                    # no point in shutting down as there is likely
                    # communication issue with modem
                    self.modemObj.close()
                    self.modemObj=None

            verdictStr = rf_global.verdict_dict[rf_global.FAIL]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            return verdictStr,self.verdictObj
        except ExFail:
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            verdictStr = rf_global.verdict_dict[rf_global.FAIL]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except ExUserBreakPoint, e:
            print '%s' %e.message
            verdictStr = rf_global.verdict_dict[rf_global.INCONC]
            return verdictStr,self.verdictObj

        except ExGeneral, e:
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            verdictStr = rf_global.verdict_dict[rf_global.INCONC]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            print '%s' %e.message
            return verdictStr,self.verdictObj

        except Exception:
            print traceback.format_exc()
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            self.shut_down_modem()
            self.recordVerdict(verdictStr='Inconclusive')
            verdictStr=self.verdictObj.GetSummaryVerdict(col_len=80)
            self.update_csvSummaryReport(verdictStr=verdictStr)
            return verdictStr,self.verdictObj

    def GetTesterMeasurments (self, exp_powerdBm, tol_dB, exp_no_signal=False):

        meas_val_dict = {'UE_POW': 1, 'FREQ_ERR': 1, 'IQ_OFFSET': 1,
                         'IQ_IMBALANCE': 1, 'EVM' : 1, 'PHASE_ERR':1,
                         'QUAD_ERR' : 1}

        check_supported(check_val_list=self.meas_list,
                        valid_meas_dic=meas_val_dict)

        self.instr.lte_tx.set_init_meas_flag(True)

        if exp_no_signal:
            try:
                # Should fail and raise an exception.
				# Otherwise the power check registers a failure.
                self.get_agc_pwr_meas(expected_pwr_dBm=-9999)
            except ExGeneral:
                self.recordVerdict("PASS")
        else:
            for meas in self.meas_list:

                self.teststep_idx += 1

                self.set_meas(meas=meas)

                if meas == 'UE_POW':
                    self.get_agc_pwr_meas(expected_pwr_dBm=exp_powerdBm, tol_dB=tol_dB)


                elif meas == 'FREQ_ERR':
                    self.get_freq_err_meas()

                elif meas == 'IQ_OFFSET':
                    self.get_IQ_offset_meas()

                elif meas == 'IQ_IMBALANCE':
                    cmwswinfo = self.get_instr_sw_version()
                    self.instr.checkSwVersion(cmwswinfo)
                    self.get_IQ_imbalance_meas()

                elif meas == 'QUAD_ERR' :
                    cmwswinfo = self.get_instr_sw_version()
                    self.instr.checkSwVersion(cmwswinfo)
                    self.get_quad_error_meas()

                elif meas == 'EVM':
                    self.get_modem_evm_meas()

                elif meas == 'PHASE_ERR':
                    self.get_phase_err_meas()

                else:
                    pass

                self.instr.lte_tx.set_init_meas_flag(False)

        # Set init_meas_flag back
        self.instr.lte_tx.set_init_meas_flag(True)

    def setup_fdd(self,earfcn,bwMhz,powerdBm,with_rx=False):
        self.setup_modem()

        self.instr.setup_4g_tx_test(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0

        band,freq_ul,freq_dl = lte_util.get_lte_ul_dl_freq_band(earfcn)

        self.set_band(band=band)
        assert(self.get_duplex_mode() == "FDD")
        self.modemObj.set_rat_band(rat='LTE', band=band)
        self.instr.lte_tx.set_band(band=band)
        self.set_bw(bwMHz=bwMhz)
        rf_config = LTE_rf_config(bwMHz=bwMhz)
        self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
        self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
        rf_config.check_config()
        self.instr.lte_tx.set_channel_bw_MHz(bwMHz=bwMhz)
        self.modemObj.send_ul_pattern()
        self.modemObj.set_freqMHz(freqMHz=freq_ul)
        self.instr.lte_tx.set_rf_freqMHz(freqMHz=freq_ul)
        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.instr.lte_tx.set_rf_exp_power(power_dBm=powerdBm+10)
        self.modemObj.enable_tx()

        if with_rx:
            self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
            self.modemObj.set_rxagc_auto(ant='m')
            self.modemObj.enable_rx(ant='m')

        self.instr.waitForCompletion()

        self.set_test_afc_val()


    def modulated_uplink_pattern_test(self,earfcn,bwMhz,powerdBm,with_rx=False):
        #set measurment list
        self.meas_list = ['FREQ_ERR','IQ_OFFSET', 'PHASE_ERR', 'EVM']
        self.setup_fdd(earfcn,bwMhz,powerdBm,with_rx)
        self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                  tol_dB=1.5)


    def setup_tdd_trigger(self,bursted,special_sf_config):
        if bursted:
            self.instr.lte_tx.set_trig_source('IF_Power')
            trig_delay = 71 if special_sf_config <= 4 else 143
            self.instr.lte_tx.set_trig_delay(trig_delay)
        else:
            self.instr.lte_tx.set_trig_source('FreeRunFastSync')

    def setup_tdd(self,earfcn,bwMhz,powerdBm,ud_config,special_sf_config=0,ul_timing_advance=0,with_rx=False):
        """Sets up LTE TDD according to the arguments. Used by several TDD tests."""

        self.setup_modem()
        self.instr.setup_4g_tx_test(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        band,freq_ul,freq_dl = lte_util.get_lte_ul_dl_freq_band(earfcn)

        self.set_band(band=band)
        self.modemObj.set_rat_band(rat='LTE', band=band)
        duplex_mode = self.get_duplex_mode()
        assert(duplex_mode == "TDD")
        self.instr.lte_tx.set_duplex_mode(duplex_mode=duplex_mode)
        self.instr.lte_tx.set_band(band=band)
        self.modemObj.set_freqMHz(freqMHz=freq_ul)
        self.instr.lte_tx.set_rf_freqMHz(freqMHz=freq_ul)
        self.set_bw(bwMHz=bwMhz)
        rf_config = LTE_rf_config(bwMHz=bwMhz)
        self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
        self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
        rf_config.check_config()
        self.instr.lte_tx.set_channel_bw_MHz(bwMHz=bwMhz)
        self.modemObj.send_ul_pattern()

        self.set_ud_config(ud_config)
        self.modemObj.set_ud_config(ud_config)
        self.instr.lte_tx.set_ul_dl_conf(ud_config)

        self.modemObj.enable_tx()

        bursted = not (ud_config=="TEST0" or ud_config=="TEST1")
        self.setup_tdd_trigger(bursted,special_sf_config)

        self.modemObj.set_special_sf_config(special_sf_config)
        self.instr.lte_tx.set_special_subframe_conf(special_sf_config)

        self.modemObj.set_ul_timing_advance(ul_timing_advance)

        meas_sf = 2
        self.set_meas_sf(meas_sf)
        self.instr.lte_tx.conf_measurement_subframe(measSubframe=meas_sf)

        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.instr.lte_tx.set_rf_exp_power(power_dBm=powerdBm+5)
        self.instr.waitForCompletion()

        if with_rx:
            assert(bursted)
            self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
            self.modemObj.set_rxagc_auto(ant='m')
            self.modemObj.enable_rx(ant='m')

        self.set_test_afc_val()

        return bursted

    def modulated_uplink_pattern_tdd_test(self,earfcn,bwMhz=5,powerdBm=-10,ud_config=1,special_sf_config=0,ul_timing_advance=0,sf_sweep=False,with_rx=False):
        self.meas_list = ['FREQ_ERR','IQ_OFFSET', 'EVM']
        bursted = self.setup_tdd(earfcn,bwMhz,powerdBm,ud_config,special_sf_config,ul_timing_advance,with_rx=with_rx)
        tol_dB = 1
        sf_sweep = bursted and sf_sweep
        meas_sf_list = range(10) if sf_sweep else [2]   # 2 is always UL
        for meas_sf in meas_sf_list:
            self.set_meas_sf(meas_sf)
            self.instr.lte_tx.conf_measurement_subframe(measSubframe=meas_sf)

            if sf_is_uplink(ud_config, meas_sf):
                self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                          tol_dB=tol_dB)
            else:
                # Non-UL subframe, do not expect signal
                self.GetTesterMeasurments(exp_powerdBm=-9999,
                                          tol_dB=0,
                                          exp_no_signal=True)

        self.modemObj.disable_tx()

    def tx_switch_channel(self,earfcn,bwMhz,powerdBm,ud_config=None,iterations=4,with_rx=False):
        """Verify that changing frequency while TX is running works.
        Turn on tx and switch between the given earfcn and 10 MHz higher 10 times."""

        self.meas_list = ['EVM']
        if earfcn >= 36000:
            self.setup_tdd(earfcn,bwMhz,powerdBm,ud_config,with_rx=with_rx)
        else:
            assert(ud_config is None)
            self.setup_fdd(earfcn,bwMhz,powerdBm,with_rx)

        tol_dB = 1

        earfcn_list = [earfcn, earfcn + 100] * iterations
        for current_earfcn in earfcn_list:
            _,freq_ul,freq_dl = lte_util.get_lte_ul_dl_freq_band(current_earfcn)
            self.modemObj.set_freqMHz(freqMHz=freq_ul)
            if with_rx:
                self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)

            self.instr.lte_tx.set_rf_freqMHz(freqMHz=freq_ul)

            self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                      tol_dB=tol_dB)

    def tx_switch_band(self,band1,band2,bwMhz,powerdBm,ud_config=None):
        """Start TX on one band, stop tx, switch band, start tx."""
        self.meas_list = ['EVM']
        tol_dB = 1

        earfcn1 = lte_util.ul_Default_EARFCN(band1)

        if earfcn1 >= 36000:
            self.setup_tdd(earfcn1,bwMhz,powerdBm,ud_config)
        else:
            self.setup_fdd(earfcn1,bwMhz,powerdBm)

        self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                  tol_dB=tol_dB)

        self.modemObj.disable_tx()

        # Set band2
        earfcn2 = lte_util.ul_Default_EARFCN(band2)
        self.set_band(band2)
        self.modemObj.set_rat_band(rat='LTE', band=band2)
        duplex_mode = self.get_duplex_mode()
        self.instr.lte_tx.set_duplex_mode(duplex_mode)
        self.instr.lte_tx.set_band(band2)

        if duplex_mode == 'TDD':
            self.set_ud_config(ud_config)
            self.modemObj.set_ud_config(ud_config)
            self.instr.lte_tx.set_ul_dl_conf(ud_config)
            meas_sf = 2
            self.set_meas_sf(meas_sf)
            self.instr.lte_tx.conf_measurement_subframe(measSubframe=meas_sf)

        bursted = duplex_mode == 'TDD' and ud_config != "TEST1"
        self.setup_tdd_trigger(bursted,special_sf_config=0)

        _,freq_ul2,_ = lte_util.get_lte_ul_dl_freq_band(earfcn2)
        self.modemObj.set_freqMHz(freqMHz=freq_ul2)
        self.instr.lte_tx.set_rf_freqMHz(freq_ul2)

        self.modemObj.enable_tx()

        self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                  tol_dB=tol_dB)

    def tx_switch_bandwidth(self,earfcn,powerdBm=-10,ud_config=None,with_rx=False,bwMhz_list=[5, 10, 15, 20, 5]):
        """Start TX and switch between bandwidths."""

        self.meas_list = ['EVM']
        bwMhz=5
        if earfcn >= 36000:
            self.setup_tdd(earfcn,bwMhz,powerdBm,ud_config,with_rx=with_rx)
        else:
            assert(ud_config is None)
            self.setup_fdd(earfcn,bwMhz,powerdBm,with_rx)

        tol_dB = 1

        for bwMhz in bwMhz_list:
            logging.info("Testing bandwidth %s..." % bwMhz)
            self.set_bw(bwMHz=bwMhz)
            rf_config = LTE_rf_config(bwMHz=bwMhz)
            self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
            self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
            self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
            self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
            rf_config.check_config()

            self.instr.lte_tx.set_channel_bw_MHz(bwMHz=bwMhz)

            self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                      tol_dB=tol_dB)


    def direct_mode_test(self,earfcn,bwMhz,powerdBm,ud_config,sf_sweep=False,with_rx=False):
        """Tests direct gain mode. Set the given powerdBm in driver mode, read back the DAC value,
        and then test that value in direct mode."""

        self.meas_list = ['FREQ_ERR','IQ_OFFSET', 'EVM']
        tol_dB = 1

        bursted = self.setup_tdd(earfcn,bwMhz,powerdBm,ud_config,with_rx=with_rx)

        self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                  tol_dB=tol_dB)

        # Note - Direct AGC value leads to different powers on different platforms
        # -- use driver mode and read back AGC value to get baseline,
        # then try that value in direct mode.
        dac_value = self.modemObj.query_txagc()

        # Set minimum power
        self.modemObj.set_txagc_dbm(value=-70)
        self.GetTesterMeasurments(exp_powerdBm=-9999,
                                  tol_dB=0,
                                  exp_no_signal=True)

        # Set the original power, but as a direct gain DAC word this time.
        self.modemObj.set_txagc_direct(value=dac_value)

        sf_sweep = bursted and sf_sweep
        meas_sf_list = range(10) if sf_sweep else [2]   # 2 is always UL
        for meas_sf in meas_sf_list:
            self.set_meas_sf(meas_sf)
            self.instr.lte_tx.conf_measurement_subframe(measSubframe=meas_sf)

            if sf_is_uplink(ud_config, meas_sf):
                self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                          tol_dB=tol_dB)
            else:
                # Non-UL subframe, do not expect signal
                self.GetTesterMeasurments(exp_powerdBm=-9999,
                                          tol_dB=0,
                                          exp_no_signal=True)

        meas_sf = 2
        self.set_meas_sf(meas_sf)
        self.instr.lte_tx.conf_measurement_subframe(measSubframe=meas_sf)

        # Check going back to driver mode
        self.modemObj.set_txagc_dbm(value=-70)
        self.GetTesterMeasurments(exp_powerdBm=-9999,
                                  tol_dB=0,
                                  exp_no_signal=True)
        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.GetTesterMeasurments(exp_powerdBm=powerdBm,
                                  tol_dB=tol_dB)


    def dc_uplink_pattern_test(self,earfcn,bwMhz):

        #Note - amplitude of IQ data affects outdut power.
        #Using driver mode at 0dBm on a Lara the power is near 0dBm with max_i,max_q = 370
        #Use a fixed driver dBm value of 0 with IQ amplitude of 370 and calculate the expected
        #power for other IQ amplitude values.
        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_power_meas(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        agc_val = 0
        iq_step = 200
        def_iq_amp = 370
        powerdBm = 0

        band,freq_ul,freq_dl = lte_util.get_lte_ul_dl_freq_band(earfcn)

        self.modemObj.set_rat_band(rat='lte', band=band)
        self.instr.gprf_meas.set_rf_exp_power(power_dBm=powerdBm+10)
        self.set_band(band=band)

        self.set_bw(bwMHz=bwMhz)
        rf_config = LTE_rf_config(bwMHz=bwMhz)
        self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
        self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
        rf_config.check_config()
        self.modemObj.set_txagc_dbm(value=agc_val)

        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.gprf_meas.set_rf_freqMHz(freqMHz=freq_ul)
        self.modemObj.enable_tx()

        #Set default IQ Amp
        self.modemObj.send_ul_pattern_arb(patt_type='dc',offset_q=0,max_i=def_iq_amp,min_i=-def_iq_amp,max_q=def_iq_amp,min_q=-def_iq_amp)
        #Check txdata validitiy
        iqdata_verdict = self.check_for_valid_dc_txdata(def_iq_amp)
        self.set_meas("Power Step Check")
        pwrstepVerdict = "FAIL"
        pwr_read_def = self.instr.gprf_meas.get_meas_fft_peak_power_single()
        print "Power Default IQ: %f" % pwr_read_def
        self.modemObj.send_ul_pattern_arb(patt_type='dc',offset_q=0,max_i=def_iq_amp+iq_step,min_i=-def_iq_amp-iq_step,max_q=def_iq_amp+iq_step,min_q=-def_iq_amp-iq_step)
        pwr_read_step = self.instr.gprf_meas.get_meas_fft_peak_power_single()
        print "Power Step IQ: %f" % pwr_read_step
        #if power has stepped up by at least 1.3dB
        self.set_meas(self.get_meas()+"Power Step: %s" % str(pwr_read_step - pwr_read_def))
        if (pwr_read_step - pwr_read_def) > 1.3:
            pwrstepVerdict = "PASS"
        self.recordVerdict(pwrstepVerdict)


    def sine_uplink_pattern_test(self,earfcn,bwMhz,powerdBm):

        #Note - amplitude of IQ data affects outdut power.
        #Using driver mode at 0dBm on a Lara the power is near 0dBm with max_i,max_q = 370
        #Use a fixed driver dBm value of 0 with IQ amplitude of 370 and calculate the expected
        #power for other IQ amplitude values.
        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_power_meas(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        agc_val = 0
        def_iq_amp = 530
        iq_step = 200
        n_samples = 40
        bw_sampling_rate_dic={5:7.68e6,10:15.36e6,15:30.72e6,20:30.72e6}

        band,freq_ul,freq_dl = lte_util.get_lte_ul_dl_freq_band(earfcn)

        self.modemObj.set_rat_band(rat='lte', band=band)
        self.instr.gprf_meas.set_rf_exp_power(power_dBm=agc_val+10)
        self.set_band(band=band)

        self.set_bw(bwMHz=bwMhz)
        rf_config = LTE_rf_config(bwMHz=bwMhz)
        self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
        self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
        self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
        rf_config.check_config()
        self.modemObj.set_txagc_dbm(value=agc_val)
        tone_freq = bw_sampling_rate_dic[bwMhz]/n_samples

        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.gprf_meas.set_rf_freqMHz(freqMHz=freq_ul)
        self.modemObj.enable_tx()

        #Set default IQ Amp
        self.modemObj.send_ul_pattern_arb(patt_type='sine',n_samples=n_samples,offset_q=n_samples/4,max_i=def_iq_amp,min_i=-def_iq_amp,max_q=def_iq_amp,min_q=-def_iq_amp)
        #Check txdata validitiy
        iqdata_verdict = self.check_for_valid_sine_txdata(iq_amp=def_iq_amp)

        self.set_meas("Sine Frequency Check")
        freq_read = self.instr.gprf_meas.get_meas_fft_peak_single()
        print "Frequency Readback %f" % freq_read
        freqverdictStr = self.get_meas_range_verdict(exp_measurement=tone_freq,measurement=freq_read,tolerance=8000)
        self.recordVerdict(freqverdictStr)

        self.set_meas("Power Step Check")
        pwrstepVerdict = "FAIL"
        #get power using default IQ amplitude
        pwr_read_def = self.instr.gprf_meas.get_meas_fft_peak_power_single()
        print "Power Default IQ: %f" % pwr_read_def
        self.modemObj.send_ul_pattern_arb(patt_type='sine',n_samples=n_samples,offset_q=n_samples/4,max_i=def_iq_amp+iq_step,min_i=-def_iq_amp-iq_step,max_q=def_iq_amp+iq_step,min_q=-def_iq_amp-iq_step)
        pwr_read_step = self.instr.gprf_meas.get_meas_fft_peak_power_single()
        print "Power Step IQ: %f" % pwr_read_step
        #if the IQ step has increased power by at least 1.5dB
        if (pwr_read_step - pwr_read_def) > 1.5:
            pwrstepVerdict = "PASS"
        self.recordVerdict(pwrstepVerdict)
