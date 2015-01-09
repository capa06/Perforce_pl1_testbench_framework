#-------------------------------------------------------------------------------
# Name:        test_wcdma_per_cl
# Purpose:
#
# Author:      joashr
#
# Created:     10/09/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, subprocess, argparse, logging, re, shutil, time

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


import unittest

from xml.etree.ElementTree import parse

from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath

from pl1_testbench_framework.jenkins_interface.unittest.common.common_testbench import common_testbench


def setUpModule():

    # get environment variable for wcdma
    try:
        os.environ['PL1_WCDMA_TEST_ROOT']
    except KeyError:
        os.environ['PL1TESTBENCH_ROOT_FOLDER']
        os.environ['PL1_WCDMA_TEST_ROOT'] = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma'])
        print "os.environ['PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']


def tearDown(self):

    pass


class pl1_wcdma_testbench(common_testbench):

    @classmethod
    def setUpClass(cls):
        
        import sys

        cls.results_dir = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])

        cls.summaryFile = os.sep.join(cls.results_dir.split(os.sep)[:]+['WCDMA_CMW500_TestReport_SUMMARY.csv'])

        if sys.platform in ['cygwin', 'win32']:
            
            cls.latest_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'win8', 'test_system', 'results', 'latest'])
            
        else:
            
            cls.latest_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'linux', 'results', 'latest'])

        cls.rm_old_results_files(results_dir=cls.latest_f)

        cls.rat = "wcdma"

        cls.get_test_params()

        cls.subtest_results_f =""


    @classmethod
    def get_test_params(cls):

        test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma_test_config_per_cl.xml'])

        class Struct():
            pass

        if os.path.isfile(test_config_xml_path):

            print "Test config xml file is chosen : %s" %test_config_xml_path
            tree = parse(test_config_xml_path)
            mapping = {}
            xml = tree.find('wcdma')
            cls.param_s=Struct()

            cls.param_s.log           = xml.find('log').text # logging level
            cls.param_s.cmwip         = xml.find('cmwip').text
            if cls.param_s.cmwip ==  "x.y.w.z":
                raise KeyboardInterrupt("setup test failure, specify a valid CMW500 IP address!")
            cls.param_s.ctrlif        = xml.find('ctrlif').text
            cls.param_s.pwrmeas       = int(xml.find('pwrmeas').text)
            cls.param_s.usimemu       = int(xml.find('usimemu').text)
            cls.param_s.psugwip       = xml.find('psugwip').text
            cls.param_s.psugpib       = xml.find('psugpib').text
            cls.param_s.msglog        = int(xml.find('msglog').text)

            database           = xml.find('database').text
            try:
                remoteDB       = int(xml.find('remoteDB').text)
            except:
                remoteDB = 0

            remoteDBhost       = xml.find('remoteDBhost').text
            remoteDBuid        = xml.find('remoteDBuid').text

            try:
                remoteDBpwd    = '%s' %unicode(xml.find('remoteDBpwd').text, ('unicode-escape')).encode('latin-1')
            except:
                remoteDBpwd    = None

            remoteDBname       = xml.find('remoteDBname').text

            cls.param_s.database      = None if database=='' else database
            cls.param_s.remoteDB      = remoteDB
            cls.param_s.remoteDBhost  = None if remoteDBhost=='' else remoteDBhost
            cls.param_s.remoteDBuid   = None if remoteDBuid=='' else remoteDBuid
            cls.param_s.remoteDBpwd   = None if remoteDBpwd=='' else remoteDBpwd
            cls.param_s.remoteDBname  = None if remoteDBname=='' else  remoteDBname


        else:
            raise KeyboardInterrupt("No valid config file found. Expecting %s" %test_config_xml_path)



    def setUp(self):
        # occurs after setUpClass and prior to the start
        # of each test
        self.orig_sys_path = sys.path
        
        for handler in logging.root.handlers[:]:

            logging.root.removeHandler(handler)


    def tearDown(self):

        sys.path = self.orig_sys_path

        self.copy_results_to_latest_f()


    def _set_test2execute(self, test_plan_ID):

        self.param_s.test2execute = str(test_plan_ID)
        self.param_s.unittest = 1


    def test_wcdma_0_per_cl_test(self):
        """
        12.2, 64k, 144k, 384k bler test
        testtype - BLER_PERF
        """

        res = self.execute_testbench(testID=0)

        self.failIf(res != 0, "Test failure")

    def test_wcdma_1_per_cl_test(self):
        """
        HSDPA bler test
        testtype - HSPA_BLER_PERF
        """
        res = self.execute_testbench(testID=1)

        self.failIf(res != 0, "Test failure")

    def test_wcdma_2_per_cl_test(self):
        """
        DC-HSDPA bler test
        testtype - DCHSDPA_BLER_PERF
        """

        res = self.execute_testbench(testID=2)

        self.failIf(res != 0, "Test failure")

    def test_wcdma_202_per_cl_test(self):
        """
        Light Intra HHO test case
        testtype - BLER_INTRAHO_DEFAULT
        """

        res = self.execute_testbench(testID=202)

        self.failIf(res != 0, "Test failure")


    @unittest.skip('skip due to R&S issue tracking 424486')
    def test_wcdma_220_per_cl_test(self):
        """
        Light InterBand HHO test case
        testtype - BLER_INTERBAND_DEFAULT
        """

        res = self.execute_testbench(testID=220)

        self.failIf(res != 0, "Test failure")

    def execute_testbench(self, testID=""):
        result = 1

        AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]))
        from runTest import wcdma_pl1testbench
        self._set_test2execute(test_plan_ID=testID)
        wcdma = wcdma_pl1testbench(param_s = self.param_s)
        result = wcdma.runTest()
        self.subtest_results_f=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])
        return result


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(pl1_wcdma_testbench)
    unittest.TextTestRunner(verbosity=2).run(suite)
    pass

