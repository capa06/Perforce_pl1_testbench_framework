#-------------------------------------------------------------------------------
# Name:        rfmodem.py
# Purpose:
#
# Author:      joashr
#
# Created:     16/11/2013
#-----------------------------------------------------------------------------

import serial
import re, sys, os, logging, shutil, math
import time
import traceback

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-1])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port
from pl1_rf_system.common.user_exceptions import *
import pl1_rf_system.common.rf_common_globals as rf_global
import pl1_rf_system.common.rf_common_functions as rf_cf
from pl1_rf_system.common.verdict import Verdict

def get_chip_id_wrapper():
    chip_id = ""
    modemObj=None
    try:
        modemObj = serialComms(timeout = 2)
        chip_id = modemObj.get_chip_id()

    except:
        print traceback.format_exc()
        print "Not able to query modem for the chip id"

    if modemObj:
        modemObj.close()

    return chip_id

def get_build_info_wrapper():
    cl_str = ""
    try:

        modemObj = serialComms(timeout = 2)
        cl_str = modemObj.get_build_info()
        modemObj.close()
        return cl_str
    except:
        print "Not able to query modem for the build CL"
        return cl_str

def get_modem_info():

    modemInfo=""

    try:
        modemObj = serialComms(timeout = 2)
        modemInfo = modemObj.getInfo()
        modemObj.close()
        return modemInfo
    except:
        print "Not able to query modem for modem detailed info"
        print traceback.format_exc()
        return modemInfo

def switch_mode_1_3():

    print "Will try to change modem mode to 1,3"

    try:

        modemObj = serialComms(timeout = 2)

        #status, response = modemObj.send_cmd_rd_response(cmd_str="at%mode=1,3")
        modemObj.send_cmd(cmd_str="at%mode=1,3")

        modemObj.close()

        if poll_for_port(portName="Modem_port", timeout_sec=30, poll_time_sec=5,
                         reason="pausing after changing to boot loader mode"):

            print "modem com port successfully found"

            time_secs = 10

            print "pausing for %s secs ..." %time_secs

            time.sleep(time_secs)

        else:

            print "modem com port not found after boot loader mode change"

            sys.exit(ec.ERRCODE_COM_PORT_DETECT)

        mode = query_modem_mode()

        print "Mode : %s" %mode

        BOOT_LOADER_MODE = 1

        if mode == BOOT_LOADER_MODE:

            print "Successful detection of boot loader mode"

        else:

            print "Unsuccessful detection of boot loader mode"

            sys.exit(ec.ERRCODE_BOOT_LOADER_MODE_FAIL)

    except:

        print "Not able to change to boot laoder mode generic error"

        print traceback.format_exc()

        sys.exit(ec.ERRCODE_BOOT_LOADER_MODE_FAIL)


def collect_full_core_dump(core_dump_dir="", filename=""):
    """
    Retrieve the coredump following a modem crash
    """

    loggerModem = logging.getLogger(__name__ + 'collect_full_core_dump')

    core_dump_path = (os.path.join(core_dump_dir, filename))

    modemObj = serialComms(timeout = 5, dumpfile = core_dump_path)

    cmd_l=[r'at%debug=0', r'at%debug=2']
    cmd_str='\r\n'.join(cmd_l)
    text_str = "AT command"

    print "Will try to collect core dump logs"
    print ("Core file : %s" % core_dump_path)
    loggerModem.debug("%-15s:\t%s" %(text_str, cmd_str))
    with open(modemObj.dumpfile, 'wb') as fd:
        cmd_str = cmd_str + '\r\n'
        modemObj.serObj.write(cmd_str)      # write a string
        len_rd=0
        response = modemObj.serObj.read(2**16)
        while len(response)>0:
            len_rd += len(response)
            loggerModem.debug("read %s bytes, current_len=%s" % (len(response), len_rd))
            fd.write(response)
            response = modemObj.serObj.read(2**16)
    print("Created core dump: %s" % modemObj.dumpfile)

    modemObj.close()
    modemObj = None



def get_crash_dump_log(core_dump_dir="", icera_utils_path=""):

    if sys.platform in ['cygwin', 'win32']:
        full_path_crash_check = os.sep.join(icera_utils_path.split(os.sep)[:]+['crash-check.exe'])
        cmd = '%s --dir %s --verbose --timestamp-fn' % (full_path_crash_check, core_dump_dir)

    elif sys.platform in ['linux', 'linux2', 'linux3']:
        import shlex
        full_path_crash_check = os.sep.join(icera_utils_path.split(os.sep)[:]+['crash-check'])
        cmd = '%s --dir %s --verbose --timestamp-fn' % (full_path_crash_check, core_dump_dir)
        cmd = shlex.split(cmd)
    else:
        print "Platform %s not supported" %sys.platform
        return -1

    rf_cf.run_script(cmd)

