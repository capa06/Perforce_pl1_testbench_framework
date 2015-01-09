#-------------------------------------------------------------------------------
# Name:        modem.py
# Purpose:
#
# Author:      joashr
#
# Created:     16/11/2013
#-----------------------------------------------------------------------------

import serial
import re, sys, os, logging, shutil
import time
import traceback

(abs_path, name)=os.path.split(os.path.abspath(__file__))

dumpfile="dump_%s" % time.strftime("%Y%m%d_%H%M%S", time.localtime())
dump_abs_filename=os.sep.join(abs_path.split(os.sep)[:]+[dumpfile+'.log'])

try:
    import test_env
except ImportError:
    test_env_dir=os.sep.join(abs_path.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env


from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec

import pl1_testbench_framework.common.globals.test_globals as tg

from pl1_testbench_framework.common.utils.os_utils import insertPause

import pl1_testbench_framework.jenkins_interface.common.parser.reg_expr as reg_expr

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

    BOOT_LOADER_MODE = 1

    print "Checking current modem build info prior to mode switch to boot loader mode"

    modemObj = serialComms(timeout = 2)

    status, response = modemObj.send_cmd_rd_response(cmd_str="at+gmr")

    print response

    modemObj.close()

    mode = query_modem_mode()

    if mode == BOOT_LOADER_MODE:

        print "Already in boot loader mode!"

        return tg.SUCCESS

    print "Will try to change modem mode to 1,3"

    try:

        modemObj = serialComms(timeout = 2)

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



        if mode == BOOT_LOADER_MODE:

            print "Successful detection of boot loader mode"

            return tg.SUCCESS

        else:

            print "Unsuccessful detection of boot loader mode"

            return tg.FAIL

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

    icera_tools_bin_path = os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['common', 'icera'])

    get_crash_dump_log(core_dump_dir=core_dump_dir, icera_utils_path=icera_tools_bin_path)


def get_crash_dump_log(core_dump_dir="", icera_utils_path=""):

    from pl1_testbench_framework.common.utils.os_utils import run_script

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

    run_script(cmd)

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

    modemObj = serialComms(timeout = 2)
    at_cmd = r'AT%%MODE=%d' %mode
    print "function %s" %sys._getframe(0).f_code.co_name
    try:
        modemObj.send_cmd_rd_response(cmd_str = at_cmd)
    except:
        #print "Not able to set the modem mode to %s" %mode
        pass

    modemObj.close()

    if poll_for_port(portName="Modem_port", timeout_sec=30, poll_time_sec=5,
                 reason="pausing after mode change"):

        print "modem com port successfully found"

        time_secs = 10

        print "pausing for %s secs ..." %time_secs

        time.sleep(time_secs)

    else:

        print "modem com port not found after modem change"

        sys.exit(ec.ERRCODE_COM_PORT_DETECT)

    modemMode = query_modem_mode()

    if mode == modemMode:

        print "Successful switch to mode %s" %mode

    else:

        print "Unsuccessful switch to mode %s" %mode

        sys.exit(ec.ERRCODE_MODE_SWITCH_FAIL)

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


def check_for_modem_port():

    func_name = sys._getframe(0).f_code.co_name

    logger = logging.getLogger(__name__ + func_name)

    if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

        logger.info("modem com port successfully found")

        insertPause(tsec=10, desc="delay after finding modem port")

        return tg.SUCCESS

    else:

        logger.info("modem com port not found")

        return tg.FAIL

