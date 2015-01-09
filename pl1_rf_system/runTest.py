#-------------------------------------------------------------------------------
# Name:        runTest
# Purpose:      perform RF system tests
#
# Author:      joashr
#
# Created:     05/06/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, argparse, time, re
from collections import OrderedDict


"""
XML parsing: ElementTree (etree) provides a Python-based API for parsing/generating
"""
import pprint
from xml.etree.ElementTree import parse

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

import pl1_rf_system_test_env
import xml.etree.cElementTree as ET

from pl1_testbench_framework.common.instr.PsuBench import PsuCheckOn, PsuBenchOn, PsuBenchOff
from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port

from pl1_rf_system.common.user_exceptions import *
from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

import pl1_rf_system.common.rf_common_globals as rf_global
import pl1_rf_system.common.rf_common_functions as rf_cf
from pl1_rf_system.common.rf_modem import *
from pl1_rf_system.common.verdict import Verdict
import pl1_rf_system.common.config.test_plan_definition as tp


# import different test types
from pl1_rf_system.common.testtype.wcdma_tx import Wcdma_tx
from pl1_rf_system.common.testtype.general_purpose import General_Purpose
from pl1_rf_system.common.testtype.lte_tx import Lte_tx
import pl1_rf_system.instr.cmw500 as cmw500

