#-------------------------------------------------------------------------------
# Name:        testbler class
# Purpose:
#
# Author:      joashr
#
# Created:     17/12/2013
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time, math, traceback
import shlex
from threading import Thread
from multiprocessing import Process, Lock


try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    print test_env_dir
    sys.path.append(test_env_dir)
    import test_env



from pl1_testbench_framework.common.utils.os_utils import insertPause
from pl1_testbench_framework.wcdma.common.config.cfg_conf import cfg_conf
from pl1_testbench_framework.common.config.CfgError import CfgError
from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging
from pl1_testbench_framework.wcdma.common.report.csv.CsvReport import CsvReport
from pl1_testbench_framework.wcdma.common.config.cfg_test import cfg_test
import pl1_testbench_framework.wcdma.instr.cmw500 as cmw
import pl1_testbench_framework.common.com.modem as modem
from pl1_testbench_framework.wcdma.instr.Agilent_E3631A_Psu import Psu
import pl1_testbench_framework.common.instr.dmm as dmm
from pl1_testbench_framework.wcdma.common.report.csv.CsvReportBler import CsvReportBler
from pl1_testbench_framework.common.report.xls.csv2Xls import csv2Xls
from pl1_testbench_framework.common.report.html.Csv2Html import Csv2Html
from pl1_testbench_framework.common.com.Serial_ComPortDet import poll_for_port, auto_detect_port
from pl1_testbench_framework.wcdma.common.classes.RunCmd import RunCmd
import pl1_testbench_framework.wcdma.common.report.sqllite.perf_bestscore_db as sqlite_db
import pl1_testbench_framework.wcdma.common.report.mysql.perf_bestscore_mySQLdb as mysql_db
import pl1_testbench_framework.wcdma.common.config.umts_utilities as umts_util


