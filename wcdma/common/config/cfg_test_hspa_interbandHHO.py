
# Author:      joashr
#
# Created:     13/10/2014
#
#

import os, sys, traceback


try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


from pl1_testbench_framework.wcdma.common.config.umts_utilities import min_dl_UARFCN, max_dl_UARFCN, default_dl_uarfcn

#import pl1_testbench_framework.common.com.modem as modem

from pl1_testbench_framework.wcdma.common.com.custom_modem import custom_modem

from test_plan import test_plan

from cfg_test import cfg_test


class cfg_test_hspa_interbandHHO(cfg_test):

    SUCCESS = 0

    def __init__(self, testID):
        '''
        Constructor
        '''
        keys = test_plan.keys()

        if testID in keys:
            self.testID           = testID
            self.testtype         = test_plan[testID]['TESTTYPE']
            self.datarate         = test_plan[testID]['DATARATE']
            #self.rfband           = test_plan[testID]['RFBAND']
            self.rfband           = self.get_rf_band_list(requestedBandList=test_plan[testID]['RFBAND'])
            self.uarfcn_dic       = self.get_uarfcn_dict(bandList=self.rfband)
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

    def get_rf_band_list(self, requestedBandList):

        supportedBandList = []

        try:
            #modemObj = modem.serialComms(timeout=2)
            modemObj = custom_modem(timeout=2)
            (res, dummy) = modemObj.enable_all_bands(rat="wcdma")
            if res == self.SUCCESS:
                supportedBandList = modemObj.get_supported_band_list(rat="wcdma")
            else:
                print ("AT command to enable all bands for %s has failed" %"wcdma")
        except:
            print traceback.format_exc()
            print "Not able to query modem"

        if modemObj:
            modemObj.close()

        unique = []
        [unique.append(band) for band in requestedBandList if band not in unique]
        new_requestedBandList = unique

        if len(new_requestedBandList) > len(supportedBandList):

            print "The number of requested bands %s" %new_requestedBandList
            print "is greater than the number of supported bands %s" %supportedBandList
            print "will default to the supported bands"
            return supportedBandList

        selectedBandList = []
        [selectedBandList.append(band) for band in new_requestedBandList if band in supportedBandList]
        if selectedBandList:
            if len(selectedBandList) == len(new_requestedBandList):
                # ok all the bands requested are supported
                return selectedBandList
            else:
                # not all the requested bands are supported
                print "bands requested %s" %new_requestedBandList
                print "bands supported %s" %supportedBandList
                print "restricted bands selected %s" %selectedBandList
                return selectedBandList
        else:
            print "None of the requested bands %s are supported" %selectedBandList
            print "will default to the supported bands"

        return supportedBandList

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

    def get_uarfcn_dict(self, bandList):

        # always ensure that HHO finishes on the original starting band
        if len(bandList) > 1 :
            bandList.append(bandList[0])

        desc_l = ['BOT','TOP']

        x = 0
        band_desc_uarfcn_l = []
        uarfcn_dict = {}
        tuple_val = ()

        for band in bandList:

            band_desc=desc_l[x % 2]

            if band_desc == 'BOT':
                #print "Bottom UARFCN for band %s" % band
                uarfcn = min_dl_UARFCN(band=band)
                #print uarfcn
            elif band_desc == 'TOP':
                #print "Top UARFCN for band %s" % band
                uarfcn = max_dl_UARFCN(band=band)
                #print uarfcn
            elif band_desc == 'MID':
                #print "Mid UARFCN for band %s" % band
                uarfcn = default_dl_uarfcn(band=band)
                #print uarfcn

            tuple_val = (band, band_desc, uarfcn)

            band_desc_uarfcn_l.append(tuple_val)

            uarfcn_dict[band] = uarfcn

            x = x + 1

        self.set_band_desc_uarfcn_tuple(tuple_list=band_desc_uarfcn_l)

        '''
        for key in sorted(uarfcn_dict.keys()):

            print "%s = > %s" % (key, uarfcn_dict[key])
        '''

        print "Bands to be tested"

        for (band, descr, uarfcn) in self.get_band_desc_uarfcn_tuple():

            print "%s(%s) = > %s" % (band, descr, uarfcn)

        return uarfcn_dict

    def set_band_desc_uarfcn_tuple(self, tuple_list):

        self.band_desc_uarfcn_tuple= tuple_list

    def get_band_desc_uarfcn_tuple(self):

        return self.band_desc_uarfcn_tuple


    def create_uarfcn_dict(self, band_desc_l):

        uarfcn_dict = {}

        for band_desc in band_desc_l:

            (band, desc) = band_desc

            if desc.upper() == 'TOP':

                uarfcn = max_dl_UARFCN(band=band)

            elif desc.upper() == 'BOT':

                uarfcn = min_dl_UARFCN(band=band)

            elif desc.upper() == 'MID':

                uarfcn = default_dl_uarfcn(band=band)

            uarfcn_dict[band] = uarfcn

        for key in sorted(uarfcn_dict.keys()):

            print "%s = > %s" % (key, uarfcn_dict[key])

    def set_modeminfo(self, modeminfo=""):
        self.modeminfo = modeminfo


    def set_total_test_steps(self):
        nsteps = 0
        num_rfbands = len(self.rfband)
        num_uarfcn = len(self.uarfcn_dic.keys())
        num_chtype = len(self.chtype)
        num_snr = len(self.snr)

        num_modulationLoops = len(self.modulation)
        num_hsdsch_codesLoops = len(self.num_hsdsch_codes)
        numKiLoops = len(self.ki)

        totalstepsInitMult = num_uarfcn * num_chtype * num_snr
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

    import logging

    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)


    testID_list = sorted(test_plan.keys())


    for testID in testID_list:

        testID=int(testID)
        curr_test_testtype = test_plan[testID]['TESTTYPE']



        if curr_test_testtype == 'BLER_INTERBAND_DEFAULT':
            curr_test = cfg_test_hspa_interbandHHO(testID)
            #curr_test.set_modeminfo(modeminfo=modeminfo)
            print curr_test
            for modulation in curr_test.modulation:
                print modulation
