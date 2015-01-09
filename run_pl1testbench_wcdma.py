#-------------------------------------------------------------------------------
# Name:        run_pl1testbench_wcdma
# Purpose:     top level python script for executing 3G regression tests
#
# Author:      joashr
#
# Created:     17/12/2013
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time

"""
XML parsing: ElementTree (etree) provides a Python-based API for parsing/generating
"""
import pprint

from xml.etree.ElementTree import parse

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

import test_env


from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging
from pl1_testbench_framework.wcdma.common.config.cfg_test import cfg_test
from pl1_testbench_framework.wcdma.common.config.cfg_test_dc_hsdpa import cfg_test_dc_hsdpa
from pl1_testbench_framework.wcdma.common.config.cfg_test_hspa import cfg_test_hspa
from pl1_testbench_framework.wcdma.common.config.cfg_test_fading_hspa import cfg_test_fading_hspa
from pl1_testbench_framework.wcdma.common.config.test_plan import test_plan
from pl1_testbench_framework.common.config.CfgError import CfgError
from pl1_testbench_framework.common.utils.os_utils import remove_dir
from pl1_testbench_framework.wcdma.common.testtype.testbler import Testbler
from pl1_testbench_framework.wcdma.common.testtype.hspa_testbler import HspaTestbler
from pl1_testbench_framework.wcdma.common.testtype.dc_hsdpa_testbler import DualCellHsdpaTestbler
from pl1_testbench_framework.wcdma.common.testtype.hspa_fading_testbler import HspaFadingTestbler
from pl1_testbench_framework.wcdma.common.testtype.hspa_interbandHHO_testbler import HspaInterBandHHO_testbler


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
        elif curr_test_testtype == 'HSPA_FADING_PERF':
            curr_test = cfg_test_fading_hspa(testID)
        print curr_test
    return

