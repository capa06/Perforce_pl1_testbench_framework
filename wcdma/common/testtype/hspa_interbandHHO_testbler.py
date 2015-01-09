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

from pl1_testbench_framework.common.utils.os_utils import insertPause
from pl1_testbench_framework.wcdma.common.config.cfg_conf import cfg_conf
from pl1_testbench_framework.wcdma.common.report.csv.CsvReport import CsvReport
from pl1_testbench_framework.wcdma.common.config.cfg_test_hspa_interbandHHO import cfg_test_hspa_interbandHHO
import pl1_testbench_framework.wcdma.instr.cmw500 as cmw
from pl1_testbench_framework.wcdma.common.com.custom_modem import custom_modem
from pl1_testbench_framework.wcdma.common.report.csv.CsvHspaReportBler import CsvHspaReportBler
from pl1_testbench_framework.common.report.xls.csv2Xls import csv2Xls
from pl1_testbench_framework.common.report.html.Csv2Html import Csv2Html

from testbler import Testbler
from hspa_testbler import HspaTestbler

import pl1_testbench_framework.wcdma.common.config.umts_utilities as umts

class HspaInterBandHHO_testbler(HspaTestbler):

    def __init__ (self, testID="", results_f=""):

        self.config = None

        self.results_f = results_f

        csv_f='WCDMA_CMW500_TestReport_SUMMARY.csv'
        csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h, frmt_msg = csv_frmt_msg)

        self.testID = testID

        self.cur_test = cfg_test_hspa_interbandHHO(testID)

        self.start_time=time.localtime()

        self.cvsReportBler = None

        self.csvReportBlerPathName = ""

        self.psu_bench=None

        self.dmm=None

        self.cmw=None

        self.modemObj = None

        self.thr_pwr=None # daemon thread for power measurements

        self.num_hsdpa_subframes=1000

        self.result = 0

        self.result_msg= 'OK'


    def runTest(self):

        try:

            logger_test = logging.getLogger(__name__ + ' runTest')

            print self.cur_test

            if self.config.database:
                logger_test.info('Addition of results to local database is currently not supported!')
                self.config.database = 0

            if self.config.remoteDB:
                logger_test.info('Addition of results to remote database is currently not supported!')
                self.config.remoteDB = 0

            # Open a connection to the CMW500
            # ====================================================
            cmwname = 'cmw500'
            self.cmw = cmw.CmuControl(name=cmwname, ip_addr=self.config.cmwip)
            logger_test.info("Connection to %s @ %s...OK" % (cmwname, self.config.cmwip))

            self.get_cmw_sw_version()

            # switch on power
            self.setup_pwr_meas(Vmax_V=3.8, Imax_A=5)

            self.cmw.Cell_OFF()

            self.modemObj = custom_modem(timeout = 2, simulate_usim=self.config.usimemu)
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

            (band, descr, uarfcn) = self.cur_test.get_band_desc_uarfcn_tuple()[0]

            # this is in initial rf band
            rfband_init = band
            uarfcn_init = uarfcn
            descr_init = descr

            #for rfband in self.cur_test.rfband:

            self.modemObj.set_preferred_rat(rat="UTRAN")

            logger_test.debug("Selected RF_BAND=%s, DL_UARFCN=%s" % (rfband_init, uarfcn))

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

                                    insertPause(tsec=1, desc= "short pause for cmw init config")

                                    self.cmw.set_rf_band(rfband_init)

                                    self.cmw.set_uarfcn(uarfcn_init)

                                    self.cmw.set_rf_power_dbm(rfpower)

                                    self.cmw.set_hsdpa_modulation(modulation= modulation)

                                    chan_code = self.calc_suitable_hsdsch_code(num_hsdpa_codes)

                                    self.cmw.set_hsdsch_num_codes(numCodes=num_hsdpa_codes)

                                    self.cmw.set_hsdsch_chanelisation_code(code=chan_code, carrier=1)

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

                                    num_hho_steps = self.cur_test.get_total_test_steps()

                                    # ignore the first tuple in the list as this is the same band
                                    for (band, desc, uarfcn_interband_hho)  in self.cur_test.get_band_desc_uarfcn_tuple()[1:]:

                                        teststep_idx += 1

                                        uarfcn_hho_target = uarfcn_interband_hho
                                        rf_band_hho_target = band
                                        desc_hho_target = desc

                                        logger_test.info("Interband HHO - Running step %s of %s..." % (teststep_idx, num_hho_steps))

                                        logger_test.info("data rate =%s" %(data_rate)  +
                                        ",rfpower=%s, SNR=%s" % (rfpower, snr) +
                                        ", modulation=%s, num HSDPA codes=%s, transport block index=%s"
                                        %(modulation, num_hsdpa_codes, tb_index))

                                        if teststep_idx == 1:
                                            uarfcn_hho_source = uarfcn_init
                                            rf_band_source = rfband_init
                                            desc_source = descr_init
                                        else:
                                            uarfcn_hho_source = uarfcn_prev_loop
                                            rf_band_source = rf_band_prev_loop
                                            desc_source = desc_prev_loop

                                        logger_test.info("Starting blind Interband HO from (%s) band %s, UARFCN %s (%s MHz) to target (%s) band %s UARFCN %s (%s MHz)"
                                                          % (desc_source, rf_band_source, uarfcn_hho_source, umts.get_umts_dl_freq(uarfcn_hho_source),
                                                             desc_hho_target, rf_band_hho_target, uarfcn_hho_target, umts.get_umts_dl_freq(uarfcn_hho_target)))

                                        self.cmw.set_rf_band(band=rf_band_hho_target)
                                        self.cmw.set_uarfcn(uarfcn=uarfcn_hho_target, carrier=1)

                                        target_freqMHz = umts.get_umts_dl_freq(uarfcn_hho_target)

                                        self.check_cmw_uarfcn_freqMHz(carrier=1,
                                                                      uarfcn=uarfcn_hho_target,
                                                                      freqMHz=target_freqMHz)

                                        uarfcn_prev_loop = uarfcn_interband_hho
                                        rf_band_prev_loop = band
                                        desc_prev_loop = desc

                                        if self.cmw.readState() != 'CEST' :
                                            msg='CONNECT ESTABLISHMENT FAILURE during INTERBAND HO'
                                            logger_test.error(msg)
                                            self.result = self.code.ERRCODE_TEST_FAILURE_INTERBANDHO if self.result == 0 else ERRCODE_TEST_FAILURE
                                            sys.exit(self.result)
                                        else:
                                            logger_test.info("Blind Interband HO SUCCESSFULL")

                                        if 0:
                                            raw_input("Check instrument and press [ENTER]")

                                        self.start_pwr_meas()

                                        # Get bler measurements
                                        # ========================

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

                                                insertPause(tsec=time_sec, poll_time_sec=2, desc="pausing to give modem time to enter boot loader mode")

                                                sys.exit(self.code.ERRCODE_TEST_FAILURE_CEST)

                                            if ret_val == self.SUCCESS:

                                                verdict_s = self.get_test_verdict(blerPerCentTol=dlblerTol)

                                                if 'PASS' in verdict_s:
                                                    break

                                                else:
                                                    logger_test.info('Bler test failure - tolerance %s' %dlblerTol)
                                                    logger_test.info('Iteration %s of %s' %(retryNum, max_num_retries))


                                            retryNum +=1

                                        if ret_val != self.SUCCESS:
                                            sys.exit(ret_val)

                                        if 'FAIL' in verdict_s:
                                            self.result = self.code.ERRCODE_TEST_FAILURE_BLER if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL

                                        schedtype = self.cur_test.schedtype[0]

                                        uarfcn_hho_str= str(uarfcn_hho_source) + " - " + str(uarfcn_hho_target)
                                        rf_band_hho_str =str(rf_band_source) + " - " + str(rf_band_hho_target)
                                        param_list = [self.testID, rf_band_hho_str, uarfcn_hho_str, self.cur_test.chtype,
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

                                        '''
                                        if not self.intraHO :

                                            self.cmw.dut_disconnect()

                                            self.end_modem_log_capture(proc_id=proc_id)
                                        '''

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
            self.update_database()

            # Create XLS
            # ========================
            csv2Xls(self.csvReportBlerPathName)

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
                    insertPause(tsec=30, desc= "waiting for modem to enter normal mode")
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
