#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        Agilent_E3631A_Psu
# Purpose:     Inherits from base class
#
# Author:      joashr
#
# Created:     31/10/2013

#-------------------------------------------------------------------------------
import os, time, re, sys, logging

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env


from pl1_testbench_framework.common.instr.PsuE3631A import PsuE3631A


class Psu(PsuE3631A):

    def open(self, psu_name):
        self.name = psu_name
        self.gwip = self.psu[psu_name]['IP']
        self.gpib_addr = self.psu[psu_name]['GPIB_PORT']
        self.dev = Agilent_E3631A(host=self.gwip, device=self.gpib_addr, timeout=2, device_name=self.name, raise_on_err=1)
        logging.info("Connected to PSU: name=%s, gwip=%s, port=%s" % (self.name, self.gwip, self.gpib_addr))

    def reset(self):
        self.dev.write("*rst")                  # this sets all output voltages to zero
        self.dev.write("*cls")
        logging.debug("Reset completed")


    def read_output_state(self):
        self.dev.write("OUTPut:STATE?")
        reading = self.dev.read()
        state = reading[2]
        state = state[:-1]  # strip of last caharacter "\n"

        return int(state)

    def check_voltage_output(self, channel='P6V', check_volts = 3.8):
        self.dev.write("MEAS:VOLT:DC? %s" % channel)
        reading = self.dev.read()
        voltage = float(reading[2])
        voltage = '%.1f' %voltage
        print "PSU voltage is %s volts" %voltage
        if str(voltage) == str(check_volts):
            print "PSU voltage is at the correct level of %s" %check_volts
            return 1
        else:
            return 0

    def check_max_current_output(self, channel='P6V', check_curr_amps = 5):
        self.dev.write('CURRent?')
        reading = self.dev.read()
        current_amps = int(float(reading[2]))
        print "PSU max current rating is %s amps" %current_amps
        if str(current_amps) == str(check_curr_amps):
            print "PSU max current is at the correct level of %s amps" %check_curr_amps
            return 1
        else:
            return 0

    def set_max_volts_amps(self, v_max, i_max):
        self.v_max = v_max
        self.i_max = i_max

    def get_max_volts(self):
        return self.v_max

    def get_max_amps(self):
        return self.i_max

    def selftest_switchon(self, vmax, imax):
        logger_00 = logging.getLogger('')
        logger_00.debug('START')
        print self
        self.reset()

        self.on()
        self.set('P6V', vmax, imax)
        time.sleep(1)

        raw_input("Check the setting and press [ENTER]")

        # This may take up to 0.5 sec!!!
        t0_msec=int(round(time.time() * 1000))
        reading=self.read('P6V')
        logging.info("PSU bench configuration: Vmax[V]=%s, Imax[A]=%s :: read back Voltage[V]=%s, Current[mA])=%s" % (Vmax_V, Imax_A, reading[0][0], reading[0][1]))

        t1_msec=int(round(time.time() * 1000))
        logging.info("Elapsed time %s [msec]" % (t1_msec-t0_msec))
        logger_00.debug('END' + __name__)

if __name__ == '__main__':

    from pl1_testbench_framework.common.config.CfgError import CfgError

    from pl1_testbench_framework.common.utils.os_utils import insertPause

    from pl1_testbench_framework.common.com.Serial_ComPortDet import poll_for_port

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)


    from pl1_testbench_framework.common.com.Serial_ComPortDet import poll_for_port

    test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config.xml'])

    import pl1_testbench_framework.wcdma.common.parser.xml_utils as xml_utils
    psugwip = xml_utils.get_psugwip(xml_file = test_config_xml_path)
    psugpib = 5

    code = CfgError()

    psu_name='E3631A_0'

    psu_bench=Psu(psu_name=psu_name,
                  psu_gwip=psugwip,
                  psu_gpib=psugpib,
                  psu_channel='P6V',
                  psu_config=0,
                  psu_reset=0)

    output_state = psu_bench.read_output_state()

    Vmax_V=3.8
    Imax_A=5
    psuname='E3631A_0'

    if output_state == 1:
        logger.info("Power supply is switched on")
        logger.info("Check that the supply voltage is at the correct level of %s volts" %Vmax_V)
        if psu_bench.check_voltage_output(check_volts = Vmax_V):
            logger.info("Power supply is at the correct voltage")
            if poll_for_port(portName="Modem_port", timeout_sec=20, poll_time_sec=1):
                print "modem com port successfully found"
            else:
                print "modem com port not found"
                sys.exit(code.ERRCODE_SYS_MODEM_NO_COM)
        else:
            logger.info("PSU voltage is not at the required level")
            output_state = 0
    else:
        print "Power supply is currently switched off"
        output_state = 0

    if output_state == 0:
        psu_bench._reset()
        psu_bench.on()
        time.sleep(1)

        psu_bench._set(channel='P6V', voltage=Vmax_V, current=Imax_A)

        reading=psu_bench.read()
        logger.info("PSU bench configuration: Vmax[V]=%s, Imax[A]=%s, read back Voltage=%s" % (Vmax_V, Imax_A, reading))

        if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

            print "modem com port successfully found"

            time_secs = 5
            txt = "pausing for %s secs ..." %time_secs
            insertPause(tsec=time_secs, desc=txt)

        else:

            print "modem com port not found after power cycle"

            sys.exit(code.ERRCODE_SYS_MODEM_NO_COM)

    reading=psu_bench.read()

    logger.info("PSU bench configuration: Vmax[V]=%s, Imax[A]=%s, read back Voltage=%s" % (Vmax_V, Imax_A, reading))




