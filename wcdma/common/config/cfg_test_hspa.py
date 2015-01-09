
# Author:      joashr
#
# Created:     20/01/2014
#
# Adapted from fsaracino 11 Jul 2013

from test_plan import test_plan

from cfg_test import cfg_test


class cfg_test_hspa(cfg_test):

    def __init__(self, testID):
        '''
        Constructor
        '''
        keys = test_plan.keys()

        if testID in keys:
            self.testID           = testID
            self.testtype         = test_plan[testID]['TESTTYPE']
            self.datarate         = test_plan[testID]['DATARATE']
            self.rfband           = test_plan[testID]['RFBAND']
            self.uarfcn_dic       = test_plan[testID]['UARFCN' ]
            self.chtype           = test_plan[testID]['CHTYPE']
            self.snr              = test_plan[testID]['SNR']
            self.rfpower          = test_plan[testID]['RFPOWER']
            self.txants           = test_plan[testID]['TXANTS' ]
            self.schedtype        = test_plan[testID]['SCHEDTYPE']
            self.inter_tti        = test_plan[testID]['INTER_TTI']
            self.num_harq_proc    = test_plan[testID]['NUM_HARQ_PROC']
            self.ki               = test_plan[testID]['Ki']
            self.num_hsdsch_codes = test_plan[testID]['NUM_HSDSCH_CODES']
            self.modulation       = test_plan[testID]['MODULATION' ]

            self.modeminfo     = ""

            self.totalsteps    = self.set_total_test_steps()

        else:
            raise TypeError("ERROR: Invalid CMW Test Index")

    def __str__(self):
        print "--------------------------------------"
        print "testID        : %s"    %self.testID
        print "testtype      : %s"    %self.testtype
        print "datarate      : %s"    %self.datarate
        print "rfband        : %s"    %self.rfband
        print "uarfcn        : %s"    %self.uarfcn_dic
        print "chtype        : %s"    %self.chtype
        print "snr           : %s"    %self.snr
        print "rfpower       : %s"    %self.rfpower
        print "txants        : %s"    %self.txants
        print "totalsteps    : %s"    %self.totalsteps
        print "schedtype     : %s"    %self.schedtype
        print "inter tti     : %s"    %self.inter_tti
        print "num Harq Proc : %s"    %self.num_harq_proc
        print "ki            : %s"    %self.ki
        print "num HS codes  : %s"    %self.num_hsdsch_codes
        print "modulation    : %s"    %self.modulation

        print "modeminfo     : %s"    %self.modeminfo
        print "--------------------------------------"
        return ""

    def set_modeminfo(self, modeminfo=""):
        self.modeminfo = modeminfo


    def set_total_test_steps(self):
        nsteps = 0
        num_rfbands = len(self.rfband)
        #num_uarfcn = GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_uarfcn = self.GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_chtype = len(self.chtype)
        num_snr = len(self.snr)

        num_modulationLoops = len(self.modulation)
        num_hsdsch_codesLoops = len(self.num_hsdsch_codes)
        numKiLoops = len(self.ki)

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
        testID=int(testID)
        curr_test_testtype = test_plan[testID]['TESTTYPE']

        """
        if curr_test_testtype == 'BLER_PERF':
            curr_test = cfg_test(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test
        """


        if curr_test_testtype == 'HSPA_BLER_PERF':
            curr_test = cfg_test_hspa(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test
            for modulation in curr_test.modulation:
                print modulation
