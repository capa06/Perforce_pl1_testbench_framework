#-------------------------------------------------------------------------------
# Name:        hspa_fading perf class
# Purpose:     HSDPA fading performance test class.
#
# Author:      joashr
#
# Created:     17/07/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, time, traceback, logging, math, re

from pl1_testbench_framework.common.utils.os_utils import insertPause
from pl1_testbench_framework.wcdma.common.config.cfg_conf import cfg_conf
from pl1_testbench_framework.wcdma.common.report.csv.CsvReport import CsvReport
from pl1_testbench_framework.wcdma.common.config.cfg_test_fading_hspa import cfg_test_fading_hspa
import pl1_testbench_framework.wcdma.instr.cmw500 as cmw
import pl1_testbench_framework.common.com.modem as modem
from pl1_testbench_framework.wcdma.common.report.csv.CsvHspaFadingReportBler import CsvHspaFadingReportBler
from pl1_testbench_framework.common.report.xls.csv2Xls import csv2Xls
from pl1_testbench_framework.common.report.html.Csv2Html import Csv2Html

import pl1_testbench_framework.wcdma.common.report.sqllite.perf_bestscore_db as sqlite_db
import pl1_testbench_framework.wcdma.common.report.mysql.perf_bestscore_mySQLdb as mysql_db


from testbler import Testbler

