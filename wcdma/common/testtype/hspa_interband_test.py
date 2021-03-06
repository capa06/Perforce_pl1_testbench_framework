#-------------------------------------------------------------------------------
# Name:        hspa_interband class
# Purpose:
#
# Author:      joashr
#
# Created:     13/10/2014
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time, math
import traceback
from threading import Thread


import pl1_wcdma_testbench.test_env

import pl1_wcdma_testbench.common.common_functions as cf
import pl1_wcdma_testbench.common.common_globals as cg
from pl1_wcdma_testbench.common.config.cfg_conf import cfg_conf
from pl1_wcdma_testbench.common.config.cfg_error import cfg_error
from pl1_jenkins.common.enableLogging import enable_logging
from pl1_wcdma_testbench.common.report.csv.Csv2Xls import Csv2Xls
from pl1_wcdma_testbench.common.report.csv.CsvReport import CsvReport
from pl1_wcdma_testbench.common.config.cfg_test  import cfg_test
from pl1_wcdma_testbench.common.config.cfg_test_hspa import cfg_test_hspa
from pl1_wcdma_testbench.instr.cmw500 import *

from pl1_jenkins.common.modem import serialComms

from pl1_jenkins.instr.psu_control import Psu
from pl1_wcdma_testbench.instr.dmm import *

from pl1_wcdma_testbench.common.report.csv.CsvHspaReportBler import *
from pl1_wcdma_testbench.common.report.csv.Csv2Xls import Csv2Xls
from pl1_wcdma_testbench.common.report.html.Csv2Html import Csv2Html
from pl1_wcdma_testbench.common.report.sqllite.perf_bestscore_db import *
from pl1_wcdma_testbench.common.report.mysql.perf_bestscore_mySQLdb import *



from pl1_wcdma_testbench.common.testtype.testbler import Testbler


class modem(serialComms):
    def set_preferred_rat(self, rat="UTRAN"):
        loggerModem = logging.getLogger(__name__ + 'set_preferred_rat')
        if rat == "UTRAN":
            loggerModem.info("setting preferred RAT=UTRAN, band = %s" %band)
            cmd_l = [ r'at%inwmode=0,U,1']
            self.sendCmdList(cmd_l)
        else:
            print "RAT %s is not supported, no preference of RAT or band will be set!" %rat

        sys.exit(0)


