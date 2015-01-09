'''
Created on 15 Sep 2013

@author: fsaracino
'''

import sys
import os
import socket
import time
import logging
import re

from xml.etree.ElementTree import parse


try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'error']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))

# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
#from os_utils import insertPause
from subprocess_helper import runCmdBlockingModeTimeout




class ADB_Modem(object):
    
    AIRPLANE_MODE_OFF       = 0
    AIRPLANE_MODE_ON        = 1
    AIRPLANE_MODE           = { AIRPLANE_MODE_OFF:'OFF',  AIRPLANE_MODE_ON:'ON' }
        
    def __init__(self, timeout=240, modem_reboot=1, ctrlif="ADB"):
        self.ctrlif    = ctrlif
        self.timeout   = timeout
        self.modeminfo             = None
        logger=logging.getLogger("%s._init" % ctrlif)
        
        # Private parameters
        self._host                 = 'localhost'
        self._proto                = socket.AF_INET
        self._type                 = socket.SOCK_STREAM
        self._maxchar              = 2048
        self._hsocket              = None
        
        # Public parameters
        self.test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'com', 'template', 'adb_config.xml'])       
        self.platform              = None
        self.root_permission       = None         
        self.port_tcp_at           = None         
        self.port_tty_at           = None
        self.port_tcp_log          = None
        self.port_tty_log          = None
        
        # Status info
        self.device_tag            = None
        self.airplane_mode         = None

        self._get_settings()

        try:
            self._open(modem_reboot)
        except SystemExit:
            exc_info = sys.exc_info()
            logger.error("Error opening ADB TCP socket (exit status=%s): %s" % (exc_info[1], exc_info[0]))
            sys.exit(CfgError.ERRCODE_SYS_SOCKET_CONN)
             
    # ------------------------------------------------------------------------------------------ #
    #                                     PRIVATE METHODS                                        #
    # ------------------------------------------------------------------------------------------ #       
    def _get_settings(self):
        logger=logging.getLogger("%s._get_settings" % self.ctrlif)

        if os.path.isfile(self.test_config_xml_path):
            logger.info("Retrieving ADB settings from file : %s" % self.test_config_xml_path)
            tree = parse(self.test_config_xml_path)
         
            #self.mapping  = {}
            section_opts         = tree.find('adb_config')
            self.platform        = section_opts.find('platform').text
            self.root_permission = int(section_opts.find('root_permission').text)
            self.port_tcp_at     = None if section_opts.find('port_tcp_at').text is None else int(section_opts.find('port_tcp_at').text)
            self.port_tty_at     = section_opts.find('port_tty_at').text
            self.port_tcp_log    = None if section_opts.find('port_tcp_log').text is None else int(section_opts.find('port_tcp_log').text)  
            self.port_tty_log    = section_opts.find('port_tty_log').text
        
        # Show settings
        if 1:
            logger.debug("platform        : %s" % self.platform)        
            logger.debug("root_permission : %s" % self.root_permission)        
            logger.debug("TTY AT port     : %s" % self.port_tty_at)
            logger.debug("TCP AT port     : %s" % self.port_tcp_at)
            logger.debug("TTY LOG port    : %s" % self.port_tty_log)
            logger.debug("TCP LOG port    : %s" % self.port_tcp_log)

    
    def _open(self, modem_reboot):
        logger=logging.getLogger('%s._open' % self.ctrlif)
        try:
            if modem_reboot: self.reboot()
            self._config()
        except:
            logger.error("modem initialisation failure. Check the USB connection with the device")
            sys.exit(CfgError.ERRCODE_SYS_ADB_COM_FAILURE)
        
        if self.root_permission and (not self.port_tcp_at is None):
            try:
                self._hsocket = socket.socket(self._proto, self._type)
                self._hsocket.connect((self._host, self.port_tcp_at))
            except:
                exc_info = sys.exc_info()
                logger.error("Error opening ADB TCP socket (exit status=%s): %s" % (exc_info[1], exc_info[0]))
                sys.exit(CfgError.ERRCODE_SYS_SOCKET_CONN)
            logger.debug("ADB Socket opened")


    def _config(self):
        logger=logging.getLogger("%s._config" % self.ctrlif)
        self._send_adb_cmd('adb kill-server', timeout=5)
        self._send_adb_cmd('adb start-server', timeout=5)
        self._send_adb_cmd('adb wait-for-device', timeout=5)
        self._send_adb_cmd('adb get-state', timeout=5)
        self._send_adb_cmd('adb devices', timeout=5)
        
        if self.root_permission: 
            # Development device
            self._send_adb_cmd('adb root', timeout=5)
            self.insert_pause(tsec=2)
            #self._send_adb_cmd('adb remount', timeout=5)
            #self.insert_pause(tsec=2)
            #self._send_adb_cmd('adb shell stop ril-daemon', timeout=5)
            #self.insert_pause(tsec=2)
            
            if not self.port_tcp_at is None:
                ret, output= self._send_adb_cmd("adb shell ls %s" % (self.port_tty_at))
                if 'No such file or directory' in output:
                    logger.error('AT TTY port %s not detected: please check modem connection' % self.port_tty_at)
                    sys.exit(CfgError.ERRCODE_SYS_ADB_COM_FAILURE)
                ret, output = self._send_adb_cmd('adb forward tcp:%d dev:%s' % (self.port_tcp_at, self.port_tty_at))
                if not ret==0:
                    logger.error('AT TCP port %s not opened' % self.port_tty_at)
                    sys.exit(CfgError.ERRCODE_SYS_ADB_COM_FAILURE)
                 
            if not self.port_tcp_log is None:
                ret, output = self._send_adb_cmd("adb shell ls %s" % (self.port_tty_log))
                if 'No such file or directory' in output:
                    logger.error('LOG TTY port %s not detected: please check modem connection' % self.port_tty_log)
                    sys.exit(CfgError.ERRCODE_SYS_ADB_COM_FAILURE)
                ret, output = self._send_adb_cmd('adb forward tcp:%d dev:%s' % (self.port_tcp_log, self.port_tty_log))
                if not ret==0:
                    logger.error('LOG TCP port %s not opened' % self.port_tty_log)
                    sys.exit(CfgError.ERRCODE_SYS_ADB_COM_FAILURE)


    def _send_adb_cmd(self, cmd, timeout=240):
        logger=logging.getLogger('%s._send_adb_cmd' % self.ctrlif)
        logger.info("Running ADB command (timeout=%s): %s" % (timeout, cmd))
        cmd_l=cmd.split(' ')
        
        ret, output = runCmdBlockingModeTimeout(cmd_l, timeout)
        if ret == None:
            logger.error("Command timeout")
        elif ret == 0:
            logger.debug("Command executed successfully")
        else:
            logger.error("Something went wrong (return code: %s)" % ret)
            sys.exit(CfgError.ERRCODE_SYS_ADB_CMD_ERROR)
        return ret, output


    def _send_at_cmdlist(self, cmd_l):
        logger=logging.getLogger('%s._send_adb_cmdlist' % self.ctrlif)
        report=""
        for cmd_str in cmd_l:
            logger.debug("SEND CMD : %s" % cmd_str)
            (ret, msg) = self._send_at_cmd(cmd_str)             
            if (  ret !=0 ):
                logger.error("RESPONSE NOT RECEIVED FOR: %s" % cmd_str)
                msg = "None"
            report += ("Response for CMD(%s) : CODE = %s  MSG = %s" % (cmd_str, ret, msg))    
        return report            


    def _send_at_cmd(self, cmd_str, rsp_str ='OK'):
        logger=logging.getLogger('ADB_Modem.send_command')
        logger.info("Sending (%s), Expecting (%s)" % (cmd_str, rsp_str))
        
        tsleep = 10 if (cmd_str == "at%itr:?") else 1
        try:
            self._hsocket.send((cmd_str+'\r\n').encode())
            self.insert_pause(tsleep)
            
            output = self._hsocket.recv(self._maxchar)
            output=re.sub(r'[\r\n|\r]', r';', output)
            output=re.sub(r'[;]+', r'; ', output) 
            reg_expr = r'\b' + re.escape(rsp_str) + r'\b'
            matchObj = re.search (reg_expr, output, re.M|re.I)
            status=0
            if matchObj:
                logger.debug("%-15s:\t%s" %("Response", matchObj.group()))
            else:
                logger.debug("Expected STR response not found")
                logger.debug("%-15s:\t%s" %("Response", output))
                status=1
        except socket.error:
            logger.error("Unable to AT send command to port: %s" % self.port_tcp_at)
            sys.exit(CfgError.ERRCODE_SYS_SOCKET_CONN)
        return (status, output)

    def _parse_modem_info(self):
        if not self.modeminfo is None:
            tmp=re.sub(r'[\r\n|\r]', r';', self.modeminfo)
            tmp=re.sub(r'[;]+', r'; ', tmp)
            tmp = '\n'.join(tmp.split(';')[5:])
            self.modeminfo=tmp
    # ------------------------------------------------------------------------------------------ #
    #                                     PUBLIC METHODS                                         #
    # ------------------------------------------------------------------------------------------ #
    def reboot(self, tsec=60):
        logger=logging.getLogger('%s._send_reboot' % self.ctrlif)
        self._send_adb_cmd('adb reboot')
        self.insert_pause(tsec)
        logger.debug("Modem READY")
  
        
    def close(self):
        logger=logging.getLogger('%s._send_close' % self.ctrlif)
        if not self._hsocket is None:
            self._hsocket.close()
            logger.debug("Socket closed")

    def insert_pause(self, tsec=5):
        logger=logging.getLogger('%s._insert_pause' % self.ctrlif)
        elapsed_time = 0 
        sleep_time   = int(tsec/5) if (tsec > 5) else 1
        logger.info("pause %s [sec]" % tsec)  
        while (elapsed_time < tsec):
            logger.info("  remaining time : %s" % (tsec-elapsed_time))
            time.sleep(sleep_time)
            elapsed_time += sleep_time

    def modem_off(self):
        logger=logging.getLogger('%s._modem_off' % self.ctrlif)
        if self.root_permission:
            (res, output) = self._send_at_cmd(r'at+cfun=0')
            #logger.debug("res=%s, msg=%s" % (res, output))
        else:
            self.dut_airplanemode_on()

    def modem_on(self):
        logger=logging.getLogger('%s._modem_on' % self.ctrlif)
        if self.root_permission:
            (res, output) = self._send_at_cmd(r'at+cfun=1')
            #logger.debug("res=%s, msg=%s" % (res, output))
        else:
            self.dut_airplanemode_off()

    def modem_config(self, cmd_l):
        logger=logging.getLogger('%s._modem_config' % self.ctrlif)
        if self.root_permission:
            logger.debug("sending command list: %s" % cmd_l)
            self._send_at_cmdlist(cmd_l)
        else:
            pass

    def modem_info(self):
        logger=logging.getLogger('%s._modem_info' % self.ctrlif)
        if self.root_permission:
            self._send_at_cmd(r'at+cfun=0')
            (res, output) = self._send_at_cmd(cmd_str=r'at%idbgtest', rsp_str='RFM Board ID')
            self.modeminfo = output
            #logger.debug("ret=%s, msg=%s" % (ret, msg))
            self._parse_modem_info()
        else:
            self.modeminfo="""Platform: %s""" % self.platform
        return self.modeminfo
    
    def get_formatted_modem_info(self):
        if not self.modeminfo is None:
            return re.sub(r';', r'\n', self.modeminfo)
    
    def modem_clear_crashinfo(self):
        pass
        
    def  dut_airplanemode_on(self, timeout=10):
        logger=logging.getLogger('ADB_Modem.dut_airplanemode_on')
        self._send_adb_cmd("adb shell settings put global airplane_mode_on 1",  timeout)
        self._send_adb_cmd("adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true", timeout)
        res, output=self._send_adb_cmd("adb shell settings get global airplane_mode_on", timeout)
        logger.info("Aiplane mode ON ? %s" % (int(res)==self.AIRPLANE_MODE_ON))
        
        
    def  dut_airplanemode_off(self, timeout=10):
        logger=logging.getLogger('ADB_Modem.dut_airplanemode_off')
        self._send_adb_cmd("adb shell settings put global airplane_mode_on 0",  timeout)
        self._send_adb_cmd("adb shell am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false", timeout)
        res, output=self._send_adb_cmd("adb shell settings get global airplane_mode_on", timeout)
        logger.info("Aiplane mode OFF ? %s" % (int(res)==self.AIRPLANE_MODE_OFF))

    
    
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

    #            # Device erase via AT port
    #            cmd_l = [ r'at+cfun=0',
    #                      #r'at+cgsn',
    #                      r'at%mode=2',
    #                      r'at%nverase',
    #                      #r'at%imei=a,b,...',
    #                      r'at%mode=0']

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
    
    
    com_h=ADB_Modem(modem_reboot=1)

    
    modeminfo=com_h.modem_info()
    logger.info("%s" % com_h.get_formatted_modem_info())

    com_h.modem_config(lte_config_cmd_l)
    com_h.modem_on()
    com_h.modem_off()
    
    if not com_h is None:
        com_h.close()
    
    logger.debug('END')
        
    
    

    
