#-------------------------------------------------------------------------------
# Name:        wcdma_tx
# Purpose:      execute the WCDMA Tx tests
#
# Author:      joashr
#
# Created:     11/06/2014
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

from pl1_rf_system.common.config.umts_utilities import *
from pl1_rf_system.common.rf_modem import *
import pl1_rf_system.instr.cmu200 as cmu
import pl1_rf_system.instr.cmw500 as cmw500
from pl1_rf_system.common.user_exceptions import *
from pl1_rf_system.instr.measurementClass import MeasurementClass
from pl1_rf_system.common.verdict import Verdict
import pl1_rf_system.common.rf_common_globals as rf_global
import pl1_rf_system.common.rf_common_functions as rf_cf
from pl1_rf_system.common.report.csv.CsvReport import CsvReport
from pl1_rf_system.instr.cmw_wcdma_meas import Wcdma_meas
from serial import SerialException


from time import sleep

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

class Wcdma_tx(object):

    def __init__ (self, testID, testConfig_s, results_f, test_func, test_params, test_rat, final_test, unittest_enabled):

        func_name = sys._getframe(0).f_code.co_name
        loggerTest = logging.getLogger(__name__ + func_name)

        self.testConfig = testConfig_s

        self.test_func = test_func

        self.test_rat = test_rat

        self.test_params = test_params

        self.FinalTest = final_test

        self.testID = testID

        self.modemObj = None

        self.instr = None

        self.test_rat = 'WCDMA'

        self.results_f = results_f

        self.set_meas("Init - no measurment set")

        # rows and columns for EVM
        if self.testConfig.instr_name == "CMW500":
            self.rowDict_EVM = {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',
                    3:'Carrier_freq_err', 4:'Peak_Code_Dom_err', 5:'UEpower'}
        else:
            self.rowDict_EVM = {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',
                                3:'Carrier_freq_err', 4:'Peak_Code_Dom_err'}
        self.colDict_EVM = {0:'Current', 1:'Average', 2:'Max/Min'}

        # rows and columns for Phase error
        self.rowDict_PERR = {0:'PhaseErr_peak', 1:'PhaseErr_rms', 2:'IQ_origin_offset',
                             3:'Carrier_freq_err', 4:'Peak_Code_Dom_err'}

        self.colDict_PERR = self.colDict_EVM

        # rows and columns for WCDMA overview (CMU200 or)
        if self.testConfig.instr_name == "CMW500":

            #self.rowDict_Overview = Wcdma_meas().MEV_MOD_DICT
            self.rowDict_Overview = {}

            # interchange key, value from dictionary and subtract 1 so that the new
            # dictionary key corresponds to zero index row number e.g.
            # 0:'Reliability' etc

            for key in Wcdma_meas().MEV_MOD_DICT.keys():
                #self.rowDict_Overview [Wcdma_meas().MEV_MOD_DICT[key]-1]=key
                self.rowDict_Overview [Wcdma_meas().MEV_MOD_DICT[key]]=key

            for key in sorted(self.rowDict_Overview.keys()):
                loggerTest.debug ("%s => %s" %(key, self.rowDict_Overview[key]))


        else:

            self.rowDict_Overview = {0:'EVM_peak', 1:'EVM_rms', 2:'MagErr_peak',
                                     3:'MagErr_rms', 4:'PhaseErr_peak', 5:'PhaseErr_rms',
                                     6:'IQ_origin_offset', 7:'IQ_imbalance', 8:'Carrier_freq_err',
                                     9:'Waveform_Quality', 10:'Peak_Code_Domain_Err', 11:'PCDE Code',
                                     12:'Transit_Time_Err'}

        self.colDict_Overview = self.colDict_EVM

        self.evm = MeasurementClass(rowDict=self.rowDict_EVM,
                                    colDict=self.colDict_EVM,
                                    instrName=self.testConfig.instr_name)

        self.phase_err = MeasurementClass(rowDict=self.rowDict_PERR,
                                          colDict=self.colDict_PERR,
                                          instrName=self.testConfig.instr_name)

        self.wcdma_overview = MeasurementClass(rowDict=self.rowDict_Overview,
                                               colDict=self.colDict_Overview,
                                               instrName=self.testConfig.instr_name)


        self.meas_ref = "Unselected Meas"  # measurement reference from test plan e.g. "UE_POW"

        self.verdictObj = Verdict()

        self.instr_sw_version = ""

        self.unittest_enabled = unittest_enabled   # indicates if  this is run as a unittest
                                                   # it is is then modem setup and shutdown is controlled from
                                                   # unit test class rather than this class

        self.start_time=time.localtime()


    def get_run_as_unittest(self):

        return self.unittest_enabled


    def set_instr_sw_version(self, version):

        self.instr_sw_version = version

    def get_instr_sw_version(self):

        return self.instr_sw_version

    def set_csvSummaryReport(self, results_f, modeminfo, instrswinfo):
        rat = self.test_rat
        csv_f = rf_global.testSummaryFileName
        csv_abs_f= os.sep.join(results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h,
                                          frmt_msg = csv_frmt_msg,
                                          modeminfo = modeminfo,
                                          instrswinfo = instrswinfo)

    def update_csvSummaryReport(self, verdictStr):

        stopNow = False

        if(verdictStr != "PASS" and stopNow):
            print "Stopping with verdictStr=%s" % (verdictStr)
            exit(0)

        end_time=time.localtime()
        start_time_frmt=time.strftime("%Y/%m/%d %H:%M:%S", self.get_start_time())
        end_time_frmt=time.strftime("%Y/%m/%d %H:%M:%S", end_time)
        duration=time.mktime(end_time)-time.mktime(self.get_start_time())

        self.csvSummaryReport.append ([self.testID, verdictStr,
                                       start_time_frmt, end_time_frmt,
                                       duration])


    def set_meas(self, meas):
        self.meas_ref = meas

    def get_meas(self):
        return self.meas_ref

    def get_start_time(self):

        return self.start_time

    def capture_core_dump(self):

        logger_test = logging.getLogger(__name__ + ' capture_core_dump')
        if self.modemObj:
            self.modemObj.close()
            self.modemObj = None
        logger_test.error("MODEM CRASH DETECTED: collecting core dump")

        icera_tools_bin_path = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['common', 'icera'])

        get_crash_dump_log(core_dump_dir=self.results_f, icera_utils_path=icera_tools_bin_path)

    def setup_modem(self):

        mode = query_modem_mode()

        if mode != rf_global.FACTORY_TEST_MODE:

            set_modem_mode(mode = rf_global.FACTORY_TEST_MODE)

        try:
            self.modemObj = serialComms(verdictObj=self.verdictObj,timeout = 0.5)

        except Exception:
            print traceback.format_exc()
            if self.modemObj:
                if self.modemObj.check_for_crash():
                    rf_cf.pause(duration_s=10, poll_time_sec=2, desc="short pause after crash detection")
                    self.capture_core_dump()
                else:
                    self.modemObj.close()
                    self.modemObj=None
            errMsg = ("Unexpected or no reponse from modem")
            raise ExGeneral(errMsg)

        # Shut off anything that may have been left running previously
        self.modemObj.disable_tx_and_rx_unconditionally()

        assert(self.modemObj is not None)

    def set_breakpoint(self):
        errMsg = ("user breakpoint activated")
        raise ExUserBreakPoint(errMsg)

    def shut_down_modem(self):

        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)

        if self.modemObj:
            self.modemObj.disable_tx()
            self.modemObj.disable_rx()
            self.modemObj.close()

            if self.FinalTest and not self.get_run_as_unittest():
                set_modem_mode(mode = rf_global.NORMAL_TEST_MODE)
            elif self.get_run_as_unittest():
                # if run as unittest then mode should adready be in
                # FACTORY_TEST_MODE as chnage to NORMAL TEST MODE is handled
                # by unit test class
                loggerDisplay.debug("test ID %s is run as unit test" %self.testID)
                loggerDisplay.debug("modem will remain in factory test mode")
            else:

                loggerDisplay.debug("Not final Test - remain in mode=2")

        self.modemObj = None


    def _get_3g_tx_pwr_meas(self, exp_power_dBm):
        print "Performing modem Tx power measurement, please be patient ..."
        print "\n"
        meas_desc = "UE Tx Power (dBm)"
        heading_len = len(self.evm.get_col_title_str())
        (meas_array, limit_array)=self.get_evm_meas_wrapper()
        self.evm.populate_2d_array(meas_val_list=meas_array)
        self.evm.get_meas_2d_array()

        self.display_ue_tx_power_heading(subTestTitle=meas_desc, total_len=heading_len)
        ue_tx_power_dBm = self.get_ue_tx_power()

        verdictStr = self.get_ue_tx_pwr_verdict(exp_power_dBm=exp_power_dBm,
                                               measured_power_dBm=ue_tx_power_dBm,
                                               tol_dB=1.0)

        print "%s: %s" %(meas_desc, verdictStr)

        return verdictStr, ue_tx_power_dBm


    def get_agc_pwr_meas(self, expected_pwr_dBm):

        verdictStr, meas_tx_power = self._get_3g_tx_pwr_meas(exp_power_dBm=expected_pwr_dBm)

        self.recordVerdict(verdictStr=verdictStr.upper(),
                           add_meas_desc="(power dBm:%s)" %meas_tx_power)

        heading_len = len(self.evm.get_col_title_str())
        print "*" * heading_len
        print "\n"


    def get_ue_tx_power(self):

        # get the last row in 2d array corresponding to
        # UE Power Current, Out of Tolerance, Slot Number (WCDMA)
        # note that the nominal power is the nominal UE power
        # after adjusting for the cable loss which is set to the
        # Ext Att input
        (nominal_power_dBm, tol, slot_num) = self.evm.get_meas_2d_array()[-1]
        nominal_power_dBm = '%.2f' % float(nominal_power_dBm)
        print "Nominal UE Power Tx Power : %6s dBm "    % nominal_power_dBm
        return nominal_power_dBm


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

    def get_meas_range_verdict(self, exp_measurement, measurement, tolerance):
        # see if exepceted power is within the +/- tol_dB of expected power
        # and set the verdict accordingly
        verdict = "FAIL"
        upper_limit = 1.0 * float(exp_measurement) + tolerance
        lower_limit = 1.0 * float(exp_measurement) - tolerance

        if float(measurement) <= upper_limit and float(measurement) >= lower_limit:
            verdict = "PASS"
        else:
            verdict = "FAIL"

        return verdict

    def recordVerdict(self, verdictStr, add_meas_desc=""):
        """
        record verdict for each subtest
        add_meas_desc : additional measurement description
        if add_meas_desc is supplied then this is added to the meas_id as
        additional information
        """
        if add_meas_desc:
            if verdictStr.upper() == "PASS":
                self.verdictObj.CheckPassed(meas_id = self.get_meas() + add_meas_desc,
                                            info="Pass")
            else:
                self.verdictObj.CheckFailed(meas_id = self.get_meas() + add_meas_desc,
                                           info="Fail")
        else:
            if verdictStr.upper() == "PASS":
                self.verdictObj.CheckPassed(meas_id=self.get_meas(), info="Pass")
            else:
                self.verdictObj.CheckFailed(meas_id=self.get_meas(), info="Fail")


    def display_rows_from_evm_meas(self, descrption, row_dict_s):

        self.evm.set_subTestTitle(subTestTitle = descrption)
        self.evm.get_selected_2d_array(selectedRowDict=row_dict_s)
        self.evm.display_selected_meas()
        self.evm.display_limit_selected_meas()
        # not closed loop system (reduced signalling) therefore
        # frequency will drift and should not impact the results
        if row_dict_s.get(int('3')) != 'Carrier_freq_err':
            verdictStr = self.evm.getTestVerdict(array_2d_val=self.evm.get_selected_limit_2d_array())
            self.recordVerdict(verdictStr=verdictStr)
            print "%s: %s" %(descrption, verdictStr)
        else:
            print ("%s will not be included in results!"
                    %row_dict_s[3])
        self.evm.display_end_title()


    def get_evm_meas_wrapper(self, num_cycles=50):
        if self.testConfig.instr_name == "CMW500":
            (meas_array, limit_array)=self.instr.wcdma_tx.get_evm_meas(num_cycles)
        else:
            (meas_array, limit_array)=self.instr.get_evm_meas(num_cycles)
        return meas_array, limit_array


    def get_3g_freq_err_meas(self):
        print "Performing 3G frequency error measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array)=self.get_evm_meas_wrapper()
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "Carrier Frequency Error (Hz)"
        dict_s = {3:'Carrier_freq_err'}
        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)


    def get_IQ_offset_meas(self):
        print "Performing I/Q offset measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array)=self.get_evm_meas_wrapper()
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "I/Q Origin Offset (dB)"
        dict_s =  {2:'IQ_origin_offset'}
        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)


    def get_row_dict(self, meas_param_key):
        # get row => meas_param_key dictionary
        # enables the selection of the correct row
        dict_s = None
        self.rowDict_Overview
        for key in self.rowDict_Overview.keys():
            if self.rowDict_Overview[key] == meas_param_key:
                if self.testConfig.instr_name == "CMW500":
                    # note that reliability is not included
                    # in the 2d results array
                    reliability_offset = 1
                    dict_s = {key:self.rowDict_Overview[key]}
                else:
                    dict_s = {key:self.rowDict_Overview[key]}
                break
        if dict_s:
            return dict_s
        else:
            errMsg = "Meas param %s cannot be found. Valid key list is %s" %(meas_param_key, self.rowDict_Overview.values())
            raise ExGeneral(errMsg)

    def get_IQ_imbalance_meas(self):
        print "Performing I/Q imbalance measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array)=self.get_wcdma_mod_overview_results_wrapper()
        self.wcdma_overview.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "I/Q Imbalance (dB)"
        if self.testConfig.instr_name == "CMW500":
            selected_meas = 'IQimbalance'
        else:
            selected_meas = 'IQ_imbalance'
        dict_s = self.get_row_dict(meas_param_key=selected_meas)
        self.wcdma_overview.set_subTestTitle(subTestTitle = meas_desc)
        self.wcdma_overview.get_selected_2d_array(selectedRowDict=dict_s)
        self.wcdma_overview.display_selected_meas()
        self.wcdma_overview.display_limit_selected_meas()
        verdictStr = self.wcdma_overview.getTestVerdict(array_2d_val=self.wcdma_overview.get_selected_limit_2d_array())
        print "%s: %s" %(meas_desc, verdictStr)
        self.recordVerdict(verdictStr=verdictStr)
        self.wcdma_overview.display_end_title()


    def get_modem_evm_results_wrapper(self):
        if self.testConfig.instr_name == "CMW500":
            (meas_array, limit_array)=self.instr.wcdma_tx.get_evm_meas()
        else:
            (meas_array, limit_array)=self.instr.get_evm_meas()
        return meas_array, limit_array

    def get_modem_evm_meas(self):
        print "Performing modem EVM measurement, please be patient ..."
        print "\n"
        (meas_array, limit_array)=self.get_modem_evm_results_wrapper()
        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "EVM Selected Measurements"
        if self.testConfig.instr_name == "CMW500":
            dict_s = {0:'EVM_peak', 1:'EVM_rms'}
        else:
            dict_s =  {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',4:'Peak_Code_Dom_err'}
        self.display_rows_from_evm_meas(descrption=meas_desc, row_dict_s=dict_s)

    def get_phase_err_meas_wrapper(self):
        if self.testConfig.instr_name == "CMW500":
            (meas_array, limit_array)=self.instr.wcdma_tx.get_perr_meas()
        else:
            (meas_array, limit_array)=self.instr.get_perr_meas()
        return meas_array, limit_array

    def get_phase_err_meas(self):
        # get phase measurements
        print "Performing phase error measurement, please be patient ..."
        print "\n"
        (phase_meas_array, phase_limit_array)=self.get_phase_err_meas_wrapper()
        self.phase_err.populate_2d_array(meas_val_list=phase_meas_array,
                                        limit_val_list=phase_limit_array)

        meas_desc = "Phase Measurements"
        if self.testConfig.instr_name == "CMW500":
            dict_s = {0:'PhErrorPeak', 1:'PhErrorRMS'}
        else:
            dict_s = {0:'PhaseErr_peak', 1:'PhaseErr_rms'}
        self.phase_err.set_subTestTitle(subTestTitle = meas_desc)
        self.phase_err.get_selected_2d_array(selectedRowDict=dict_s)
        self.phase_err.display_selected_meas()
        self.phase_err.display_limit_selected_meas()
        verdictStr = self.phase_err.getTestVerdict(array_2d_val=self.phase_err.get_selected_limit_2d_array())
        print "%s: %s" %(meas_desc, verdictStr)
        self.recordVerdict(verdictStr=verdictStr)
        self.phase_err.display_end_title()


    def get_wcdma_mod_overview_results_wrapper(self):
        if self.testConfig.instr_name == "CMW500":
            (meas_array, limit_array)=self.instr.wcdma_tx.get_wcdma_mod_overview_results()
        else:
            (meas_array, limit_array)=self.instr.get_wcdma_mod_overview_results()
        return meas_array, limit_array


    def get_wcdma_overview_meas(self):
        # get wcdma overview
        print "Performing wcdma overview measurement, please be patient ..."
        print "\n"
        (overview_meas_array, overview_limit_array)=self.get_wcdma_mod_overview_results_wrapper()
        print overview_meas_array
        print overview_limit_array
        self.wcdma_overview.populate_2d_array(meas_val_list=overview_meas_array,
                                             limit_val_list=overview_limit_array)
        meas_desc = "WCDMA Measurements"
        self.wcdma_overview.set_subTestTitle(subTestTitle = meas_desc)
        self.wcdma_overview.display_meas(type_flag=0)
        self.wcdma_overview.display_limit()
        verdictStr = self.wcdma_overview.getTestVerdict(array_2d_val=self.wcdma_overview.get_limit_2d_array())
        self.recordVerdict(verdictStr=verdictStr)
        print "%s: %s" %(meas_desc, verdictStr)
        self.wcdma_overview.display_end_title()


    def get_freq_err_info_tuple(self):
        """
        get "current" carrier ferequency error and carrier frequency limit
        error
        """

        (meas_array, limit_array)=self.get_evm_meas_wrapper(num_cycles=20)

        self.evm.populate_2d_array(meas_val_list=meas_array, limit_val_list=limit_array)
        meas_desc = "Carrier Frequency Error (Hz)"
        dict_s = {3:'Carrier_freq_err'}

        meas_desc = "Carrier Frequency Error (Hz)"
        self.evm.set_subTestTitle(subTestTitle = meas_desc)
        selected_2d_array, selected_limit_2d_array = self.evm.get_selected_2d_array(selectedRowDict=dict_s)
        freq_err_lim_str = selected_limit_2d_array[0][0]
        try:
            lim_desc = self.evm.dictKeysValidLim[freq_err_lim_str]
            freq_err_Hz = float (selected_2d_array[0][0])
        except KeyError:
                keysStr = ', '.join(self.evm.dictKeysValidLim.keys())
                raise ExGeneral('%s indicates invalid measurement. Expected values are : %s'
                                %(freq_err_lim_str, keysStr))

        return freq_err_Hz, freq_err_lim_str

    def check_for_valid_dc_txdata (self,iq_amp, n_samples = 20):
        self.set_meas('DC TXData Validitiy Check IQ Amp = %d' % iq_amp)
        testverdict = "PASS"
        idata,qdata=self.modemObj.query_txdata_raw(n_samples=n_samples)
        iqdata = idata
        iqdata.extend(qdata) #append lists
        for elem  in iqdata:
            if elem == 0 or elem != iqdata[0]:
                testverdict="FAIL"
        self.recordVerdict(testverdict)
        return testverdict

    def check_for_valid_sine_txdata (self, iq_amp=0,n_samples = 20):
        self.set_meas('Sine TXData Validitiy Check IQ Amp = %d' % iq_amp)
        zc = 0
        testverdict = "PASS"
        idata,qdata=self.modemObj.query_txdata_raw(n_samples=n_samples)
        iqdata = idata
        iqdata.extend(qdata) #append lists
        #Check for non zero elements
        for elem  in iqdata:
            if elem == 0:
                zc += 1
        if zc == n_samples:
            testverdict="FAIL"
        self.recordVerdict(testverdict)
        return testverdict

    def set_test_afc_val(self):
        """
        set afc values so that carrier frequency error is within the required
        range for test purposes
        """

        LOWER_FREQ_LIM_HZ = -500

        UPPER_FREQ_LIM_HZ = abs(LOWER_FREQ_LIM_HZ)

        AFC_STEP_SIZE = 200

        MAX_NUM_AGC_ITER = 10

        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        afc_val = self.modemObj.get_afc_val()
        afc_val = int(afc_val)
        loggerDisplay.info('Current afc value is %s' %afc_val)
        freq_err_Hz, freq_err_lim_str = self.get_freq_err_info_tuple()

        if freq_err_lim_str in ['ULEL', 'NMAU']:
            iteration = 0
            while freq_err_Hz < LOWER_FREQ_LIM_HZ and iteration < MAX_NUM_AGC_ITER:
                afc_val = afc_val - AFC_STEP_SIZE
                self.modemObj.set_afc_val(afc_val)
                loggerDisplay.info('Iteration %s' %(iteration+1))
                loggerDisplay.info("%s will try with new AFC value %s"
                                    %(self.evm.dictKeysValidLim[freq_err_lim_str], afc_val))
                freq_err_Hz, freq_err_lim_str = self.get_freq_err_info_tuple()
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
                self.modemObj.set_afc_val(afc_val)
                loggerDisplay.info('Iteration %s' %(iteration+1))
                loggerDisplay.info("%s will try with new AFC value %s"
                                    %(self.evm.dictKeysValidLim[freq_err_lim_str], afc_val))
                freq_err_Hz, freq_err_lim_str = self.get_freq_err_info_tuple()
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

        else:
            loggerDisplay.info('Unexpected response; %s' %freq_err_lim_str.upper())
            loggerDisplay.info('Will continue with current afc value')


    def executeTest(self,instr_control):

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

            if self.instr:
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

        except ExGeneral:
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            verdictStr = rf_global.verdict_dict[rf_global.INCONC]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except Exception:
            print traceback.format_exc()
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            self.recordVerdict(verdictStr='Inconclusive')
            verdictStr=self.verdictObj.GetSummaryVerdict(col_len=80)
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except AttributeError:
            errmsg = "Test does not exist in this file"
            print errmsg
            self.verdictObj.RecordError(errmsg)
            return verdictStr,self.verdictObj

    def GetTesterMeasurements (self, exp_powerdBm):
        """
        exp_powerdBm  : expected power in dBm for agcVal
        """

        meas_val_dict = {'UE_POW': 1, 'FREQ_ERR': 1, 'IQ_OFFSET': 1,
                         'IQ_IMBALANCE': 1, 'EVM' : 1, 'PHASE_ERR':1}

        check_supported(check_val_list=self.meas_list,
                        valid_meas_dic=meas_val_dict)

        self.instr.wcdma_tx.set_init_meas_flag(True)

        for meas in self.meas_list:

            self.teststep_idx += 1

            self.set_meas(meas=meas)

            if meas == 'UE_POW':
                self.get_agc_pwr_meas(expected_pwr_dBm=exp_powerdBm)

            elif meas == 'FREQ_ERR':
                self.get_3g_freq_err_meas()

            elif meas == 'IQ_OFFSET':
                self.get_IQ_offset_meas()

            elif meas == 'IQ_IMBALANCE':
                self.get_IQ_imbalance_meas()

            elif meas == 'EVM':
                self.get_modem_evm_meas()

            elif meas == 'PHASE_ERR':
                self.get_phase_err_meas()

            else:
                self.set_meas(meas="WCDMA Measurements Overview")
                self.get_wcdma_overview_meas()
                pass

            self.instr.wcdma_tx.set_init_meas_flag(flag=False)

        # Set init_meas_flag back
        self.instr.wcdma_tx.set_init_meas_flag(True)


    def driver_mode_uplink_pattern_test(self,uarfcn,powerdBm):

        #Set measurment list
        self.meas_list = ['FREQ_ERR', 'UE_POW', 'IQ_OFFSET', 'EVM', 'PHASE_ERR']

        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_3g_tx_test(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(uarfcn)

        self.modemObj.disable_tx()
        self.modemObj.set_rat_band(rat='3g', band=band)
        self.modemObj.enable_tx()
        self.modemObj.send_ul_pattern()
        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.wcdma_tx.set_rf_freqMHz(freqMHz=freq_ul)
        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.instr.wcdma_tx.set_rf_exp_power(power_dBm=powerdBm+5)
        self.instr.waitForCompletion()

        self.set_test_afc_val()

        self.GetTesterMeasurements(exp_powerdBm=powerdBm)


    def direct_mode_uplink_pattern_test(self,uarfcn):

        #Set measurment list
        self.meas_list = ['FREQ_ERR', 'UE_POW', 'IQ_OFFSET', 'EVM', 'PHASE_ERR']

        initial_power_dBm = -10
        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_3g_tx_test(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(uarfcn)

        self.modemObj.disable_tx()
        self.modemObj.set_rat_band(rat='3g', band=band)
        self.modemObj.enable_tx()
        self.modemObj.send_ul_pattern()
        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.wcdma_tx.set_rf_freqMHz(freqMHz=freq_ul)

        # Note - Direct AGC value leads to different powers on different platforms
        # -- use driver mode at -10 dBm and read back AGC value to get baseline,
        # then try that value in direct mode.

        self.modemObj.set_txagc_dbm(value=initial_power_dBm)
        dac_value = self.modemObj.query_txagc()
        self.modemObj.set_txagc_direct(value=dac_value)
        self.instr.wcdma_tx.set_rf_exp_power(power_dBm=initial_power_dBm+5)

        self.set_test_afc_val()

        self.GetTesterMeasurements(exp_powerdBm=initial_power_dBm)


    def dc_uplink_pattern_test(self,uarfcn):

        #Note - amplitude of IQ data affects outdut power.
        #Using driver mode at 0dBm on a Lara the power is near 0dBm with max_i,max_q = 370
        #Use a fixed driver dBm value of 0 with IQ amplitude of 370 and calculate the expected
        #power for other IQ amplitude values.
        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_power_meas(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        powerdBm = 0
        def_iq_amp = 370
        iq_step = 200

        band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(uarfcn)

        self.modemObj.disable_tx()
        self.modemObj.set_rat_band(rat='3g', band=band)
        self.modemObj.enable_tx()
        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.instr.gprf_meas.set_rf_exp_power(power_dBm=powerdBm+10)
        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.gprf_meas.set_rf_freqMHz(freqMHz=freq_ul)

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

    def sine_uplink_pattern_test(self,uarfcn):

        #Note - amplitude of IQ data affects outdut power.
        #Using driver mode at 0dBm on a Lara the power is near 0dBm with max_i,max_q = 370
        #Use a fixed driver dBm value of 0 with IQ amplitude of 370 and calculate the expected
        #power for other IQ amplitude values.
        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_power_meas(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0
        powerdBm = 0
        def_iq_amp = 530
        iq_step=200
        n_samples = 40
        tone_freq = 3.84e6 / 40

        band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(uarfcn)

        self.modemObj.disable_tx()
        self.modemObj.set_rat_band(rat='3g', band=band)
        self.modemObj.enable_tx()
        self.modemObj.set_txagc_dbm(value=powerdBm)
        self.instr.gprf_meas.set_rf_exp_power(power_dBm=powerdBm+10)
        self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
        self.instr.gprf_meas.set_rf_freqMHz(freqMHz=freq_ul)

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


    def temperature_sensor_test (self):
        verdictStr = "FAIL"
        self.set_meas("Temperature Monitor Check")

        self.setup_modem()

        self.modemObj.disable_tx()
        self.modemObj.set_rat_band(rat='3g', band=1)
        self.modemObj.enable_tx()

        #Check temperature
        initialTempStr = self.modemObj.query_temperature(temp_sensor=0)

        #Wait
        sleep(3)

        #Check temperature again - should have gone up
        laterTempStr = self.modemObj.query_temperature(temp_sensor=0)

        self.modemObj.disable_tx()

        try:
            self.set_meas("Temperature Conversion: %s, %s" % (initialTempStr,laterTempStr))
            initialTemp = float(initialTempStr)
            laterTemp = float(laterTempStr)
            #Check for -0.1K - i.e. invalid ADC reading
            if (laterTemp!=-0.1) and (initialTemp!=-0.1):
                #If temp increases
                if laterTemp >= initialTemp:
                    verdictStr = "PASS"
                else:
                    self.set_meas("Temperature Increase Check: %f -> %f" % (initialTemp,laterTemp))
            else:
                self.set_meas("Temperature Validity Check: %f, %f" % (initialTemp,laterTemp))
        except:
            verdictStr = "FAIL"

        self.recordVerdict(verdictStr)


