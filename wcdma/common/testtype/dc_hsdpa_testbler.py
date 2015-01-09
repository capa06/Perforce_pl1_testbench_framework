#-------------------------------------------------------------------------------
# Name:        dc_hsdpa_testbler class
# Purpose:
#
# Author:      joashr
#
# Created:     27/01/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time, math
import traceback
from threading import Thread


from pl1_testbench_framework.common.utils.os_utils import insertPause
from pl1_testbench_framework.wcdma.common.config.cfg_conf import cfg_conf
from pl1_testbench_framework.common.config.CfgError import CfgError
from pl1_testbench_framework.wcdma.common.report.csv.CsvReport import CsvReport
from pl1_testbench_framework.wcdma.common.config.cfg_test_dc_hsdpa import cfg_test_dc_hsdpa
import pl1_testbench_framework.wcdma.instr.cmw500 as cmw
import pl1_testbench_framework.common.com.modem as modem
from pl1_testbench_framework.wcdma.common.report.csv.CsvDualCellHsdpaReportBler import CsvDualCellHsdpaReportBler
from pl1_testbench_framework.common.report.xls.csv2Xls import csv2Xls
from pl1_testbench_framework.common.report.html.Csv2Html import Csv2Html
from pl1_testbench_framework.wcdma.common.testtype.hspa_testbler import HspaTestbler


class DualCellHsdpaTestbler(HspaTestbler):

    def __init__ (self, testID="", results_f="", intraHO=0):

        self.config = None

        self.results_f = results_f

        csv_f='WCDMA_CMW500_TestReport_SUMMARY.csv'
        csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h, frmt_msg = csv_frmt_msg)

        self.testID = testID

        self.cur_test = cfg_test_dc_hsdpa(testID)

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

        self.result_msg = 'OK'

        self.intraHO = intraHO

    def get_test_verdict(self, blerPerCentTol=3 ):

        """"
        see if the test is pass or fail
        measured Tput should be within perCent % of dlTputMaxVal
        """

        logger_test=logging.getLogger(__name__ + ' get_test_verdict')

        dlVerdict = "FAIL"
        dlbler_1 = float(self.cmw.get_hsdpa_bler(carrier=1))
        dlbler_2 = float(self.cmw.get_hsdpa_bler(carrier=2))
        blerPerCentTol = float(blerPerCentTol)

        if dlbler_1 <= blerPerCentTol and dlbler_2 <= blerPerCentTol  :

            dlVerdict = "PASS"

        else:

            dlVerdict = "FAIL"

        return dlVerdict

#    def get_dlbler_tol(self, tb_index, numCodes, modulation):
        """
        get the percentage bler tolerance for bler Tput
        """
#        logger_test = logging.getLogger(__name__ + ' get_dlbler_tol')

#        defaultTol = 3

#        perCentTol = defaultTol

#        if str(tb_index) == '62' and str(numCodes) == '15' and str(modulation) == '64-QAM':

#            perCentTol = 10

#            logger_test.info('DL BLER tolerance has been changed from %s to %s' %(defaultTol,perCentTol))

#        elif modulation == '64-QAM':

#            perCentTol = 5

#            logger_test.info('DL BLER tolerance has been changed from %s to %s' %(defaultTol,perCentTol))