class Testbler(object):

    SUCCESS = 0
    FAIL = 1

    ENABLE_DMM = 0
    code = CfgError()

    # Icera logs
    log_iom_f = ""
    log_db_f  = ""
    log_glp_f = ""
    log_dec_f = ""

    # Icera logging commands
    geanielog_cmd_iom = ""
    geanielog_cmd_db  = ""
    geanielog_cmd_glp = ""
    geanielog_cmd_dec = ""

    modemLogProcessRunning = False # indicates if the log process is running
    modemLogProcId = -1

    dflt_database=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'common', 'report', 'sqllite', 'database', 'perf_bestscore.db'])

    def __init__ (self, testID="", results_f="", intraHO=0):

        self.config = None

        self.results_f = results_f

        csv_f='WCDMA_CMW500_TestReport_SUMMARY.csv'
        csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])
        csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
        csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'
        self.csvSummaryReport = CsvReport(fname=csv_abs_f, frmt_header=csv_frmt_h, frmt_msg = csv_frmt_msg)

        self.testID = testID

        self.cur_test = cfg_test(testID)

        self.start_time=time.localtime()

        self.cvsReportBler = None

        self.csvReportBlerPathName = ""

        self.psu_bench=None

        self.dmm=None

        self.cmw=None

        self.modemObj = None

        self.thr_pwr=None # daemon thread for power measurements

        self.result= 0

        self.result_msg = 'OK'

        self.intraHO = intraHO

        #self.csvJenkinsVerdict=CsvJenkinsVerdict()


    def set_test_config(self, log = 'info', cmwip ='10.21.141.148',ctrlif = 'AT',
                         test2execute='[0]', pwrmeas=0, usimemu=0,
                         psugwip='10.21.141.175', psugpib=6, msglog=0, database=None, remoteDB = 0,
                         remoteDBhost = None, remoteDBuid = None,
                         remoteDBpwd = None, remoteDBname = None):

        self.config=cfg_conf(loglevel=log, cmwip=cmwip, ctrlif=ctrlif,
                             test2execute=test2execute, pwrmeas=pwrmeas,
                             usimemu=usimemu, psugwip=psugwip, psugpib=psugpib,
                             msglog=msglog, database=database,remoteDB = remoteDB,
                             remoteDBhost = remoteDBhost, remoteDBuid = remoteDBuid,
                             remoteDBpwd = remoteDBpwd, remoteDBname = remoteDBname)

        print self.config

        csv_f='WCDMA_CMW500_TestReport_testID_%s_testType_%s.csv' % (self.cur_test.testID, self.cur_test.testtype)
        csv_abs_f = csv_abs_f= os.sep.join(self.results_f.split(os.sep)[:]+[csv_f])

        self.csvReportBlerPathName = csv_abs_f


    def __str__(self):
        print "---------------------------------------------------------------------"
        print self.config
        print self.csvSummaryReport
        print "  bler report filename      :     %s"     %self.csvReportBlerPathName
        print "  summary report            :     %s"     %self.csvSummaryReport
        print "  cvs report bler filename  :     %s"     %self.csvReportBlerPathName
        self.results_f = results_f
        print "  results folder            :     %s"     %self.results_f
        print "---------------------------------------------------------------------"
        return ""

    def setUp(self):
        """
            It allows to start the testbench as a function. For instance:
            res=runme(log='DEBUG', cmwip='10.21.141.154',ctrlif='AT', test2execute='[0]',
                      pwrmeas=0, usimemu=0, psu=1, psugwip='10.21.141.174', psugpib=5)
        """

        res = self.code.ERRCODE_TEST_FAILURE_GENERAL

        logger_test=logging.getLogger('testbler')

        logger_test.info("-----------------------------------------------")
        logger_test.info("Testing with the following configuration:      ")
        logger_test.info("-----------------------------------------------")
        logger_test.info("      loglevel : %s" % self.config.loglevel)
        logger_test.info("       cmwname : %s" % self.config.cmwname)
        logger_test.info("         cmwip : %s" % self.config.cmwip)
        logger_test.info("        ctrlif : %s" % self.config.ctrlif)
        logger_test.info("  test2execute : %s" % self.config.test2execute)
        logger_test.info("       pwrmeas : %s" % self.config.pwrmeas)
        logger_test.info("       usimemu : %s" % self.config.usimemu)
        logger_test.info("       psugwip : %s" % self.config.psugwip)
        logger_test.info("       psugpip : %s" % self.config.psugpib)
        logger_test.info("       msglog  : %s" % self.config.msglog)
        logger_test.info("      database : %s" % self.config.database)
        logger_test.info("      remoteDB : %s" % self.config.remoteDB)
        logger_test.info("  remoteDBhost : %s" % self.config.remoteDBhost)
        logger_test.info("   remoteDBuid : %s" % self.config.remoteDBuid)
        logger_test.info("  remoteDBname : %s" % self.config.remoteDBname)
        logger_test.info("-----------------------------------------------")

        return

    def update_summary_report(self, return_state, verdict_str):

        end_time=time.localtime()
        start_time_frmt=time.strftime("%Y/%m/%d %H:%M:%S", self.start_time)
        end_time_frmt=time.strftime("%Y/%m/%d %H:%M:%S", end_time)
        duration=time.mktime(end_time)-time.mktime(self.start_time)

        self.csvSummaryReport.append ([self.testID, verdict_str, return_state,
                                       self.code.MSG[return_state], start_time_frmt, end_time_frmt,
                                       duration])


    def setup_pwr_meas(self, Vmax_V=3.8, Imax_A=5):
        if self.config.pwrmeas:
            logger_test = logging.getLogger(__name__ + ' setup_pwr_meas')
            psu_name='E3631A_0'
            # do not reset or configure the power supply current and voltage
            self.psu_bench=Psu(psu_name=psu_name,
                               psu_gwip=self.config.psugwip,
                               psu_gpib=self.config.psugpib,
                               psu_channel='P6V',
                               psu_config=0,
                               psu_reset=0)
            self.psu_bench.set_max_volts_amps(v_max= Vmax_V, i_max=Imax_A)
            output_state=0
            output_state = self.psu_bench.read_output_state()
            if output_state == 1:
                print "Power supply is switched on"
                print "Check that the supply voltage is at the correct level of %s volts" %Vmax_V
                if self.psu_bench.check_voltage_output(check_volts = Vmax_V):
                    #output_state = 1
                    print "Power supply is at the correct voltage"
                    if poll_for_port(portName="Modem_port", timeout_sec=20, poll_time_sec=1):
                        print "modem com port successfully found"
                    else:
                        print "modem com port not found"
                        sys.exit(self.code.ERRCODE_SYS_MODEM_NO_COM)
                else:
                    print "PSU voltage is not at the required level"
                    output_state = 0
            else:
                print "Power supply is currently switched off"
                output_state = 0

            if output_state == 0:
                #self.psu_bench.reset()
                self.psu_bench._reset()
                self.psu_bench.on()
                time.sleep(1)
                #self.psu_bench.set_max_volts_amps(v_max= Vmax_V, i_max=Imax_A)
                #self.psu_bench.set(channel='P6V', voltage=Vmax_V, current=Imax_A)
                self.psu_bench._set(channel='P6V',
                                    voltage=self.psu_bench.get_max_volts(),
                                    current=self.psu_bench.get_max_amps())
                #self.psu_bench._set(channel='P6V', voltage=Vmax_V, current=Imax_A)

                #reading=self.psu_bench.read('P6V')
                reading=self.psu_bench.read()
                logger_test.info("PSU bench configuration: Vmax[V]=%s, Imax[A]=%s, read back Voltage=%s" % (Vmax_V, Imax_A, reading))

                if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

                    print "modem com port successfully found"

                    time_secs = 5
                    txt = "pausing for %s secs ..." %time_secs
                    insertPause(tsec=time_secs, desc=txt)

                else:

                    print "modem com port not found after power cycle"

                    sys.exit(self.code.ERRCODE_SYS_MODEM_NO_COM)


            #reading=self.psu_bench.read('P6V')
            reading=self.psu_bench.read()
            logger_test.info("PSU bench configuration: Vmax[V]=%s, Imax[A]=%s, read back Voltage=%s" % (Vmax_V, Imax_A, reading))

            if self.ENABLE_DMM:
                #Digital Multimeter
                self.dmm = DmmControl('34401a-0')
                self.dmm.config('DC_I')
                self.dmm.read_config('DC_I')



    def start_pwr_meas(self):

        if self.config.pwrmeas:

            logger_test = logging.getLogger(__name__ + ' start_pwr_meas')

            if self.ENABLE_DMM:
                logger_test.debug("Starting DMM thread for power measurements")
                self.thr_pwr=Thread(target=self.dmm.meas_fetch, args=('DC_I',))
            else:
                logger_test.debug("Starting PSU thread for power measurements")
                #self.thr_pwr=Thread(target=self.psu_bench.read, args=('P6V',))
                self.thr_pwr=Thread(target=self.psu_bench.read)

            self.thr_pwr.setDaemon(True)
            self.thr_pwr.start() # spawn thread as daemon

    def get_pwr_meas(self):

        if self.config.pwrmeas:

            logger_test = logging.getLogger(__name__ + ' get_pwr_meas')

            pwr_s= [ (-1) for j in range(len(self.csvReportBler.pwr_meas))]


            self.thr_pwr.join()  # wait for thread exits

            if self.ENABLE_DMM:
                Imin_mA    = abs(self.dmm.currdc_min)*1000
                Iavrg_mA   = abs(self.dmm.currdc_avrg)*1000
                Imax_mA    = abs(self.dmm.currdc_max)*1000
                I_dev      = (100*self.dmm.currdc_dev)
                Voltage_V = self.psu_bench.get_max_volts()
                Pmin_mW    = Voltage_V*Imin_mA
                Pavrg_mW   = Voltage_V*Iavrg_mA
                Pmax_mW    = Voltage_V*Imax_mA
                logger_test.info("DMM measurements: Imin[mA]=%s, Imax[mA]=%s, Iavrg[mA]=%s, Ideviation=%s)" % (Imin_mA, Iavrg_mA, Imax_mA, I_dev))
                logger_test.info("DMM measurements: Pmin[mW]=%s, Pmax[mW]=%s, Pavrg[mW]=%s)" % (Pmin_mW, Pavrg_mW, Pmax_mW))
            else:
                Imin_mA    = self.psu_bench.current_mA
                Iavrg_mA   = self.psu_bench.current_mA
                Imax_mA    = self.psu_bench.current_mA
                I_dev      = 0
                Voltage_V=self.psu_bench.get_max_volts()
                Pmin_mW    = Voltage_V*Imin_mA
                Pavrg_mW   = Voltage_V*Iavrg_mA
                Pmax_mW    = Voltage_V*Imax_mA
                logger_test.info("PSU measurements: Imin[mA]=%s, Imax[mA]=%s, Iavrg[mA]=%s, Ideviation=%s)" % (Imin_mA, Imax_mA, Iavrg_mA, I_dev))
                logger_test.info("PSU measurements: Pmin[mW]=%s, Pmax[mW]=%s, Pavrg[mW]=%s)" % (Pmin_mW,Pmax_mW, Pavrg_mW))

            pwr_s[0]='%.4f'   % Imin_mA
            pwr_s[1]='%.4f'   % Iavrg_mA
            pwr_s[2]='%.4f'   % Imax_mA
            pwr_s[3]='%.4f%%' % I_dev
            pwr_s[4]='%.4f'   % Pmin_mW
            pwr_s[5]='%.4f'   % Pavrg_mW
            pwr_s[6]='%.4f'   % Pmax_mW

            return pwr_s

    def close_pwr_meas(self):
        """
        turn off power supply and close connections to psu and dmm
        """
        if self.config.pwrmeas:
            if self.psu_bench:
                #self.psu_bench.off()
                self.psu_bench.close()
                self.psu_bench=None

            if self.ENABLE_DMM:
                self.dmm.close()

    def close_conn_cmw(self):
        self.cmw.Cell_OFF()
        self.cmw.gotolocal()
        self.cmw.close()


    def disable_modem_fun(self):
        try:
            report = self.modemObj.funcOff()
            self._check_response(response=report)
        except Exception:
            print traceback.format_exc()
            #cf.pause(duration_s=60, poll_time_sec=2, desc= "waiting for coredump information to beconme available")
            insertPause(tsec=60, desc= "waiting for coredump information to beconme available")
            sys.exit(self.code.ERRCODE_SYS_SERIAL_CONN)


    def _check_response(self, response):
        # get return code from report
        # if non zero then something has gone wrong
        logger_test = logging.getLogger(__name__ + 'check_response')
        compileObj = re.compile(r'(.*)CODE(\s*)=(\s*)(?P<num>[+-]?\d+)(\s*)(.*)')
        matchObj = compileObj.match(response)
        # check return code from report
        if matchObj:
            # convert return to number
            num =  int(matchObj.group('num'))
            if num != 0:
                logger_test.info(response)
                logger_test.info("Erroneous response detected from modem")
                #cf.pause(duration_s=60, poll_time_sec=2, desc= "waiting for coredump information to beconme available")
                insertPause(tsec=60, desc= "waiting for coredump information to beconme available")
                sys.exit(self.code.ERRCODE_SYS_SERIAL_CONN)


    def capture_core_dump(self):

        logger_test = logging.getLogger(__name__ + ' capture_core_dump')
        if self.modemObj:
            self.modemObj.close()
            self.modemObj = None
        logger_test.error("MODEM CRASH DETECTED: collecting core dump")

        icera_tools_bin_path = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera'])

        modem.get_crash_dump_log(core_dump_dir=self.results_f, icera_utils_path=icera_tools_bin_path)


    def getVerdict(self, testStatus):
        """
        return "PASS, FAIL or INCONCLUSIVE"
        """
        if testStatus == 0:
            return "PASS"

        elif testStatus in [self.code.ERRCODE_SYS_CMW_CONN, self.code.ERRCODE_SYS_CMW_TIMEOUT,
                            self.code.ERRCODE_SYS_SOCKET_CONN, self.code.ERRCODE_SYS_FILE_IO,
                            self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG, self.code.ERRCODE_SYS_CMW_INVMEAS,
                            self.code.ERRCODE_SYS_CMW_CELL_ON, self.code.ERRCODE_SYS_LOG_FAIL,
                            self.code.ERRCODE_SYS_CMW_INCORRECT_SW_VERSION, self.code.ERRCODE_SYS_CMW_CONFIG,
                            self.code.ERRCODE_UNHANDLED_EXECEPTION]:
            return "INCONCLUSIVE"
        else:
            return "FAILURE"


    def set_modemLogProcessRunning(self, state):
        self.modemLogProcessRunning=state

    def get_modemLogProcessRunning(self):
        return self.modemLogProcessRunning

    def set_log_iom_f(self, basefilename):
        self.log_iom_f = basefilename

    def set_log_db_f(self, basefilename):
        self.log_db_f= basefilename

    def set_log_glp_f(self, basefilename):
        self.log_glp_f = basefilename

    def set_log_dec_f(self, basefilename):
        self.log_dec_f = basefilename

    def get_log_iom_f(self):
        return self.log_iom_f

    def get_log_db_f(self):
        return self.log_db_f

    def get_log_glp_f(self):
        return self.log_glp_f

    def get_log_dec_f(self):
        return self.log_dec_f

    def _set_up_modem_logging(self, basefilename):

        # log file setup
        icera_results_path = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'results', 'current'])
        log_iom_f = "%s.iom" %basefilename
        log_db_f  = "%s.ix" %basefilename
        log_glp_f = "%s.glp" %basefilename
        log_dec_f = "%s.iot" %basefilename

        log_iom_f = os.sep.join(icera_results_path.split(os.sep)[:]+[log_iom_f])
        self.set_log_iom_f(log_iom_f)

        log_db_f =  os.sep.join(icera_results_path.split(os.sep)[:]+[log_db_f])
        self.set_log_db_f(log_db_f)

        log_glp_f = os.sep.join(icera_results_path.split(os.sep)[:]+[log_glp_f])
        self.set_log_glp_f(log_glp_f)

        log_dec_f = os.sep.join(icera_results_path.split(os.sep)[:]+[log_dec_f])
        self.set_log_dec_f(log_dec_f)

        icera_tools_bin_path = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera'])


        if sys.platform in ['cygwin', 'win32']:
            # command setup
            self.geanielog_cmd_iom   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['icera_log_serial -v5 %s' %self.get_log_iom_f()])
            self.geanielog_cmd_db    = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['icera_log_serial -e %s' %self.get_log_db_f()])
            self.geanielog_cmd_glp   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['genie-log-file convert %s %s %s' % (self.get_log_iom_f(), self.get_log_db_f(), self.get_log_glp_f())])
            self.geanielog_cmd_dec   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['genie-log-file decode %s %s' % (self.get_log_glp_f(), self.get_log_dec_f())])
        else:
            logging_port = auto_detect_port("LOGGING_PORT")
            # change to executable file as after perforce check in files are non executable
            cmd_chmodx="chmod +x %s/icera_log_serial" % icera_tools_bin_path
            RunCmd(cmd=cmd_chmodx, timeout=20).Run()
            cmd_chmodx="chmod +x %s/genie-log-file" % icera_tools_bin_path
            RunCmd(cmd=cmd_chmodx, timeout=20).Run()

            self.geanielog_cmd_iom   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['icera_log_serial -d %s -v5 %s' %(logging_port, self.get_log_iom_f())])
            self.geanielog_cmd_db    = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['icera_log_serial -d %s -e %s' %(logging_port, self.get_log_db_f())])
            self.geanielog_cmd_glp   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['genie-log-file convert %s %s %s' % (self.get_log_iom_f(), self.get_log_db_f(), self.get_log_glp_f())])
            self.geanielog_cmd_dec   = os.sep.join(icera_tools_bin_path.split(os.sep)[:]+['genie-log-file decode %s %s' % (self.get_log_glp_f(), self.get_log_dec_f())])


    def set_modemLogProcId(self, proc_id):
        self.modemLogProcId=proc_id

    def get_modemProcId(self):
        return self.modemLogProcId

    def start_modem_log_capture(self, basefilename):
        logger_test=logging.getLogger('start_modem_log_capture')
        if self.config.msglog:
            self._set_up_modem_logging(basefilename)

            logger_test=logging.getLogger('start_modem_log_capture')
            # Start IOM process
            proc_log=Process(target=os.system, args=(self.geanielog_cmd_iom,))
            time.sleep(1)
            proc_log.start()
            logger_test.info("**************>>>>> Started IOM procid = %s" %  proc_log.pid)
            self.set_modemLogProcessRunning(state=True)
            return proc_log.pid
            #self.set_modemLogProcId(proc_id=proc_log.pid)

    '''
    def set_log_capture_status(self, status=cg.SUCCESS):
        self.log_capture_status = status
    '''

    def set_log_capture_status(self, status=SUCCESS):
        self.log_capture_status = status

    def get_log_capture_status(self):
        return self.log_capture_status

    def end_modem_log_capture(self, proc_id):

        #self.set_log_capture_status(status=cg.SUCCESS)
        self.set_log_capture_status(status=self.SUCCESS)

        if self.config.msglog:
            logger_test=logging.getLogger('end_log_capture')
            logger_test.info( ">>>> Killing proc_log.pid = %s" % proc_id)
            if sys.platform in ['cygwin', 'win32']:
                cmd = 'taskkill /f /t /im icera_log_serial.exe'
                runStatus, StDout,StDerr = RunCmd(cmd=cmd, timeout=40).Run()
                #if runStatus == cg.FAIL:
                if runStatus == self.FAIL:
                    sys.exit(self.code.ERRCODE_SYS_LOG_FAIL)
                elif StDerr:
                    #self.set_log_capture_status(status=cg.FAIL)
                    self.set_log_capture_status(status=self.FAIL)
                else:
                    pass
            else:
                os.system('killall -v icera_log_serial')

            self.set_modemLogProcessRunning(state=False)
            self.set_modemLogProcId(proc_id=-1)
            time.sleep(2)       # this is maybe not needed

    def process_log_capture(self):
        if self.config.msglog:
            logger_test=logging.getLogger('process_log_capture')
            #if self.get_log_capture_status()==cg.FAIL:
            if self.get_log_capture_status()==self.FAIL:
                logger_test=logging.getLogger('log processing will not take place beacuse of modem log capture error')
                return
            if 1:
                # TRACE
                proc_log=Process(target=os.system, args=(self.geanielog_cmd_db,))
                time.sleep(1)
                proc_log.start()
                time.sleep(1)
                logger_test.info("Collecting tracegen procid = %s" %  proc_log.pid)
                proc_log.join()
                # GLP
                proc_log=Process(target=os.system, args=(self.geanielog_cmd_glp,))
                time.sleep(1)
                proc_log.start()
                time.sleep(1)
                logger_test.info("Creating GLP = %s" %  proc_log.pid)
                proc_log.join()
                # DECODE
                proc_log=Process(target=os.system, args=(self.geanielog_cmd_dec,))
                time.sleep(1)
                proc_log.start()
                time.sleep(1)
                logger_test.info("Decoding GLP = %s" %  proc_log.pid)
                proc_log.join()
                try:
                    os.remove(self.get_log_iom_f())
                except Exception:
                    print traceback.format_exc()
                    print "Non fatal error, will continue anyway"
                try:
                    os.remove(self.get_log_db_f())
                except Exception:
                    print traceback.format_exc()
                    print "Non fatal error, will continue anyway"
                try:
                    os.remove(self.get_log_dec_f())
                except Exception:
                    print traceback.format_exc()
                    print "Non fatal error, will continue anyway"

    def get_cmw_sw_version(self):

        cmwswinfo = self.cmw.get_sw_version()

        cmwinfo = self.cmw.checkSwVersion(cmwswinfo)

        if cmwinfo:
            info = [x.replace(',', '_') for x in cmwinfo]
        else:
            info = ['N/A']

        self.cur_test.set_cmwinfo(cmwinfo=info)


    def get_intraHHO_list(self, band, num_uarfcn_sel_str="all"):

        func_name = sys._getframe(0).f_code.co_name
        logger_test = logging.getLogger(__name__ + func_name)

        MIN_NUM_UARFCN = 1
        uarfcn_minmax = umts_util.Range_EARFCN(band)
        uarfcn_intraho_l=range(uarfcn_minmax[0],uarfcn_minmax[1]+1)
        len_intrahho_l = len(uarfcn_intraho_l)

        bot = umts_util.min_dl_UARFCN(band=band)
        mid = umts_util.default_dl_uarfcn(band=band)
        top = umts_util.max_dl_UARFCN(band=band)

        add_uarfcn_list = [bot, mid, bot, top, bot, mid, top, mid]

        if num_uarfcn_sel_str.upper() == "ALL":

            min_num_uarfcn = len_intrahho_l

            uarfcn_step_size = len(uarfcn_intraho_l)/min_num_uarfcn

            uarfcn_l = uarfcn_intraho_l[::uarfcn_step_size]

            uarfcn_l = add_uarfcn_list + uarfcn_l

        elif num_uarfcn_sel_str.upper() == "DEFAULT":

            uarfcn_l = [bot, mid, bot, top, bot, mid, top, mid]

        else:
            min_num_uarfcn = 5

            if min_num_uarfcn <= 0:
                logger_test.debug ("Minimum number of UARFCN %s is less than %s" %(min_num_uarfcn, MIN_NUM_UARFCN))
                logger_test.debug ("Setting the minimum number of UARFCN under test to %s" %MIN_NUM_UARFCN)
                min_num_uarfcn = MIN_NUM_UARFCN

            elif min_num_uarfcn > len_intrahho_l:
                logger_test.debug ("number of uarfcn %s is greater than max number of UARFCN' %s in band %s"
                                   %(min_num_uarfcn, len_intrahho_l, band))
                logger_test.debug ("setting min number of UARFCN to %s" % len_intrahho_l)
                min_num_uarfcn = len_intrahho_l

            uarfcn_step_size = len(uarfcn_intraho_l)/min_num_uarfcn

            uarfcn_l = uarfcn_intraho_l[::uarfcn_step_size]

        logger_test.debug("UARFCN list")
        logger_test.debug(uarfcn_l)
        return uarfcn_l

    def set_breakpoint(self):
        '''
        gracefully break the test
        '''
        sys.exit(self.code.ERRCODE_TEST_DEBUG)
        return


    def init_database(self):

        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + " " + func_name)

        if self.config.database:
            local_dbname = self.config.database
            if not os.path.exists(local_dbname):
                db_h=results_db(local_dbname)
                db_h.disconnect()
                del db_h

            sqlite_db.DB_CheckPermission(local_dbname)

        else:
            loggerDisplay.info("local database name has not been specified or identified")

    def update_database(self):
        if self.config.database:
            local_dbname=self.config.database

            sqlite_db.DB_wcdma_import_from_file_meas(dbname=local_dbname, filename=self.csvReportBlerPathName, testType=self.cur_test.testtype)
        if self.config.remoteDB:

            mysql_db.DB_mySQL_wcdma_import_from_file_meas(filename=self.csvReportBlerPathName, testType=self.cur_test.testtype,
                                                          host=self.config.remoteDBhost, dbname=self.config.remoteDBname,
                                                          uid=self.config.remoteDBuid, pwd=self.config.remoteDBpwd,
                                                          config_pwr_meas=self.config.pwrmeas)

    def check_cmw_uarfcn_freqMHz(self, carrier, uarfcn, freqMHz):

        func_name = sys._getframe(0).f_code.co_name

        logger_test = logging.getLogger(__name__ + " " + func_name)

        # get raw readings from cmw
        dl_chan=self.cmw.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:CHANnel:DL?' % carrier)
        dl_freq=self.cmw.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:FREQuency:DL?' % carrier)

        # check that cmw has been configured correctly
        if int(dl_chan) == int(uarfcn):
            cmw_freqMHz = float(dl_freq)/1e6
            cmw_freqMHz = "%.2f" % cmw_freqMHz
            target_freqMHz = "%.2f" % freqMHz
            if cmw_freqMHz == target_freqMHz:
                logger_test.info('cmw changed to target UARFCN=%s, Freq=%s MHz' %(dl_chan, cmw_freqMHz))
            else:
                logger_test.info('cmw freq read from instrument %s MHz does not match with target freq %s MHz'
                                  %(cmw_freqMHz, target_freqMHz))
                self.result = self.code.ERRCODE_SYS_CMW_CONFIG
                sys.exit(self.result)
        else:
            logger_test.info('cmw uarfcn read from instrument %s does not match with target uarfcn %s'
                             %(dl_chan, uarfcn))
            self.result = self.code.ERRCODE_SYS_CMW_CONFIG
            sys.exit(self.result)


    def runTest(self):

        try:

            logger_test = logging.getLogger(__name__ + ' runTest')

            print self.cur_test

            # Open a connection to the CMW500
            # ====================================================
            cmwname = 'cmw500'
            #self.cmw = CmuControl(name=cmwname, ip_addr=self.config.cmwip)
            self.cmw = cmw.CmuControl(name=cmwname, ip_addr=self.config.cmwip)
            logger_test.info("Connection to %s @ %s...OK" % (cmwname, self.config.cmwip))

            self.get_cmw_sw_version()

            # switch on power
            self.setup_pwr_meas(Vmax_V=3.8, Imax_A=5)

            self.cmw.Cell_OFF()

            if 0:
                raw_input("Force modem crash")

            #self.modemObj = serialComms(timeout = 2, simulate_usim=self.config.usimemu)
            self.modemObj = modem.serialComms(timeout = 2, simulate_usim=self.config.usimemu)

            modeminfo = self.modemObj.getInfo()
            if not modeminfo:
                sys.exit(self.code.ERRCODE_SYS_MODEM_RESPONSE)
            self.cur_test.set_modeminfo(modeminfo=modeminfo)

            # initialise cvs report bler, must be done here to extract modeminfo
            self.csvReportBler=CsvReportBler(test_s = self.cur_test, test_conf=self.config,
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

            for rfband in self.cur_test.rfband:

                self.modemObj.set_preferred_rat(rat="UTRAN", band=rfband)

                for uarfcn in self.cur_test.uarfcn_dic[rfband]:

                    logger_test.debug("Selected RF_BAND=%s, DL_UARFCN=%s" % (rfband, uarfcn))

                    if self.intraHO:

                        matchObj = re.match('BLER_INTRAHO_(.*)', self.cur_test.testtype, re.I)

                        if matchObj:

                            uarfcn_intraho_l = self.get_intraHHO_list(band=rfband,
                                                                      num_uarfcn_sel_str=matchObj.group(1))

                            num_hho_steps = len(uarfcn_intraho_l)

                        else:

                            sys.exit(self.code.ERRCODE_TEST_FAILURE_INTRAHO)

                    else:

                        uarfcn_intraho_l =[uarfcn]

                    for data_rate in self.cur_test.datarate:

                        for rfpower in self.cur_test.rfpower:

                            for txants in self.cur_test.txants:

                                for snr in self.cur_test.snr:

                                    #teststep_idx += 1

                                    logger_test.info("Resetting CMW500")
                                    self.cmw.reset()
                                    self.cmw.initialConfig()

                                    #self.cmw_conf.set_snr(snr)
                                    self.cmw.set_rf_band(rfband)
                                    self.cmw.set_uarfcn(uarfcn)
                                    # check that date rate is supported by CMW500
                                    if not self.cmw.set_data_rate(datarate_str = data_rate):
                                        continue
                                    self.cmw.set_rf_power_dbm(rfpower)

                                    self.cmw.Cell_OFF()

                                    # radio off
                                    self.disable_modem_fun()

                                    # ENABLE LOG
                                    # ====================================================
                                    modemLogBaseName=""
                                    modemLogBaseName='WCDMA_CMW500_test_id_%s_modem_%s' %(self.testID,data_rate)
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

                                            print("Intra HHO - Running step %s of %s..." % (teststep_idx, num_hho_steps))
                                            logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                            ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn_hho_target, rfpower, snr))

                                            if teststep_idx == 1:
                                                uarfcn_hho_source = uarfcn
                                            else:
                                                uarfcn_hho_source = uarfcn_prev_loop

                                            logger_test.info("Starting blind HO from UARFCN %s (%s MHz) to target UARFCN %s (%s MHz)"
                                                              % (uarfcn_hho_source, umts_util.get_umts_dl_freq(uarfcn_hho_source),
                                                                 uarfcn_hho_target, umts_util.get_umts_dl_freq(uarfcn_hho_target)))
                                            self.cmw.set_uarfcn(uarfcn=uarfcn_intraho, carrier=1)

                                            target_freqMHz = umts_util.get_umts_dl_freq(uarfcn_hho_target)
                                            self.check_cmw_uarfcn_freqMHz(carrier=1,
                                                                          uarfcn=uarfcn_hho_target,
                                                                          freqMHz=target_freqMHz)

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
                                            print("Running step %s of %s..." % (teststep_idx, self.cur_test.get_total_test_steps()))
                                            logger_test.info("data rate =%s, band=%s" %(data_rate, rfband)  +
                                            ", uarfcn=%s, rfpower=%s, SNR=%s" % (uarfcn, rfpower, snr))

                                        self.start_pwr_meas()

                                        # Get bler measurements
                                        # ========================
                                        self.cmw.get_ber_meas(Tblocks=500)
                                        try:
                                            meas_list = self.cmw.ber_meas.get_list()
                                        except ValueError:
                                            print traceback.format_exc()
                                            sys.exit(self.code.ERRCODE_TEST_FAILURE_CEST)

                                        logger_test.info ("Bler results list : %s" %meas_list)
                                        print self.cmw.ber_meas
                                        verdict_s = self.cmw.get_ber_verdict(dlBlerLim = 3)
                                        if 'FAIL' in verdict_s:
                                            self.result = self.code.ERRCODE_TEST_FAILURE_BLER if self.result == 0 else self.code.ERRCODE_TEST_FAILURE_GENERAL

                                        if self.intraHO :
                                            uarfcn_hho_str= str(uarfcn_hho_source) + " - " + str(uarfcn_hho_target)
                                            param_list = [self.testID, rfband, uarfcn_hho_str, self.cur_test.chtype,
                                                          data_rate, snr, rfpower, txants ]
                                        else:
                                            param_list = [self.testID, rfband, uarfcn, self.cur_test.chtype,
                                                          data_rate, snr, rfpower, txants ]

                                        # Add power measurements
                                        # ========================
                                        pwr_s = self.get_pwr_meas()

                                        # Update CSV report
                                        # ========================
                                        msg_s = param_list + meas_list + [verdict_s]
                                        if self.config.pwrmeas:
                                            msg_s = msg_s + pwr_s

                                        self.csvReportBler.append(msg_s)
                                        #####

                                        if not self.intraHO :

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
            #Csv2Xls(self.csvReportBlerPathName)

            # Create HTML
            # ========================
            Csv2Html(self.csvReportBlerPathName)

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
                self.cmw.abort_ber_meas()
                self.close_conn_cmw()

            # capture core dump and close modem connection
            if self.modemObj:
                if self.modemObj.check_for_crash():
                    self.capture_core_dump()
                    #cf.pause(duration_s=30, poll_time_sec=2, desc= "waiting for modem to enter normal mode")
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