class HspaInterBandBler(Testbler):

    def __init__ (self, testID="", results_f="", intraHO=0):

        self.config = None

        self.results_f = results_f

        csv_f='WCDMA_CMW500_TestReport_SUMMARY.csv'
        csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h, frmt_msg = csv_frmt_msg)

        self.testID = testID

        self.cur_test = cfg_test_hspa(testID)

        self.start_time=time.localtime()

        self.cvsReportBler = None

        self.csvReportBlerPathName = ""

        self.psu_bench=None

        self.dmm=None

        self.cmw=None

        self.modemObj = None

        self.thr_pwr=None # daemon thread for power measurements

        self.num_hsdpa_subframes=6000

        self.result = 0

        self.result_msg= 'OK'

        self.intraHO = intraHO

    def get_test_verdict(self, blerPerCentTol=3 ):

        """"
        see if the test is pass or fail
        measured Tput should be within perCent % of dlTputMaxVal
        """

        logger_test=logging.getLogger(__name__ + ' get_test_verdict')

        dlVerdict = "FAIL"
        dlbler = float(self.cmw.get_hsdpa_bler())
        blerPerCentTol = float(blerPerCentTol)

        logger_test.info("checking that DL BLER is less than %s" %blerPerCentTol)

        if dlbler <= blerPerCentTol:

            dlVerdict = "PASS"

        else:

            dlVerdict = "FAIL"

        return dlVerdict

    def get_dlbler_tol(self, tb_index, numCodes, modulation):
        """
        get the percentage bler tolerance for bler Tput
        """
        logger_test = logging.getLogger(__name__ + ' get_dlbler_tol')

        defaultTol = 3

        perCentTol = defaultTol

        return perCentTol

    def calc_suitable_hsdsch_code(self, numCodes):
        """
        return suitable channelisation code
        """

        logger_test = logging.getLogger(__name__ + ' calc_suitable_hsdsch_code')

        MAX_NUM_HSDPA_CODES = 16

        if numCodes >= 1 and numCodes <=15:

            if numCodes == 1:

                chan_code = 14

                return chan_code

            else:

                return MAX_NUM_HSDPA_CODES - numCodes

        else:

            logger_test.error('num HSDPA codes %s not supported, valid range 1 to 15' %numCodes)

            sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)


    def get_and_display_instr_meas(self, max_num_retries=1, numSubframes=2000):

        retryNum = 0
        ret_val = cg.SUCCESS
        while retryNum < max_num_retries:
            if self.cmw.get_hsdpa_ack_meas(numSubframes=numSubframes):
                # hsdpa ack measurements are valid
                break
            else:
                # invalid meas
                self.cmw.abort_hsdpa_ack_meas()
                retryNum +=1
                if retryNum == max_num_retries:
                    #self.result = self.code.ERRCODE_SYS_CMW_INVMEAS if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL
                    self.result = self.code.ERRCODE_SYS_CMW_INVMEAS
                    ret_val = self.result
                    return ret_val


        carrier1=0
        print self.cmw.hsdpa_meas[carrier1]

        if self.cmw.get_dc_hsdpa() == 1:
            carrier2=1
            print self.cmw.hsdpa_meas[carrier2]

        self.cmw.display_ack_trans_meas(carrier=1)

        if self.cmw.get_dc_hsdpa() == 1:
            self.cmw.display_ack_trans_meas(carrier=2)

        self.cmw.display_hsdpa_bler_cqi_subframes(carrier=1)

        if self.cmw.get_dc_hsdpa() == 1:
            self.cmw.display_hsdpa_bler_cqi_subframes(carrier=2)

        return ret_val


    def runTest(self):

        try:

            logger_test = logging.getLogger(__name__ + ' runTest')

            print self.cur_test

            # Open a connection to the CMW500
            # ====================================================
            cmwname = 'cmw500'
            self.cmw = CmuControl(name=cmwname, ip_addr=self.config.cmwip)
            logger_test.info("Connection to %s @ %s...OK" % (cmwname, self.config.cmwip))

            self.get_cmw_sw_version()

            # switch on power
            self.setup_pwr_meas(Vmax_V=3.8, Imax_A=5)

            self.cmw.Cell_OFF()
            #cf.pause(duration_s=25, poll_time_sec=5, desc= "modem boot up")