class wcdma_pl1testbench(object):

    LOG_FILE_MIN_LIMIT = 1 # minimum number of iterations before log summary file
                           # is produced

    def __init__(self, param_s):

        self.log             = param_s.log
        self.cmwip           = param_s.cmwip
        self.ctrlif          = param_s.ctrlif
        self.test2execute    = param_s.test2execute
        self.pwrmeas         = param_s.pwrmeas
        self.usimemu         = param_s.usimemu
        self.psugwip         = param_s.psugwip
        self.psugpib         = param_s.psugpib
        self.msglog          = param_s.msglog
        self.stored_msg_log  = param_s.msglog # need to store this setting as it is
                                              # changed for intra HHO tests
        self.database        = None if param_s.database=='' else param_s.database
        self.remoteDB        = param_s.remoteDB
        self.remoteDBhost    = None if param_s.remoteDBhost=='' else param_s.remoteDBhost
        self.remoteDBuid     = None if param_s.remoteDBuid=='' else param_s.remoteDBuid
        self.remoteDBpwd     = None if param_s.remoteDBpwd=='' else param_s.remoteDBpwd
        self.remoteDBname    = None if param_s.remoteDBname=='' else  param_s.remoteDBname

        self.final_f            = ""   # final destination folder for logs
        self.logFileSummaryPath = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'results', 'log']+['logSummary.csv'])
        self.numIterations = 1        # defines the number of iterations of self.runTest
                                      # if only a single iteration then there is no need
                                      # for logFileSummary
        try:
            self.unittest      = param_s.unittest
        except AttributeError:
            self.unittest      = 0

    def get_numIterations(self):
        return self.numIterations

    def set_numIterations(self, numIters):
        self.numIterations = numIters

    def __str(self):
        print "--------------------------------------"
        print "log                : %s"    %self.log
        print "cmwip              : %s"    %self.cmwip
        print "ctrlif             : %s"    %self.ctrlif
        print "test2execute       : %s"    %self.test2execute
        print "pwrmeas            : %s"    %self.pwrmeas
        print "usimemu            : %s"    %self.usimemu
        print "psugwip            : %s"    %self.psugwip
        print "psugpib            : %s"    %self.psugpib
        print "msglog             : %s"    %self.msglog
        print "final_f            : %s"    %self.final_f
        print "logFileSummaryPath : %s"    %self.logFileSummaryPath
        print "numIterations      ; %s"    %self.numIterations
        print "--------------------------------------"
        return ""

    def set_final_f(self, dst_folder):

        self.final_f = dst_folder

    def get_final_f(self):

        return self.final_f

    def runTest(self):

        code = CfgError()

        state = 0

        if self.cmwip == "x.y.w.z":
            print "ERROR: runme() : specify a valid CMW500 IP address"
            exit(code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

        if self.test2execute.upper()=='ALL':
            test2execute_l=sorted(test_plan.keys())
        else:
            test2execute_l=re.sub(r'[\[\]\s]', '', self.test2execute).split(',')

        logfilename=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'run_pl1testbench_wcdma.LOG'])
        cfg_multilogging(log_level=self.log, log_file=logfilename)
        logger_test=logging.getLogger('runTest')

        curr_f=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'results', 'current'])
        latest_f=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'results', 'latest'])

        ts=time.strftime("%Y%m%d_%H%M%S", time.localtime())
        final_f=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['wcdma', 'results', ts + '_WCDMA_TestReport'])
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

                curr_test_testtype = test_plan[testID]['TESTTYPE']

                self.msglog = self.stored_msg_log

                if curr_test_testtype == 'BLER_PERF':

                    testbler = Testbler(testID=testID, results_f=curr_f)

                elif curr_test_testtype == 'HSPA_BLER_PERF':

                    testbler = HspaTestbler(testID=testID, results_f=curr_f)

                elif curr_test_testtype == 'DCHSDPA_BLER_PERF':

                    # choose the correct object
                    testbler = DualCellHsdpaTestbler(testID=testID, results_f=curr_f)

                elif curr_test_testtype == 'HSPA_FADING_PERF':

                    testbler = HspaFadingTestbler(testID=testID, results_f=curr_f)

                    if self.unittest:

                        regression = 1

                        testbler.set_jenkins_regression(regression=regression)

                elif curr_test_testtype in ['BLER_INTRAHO_ALL', 'BLER_INTRAHO_DEFAULT']:

                    testbler = Testbler(testID=testID, results_f=curr_f, intraHO=1)

                    if self.msglog:

                        logger_test.info("Intra HHO test auto modem logging will be disabled!")

                        self.msglog = 0

                elif curr_test_testtype in [ 'HSPA_BLER_INTRAHO_DEFAULT', 'HSPA_BLER_INTRAHO_ALL',]:

                    testbler = HspaTestbler(testID=testID, results_f=curr_f, intraHO=1)

                    if self.msglog:

                        logger_test.info("Intra HHO test auto modem logging will be disabled!")

                        self.msglog = 0

                elif curr_test_testtype in [ 'DCHSDPA_BLER_INTRAHO_DEFAULT', 'DCHSDPA_BLER_INTRAHO_ALL']:

                    testbler = DualCellHsdpaTestbler(testID=testID, results_f=curr_f, intraHO=1)

                    if self.msglog:

                        logger_test.info("Intra HHO test auto modem logging will be disabled!")

                        self.msglog = 0

                elif curr_test_testtype in ['BLER_INTERBAND_DEFAULT']:

                    testbler = HspaInterBandHHO_testbler(testID=testID, results_f=curr_f)

                    if self.msglog:

                        logger_test.info("Interband HHO test auto modem logging will be disabled!")

                        self.msglog = 0

                else:

                    logger_test.warning("Unknown test type %s. TestID %s SKIPPED" % (curr_test.testtype, curr_test.testID))

                    continue


                testbler.set_test_config(log=self.log.upper(), cmwip=self.cmwip, ctrlif=self.ctrlif,
                                         test2execute=testID, pwrmeas=self.pwrmeas,
                                         usimemu=self.usimemu, psugwip=self.psugwip, psugpib=self.psugpib,
                                         msglog=self.msglog, database=self.database, remoteDB = self.remoteDB,
                                         remoteDBhost = self.remoteDBhost, remoteDBuid = self.remoteDBuid,
                                         remoteDBpwd = self.remoteDBpwd, remoteDBname = self.remoteDBname)

                result = testbler.runTest()

                if state == 0 :

                    state = result

                else:

                    if result == state:

                        pass

                    else:

                        if result == 0:

                            pass

                        else:
                            # must be a new error

                            state = code.ERRCODE_TEST_FAILURE_GENERAL


        # end of for loop

        except SystemExit:
            exc_info = sys.exc_info()
            state=int('%s' % exc_info[1])
            return (state)

        if self.get_numIterations > self.LOG_FILE_MIN_LIMIT:
            self.writeLogSummaryFile(testbler.csvSummaryReport.get_full_path_name())

        # Rename test result folder before exiting
        if os.path.isdir(latest_f):
            remove_dir(latest_f)
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


