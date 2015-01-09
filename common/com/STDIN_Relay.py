'''
Created on 26 Jul 2013

@author: fsaracino
'''

import os
import sys
import re
#import time
import serial
import logging

from xml.etree.ElementTree import parse

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************                
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
else:
    pass

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
#from os_utils import insertPause

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError



class STDIN_Relay(object):
        
    def __init__(self, timeout=5, ctrlif="STDIN"):
        logger=logging.getLogger('%s._init_' % ctrlif)
        self.test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'com', 'template', 'stdin_config.xml'])  

        self.ctrlif    = ctrlif
        self.timeout   = timeout
        self.port      = None
        self.modeminfo = None
        self.ser_h     = None
        self._get_settings()
        self._open()
        
    # ********************************************
    # Private methods
    # ********************************************
    def _get_settings(self):
        logger=logging.getLogger("%s._get_settings" % self.ctrlif)

        if os.path.isfile(self.test_config_xml_path):
            logger.info("Retrieving STDIN settings from file : %s" % self.test_config_xml_path)
            tree = parse(self.test_config_xml_path)
         
            section_opts         = tree.find('stdin')
            self.platform        = section_opts.find('platform').text
            logger.info("-----------------------------------")
            logger.info(" STDIN platform : %s" % self.platform)
            logger.info("-----------------------------------")
            
    def _open (self):
        pass
    
    # ********************************************
    # Public methods
    # ********************************************
    def close(self):
        pass

    def reboot(self):
        self.modem_off()
        self.modem_on()
    
    def modem_on(self, pause=30):
        logger=logging.getLogger('%s.modem_on' % self.ctrlif)        
        raw_input("power ON the modem and press [ENTER]")
        logger.debug("modem switched ON")
        
    def modem_off(self):
        logger=logging.getLogger('%s.modem_off' % self.ctrlif)        
        raw_input("power OFF the modem and press [ENTER]")
        logger.debug("modem switched OFF")

    def modem_config(self, cmd_l):
        logger=logging.getLogger('%s.modem_config' % self.ctrlif)
        raw_input("configure the modem and press [ENTER]")
    
    def modem_info(self):
        logger=logging.getLogger('%s.modem_info' % self.ctrlif)
        self.modeminfo="""Platform: %s""" % self.platform
        return self.modeminfo
    
    def get_formatted_modem_info(self):
        if not self.modeminfo is None:
            return re.sub(r';', r'\n', self.modeminfo)
    
    def modem_clear_crashinfo(self):
        pass


if __name__ == '__main__':

    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
    rat='LTE'
    rfband=1
    usimemu=0
    earfcn = 300

    lte_config_cmd_l = [ r'at+cfun=0', 
                        r'at%%inwmode=1,E%s,3' % (rfband),
                        r'at%inwmode=0,E,1', 
                        r'at%%ilteearfcn=%s' % (earfcn),
                        r'at%%isimemu=%s' % (usimemu)]
    
    wcdma_config_cmd_l = [ r'at+cfun=0', 
                           r'at%inwmode=0,U,1', 
                           r'at%%isimemu=%s' % (usimemu)]
    
    gsm_config_cmd_l = [ r'at+cfun=0', 
                         r'at%inwmode=0,G,1', 
                         r'at%%isimemu=%s' % (usimemu)]

        
    com_h = STDIN_Relay()
    
    modeminfo=com_h.modem_info()
    logger.info("%s" % com_h.get_formatted_modem_info())

    com_h.modem_config(lte_config_cmd_l)
    com_h.modem_on()
    com_h.modem_off()
    
    if not com_h is None:
        com_h.close()
    
    logger.debug('END')
    
    