class rf_testbench(object):

    LOG_FILE_MIN_LIMIT = 1 # minimum number of iterations before log summary file
                           # is produced

    def __init__(self, param_s, unittest_enabled=0):

        self.config       = param_s

        self.final_f            = ""   # final destination folder for logs
        self.logFileSummaryPath = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'log']+['logSummary.csv'])
        self.numIterations = 1        # defines the number of iterations of self.runTest
                                      # if only a single iteration then there is no need
                                      # for logFileSummary

        self.unittest_enabled=unittest_enabled

    def set_final_f(self, dst_folder):

        self.final_f = dst_folder

    def get_final_f(self):

        return self.final_f


    def __str__(self):
        print "--------------------------------------"
        print "log                : %s"    %self.config.log
        print "instr_name         : %s"    %self.config.instr_name
        print "instr_ip           : %s"    %self.config.instr_ip
        print "instr_gpib         : %s"    %self.config.instr_gpib
        print "test2execute       : %s"    %self.config.test2execute
        print "psugwip            : %s"    %self.config.psugwip
        print "psugpib            : %s"    %self.config.psugpib
        print "cable_loss (dB)    : %s"    %self.config.cable_loss
        print "final_f            : %s"    %self.final_f
        print "logFileSummaryPath : %s"    %self.logFileSummaryPath
        print "numIterations      : %s"    %self.numIterations
        print "--------------------------------------"
        return ""

    def print_pre_test_information (self,testID,test_exec_dic,testparams):
        print "\n-------------------------------------------------------------"
        print "-------------- Pre Test Information -------------------------"
        print "-------------------------------------------------------------"
        print "TestID        : %s" % testID
        print "TestFile      : %s" % test_exec_dic['test_file']
        print "TestName      : %s" % test_exec_dic['test_func']
        print "TestParams    : %s" % str(testparams)
        print "-------------------------------------------------------------\n\n"


    def print_pass_fail_list (self,resultdics,test_exec_dics):
        print "#########################################################################################"
        print "############################## OVERALL VERDICT ##########################################"
        print "#########################################################################################"
        print "\n TEST SEL    TEST/PARAM            TEST NAME                        RAT            VERDICT\n"
        for testsel, resultdic in resultdics.iteritems():
            test_exec_dic = test_exec_dics[testsel]
            for testparamID in resultdic:
                 testID = testparamID.split()[0]
                 paramIDX = int(testparamID.split()[1])
                 testparams = tp.test_plan[testsel][test_exec_dic[testID]['param_idx']][paramIDX]

                 try:
                     testrat = testparams['rat']
                 except KeyError:
                     testrat = test_exec_dic[testID]['test_rat']

                 print " %-10s   %-10s     %-36s  %-05s            %s" % (testsel,str(testparamID),test_exec_dic[testID]['test_func'],testrat,str(resultdic[testparamID]))
        print "\n"
        print "########################################################################################"
        print "########################################################################################"

    def print_itemized_failures(self,resultdic,verdictdic):
        heading_printed = False
        for testparamID in resultdic:
            if resultdic[testparamID] != "PASS":
                if not heading_printed:
                    heading_printed = True
                    print "\n###################### ITEMIZED FAILURES PER TEST ID ##########################"
                print "\nTest/Param ID: %s" % str(testparamID)
                if verdictdic[testparamID].ERROR_flag:
                    verdictdic[testparamID].PrintErrors()
                if verdictdic[testparamID].FAIL_flag:
                    verdictdic[testparamID].PrintFailed()
                elif not verdictdic[testparamID].ERROR_flag:
                    print "No failure information"

    def WriteResultsXml (self,folder,testsel,verdictdic,resultdic,test_exec_dic,startTimeDic,EndTimeDic,test_count):
        xml_file_path = folder+"/rf_factory_tests_per_cl.xml"

        if os.path.isfile(xml_file_path):
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            num_errors = int(root.get('errors'))
            num_test_failures = int(root.get('failures'))
            total_test_count = int(root.get('tests'))
        else:
            root = ET.Element("testsuite")
            root.set('name','rf_sys_tests')
            root.set('skip','0')
            num_errors = 0
            num_test_failures = 0
            total_test_count = 0

        for testparamID in resultdic:
            if resultdic[testparamID] != "PASS":
                if verdictdic[testparamID].ERROR_flag:
                    num_errors += len(verdictdic[testparamID].ERROR_list)
                if verdictdic[testparamID].FAIL_flag:
                    num_test_failures += 1

        total_test_count += test_count

        root.set('errors',str(num_errors))
        root.set('failures',str(num_test_failures))
        root.set('tests',str(total_test_count))

        for testparamID in resultdic:

            testID = testparamID.split()[0]
            paramIDX = int(testparamID.split()[1])
            testparams = tp.test_plan[testsel][test_exec_dic[testID]['param_idx']][paramIDX]

            try:
                testrat = testparams['rat']
            except KeyError:
                testrat = test_exec_dic[testID]['test_rat']

            exectime=time.mktime(EndTimeDic[testparamID])-time.mktime(startTimeDic[testparamID])
            testcase = ET.SubElement(root, "testcase")
            testcase.set('classname','pl1_rf_system.%s' % testsel)
            testcase.set('name',testrat+'_'+test_exec_dic[testID]['test_func'])
            testcase.set('time',str(exectime))

            if resultdic[testparamID] != "PASS":
                failinfo = ET.SubElement(testcase,'failure')
                failinfo.set('type','FAIL')
                failinfo.set('message','test_failure')

        tree = ET.ElementTree(root)
        tree.write(xml_file_path)


    def TestCount ():
        return current_test_count,total_test_count

    def runTest(self):

        curr_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'current'])
        latest_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'latest'])

        overall_result_str = rf_global.verdict_dict[rf_global.PASS]

        try:

            if self.config.instr_ip == "ww.xx.yy.zz":
                ErrMsg = "ERROR: runTest() : specify a valid Instrument IP address"
                raise ExRunTest(ErrMsg)

            test_selection = self.config.test_selection
            test_exec_dic = OrderedDict()
            total_test_count = 0
            current_test_count = 0

            #Build up list of tests to execute
            curr_test_p = tp.test_plan[test_selection]
            num_tests = len(curr_test_p)
            test_id_index_list = range(0,num_tests,2)


            for test_id_idx in test_id_index_list:
                test_id = curr_test_p[test_id_idx]
                num_param_sets = len(curr_test_p[test_id_idx+1])
                test_exec_dic[test_id]={'param_idx':test_id_idx+1}
                test_exec_dic[test_id]['total_iterations'] = num_param_sets
                test_exec_dic[test_id]['curr_iteration'] = 0
                test_exec_dic[test_id]['test_file'] = tp.testFilefromID(test_id)
                test_exec_dic[test_id]['test_func'] = tp.testFuncfromID(test_id)
                test_exec_dic[test_id]['test_rat'] = 'Undef'
                total_test_count += num_param_sets

            func_name = sys._getframe(0).f_code.co_name
            logfilename=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['%s.LOG' %func_name])
            cfg_multilogging(log_level=self.config.log, log_file=logfilename)
            logger_test=logging.getLogger('runTest')

            resultStrDic = OrderedDict()
            verdictObjDic = OrderedDict()
            startTimeDic = {}
            endTimeDic = {}


            if self.config.psugwip != 'ww.xx.yy.zz':
                '''
                if check_output_state_on(psu_gwip=self.config.psugwip,
                                         psu_gpib=self.config.psugpib,
                                         psu_name='E3631A_0',
                                         check_volts = self.config.psuvolt,
                                         check_curr_amps=2):
                '''
                if PsuCheckOn(psu_gwip=self.config.psugwip,
                                         psu_gpib=self.config.psugpib,
                                         check_volts = self.config.psuvolt,
                                         check_curr_amps=2):

                    print "PSU is already switched on"
                else:
                    PsuBenchOn(psu_gwip=self.config.psugwip,
                               psu_gpib=self.config.psugpib,
                               setVolts=self.config.psuvolt,
                               Imax_A=2)

                    if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

                        print "modem com port successfully found"

                        time_secs = 10

                        print "pausing for %s secs ..." %time_secs

                        time.sleep(time_secs)

                    else:
                        ErrMsg = "ERROR: runTest() : modem com port not found after switching on the PSU"
                        raise ExRunTest(ErrMsg)

            #Initiate CMW control

            if self.config.instr_ip == "no_instr":
                no_tester = True
            else:
                no_tester = False

            self.instr=cmw500.CmwControl(name=self.config.instr_name,
                                         ip_addr=self.config.instr_ip,
                                         NoTester=no_tester)


            for testID in test_exec_dic:

                while test_exec_dic[testID]['curr_iteration'] < test_exec_dic[testID]['total_iterations']:


                    testfile = test_exec_dic[testID]['test_file']
                    testfunc = test_exec_dic[testID]['test_func']
                    testparams = tp.test_plan[test_selection][test_exec_dic[testID]['param_idx']][test_exec_dic[testID]['curr_iteration']]
                    finalTest = ((current_test_count + 1) == total_test_count)

                    self.print_pre_test_information(testID,test_exec_dic[testID],testparams)

                    if testfile == "wcdma_tx.py":

                        test_exec_dic[testID]['test_rat'] = 'WCDMA'
                        test_rf = Wcdma_tx(testID = testID,
                                           testConfig_s = self.config,
                                           results_f = curr_f,
                                           test_func = testfunc,
                                           test_params = testparams,
                                           test_rat = 'WCDMA',
                                           final_test=finalTest,
                                           unittest_enabled=self.unittest_enabled)

                    elif testfile == "lte_tx.py":

                        test_exec_dic[testID]['test_rat'] = 'LTE'

                        test_rf = Lte_tx(testID = testID,
                                         testConfig_s = self.config,
                                         results_f = curr_f,
                                         test_func = testfunc,
                                         test_params = testparams,
                                         test_rat = 'LTE',
                                         final_test=finalTest,
                                         unittest_enabled=self.unittest_enabled)

                    elif testfile == "general_purpose.py":

                        try:
                            testrat = tp.test_plan[test_selection][test_exec_dic[testID]['param_idx']][test_exec_dic[testID]['curr_iteration']]['rat']
                        except KeyError:
                            testrat = "None"

                        test_exec_dic[testID]['test_rat'] = testrat

                        test_rf = General_Purpose(testID = testID,
                                                 testConfig_s = self.config,
                                                 results_f = curr_f,
                                                 test_func = testfunc,
                                                 test_params = testparams,
                                                 test_rat = testrat,
                                                 final_test=finalTest,
                                                 unittest_enabled=self.unittest_enabled)

                    else:

                        logger_test.warning("Test file %s does not exist. TestID %s SKIPPED"
                                            % (testfile, testID))

                    test_param_idx = "%-08s  %s" % (testID,str(test_exec_dic[testID]['curr_iteration']))
                    startTimeDic[test_param_idx] = time.localtime()
                    resultStrDic[test_param_idx],verdictObjDic[test_param_idx] = test_rf.executeTest(self.instr)
                    endTimeDic[test_param_idx] = time.localtime()

                    test_exec_dic[testID]['curr_iteration'] = test_exec_dic[testID]['curr_iteration'] + 1

                    if resultStrDic[test_param_idx] != rf_global.verdict_dict[rf_global.PASS]:

                        overall_result_str = resultStrDic[test_param_idx]

                    current_test_count += 1

        except ExGeneral, e:
            print '%s' %e.message
            overall_result_str = rf_global.verdict_dict[rf_global.INCONC]

        self.print_itemized_failures(resultStrDic,verdictObjDic)
        self.WriteResultsXml(curr_f,test_selection,verdictObjDic,resultStrDic,test_exec_dic,startTimeDic,endTimeDic,total_test_count)

        return overall_result_str,resultStrDic,test_exec_dic

