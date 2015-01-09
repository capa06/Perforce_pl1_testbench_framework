#-------------------------------------------------------------------------------
# Name:        wcdma_rx
# Purpose:      execute the WCDMA Rx tests
#
# Author:      joashr
#
# Created:     11/06/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, traceback, logging, math, time, platform, csv
from collections import OrderedDict
#curr_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'current'])


try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.config.umts_utilities import *
from pl1_rf_system.common.config.lte_utilities import *
from pl1_rf_system.common.rf_modem import *
import pl1_rf_system.instr.cmu200 as cmu
import pl1_rf_system.instr.cmw500 as cmw500
from pl1_rf_system.common.user_exceptions import *
from pl1_rf_system.instr.measurementClass import MeasurementClass
from pl1_rf_system.common.verdict import Verdict
import pl1_rf_system.common.rf_common_globals as rf_global
import pl1_rf_system.common.rf_common_functions as rf_cf
from pl1_rf_system.common.report.csv.CsvReport import CsvReport
from serial import SerialException
#from pl1_jenkins.instr.psu_control import check_output_state_on, switch_on_psu, switch_off_psu
from pl1_testbench_framework.common.instr.PsuBench import PsuBenchOn, PsuBenchOff

#from pl1_rf_system.common.comPortDet import auto_detect_port, poll_for_port
from pl1_testbench_framework.common.com.Serial_ComPortDet import poll_for_port

import pl1_rf_system.rfic.regread as rficregread
import pl1_rf_system.common.testtype.tables as tables

from pl1_rf_system.common.testtype.lte_tx import LTE_rf_config

# inherit functions and methods from Wcdma_tx
from wcdma_tx import Wcdma_tx