def extract_modem_mode(str):
    modeNum = -1
    m_obj = re.search(r'mode:?\s*(\d)', str, re.I)
    if m_obj:
        modeNum = m_obj.group(1)
        print "modem mode is %s" %modeNum
    else:
        print "not able to get the modem mode"

    return modeNum


def query_modem_mode():
    mode = -1
    try:
        modemObj = serialComms(timeout = 2)
        modemObj.send_cmd(cmd_str="at%mode?")
        res = modemObj.read_response()
        mode = extract_modem_mode(res)
        modemObj.close()
    except:
        print "Not able to query the mode of the modem"

    return int(mode)


def set_modem_mode(mode = 1):

    func_name = sys._getframe(0).f_code.co_name
    loggerModem = logging.getLogger(__name__ + func_name)

    current_mode = query_modem_mode()

    if current_mode == mode:
        loggerModem.info (" Modem mode is already set to %s" %mode)
        return

    modemObj = None

    at_cmd = r'AT%%MODE=%d' %mode

    retryNum = 0
    maxRetry = 3
    SUCCESS = 0
    FAIL = 1
    response =""
    status = FAIL
    while retryNum <= maxRetry:
        try:
            if not modemObj:
                modemObj = serialComms(timeout = 4)
            (status, response)=modemObj.send_cmd_rd_response(cmd_str = at_cmd)
            break
        except Exception:
            loggerModem.error (" Not able to read response to %s" %at_cmd)
            if retryNum != maxRetry:
                loggerModem.info ("Retry %s of %s" %(retryNum+1, maxRetry))
                if modemObj:
                    modemObj.close()
                    modemObj = None
            else:
                errMsg = "Not able to read response to %s" %at_cmd
                if modemObj:
                    modemObj.close()
                    modemObj = None
                #self.RecordError(errMsg) #There is no self

            wait_sec = 20
            txt = "Waiting %s secs before sending AT cmd again" %wait_sec
            rf_cf.pause(duration_s=wait_sec, poll_time_sec=10, desc=txt)
            retryNum +=1

    if modemObj:
        modemObj.close()

    if status != SUCCESS:

        if poll_for_port(portName="Modem_port", timeout_sec=30, poll_time_sec=5,
                     reason="pausing after mode change"):

            print "modem com port successfully found"

            time_secs = 10

            print "pausing for %s secs ..." %time_secs

            time.sleep(time_secs)

        else:

            self.RecordError("modem com port not found after modem change")

    modemMode = query_modem_mode()

    if mode == modemMode:

        print "Successful switch to mode %s" %mode

    else:

        err_msg = ("Unsuccessful switch to mode %s" %mode)
        raise ExGeneral(err_msg)

def switch_off_radio(ristretto_com_port=7):
    serialCom = serialComms(portNum = (ristretto_com_port - 1), timeout = 5)
    print "Will now switch off the radio ..."
    rsp = serialCom.send_cmd_rd_response(cmd_str=r'AT+CFUN=0')
    serialCom.close()

def switch_mode_to_zero():

    g_modem_com_port = auto_detect_port("Modem_Port")

    modeNum = query_modem_mode(g_modem_com_port)

    if modeNum == 0:

        print "Modem mode is in the expected mode"

    elif modeNum == 1:
        mode = 0
        print "Warning modem mode should be 0 between execution of tests"
        print "It is likely that the modem has reset"
        print "Changing modem mode to %s" %mode
        set_modem_mode(g_modem_com_port, mode)
        g_modem_com_port = auto_detect_port("Modem_Port")
        print "Auto port detection: modem com port is COM%s" %(g_modem_com_port)
        modem_mode = query_modem_mode(g_modem_com_port)
        if modem_mode == mode:
            print "modem mode successfully set to %s" %mode

    else:
        print "Error querying the modem mode!!"

    #switch_off_radio(g_modem_com_port)


def get_p4webrevStringfrom_modem(modemInfo):
    """
    obtain p4webrev list from get_modem_info()
    """
    p4WebRevStr = ""

    m_obj = re.search(r'P4webrev\s+:\s*(\S+)', modemInfo, re.I)

    if m_obj:
        p4WebRevStr = m_obj.group(1)
        print "p4webrev is %s" %p4WebRevStr
        #p4WebRevList = p4WebrevStr.split(',')
        return p4WebRevStr

    else:
        print "not able to get p4webrev"
        return p4WebRevStr

def get_build_cl_from_modem(modemInfo):
    """
    obtain build CL from get_modem_info()
    """

    build_cl_str = ""

    m_obj = re.search(r'Changelist\s+:\s+(CL\d+)', modemInfo, re.I)
    if m_obj:
        build_cl_str = m_obj.group(1)
        print "build CL is %s" %build_cl_str
        return build_cl_str
    else:
        print "not able to get the build CL from"
        return build_cl_str

