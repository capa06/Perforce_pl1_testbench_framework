#-------------------------------------------------------------------------------

# Name:        cmw_gen_rf.py

# Purpose:

#

# Author:      joashr

#

# Created:     20/06/2014

# Copyright:   (c) joashr 2014


#-------------------------------------------------------------------------------



import os, sys, logging, time


try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-1])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env


import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *

import pl1_rf_system.common.rf_common_globals as rf_global

import pl1_rf_system.common.rf_common_functions as rf_cf


class gprf_gen():

    """"

    GPRF Generator control class for CMW500

    """

    def __init__(self, instrObj=None):

        self.instrObj = instrObj


    def _read_scenario(self):

        instr_scenario = self.instrObj.read('ROUTe:GPRF:GEN:SCENario?')

        return instr_scenario


    def set_scenario(self):

        maxRetry = 3

        retryNum = 0

        while retryNum < maxRetry:

            self.instrObj.write('ROUTe:GPRF:GEN:SCENario:SALone RF1C, RX1')

            instr_scen = self._read_scenario()

            if instr_scen == 'SAL':

                break

            elif retryNum == maxRetry - 1:

                func_name = sys._getframe(0).f_code.co_name

                loggerInstr = logging.getLogger(__name__ + "::" + func_name)

                errMsg=("CMW500 Failed to set scenario: %s" %__name__ + "::" + func_name)

                raise ExGeneral(errMsg)

            retryNum += 1


    def set_default_general_settings(self):

        self.set_rf_freqkHz(freqkHz=2140200)

        self.set_rf_ext_att_in(atten_dB=0)

        self.set_rf_level(power_dBm = -80)


    def set_rf_freqkHz(self, freqkHz):

        freqHz = int(freqkHz * 1e3)

        self.instrObj.write('SOURce:GPRF:GEN:RFSettings:FREQuency %s' %freqHz)

        self.instrObj.waitForCompletion()

    def set_rf_freqMHz(self, freqMHz):

        freqHz = int(freqMHz * 1e6)

        self.instrObj.write('SOURce:GPRF:GEN:RFSettings:FREQuency %s' %freqHz)

        self.instrObj.waitForCompletion()

    def set_rf_level (self, power_dBm):

        self.instrObj.write('SOURce:GPRF:GEN:RFSettings:LEVel %s' %power_dBm)

        self.instrObj.waitForCompletion()


    def set_rf_ext_att_in(self, atten_dB):

        self.instrObj.write('SOURce:GPRF:GEN:RFSettings:EATTenuation %s' % atten_dB)

        self.instrObj.waitForCompletion()


    def set_rf_generator_state (self, state='ON'):

        self.instrObj.write('SOURce:GPRF:GEN:STATe %s' %state)

        self.instrObj.waitForCompletion()


