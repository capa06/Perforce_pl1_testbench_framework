'''
Created on 1 Dec 2013

@author: joashr

Adapted from pl1testbench
'''

import re

import test_globals

class cfg_cmw(object):
    """
    Derived data structure holding the BLER test parameter
    """
    def __init__(self):
        # test
        self.testtype       = ""
        self.datarate       = ""
        self.rfband         = ""
        self.uarfcn         = ""
        self.chtype         = ""
        self.snr            = ""
        self.rfpower        = ""
        self.txants         = ""


    def set_data_rate(self, datarate):

        self.datarate = datarate

        return (self.check_data_rate())

    def check_data_rate(self):

        """
        check that the date rate is supported by the cmw tester
        returns 1 if supported, otherwise 0
        """
        check_pass = 1

        dl_rmc_dataRate_dic = dict.fromkeys(test_globals.dl_rmc_dataRate_list, 1)
        ul_rmc_dataRate_dic = dict.fromkeys(test_globals.ul_rmc_dataRate_list, 1)

        matchObj = re.match('dl_(R.*)_ul_(R.*)', self.datarate, re.I)

        if matchObj:
            dl_rmc = matchObj.group(1)
            ul_rmc = matchObj.group(2)

            try:
                dl_rmc_dataRate_dic[dl_rmc.upper()]
            except KeyError:
                print "dl data rate %s is not supported from RMC rate selection %s" %(dl_rmc, self.datarate)
                print "supported rates are %s" %test_globals.dl_rmc_dataRate_list
                check_pass = 0

            try:
                ul_rmc_dataRate_dic[ul_rmc.upper()]
            except KeyError:
                print "ul data rate %s is not supported from RMC rate selection %s " %(ul_rmc, self.datarate)
                print "supported rates are %s" %test_globals.ul_rmc_dataRate_list
                check_pass = 0

        else:
            print "RMC data rate %s is not supported" %self.datarate
            print "or the data rate is in the wrong format!"
            print "supported RMC rates are"
            for dl_rmc_rate in test_globals.dl_rmc_dataRate_list:
                for ul_rmc_rate in test_globals.ul_rmc_dataRate_list:
                    print "dl_%s_ul_%s" %(dl_rmc_rate, ul_rmc_rate)
            check_pass = 0

        return check_pass

    def get_data_rate(self):

        return self.datarate

    def set_rf_band(self, rfband):

        self.rfband = rfband

    def get_rf_band(self):

        return self.rfband

    def set_rf_power(self, rfpower):

        self.rfpower = rfpower

    def get_rf_power(self):

        return self.rfpower

    def set_snr(self, snr):

        self.snr = snr

    def get_snr(self):

        return self.snr

    def set_uarfcn(self, uarfcn):

        self.uarfcn = uarfcn

    def get_uarfcn(self):

        return self.uarfcn


    def __str__(self):
        print "--------------------------------------"
        print "  testtype      : %s" % self.testtype
        print "  datarate      : %s" % self.datarate
        print "  rfband        : %s" % self.rfband
        print "  uarfcn        : %s" % self.uarfcn
        print "  chtype        : %s" % self.chtype
        print "  snr           : %s" % self.snr
        print "  rfpower       : %s" % self.rfpower
        print "  txants        : %s" % self.txants

        return ""



if __name__ == "__main__":

    cmw_conf = cfg_cmw()

    cmw_conf.set_data_rate("dl_R384k_ul_R64K")