def RemoveOldFolders ():
    curr_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'current'])
    latest_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'latest'])
    rx_sweep_data_folder=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets', 'results'])

   # Clean any curr_f from previous run
    if os.path.exists(curr_f):
        shutil.rmtree(curr_f)
    if os.path.exists(latest_f):
        shutil.rmtree(latest_f)

    os.makedirs(curr_f)

    if not os.path.exists(rx_sweep_data_folder):
        os.makedirs(rx_sweep_data_folder)

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d) if '.' in f]


def ExitFolderRename ():
    curr_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'current'])
    latest_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'latest'])
    ts=time.strftime("%Y%m%d_%H%M%S", time.localtime())
    final_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:] + ['results', ts + '_RF_TESTBENCH_TestReport'])
    rx_sweep_data_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'rx_sweep_datasets'])

    # Rename test result folder before exiting
    if os.path.isdir(latest_f):
        rf_cf.remove_dir(latest_f)
    if os.path.isdir(curr_f):
        shutil.copytree(curr_f, latest_f)

        files = os.listdir(curr_f)
        for file in files:
            if '.csv' in file and 'TestReport' not in file:
                filsrc = os.path.join(curr_f,file)
                filedest = os.path.join(rx_sweep_data_f,file)
                shutil.copyfile(filsrc,filedest)
        os.rename(curr_f, final_f)


