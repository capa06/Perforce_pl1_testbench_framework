
# Author:      joashr
#
# Created:     28/11/2013
#


import os, sys, traceback

'''
try:
    import pl1_wcdma_testbench.test_env
except ImportError:
    (abs_path, name)=os.path.split(os.path.abspath(__file__))
    os.environ['PL1_WCDMA_TEST_ROOT'] = os.sep.join(abs_path.split(os.sep)[:-2])
    print "os.environ['PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']
    sys.path.append(os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]))
    import pl1_wcdma_testbench.test_env
'''

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


from test_plan import test_plan


class cfg_test(object):

    def __init__(self, testID):
        '''
        Constructor
        '''
        keys = test_plan.keys()

        if testID in keys:
            self.testID        = testID
            self.testtype      = test_plan[testID]['TESTTYPE']
            self.datarate      = test_plan[testID]['DATARATE']
            self.rfband        = test_plan[testID]['RFBAND']
            self.uarfcn_dic    = test_plan[testID]['UARFCN' ]
            self.chtype        = test_plan[testID]['CHTYPE']
            self.snr           = test_plan[testID]['SNR']
            self.rfpower       = test_plan[testID]['RFPOWER']
            self.txants        = test_plan[testID]['TXANTS' ]
            self.modeminfo     = ""
            self.cmwinfo       = ""

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
        print "modeminfo     : %s"    %self.modeminfo
        print "cmwinfo       : %s"    %self.cmwinfo
        print "--------------------------------------"
        return ""

    def set_modeminfo(self, modeminfo=""):
        self.modeminfo = modeminfo

    def set_cmwinfo(self, cmwinfo=""):
        self.cmwinfo = cmwinfo


    def set_total_test_steps(self):
        nsteps = 0
        num_rfbands = len(self.rfband)
        #num_uarfcn = GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_uarfcn = self.GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_chtype = len(self.chtype)
        num_snr = len(self.snr)
        num_datarate = len(self.datarate)

        totalsteps = num_rfbands * num_uarfcn * num_chtype * num_snr * num_datarate
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

    #import pl1_jenkins.common.modem as modem
    import pl1_testbench_framework.common.com.modem as modem


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
        testID=int(testID)
        curr_test_testtype = test_plan[testID]['TESTTYPE']
        if curr_test_testtype == 'BLER_PERF':
            curr_test = cfg_test(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test

        elif curr_test_testtype == 'HSPA_FADING_PERF':
            curr_test = cfg_test(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test
