'''
Created on 26 Jul 2013

@author: fsaracino
'''

import os
import sys
import logging
import time
import serial
import re

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************                
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
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
from Serial_ComPortDet import auto_detect_port
#from os_utils import insertPause

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError







class AT_Modem(object):
    """
      Class used for modem configuration via AT commands
    """             
    BAUDRATE = 9600
    BYTESIZE = 8
    PARITY   = 'N'
    STOPBIT  = 1

    # ********************************************
    # Private methods
    # ********************************************
    def __init__(self, timeout=10, ctrlif="AT"):
        self.ctrlif    = ctrlif
        self.timeout   = timeout
        self.modeminfo = None
        logger=logging.getLogger("%s._init" % ctrlif)
        
        if ctrlif == 'AT':
            self.port = auto_detect_port("Modem_port")
            if self.port is None:
                sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)
                logger.debug('Detected communication port: %s' % self.port)
            else:
                if sys.platform in ['cygwin', 'win32']:
                    self.port = int(self.port)-1
        else:
            self.port = ctrlif

        try:
            self._open()
        except serial.SerialException, e:
            logging.error("Unable to open port %s: %s" % (self.port, e))
            sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)


    def _open (self):
        kwargs = { 'baudrate': self.BAUDRATE, 'bytesize': self.BYTESIZE, 'parity': self.PARITY, 'stopbits': self.STOPBIT, 'timeout': self.timeout}
        is_url = isinstance(self.port, str) and '://' in self.port
        if is_url:
            self.hdlr = serial.serial_for_url(self.port, **kwargs)
        else:
            self.hdlr = serial.Serial(self.port, **kwargs)

    def _send_cmdlist(self, cmd_l):
        logger=logging.getLogger('%s._send_cmdlist' % self.ctrlif)
        report=""
        for cmd_str in cmd_l:
            logger.debug("SEND CMD : %s" % cmd_str)
            (ret, msg) = self._send_cmd(cmd_str)             
            if (  ret !=0 ):
                logger.error("RESPONSE NOT RECEIVED FOR: %s" % cmd_str)
                msg="None"
            report += ("Response for CMD(%s) : CODE = %s  MSG = %s" % (cmd_str, ret, msg))    
        return report


    def _send_cmd(self, cmd_str=r'AT', rsp_str ='OK'):
        """
        Send AT command, cmd_str
        Check response, rsp_str
        """
        logger=logging.getLogger('%s._send_cmd' % self.ctrlif)
        try:
            text_str = "AT command"
            logger.debug("%-15s:\t%s" %(text_str, cmd_str))
            cmd_str = cmd_str + '\r\n'
            self.hdlr.write(cmd_str)      # write a string
            if not 'ireset' in cmd_str:
                curr_iter, MAX_ITER = 1, 3
                while (curr_iter <= MAX_ITER):
                    logger.debug("Sending AT command. Iteration %s of %s" %(curr_iter, MAX_ITER))
                    
                    self.hdlr.write(cmd_str)      # write a string
                    reg_expr = r'\b' + re.escape(rsp_str) + r'\b'
                    response, matchObj = self._read_resp(reg_expr)
                    # Reformat the output response 
                    #response=re.sub(r'[\r\n|\r]', r';', response)
                    #response=re.sub(r'[;]+', r'; ', response)
                    if matchObj:
                        text_str = "Response"
                        logger.debug("%-15s:\t%s" %(text_str, matchObj.group()))
                        return (0, response)
                    else:
                        logger.debug("Expected STR response not found")
                        text_str ="Response"
                        logger.debug("%-15s:\t%s" %(text_str, response))
                        return (1, response)
            else:
                self.hdlr.write(cmd_str)      # write a string
                logger.info("Modem RESET in progress...")
                return (0, None)
            
        except serial.SerialException, e:
            logging.error("Unable to send command to port %s: %s" % (self.port, e))
            sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)
        else:
            pass


    

    def _read_resp(self, reg_expr):
        '''Read from the serial device until a string matching reg_expr is
        found, or the timeout elapses.'''
        iteration=0
        resp_buf = ""
        expiry = time.time() + self.timeout
        while (expiry - time.time() > 0):
            iteration +=1
            s = self.hdlr.readline()
            if len(s)==0: break
            resp_buf += s
            matchObj = re.search(reg_expr, resp_buf, re.M|re.I)
            if matchObj: 
                break
            time.sleep(0.1)
            
        return resp_buf, matchObj
    
    def _parse_modem_info(self):
        if not self.modeminfo is None:
            tmp=re.sub(r'[\r\n|\r]', r';', self.modeminfo)
            tmp=re.sub(r'[;]+', r'; ', tmp)
            tmp = '\n'.join(tmp.split(';')[5:])
            self.modeminfo=tmp

    # ********************************************
    # Public methods
    # ********************************************
    def insert_pause(self, tsec=5):
        logger=logging.getLogger('%s._insert_pause' % self.ctrlif)
        elapsed_time = 0 
        sleep_time   = int(tsec/5) if (tsec > 5) else 1
        logger.info("pause %s [sec]" % tsec)  
        while (elapsed_time < tsec):
            logger.info("  remaining time : %s" % (tsec-elapsed_time))
            time.sleep(sleep_time)
            elapsed_time += sleep_time
            
    def reboot(self, pause=30):
        logger=logging.getLogger('%s.swreset' % self.ctrlif)
        self._send_cmd(cmd_str=r'at%ireset')
        logger.info("Waiting for %s [sec] DUT booting " % pause)
        self.insert_pause(pause)     

           
    def close(self):
        logger=logging.getLogger('%s.close' % self.ctrlif)
        self.hdlr.close()
        logger.debug("Closed COM %s" % self.port)

        
    def modem_off(self):
        logger=logging.getLogger('%s.modem_off' % self.ctrlif)        
        self._send_cmd(cmd_str=r'at+cfun=0')
        logger.info("modem switched OFF")


    def modem_on(self):
        logger=logging.getLogger('%s.modem_on' % self.ctrlif)        
        self._send_cmd(cmd_str=r'at+cfun=1')
        logger.info("modem switched ON")

    def modem_info(self):
        logger=logging.getLogger('%s.modem_info' % self.ctrlif)
        if self.modeminfo is None:        
            self._send_cmd(cmd_str=r'at+cfun=0')
            ret, msg = self._send_cmd(cmd_str=r'at%idbgtest', rsp_str='RFM Board ID')
            self.modeminfo = msg
            #logger.debug("ret=%s, msg=%s" % (ret, msg))
        self._parse_modem_info()
        return self.modeminfo
    
    def get_formatted_modem_info(self):
        if not self.modeminfo is None:
            return re.sub(r';', r'\n', self.modeminfo)

    def modem_clear_crashinfo(self):
        logger=logging.getLogger('%s.modem_clear_crashinfo' % self.ctrlif)
        self._send_cmd(cmd_str='at%debug=99')
        logger.info("erased modem crash info")


    def modem_ta(self, val):
        logger=logging.getLogger('%s.modem_ta' % self.ctrlif)
        cmd = [r'at%%plctrl=%s' % val]
        self._send_cmd(cmd_str=cmd)
        logger.info("programmed TA with val : %s" % val)


    def modem_config(self, cmd_l):
        logger=logging.getLogger('%s.modem_config' % self.ctrlif)
        logger.info("sending command list: %s" % cmd_l)
        self._send_cmdlist(cmd_l)

    
    def modem_mode(self):
        logger=logging.getLogger('%s.modem_mode' % self.ctrlif)
        #self._send_cmd(cmd_str=r'at+cfun=0')    
        status, msgstr=self._send_cmd(cmd_str=r'at%mode?')
        #reg_expr = r'\b' + re.escape("OK") + r'\b'
        #res = self.read_resp(reg_expr)
        #print msgstr
        mode = -1
        if status==0:
            m_obj = re.search(r'.*:?\s*(\d)', msgstr, re.I)
            if m_obj:
                mode = m_obj.group(1)
        
        logger.info("Detected modem mode : %s" % mode)
        return mode


    def modem_core_dump(self, filedump):
        """
        Retrieve the coredump following a modem crash
        """
        logger=logging.getLogger('%s.modem_core_dump' % self.ctrlif)
        logger.info("Preparing core dump file: %s" % filedump)
        #filedump="dump_%s.log" % time.strftime("%Y%m%d_%H%M%S", time.localtime())
        #cmd_l=[r'at%debug=1']
        cmd_l=[r'at%debug=0', r'at%debug=2']       
        cmd_str='\r\n'.join(cmd_l)

        text_str = "AT command"
        logging.debug("Core file : %s" % filedump)        
        logging.debug("%-15s:\t%s" %(text_str, cmd_str))
        with open(filedump, 'wb') as fd:
            cmd_str = cmd_str + '\r\n'
            self.hdlr.write(cmd_str)      # write a string
            len_rd=0
            response = self.hdlr.read(2**16)
            while len(response)>0:
                len_rd += len(response)
                logging.info("read %s bytes, current_len=%s" % (len(response), len_rd))
                fd.write(response)
                response = self.hdlr.read(2**16)        
        print "END"



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

        
    com_h = AT_Modem()
    
    modeminfo=com_h.modem_info()
    logger.info("%s" % com_h.get_formatted_modem_info())

    com_h.modem_config(lte_config_cmd_l)
    com_h.modem_on()
    #com_h.modem_off()
    
    if not com_h is None:
        com_h.close()
    
    logger.debug('END')

