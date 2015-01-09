#-------------------------------------------------------------------------------
# Name:        ber.py
# Purpose:
#
# Author:      joashr
#
# Created:     27/11/2013
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, logging

#import pl1_wcdma_testbench.test_env

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env

#from pl1_wcdma_testbench.common.config.cfg_error import cfg_error
from pl1_testbench_framework.common.config.CfgError import CfgError

#code = cfg_error()
code = CfgError

class ber:
    '''
    Class used as structure to gather ber stats from the CMW500
    '''

    def __init__(self):
        self.reliability      = "-1"
        self.ber              = "-1"
        self.bler             = "-1"
        self.dlbler           = "-1"
        self.lostblocks       = "-1"
        self.ultfci_faults    = "NCAP"   # not supported
        self.fdr              = "NCAP"   # false transmit detection ratio (not supported)
        self.PNDiscon         = "-1"     # number of  transport blocks  that the CMW
                                         # corrected (i.e. reordered) in the PN Resync
                                         # procedure

    def set_results_list(self, reading):
        '''
        set the results of the signaling BER mesaurement
        typically returned by 'READ:WCDMa:SIGN:BER?'
        '''
        self.reliability     = reading[0]
        self.ber             = reading[1]
        self.bler            = reading[2]
        self.dlbler          = reading[3]
        self.lostblocks      = reading[4]
        self.ultfci_faults   = reading[5]
        self.fdr             = reading[6]
        self.PNDiscon        = reading[7]

    def reset(self):

        self.__init__()

    def __str__(self):
        print "CMW500 bler stats:"
        print "-------------------"
        print "  reliability        : %s"   % self.reliability
        print "  ber                : %s"   % self.ber
        print "  bler               : %s"   % self.bler
        print "  dlbler             : %s"   % self.dlbler
        print "  lostblocks         : %s"   % self.lostblocks
        print "  ultfci_faults      : %s"   % self.ultfci_faults
        print "  FDR                : %s"   % self.fdr
        print "  PNDiscontinuity    : %s"   % self.PNDiscon

        return ""

    def get_list(self):
        meas_list=[]
        reliability = self.reliability
        ber ='%.2f' % float(self.ber)
        bler ='%.2f' % float(self.bler)
        dlbler ='%.2f' % float(self.dlbler)
        lostblocks = self.lostblocks
        PNDiscon = self.PNDiscon

        meas_list = [reliability, ber, bler, dlbler, lostblocks, PNDiscon]
        return meas_list

if __name__ == '__main__':
    ber = ber()
    ber.reset()
    print ber