#            self.modemObj = serialComms(timeout = 2, simulate_usim=self.config.usimemu)
            self.modemObj = modem(timeout = 2, simulate_usim=self.config.usimemu)
            modeminfo = self.modemObj.getInfo()
            self.cur_test.set_modeminfo(modeminfo=modeminfo)

            # initialise cvs report bler, must be done here to extract modeminfo
            self.csvReportBler=CsvHspaReportBler(test_s = self.cur_test, test_conf=self.config,
                                                 csv_fname=self.csvReportBlerPathName,
                                                 pwrmeas=self.config.pwrmeas)
            # Initialise database
            # ====================================================
            self.init_database()


            # Local constant and variables
            # ====================================================
            self.result, self.result_msg  = 0, 'OK'         # OK=0, ERROR otherwise
            teststep_idx=0                        # Test step index

            # CSV Bler report
            logger_test.debug("Total test steps = %s" % self.cur_test.get_total_test_steps())

            data_rate = self.cur_test.datarate[0]

            for rfband in self.cur_test.rfband:

                self.modemObj.set_preferred_rat(rat="UTRAN", band=rfband)


                for uarfcn in self.cur_test.uarfcn_dic[rfband]:

                    logger_test.debug("Selected RF_BAND=%s, DL_UARFCN=%s" % (rfband, uarfcn))

                    if self.intraHO:

                        matchObj = re.match('.*BLER_INTRAHO_(.*)', self.cur_test.testtype, re.I)

                        if matchObj:

                            uarfcn_intraho_l = self.get_intraHHO_list(band=rfband,
                                                                      num_uarfcn_sel_str=matchObj.group(1))

                            num_hho_steps = len(uarfcn_intraho_l)

                        else:

                            sys.exit(self.code.ERRCODE_TEST_FAILURE_INTRAHO)

                    else:

                        uarfcn_intraho_l =[uarfcn]

                    for rfpower in self.cur_test.rfpower:

                        for txants in self.cur_test.txants:

                            for snr in self.cur_test.snr:

                                for modulation in self.cur_test.modulation:

                                    for num_hsdpa_codes in self.cur_test.num_hsdsch_codes:

                                        for tb_index in self.cur_test.ki:

                                            logger_test.info("Resetting CMW500")
                                            self.cmw.reset()

                                            self.cmw.max_hspa_tputConfig(modulation='64-QAM', numHsdschCodes=15, ki = 62,
                                                                         hsupa_cat=6, tti_ms = 10)

                                            cf.pause(duration_s=1, poll_time_sec=1, desc= "short pause for cmw init config")

                                            self.cmw.set_rf_band(rfband)

                                            self.cmw.set_uarfcn(uarfcn)

                                            self.cmw.set_rf_power_dbm(rfpower)

                                            self.cmw.set_hsdpa_modulation(modulation= modulation)

                                            chan_code = self.calc_suitable_hsdsch_code(num_hsdpa_codes)

                                            self.cmw.set_hsdsch_chanelisation_code(code=chan_code, carrier=1)

                                            self.cmw.set_hsdsch_num_codes(numCodes=num_hsdpa_codes)

                                            if num_hsdpa_codes == 1:

                                                self.cmw.set_hsdsch_level(leveldB=-4)

                                            else:

                                                self.cmw.set_hsdsch_level(leveldB=-1)


                                            self.cmw.set_hsdpa_tbi(ki=tb_index)

                                            self.cmw.Cell_OFF()

                                            # radio off
                                            self.disable_modem_fun()

                                            # ENABLE LOG
                                            # ====================================================
                                            modemLogBaseName=""
                                            modemLogBaseName='WCDMA_CMW500_test_id_%s_modem_tbi_%s_mod_%s_numCodes_%s' %(self.testID,
                                                                                                                         tb_index,
                                                                                                                         modulation,
                                                                                                                         num_hsdpa_codes)

                                            proc_id = self.start_modem_log_capture(basefilename=modemLogBaseName)

                                            self.cmw.Cell_ON()

                                            # DUT ON
                                            self.modemObj.funcON()

                                            # DUT ATTACH
                                            # =========================================================
                                            T0=time.time()     # Probe start time
                                            if not self.cmw.dut_attach():
                                                logger_test.debug("ATTACH FAILURE: Skipping DL BLER test")
                                                self.result = self.code.ERRCODE_TEST_FAILURE_ATTACH if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL
                                                sys.exit(self.result)

                                            # Check for chanelisation code conflict
                                            # =========================================================
                                            if self.cmw.check_code_conflict():
                                                logger_test.error (" code conflict detected" )
                                                self.result = self.code.ERRCODE_TEST_FAILURE_TESTCONFIG if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL


                                            # DUT CONNECT
                                            # =========================================================
                                            if not self.cmw.dut_connect():
                                                logger_test.debug("CONNECT FAILURE: Skipping DL BLER test")
                                                self.result = self.code.ERRCODE_TEST_FAILURE_CEST if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL
                                                sys.exit(self.result)
                                            Tf=time.time()

                                            logger_test.debug("DUT CONNECTION PROCEDURE: T0=%d, Tf=%d, Tf-T0[sec]=%d" % (T0, Tf, math.floor(Tf-T0)))

                                            for uarfcn_intraho in uarfcn_intraho_l :

                                                teststep_idx += 1

                                                uarfcn_hho_target = uarfcn_intraho

                                                if self.intraHO :

                                                    logger_test.info("Intra HHO - Running step %s of %s..." % (teststep_idx, num_hho_steps))

                                                    logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                                    ", target uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn_hho_target, rfpower, snr) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s"
                                                    %(modulation, num_hsdpa_codes, tb_index))

                                                    if teststep_idx == 1:
                                                        uarfcn_hho_source = uarfcn
                                                    else:
                                                        uarfcn_hho_source = uarfcn_prev_loop

                                                    logger_test.info("Starting blind HO from UARFCN %s (%s MHz) to target UARFCN %s (%s MHz)"
                                                                      % (uarfcn_hho_source, get_umts_dl_freq(uarfcn_hho_source),
                                                                         uarfcn_hho_target, get_umts_dl_freq(uarfcn_hho_target)))
                                                    self.cmw.set_uarfcn(uarfcn=uarfcn_intraho, carrier=1)
                                                    dl_chan=self.cmw.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier1:CHANnel:DL?')
                                                    dl_freq=self.cmw.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier1:FREQuency:DL?')

                                                    logger_test.info('cmw changed to UARFCN=%s, Freq=%s' %(dl_chan, dl_freq))

                                                    uarfcn_prev_loop = uarfcn_intraho

                                                    if self.cmw.readState() != 'CEST' :
                                                        msg='CONNECT ESTABLISHMENT FAILURE during INTRA HO'
                                                        logger_test.error(msg)
                                                        self.result = self.code.ERRCODE_TEST_FAILURE_INTRAHO if self.result == 0 else ERRCODE_TEST_FAILURE
                                                        sys.exit(self.result)
                                                    else:
                                                        logger_test.info("Blind HO SUCCESSFULL")
                                                        if 0:
                                                            raw_input("Check instrument and press [ENTER]")

                                                else:

                                                    logger_test.info("Running step %s of %s..." % (teststep_idx, self.cur_test.get_total_test_steps()))

                                                    logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                                    ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn, rfpower, snr) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s"
                                                    %(modulation, num_hsdpa_codes, tb_index))

                                                self.start_pwr_meas()

                                                # Get bler measurements
                                                # ========================

                                                #self.get_and_display_instr_meas(max_num_retries=2, numSubframes=self.num_hsdpa_subframes)

                                                # dynamic bler tolerance
                                                dlblerTol = self.get_dlbler_tol(tb_index=tb_index,
                                                                                numCodes=num_hsdpa_codes,
                                                                                modulation=modulation)

                                                max_num_retries=2

                                                retryNum = 1

                                                while retryNum < (max_num_retries+1):

                                                    try:

                                                        ret_val = self.get_and_display_instr_meas(max_num_retries=2, numSubframes=self.num_hsdpa_subframes)

                                                    except ValueError:

                                                        print traceback.format_exc()

                                                        if self.get_modemLogProcessRunning() == True:

                                                            self.end_modem_log_capture(proc_id=proc_id)

                                                        time_sec = 20

                                                        cf.pause(duration_s=time_sec, poll_time_sec=2, desc="pausing to give modem time to enter boot loader mode")

                                                        sys.exit(self.code.ERRCODE_TEST_FAILURE_CEST)

                                                    if ret_val == cg.SUCCESS:

                                                        verdict_s = self.get_test_verdict(blerPerCentTol=dlblerTol)

                                                        if 'PASS' in verdict_s:
                                                            break

                                                        else:
                                                            logger_test.info('Bler test failure - tolerance %s' %dlblerTol)
                                                            logger_test.info('Iteration %s of %s' %(retryNum, max_num_retries))


                                                    retryNum +=1

                                                if ret_val != cg.SUCCESS:
                                                    sys.exit(ret_val)

                                                if 'FAIL' in verdict_s:
                                                    self.result = self.code.ERRCODE_TEST_FAILURE_BLER if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL

                                                schedtype = self.cur_test.schedtype[0]

                                                if self.intraHO :
                                                    uarfcn_hho_str= str(uarfcn_hho_source) + " - " + str(uarfcn_hho_target)
                                                    param_list = [self.testID, rfband, uarfcn_hho_str, self.cur_test.chtype,
                                                                  data_rate, snr, rfpower, txants, schedtype, modulation,
                                                                  tb_index, num_hsdpa_codes]
                                                else:
                                                    param_list = [self.testID, rfband, uarfcn, self.cur_test.chtype,
                                                                  data_rate, snr, rfpower, txants, schedtype, modulation,
                                                                  tb_index, num_hsdpa_codes]

                                                carrier1=0
                                                meas_list = [self.cmw.get_hsdpa_measured_subframes(), self.cmw.hsdpa_meas[carrier1].get_maxTputMbps(), self.cmw.hsdpa_meas[carrier1].get_avgTputMbps(),
                                                             self.cmw.get_hsdpa_bler(carrier=1), dlblerTol, self.cmw.get_medianCqi(carrier=1)]
                                                first_tx = 0
                                                meas_list = meas_list + self.cmw.trans_meas_1[first_tx].get_list()

                                                # Add power measurements
                                                # ========================
                                                pwr_s = self.get_pwr_meas()

                                                # Update CSV report
                                                # ========================
                                                msg_s = param_list + meas_list + [verdict_s]

                                                if self.config.pwrmeas:
                                                    msg_s = msg_s + pwr_s

                                                self.csvReportBler.append(msg_s)

                                                if not self.intraHO :

                                                    self.cmw.dut_disconnect()

                                                    self.end_modem_log_capture(proc_id=proc_id)

                                                #self.process_log_capture()

                                                matchObj = re.match('\s*FAIL', verdict_s, re.I)
                                                if matchObj and self.config.msglog:
                                                    self.process_log_capture()
                                                    logger_test.info ("Test failure, modem log %s will be kept" %self.get_log_glp_f())
                                                elif self.config.msglog:
                                                    if os.path.isfile(self.get_log_iom_f()):
                                                        logger_test.info ("Test Pass, modem log %s will be removed" %self.get_log_iom_f())
                                                        try:
                                                            os.remove(self.get_log_iom_f())
                                                        except Exception:
                                                            print traceback.format_exc()
                                                            print "Non fatal error, will continue anyway"

                                            if self.intraHO :

                                                self.cmw.dut_disconnect()

            self.cmw.dut_detach()

            # end of outer for loop
            # Close CMW instances
            if self.cmw:

                self.close_conn_cmw()

            self.close_pwr_meas()

            # Close COM ports
            self.modemObj.close()

            # UPDATE DATABASE
            # ==========================
            if not self.intraHO:
                self.update_database()

            # Create XLS
            # ========================
            Csv2Xls(self.csvReportBlerPathName)

            # Create HTML
            # ========================
            Csv2Html(self.csvReportBlerPathName)

            #test_marker='PASS' if self.result==0 else 'FAILURE'
            test_marker=self.getVerdict(testStatus=self.result)

            self.update_summary_report(return_state=self.result, verdict_str=test_marker)

            return self.result

        except SystemExit, KeyboardInterrupt:

            # Propagate error
            exc_info = sys.exc_info()
            state=int('%s' % exc_info[1])

            test_marker=self.getVerdict(testStatus=state)

            if self.get_modemLogProcessRunning() == True:
                self.end_modem_log_capture(proc_id=proc_id)

                if test_marker.upper() == "FAILURE":
                    self.process_log_capture()

                else:
                    if os.path.isfile(self.get_log_iom_f()):
                        logger_test.info ("Test Pass, modem log %s will be removed" %self.get_log_iom_f())
                        try:
                            os.remove(self.get_log_iom_f())
                        except Exception:
                            print traceback.format_exc()
                            print "Non fatal error, will continue anyway"


            # Close CMW instances
            if self.cmw:
                self.cmw.abort_hsdpa_ack_meas()
                self.close_conn_cmw()
                self.cmw=None

            # capture core dump and close modem connection
            if self.modemObj:
                if self.modemObj.check_for_crash():
                    self.capture_core_dump()
                    cf.pause(duration_s=30, poll_time_sec=2, desc= "waiting for modem to enter normal mode")
                else:
                    self.modemObj.close()
                    self.modemObj=None

            self.close_pwr_meas()

            self.update_summary_report(return_state=state, verdict_str=test_marker)

            return(state)

        except Exception:

            # always make sure that we can kill the modem logging process if active
            if self.get_modemLogProcessRunning() == True:
                self.end_modem_log_capture(proc_id=proc_id)
                #self.process_log_capture()
                if os.path.isfile(self.get_log_iom_f()):
                    logger_test.info ("Test Pass, modem log %s will be removed" %self.get_log_iom_f())
                    try:
                        os.remove(self.get_log_iom_f())
                    except Exception:
                        print traceback.format_exc()
                        print "Non fatal error, will continue anyway"

            print traceback.format_exc()

            state = self.code.ERRCODE_UNHANDLED_EXECEPTION

            test_marker=self.getVerdict(testStatus=state)

            self.update_summary_report(return_state=state, verdict_str=test_marker)

            return state


if __name__ == '__main__':
    pass