class HspaFadingTestbler(Testbler):

    def __init__ (self, testID="", results_f=""):

        self.config = None

        self.results_f = results_f

        csv_f='WCDMA_CMW500_TestReport_SUMMARY.csv'
        csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h, frmt_msg = csv_frmt_msg)

        self.testID = testID

        self.cur_test = cfg_test_fading_hspa(testID)

        self.start_time=time.localtime()

        self.cvsReportBler = None

        self.csvReportBlerPathName = ""

        self.psu_bench=None

        self.dmm=None

        self.cmw=None

        self.modemObj = None

        self.thr_pwr=None # daemon thread for power measurements

        self.num_hsdpa_subframes=50000

        self.result = 0

        self.result_msg= 'OK'

        self.jenkins_regression = 0

    def set_jenkins_regression(self, regression=1):

        self.jenkins_regression = regression

    def get_jenkins_regression(self):

        return self.jenkins_regression

    def get_ref_percentage(self, refthput, testthput):

        logger_test=logging.getLogger(__name__ + ' get_ref_percentage')

        percent = 0

        if refthput == 0:
            logger_test.info("Provided Reference Throughput is 0.")
            return percent

        percent = (float(testthput) * 100 / float(refthput))
        percent = '%.2f' % float(percent)
        percent = float(percent)

        logger_test.info("Reference Thput  %s Mbps, Test thput %s Mbps, Percentage of Ref %s." % (refthput, testthput, percent))

        return percent


    def get_test_verdict(self, ref_thput, thputPerCentTol=5 ):

        """"
        see if the test is pass or fail
        measured Tput should be more than (-ve)% thputPerCentTol of best score throughput achieved so far for same set of parameters
        """
        logger_test=logging.getLogger(__name__ + ' get_test_verdict')

        if ref_thput == 0:
            logger_test.info("Provided Reference Throughput is %s, Verdict is forced as PASS." %ref_thput)
            return "PASS"


        dlVerdict = "FAIL"
        test_thput = float(self.cmw.hsdpa_meas[0].get_avgTputMbps())
        thputPerCentTol = float(thputPerCentTol)
        percent_ref = self.get_ref_percentage(ref_thput, test_thput)


        logger_test.info("checking that DL Throughput is within %s percent of lower Tol, of best score recorded." %thputPerCentTol)

        if percent_ref < (100 - thputPerCentTol):

            dlVerdict = "FAIL"

        else:

            dlVerdict = "PASS"

        return dlVerdict

    def get_dlthput_tol(self):
        """
        get the percentage bler tolerance for bler Tput
        """
        logger_test = logging.getLogger(__name__ + ' get_dlthput_tol')

        defaultTol = 8

        perCentTol = defaultTol

        return perCentTol

    def get_and_display_instr_meas(self, max_num_retries=1, numSubframes=2000):

        retryNum = 0
        ret_val = self.SUCCESS
        while retryNum < max_num_retries:
            if self.cmw.get_hsdpa_ack_meas(numSubframes=numSubframes, testType=self.cur_test.testtype):
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

    def change_rf_band_list(self, rfbandList):
        import datetime
        datetime=datetime.datetime.today()
        # note Monday is 0, Tuesday is 1, Sunday is 6
        dayInteger = int(datetime.weekday())

        listIndex = dayInteger % (len(rfbandList))
        singleBandUnderTest = rfbandList[listIndex]
        singleBandList = [singleBandUnderTest]
        return singleBandList

    def runTest(self):

        try:

            logger_test = logging.getLogger(__name__ + ' runTest')

            if not self.get_jenkins_regression():

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

            if self.get_jenkins_regression():

                newrfbandList = self.change_rf_band_list(rfbandList=self.cur_test.rfband)

                self.cur_test.set_rf_band_list(bandList=newrfbandList)

                new_uarfcn_dict = self.cur_test.get_dict_from_uarfcn_dict(rfbandList=newrfbandList)

                self.cur_test.set_uarcn_dict(uarfcn_dict=new_uarfcn_dict)

                print self.cur_test

            # initialise cvs report bler, must be done here to extract modeminfo
            self.csvReportBler=CsvHspaFadingReportBler(test_s = self.cur_test, test_conf=self.config,
                                                 csv_fname=self.csvReportBlerPathName,
                                                 pwrmeas=self.config.pwrmeas)
            # Initialise database
            # ====================================================
            if self.config.remoteDB:
                access = mysql_db.DB_mySQL_CheckPermission(host=self.config.remoteDBhost,
                                                 dbname=self.config.remoteDBname,
                                                 uid=self.config.remoteDBuid,
                                                 pwd=self.config.remoteDBpwd)
                if access == "READ_WRITE":
                    db_write_access = 1
                elif access == None:
                    db_write_access = 0
                    remoteDB        = 0

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

                    for chtype in self.cur_test.chtype:

                        for rfpower in self.cur_test.rfpower:

                            for txants in self.cur_test.txants:

                                for cpich_power in self.cur_test.cpich_power:

                                    for hspdsch_power in self.cur_test.hs_pdsch_power:

                                        logger_test.info("Resetting CMW500")
                                        self.cmw.reset()
                                        self.cmw.wait_for_completion()

                                        self.cmw.hsdpa_fading_test_init_config(cpich_power, hspdsch_power, chtype)

                                        insertPause(tsec=1, desc= "short pause for cmw init config")

                                        self.cmw.set_rf_band(rfband)

                                        self.cmw.set_uarfcn(uarfcn)

                                        # Set Ior
                                        self.cmw.set_rf_power_dbm(rfpower)

                                        self.cmw.Cell_OFF()

                                        # radio off
                                        self.disable_modem_fun()

                                        # ENABLE LOG
                                        # ====================================================
                                        modemLogBaseName=""
                                        modemLogBaseName='WCDMA_CMW500_test_id_%s_modem_chtype_%s_cpich_%s_hspdsch_%s' %(self.testID,
                                                                                                                     chtype,
                                                                                                                     cpich_power,
                                                                                                                     hspdsch_power)

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


                                        time_sec = 6
                                        insertPause(tsec=time_sec, desc="pausing before DUT Connect")


                                        # DUT CONNECT
                                        # =========================================================
                                        if not self.cmw.dut_connect():
                                            if not self.cmw.dut_connect(): # Try one more time to connect.
                                                logger_test.debug("DUT CONNECT FAILURE: Skipping DL BLER test")
                                                self.result = self.code.ERRCODE_TEST_FAILURE_CEST if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL
                                                sys.exit(self.result)
                                        Tf=time.time()

                                        logger_test.debug("DUT CONNECTION PROCEDURE: T0=%d, Tf=%d, Tf-T0[sec]=%d" % (T0, Tf, math.floor(Tf-T0)))

                                        for snr in self.cur_test.snr:

                                            teststep_idx += 1

                                            # Set Channel Type and SNR level
                                            noise_level = rfpower - snr;
                                            self.cmw.reconfig_internal_fading(chtype, noise_level)

                                            print("Running step %s of %s..." % (teststep_idx, self.cur_test.get_total_test_steps()))
                                            logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                            ", uarfcn=%s, rfpower=%s" % (uarfcn, rfpower) +
                                            ", CPICH Power=%s dB, HS-PDSCH Power=%s dB, Channel Type=%s, SNR = %s dB"
                                            %(cpich_power, hspdsch_power, chtype, snr))

                                            self.start_pwr_meas()

                                            schedtype = self.cur_test.schedtype[0]
                                            param_list = [self.testID, rfband, uarfcn, chtype,
                                                          data_rate, snr, rfpower, txants, schedtype, cpich_power,
                                                          hspdsch_power]

                                            # Get Reference and Best scores
                                            # ========================
                                            dlthr_ref       = [None, None, None]
                                            dlth_bestscore  = [None, None, None]
                                            if self.config.remoteDB:
                                                dlthr_ref, dlth_bestscore = mysql_db.DB_mySQL_wcdma_hspa_fading_SelectBestScore(host=self.config.remoteDBhost,
                                                                                                                                dbname=self.config.remoteDBname,
                                                                                                                                uid=self.config.remoteDBuid,
                                                                                                                                pwd=self.config.remoteDBpwd,
                                                                                                                                modeminfo=self.cur_test.modeminfo,
                                                                                                                                testparams=param_list)


                                            if (dlthr_ref[2] is None):
                                                logging.info("THROUGHPUT REFERENCE RESULTS NOT FOUND.")
                                                ref_dlthr=0
                                            else:
                                                ref_dlthr= float('%.6f' % dlthr_ref[2])
                                                logging.info("DL THR REFERENCE: '%s', CL%s, %s[Mbps]" % (dlthr_ref[0], dlthr_ref[1], ref_dlthr))

                                            if (dlth_bestscore[2] is None):
                                                logging.info("THROUGHPUT BEST SCORE RESULTS NOT FOUND.")
                                                bestscore_dlthr=0
                                            else:
                                                bestscore_dlthr= float('%.6f' % dlth_bestscore[2])
                                                logging.info("DL THR BEST SCORE: '%s', CL%s, %s[Mbps]" % (dlth_bestscore[0], dlth_bestscore[1], bestscore_dlthr))

                                            # dynamic bler tolerance
                                            dlthputTol = self.get_dlthput_tol()

                                            max_num_retries=1

                                            retryNum = 1

                                            while retryNum < (max_num_retries+1):

                                                try:

                                                    ret_val = self.get_and_display_instr_meas(max_num_retries=3, numSubframes=self.num_hsdpa_subframes)

                                                except ValueError:

                                                    print traceback.format_exc()

                                                    if self.get_modemLogProcessRunning() == True:

                                                        self.end_modem_log_capture(proc_id=proc_id)

                                                    time_sec = 20

                                                    insertPause(tsec=time_sec, desc="pausing to give modem time to enter boot loader mode")

                                                    sys.exit(self.code.ERRCODE_TEST_FAILURE_CEST)

                                                if ret_val == self.SUCCESS:

                                                    verdict_s = self.get_test_verdict(bestscore_dlthr, thputPerCentTol=dlthputTol)

                                                    if 'PASS' in verdict_s:
                                                        break

                                                    else:
                                                        logger_test.info('Bler test failure - tolerance %s' %dlthputTol)
                                                        logger_test.info('Iteration %s of %s' %(retryNum, max_num_retries))


                                                retryNum +=1

                                            if ret_val != self.SUCCESS:
                                                sys.exit(ret_val)

                                            if 'FAIL' in verdict_s:
                                                self.result = self.code.ERRCODE_TEST_FAILURE_BLER if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL

                                            carrier1=0
                                            test_thput = self.cmw.hsdpa_meas[carrier1].get_avgTputMbps();

                                            meas_list = [self.cmw.get_hsdpa_measured_subframes(), ref_dlthr, bestscore_dlthr, test_thput,
                                                         self.get_ref_percentage(ref_dlthr, test_thput), self.get_ref_percentage(bestscore_dlthr, test_thput), self.cmw.get_hsdpa_bler(carrier=1), dlthputTol, self.cmw.get_medianCqi(carrier=1)]
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


                                        # TURN OFF MEASUREMENTS
                                        # ========================
                                        self.cmw.abort_hsdpa_ack_meas()
                                        self.cmw.wait_for_completion()


                                        self.cmw.dut_disconnect()

                                        # DUT DETACH
                                        # ========================
                                        self.cmw.dut_detach()
                                        self.cmw.wait_for_completion()

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


            # end of outer for loop
            # Close CMW instances
            if self.cmw:
                self.close_conn_cmw()

            self.close_pwr_meas()

            # Close COM ports
            self.modemObj.close()

            # UPDATE DATABASE
            # ==========================
            if self.config.remoteDB and db_write_access:
                mysql_db.DB_mySQL_wcdma_import_from_file_meas(filename=self.csvReportBlerPathName,
                                                              testType=self.cur_test.testtype,
                                                              host=self.config.remoteDBhost,
                                                              dbname=self.config.remoteDBname,
                                                              uid=self.config.remoteDBuid,
                                                              pwd=self.config.remoteDBpwd,
                                                              config_pwr_meas=self.config.pwrmeas)

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
