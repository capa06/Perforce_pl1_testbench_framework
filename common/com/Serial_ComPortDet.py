#-------------------------------------------------------------------------------
# Name:        comPortDet.py
# Purpose:
#
# Author:      Joash Robinson, Francesco Saracino
#
# Created:     16/04/2014
# Copyright:   (c) NVIDIA 2014
#-------------------------------------------------------------------------------
import os
import sys
import re
import logging
import time
import serial
if sys.platform in ['cygwin', 'win32']:
    import _winreg as winreg

import traceback

try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
#sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))




def extract_portnum(portNumStr='COM17'):
    portNum = None
    m_obj = re.search(r'COM(\d+)', portNumStr, re.I)
    if m_obj:
        portNum = m_obj.group(1)
        return int(portNum)
    else:
        portNum = None
    return portNum


def get_last_port(portList):
    position = -1
    lastPortNum = portList[-1]
    for position, port in enumerate(portList):
        if port == lastPortNum:
            return int(position)
    return position

def auto_detect_port_win(portName, suppressPrint):
    logger=logging.getLogger('auto_detect_port_win')

    usb_enum_dict = {'MODEM_PORT':'0', 'AT_PORT':'1', 'LOGGING_PORT':'2'}

    try:
        enum_instanceVal = usb_enum_dict[portName.upper()]
    except KeyError:
        logger.warning("%s is not supported" % portName)
        return None
    try:
        path = 'SYSTEM\\CurrentControlSet\\Services\\usbser\\Enum'
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        logger.error("not able to detect port")
        return None

    try:
        # get number of vid_pid instances
        instanceCount, instanceType = winreg.QueryValueEx (hkey, 'count')
        vid_pid_list = []
        # put vid_pid instances into a list
        for index in range (int(instanceCount)):
            value, dummy = winreg.QueryValueEx (hkey, str(index))
            vid_pid_list.append(value)
        # order the list because on rare occasions the list of
        # vid and pid are not listed in the corrcet order i.e
        #VID_1983&PID_1002&MI_02\7&39639c3&0&0002
        #VID_1983&PID_1004&MI_02\7&39639c3&0&0004
        #VID_1983&PID_1002&MI_06\7&39639c3&0&0006
        # this order can be different and it looks like the modem
        # is laways the first one in the sorted list
        sorted_vid_pid_list = sorted(vid_pid_list)
        value = sorted_vid_pid_list[int(enum_instanceVal)]
        vid_pid = value.split('\\')[1]  # get vid and pid from value list
        instance = value.split('\\')[2] # get vid/pid instance from value list

        # now use the above values to get the correct entry into USB enum list
        # of the windows registry
        deviceParamsPath = os.path.join('SYSTEM\CurrentControlSet\Enum\USB',
                                        vid_pid, instance, 'Device Parameters' )
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, deviceParamsPath)
        portStr = ""
        portStr, dummy = winreg.QueryValueEx (hkey, "PortName")

    except Exception:
        #print traceback.format_exc()
        if not suppressPrint:
            logger.info("Auto detection of %s com port failed" % portName)
        else:
            pass
        return None

    if portStr:
        portNum = extract_portnum(portStr)
    else:
        return None

    if not suppressPrint:
        logger.info("Auto detection SUCCESS port: %s" % portStr)

    return portNum



