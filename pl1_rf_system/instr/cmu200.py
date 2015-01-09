#! /usr/bin/env python

# Author:      joashr
#
# Created:     21/05/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, time, re,  logging


from vxi_11 import vxi_11_connection


try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-1])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *
from pl1_rf_system.instr.measurementClass import MeasurementClass

def extract_digit_from_rf_conn(conn="RF2"):
    # extract <Num> from RF<Num> string
    p = re.compile(r'RF(\d+)')
    m=p.match(conn)
    if m:
        return m.group(1)
    else:
        raise ExCmu200("cannot extract conn num from %s" %conn)


class rohde_and_schwarz_CMU200(vxi_11_connection):
    default_lock_timeout=5000
    #idn_head="HEWLETT-PACKARD,E3631A,0,2.1-5.0-1.0"
    pass

class CmuControl(object):
    CMU_NAME_L         = ['CMU200', 'E3631A_1']

    def __init__(self, cmu_gwip, cmu_gpib, cmu_name='CMU200', buffsize=10):

        if not cmu_name in self.CMU_NAME_L:
            err_msg = ('must use -p [ %s ]' % ' | '.join(sorted(self.CMU_NAME_L)))
            raise ExCmu200(err_msg)

        self.cmu={ cmu_name: {'IP': r'%s' % cmu_gwip, 'GPIB_PORT' : r'gpib0,%s' % cmu_gpib}}
        try:
            self.open(cmu_name)
        except Exception:
            errMsg = "Not able to connect to Instrument IP : %s GPIB_PORT %s" %(cmu_gwip,cmu_gpib)
            try:
                psugpib="20,1"
                primary_gpib_addr, secondary_gpib_addr = psugpib.split(',')
                errMsg = errMsg + "\nCorresponding to primary GPIB address %s, " %primary_gpib_addr
                errMsg = errMsg + "secondary GPIB address %s" %secondary_gpib_addr
            except:
                pass
            raise ExCmu200(errMsg)

        self.buffsize=buffsize
        self.func_grp_mapping={'WCDMA19UEFDD_Sig':'4', 'WCDMA19UEFDD_NSig':'2'}
        self.func_grp_addr=""



    def close(self):
        logging.info("Closing CMU connection name = %s" % (self.name))
        # go to local
        self.write('*GTL')
        self.dev.disconnect

    def func_grp_reset(self):
        self.write('SYSTem:RESet:All')
        time.sleep(10)

    def get_func_grp_addr(self):
        return self.func_grp_addr

    def get_id(self):
        self.read('*IDN?')
        self.write('*SEC 0')
        return

    def set_wcdma_evm_ctrl(self, num_slots_per_stats_cycle=10):

        self.write('%s;CONFigure:MODulation:EVMagnitude:WCDMa:DPCH:CONTrol:STATistics %s'
                    %(self.get_func_grp_addr(), num_slots_per_stats_cycle))

        self.waitForCompletion()

    def set_wcdma_perr_ctrl(self, num_slots_per_stats_cycle=10):

        self.write('%s;CONFigure:MODulation:PERRor:WCDMa:DPCH:CONTrol:STATistics %s'
                    %(self.get_func_grp_addr(), num_slots_per_stats_cycle))

        self.waitForCompletion()

    def set_wcdma_overview_ctrl(self, num_slots_per_stats_cycle=10):

        self.write('%s;CONFigure:MODulation:OVERview:WCDMa:DPCH:CONTrol:STATistics %s'
                   %(self.get_func_grp_addr(), num_slots_per_stats_cycle))

        self.waitForCompletion()

    def get_evm_meas(self, num_cycles=50):

        loggerInstr=logging.getLogger(__name__ + 'get_evm_meas')

        self.set_wcdma_evm_ctrl(num_slots_per_stats_cycle=num_cycles)

        retryNum = 0
        maxRetry = 3
        evm_meas = []
        evm_meas = ""
        while retryNum <= maxRetry:
            try:
                self.write('%s;INITiate:MODulation:EVMagnitude:WCDMa:DPCH'
                            %(self.get_func_grp_addr()))

                query_str = ('%s;FETCh:MODulation:EVMagnitude:WCDMa:DPCH:STATus?'
                             %self.get_func_grp_addr())

                self.waitForRDY(cmd_query=query_str)

                cmd = '%s;FETCH:MODulation:EVMagnitude:WCDMa:DPCH?'%(self.get_func_grp_addr())
                evm_meas = self.read(cmd)
                break

            except Exception:
                loggerInstr.error (" Not able to read the following")
                loggerInstr.error ("   %s read command \"%s\"" % (self.name, cmd))
                if retryNum != maxRetry:
                    print "Retry %s of %s" %(retryNum+1, maxRetry)
                else:
                    print "Fata error!"
                    errMsg = "Not able to read response to %s" %cmd
                    raise ExCmu200(errMsg)
                time.sleep(4)
                retryNum +=1

        time.sleep(1)

        evm_limit = self.read('%s;CALCulate:MODulation:EVMagnitude:WCDMa:DPCH:MATChing:LIMit?'
                              %(self.get_func_grp_addr()))

        return evm_meas, evm_limit


    def get_wcdma_mod_overview_results(self):

        self.set_wcdma_overview_ctrl(num_slots_per_stats_cycle=50)

        self.write('%s;INITiate:MODulation:OVERview:WCDMa:DPCH'
                   %(self.get_func_grp_addr()))

        query_str = '%s;FETCh:MODulation:OVERview:WCDMa:DPCH:STATus?' %self.get_func_grp_addr()

        self.waitForRDY(cmd_query=query_str)

        wcdma_overview_meas = self.read('%s;FETCH:MODulation:OVERview:WCDMa:DPCH?'
                                         %self.get_func_grp_addr())



        time.sleep(1)

        wcdma_overview_limit = self.read('%s; CALCulate:MODulation:OVERview:WCDMa:DPCH:MATChing:LIMit?'
                                          %(self.get_func_grp_addr()))

        return wcdma_overview_meas, wcdma_overview_limit


    def get_perr_meas(self):

        self.set_wcdma_perr_ctrl(num_slots_per_stats_cycle=50)

        self.write('%s;INITiate:MODulation:PERRor:WCDMa:DPCH'
                    %(self.get_func_grp_addr()))

        query_str = ('%s;FETCh:MODulation:PERRor:WCDMa:DPCH:STATus?'
                      %self.get_func_grp_addr())

        self.waitForRDY(cmd_query=query_str)

        phase_meas = self.read('%s;FETCH:MODulation:PERRor:WCDMa:DPCH?'
                                %(self.get_func_grp_addr()))

        phase_limit = self.read('%s;CALCulate:MODulation:PERRor:WCDMa:DPCH:MATChing:LIMit?'
                              %(self.get_func_grp_addr()))

        return phase_meas, phase_limit

    def get_iq_analyz_meas(self):

        self.write('%s;INITiate:MODulation:IQANalyzer:WCDMa:DPCH'
                    %self.get_func_grp_addr())

        time.sleep(1)

        iq_meas = self.read('%s;READ:MODulation:IQANalyzer:WCDMa:DPCH?'
                             %(self.get_func_grp_addr()))



    def open(self, cmu_name):
        self.name = cmu_name
        self.gwip = self.cmu[cmu_name]['IP']
        self.gpib_addr = self.cmu[cmu_name]['GPIB_PORT']
        self.dev = rohde_and_schwarz_CMU200(host=self.gwip, device=self.gpib_addr, timeout=100, device_name=self.name, raise_on_err=1)
        logging.info("Connected to CMU: name=%s, gwip=%s, port=%s\n" % (self.name, self.gwip, self.gpib_addr))
        self.reset()
        logging.debug("Reset completed")

    def read(self, command):

        loggerInstr=logging.getLogger(__name__ + 'cmu.read')
        loggerInstr.debug ("   %s read command \"%s\"" % (self.name, command))

        numRetry = 0
        maxRetry = 3

        self.dev.write(command)
        while numRetry < maxRetry:
            reading = self.dev.read()[2].strip()
            if reading != "":
                break
            elif numRetry == maxRetry:
                loggerInstr.error (" Not able to read the following")
                loggerInstr.error ("   %s read command \"%s\"" % (self.name, command))
                loggerInstr.error ("   %s read response \"%s\"" % (self.name, reading))
                break
            time.sleep(0.5)
            numRetry +=1

        lettercount = 400
        readingshort = reading[0:lettercount]
        if len(reading)>lettercount:
            loggerInstr.debug ("   %s read response \"%s\"..........." % (self.name, readingshort))
        else:
            loggerInstr.debug ("   %s read response \"%s\"" % (self.name, reading))
        return reading

    def reset(self):
        #self.write("*rst")                  # resets the instrument
        self.write("*CLS")
        self.read('*OPC?')
        self.waitForCompletion()

    def set_func_grp_addr(self, func_grp='WCDMA19UEFDD_NSig'):
        self.func_grp_addr = self.func_grp_mapping[func_grp]


    def set_input_conn(self, conn="RF2"):
        if conn in ["RF1", "RF2", "RF3", "RF4"]:
            self.write('%s;INP:STAT %s' %(self.get_func_grp_addr(),conn))
        else:
            err_msg = ('RF connector : %s not supported' %conn)
            raise ExCmu200(err_msg)


    def set_default_levels(self):
        self.write('%s;DEFault:LEVel ON'
                   %self.get_func_grp_addr())
        return

    def set_output_atten(self, value_dB = 0.5, conn="RF2"):
        valid_list = ["RF1", "RF2", "RF3"]
        if conn in valid_list:
            con_num = extract_digit_from_rf_conn(conn)
            self.write('%s;SENS:CORR:LOSS:OUTP%s %s'
                       %(self.get_func_grp_addr(),con_num, value_dB))
        else:
            err_msg=('conn : %s is not in the valid range %s' %(conn, valid_list))
            raise ExCmu200(err_msg)

    def set_output_conn(self, conn="RF2"):
        if conn in ["RF1", "RF2", "RF3"]:
            self.write('%s;OUTP:STAT %s' %(self.get_func_grp_addr(),conn))
        else:
            err_msg = ('RF connector : %s not supported' %conn)
            raise ExCmu200(err_msg)

    def set_secondary_addresses(self):

        func_grp = 'WCDMA19UEFDD_Sig'
        self.write('SYST:REM:ADDR:SEC %s,\"%s\"'
                   %(self.func_grp_mapping[func_grp],
                    func_grp))
        func_grp = 'WCDMA19UEFDD_NSig'
        self.write('SYST:REM:ADDR:SEC %s,\"%s\"'
           %(self.func_grp_mapping[func_grp],
            func_grp))

        self.read('*STB?')
        return


    def set_input_atten(self, value_dB = 0.5, conn="RF2"):
        valid_list = ["RF1", "RF2", "RF3", "RF4"]
        if conn in valid_list:
            con_num = extract_digit_from_rf_conn(conn)
            self.write('%s;SENS:CORR:LOSS:INP%s %s'
                        %(self.get_func_grp_addr(),con_num, value_dB))
        else:
            err_msg=('conn : %s is not in the valid range %s' %(conn, valid_list))
            raise ExCmu200(err_msg)


    def set_analyser_unit(self, unit="MHz"):
        unit = unit.upper()
        unit_list = ['HZ', 'KHZ', 'MHZ', 'GHZ', 'CH']
        if unit in unit_list:
            self.write('%s;UNIT:RFANalyzer:FREQuency %s'
                        %(self.get_func_grp_addr(), unit))
        else:
            err_msg=('Error: unit %s is not in the valid range %s'
                     %(unit,unit_list))
            raise ExCmu200(err_msg)

    def set_analyser_freq_chan(self, value):
        self.write ('%s;SENSe:RFANalyzer:FREQuency %s'
                     %(self.get_func_grp_addr(), value))
        time.sleep(2)


    def setup_modulation_overview_ctrl():
        pass

    def switch_on_display(self):
        self.write('TRAC:REM:MODE:DISP ON')
        time.sleep(5)

    def waitForCompletion(self, timeout=30):
        num_iter      = 0
        NUM_ITER_MAX  = timeout
        POLL_INTERVAL = 1
        while (num_iter < NUM_ITER_MAX):
            completed=(self.read("*OPC?") == "1")
            if completed: break
            num_iter += 1
            time.sleep(POLL_INTERVAL)
        if num_iter == NUM_ITER_MAX:
            err_msg = "Error: waitForCompletion timeout"
            raise ExCmu200(err_msg)

    def waitForRDY(self, cmd_query, timeout=30):
        # wait for RDY indicating that single shot measurements have terminated
        num_iter      = 0
        NUM_ITER_MAX  = timeout
        POLL_INTERVAL = 1
        while (num_iter < NUM_ITER_MAX):
            resp = self.read(cmd_query)
            meas_state = resp.split(',')[0]
            completed=(meas_state == "RDY")
            if completed: break
            num_iter += 1
            time.sleep(POLL_INTERVAL)
        if num_iter == NUM_ITER_MAX:
            err_msg = "Error: waitForRDY timeout"
            raise ExCmu200(err_msg)

    def write(self, command):
        loggerInstr=logging.getLogger(__name__ + 'cmu.write')
        loggerInstr.debug ("   %s write command \"%s\"" % (self.name, command))
        self.dev.write(command)

    def __str__(self):
        print "CMU name   : %s" % self.name
        print "Gateway IP : %s" % self.gwip
        print "GPIB Addr  : %s" % self.gpib_addr
        return ""

    def get_sw_version(self):

        instrswinfo=self.read("0;SYSTEM:OPTIONS:INFO?")

        sw_info_list = instrswinfo.split(',')
        sw_info_str = ' '.join(sw_info_list)

        return sw_info_str

    def setup_3g_tx_test(self, freq=1950, cable_loss_dB=0):

        func_name = sys._getframe(0).f_code.co_name
        loggerInstr = logging.getLogger(__name__ + func_name)
        self.get_id()
        self.set_secondary_addresses()
        self.switch_on_display()
        self.waitForCompletion()
        self.func_grp_reset()
        self.waitForCompletion()

        self.set_func_grp_addr(func_grp='WCDMA19UEFDD_NSig')
        rf_conn = "RF2"
        freqMHz = freq
        self.set_default_levels()
        self.set_input_conn(conn=rf_conn)
        self.set_output_conn(conn=rf_conn)
        self.set_input_atten(value_dB=cable_loss_dB,conn=rf_conn)
        self.set_output_atten(value_dB=0.5,conn=rf_conn)
        self.set_analyser_unit(unit="MHz")
        self.waitForCompletion()
        self.set_analyser_freq_chan(value=freqMHz)
        self.waitForCompletion()
        self.set_wcdma_evm_ctrl(num_slots_per_stats_cycle=5)
        self.waitForCompletion()



#######################################################################################################################

if __name__ == '__main__':

    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

    from common.enableLogging import enable_logging
    logfilename=os.sep.join(cmdpath.split(os.sep)[:]+['cmu200_jr.LOG'])

    enable_logging(loglevel='DEBUG', log_file=logfilename)

    logger_00 = logging.getLogger('')
    logger_00.debug('START')

    cmu_name='CMU200'
    psugwip='10.21.140.230'
    psugpib="20,1"

    freqMHz = 1950

    try:

        cmu = None

        cmu=CmuControl(cmu_name=cmu_name, cmu_gwip=psugwip, cmu_gpib=psugpib)

        cmu.setup_3g_tx_test(freq=freqMHz)

        cmu.get_evm_meas()

        cmu.get_perr_meas()

        cmu.get_wcdma_mod_overview_results()

        cmu.close()

    except ExCmu200 as X:
        print X.message
        if cmu:
            cmu.close()


    logger_00.debug('END')


