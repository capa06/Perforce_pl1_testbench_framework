
# Author:      joashr
#
# Created:     27/01/2014
#
#

from test_plan import test_plan

from cfg_test import cfg_test

from cfg_test_hspa import cfg_test_hspa


class cfg_test_dc_hsdpa(cfg_test):

    def __init__(self, testID):
        '''
        Constructor
        '''
        keys = test_plan.keys()

        if testID in keys:
            self.testID               = testID
            self.testtype             = test_plan[testID]['TESTTYPE']
            self.datarate             = test_plan[testID]['DATARATE']
            self.rfband               = test_plan[testID]['RFBAND']
            self.uarfcn_dic           = test_plan[testID]['UARFCN' ]
            self.chtype               = test_plan[testID]['CHTYPE']
            self.snr_1                = test_plan[testID]['SNR_1']
            self.snr_2                = test_plan[testID]['SNR_2']
            self.rfpower_1            = test_plan[testID]['RFPOWER_1']
            self.rfpower_2            = test_plan[testID]['RFPOWER_2']
            self.txants               = test_plan[testID]['TXANTS' ]
            self.schedtype            = test_plan[testID]['SCHEDTYPE']
            self.inter_tti_1          = test_plan[testID]['INTER_TTI_1']
            self.inter_tti_2          = test_plan[testID]['INTER_TTI_2']
            self.num_harq_proc        = test_plan[testID]['NUM_HARQ_PROC']
            self.ki_1                 = test_plan[testID]['Ki_1']
            self.ki_2                 = test_plan[testID]['Ki_2']
            self.num_hsdsch_codes_1   = test_plan[testID]['NUM_HSDSCH_CODES_1']
            self.num_hsdsch_codes_2   = test_plan[testID]['NUM_HSDSCH_CODES_2']
            self.modulation_1         = test_plan[testID]['MODULATION_1' ]
            self.modulation_2         = test_plan[testID]['MODULATION_2' ]


            self.modeminfo     = ""

            self.totalsteps    = self.set_total_test_steps()

        else:
            raise TypeError("ERROR: Invalid CMW Test Index")

    def __str__(self):
        print "--------------------------------------"
        print "testID               : %s"    %self.testID
        print "testtype             : %s"    %self.testtype
        print "datarate             : %s"    %self.datarate
        print "rfband               : %s"    %self.rfband
        print "uarfcn               : %s"    %self.uarfcn_dic
        print "chtype               : %s"    %self.chtype
        print "snr_1                : %s"    %self.snr_1
        print "snr_2                : %s"    %self.snr_2
        print "rfpower_1            : %s"    %self.rfpower_1
        print "rfpower_2            : %s"    %self.rfpower_2
        print "txants               : %s"    %self.txants
        print "totalsteps           : %s"    %self.totalsteps
        print "schedtype            : %s"    %self.schedtype
        print "inter tti_1          : %s"    %self.inter_tti_1
        print "inter tti_2          : %s"    %self.inter_tti_2
        print "num Harq Proc        : %s"    %self.num_harq_proc
        print "ki_1                 : %s"    %self.ki_1
        print "ki_2                 : %s"    %self.ki_2
        print "num HS codes carr 1  : %s"    %self.num_hsdsch_codes_1
        print "num HS codes carr 2  : %s"    %self.num_hsdsch_codes_2
        print "modulation_1         : %s"    %self.modulation_1
        print "modulation_2         : %s"    %self.modulation_2

        print "modeminfo     : %s"    %self.modeminfo
        print "--------------------------------------"
        return ""

    def set_modeminfo(self, modeminfo=""):
        self.modeminfo = modeminfo

    def check_array_sizes_are_equal(self):
        assert self.snr_1 == self.snr_2, 'snr_1 and snr_2 should have equal size'
        assert self.rfpower_1 == self.rfpower_2, 'snr_1 and snr_2 should have equal size'
        assert self.inter_tti_1 == self.inter_tti_2, 'inter_tti_1 and inter_tti_2 should have equal size!'
        assert self.ki_1 == self.ki_2, 'ki_1 and ki_2 should have equal size'
        assert self.num_hsdsch_codes_1 == self.num_hsdsch_codes_2, 'arrays should have equal size'
        assert self.modulation_1 == self.modulation_2, 'arrays should have equal size'

    def set_total_test_steps(self):
        nsteps = 0
        self.check_array_sizes_are_equal()
        num_rfbands = len(self.rfband)
        num_uarfcn = self.GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_chtype = len(self.chtype)
        num_snr = len(self.snr_1)

        num_modulationLoops = len(self.modulation_1)
        num_hsdsch_codesLoops = len(self.num_hsdsch_codes_1)
        numKiLoops = len(self.ki_1)

        totalstepsInitMult = num_rfbands * num_uarfcn * num_chtype * num_snr
        totalstepsHsdpa =  num_modulationLoops * num_hsdsch_codesLoops * numKiLoops
        totalsteps = totalstepsInitMult * totalstepsHsdpa
        return totalsteps

    def GetTotalStepsFromDictL1(self, dict_s):
        """
        Assumptions : dict_s = { <key> : [list of values] }
        return sum(len([list of value](j))) for j=1,..N
           where N is the total number of keys in the dictionary
        """
        totlen   = 0
        key_l = dict_s.keys()
        for key in key_l:
            totlen += len(dict_s[key])
        return totlen

    def get_total_test_steps(self):
        return (self.totalsteps)


if __name__ == '__main__':
    import os, sys
    (abs_path, name)=os.path.split(os.path.abspath(__file__))
    os.environ['PL1_WCDMA_TEST_ROOT'] = os.sep.join(abs_path.split(os.sep)[:-2])
    print "os.environ['PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']
    sys.path.append(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]))

    from addSystemPath import AddSysPath

    os.environ['TEST_SYSTEM_ROOT_FOLDER']  = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:-1]+['pl1_jenkins', 'test_system'])
    print "os.environ['TEST_SYSTEM_ROOT_FOLDER']=%s" % os.environ['TEST_SYSTEM_ROOT_FOLDER']
    AddSysPath(os.sep.join(os.environ['TEST_SYSTEM_ROOT_FOLDER'].split(os.sep)[:]))
    from test_env import set_test_search_paths as set_jenkins_search_paths
    set_jenkins_search_paths()

    from modem import *

    modeminfo=""

    """
    modemObj = serialComms(timeout = 2)
    modeminfo=modemObj.getInfo()
    modemObj.close()
    """


    """
    from test_plan import test_plan

    curr_test=cfg_test(testID)


    if curr_test.testtype == 'BLER_PERF':
    """

    testID_list = sorted(test_plan.keys())
    #testID_list=[1]


    for testID in testID_list:
        #curr_test = cfg_test(testID)
        cur_test_testtype = test_plan[testID]['TESTTYPE']


        if cur_test_testtype == 'BLER_PERF':
            curr_test = cfg_test(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            #print curr_test


        elif cur_test_testtype == 'HSPA_BLER_PERF':
            curr_test = cfg_test_hspa(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            #print curr_test
            for modulation in curr_test.modulation:
                print modulation


        elif cur_test_testtype == 'DCHSDPA_BLER_PERF':
            curr_test = cfg_test_dc_hsdpa(testID)
            rfpower_zip =  zip(curr_test.rfpower_1, curr_test.rfpower_2)
            for (rfpower_1, rfpower_2) in rfpower_zip:
                print rfpower_1, rfpower_2
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test