class gprf_meas():
    """"

    GPRF Measure control class for CMW500

    """

    def __init__(self, instrObj=None):

        self.instrObj = instrObj


    def _read_scenario(self):

        instr_scenario = self.instrObj.read('ROUTe:GPRF:MEAS:SCENario?')

        return instr_scenario


    def set_scenario(self):

        maxRetry = 3

        retryNum = 0

        while retryNum < maxRetry:

            self.instrObj.write('ROUTe:GPRF:MEAS:SCENario:SALone RF1C, RX1')

            instr_scen = self._read_scenario()

            if instr_scen == 'SAL':

                break

            elif retryNum == maxRetry - 1:

                func_name = sys._getframe(0).f_code.co_name

                loggerInstr = logging.getLogger(__name__ + "::" + func_name)

                errMsg=("CMW500 Failed to set scenario: %s" %__name__ + "::" + func_name)

                raise ExGeneral(errMsg)

            retryNum += 1

    def waitForRDY(self, timeout=30):

        num_iter      = 0

        NUM_ITER_MAX  = timeout

        POLL_INTERVAL = 1

        queryState='FETCh:GPRF:MEAS:POWer:STATe?' %self.rat

        while (num_iter < NUM_ITER_MAX):

            required_response=(self.instrObj.read(queryState) == 'RDY')

            if required_response: break

            num_iter += 1

            time.sleep(POLL_INTERVAL)

        if num_iter == NUM_ITER_MAX:

            errMsg = ('Timeout error waiting for %s' %response)

            raise ExGeneral(errMsg)


    def set_default_general_settings(self):

        self.set_rf_freqkHz(freqkHz=1950000)

        self.set_rf_ext_att_in(atten_dB=0)


    def set_rf_freqkHz(self, freqkHz):

        freqHz = int(freqkHz * 1e3)

        self.instrObj.write('CONFigure:GPRF:MEAS:RFSettings:FREQuency %s' %freqHz)

    def set_rf_freqMHz(self, freqMHz):

        freqHz = int(freqMHz * 1e6)

        self.instrObj.write('CONFigure:GPRF:MEAS:RFSettings:FREQuency %s' %freqHz)

    def set_rf_ext_att_in(self, atten_dB):

        self.instrObj.write('CONFigure:GPRF:MEAS:RFSettings:EATTenuation %s' % atten_dB)

    def set_rf_exp_power(self, power_dBm):

        self.instrObj.write('CONFigure:GPRF:MEAS:RFSettings:ENPower %s' % power_dBm)

    def set_up_meas_power(self):

        #<Repetition> SINGleshot | CONTinuous

        self.instrObj.write('CONFigure:GPRF:MEAS:POWer:REPetition SINGleshot')
        self.instrObj.write('CONFigure:GPRF:MEAS:POWer:TOUT 1')
        #self.instrObj.write('CONFigure:GPRF:MEAS:POWer:SLENgth 577.9230769E-6')
        #self.instrObj.write('CONFigure:GPRF:MEAS:POWer:MLENgth 400E-6')
        #self.instrObj.write('CONFigure:GPRF:MEAS:POWer:FILTer:TYPE GAUSs')
        #self.instrObj.write('CONFigure:GPRF:MEAS:POWer:FILTer:GAUSs:BWIDth 30E+3')
        self.instrObj.write("TRIGger:GPRF:MEAS:POWer:SOURce 'IF Power'")
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:SLOPe REDGe')
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:THReshold -25')
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:OFFSet 50E-6')
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:TOUT 2')
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:MGAP 0.0001')
        self.instrObj.write('TRIGger:GPRF:MEAS:POWer:MODE ONCE')

    def set_up_meas_power_cont(self):

        self.instrObj.write('CONFigure:GPRF:MEAS:POWer:REPetition CONTinuous')
        self.instrObj.write('INITiate:GPRF:MEAS:POWer')


    def set_meas_state (self,state='ON'):

        self.instrObj.write('INITiate:GPRF:MEAS:POWer %s' %state)

    def get_meas_curr_power_cont (self):
        #for REPetition CONTinuous
        meas_power = self.instrObj.read('FETCh:GPRF:MEAS:POWer:CURRent?')

        return meas_power

    def get_meas_curr_min_power_cont (self):
        #for REPetition CONTinuous
        meas_power = self.instrObj.read('FETCh:GPRF:MEAS:POWer:MINimum:CURRent?')

        return meas_power

    def get_meas_curr_min_power_cont (self):
        #for REPetition CONTinuous
        meas_power = self.instrObj.read('FETCh:GPRF:MEAS:POWer:MAXimum:CURRent?')

        return meas_power

    def get_meas_curr_power_single (self):
        #for REPetition SINGleshot
        meas_power = self.instrObj.read('READ:GPRF:MEAS:POWer:CURRent?')
        return float(meas_power.split(',')[1])

    def get_meas_curr_min_power_single (self):
        #for REPetition SINGleshot
        meas_power = self.instrObj.read('READ:GPRF:MEAS:POWer:MINimum:CURRent?')

        return meas_power

    def get_meas_curr_min_power_single (self):
        #for REPetition SINGleshot
        meas_power = self.instrObj.read('READ:GPRF:MEAS:POWer:MAXimum:CURRent?')

        return meas_power

    def setup_meas_fft(self):
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:REPetition SINGleshot')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:TOUT 1')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:FSPan 2e+07')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:FFTLength MAX')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:DETector RMS')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:AMODe LOG')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:MOEXception ON')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:IQRMode AWINdow')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:PSEarch:NOAMarkers 5')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:PSEarch OFF, -10e+06, -6e-06, OFF, -6e-06,-2E-06, OFF, -2E-06, +2E-06, OFF, +2E-06, +6E-06, OFF, +6E-06, +10E-06')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:CATalog:SOURce?')
        self.instrObj.write("TRIGger:GPRF:MEAS:FFTSanalyzer:SOURce 'IF Power'")
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:SLOPe REDGe')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:THReshold -25')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:TOUT 2')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:MGAP 550E-6')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:OMODe FIXed')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:OFFSet 1E-3')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:OMODe VARiable')
        self.instrObj.write('TRIGger:GPRF:MEAS:FFTSanalyzer:OSStop -1E-3, 1E-3')

    def get_fft_average_power_single (self):
        meas_power = self.instrObj.read('READ:GPRF:MEAS:FFTSanalyzer:POWer:AVERage?')
        return meas_power

    def setup_meas_fft_cont (self):
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:REPetition CONTinuous')
        self.instrObj.write('CONFigure:GPRF:MEAS:FFTSanalyzer:SCOunt 10')
        self.instrObj.write('INITiate:GPRF:MEAS:FFTSanalyzer')

    def get_meas_fft_peak_cont (self):
        meas = self.instrObj.read('FETCh:GPRF:MEAS:FFTSanalyzer:PEAKs:AVERage?')
        return meas

    def get_meas_fft_peak_single (self):
        meas = self.instrObj.read('READ:GPRF:MEAS:FFTSanalyzer:PEAKs:AVERage?')
        return float(meas.split(',')[1])

    def get_meas_fft_peak_power_single (self):
        meas = self.instrObj.read('READ:GPRF:MEAS:FFTSanalyzer:PEAKs:AVERage?')
        return float(meas.split(',')[2])

    def get_meas_fft_i_cont (self):
        meas = self.instrObj.read('FETCh:GPRF:MEAS:FFTSanalyzer:I?')
        return meas

    def get_meas_fft_q_cont (self):
        meas = self.instrObj.read('FETCh:GPRF:MEAS:FFTSanalyzer:Q?')
        return meas

if __name__ == '__main__':

    pass

