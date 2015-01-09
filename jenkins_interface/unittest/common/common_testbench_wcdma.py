#-------------------------------------------------------------------------------
# Name:        common_testbench_wcdma
# Purpose:
#
# Author:      joashr
#
# Created:     01/10/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os


(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2]+['test_system'])
sys.path.append(test_env_dir)

import test_env
import unittest

from pl1_testbench_framework.jenkins_interface.unittest.common.common_testbench import common_testbench
from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath


def setUpModule():

    # get environment variable for wcdma
    try:
        os.environ['PL1_WCDMA_TEST_ROOT']
    except KeyError:
        os.environ['PL1_WCDMA_TEST_ROOT'] = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma'])
        print "os.environ['PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']


def tearDown(self):

    pass

class common_testbench_wcdma(common_testbench):
    @classmethod
    def setUpClass(cls):

        cls.results_dir = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])

        cls.summaryFile = os.sep.join(cls.results_dir.split(os.sep)[:]+['WCDMA_CMW500_TestReport_SUMMARY.csv'])

        if sys.platform in ['cygwin', 'win32']:
            
            cls.latest_f = os.sep.join(os.environ['TEST_ROOT_FOLDER'].split(os.sep)[:]+['pl1_jenkins', 'test_system', 'results', 'latest'])
            
        else:
            
            cls.latest_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'linux', 'results', 'latest'])

        cls.rm_old_results_files(results_dir=cls.latest_f)

        cls.rat = "wcdma"

        cls.get_test_params()

        cls.subtest_results_f =""


    def execute_testbench(self, testID=""):
        result = 1

        AddSysPath(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]))
        from runTest import wcdma_pl1testbench
        self._set_test2execute(test_plan_ID=testID)
        wcdma = wcdma_pl1testbench(param_s = self.param_s)
        result = wcdma.runTest()
        self.subtest_results_f=os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'latest'])
        return result


    def _set_test2execute(self, test_plan_ID):

        self.param_s.test2execute = str(test_plan_ID)


if __name__ == '__main__':
    pass
