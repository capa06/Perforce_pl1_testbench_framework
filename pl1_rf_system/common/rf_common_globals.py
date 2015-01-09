#-------------------------------------------------------------------------------
# Name:        rf system test common_globals.py
# Purpose:
#
# Author:      joashr
#
# Created:     16/05/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

FACTORY_TEST_MODE = 2
NORMAL_TEST_MODE = 0

PASS    = 1
FAIL    = 0
INCONC  = 2

verdict_dict = {FAIL:'FAIL', PASS:'PASS', INCONC:'INCONCLUSIVE'}

testSummaryFileName = 'RF_FACTORY_TestReport_SUMMARY.csv'