#! /usr/bin/env python

#######################################################################################################################
#
# $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/common/instr/Scdu.py#2 $
# $Author: fsaracino $
# $Revision: #2 $
# $DateTime: 2014/11/10 14:42:42 $
#
#######################################################################################################################

# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import time
import logging


    
import bz2

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


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError


# ********************************************************************
# API functions
# ********************************************************************
def scduOffAll(scdu_ip, usr, pwd, port_l):
    logger=logging.getLogger('scduOffAll')
    scdu_h=Scdu(scdu_ip=scdu_ip, usrname=usr, passwd=pwd, port_l= port_l)
    scdu_h.scdu_off_all()     
    del scdu_h
     
def scduOff(scdu_ip, usr, pwd, port):
    logger=logging.getLogger('scduOff')
    scdu_h=Scdu(scdu_ip=scdu_ip, usrname=usr, passwd=pwd)
    scdu_h.scdu_off(port)     
    del scdu_h
    logger.debug("Turned OFF modem mapped on SCDU %s,%s" % (scdu_ip, port))
    
def scduOn(scdu_ip, usr, pwd, port):
    logger=logging.getLogger('scduOff')
    scdu_h=Scdu(scdu_ip=scdu_ip, usrname=usr, passwd=pwd)
    scdu_h.scdu_on(port)     
    del scdu_h
    logger.debug("Turned ON modem mapped on SCDU %s,%s" % (scdu_ip, port))


class Scdu(object):

    """
    Switched Cabinet Distribution Unit management
    """
    USRNAME = 'jenkins'
    
    def __init__(self, scdu_ip, usrname, passwd, port_l=[1,2,3,4,5,6,7,8], scdu_name='Scdu'):
        """
          scdu_ip : SCDU IP address
          usrname : usrname
          pawsswd : password
          port_l  : list of ports to use, valid range {1..8}          
        """
        self.scdu_ip   = scdu_ip
        self.usrname   = usrname
        self.passwd    = passwd
        self.port_l    = port_l
        self.scdu_name = scdu_name
    
    def insert_pause(self, tsec=5):
        logger=logging.getLogger("%s.insert_pause" % self.scdu_name)
        elapsed_time = 0 
        sleep_time   = int(tsec/5) if (tsec > 5) else 1
        logger.info("pause %s [sec]" % tsec)  
        while (elapsed_time < tsec):
            logger.info("  remaining time : %s" % (tsec-elapsed_time))
            time.sleep(sleep_time)
            elapsed_time += sleep_time 
        
    def scdu_off_all(self, tsec=5):
        logger=logging.getLogger("%s.scdu_off_all" % self.scdu_name)

        if sys.platform in ['linux', 'linux2', 'linux3']:
            import pexpect
            tsec_offs=5
            child = pexpect.spawn(r"telnet %s" % self.scdu_ip)
            child.expect('Username: ')
            child.sendline('%s\r' % self.usrname)    
            child.expect('Password: ')
            child.sendline(bz2.decompress(self.passwd))
            for port_num in self.port_l:
                logger.info("Turning OFF %s:.A%d ... Sleeping for %s [sec]" % (self.scdu_ip, int(port_num), tsec))
                cmd=r"off .A%d" % int(port_num)
                child.sendline(cmd)
                self.insert_pause(tsec)
            child.sendline("sleep %s" % tsec)
            child.close()
            self.insert_pause(tsec_offs)
        else:
            logger.warning("No SCDU function support for Win8")
        
        
    def scdu_off(self, scdu_port, tsec=5):
        logger=logging.getLogger("%s.scdu_off" % self.scdu_name)
        if sys.platform in ['linux', 'linux2', 'linux3']:
            import pexpect
            
            tsec_offs=5
            logger.info("Turning OFF %s:.A%d ... Sleeping for %s [sec]" % (self.scdu_ip, int(scdu_port), tsec))
            child = pexpect.spawn(r"telnet %s" % self.scdu_ip)
            child.expect('Username: ')
            child.sendline('%s\r' % self.usrname)    
            child.expect('Password: ')
            child.sendline(bz2.decompress(self.passwd))
            cmd=r"off .A%d" % int(scdu_port)
            child.sendline(cmd)
            cmd=r"sleep %d" % int(tsec)
            child.sendline(cmd)
            self.insert_pause(tsec)
            child.close()
            self.insert_pause(tsec_offs)
        else:
            logger.warning("No SCDU function support for Win8")


    def scdu_on(self, scdu_port, tsec=20):
        logger=logging.getLogger("%s.scdu_on" % self.scdu_name)
        if sys.platform in ['linux', 'linux2', 'linux3']:
            import pexpect

            tsec_offs=5
            logger.info("Turning ON %s:.A%d ... Sleeping for %s [sec]" % (self.scdu_ip, int(scdu_port), tsec))
            child = pexpect.spawn('telnet %s\r' % self.scdu_ip)
            child.expect('Username: ')
            child.sendline('%s\r' % self.usrname)    
            child.expect('Password: ')
            child.sendline(bz2.decompress(self.passwd))
            #child.sendline('%s\r' % self.passwd)
            cmd=r"on .A%d" % int(scdu_port)
            child.sendline(cmd)
            cmd=r"sleep %d" % int(tsec)
            child.sendline(cmd)
            self.insert_pause(tsec)
            child.close()
            self.insert_pause(tsec_offs)
        else:
            logger.warning("No SCDU function support for Win8")

#######################################################################################################################

if __name__ == '__main__':
        
    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    

    ip          = r'0.0.0.0'
    uid         = 'jenkins'
    pwd         = """BZh91AY&SYN\x0fuz\x00\x00\x01A\x80\x00\x02 #\x86\x00 \x00"\x1a3PC\x02\x1b\xc0\xa4\x1c\xbc]\xc9\x14\xe1BA8=\xd5\xe8"""
    used_port_l = [1,2,7,8] 
    logger.debug('Connecting to SCDU : %s' % ip)
    if 0:
        scdu_h=Scdu(ip, uid, pwd, used_port_l, scdu_name='scdu_h')
        scdu_h.scdu_off_all()     
        scdu_h.scdu_on(7)
        scdu_h.scdu_off(7)
    else:
        scduOffAll(ip, uid, pwd, port_l=[2,7])
        scduOn(ip, uid, pwd, port=7)
        scduOff(ip, uid, pwd, port=7)
                   
    logger.debug('END')    
    

