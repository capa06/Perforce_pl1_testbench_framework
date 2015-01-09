#-------------------------------------------------------------------------------
# Name:        runTest
# Purpose:     top level python script for executing 3G regression tests
#
# Author:      joashr
#
# Created:     17/12/2013
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

try:
    os.environ['PL1_WCDMA_TEST_ROOT']
except KeyError:
    os.environ['PL1_WCDMA_TEST_ROOT'] = cmdpath
    print ">> os.environ['PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']

try:
    os.environ['TEST_SYSTEM_ROOT_FOLDER']
except KeyError:
    os.environ['TEST_SYSTEM_ROOT_FOLDER']  = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:-1]+['pl1_jenkins', 'test_system'])
    print "os.environ['TEST_SYSTEM_ROOT_FOLDER']=%s" % os.environ['TEST_SYSTEM_ROOT_FOLDER']

from addSystemPath import AddSysPath
AddSysPath(os.sep.join(os.environ['TEST_SYSTEM_ROOT_FOLDER'].split(os.sep)[:]))

# add wcdma paths before jenkins search path so that this aerch path has prioeity
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common', 'com']))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common']))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common', 'testtype']))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common', 'config']))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['instr']))
AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common', 'report', 'csv']))

from test_env import set_test_search_paths as set_jenkins_search_paths
set_jenkins_search_paths()

from enableLogging import enable_logging
import test_config as tg
from cfg_test import cfg_test
from cfg_test_dc_hsdpa import cfg_test_dc_hsdpa
from cfg_test_hspa import cfg_test_hspa
from test_plan import test_plan
from cfg_error import cfg_error
import common_functions as cf
from enableLogging import enable_logging
from testbler import Testbler
from hspa_testbler import HspaTestbler
from dc_hsdpa_testbler import DualCellHsdpaTestbler

def display_testlist():
    testID_list = sorted(test_plan.keys())
    print "LIST testIDs = %s" % testID_list
    for testID in testID_list:
        curr_test_testtype = test_plan[testID]['TESTTYPE']
        if curr_test_testtype == 'BLER_PERF':
            curr_test = cfg_test(testID)
        elif curr_test_testtype == 'HSPA_BLER_PERF':
            curr_test = cfg_test_hspa(testID)
        elif  curr_test_testtype == 'DCHSDPA_BLER_PERF':
            curr_test = cfg_test_dc_hsdpa(testID)
        print curr_test
    return

class wcdma_pl1testbench(object):

    def __init__(self, log, cmwip, ctrlif, test2execute, pwrmeas, usimemu, psugwip, psugpib, msglog=0):

        self.log = log
        self.cmwip = cmwip
        self.ctrlif = ctrlif
        self.test2execute=test2execute
        self.pwrmeas = pwrmeas
        self.usimemu= usimemu
        self.psugwip = psugwip
        self.psugpib = psugpib
        self.msglog = msglog

        self.final_f            = ""   # final destination folder for logs
        self.logFileSummaryPath = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'log']+['logSummary.csv'])

    def __str(self):
        print "--------------------------------------"
        print "log           : %s"    %self.logog
        print "cmwip         : %s"    %self.cmwip
        print "ctrlif        : %s"    %self.ctrlif
        print "test2execute  : %s"    %self.test2execute
        print "pwrmeas       : %s"    %self.pwrmeas
        print "usimemu       : %s"    %self.usimemu
        print "psugwip       : %s"    %self.psugwip
        print "psugpib       : %s"    %self.psugpib
        print "msglog        : %s"    %self.msglog
        print "final_f       : %s"    %self.final_f
        print "--------------------------------------"
        return ""

    def set_final_f(self, dst_folder):

        self.final_f = dst_folder

    def get_final_f(self):

        return self.final_f

    def runTest(self):

        code = cfg_error()

        state = 0

        if self.cmwip == "x.y.w.z":
            print "ERROR: runme() : specify a valid CMW500 IP address"
            exit(code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

        if self.test2execute.upper()=='ALL':
            test2execute_l=sorted(test_plan.keys())
        else:
            test2execute_l=re.sub(r'[\[\]\s]', '', self.test2execute).split(',')

        logfilename=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['runTest.LOG'])
        enable_logging(loglevel=self.log, log_file=logfilename)
        logger_test=logging.getLogger('runTest')

        curr_f=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'current'])
        latest_f=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])

        ts=time.strftime("%Y%m%d_%H%M%S", time.localtime())
        final_f=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:] + ['results', ts + '_WCDMA_TestReport'])
        self.set_final_f(dst_folder=final_f)

        try:

            # Clean any curr_f from previous run
            if os.path.exists(curr_f):
                shutil.rmtree(curr_f)
            if os.path.exists(latest_f):
                shutil.rmtree(latest_f)

            for testID in test2execute_l:

                result = 0
                t0=time.localtime()                       # Probe start time
                testID=int(testID)

                #curr_test=cfg_test(testID)
                curr_test_testtype = test_plan[testID]['TESTTYPE']

                if curr_test_testtype == 'BLER_PERF':

                    # choose the correct object
                    testbler = Testbler(testID=testID, results_f=curr_f)

                elif curr_test_testtype == 'HSPA_BLER_PERF':

                    # choose the correct object
                    testbler = HspaTestbler(testID=testID, results_f=curr_f)


                elif curr_test_testtype == 'DCHSDPA_BLER_PERF':

                    # choose the correct object
                    testbler = DualCellHsdpaTestbler(testID=testID, results_f=curr_f)

                else:

                    logger_test.warning("Unknown test type %s. TestID %s SKIPPED" % (curr_test.testtype, curr_test.testID))
                    continue

                testbler.set_test_config(log=self.log.upper(), cmwip=self.cmwip, ctrlif=self.ctrlif,
                                         test2execute=testID, pwrmeas=self.pwrmeas,
                                         usimemu=self.usimemu, psugwip=self.psugwip, psugpib=self.psugpib,
                                         msglog=self.msglog)

                result = testbler.runTest()

                state = result if result != 0 else 0

        # end of for loop

        except SystemExit:
            exc_info = sys.exc_info()
            state=int('%s' % exc_info[1])
            return (state)

        self.writeLogSummaryFile(testbler.csvSummaryReport.get_full_path_name())

        # Rename test result folder before exiting
        if os.path.isdir(latest_f):
            cf.remove_dir(latest_f)
        if os.path.isdir(curr_f):
            shutil.copytree(curr_f, latest_f)
            os.rename(curr_f, final_f)

        return (state)

    def removeLogSummaryFile(self):
        if os.path.isfile(self.logFileSummaryPath):
            print "Current log summary file %s will be removed" %self.logFileSummaryPath
            os.remove(self.logFileSummaryPath)

    def writeLogSummaryFile(self, testSummaryPath):

        """
        write contents of testSummaryPath to log summary file with
        an extra column referring to the directory location where the
        *TestReport_SUMMARY,csv is stored
        """
        import ntpath

        #self.logSummaryFilePath = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'log']+['logSummary.csv'])

        finalDirName = ntpath.basename(self.get_final_f())

        logSummaryFilePathDir = os.path.split(self.logFileSummaryPath)[0]

        if not os.path.exists(logSummaryFilePathDir):
            os.makedirs(logSummaryFilePathDir)

        with open(testSummaryPath) as mySummaryFile:
            summaryLineNum = 0
            for lineInSummaryFile in mySummaryFile:
                cols = lineInSummaryFile.split(',')
                if summaryLineNum == 0:
                    # i.e. headings column
                    lineInSummaryFile = lineInSummaryFile[:-1]
                    cols.insert(0,'Directory')
                else:
                    lineInSummaryFile = lineInSummaryFile[:-1]
                    cols.insert(0,finalDirName)

                summaryLineNum += 1

                with open(self.logFileSummaryPath,'a') as mylogfile:
                    lineInLogSummary = ','.join(cols)
                    mylogfile.write("%s" %lineInLogSummary)

        mySummaryFile.close()
        mylogfile.close()