def get_platform_from_modem(modemInfo):
    """
    obtain build CL from get_modem_info()
    """

    platform = ""

    m_obj = re.search(r'Variant\s+:\s+(\S+)', modemInfo, re.I)
    if m_obj:
        platform = m_obj.group(1)
        print "Platform is %s" %platform
        return platform
    else:
        print "not able to get the Platform"
        return platform



def modem_setup_3g_tx_test(band=2, freqMHz=1960, tx_agc_val=-8):
    set_modem_mode(mode = rf_global.FACTORY_TEST_MODE)
    modemObj = serialComms(timeout = 2)
    modemObj.set_rat_band(rat='3g', band=1)
    modemObj.set_freqMHz(rat='3g', freqMHz=1950)
    modemObj.enable_tx(rat='3g')
    modemObj.send_ul_pattern()
    modemObj.set_txagc(rat='3g', value=-10)
    modemObj.close()

def query_build_info_from_modem():

    modemObj = serialComms(timeout = 2)
    modeminfo = modemObj.getInfo()
    modemObj.close()
    modemObj = None
    return modeminfo


class serialComms:

    def __init__( self,verdictObj=Verdict(), timeout = 5, dumpfile="", simulate_usim=0):

        self.timeout = timeout
        self.modemInfo = ""
        self.dumpfile=dumpfile
        self.set_tx_enabled_state(boolVal=0)
        self.set_rx_enabled_state(boolVal=0)
        self.verdictObj = verdictObj

        # note that the return value is 1 based i.e.
        # e.g. modemPortNum = 1, corresponds to COM1
        # for windows os
        if sys.platform in ['cygwin', 'win32']:
            modemPortNum = auto_detect_port("Modem_port")
        else:
            modemPortNum = auto_detect_port("Modem_port", suppressPrint=1)

        if not modemPortNum :

            #print "Cannot detect modem port"
            #raise Exception
            err_msg = ('Cannot detect modem port')
            self.RecordError(err_msg)

        # translation to zero based number mapping
        # i.e. modemPortNum 7 maps to serial port 6
        # as this is required by the serial class
        if sys.platform in ['cygwin', 'win32']:
            self.modemPortNum_zero_index = modemPortNum = modemPortNum - 1
        elif sys.platform in ['linux', 'linux2', 'linux3']:
            # note in linux modemPortNum_zero_index is /dev/ttyACM*
            # so the name is a misnomer but used because this was
            # initially developed for windows
            self.modemPortNum_zero_index = modemPortNum
        else:
            print "Unsupported platform %s" %sys.platform
            sys.exit(ec.ERRCODE_UNSUPPORTED_OS_PLATFORM)

        self.build_cl = ""
        self.simulate_usim = simulate_usim

        self.serObj = None
        try:
            self.serObj = self.open()
        except:
            if sys.platform in ['cygwin', 'win32']:
                errMsg = "Unable to open com port %s" %(self.modemPortNum_zero_index + 1)
            else:
                errMsg = "Unable to open com port %s" %(self.modemPortNum_zero_index)
            #raise Exception
            #sys.exit(ec.ERRCODE_COM_PORT_DETECT)
            self.RecordError(errMsg)

    def RecordError (self, errmsg="",raise_except=True):

        self.verdictObj.RecordError(errmsg)

        if(raise_except):
            raise ExModem(errmsg)

    def set_tx_enabled_state(self, boolVal):

        self.tx_enabled = boolVal

    def get_tx_enabled_state(self):

        return self.tx_enabled

    def set_rx_enabled_state(self, boolVal):

        self.rx_enabled = boolVal

    def get_rx_enabled_state(self):

        return self.rx_enabled

    def check_for_crash(self):
        crash_detect = 0
        mode = self.query_mode()
        if mode == 1:
            logging.info("crash detected!")
            crash_detect = 1
        return crash_detect


    def open (self):
        kwargs = { 'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'timeout': self.timeout }
        loggerModem = logging.getLogger(__name__ + 'open')
        #serObj = serial.Serial(port=self.modemPortNum_zero_index, timeout = self.timeout)
        serObj = serial.Serial(port=self.modemPortNum_zero_index, **kwargs)
        loggerModem.debug("%s opened" %serObj.portstr)
        return serObj

    def close(self):
        loggerModem = logging.getLogger(__name__ + 'close')
        if self.serObj:
            self.serObj.close()
            loggerModem.debug("%s closed" %self.serObj.portstr)
            self.serObj = None
        else:
            if sys.platform in ['cygwin', 'win32']:
                loggerModem.debug("COM%s already closed or not opened" %(self.modemPortNum_zero_index + 1))
            else:
                loggerModem.debug("%s already closed or not opened" %self.modemPortNum_zero_index)

    def get_build_info(self):
        try:
            cl_str = ""
            self.send_cmd(cmd_str="AT+GMR")
            res = self.read_response()
            cl_str = self.extract_build_cl(res)
            return cl_str
        except:
            print "Not able to query modem for the build CL"
            return cl_str

    def extract_build_cl(self, str):
        loggerModem = logging.getLogger(__name__ + 'extract_build_cl')
        build_cl_str = ""
        m_obj = re.search(r'(CL\d+)', str, re.I)
        if m_obj:
            build_cl_str = m_obj.group(1)
            loggerModem.info("build CL is %s" %build_cl_str)
        else:
            loggerModem.info("not able to get the build CL")

        return build_cl_str

    def extract_row_col (self,str,row,col):
        loggerModem = logging.getLogger(__name__ + 'extract_row_col')
        rows = str.split('\n')
        split_list = re.split('[, :]',rows[row])
        list = [x for x in split_list if x not in ['',':']]
        return list[col]

    def extract_col_list (self,str,rowlist,col):
        loggerModem = logging.getLogger(__name__ + 'extract_col_list')
        retlist = []
        for row in rowlist:
            retlist.append(self.extract_row_col(str,row,col))
        return retlist

    def extract_row_list (self,str,row,collist):
        loggerModem = logging.getLogger(__name__ + 'extract_row_list')
        retlist = []
        for col in collist:
            retlist.append(self.extract_row_col(str,row,col))
        return retlist

    def get_afc_val(self):
        self.send_cmd(cmd_str="AT%afc?")
        res = self.read_response()
        mobj=None
        m_obj = re.search(r'AFC(\s*):(\s*)(\d+)', res, re.I)
        if m_obj:
            afc_val = m_obj.group(3)
            return afc_val
        return None

    def set_afc_val(self, val):
        self.send_cmd_rd_response(cmd_str="AT%%afc=%s" %val)

    def send_cmd (self, cmd_str):
        loggerModem = logging.getLogger(__name__ + 'send_cmd')
        text_str = "AT command"
        loggerModem.debug("send_cmd(): %-15s:\t%s" %(text_str, cmd_str))
        cmd_str = cmd_str + "\r"
        self.serObj.write(cmd_str)      # write a string

    def read_response(self):
        loggerModem = logging.getLogger(__name__ + 'send_cmd')
        res = self.serObj.read(200)
        loggerModem.debug("read_response(): %s" %res)
        return res

    def extract_modem_mode(self, str):
        modeNum = -1
        m_obj = re.search(r'mode:?\s*(\d)', str, re.I)
        if m_obj:
            modeNum = m_obj.group(1)
            print "modem mode is %s" %modeNum
        else:
            print "not able to get the modem mode"

        return modeNum

    def query_mode(self):
        mode = -1
        try:
            self.send_cmd(cmd_str="at%mode?")
            res = self.read_response()
            mode = extract_modem_mode(res)
        except:
            print "Not able to query the mode of the modem"
            print "likely modem crash"
            mode = 1

        return int(mode)

    def check_state(self):

        state = 0

        loggerModem = logging.getLogger(__name__ + 'check_state')
        loggerModem.info ("Checking the modem state")
        auto_detect_modem_port_num = auto_detect_port("Modem_port", suppressPrint=1)


        if auto_detect_modem_port_num != -1:
            # check for change in modem port
            if sys.platform in ['cygwin', 'win32']:
                if self.modemPortNum_zero_index + 1 != auto_detect_modem_port_num:
                    print "Modem port change detected"
                    print "Initial modem port was COM%s, new modem port is COM%s" %(self.modemPortNum_zero_index + 1, auto_detect_modem_port_num)


            # check for AT port
            auto_detect_AT_port_num = auto_detect_port("at_port", suppressPrint=1)
            if auto_detect_AT_port_num == -1 :
                return ec.ERRCODE_AT_PORT

            # check modem mode
            mode = self.query_mode()
            if mode == 0:
                return state
            else:
                return ec.ERRCODE_WRONG_MODE

        else:
            return (ec.ERRCODE_COM_PORT_DETECT)

    def get_chip_id(self):
        loggerModem = logging.getLogger(__name__ + 'get_chip_id')
        chip_id = ""
        try:
            self.send_cmd(cmd_str="at%chipid")
            res = self.read_response()
            chip_id = self.extract_chip_id(res)
            loggerModem.info ("chip id is %s" %chip_id)
            print"chip id is %s" %chip_id
            return chip_id
        except:
            loggerModem.error ("Not able to query modem for the chip id")
            print "Not able to query modem for the chip id"
            return chip_id

    def extract_chip_id(self, str):
        loggerModem = logging.getLogger(__name__ + 'extract_chip_id')
        m_obj = re.search(r'chip\s*id\s*[:|=]\s*(\w+)', str, re.I)
        if m_obj:
            chip_id = m_obj.group(1)
            loggerModem.debug ("chip id is %s" %chip_id)
        else:
            loggerModem.debug ("no match")
            chip_id = ""

        return chip_id

    def change_timeout(self, timeout_s):
        loggerModem = logging.getLogger(__name__ + 'change_timeout')
        loggerModem.debug("change serial connection timeout to %s" %timeout_s)
        self.serObj.timeout = timeout_s

    def restore_timeout(self):
        loggerModem = logging.getLogger(__name__ + 'restore_timeout')
        loggerModem.debug("restoring serial connection timeout to %s" %self.timeout)
        self.serObj.timeout = self.timeout

    def sendCmdList(self, cmd_l, ret_msg_only=False):

        loggerModem = logging.getLogger(__name__ + 'sendCmdList')
        report=""

        NON_BLOCKING_TIMEOUT = 0

        for cmd_str in cmd_l:
            #loggerModem.debug("Sending CMD : %s" % cmd_str)

            if cmd_str.lower() == 'at+cfun=0':
                self.change_timeout(NON_BLOCKING_TIMEOUT)
                (ret, msg) = self.send_cmd_rd_response(cmd_str)

            elif cmd_str.lower() == 'at+cfun=1':
                self.change_timeout(NON_BLOCKING_TIMEOUT)
                (ret, msg) = self.send_cmd_rd_response(cmd_str)
                self.restore_timeout()

            else:

                (ret, msg) = self.send_cmd_rd_response(cmd_str)

            if (ret == 1):
                errmsg = "Error response from %s" % cmd_str
                loggerModem.error(errmsg)
                self.RecordError(errmsg,raise_except=True)
            elif (ret == 2):
                errmsg = "No response from %s" % cmd_str
                loggerModem.error(errmsg)
                self.RecordError(errmsg)

            report += ("Response for CMD(%s) : CODE = %s  MSG = %s" % (cmd_str, ret, msg))

        if ret_msg_only:
            return msg
        else:
            return report

    def getInfo(self):

        loggerModem = logging.getLogger(__name__ + 'getInfo')
        cmd_l = [r'AT%IDBGTEST']
        report = self.sendCmdList(cmd_l)
        report=''.join((report.split('\n'))[1:-3])
        report = report.strip()
        self.modemInfo=report
        return self.modemInfo

    def funcON(self):

        loggerModem = logging.getLogger(__name__ + 'funcON')
        loggerModem.info("Enable modem full functionality")

        """
        cmd_l = [ r'at+cfun=0',
                  r'at%inwmode=0,U,1',
                  r'at%%inwmode=1,U%s,1' % (band) ,
                  r'at%%isimemu=%s' % (self.simulate_usim),
                  r'at+cfun=1']
        """
        cmd_l = [ r'at+cfun=1']

        self.sendCmdList(cmd_l)

    def set_usim(self):
        loggerModem = logging.getLogger(__name__ + 'set_usim')
        cmd_l = [ r'at%%isimemu=%s' % (self.simulate_usim)]
        self.sendCmdList(cmd_l)

    def set_preferred_rat(self, rat="UTRAN", band=1):
        loggerModem = logging.getLogger(__name__ + 'set_preferred_rat')
        if rat == "UTRAN":
            loggerModem.info("setting preferred RAT=UTRAN, band = %s" %band)
            cmd_l = [ r'at%inwmode=0,U,1',
                      r'at%%inwmode=1,U%s,1' % (band) ]
            self.sendCmdList(cmd_l)
        else:
            print "RAT %s is not supported, no preference of RAT or band will be set!" %rat


    def funcOff(self):

        loggerModem = logging.getLogger(__name__ + 'funcOff')
        loggerModem.info("Disable modem full functionality")
        cmd_l = [ r'at+cfun=0']
        response = self.sendCmdList(cmd_l)
        return response


    def set_rat_band(self, rat='3g', band = 1):
        loggerModem = logging.getLogger(__name__ + 'set_rat_band')

        if rat.upper() == '3G' or rat.upper() == 'LTE':
            loggerModem.info("RAT=%s, band=%s" %(rat.lower(),band))
            cmd = r'at%%%sband=%s' %(rat.lower(), band)
            cmd_l = [cmd]
            self.sendCmdList(cmd_l)
        else:
            self.RecordError('Rat %s is not supported' %band)

    def set_freqMHz(self,direction='tx',freqMHz=1950):
        loggerModem = logging.getLogger(__name__ + 'set_freqMHz')
        loggerModem.info('set frequency %s MHz' %freqMHz)
        cmd = r'at%%%s%s=%s' %("rf",direction,freqMHz)
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def enable_tx(self):
        self.set_tx_enabled_state(boolVal=1)
        loggerModem = logging.getLogger(__name__ + 'enable_tx')
        loggerModem.info('enable Tx')
        cmd = 'at%%%stxenable=on' %"rf"
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def disable_tx(self):
        loggerModem = logging.getLogger(__name__ + 'disable_tx')
        if self.get_tx_enabled_state():
            loggerModem.info('disable Tx')
            cmd = 'at%%%stxenable=off' %"rf"
            cmd_l = [cmd]
            self.sendCmdList(cmd_l)
            self.set_tx_enabled_state(boolVal=0)
        else:
            loggerModem.info('modem Tx already disabled')
            loggerModem.info('AT command will not be sent again to modem')

    def enable_rx(self,ant='m'):
        self.set_rx_enabled_state(boolVal=1)
        loggerModem = logging.getLogger(__name__ + 'enable_rx')
        loggerModem.info('enable Rx')
        cmd = 'at%%%srxenable=%s,on' %("rf",ant.lower())
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def disable_rx(self,ant='b'):
        loggerModem = logging.getLogger(__name__ + 'disable_rx')
        if self.get_rx_enabled_state():
            loggerModem.info('disable Rx')
            cmd = 'at%%%srxenable=%s,off' %("rf",ant.lower())
            cmd_l = [cmd]
            self.sendCmdList(cmd_l)
            self.set_rx_enabled_state(boolVal=0)
        else:
            loggerModem.info('modem rx already disabled')
            loggerModem.info('AT command will not be sent again to modem')

    def disable_tx_and_rx_unconditionally(self):
        loggerModem = logging.getLogger(__name__ + 'disable_tx_and_rx_unconditionally')
        loggerModem.info('disable Rx+Tx')
        cmd_l = ['at%rftxenable=off', 'at%rfrxenable=b,off']
        self.sendCmdList(cmd_l)
        self.set_tx_enabled_state(0)
        self.set_rx_enabled_state(0)

    def send_ul_pattern(self):
        loggerModem = logging.getLogger(__name__ + 'send_ul_pattern')
        loggerModem.info('send uplink pattern')
        cmd_l = [r'at%txpattern=fn,uplink']
        self.sendCmdList(cmd_l)

    def send_ul_pattern_arb(self,patt_type='dc',max_i=370,min_i=-370,max_q=370,min_q=-370,n_samples=40,offset_q=10):
        loggerModem = logging.getLogger(__name__ + 'send_ul_pattern')
        loggerModem.info('send uplink pattern')
        cmd1 = 'at%%txpattern=fn,%s' % patt_type
        cmd2 = 'at%%txpattern=max_i,%d,min_i,%d,max_q,%d,min_q,%d' % (max_i,min_i,max_q,min_q)
        cmd3 = 'at%%txpattern=samples,%d,offset_q,%d' % (n_samples,offset_q)
        cmd_l = [cmd1,cmd2,cmd3]
        self.sendCmdList(cmd_l)

    def set_txagc_dbm(self, value = -10):
        loggerModem = logging.getLogger(__name__ + 'set_txagc_dbm')
        loggerModem.info('set agc dbm value to %s' %value)
        cmd = 'at%%%stxagc=driver,%s' %("rf", value)
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def set_txagc_direct(self, value = 100):
        loggerModem = logging.getLogger(__name__ + 'set_txagc_direct')
        loggerModem.info('set agc direct value to %s' %value)
        cmd = 'at%%%stxagc=direct,%s,1' %("rf", value)
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def query_txagc (self):
        loggerModem = logging.getLogger(__name__ + 'query_txagc')
        loggerModem.info('query tx agc value')
        cmd = 'at%rftxagc?'
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        dac_val = self.extract_row_col(ret,row=1,col=1)

        return int(dac_val)

    def set_rxagc_auto (self,ant='m'):
        loggerModem = logging.getLogger(__name__ + 'set_rxagc_auto')
        loggerModem.info('set rx agc to auto')
        cmd = 'at%%rfrxagc=%s,auto' % ant.lower()
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def set_rxagc_manual (self,ant='m',be_val=10,fine_i=0,fine_q=0,fe_val=1):
        loggerModem = logging.getLogger(__name__ + 'set_rxagc_manual')
        loggerModem.info('set rx agc to manual %s' % be_val)
        cmd = 'at%%rfrxagc=%s,%d,%d,%d,%d' % (ant.lower(),be_val,fe_val,fine_i,fine_q)
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def query_rxagc (self,ant='m',agc_val='backend'):
        agc_val_col = {'backend':3,'fine_i':4,'fine_q':5}
        loggerModem = logging.getLogger(__name__ + 'query_rxagc')
        loggerModem.info('query rx agc value')
        cmd = 'at%rfrxagc?'
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        main_agc = self.extract_row_col(ret,row=1,col=agc_val_col[agc_val])
        div_agc  = self.extract_row_col(ret,row=2,col=agc_val_col[agc_val])

        if ant == 'm':
            return int(main_agc)
        else:
            return int(div_agc)

    def query_rxdata_antpower (self,ant='m',n_samples=2000):
        loggerModem = logging.getLogger(__name__ + 'query_rxdata_antpower')
        loggerModem.info('query rxdata antpower value')
        cmd = 'at%%rxdata=%s,antpower,%d' % (ant,n_samples)
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        antpower = self.extract_row_col(ret,row=1,col=6)
        return float(antpower)

    def query_rxdata_pwr_per_lsb (self,ant='m',n_samples=2000):
        loggerModem = logging.getLogger(__name__ + 'query_rxdata_pwr_per_lsb')
        loggerModem.info('query rxdata power per lsb value')
        cmd = 'at%%rxdata=%s,power,%d' % (ant,n_samples)
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        pow_per_lsb = self.extract_row_col(ret,row=2,col=7)
        return float(pow_per_lsb)

    def query_rxdata_iq_pow_from_ssi_ssq (self,ant='m',n_samples=1000):
        loggerModem = logging.getLogger(__name__ + 'query_rxdata_pwr_per_lsb')
        loggerModem.info('query rxdata power per lsb value')
        cmd = 'at%%rxdata=%s,sum,%d' % (ant,n_samples)
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        ssi = self.extract_row_col(ret,row=1,col=9)
        ssq = self.extract_row_col(ret,row=1,col=12)
        sum = float(ssi)/n_samples + float(ssq)/n_samples
        return 10*math.log(sum,10)

    def query_rxdata_raw (self,ant='m',n_samples=20):
        loggerModem = logging.getLogger(__name__ + 'query_rxdata_raw')
        loggerModem.info('query rxdata raw values')
        cmd = 'at%%rxdata=%s,raw,%d' % (ant,n_samples)
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        #Data starts at row 2 - Col0:I Col1:Q
        i_data = self.extract_col_list(ret,rowlist=range(2,n_samples+2),col=0)
        q_data = self.extract_col_list(ret,rowlist=range(2,n_samples+2),col=1)
        i_data = [int(x) for x in i_data]
        q_data = [int(x) for x in q_data]
        return i_data,q_data

    def query_txdata_raw (self,n_samples=20):
        loggerModem = logging.getLogger(__name__ + 'query_txdata_raw')
        loggerModem.info('query txdata raw values')
        cmd = 'at%%txdata=raw,%d' % n_samples
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        #Data starts at row 2 - Col0:I Col1:Q
        i_data = self.extract_col_list(ret,rowlist=range(2,n_samples+2),col=0)
        q_data = self.extract_col_list(ret,rowlist=range(2,n_samples+2),col=1)
        i_data = [int(x) for x in i_data]
        q_data = [int(x) for x in q_data]
        return i_data,q_data

    def query_temperature (self,temp_sensor=0):
        loggerModem = logging.getLogger(__name__ + 'query_temperature')
        loggerModem.info('query temperature values')
        cmd = 'at%temp?'
        cmd_l = [cmd]
        ret = self.sendCmdList(cmd_l, ret_msg_only=True)
        #Data starts at row 2 - Col0:I Col1:Q
        tempadc = self.extract_col_list(ret,rowlist=range(1,4+1),col=2)
        return tempadc[temp_sensor]

    def set_rb(self, direction, num_rb):
        """
        set number of RB's for UL and DL
        BW's supported [5, 10, 15, 20], corresponding to max RB's of
                       [25, 50, 75, 100]
        """
        try:
            allowed_dict = {'UL':'n_rb_ul', 'DL':'n_rb_dl'}
            dir_str = allowed_dict[direction.upper()]
            cmd = 'at%%txparam=%s, %s' %(dir_str, num_rb)
            cmd_l = [cmd]
            self.sendCmdList(cmd_l)
        except IndexError:
            errMsg = ('direction %s is not supported' %direction)
            errMsg += ('possible values are %s' %allowed_dict.keys())
            self.RecordError(errMsg)

    def set_rb_start(self, rb_offset=0):
        cmd = 'at%%txparam=rb_start,%s' %rb_offset
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def set_rb_len(self, rb_len):
        """
        set rabio bearer len
        rb_offset + rb_len <= num_rb
        """
        cmd = 'at%%txparam=rb_len, %s' %rb_len
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)

    def set_rx_bw(self, rx_bw):

        cmd = 'at%%rxparam=rate, %dmhz' % rx_bw
        cmd_l = [cmd]
        self.sendCmdList(cmd_l)


    def set_ud_config(self, ud_config=1):
        """
        Set Uplink-Downlink configuration for TD-LTE.
        Supported: 1..6, "TEST0", "TEST1"
        """
        if not (ud_config=="TEST0" or ud_config=="TEST1"):
            ud_config = "STD" + str(ud_config)
        cmd = 'at%%txparam=ud_config, %s' %ud_config
        self.sendCmdList([cmd])

    def set_special_sf_config(self, special_sf_config=0):
        """
        Set Special subframe configuration for TD-LTE.
        Supported: 0..8
        """
        cmd = 'at%%txparam=special_sf_config, %s' %special_sf_config
        self.sendCmdList([cmd])

    def set_ul_timing_advance(self, ul_timing_advance=0):
        """
        Uplink timing advance.
        Supported: -624..20512
        """
        cmd = 'at%%txparam=ul_timing_advance, %s' %ul_timing_advance
        self.sendCmdList([cmd])

    def send_cmd_rd_response  ( self,
                                cmd_str=r'AT'):
        """
        Send AT command, cmd_str
        Check response, rsp_str
        0, denotes good response
        1, denotes unexpected or incorrect response
        """
        loggerModem = logging.getLogger(__name__ + 'send_cmd_rd_response')
        text_str = "AT command"
        loggerModem.debug("%-15s:\t%s" %(text_str, cmd_str))
        cmd_str = cmd_str + '\r\n'
        ok_resp = 'OK'
        err_resp = 'ERROR'
        reg_expr_ok  = r'\b' + re.escape(ok_resp) + r'\b'
        reg_expr_err = r'\b' + re.escape(err_resp) + r'\b'


        self.serObj.write(cmd_str)      # write a string

        timeout_sec = 5
        remaining_time = timeout_sec
        poll_time_sec=1
        response = ""

        while remaining_time > 0:
            response = self.serObj.read(2048)
            loggerModem.debug("remaining time %s" %remaining_time)
            matchObjOk  = re.search (reg_expr_ok,  response, re.M|re.I)
            matchObjErr = re.search (reg_expr_err, response, re.M|re.I)
            if matchObjOk or matchObjErr:
                break
            else:
                time.sleep(poll_time_sec)
                remaining_time -= poll_time_sec

        if matchObjOk:
            text_str = "Response"
            loggerModem.debug ("%-15s:\t%s" %(text_str, matchObjOk.group()))
            return (0, response)
        elif matchObjErr:
            text_str = "Response"
            loggerModem.debug ("%-15s:\t%s" %(text_str, matchObjErr.group()))
            return (1, response)
        else:
            loggerModem.info("OK or ERROR strings not found in the response message")
            return (2, response)


    def core_dump(self):
        """
        Retrieve the coredump following a modem crash
        """
        loggerModem = logging.getLogger(__name__ + 'core_dump')
        cmd_l=[r'at%debug=0', r'at%debug=2']
        cmd_str='\r\n'.join(cmd_l)

        text_str = "AT command"
        if self.dumpfile:
            loggerModem.debug("Core file : %s" % self.dumpfile)
            loggerModem.debug("%-15s:\t%s" %(text_str, cmd_str))
            with open(self.dumpfile, 'wb') as fd:
                cmd_str = cmd_str + '\r\n'
                self.serObj.write(cmd_str)      # write a string
                len_rd=0
                response = self.serObj.read(2**16)
                while len(response)>0:
                    len_rd += len(response)
                    loggerModem.debug("read %s bytes, current_len=%s" % (len(response), len_rd))
                    fd.write(response)
                    response = self.serObj.read(2**16)
            loggerModem.info("Created core dump: %s" % self.dumpfile)
        else:
            loggerModem.info("No core dump as no dump file specified!")

    def crash_simulation(self):

        loggerModem = logging.getLogger(__name__ + 'crash_simulation')

        loggerModem.info("Forced crash simulation")

        self.send_cmd(cmd_str='AT%IDBGTEST=1')

        rf_cf.pause(duration_s=60, poll_time_sec=5, desc="Wait for modem to crash")

        return


if __name__ == '__main__':

    import logging

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'

    loglevel = 'DEBUG'

    cfg_multilogging(loglevel, logfile)

    logger=logging.getLogger(logname)

    set_modem_mode(mode = rf_global.FACTORY_TEST_MODE)
    modeminfo = query_build_info_from_modem()
    changelist = get_build_cl_from_modem(modeminfo)
    platform = get_platform_from_modem(modeminfo)

    print "Changelist %s, Platform %s" % (changelist,platform)