def auto_detect_port_linux(portName):
    import subprocess

    logger=logging.getLogger('auto_detect_port_linux')

    portName = portName.upper()
    portMap  = { 'MODEM_PORT':0, 'AT_PORT':1, 'LOGGING_PORT':2 }

    try:
        portIndex = int(portMap[portName])
    except:
        logger.error("%s is unsupported" %portName)
        return None

    # Retrieve the list of the available ttyACM ports
    devnull = open(os.devnull, 'wb')
    proc    = subprocess.Popen("ls /dev/ttyACM*", shell=True, stdout=subprocess.PIPE, stderr=devnull) # Retrieve the list if the ttyUSB
    cmd_out = proc.stdout.readlines()
    devnull.close()
    if (not cmd_out):                                            # If empty no ttyUSB detected
        logger.debug('No active ttyACM detected')
        return None

    # Remove the newline at the end
    ttyACM_l =[x.rstrip(os.linesep) for x in cmd_out]
    if 1: logger.debug('ttyACM_l          : %s' % ttyACM_l)

    try:
        ttyACM=None
        if portName == 'LOGGING_PORT':
            indexLastPort = get_last_port(ttyACM_l)
            if indexLastPort > 0:
                ttyACM = ttyACM_l[indexLastPort]
            elif indexLastPort == 0 :
                logging.error('Only one port %s found' % ttyACM_l[indexLastPort])
                logging.error('Unlikely to be the logging port')
                return ttyACM
            else:
                logging.error('Fatal error in determining logging port')
        else:
            ttyACM=ttyACM_l[portIndex]

    except IndexError:
        logging.error('%s could not be detected' % portName)
        return ttyACM

    try:
        logger.debug("Checking port : %s" % ttyACM)
        ser = serial.Serial(ttyACM, timeout=10)
        logger.debug(">> PASS")
        logger.debug("Port Name: %s, Map: %s" %(portName, ttyACM))
        ser.close()
    except serial.SerialException:
        ttyACM_selected=None
        logging.debug("Cannot open %s" % ttyACM)
        return ttyACM_selected

    except OSError:
        pass


    return ttyACM



def auto_detect_port(portName, suppressPrint=1):

    logger=logging.getLogger('auto_detect_port')

    detection_str = "Auto port detection of %s" %portName

    if not suppressPrint:
        print detection_str

    logger.debug(detection_str)

    if sys.platform in ['cygwin', 'win32']:
        portNum = auto_detect_port_win(portName, suppressPrint)
        return portNum

    elif sys.platform in ['linux', 'linux2', 'linux3']:
        portNum = auto_detect_port_linux(portName)
        return portNum
    else:
        logger.error("Not supported")
        return None



def poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5, reason=""):

    if reason != "":
        desc = reason
    else:
        desc ="polling modem for active com ports after boot up"

    logger=logging.getLogger('poll_for_port')
    remaining_time = timeout_sec
    found_port   = None
    logger.info("timeout set to %s [sec] : " % (remaining_time) + desc)

    while remaining_time > 0:
        try:
            found_port=auto_detect_port(portName=portName, suppressPrint=1)
            if not found_port is None: break
        except:
            if 1: print traceback.print_exc()
        time.sleep(poll_time_sec)
        remaining_time -= poll_time_sec
        logger.info("remaining time %s" %remaining_time)

    return found_port


if __name__ == '__main__':

    from cfg_multilogging import cfg_multilogging
    cfg_multilogging('DEBUG', 'Serial_ComPortDet.LOG')
    logger=logging.getLogger('Serial_ComPortDet')

    if 1:
        modemPortNum = auto_detect_port("Modem_port")
        if modemPortNum is None:
            logger.error("MODEM port not found")
        else:
            logger.info("Selected MODEM port : %s " % modemPortNum)

        atPortNum = auto_detect_port("at_port")
        if atPortNum is None:
            logger.error("AT port not found")
        else:
            logger.info("Selected AT port : %s " % atPortNum)

        loggingPortNum = auto_detect_port("LOGGING_PORT")
        if loggingPortNum is None:
            logger.error("LOGGING port not found")
        else:
            logger.info("Selected LOGGING port : %s " % loggingPortNum)

    if 0:
        if poll_for_port(portName="Modem_port") is None:
            logger.error("No active serial port found")
    if 0:
        if poll_for_port(portName="at_port") is None:
            logger.error("No active serial port found")
    if 0:
        if poll_for_port(portName="Logging_port") is None:
            logger.error("No active serial port found")



