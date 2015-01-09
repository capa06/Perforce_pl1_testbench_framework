'''
Created on 11 Jul 2013

@author: fsaracino
'''

class cfg_testbler(object):
    """
    Derived data structure holding the BLER test parameter
    """
    def __init__(self, conf, test):
        # conf
        self.cmwip          = conf.cmwip
        self.cmwname        = conf.cmwname
        self.ctrlif         = conf.ctrlif
        self.simulate_usim  = conf.usimemu
        # test
        self.testID         = test.testID
        self.testtype       = test.testtype
        self.datarate       = test.datarate
        self.rfband         = test.rfband
        self.uarfcn         = test.uarfcn
        self.chtype         = test.chtype
        self.snr            = test.snr
        self.rfpower        = test.rfpower
        self.txants         = test.txants
        self.totalsteps     = test.get_total_test_steps()


    def __str__(self):
        print "--------------------------------------"
        print "Config:"
        print "  cmwip         : %s" % self.cmwip
        print "  cmwname       : %s" % self.cmwname
        print "  ctrlif        : %s" % self.ctrlif
        print "  simulate usim : %s" % self.simulate_usim
        print "Test plan parameters"
        print "  testID        : %s" % self.testID
        print "  testtype      : %s" % self.testtype
        print "  datarate      : %s" % self.datarate
        print "  rfband        : %s" % self.rfband
        print "  uarfcn        : %s" % self.uarfcn
        print "  chtype        : %s" % self.chtype
        print "  snr           : %s" % self.snr
        print "  rfpower       : %s" % self.rfpower
        print "  txants        : %s" % self.txants
        print "  totalsteps    : %s" % self.totalsteps

        return ""

if __name__ == "__main__":
	pass

