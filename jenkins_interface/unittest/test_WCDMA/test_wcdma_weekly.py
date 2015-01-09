#-------------------------------------------------------------------------------
# Name:        test_wcdma_weekly
# Purpose:     execute WCDMA weekly unittests
#
# Author:      joashr
#
# Created:     30/09/2014
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

from pl1_testbench_framework.jenkins_interface.unittest.common.common_testbench_wcdma import common_testbench_wcdma

class pl1_wcdma_testbench_weekly(common_testbench_wcdma):

    @classmethod
    def setUpClass(cls):

        import pl1_wcdma_testbench.wcdma_test_env

        cls.results_dir = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])

        cls.summaryFile = os.sep.join(cls.results_dir.split(os.sep)[:]+['WCDMA_CMW500_TestReport_SUMMARY.csv'])

        cls.latest_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'win8', 'test_system', 'results', 'latest'])

        cls.rm_old_results_files(results_dir=cls.latest_f)

        cls.rat = "wcdma"

        cls.get_test_params()

        cls.subtest_results_f =""

    @classmethod
    def get_test_params(cls):

        test_config_xml_path  = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['test_config_weekly.xml'])

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


    def test_wcdma_101_weekly(self):
        """ HSPA_FADING_PERF """

        res = self.execute_testbench(testID=101)

        self.failIf(res != 0, "Test failure")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(pl1_wcdma_testbench_weekly)
    unittest.TextTestRunner(verbosity=2).run(suite)
    pass