#        return perCentTol


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

    def construct_paramStr(self, c1_param, c2_param):
        """
        converts the spreadsheet params into c1_param (c2_param)
        where c1_param is for carrier 1 and c2_param is for carrier 2
        """

        combined_str = str(c1_param) +  ' (' + str(c2_param)  +')'

        return combined_str

    def constructCombinedList(self, list1, list2):
        listZip = zip(list1,list2)
        newList = []
        for (elem1,elem2) in listZip:
            new_elem = self.construct_paramStr(elem1,elem2)
            newList.append(new_elem)

        return newList


    def runTest(self):

        try:

            logger_test = logging.getLogger(__name__ + ' runTest')

            print self.cur_test

            # Open a connection to the CMW500
            # ====================================================
            cmwname = 'cmw500'
            self.cmw = cmw.CmuControl(name=cmwname, ip_addr=self.config.cmwip)
            logger_test.info("Connection to %s @ %s...OK" % (cmwname, self.config.cmwip))

            self.get_cmw_sw_version()

            # switch on power
            self.setup_pwr_meas(Vmax_V=3.8, Imax_A=5)

            self.cmw.Cell_OFF()

            self.modemObj = modem.serialComms(timeout = 2, simulate_usim=self.config.usimemu)
            modeminfo = self.modemObj.getInfo()
            self.cur_test.set_modeminfo(modeminfo=modeminfo)

            # initialise cvs report bler, must be done here to extract modeminfo
            self.csvReportBler=CsvDualCellHsdpaReportBler(test_s = self.cur_test, test_conf=self.config,
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

            # hard code configuration for max Tput
            #self.cmw.max_hspa_tputConfig(modulation='64-QAM', numHsdschCodes=15, ki = 62,
            #                             hsupa_cat=6, tti_ms = 10)

            data_rate = self.cur_test.datarate[0]

            snr_zip = zip(self.cur_test.snr_1, self.cur_test.snr_2) # currently not used
            rfpower_zip =  zip(self.cur_test.rfpower_1, self.cur_test.rfpower_2)
            inter_tti_zip = zip(self.cur_test.inter_tti_1, self.cur_test.inter_tti_2)
            ki_zip = zip(self.cur_test.ki_1, self.cur_test.ki_2)
            num_hsdcsh_codes_zip = zip(self.cur_test.num_hsdsch_codes_1, self.cur_test.num_hsdsch_codes_2)
            modulation_zip =zip(self.cur_test.modulation_1, self.cur_test.modulation_2)

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

                    for (rfpower_1, rfpower_2) in rfpower_zip:

                        for txants in self.cur_test.txants:

                            for (snr_1, snr_2) in snr_zip:

                                for (modulation_1, modulation_2) in modulation_zip:

                                    for (num_hsdpa_codes_1, num_hsdpa_codes_2) in num_hsdcsh_codes_zip:

                                        for (tb_index_1, tb_index_2) in ki_zip:

                                            logger_test.info("Resetting CMW500")

                                            self.cmw.reset()

                                            self.cmw.max_hspa_tputConfig(modulation='64-QAM', numHsdschCodes=15, ki = 62,
                                                                         hsupa_cat=6, tti_ms = 10, dc_hsdpa=1)

                                            insertPause(tsec=1, desc= "short pause for cmw init config")

                                            self.cmw.set_rf_band(rfband)

                                            self.cmw.set_uarfcn(uarfcn)

                                            self.cmw.set_rf_power_dbm(power=rfpower_1, carrier=1)
                                            self.cmw.set_rf_power_dbm(power=rfpower_2, carrier=2)

                                            self.cmw.set_hsdpa_modulation(carrier=1, modulation=modulation_1)
                                            self.cmw.set_hsdpa_modulation(carrier=2, modulation=modulation_2)

                                            chan_code_1 = self.calc_suitable_hsdsch_code(num_hsdpa_codes_1)
                                            self.cmw.set_hsdsch_num_codes(numCodes=num_hsdpa_codes_1)
                                            self.cmw.set_hsdsch_chanelisation_code(code=chan_code_1, carrier=1)

                                            chan_code_2 = self.calc_suitable_hsdsch_code(num_hsdpa_codes_2)
                                            self.cmw.set_hsdsch_num_codes(numCodes=num_hsdpa_codes_2)
                                            self.cmw.set_hsdsch_chanelisation_code(code=chan_code_2, carrier=2)

                                            if num_hsdpa_codes_1 == 1:

                                                self.cmw.set_hsdsch_level(carrier=1, leveldB=-4)

                                            else:

                                                self.cmw.set_hsdsch_level(carrier=1, leveldB=-1)

                                            if num_hsdpa_codes_2 == 2:

                                                self.cmw.set_hsdsch_level(carrier=2, leveldB=-4)

                                            else:

                                                self.cmw.set_hsdsch_level(carrier=2, leveldB=-1)

                                            self.cmw.set_hsdpa_tbi(carrier=1, ki=tb_index_1)
                                            self.cmw.set_hsdpa_tbi(carrier=2, ki=tb_index_2)

                                            self.cmw.Cell_OFF()

                                            # radio off
                                            self.disable_modem_fun()

                                            # ENABLE LOG
                                            # ====================================================
                                            modemLogBaseName=""
                                            modemLogBaseName='WCDMA_CMW500_test_id_%s_modem_tbi_%s_%s_mod_%s_%s_numCodes_%s_%s' %(self.testID,
                                                                                                                                  tb_index_1, tb_index_2,
                                                                                                                                  modulation_1, modulation_2,
                                                                                                                                  num_hsdpa_codes_1, num_hsdpa_codes_2)
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

                                            uarfcn_prev_loop = uarfcn

                                            for uarfcn_intraho in uarfcn_intraho_l :

                                                teststep_idx += 1

                                                uarfcn_hho_target = uarfcn_intraho

                                                if self.intraHO :

                                                    logger_test.info("Intra HHO - Running step %s of %s..." % (teststep_idx, num_hho_steps))

                                                    logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                                    ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn_hho_target, rfpower_1, snr_1) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s for carrier 1"
                                                    %(modulation_1, num_hsdpa_codes_1, tb_index_1))

                                                    if teststep_idx == 1:
                                                        uarfcn_hho_source = uarfcn
                                                    else:
                                                        uarfcn_hho_source = uarfcn_prev_loop

                                                    logger_test.info("data rate =%s, band=%s," %(data_rate, rfband)  +
                                                    " rfpower=%s, SNR=%s" % (rfpower_2, snr_2) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s for carrier 2"
                                                    %(modulation_2, num_hsdpa_codes_2, tb_index_2))

                                                    logger_test.info("Starting blind HO from UARFCN %s (%s MHz) to target UARFCN %s (%s MHz)"
                                                                      % (uarfcn_hho_source, get_umts_dl_freq(uarfcn_hho_source),
                                                                         uarfcn_hho_target, get_umts_dl_freq(uarfcn_hho_target)))

                                                    self.cmw.set_uarfcn(uarfcn=uarfcn_intraho, carrier=1)

                                                    uarfcn_1 = self.cmw.get_uarfcn(carrier=1)
                                                    dl_freq_1 = self.cmw.get_freq_Hz(carrier=1)
                                                    dl_freq_1_MHz = float(dl_freq_1)/1000000

                                                    uarfcn_2 = self.cmw.get_uarfcn(carrier=2)
                                                    dl_freq_2 = self.cmw.get_freq_Hz(carrier=2)
                                                    dl_freq_2_MHz = float(dl_freq_2)/1000000

                                                    logger_test.info('cmw changed to UARFCN=%d, Freq=%.1f for carrier 1' %(int(uarfcn_1), dl_freq_1_MHz))
                                                    logger_test.info('cmw changed to UARFCN=%d, Freq=%.1f for carrier 2' %(int(uarfcn_2), dl_freq_2_MHz))

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

                                                    logger_test.info("Running step %s of %s for carrier 1..." % (teststep_idx, self.cur_test.get_total_test_steps()))
                                                    logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                                    ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn, rfpower_1, snr_1) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s for carrier 1"
                                                    %(modulation_1, num_hsdpa_codes_1, tb_index_1))

                                                    uarfcn_2 = self.cmw.get_uarfcn(carrier=2)
                                                    logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                                    ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn_2, rfpower_2, snr_2) +
                                                    ", modulation=%s, num HSDPA codes=%s, transport block index=%s for carrier 2"
                                                    %(modulation_2, num_hsdpa_codes_2, tb_index_2))


                                                self.start_pwr_meas()

                                                # Get bler measurements
                                                # ========================
                                                # note that 2 iterations  to cater for delay caused
                                                # by adaptive wireless switching. This can account
                                                # for high bler on the first iteration

                                                # dynamic bler tolerance
                                                dlblerTol = self.get_dlbler_tol(tb_index=tb_index_1,
                                                                                numCodes=num_hsdpa_codes_1,
                                                                                modulation=modulation_1)

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

                                                        insertPause(tsec=time_sec, desc="pausing to give modem time to enter boot loader mode")

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

                                                if self.intraHO:
                                                    uarfcn_hho_str= str(uarfcn_hho_source) + " - " + str(uarfcn_hho_target)
                                                    param_list = [self.testID, rfband, uarfcn_hho_str, self.cur_test.chtype,
                                                                  data_rate, snr_1, rfpower_1, txants, schedtype,
                                                                  modulation_1, tb_index_1, num_hsdpa_codes_1,
                                                                  snr_2, rfpower_2, modulation_2, tb_index_2, num_hsdpa_codes_2]

                                                else:
                                                    param_list = [self.testID, rfband, uarfcn, self.cur_test.chtype,
                                                                  data_rate, snr_1, rfpower_1, txants, schedtype,
                                                                  modulation_1, tb_index_1, num_hsdpa_codes_1,
                                                                  snr_2, rfpower_2, modulation_2, tb_index_2, num_hsdpa_codes_2]

                                                carrier1=0
                                                carrier2=1

                                                meas_list = [self.cmw.get_hsdpa_measured_subframes(),
                                                             self.cmw.hsdpa_meas[carrier1].get_maxTputMbps(),
                                                             self.cmw.hsdpa_meas[carrier1].get_avgTputMbps(),
                                                             self.cmw.get_hsdpa_bler(carrier=1),
                                                             dlblerTol,
                                                             self.cmw.get_medianCqi(carrier=1)]


                                                first_tx = 0

                                                meas_list = meas_list + self.cmw.trans_meas_1[first_tx].get_list()

                                                meas_list = meas_list + [self.cmw.hsdpa_meas[carrier2].get_maxTputMbps(),self.cmw.hsdpa_meas[carrier2].get_avgTputMbps(),
                                                             self.cmw.get_hsdpa_bler(carrier=2), self.cmw.get_medianCqi(carrier=2)]

                                                meas_list = meas_list + self.cmw.trans_meas_2[first_tx].get_list();

                                                # Add power measurements
                                                # ========================
                                                pwr_s = self.get_pwr_meas()

                                                # Update CSV report
                                                # ========================
                                                msg_s = param_list + meas_list + [verdict_s]

                                                if self.config.pwrmeas:
                                                    msg_s = msg_s + pwr_s

                                                self.csvReportBler.append(msg_s)

                                                if not self.intraHO:

                                                    self.cmw.dut_disconnect()

                                                    self.end_modem_log_capture(proc_id=proc_id)

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
                self.cmw.write("ABORt:WCDMa:SIGN:BER")
                self.close_conn_cmw()

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