def runTestExternal(testType="per_cl", branch="", variant=""):

    use_special_xml = 0

    p=re.compile(r'.*pl1_dev.br')
    if p.match(branch):
        print "pl1_dev.br under test, will check the variant"
        if variant =='nvidia-p2341-win7_internal':
            print "Lara variant detected, will use xml file specific for pl1_dev"
            use_special_xml = 1
        else:
            print "Non Lara variant %s, will use default xml configuration file" %variant
    else:
        print "branch %s under test, will use default xml configuration file" %branch


    valid_testTypes_dict = {'PER_CL':1, 'NIGHTLY':1, 'WEEKLY':1 }
    res_str = rf_global.verdict_dict[rf_global.PASS]

    RemoveOldFolders()

    try:
        dummyVal = valid_testTypes_dict[testType.upper()]
    except KeyError:
        print "testType %s not supported" %testType
        print "testType supported list is %s" %valid_testTypes_dict.keys()
        return

    if testType.upper() == "PER_CL":

        if use_special_xml:

            test_config_xml_path  = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['test_config_pl1_dev_per_cl.xml'])

        else:

            test_config_xml_path  = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['test_config_per_cl.xml'])

    elif testType.upper() == "NIGHTLY":

        test_config_xml_path  = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['test_config_nightly.xml'])

    elif testType.upper() == "WEEKLY":

        test_config_xml_path  = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['test_config_weekly.xml'])

    print test_config_xml_path

    if os.path.isfile(test_config_xml_path):

        param = get_params_from_xml(xml_file=test_config_xml_path)

    else:
        print "%s cannot be found!" %test_config_xml_path
        return

    results = OrderedDict()
    testexec = OrderedDict()

    for test_sel in param.test_selection_list:
        param.test_selection = test_sel
        rftb = rf_testbench(param_s = param)

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        test_res_str,results[test_sel],testexec[test_sel] = rftb.runTest()

        if test_res_str != rf_global.verdict_dict[rf_global.PASS]:
            res_str = test_res_str

    ExitFolderRename()

    #print overall verdicts
    rftb.print_pass_fail_list(results,testexec)

    return res_str