def get_remote_dbase_params_from_xml(xml_file=""):
    class Struct():
        pass
    param = Struct()
    print "Test config xml file chosen for remote database parameters : %s" %xml_file
    tree = parse(xml_file)
    wcdma = tree.find('wcdma')
    try:
        param.remoteDB = int(wcdma.find('remoteDB').text)
    except:
        param.remoteDB = 0
    param.remoteDBhost = wcdma.find('remoteDBhost').text
    param.remoteDBuid  = wcdma.find('remoteDBuid').text
    try:
        param.remoteDBpwd  = '%s' %unicode(wcdma.find('remoteDBpwd').text, ('unicode-escape')).encode('latin-1')
    except:
        param.remoteDBpwd = None
    param.remoteDBname = wcdma.find('remoteDBname').text
    return param

def get_params_from_xml(xml_file="", jenkins_linux=0):

    class Struct():
        pass

    param = Struct()

    print "Local test config xml file for WCDMA parameters : %s" %xml_file
    tree = parse(xml_file)

    wcdma = tree.find('wcdma')

    param.log          = wcdma.find('log').text
    param.cmwip        = wcdma.find('cmwip').text
    param.ctrlif       = wcdma.find('ctrlif').text
    param.test2execute = wcdma.find('test2execute').text
    param.pwrmeas      = int(wcdma.find('pwrmeas').text)
    param.usimemu      = int(wcdma.find('usimemu').text)

    param.psugpib      = wcdma.find('psugpib').text
    param.msglog       = int(wcdma.find('msglog').text)
    param.database     = wcdma.find('database').text

    param.cmwip        = wcdma.find('cmwip').text
    param.psugwip      = wcdma.find('psugwip').text

    try:
        param.remoteDB = int(wcdma.find('remoteDB').text)
    except:
        param.remoteDB = 0
    param.remoteDBname = wcdma.find('remoteDBname').text
    param.remoteDBhost = wcdma.find('remoteDBhost').text
    param.remoteDBuid  = wcdma.find('remoteDBuid').text
    try:
        param.remoteDBpwd  = '%s' %unicode(wcdma.find('remoteDBpwd').text, ('unicode-escape')).encode('latin-1')
    except:
        param.remoteDBpwd = None

    return param


def get_params_jenkins_linux_xml():

    local_setupconfig_xml = os.path.join(os.environ['PL1_WCDMA_TEST_ROOT'], 'test_config_per_cl.xml')
    print local_setupconfig_xml

    class Struct():
        pass

    param = Struct()


    if not os.path.isfile(local_setupconfig_xml):
        print("Could not find local Jenkins XML configuration file : %s" % local_setupconfig_xml)
        sys.exit(0)

    else:
        print "Reading from %s" %local_setupconfig_xml
        tree              = parse(local_setupconfig_xml)
        section           = tree.find('pl1jenkins')

        param.cmw500_ip   = section.find('cmw500_ip').text
        param.lan2gpib_ip = section.find('lan2gpib_ip').text
        param.scdu_ip     = section.find('scdu_ip').text

        print("-------------------------------------------")
        print("  cmw500_ip   : %s" % param.cmw500_ip)
        print("  lan2gpib_ip : %s" % param.lan2gpib_ip)
        print("  scdu_ip     : %s" % param.scdu_ip)
        print("-------------------------------------------")


    return param