class serialComms:

    INVALID_MODEM_RESPONSE_FORMAT = -100

    SUCCESS = 0

    def __init__( self, timeout = 5, dumpfile="", simulate_usim=0 ):

        self.timeout = timeout
        self.modemInfo = ""
        self.dumpfile=dumpfile

        # note that the return value is 1 based i.e.
        # e.g. modemPortNum = 1, corresponds to COM1
        # for windows os
        if sys.platform in ['cygwin', 'win32']:
            modemPortNum = auto_detect_port("Modem_port")
        else:
            modemPortNum = auto_detect_port("Modem_port", suppressPrint=1)

        if not modemPortNum:

            print "Cannot detect modem port"
            raise Exception

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
                print "Unable to open com port %s" %(self.modemPortNum_zero_index + 1)
            else:
                print "Unable to open com port %s" %(self.modemPortNum_zero_index)
            #raise Exception
            #sys.exit(ec.ERRCODE_COM_PORT_DETECT)
            sys.exit(ec.ERRCODE_SYS_MODEM_NO_COM)


    def check_for_crash(self):
        crash_detect = 0
        func_name = sys._getframe(0).f_code.co_name
        loggerModem = logging.getLogger(__name__ + func_name)
        waitTimeSec = 15
        loggerModem.info("Will wait for %s sec prior to modem crash check" %waitTimeSec)
        time.sleep(waitTimeSec)
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


        if auto_detect_modem_port_num :
            # check for change in modem port
            if sys.platform in ['cygwin', 'win32']:
                if self.modemPortNum_zero_index + 1 != auto_detect_modem_port_num:
                    print "Modem port change detected"
                    print "Initial modem port was COM%s, new modem port is COM%s" %(self.modemPortNum_zero_index + 1, auto_detect_modem_port_num)


            # check for AT port
            auto_detect_AT_port_num = auto_detect_port("at_port", suppressPrint=1)
            if not auto_detect_AT_port_num :
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

    def sendCmdList(self, cmd_l):

        loggerModem = logging.getLogger(__name__ + 'sendCmdList')
        report=""

        NON_BLOCKING_TIMEOUT = 0

        for cmd_str in cmd_l:
            loggerModem.debug("Sending CMD : %s" % cmd_str)

            if cmd_str.lower() == 'at+cfun=0':
                self.change_timeout(NON_BLOCKING_TIMEOUT)
                (ret, msg) = self.send_cmd_rd_response(cmd_str)

            elif cmd_str.lower() == 'at+cfun=1':
                self.change_timeout(NON_BLOCKING_TIMEOUT)
                (ret, msg) = self.send_cmd_rd_response(cmd_str)
                self.restore_timeout()

            else:

                (ret, msg) = self.send_cmd_rd_response(cmd_str)

            if (  ret != 0 ):

                loggerModem.error("Did not receive expected response. Sent: %s" % cmd_str)

            report += ("Response for CMD(%s) : CODE = %s  MSG = %s" % (cmd_str, ret, msg))

        return report

    def _get_response_code(self, response):

        code = 0
        compileObj = re.compile(r'(.*)CODE(\s*)=(\s*)(?P<num>[+-]?\d+)(\s*)(.*)')
        matchObj = compileObj.match(response)
        # check return code from report
        if matchObj:
            # convert return to number
            code =  int(matchObj.group('num'))
            return code
        else:
            print "Debug : response message is in the wrong format"
            print "modem response is :"
            print response
            return self.INVALID_MODEM_RESPONSE_FORMAT


    def getInfo(self):

        MAX_NUM_TRIES = 2
        loggerModem = logging.getLogger(__name__ + 'getInfo')
        cmd_l = [r'AT%IDBGTEST']

        for tries in range (MAX_NUM_TRIES):
            report = self.sendCmdList(cmd_l)
            err_code = self._get_response_code(response=report)
            if err_code == self.SUCCESS:
                break
            else:
                report = ""

        if report == "":
            return report

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
                      r'at%%inwmode=1,U%s,3' % (band) ]
            self.sendCmdList(cmd_l)
        else:
            print "RAT %s is not supported, no preference of RAT or band will be set!" %rat


    def get_supported_band_list(self, rat="WCDMA"):

        self.send_cmd(cmd_str="AT%INWMODE?")
        inwmode_res = self.read_response()

        supported_rat_dict = {'WCDMA':'U',
                              'LTE'  :'E',
                              'GSM'  :'G' }

        try:
            rat_searchStr = supported_rat_dict[rat.upper()]
        except KeyError:
            print "Unsupported rat %s" % rat
            print "Supported rats are %s" % supported_rat_dict.keys()
            return []

        searchStr = "%s\d+" %rat_searchStr
        p = re.compile(searchStr, re.I)
        listStr = p.findall(inwmode_res)
        bandListStr=''.join(listStr)

        searchStr = "\d+"
        p = re.compile(searchStr)
        bandList = p.findall(bandListStr)
        bandList = sorted( [int(x) for x in bandList])
        return bandList


    def enable_all_bands(self, rat="wcdma"):

        supported_rat_dict = {'WCDMA':'U',
                              'LTE'  :'E',
                              'GSM'  :'G' }

        try:
            rat_prefixStr = supported_rat_dict[rat.upper()]
        except KeyError:
            print "Unsupported rat %s" % rat
            print "Supported rats are %s" % supported_rat_dict.keys()
            return []

        cmd = r'AT%%INWMODE=1,%s999,1' %rat_prefixStr

        response = self.send_cmd_rd_response(cmd)
        return response

    def funcOff(self):

        loggerModem = logging.getLogger(__name__ + 'funcOff')
        loggerModem.info("Disable modem full functionality")
        cmd_l = [ r'at+cfun=0']
        response = self.sendCmdList(cmd_l)
        return response


    def send_cmd_rd_response  ( self,
                                cmd_str=r'AT',
                                rsp_str ='ok'):
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

        self.serObj.write(cmd_str)      # write a string

        timeout_sec = 30
        remaining_time = timeout_sec
        poll_time_sec=2
        response = ""

        while remaining_time > 0:
            response = self.serObj.read(2048)
            time.sleep(poll_time_sec)
            remaining_time -= poll_time_sec
            loggerModem.debug("remaining time %s" %remaining_time)
            reg_expr = r'\b' + re.escape(rsp_str) + r'\b'
            matchObj = re.search (reg_expr, response, re.M|re.I)
            if matchObj:
                break

        if matchObj:
            text_str = "Response"
            loggerModem.debug ("%-15s:\t%s" %(text_str, matchObj.group()))
            return (0, response)
        else:
            loggerModem.debug("Ok, string not found in the response message")
            return (1, response)


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

        insertPause(tsec=60, desc="Wait for modem to crash")

        return



