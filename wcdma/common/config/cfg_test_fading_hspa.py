
# Author:      joashr
#
# Created:     20/01/2014
#

from test_plan import test_plan

from cfg_test import cfg_test


class cfg_test_fading_hspa(cfg_test):

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
            self.cpich_power      = test_plan[testID]['CPICH_POWER']
            self.hs_pdsch_power   = test_plan[testID]['HSPDSCH_POWER']

            self.modeminfo     = ""

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
        print "totalsteps    : %s"    %self.get_total_test_steps()
        print "schedtype     : %s"    %self.schedtype
        print "inter tti     : %s"    %self.inter_tti
        print "num Harq Proc : %s"    %self.num_harq_proc
        print "cpich power   : %s"    %self.cpich_power
        print "hs pdsch power: %s"    %self.hs_pdsch_power

        print "modeminfo     : %s"    %self.modeminfo
        print "--------------------------------------"
        return ""

    def set_modeminfo(self, modeminfo=""):
        self.modeminfo = modeminfo


    def set_rf_band_list(self, bandList):

        self.rfband = bandList


    def get_dict_from_uarfcn_dict(self, rfbandList):
        newDict = {}
        for band in rfbandList:
            newDict[band]=self.uarfcn_dic[band]
        return newDict

    def set_uarcn_dict(self, uarfcn_dict):
        self.uarfcn_dic = uarfcn_dict

    def get_total_test_steps(self):
        nsteps = 0
        num_rfbands = len(self.rfband)
        #num_uarfcn = GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_uarfcn = self.GetTotalStepsFromDictL1(dict_s = self.uarfcn_dic)
        num_chtype = len(self.chtype)
        num_snr = len(self.snr)

        num_cpich_loop = len(self.cpich_power)
        num_hspdsch_loop = len(self.hs_pdsch_power)
        totalstepsInitMult = num_uarfcn * num_chtype * num_snr
        totalstepsHsdpa =  num_cpich_loop * num_hspdsch_loop
        totalsteps = totalstepsInitMult * totalstepsHsdpa
        #self.totalsteps = totalsteps
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


if __name__ == '__main__':
    import os, sys
    (abs_path, name)=os.path.split(os.path.abspath(__file__))

    try:
        import test_env
    except ImportError:
        (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
        test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
        print test_env_dir
        sys.path.append(test_env_dir)
        import test_env


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
    from test_plan import test_plan
    testID_list = sorted(test_plan.keys())
    #testID_list=[1]


    for testID in testID_list:
        #curr_test = cfg_test(testID)
        testID=int(testID)
        print 'TestID %s' %testID
        curr_test_testtype = test_plan[testID]['TESTTYPE']


        if curr_test_testtype == 'HSPA_FADING_PERF':
            curr_test = cfg_test_fading_hspa(testID)
            curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test

