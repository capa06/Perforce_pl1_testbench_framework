'''
Created on 19 Sep 2014

@author: fsaracino
'''
# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging

from xml.etree.ElementTree import parse


# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'error']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'tools']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError    import CfgError
from AT_Modem    import AT_Modem
from ADB_Modem   import ADB_Modem
from KMT_Relay   import KMT_Relay
from STDIN_Relay import STDIN_Relay

class ComLib():
    def __init__(self, ctrlif):
        if (ctrlif=='AT'):
            self.modem = AT_Modem()
        elif ctrlif=='ADB':
            self.modem = ADB_Modem()
        elif ctrlif=='STDIN':
            self.modem = STDIN_Relay()
        elif ctrlif=='KMT':
            self.modem = KMT_Relay()
        else:
            # Default to an AT modem with path or URL specified.
            self.modem = AT_Modem(ctrlif=ctrlif)
             
if __name__ == '__main__':

    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
#    for modemtype in ['AT', 'ADB', 'KMT', 'STDIN']:
#    for modemtype in ['socket://<ipaddr>:2217']:
    for modemtype in ['AT']:
        try:
            com_h = ComLib(modemtype)
            logger.debug("Got handler %s" % com_h)
            if not com_h.modem is None:
                print "%s" % com_h.modem.modem_info()
                com_h.modem.close()
        except:
            logger.error("------------------")
            print sys.exc_info()
            pass

    logger.debug("END")
