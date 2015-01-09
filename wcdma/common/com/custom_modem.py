#-------------------------------------------------------------------------------
# Name:        custom_modem
# Purpose:     customised modem
#
# Author:      joashr
#
# Created:     19/11/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, sys, logging

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    print test_env_dir
    sys.path.append(test_env_dir)
    import test_env

from pl1_testbench_framework.common.com.modem import serialComms

class custom_modem(serialComms):
    def set_preferred_rat(self, rat="UTRAN"):
        loggerModem = logging.getLogger(__name__ + 'set_preferred_rat')
        if rat == "UTRAN":
            loggerModem.info("setting preferred RAT=UTRAN")
            cmd_l = [ r'at%inwmode=0,U,1']
            self.sendCmdList(cmd_l)
        else:
            print "RAT %s is not supported, no preference of RAT or band will be set!" %rat

if __name__ == '__main__':
    pass