if __name__ == '__main__':

    NUM_ITERATIONS = 1

    # Parse Input Parameters
    description_msg="""
    Start the wcdma test bench for PL1 branch validation. CMW500 IP is required. Example: python run_wcdma_test.py -log=INFO -test2execute=[0] -cmwip=x.y.z -ctrlif=AT -pwrmeas=0 -usimemu=1"""
    parser=argparse.ArgumentParser(description=description_msg)
    parser.add_argument("-log", type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='DEBUG', help="Define logging level. Default='DEBUG'" )
    parser.add_argument("-cmd", type=str, choices=['testlist'], help="testlist : Retrieve the list of testIDs available" )
    parser.add_argument("-cmwip", type=str, default='x.y.w.z', help='cmw500 IP address' )
    parser.add_argument("-ctrlif", type=str, choices=['AT', 'KMT', 'STDIN', 'ADB'], default='AT', help="define the modem communication control interface")
    parser.add_argument("-test2execute", type=str, default='[0]', help="select the tests to execute. Default=ALL")
    parser.add_argument("-pwrmeas", type=int, choices=[0, 1], default=0, help="Enable power measurements. Default=0")
    parser.add_argument("-usimemu", type=int, choices=[0, 1], default=0, help="Enable USIM emulator. Default=0")
    parser.add_argument("-psugwip", type=str, default='x.y.w.z', help='PSU Gateway IP address' )
    parser.add_argument("-psugpib", type=int, default='0', help='PSU GPIB port. Default=0' )
    parser.add_argument("-msglog", type=int, choices=[0, 1], default=0, help="Enable msglog for debugging. Default=0")

    args=parser.parse_args()

    if args.cmd == 'testlist':
        display_testlist()
        exit(0)

    """
    wcdma = wcdma_pl1testbench(log=args.log, cmwip=args.cmwip, ctrlif=args.ctrlif,
                               test2execute=args.test2execute, pwrmeas=args.pwrmeas,
                               usimemu=args.usimemu, psugwip=args.psugwip,
                               psugpib=args.psugpib, msglog=args.msglog)
    """


    wcdma = wcdma_pl1testbench(log = 'info', cmwip =tg.get_cmwip(),ctrlif = 'AT',
                           test2execute='[0]', pwrmeas=1, usimemu=0,
                           psugwip=tg.get_psugwip(), psugpib=tg.get_psugpib(),
                           msglog=1)

    wcdma.removeLogSummaryFile()

    for loop in range(NUM_ITERATIONS):

        # remove logging handlers which could have been configured previously
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        stars = "*" *50

        print "%sIteration %s in %s%s"%(stars,(loop+1), NUM_ITERATIONS, stars)



        res = wcdma.runTest()


    exit(res)