if __name__ == '__main__':

    try:
        os.environ['PL1_WCDMA_TEST_ROOT']
    except:
        os.environ['PL1_WCDMA_TEST_ROOT']  = os.sep.join(abs_path.split(os.sep)[:-2]+['pl1_wcdma_testbench'])
        print "os.environ[''PL1_WCDMA_TEST_ROOT']=%s" % os.environ['PL1_WCDMA_TEST_ROOT']

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging
    cfg_multilogging(log_level = "debug")
    band = 1

    modemObj = serialComms(timeout = 15)

    modemObj.crash_simulation()
    modemObj.close()

    results_dir = os.sep.join(os.environ['TEST_SYSTEM_ROOT_FOLDER'].split(os.sep)[:]+['results'])
    if not os.path.isdir(results_dir):
        print "Creating local build folder: %s" %results_dir
        os.makedirs(results_dir)

    icera_tools_path = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera'])
    get_crash_dump_log(core_dump_dir=results_dir, icera_utils_path=icera_tools_path)

    insertPause(tsec=10, desc="waiting for short time after coredump extraction")
    set_modem_mode(mode = 0)


    modemInfo = get_modem_info()
    print modemInfo

    modem_p4WebRevStr = reg_expr.get_p4webrevStringfrom_modem(modemInfo)
    modem_build_cl = reg_expr.get_build_cl_from_modem(modemInfo)

    get_chip_id_wrapper()
    build_cl=get_build_info_wrapper()
    print build_cl

    modemObj = serialComms(timeout = 2, dumpfile = dump_abs_filename)
    modemObj.funcOff()
    modemObj.close()

    modemObj = serialComms(timeout = 2, dumpfile = dump_abs_filename)
    modemObj.funcON()
    modemObj.close()

    modemObj = serialComms(timeout = 2, dumpfile = dump_abs_filename)
    modemObj.funcOff()
    modemObj.close()


    modemObj = serialComms(timeout = 2, simulate_usim=0)
    modem_state = modemObj.check_state()
    if modem_state != 0:
        print "Reboot or flash required"
        print modem_state

    print modemObj.getInfo()

    modemObj.get_build_info()
    modemObj.get_chip_id()

    modemObj.close()

    switch_mode_1_3()