def get_params_from_xml(xml_file=""):

    class Struct():
        pass

    param = Struct()

    print "Local test config xml file for RF factory test parameters : %s" %xml_file
    tree = parse(xml_file)
    rf = tree.find('rf')

    print "Reading test configuration from %s" %xml_file

    param.log                 = rf.find('log').text
    param.instr_name          = rf.find('instr_name').text
    param.instr_ip            = rf.find('instr_ip').text
    param.instr_gpib          = rf.find('instr_gpib').text
    param.test_selection_list = rf.find('test_selection').text.split(',')
    param.psugwip             = rf.find('psugwip').text
    param.psugpib             = rf.find('psugpib').text
    param.psuvolt             = rf.find('psuvolt').text
    param.cable_loss          = rf.find('cable_loss').text

    return param


if __name__ == '__main__':

    class Struct():
        pass

    param = Struct()

    RemoveOldFolders()

    test_config_xml_path  = os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['test_config.xml'])

    res_str = rf_global.verdict_dict[rf_global.PASS]

    if os.path.isfile(test_config_xml_path):
        print "Test config xml file is chosen : %s" %test_config_xml_path
        tree = parse(test_config_xml_path)
        mapping = {}
        rf = tree.find('rf')

        print "Reading test configuration from %s" %test_config_xml_path

        param.log                 = rf.find('log').text
        param.instr_name          = rf.find('instr_name').text
        param.instr_ip            = rf.find('instr_ip').text
        param.instr_gpib          = rf.find('instr_gpib').text
        param.test_selection_list = [x.strip() for x in rf.find('test_selection').text.split(',')]
        param.psugwip             = rf.find('psugwip').text
        param.psugpib             = rf.find('psugpib').text
        param.psuvolt             = rf.find('psuvolt').text
        param.cable_loss          = rf.find('cable_loss').text

    else:

        # parse input parameters
        description_msg="""
        Start the wcdma test bench for PL1 branch validation. Instrument(CMW or CMU) IP is required. Example: python runTest -log=INFO -test2execute=[0] -instr_ip=x.y.z
        """

        parser=argparse.ArgumentParser(description=description_msg)
        parser.add_argument("-log", type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO', help="Define logging level. Default='DEBUG'" )
        parser.add_argument("-cmd", type=str, choices=['testlist'], help="testlist : Retrieve the list of testIDs available" )
        parser.add_argument("-instr_name", type=str, default='CMU200', help='supported instrument types CMU200, CMW500' )
        parser.add_argument("-instr_ip", type=str, default='ww.xx.yy.zz', help='instrument IP address, specify -instr_gpib if cmu' )
        parser.add_argument("-instr_gpib", type=str, default='20,1', help='CMU200 GPIB port. Default=20,1' )
        parser.add_argument("-cable_loss", type=str, default='0.5', help='RF cable loss in dB. Default=0.5' )
        parser.add_argument("-test_selection", type=str, default='Jenkins', help="Test selection to run. Default=Jenkins")
        parser.add_argument("-psugwip", type=str, default='ww.xx.yy.zz', help='PSU Gateway IP address' )
        parser.add_argument("-psugpib", type=int, default='0', help='PSU GPIB port. Default=0' )
        parser.add_argument("-psuvolt", type=int, default='0', help='PSU Voltage. Default=0' )


        args=parser.parse_args()

        param.log = args.log
        param.instr_name = args.instr_name
        param.instr_ip = args.instr_ip
        param.instr_gpib = args.instr_gpib
        param.test_selection_list = args.test_selection.split(',')
        param.psugwip = args.psugwip
        param.psugpib = args.psugpib
        param.psuvolt = args.psuvolt
        param.cable_loss = args.cable_loss

    results = OrderedDict()
    testexec = OrderedDict()


    for test_sel in param.test_selection_list:
        param.test_selection = test_sel
        rftb = rf_testbench(param_s = param)

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        test_res_str,results[test_sel],testexec[test_sel] = rftb.runTest()

        if test_res_str != rf_global.verdict_dict[rf_global.PASS]:
            res_str = test_res_str

    ExitFolderRename()

    #print overall verdicts
    rftb.print_pass_fail_list(results,testexec)

    print ("\nTEST STATUS : (%s)\n" % res_str)

