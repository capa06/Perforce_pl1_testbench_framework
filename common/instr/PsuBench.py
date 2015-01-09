#! /usr/bin/env python

#######################################################################################################################
#
# $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/common/instr/PsuBench.py#4 $
# $Author: joashr $
# $Revision: #4 $
# $DateTime: 2014/11/27 15:03:57 $
#
#######################################################################################################################

# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import time
#import re
import logging

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************

try:
    import test_env
except ImportError:
    (abs_path, name)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(abs_path.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from vxi_11 import vxi_11_connection
from CfgError import CfgError
from PsuE3631A import PsuE3631A


# ********************************************************************
# API functions
# ********************************************************************
def PsuBenchOff(psu_gwip, psu_gpib):
    logger=logging.getLogger('PsuBenchOff')
    psu_h=PsuBench(psu_gwip, psu_gpib, psu_reset=0)
    psu_h.off()
    psu_h.close()
    logger.info("PSU bench is OFF")

def PsuBenchOn(psu_gwip="", psu_gpib=5, setVolts=3.8, Imax_A=5):
    logger=logging.getLogger('PsuBenchOn')
    psu_h=PsuBench(psu_gwip, psu_gpib, psu_reset=1)
    psu_h.on()
    psu_h._set(channel='P6V', voltage=setVolts, current=Imax_A)
    psu_h.close()
    logger.info("PSU bench is ON")

def PsuBenchPowerCycle(psu_gwip, psu_gpib, setVolts=3.8, Imax_A=5):
    logger=logging.getLogger('PowerCycle')
    psu_h=PsuBench(psu_gwip, psu_gpib, psu_reset=1)
    psu_h.off()
    psu_h.insert_pause(10)
    psu_h.on()
    psu_h._set(channel='P6V', voltage=setVolts, current=Imax_A)
    psu_h.close()
    logger.info("PSU bench is ON")

def PsuBenchRead(psu_gwip, psu_gpib, setVolts=3.8, Imax_A=5):
    logger=logging.getLogger('PsuBenchRead')
    psu_h=PsuBench(psu_gwip, psu_gpib, psu_reset=0)
    psu_h.on()
    psu_h._set(channel='P6V', voltage=setVolts, current=Imax_A)
    (volt, curr) = psu_h.read()
    psu_h.close()
    logger.info("read voltage=%.02f[V], current=%.02f[mA] " % (volt, curr))
    return (volt, curr)

def PsuCheckOn(psu_gwip, psu_gpib, check_volts = 3.8, check_curr_amps=5):
    logger=logging.getLogger('PsuCheckOn')
    psu_bench=PsuBench(psu_gwip=psu_gwip, psu_gpib=psu_gpib, psu_reset=0)
    output_state = psu_bench.read_output_state()
    print "output state is %s" % output_state
    if output_state == 1:
        logger.info("Power supply is switched on")
        logger.info("Check that the supply voltage is at the correct level of %s volts" %check_volts)
        if psu_bench.check_voltage_output(check_volts = check_volts):
            logger.info("Voltage is at the correct level, will now check the max current setting")
            if psu_bench.check_max_current_output(check_curr_amps=check_curr_amps):
                logger.info("PSU current is at the correct level")
                output_state = 1
            else:
                logger.info("PSU current is not at the correct level %s amps" %check_curr_amps)
                logger.info("Setting to the correct level")
                psu_bench._set('P6V', check_volts, check_curr_amps)
                output_state = 1
        else:
            print "PSU voltage is not at the required level"
            print "Setting PSU voltage to %s voltages and current to %s amps" %(check_volts, check_curr_amps)
            psu_bench._set(psu_bench.psu_channel, check_volts, check_curr_amps)
            output_state = 1
    else:
        print "Power supply is currently switched off"

    psu_bench.close()

    return output_state


class PsuBench(PsuE3631A):
    #MAX_VOLTAGE_V = 3.8
    #MAX_CURRENT_A = 5
    #PSU_CHANNEL   = 'P6V'

    def __init__(self, psu_gwip, psu_gpib, psu_reset, psu_name='PsuBench'):
        PsuE3631A.__init__(self, psu_gwip=psu_gwip,
                                 psu_gpib=psu_gpib,
                                 psu_channel='P6V',
                                 max_voltage_V=3.8,
                                 max_current_A=5,
                                 psu_reset=psu_reset,
                                 psu_name=psu_name)

#######################################################################################################################

if __name__ == '__main__':

    from pl1_testbench_framework.common.utils.os_utils import insertPause

    from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port

    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)

    logger.debug('START')

    # specify path to xml file if this exists
    test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config.xml'])

    if os.path.isfile(test_config_xml_path):
        import pl1_testbench_framework.wcdma.common.parser.xml_utils as xml_utils
        psu_gwip = xml_utils.get_psugwip(xml_file = test_config_xml_path)
        print psu_gwip
    else:
        psu_gwip=r'10.21.140.206'

    psu_gpib=5

    if 0:
        psu_h=PsuBench(psu_gwip, psu_gpib, psu_reset=1)
        psu_h.on()
        raw_input("Check che setting and press [ENTER]")
        # This may take up to 0.5 sec!!!
        t0_msec=int(round(time.time() * 1000))
        (volt, curr) = psu_h.read()
        logger.info("PSU measurement Voltage[V]=%s, Current[mA]=%s" % (volt, curr))
        t1_msec=int(round(time.time() * 1000))
        logger.info("Elapsed time %s [msec]" % (t1_msec-t0_msec))
        psu_h.off()
        psu_h.close()
    else:
        psu_state_on = PsuCheckOn(psu_gwip=psu_gwip,
                                  psu_gpib=psu_gpib,
                                  check_volts = 3.8,
                                  check_curr_amps=5)
        if psu_state_on:
            print "psu is already switched on - no action required"
            pass
        else:
            PsuBenchOn(psu_gwip=psu_gwip, psu_gpib=5)

            if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):
                print "modem com port successfully found"
            else:
                print "modem com port not found"
                assert False, 'Modem com port is not found after power cycle'
        if 0:
            logger.info("Simulate timeout")
            insertPause(tsec=300)

        insertPause(tsec=10)
        (volt, curr)=PsuBenchRead(psu_gwip, psu_gpib)
        insertPause(tsec=10)

        PsuBenchOff(psu_gwip, psu_gpib)

    logger.debug('END')


