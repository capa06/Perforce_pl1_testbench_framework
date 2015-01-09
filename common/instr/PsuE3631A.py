#! /usr/bin/env python

#######################################################################################################################
#
# $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/common/instr/PsuE3631A.py#4 $
# $Author: joashr $
# $Revision: #4 $
# $DateTime: 2014/11/26 19:55:32 $
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

# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class Agilent_E3631A(vxi_11_connection):
    default_lock_timeout=5000
    #idn_head="HEWLETT-PACKARD,E3631A,0,2.1-5.0-1.0"


class PsuE3631A(object):
    PSU_MEAS_CHANNEL_L = ['P6V', 'P25V', 'N25V']

    def __init__(self, psu_gwip="0.0.0.0",
                       psu_gpib=5,
                       psu_channel='P6V',
                       max_voltage_V=0,
                       max_current_A=0,
                       psu_reset=1,
                       psu_config=1,
                       psu_name='PSU_E3631A',
                       buffsize=10):

        logger=logging.getLogger('%s._init' % psu_name)
        self.psu_gwip      = psu_gwip
        self.psu_gpib      = 'gpib0,%s' % psu_gpib
        if not psu_channel in self.PSU_MEAS_CHANNEL_L:
            logger.error('Invalid measurement channel %s' % (psu_channel))
            sys.exit(CfgError.ERRCODE_SYS_PSU_FAILURE)
        self.psu_channel   = psu_channel
        self.max_voltage_V = max_voltage_V
        self.max_current_A = max_current_A
        self.psu_name      = psu_name
        self.buffsize      = buffsize

        self.current_mA   = None
        self.voltage_V    = None

        self._open(psu_name)

        if psu_reset:
            self._reset()

        if psu_config:
            self._set(self.psu_channel, self.max_voltage_V, self.max_current_A)

    # ****************************************************
    # Private methods
    # ****************************************************
    def _open(self, psu_name):
        logger=logging.getLogger('%s._open' % self.psu_name)
        self.name = psu_name
        self.dev = Agilent_E3631A(host=self.psu_gwip, device=self.psu_gpib, timeout=2, device_name=self.name, raise_on_err=1)
        logger.debug("Connected to PSU: name=%s, psu_gwip=%s, port=%s" % (self.name, self.psu_gwip, self.psu_gpib))

    def _reset(self):
        logger=logging.getLogger('%s._reset' % self.psu_name)
        self.dev.write("*rst")
        self.dev.write("*cls")
        logger.debug("%s reset completed" % self.psu_name)

    def _set(self, channel, voltage, current):
        logger=logging.getLogger('%s._set' % self.psu_name)
        if channel in self.PSU_MEAS_CHANNEL_L:
            logger.debug("%s settings: channel %s, voltage=%05.3fV, current=%05.3fA" % (self.name, channel, float(voltage), float(current)))
            self.dev.write("INST %s" % channel)
            self.dev.write("CURR %s A" % current)
            self.dev.write("VOLT %s V" % voltage)
        else:
            logger.error('PsuE3631A.set(): Invalid channel %s. Skipping configuration ' % (channel))

    # ****************************************************
    # Public methods
    # ****************************************************
    def on(self):
        logger=logging.getLogger('%s.on' % self.psu_name)
        self.dev.write("OUTP ON")
        logger.debug("%s switched ON" % self.psu_name)

    def off(self):
        logger=logging.getLogger('%s.off' % self.psu_name)
        self.dev.write("OUTP OFF")
        logger.debug("%s switched OFF" % self.psu_name)


    def read_output_state(self):
        self.dev.write("OUTPut:STATE?")
        reading = self.dev.read()
        state = reading[2]
        state = state[:-1]  # strip of last caharacter "\n"
        return int(state)

    def check_voltage_output(self, check_volts = 3.8):
        self.dev.write("MEAS:VOLT:DC? %s" % self.psu_channel)
        reading = self.dev.read()
        voltage = float(reading[2])
        voltage = '%.1f' %voltage
        print "PSU voltage is %s volts" %voltage
        if str(voltage) == str(check_volts):
            print "PSU voltage is at the correct level of %s" %check_volts
            return True
        else:
            return False

    def check_max_current_output(self, check_curr_amps = 5):
        self.dev.write('CURRent?')
        reading = self.dev.read()
        current_amps = int(float(reading[2]))
        print "PSU max current rating is %s amps" %current_amps
        if str(current_amps) == str(check_curr_amps):
            print "PSU max current is at the correct level of %s amps" %check_curr_amps
            return 1
        else:
            return 0

    def read(self):
        logger=logging.getLogger('%s.read' % self.psu_name)

        # Read voltage
        self.dev.write("MEAS:VOLT:DC? %s" % self.psu_channel)
        reading = self.dev.read()
        voltage = float(reading[2])

        # Read current
        self.dev.write("MEAS:CURR:DC? %s" % self.psu_channel)
        reading = self.dev.read()
        current = int(float(reading[2]) * 1000)
        logger.info("%s channel %s : voltage=%05.3fV, current=%.0fmA" % (self.name, self.psu_channel, voltage, current))

        # Update local properties
        self.current_mA = current
        self.voltage_V  = voltage

        return voltage, current

    def insert_pause(self, tsec):
        logger = logging.getLogger('%s.insert_pause' % self.name)
        remaining_time = tsec
        sleep_time   = int(tsec/5) if (tsec > 5) else 1
        logger.info("pause %s [sec]" % tsec)
        while (remaining_time > 0):
            logger.info("  remaining time : %s [sec]" % (remaining_time))
            time.sleep(sleep_time)
            remaining_time -= sleep_time

    def close(self):
        self.dev.disconnect

    def __str__(self):
        print "PSU name   : %s" % self.name
        print "Gateway IP : %s" % self.psu_gwip
        print "GPIB Addr  : %s" % self.psu_gpib
        return ""


#######################################################################################################################

if __name__ == '__main__':

    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)

    logger.debug('START')

    Vmax_V=3.8
    Imax_A=5
    psu_channel='P6V'
    psuname='E3631A_0'

    #import pl1_testbench_framework.jenkins_interface.common.test_config as tg
    psu_gwip=r'10.21.141.107'
    #psu_gwip=tg.get_psugwip()
    psu_gpib=5
    psu_h=PsuE3631A(psu_gwip=psu_gwip,
                    psu_gpib=psu_gpib,
                    psu_channel=psu_channel,
                    max_voltage_V=Vmax_V,
                    max_current_A=Imax_A,
                    psu_reset=1,
                    psu_name=psuname )

    psu_h._set(channel=psu_h.psu_channel,
              voltage=Vmax_V,
              current=Imax_A)
    print psu_h

    if 0:
        # Simulate timeout error
        psu_h.insert_pause(tsec=300)

    psu_h.on()
    raw_input("Check che setting and press [ENTER]")

    # This may take up to 0.5 sec!!!
    t0_msec=int(round(time.time() * 1000))
    if 0:
        (volt, curr) = psu_h.read()
        logger.info("PSU measurement Voltage[V]=%s, Current[mA]=%s" % (volt, curr))
    else:
        psu_h.read()
        logger.info("PSU measurement Voltage[V]=%s, Current[mA]=%s" % (psu_h.voltage_V, psu_h.current_mA))

    t1_msec=int(round(time.time() * 1000))
    logger.info("Elapsed time %s [msec]" % (t1_msec-t0_msec))

    psu_h.off()
    psu_h.close()


    logger.debug('END')