class General_Purpose(Wcdma_tx):

    curr_f=os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['results', 'current'])

    def __init__ (self, testID, testConfig_s, results_f, test_func, test_params, test_rat, final_test, unittest_enabled):

        func_name = sys._getframe(0).f_code.co_name
        loggerTest = logging.getLogger(__name__ + func_name)

        self.testConfig = testConfig_s

        self.test_func = test_func

        self.test_params = test_params

        self.testID = testID

        self.modemObj = None

        self.instr = None

        self.results_f = results_f

        self.FinalTest = final_test

        self.verdictObj = Verdict()

        self.instr_sw_version = ""

        self.test_rat = test_rat

        self.unittest_enabled = unittest_enabled

        self.start_time=time.localtime()

        self.set_meas("Init - no measurment set")

    def set_curr_power(self, power_dBm):
        self.curr_power = power_dBm

    def get_curr_power(self):
        return self.curr_power

    def set_freq(self, freqMHz):
        self.freqMHz = freqMHz

    def get_freq(self):
        return self.freqMHz

    def get_dl_frequency (self, rat='3G',arfcn=0):

        freqMhz = 0
        if rat == '3G':
            (band,freq_ul,freqMhz) = get_umts_ul_dl_freq_band(uarfcn=arfcn)
        elif rat == 'LTE':
            (band,freq_ul,freqMhz) = get_lte_ul_dl_freq_band(earfcn=arfcn)
        else:
            raise ValueError('Incorrect RAT')

        return freqMhz


    def check_for_iq_data_clipping (self, ant='m', n_samples = 20):
        self.set_meas("IQ Data Clipping Test - Auto AGC, Power=%ddBm" % self.get_curr_power())
        testverdict = "PASS"
        idata,qdata=self.modemObj.query_rxdata_raw(ant=ant,n_samples=n_samples)
        iqdata = idata
        iqdata.extend(qdata) #append lists
        iqdata = [math.fabs(x) for x in iqdata] #change list to absolute values
        if 127 in iqdata:
            testverdict = "FAIL"
        self.recordVerdict(testverdict)
        return testverdict

    def check_rx_antpower (self, ant='m', n_samples=2000, tol_dB = 4):
        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        loggerDisplay.debug("Performing modem Rx power measurement...\n")
        meas_desc = "UE Rx Power (dBm)"
        exp_power_dBm = self.get_curr_power()
        ue_rx_power_dBm = self.modemObj.query_rxdata_antpower(ant=ant,n_samples=n_samples)
        loggerDisplay.debug('antenna power %s dBm' %ue_rx_power_dBm)

        self.set_meas("UE Rx Power Check Auto AGC, Tester Power=%ddBm, Received Power=%ddBm, freq=%dMHz" % (self.get_curr_power(),ue_rx_power_dBm,self.get_freq()))

        verdictStr = self.get_ue_rx_pwr_verdict(exp_power_dBm=exp_power_dBm,
                                               received_power_dBm=ue_rx_power_dBm,
                                               tol_dB=tol_dB)

        loggerDisplay.debug("%s: %s" %(meas_desc, verdictStr))

        if verdictStr != "PASS":
        	rxagc = self.modemObj.query_rxagc(ant=ant)
        	pwr_per_lsb = self.modemObj.query_rxdata_pwr_per_lsb(ant=ant)
        	iq_pow_from_ssi_ssq = self.modemObj.query_rxdata_iq_pow_from_ssi_ssq(ant=ant)
        	antpower = self.modemObj.query_rxdata_antpower(ant=ant,n_samples=n_samples)
        	loggerDisplay.info("rxagc=%s, pwr_per_lsb=%s, iq_pow_from_ssi_ssq=%s, antpower=%s" %(rxagc, pwr_per_lsb, iq_pow_from_ssi_ssq, antpower))

        self.recordVerdict(verdictStr)

    def check_rx_fine_gain_steps (self, ant='m', n_samples=2000, full_range = False, tol_dB = 0.1):
        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        meas_desc = "Fine RX Gain step check"
        self.set_meas(meas_desc)
        exp_power_dBm = self.get_curr_power()
        meas_list = []
        res_list = []

        verdictStr = 'PASS'

        #current AGC backend gain
        curr_agc_be = self.modemObj.query_rxagc(ant='m',agc_val='backend')

        if full_range:
            for elem in range(-30,10):
                meas_list.append((elem,elem))
        else:
            meas_list = [(-25,-25),(-9,-9),(7,7)]

        for val in meas_list:
            self.modemObj.set_rxagc_manual(ant='m',be_val=curr_agc_be,fine_i=val[0],fine_q=val[1])
            iq_pwr = self.modemObj.query_rxdata_iq_pow_from_ssi_ssq()
            res_list.append(iq_pwr)

        if full_range:
            print "Fine Gain Step Measurements - 1/16dB Steps, Should increase by 1dB every 16\n"
            idx = 0
            for elem in res_list:
                print "%d: Fine Gain: %d,%d   IQ Power: %f" % (idx+1,meas_list[idx][0],meas_list[idx][1],elem)
                idx += 1
        else:
            #These element separations should result in 1dB steps from fine gain changes only
            elem_idx = range(0,len(meas_list))
            for elem in elem_idx:
                try:
                    verdictStr = self.get_ue_rx_pwr_verdict(1,abs(res_list[elem]-res_list[elem+1]),tol_dB)
                    print res_list[elem],res_list[elem+1],verdictStr, abs(res_list[elem]-res_list[elem+1])
                except IndexError:
                    pass

        loggerDisplay.debug("%s: %s" %(meas_desc, verdictStr))

        self.recordVerdict(verdictStr)


    def get_ue_rx_pwr_verdict(self, exp_power_dBm, received_power_dBm, tol_dB):
        # see if exepceted power is within the +/- tol_dB of expected power
        # and set the verdict accordingly
        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        verdict = "FAIL"
        loggerDisplay.debug("expected power : %s" %exp_power_dBm)

        upper_limit = 1.0 * float(exp_power_dBm) + tol_dB
        lower_limit = 1.0 * float(exp_power_dBm) - tol_dB

        if float(received_power_dBm) <= upper_limit and float(received_power_dBm) >= lower_limit:
            loggerDisplay.debug("Ue Rx power is within the expected range %s : %s" %(lower_limit, upper_limit))
            verdict = "PASS"
        else:
            loggerDisplay.debug("Ue Rx power is outside the expected range %s : %s" %(lower_limit, upper_limit))
            verdict = "FAIL"

        return verdict


    def executeTest(self,instr_control):

        modeminfo = ""

        modeminfo = query_build_info_from_modem()

        self.instr= instr_control

        self.set_instr_sw_version(version=self.instr.get_sw_version())

        self.instr.set_verdictObj(self.verdictObj)

        self.set_csvSummaryReport(results_f=self.results_f, modeminfo=modeminfo,
                                  instrswinfo=self.get_instr_sw_version())

        try:

            test_function = getattr(self,self.test_func)
            test_function(**self.test_params)

            if self.instr:
                self.instr.close()
                self.instr = None

            self.shut_down_modem()
            verdictStr = self.verdictObj.GetSummaryVerdict(col_len=80)
            self.update_csvSummaryReport(verdictStr=verdictStr)
            return verdictStr,self.verdictObj

        except (IOError,SerialException) as err:
            # communication error with modem, likely assert
            print traceback.format_exc()
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None

            # capture core dump and close modem connection
            if self.modemObj:
                rf_cf.pause(duration_s=20, poll_time_sec=2, desc="short pause prior to modem crash detection!!")
                if self.modemObj.check_for_crash():
                    self.capture_core_dump()
                else:
                    # no point in shutting down as there is likely
                    # communication issue with modem
                    self.modemObj.close()
                    self.modemObj=None

            verdictStr = rf_global.verdict_dict[rf_global.FAIL]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            return verdictStr,self.verdictObj

        except ExFail:
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            verdictStr = rf_global.verdict_dict[rf_global.FAIL]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except ExUserBreakPoint, e:
            print '%s' %e.message
            verdictStr = rf_global.verdict_dict[rf_global.INCONC]
            return verdictStr,self.verdictObj

        except ExGeneral:
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            verdictStr = rf_global.verdict_dict[rf_global.INCONC]
            self.update_csvSummaryReport(verdictStr=verdictStr)
            self.shut_down_modem()
            return verdictStr,self.verdictObj

        except Exception:
            print traceback.format_exc()
            if self.instr and self.FinalTest:
                self.instr.close()
                self.instr=None
            self.shut_down_modem()
            self.recordVerdict(verdictStr='Inconclusive')
            verdictStr=self.verdictObj.GetSummaryVerdict(col_len=80)
            self.update_csvSummaryReport(verdictStr=verdictStr)
            return verdictStr,self.verdictObj

    def start_tx(self,freqMHz):
        """Starts TX to run together with RX. Used by TDD tests."""
        self.modemObj.set_freqMHz(direction='tx',freqMHz=freqMHz)
        self.modemObj.send_ul_pattern()
        self.modemObj.set_txagc_dbm(value=-10)
        self.modemObj.enable_tx()

    def auto_agc_verification(self,rat,arfcn,powerdBm,ud_config=None,special_sf_config=0,with_tx=False):

        tone_offset_khz = 200

        if rat.upper() == "3G":
            band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(arfcn)
            toldB = 4
        else:
            band,freq_ul,freq_dl = get_lte_ul_dl_freq_band(arfcn)
            toldB = 5

        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_tone(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0

        self.modemObj.set_rat_band(rat=self.test_rat, band=band)
        self.modemObj.set_rxagc_auto(ant='m')

        if ud_config is not None:
            self.modemObj.set_ud_config(ud_config)
            self.modemObj.set_special_sf_config(special_sf_config)

        self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
        self.set_freq(freq_dl)
        self.instr.gprf_gen.set_rf_freqkHz(freqkHz=(freq_dl*1e3) + tone_offset_khz)
        rf_cf.pause(duration_s=2, poll_time_sec=1, desc="short pause")

        self.set_curr_power(power_dBm=powerdBm)
        self.instr.gprf_gen.set_rf_level(power_dBm=powerdBm)

        self.modemObj.enable_rx(ant='m')

        if with_tx:
            assert(int(ud_config) >=0)
            self.start_tx(freq_ul)

        rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")

        if ud_config is None:
            self.check_for_iq_data_clipping(ant='m',n_samples=20)

        self.check_rx_antpower(ant='m',tol_dB=toldB)

        if ud_config is not None:
            fine_gain_tol_dB = 0.4 # Higher tolerance for TDD
        else:
            fine_gain_tol_dB = 0.15
        self.check_rx_fine_gain_steps (ant='m', full_range = False, tol_dB=fine_gain_tol_dB)

        self.instr.gprf_gen.set_rf_generator_state(state='OFF')

    def auto_agc_and_manual(self,rat,arfcn,powerdBm,ud_config=None,iterations=4,with_tx=False):
        tone_offset_khz = 200

        if rat.upper() == "3G":
            band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(arfcn)
            toldB = 4
        else:
            band,freq_ul,freq_dl = get_lte_ul_dl_freq_band(arfcn)
            toldB = 5

        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_tone(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0

        self.modemObj.set_rat_band(rat=self.test_rat, band=band)

        if ud_config is not None:
            self.modemObj.set_ud_config(ud_config)

        self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
        self.set_freq(freq_dl)
        self.instr.gprf_gen.set_rf_freqkHz(freqkHz=(freq_dl*1e3) + tone_offset_khz)
        rf_cf.pause(duration_s=2, poll_time_sec=1, desc="short pause")

        self.set_curr_power(power_dBm=powerdBm)
        self.instr.gprf_gen.set_rf_level(power_dBm=powerdBm)

        self.modemObj.enable_rx(ant='m')

        if with_tx:
            assert(int(ud_config) >=0)
            self.start_tx(freq_ul)

        rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")

        self.modemObj.set_rxagc_auto(ant='m')
        manual_atten = self.modemObj.query_rxagc(ant='m')

        for i in range(iterations):
            # Set manual rx gain
            logging.info("Iteration %d, set manual RX gain." % (i))
            self.modemObj.set_rxagc_manual(ant='m',be_val=manual_atten)
            rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")
            # self.check_for_iq_data_clipping(ant='m',n_samples=20)
            self.check_rx_antpower(ant='m',tol_dB=toldB)

            # Back to auto
            logging.info("Iteration %d, set auto RX gain." % (i))
            self.modemObj.set_rxagc_auto(ant='m')
            rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")
            # self.check_for_iq_data_clipping(ant='m',n_samples=20)
            self.check_rx_antpower(ant='m',tol_dB=toldB)

        self.instr.gprf_gen.set_rf_generator_state(state='OFF')

    def power_cycle_modem(self):

        if self.testConfig.psugwip != 'ww.xx.yy.zz':

            #switch_off_psu(psu_gwip=self.testConfig.psugwip, psu_gpib=self.testConfig.psugpib, psu_name='E3631A_0')
            PsuBenchOff(psu_gwip=self.testConfig.psugwip,
                        psu_gpib=self.testConfig.psugpib)
            time.sleep(3)
            #switch_on_psu(psu_gwip=self.testConfig.psugwip, psu_gpib=self.testConfig.psugpib, psu_name='E3631A_0', Vmax_V=self.testConfig.psuvolt, Imax_A=2)
            PsuBenchOn(psu_gwip=self.testConfig.psugwip,
                       psu_gpib=self.testConfig.psugpib,
                       setVolts=self.testConfig.psuvolt,
                       Imax_A=2)

            if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

                print "modem com port successfully found"

                time_secs = 10

                print "pausing for %s secs ..." %time_secs

                time.sleep(time_secs)

            else:

                errMsg = "modem com port not found after PSU switch on"
                raise ExFail(errMsg)

        else:
            print "\n\n\n\********************* Note ****************************************"
            print "A power cycle is needed after this test to ensure a known RFIC state\n\n\n\n"

    def rfic_test_mode_basic_check (self):

        #setup modem - serial comms
        self.setup_modem()

        self.set_meas("Basic RFIC Test Mode Check - Pass if no Crash")
        verdictStr = "PASS"

        cmd_l = ['at+gmr','AT%IPRPR=SPI_RADIO,,0,0x3FF','AT%IPRPR=SPI_RADIO,,0,0x3FE','AT%SCRSTOP=CLEAR,ON',
                 'AT%RFMODE=RESET','AT%IPRPW=SPI_RADIO,,0,0x30F,0x00005','AT%IPRPW=SPI_RADIO,,0,0x3D1,0x00041',
                 'AT%IPRPW=SPI_RADIO,,0,0x317,0x00200','AT%RFMODE=BASIC','AT%SCRIQ=0,WCDMA,RX','AT%SCRBEGIN=2,100,DIRECT',
                 'AT%SCRREG=0xc3d00005','AT%SCRREG=0xc4100106','AT%SCRREG=0xf4d00907','AT%SCRREG=0xf510068b',
                 'AT%SCRREG=0xbe904584','AT%SCRREG=0xbe500000','AT%SCRREG=0xbe906584','AT%SCRREG=0xf4104e1c',
                 'AT%SCRREG=0x6500003','AT%SCRREG=0x51500003','AT%SCRREG=0x65500003','AT%SCRREG=0xf4500041',
                 'AT%SCRREG=0xc5d00200','AT%SCRREG=0xc6d00000','AT%SCRREG=0x6900001','AT%SCRREG=0x6d00001',
                 'AT%SCRREG=0xc1500447','AT%SCRREG=0xb15006e0','AT%SCRREG=0xa81054e3','AT%SCRREG=0xa851825c',
                 'AT%SCRREG=0xa8917710','AT%SCREND','AT%SCRSTART','AT%SCRSTOP', 'AT%RFMODE=RESET','AT%RFMODE=RF']

        self.modemObj.sendCmdList(cmd_l)

        self.power_cycle_modem()

        self.recordVerdict(verdictStr)

    def basic_iprpr (self):

        self.setup_modem()

        self.set_meas("IPRPR test, read back chip revision, super-basic test")

        # initialise verdict
        verdictStr = "FAIL"

        # perform test
        msg = self.modemObj.sendCmdList(['AT%IPRPR=SPI_RADIO,,0,0x3FF'], ret_msg_only=True)
        rficchiprevision = 0
        for line in msg.splitlines():
            if '3FF = ' in line:
                rficchiprevision = int(line.split(' = ')[-1], 0)
        if rficchiprevision != 0:
            verdictStr = "PASS"

        # record chip revision (as reported) into log (debug only)
        func_name = sys._getframe(0).f_code.co_name
        loggerDisplay = logging.getLogger(__name__ + func_name)
        loggerDisplay.debug("RFIC chip revision = %X" % rficchiprevision)

        self.recordVerdict(verdictStr)

    def frequency_change(self,rat,arfcn,powerdBm,ud_config=None,iterations=4,with_tx=False):
        """Verify that changing frequency while RX is running works.
        Turn on RX and switch between the given earfcn and 10 MHz higher 5 times."""
        tone_offset_khz = 200

        if rat.upper() == "3G":
            band,base_freq_ul,base_freq_dl = get_umts_ul_dl_freq_band(arfcn)
            assert(ud_config is None)
        else:
            band,base_freq_ul,base_freq_dl = get_lte_ul_dl_freq_band(arfcn)

        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_tone(cable_loss_dB=self.testConfig.cable_loss)
        self.teststep_idx = 0

        self.modemObj.set_rat_band(rat=self.test_rat, band=band)
        self.modemObj.enable_rx(ant='m')
        self.modemObj.set_rxagc_auto(ant='m')

        if ud_config is not None:
            self.modemObj.set_ud_config(ud_config)

        if with_tx:
            self.start_tx(base_freq_ul)

        self.set_curr_power(power_dBm=powerdBm)
        self.instr.gprf_gen.set_rf_level(power_dBm=powerdBm)
        rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")

        for freq_offset in [0, 10] * iterations:
            freq_dl = base_freq_dl + freq_offset
            freq_ul = base_freq_ul + freq_offset
            self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
            if with_tx:
                self.modemObj.set_freqMHz(direction='tx',freqMHz=freq_ul)
            self.set_freq(freq_dl)
            self.instr.gprf_gen.set_rf_freqkHz(freqkHz=(freq_dl*1e3) + tone_offset_khz)
            rf_cf.pause(duration_s=2, poll_time_sec=1, desc="short pause")

            #self.check_for_iq_data_clipping(ant='m',n_samples=20)
            self.check_rx_antpower(ant='m', tol_dB = 5)

        self.instr.gprf_gen.set_rf_generator_state(state='OFF')


    def envelope_tracking_at_cmds_only (self):

        #setup modem - serial comms
        self.setup_modem()

        self.set_meas("ET Direct Mode AT commands, pass if register writes read back as expected")

        # prepare modem into state for testing
        cmd_l = ['at+gmr','at%caltable=load','at%3gband=1','at%rftx=1950.000','at%rftxiqadjust=OFF','at%rftxagc=DIRECT,100,0']
        self.modemObj.sendCmdList(cmd_l)
        self.modemObj.enable_tx()

        et_at_test_result = True

        ## perform ET AT cmd tests

        # RFIC register writes
        for atcmd in tables.et_atcmd_table:
            if (len(tables.et_atcmd_table[atcmd]) != 0):
                self.modemObj.sendCmdList(['AT%' + atcmd + str(tables.et_atcmd_table[atcmd][0])])

                # iterate through table listing register fields that need to be read back and checked
                fieldindex = 1
                while fieldindex < len(tables.et_atcmd_table[atcmd]):
                    et_at_test_result = et_at_test_result and rficregread.verify_field_val (self.modemObj,tables.et_atcmd_table[atcmd][fieldindex], tables.et_atcmd_table[atcmd][fieldindex+1])
                    fieldindex += 2

        ## ETM register writes
        for atcmd in tables.et_atcmd_etm_table:
            line = tables.et_atcmd_etm_table[atcmd]
            if (len(line) != 0):
                self.modemObj.sendCmdList(['AT%' + atcmd + str(line[0])])
                et_at_test_result = et_at_test_result and rficregread.verify_etm_field_val (self.modemObj, line[1], line[2], line[3], line[4])

        self.modemObj.disable_tx()

        if (et_at_test_result):
            verdictStr = "PASS"
        else:
            verdictStr = "FAIL"

        self.power_cycle_modem()

        self.recordVerdict(verdictStr)


    def receiver_filter_characterization(self,rat,arfcn,offsetkhz,stepkHz,powerdBm,bwMhz):

        #This test is designed to set the modem to receive on a particular channel and sweep the cmw tone frequency across
        #-offset - arfcn_freq - +offset and record the IQ power. Fixed AGC is used.

        import matplotlib.pyplot as pyplot

        sweep_results = OrderedDict()


        modeminfo = query_build_info_from_modem()
        changelist = get_build_cl_from_modem(modeminfo)
        platform = get_platform_from_modem(modeminfo)

        if rat.upper() == "3G":
            band,freq_ul,freq_dl = get_umts_ul_dl_freq_band(arfcn)
        else:
            band,freq_ul,freq_dl = get_lte_ul_dl_freq_band(arfcn)

        sweep_low_kHz = int(1e3*freq_dl - offsetkhz)
        sweep_high_kHz = int(1e3*freq_dl + offsetkhz)
        init_tone_offset_kHz = 200000

        print "sweep low" , sweep_low_kHz
        print "sweep high", sweep_high_kHz

        #setup modem - serial comms
        self.setup_modem()

        #setup tester
        self.instr.setup_rf_tone(cable_loss_dB=self.testConfig.cable_loss)

        self.modemObj.set_rat_band(rat=self.test_rat, band=band)
        self.modemObj.set_rxagc_auto(ant='m')


        self.modemObj.set_freqMHz(direction='rx',freqMHz=freq_dl)
        self.set_freq(freq_dl)
        self.instr.gprf_gen.set_rf_freqkHz(freqkHz=(freq_dl*1e3) + init_tone_offset_kHz)
        rf_cf.pause(duration_s=2, poll_time_sec=1, desc="short pause")

        self.set_curr_power(power_dBm=powerdBm)
        self.instr.gprf_gen.set_rf_level(power_dBm=powerdBm)

        if rat == "LTE":
            rf_config = LTE_rf_config(bwMHz=bwMhz)
            self.modemObj.set_rb(direction='ul', num_rb=rf_config.num_rbs)
            self.modemObj.set_rb(direction='dl', num_rb=rf_config.num_rbs)
            self.modemObj.set_rb_len(rb_len=rf_config.rb_len)
            self.modemObj.set_rb_start(rb_offset=rf_config.rb_offset)
            self.modemObj.set_rx_bw(rx_bw=bwMhz)


        self.modemObj.enable_rx(ant='m')
        rf_cf.pause(duration_s=1, poll_time_sec=1, desc="short pause to allow rf level to settle")

        verdict = self.check_for_iq_data_clipping(ant='m',n_samples=20)

        if verdict == "PASS":
            #Change AGC to manual at current auto selected backend gain
            curr_agc_be = self.modemObj.query_rxagc(ant='m',agc_val='backend')
            if curr_agc_be == 86:
                curr_agc_be = 85
            #86 returns error

            self.modemObj.set_rxagc_manual(ant='m',be_val=curr_agc_be)

            sweep_range = range(sweep_low_kHz,sweep_high_kHz+1,stepkHz)

            for freq in sweep_range:
                self.instr.gprf_gen.set_rf_freqkHz(freqkHz=freq)
                #rf_cf.pause(duration_s=1, poll_time_sec=1, desc="rf pause")
                iq_pwr = self.modemObj.query_rxdata_iq_pow_from_ssi_ssq()
                sweep_results[freq]=iq_pwr

        else:
            raise ExGeneral('IQ Clipping')

        #print sweep_results

        self.instr.gprf_gen.set_rf_generator_state(state='OFF')

        pyplot.plot(sweep_results.keys(),sweep_results.values())
        pyplot.title('RX IQ Power vs Frequency - Fixed AGC %d - %dMhz Sweep' % (curr_agc_be,(offsetkhz*2)/1e3))
        pyplot.ylabel('IQ Power')
        pyplot.xlabel('Frequency')
        pyplot.grid(True)
        pyplot.axis([sweep_low_kHz-50,sweep_high_kHz+50,15,50])
        #pyplot.show()
        #savetitle = curr_f+'\%s_%s_%s-band%s_%dMHzBW_%dMHzSweep' % (platform,changelist,rat,str(band),bwMhz,(offsetkhz*2)/1e3)
        savetitle = self.curr_f+'\%s_%s_%s-band%s_%dMHzBW_%dMHzSweep' % (platform,changelist,rat,str(band),bwMhz,(offsetkhz*2)/1e3)
        pyplot.savefig(savetitle+'.svg')
        pyplot.clf()
        writer = csv.writer(open(savetitle+'.csv', 'w'))
        freq_list = sweep_results.keys()
        iq_list = sweep_results.values()
        rows = zip(freq_list,iq_list)

        for row in rows:
            writer.writerow(row)

if __name__ == '__main__':

    print "Hello"