def runTestExternal(testType="per_cl"):

    code = CfgError()

    valid_testTypes_dict = {'PER_CL':1, 'NIGHTLY':1, 'WEEKLY':1 }

    try:
        dummyVal = valid_testTypes_dict[testType.upper()]
    except KeyError:
        print "testType %s not supported" %testType
        print "testType supported list is %s" %valid_testTypes_dict.keys()
        return

    if testType.upper() == "PER_CL":

        test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config_per_cl.xml'])

    elif testType.upper() == "NIGHTLY":

        test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config_nightly.xml'])

    elif testType.upper() == "WEEKLY":

        test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config_weekly.xml'])

    print test_config_xml_path

    if os.path.isfile(test_config_xml_path):

        param = get_params_from_xml(xml_file=test_config_xml_path, jenkins_linux=0)

    else:
        print "%s cannot be found!" %test_config_xml_path
        res = code.ERRCODE_SYS_FILE_IO
        return res

    wcdma = wcdma_pl1testbench(param_s = param)
    res = wcdma.runTest()
    return res

if __name__ == '__main__':

    code =CfgError()

    #test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config.xml'])
    test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma_test_config.xml'])

    if os.path.isfile(test_config_xml_path):

        param = get_params_from_xml(xml_file=test_config_xml_path)

    else:
        # Parse Input Parameters
        description_msg="""
        Start the wcdma test bench for PL1 branch validation. CMW500 IP is required. Example: python run_wcdma_test.py -log=INFO -test2execute=[0] -cmwip=x.y.z -ctrlif=AT -pwrmeas=0 -usimemu=1"""
        parser=argparse.ArgumentParser(description=description_msg)
        parser.add_argument("-log", type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO', help="Define logging level. Default='DEBUG'" )
        parser.add_argument("-cmd", type=str, choices=['testlist'], help="testlist : Retrieve the list of testIDs available" )
        parser.add_argument("-cmwip", type=str, default='x.y.w.z', help='cmw500 IP address' )
        parser.add_argument("-ctrlif", type=str, choices=['AT', 'KMT', 'STDIN', 'ADB'], default='AT', help="define the modem communication control interface")
        parser.add_argument("-test2execute", type=str, default='[0,1,2]', help="select the tests to execute. Default=ALL")
        parser.add_argument("-pwrmeas", type=int, choices=[0, 1], default=0, help="Enable power measurements. Default=0")
        parser.add_argument("-usimemu", type=int, choices=[0, 1], default=0, help="Enable USIM emulator. Default=0")
        parser.add_argument("-psugwip", type=str, default='x.y.w.z', help='PSU Gateway IP address' )
        parser.add_argument("-psugpib", type=int, default='0', help='PSU GPIB port. Default=0' )
        parser.add_argument("-msglog", type=int, choices=[0, 1], default=0, help="Enable msglog for debugging. Default=0")
        parser.add_argument("-database", type=str, default='', help="Specify database location")

        args=parser.parse_args()

        if args.cmd == 'testlist':
            display_testlist()
            exit(0)

        class Struct():
            pass

        param = Struct()
        param.log           = args.log
        param.cmwip         = args.cmwip
        param.ctrlif        = args.ctrlif
        param.test2execute  = args.test2execute
        param.pwrmeas       = args.pwrmeas
        param.usimemu       = args.usimemu
        param.psugwip       = args.psugwip
        param.psugpib       = args.psugpib
        param.msglog        = args.msglog
        param.database      = args.database
        param.remoteDB      = 0

        param.remoteDBhost  = None
        param.remoteDBuid   = None
        param.remoteDBpwd   = None
        param.remoteDBname  = None

    wcdma = wcdma_pl1testbench(param_s = param)

    NUM_ITERATIONS = 1

    wcdma.set_numIterations(numIters=NUM_ITERATIONS)

    if wcdma.get_numIterations() > wcdma.LOG_FILE_MIN_LIMIT:

        wcdma.removeLogSummaryFile()

    for loop in range(wcdma.get_numIterations()):

        # remove logging handlers which could have been configured previously
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        if wcdma.get_numIterations() > wcdma.LOG_FILE_MIN_LIMIT:

            stars = "*" *50

            print "%sIteration %s in %s%s"%(stars,(loop+1), NUM_ITERATIONS, stars)

        res = wcdma.runTest()

    if wcdma.get_numIterations() == 1:

        print ("EXIT STATUS : (%s, %s)" % (res, code.MSG[res]))

    exit(res)

