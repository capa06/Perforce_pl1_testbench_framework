#-------------------------------------------------------------------------------

# Name:        cmw_wcdma_meas.py

# Purpose:

#

# Author:      joashr

#

# Created:     20/06/2014

# Copyright:   (c) joashr 2014

# Licence:     <your licence>

#-------------------------------------------------------------------------------



import os, sys, logging, time



(abs_path, name)=os.path.split(os.path.abspath(__file__))



try:

    os.environ['PL1_RF_SYSTEM_ROOT']

except KeyError:

    os.environ['PL1_RF_SYSTEM_ROOT'] = os.sep.join(abs_path.split(os.sep)[:-1])

    print ">> os.environ['PL1_RF_SYSTEM_ROOT']=%s" % os.environ['PL1_RF_SYSTEM_ROOT']

    sys.path.append(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]))



from addSystemPath import AddSysPath

AddSysPath(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['common']))

from user_exceptions import *

import rf_common_globals as rf_global

import rf_common_functions as rf_cf





class Wcdma_meas():

    """"

    measurment class for WCDMA measurements from CMW500

    """

    MEAS_OK = "0"

    FULL_SLOT = 0

    HALF_SLOT = 1

    # below aligns to output of

    # FETCh:WCDMa:MEAS<i>:MEValuation:MODulation:CURRent?

    # integer number value corresponds to paramter position to

    # results array





    MEV_MOD_DICT={'EVMrms':0, 'EVMpeak':1, 'MagErrorRMS':2,

                  'MagErrorPeak':3, 'PhErrorRMS':4, 'PhErrorPeak':5, 'IQoffset':6,

                  'IQimbalance':7, 'CarrFreqErr':8, 'TransTimeErr':9, 'UEpower':10,

                  'PowerSteps':11, 'PhaseDisc':12}



    meas_period_dict={'FULLSLOT':FULL_SLOT, 'HALFSLOT':HALF_SLOT}



    def __init__(self, instrObj=None, verdictObj=None):


        self.rat = "WCDMa"


        self.instrObj = instrObj



        self.rely_ind = "-1"    # measurement relaibility indicato



        self.meas_valid = False



        self.slot_for_stats = 0      # this is the slot number for stats and analysis

                                     # maps to Slot Number (Table)

        self.init_meas_flag = True

        self.verdictObj = verdictObj


    def set_verdictObj (self,verdictObj):
        self.verdictObj = verdictObj

    def set_init_meas_flag (self,flag):
        self.init_meas_flag = flag

    def set_meas_period(self, meas_key_val):



        try:



            meas_period = self.meas_period_dict[meas_key_val.upper()]



            self.meas_period = meas_key_val



        except KeyError:



            errMsg = ("key value %s not supported. Valid values are %s"

                       %(meas_key_val, self.meas_period_dict.keys()))

            print self.meas_period_dict.keys()

            raise ExGeneral(errMsg)


    def RecordError (self, errmsg="",raise_except=True):

        self.verdictObj.RecordError(errmsg)

        if(raise_except):
            raise ExModem(errmsg)

    def get_meas_period(self):



        return self.meas_period





    def set_slot_num(self, slotNum):



        self.slot_for_stats = slotNum



    def get_slot_num(self):



        return self.slot_for_stats



    def set_rely_ind (self, relyStr):



        self.rely_ind = relyStr



        if relyStr == self.MEAS_OK:



            self.set_meas_valid(boolVal=True)



        else:



            self.set_meas_valid(boolVal=False)



    def get_rely_ind (self):



        return self.rely_ind



    def set_meas_valid(self, boolVal):



        self.meas_valid = boolVal



    def get_meas_valid(self):



        return self.meas_valid





    def set_mod_cur_meas(self, valStr):



        self.mod_cur_meas_list = valStr





    def set_mod_avg_meas(self, valStr):



        self.mod_avg_meas_list = valStr



    def set_mod_max_meas(self, valStr):



        self.mod_max_meas_list = valStr



    def get_mod_cur_meas(self):



        return self.mod_cur_meas_list



    def get_mod_avg_meas(self):



        return self.mod_avg_meas_list



    def get_mod_max_meas(self):



        return self.mod_max_meas_list



    #+++++++++++++++++++++++++++++++++++++++++++



    def set_mod_cur_lim_meas(self, valStr):



        self.mod_cur_meas_lim_list = valStr



    def set_mod_avg_lim_meas(self, valStr):



        self.mod_avg_meas_lim_list = valStr



    def set_mod_max_lim_meas(self, valStr):



        self.mod_max_meas_lim_list = valStr



    def get_mod_cur_lim_meas(self):



        return self.mod_cur_meas_lim_list



    def get_mod_avg_lim_meas(self):



        return self.mod_avg_meas_lim_list



    def get_mod_max_lim_meas(self):



        return self.mod_max_meas_lim_list





    def _read_scenario(self):

        instr_scenario = self.instrObj.read('ROUTe:%s:SIGN:SCENario?' %self.rat)

        return instr_scenario





    def set_scenario(self):

        maxRetry = 3

        retryNum = 0

        while retryNum < maxRetry:

            self.instrObj.write('ROUTe:%s:MEAS:SCENario:SALone RF1C, RX1' %self.rat)

            instr_scen = self._read_scenario()

            if instr_scen == 'SCEL':

                break


            elif retryNum == maxRetry - 1:

                func_name = sys._getframe(0).f_code.co_name

                loggerInstr = logging.getLogger(__name__ + "::" + func_name)

                errMsg=("CMW500 Failed to set scenario: %s" %__name__ + "::" + func_name)

                raise ExGeneral(errMsg)

            retryNum += 1



    def set_default_general_settings(self):



        self.set_rf_freqMHz(freqMHz=1950)



        # external attaenuation setting

        self.set_rf_ext_att_in(atten_dB=0)



        # set the expected nominal power

        self.set_rf_exp_power(power_dBm=0)



        self.set_rf_user_margin(value_dB=5)



    def set_rf_freqMHz(self, freqMHz):



        freqHz = int(freqMHz * 1e6)



        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:FREQuency %s' %(self.rat, freqHz))



    def set_band(self, band):

        band_str ="OB" + str(band)

        self.instrObj.write('CONFigure:%s:MEAS:BAND %s' %(self.rat, band_str))


    def set_rf_ext_att_in(self, atten_dB):



        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:EATTenuation %s' %(self.rat, atten_dB))



    def set_rf_exp_power(self, power_dBm):



        # expected nominal power



        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:ENPower %s' %(self.rat, power_dBm))



    def set_rf_user_margin(self, value_dB):



        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:UMARgin %s' %(self.rat, value_dB))





    # UE Signal Info

    def set_ue_signal_info(self):



        self.enable_dpdch(boolVal = True)



        self.set_ul_slot_format(slot_format=0)



        self.set_scramble_code(val=0)



        self.set_ul_config(configStr=self.rat)



        self.set_phy_chan_config(channelStr='DPCCh', beta=4, sf=256)



        self.set_phy_chan_config(channelStr='DPDCh', beta=15, sf=256)



    def set_ul_slot_format(self, slot_format):



        self.instrObj.write('CONFigure:%s:MEAS:UESignal:SFORmat %s' %(self.rat, slot_format))



    def enable_dpdch(self, boolVal):



        if boolVal == True:

            self.instrObj.write('CONFigure:%s:MEAS:UESignal:DPDCh ON' %self.rat)

        else:

            self.instrObj.write('CONFigure:%s:MEAS:UESignal:DPDCh OFF' %self.rat)



    def set_scramble_code(self, val):



        self.instrObj.write('CONFigure:%s:MEAS:UESignal:SCODe %s' %(self.rat, val))



    def set_ul_config(self, configStr):



        try:



            validConfigDic = {'QPSK': 1, 'WCDMA': 1, 'HSDPA': 1,

                              'HSUPA' : 1,  'HSPA': 1, 'HSPLUS' : 1,

                              'DCHS' : 1, 'HDUPLUS' : 1, 'DDUPLUS':1}[configStr.upper()]



            self.instrObj.write('CONFigure:%s:MEAS:UESignal:ULConfig %s'
                                %(self.rat, configStr))



        except KeyError:

            errMsg = ("UL configuration %s is not supported" %configStr)

            raise ExGeneral(errMsg)





    def set_phy_chan_config(self, channelStr, beta, sf):

        try:

            valid_chan_dict = {'DPCCH':1, 'DPDCH':2}[channelStr.upper()]

            self.instrObj.write('CONFigure:%s:MEAS:UECHannels:CARRIER:%s ON,%s,%s'

                                % (self.rat, channelStr, beta, sf))

        except KeyError:

            errMsg = ('Channel configuration %s is not supported' %channelStr)

            raise ExGeneral(errMsg)



    def set_up_meas_control(self):



        # slot number for displayed statistical measure

        self.set_slot_num(slotNum=0)



        #<Repetition> SINGleshot | CONTinuous

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:REPetition SINGleshot' %self.rat)

        # <StopCondition> NONE | SLFail

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCONdition None'%self.rat)

        # <MeasOnException> OFF | ON

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MOEXception OFF' %self.rat)

        # number of measured slots

        # <SlotCount> Range: 	1 slot  to  120 slots

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MSCount 15' %self.rat)

        # <SlotNumber> Range: 	0  to  119

        # must be smaller than the number of measured slots

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:PSLot 3' %self.rat)

        # <SlotNumber> ANY | SL1 | SL2 | SL3 | SL4 | SL5 | SL6 | SL7 | SL8 |

        #              SL9 | SL10 | SL11 | SL12 | SL13 | SL14 | SL0

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SYNCh ANY' %self.rat)



        # modulation / CDP paarmeters

        #<MeasPeriod> FULLslot | HALFslot

        self.set_meas_period(meas_key_val='FULLslot')

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MPERiod:MODulation %s'
                             %(self.rat,self.get_meas_period()))

        # statistics count, The statistic count is equal to the number of

        #  measurement intervals per single shot.

        self.set_meas_ctrl_stats(num_slots_per_stats_cycle=5)

        self.check_ul_detection_mode()

        # Defines whether a possible origin offset is included in the

        # measurement results (WOOFfset) or subtracted out (NOOFfset)

        # <AnalysisMode> WOOFfset | NOOFfset

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:AMODe:MODulation WOOFfset' %self.rat)

        #Selects a particular slot or half-slot within the "Measurement Length"

        # where the R&S CMW evaluates the statistical measurement results for

        # multislot measurements

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SSCalar:MODulation %s'
                            %(self.rat, self.get_slot_num()))

        #Selects the spreading factor for the displayed code domain monitor results

        # SF4 | SF8 | SF16 | SF32 | SF64 | SF128 | SF256

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:DSFactor:MODulation SF4'
                             %self.rat)

        # <Rotation> The entered value is rounded to 0 deg or 45 deg

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:ROTation:MODulation 0'
                             %self.rat)



        self.enable_all_meas()



    def waitForRDY(self, timeout=30):

        num_iter      = 0

        NUM_ITER_MAX  = timeout

        POLL_INTERVAL = 1

        queryState='FETCh:%s:MEAS:MEValuation:STATe?' %self.rat

        while (num_iter < NUM_ITER_MAX):

            required_response=(self.instrObj.read(queryState) == 'RDY')

            if required_response: break

            num_iter += 1

            time.sleep(POLL_INTERVAL)

        if num_iter == NUM_ITER_MAX:

            errMsg = ('Timeout error waiting for %s' %response)

            raise ExGeneral(errMsg)



    def get_mod_meas_from_instr(self):



        for modType in ['CURRENT', 'AVERAGE', 'MAXIMUM']:



            reading = self.instrObj.read('FETCh:%s:MEAS:MEValuation:MODulation:%s?' %(self.rat, modType))

            reading = reading.split(',')

            reliability_indicator = reading[0]

            self.set_rely_ind(relyStr=reliability_indicator)

            if self.get_meas_valid() != True:

                return



            reading_lim = self.instrObj.read('CALCulate:%s:MEAS:MEValuation:MODulation:%s?' %(self.rat, modType))

            reading_lim = reading_lim.split(',')

            reliability_indicator = reading_lim[0]

            self.set_rely_ind(relyStr=reliability_indicator)

            if self.get_meas_valid() != True:

                return



            if modType.upper() == 'CURRENT':

                self.set_mod_cur_meas(reading)

                self.set_mod_cur_lim_meas(reading_lim)

            elif modType.upper() == 'AVERAGE':

                self.set_mod_avg_meas(reading)

                self.set_mod_avg_lim_meas(reading_lim)

            else:

                self.set_mod_max_meas(reading)

                self.set_mod_max_lim_meas(reading_lim)



        return



    def get_row_index(self, keyValue):

        # first item in the measurement list is reliability which is not included

        # which is not included in self.MEV_MOD_DICT so required list is offset by

        # 1

        index = self.MEV_MOD_DICT[keyValue] +  1

        return index



    def get_results_array_from_modulation(self, resultsType):

        """

        extract measurements data from the modulation measurements performed

        by get_mod_meas_from_instr

        get measurement in the form

        Current    #Average    #Max

        for measX

        # where measX can be EVM(peak), EVM(RMS) etc,

        # e.g. current EVM(peak)    Average EVM(peak)   Max EVM(peak)

        # this is similar format to results row display of CMU200

        """



        #validTypeDict = {'EVMpeak':1, 'EVMrms':1, 'IQoffset':1, 'CarrFreqErr':1}

        validTypeDict = self.MEV_MOD_DICT

        try:

            check = validTypeDict[resultsType]

        except KeyError:

            errMsg = ('Results type %s is not supported' %resultsType)

            errMsg +=('List of supported types are %s' %validTypeDict.keys())

            raise ExGeneral(errMsg)



        func_name = sys._getframe(0).f_code.co_name



        loggerCmw = logging.getLogger(__name__ + func_name)



        loggerCmw.debug('%s results row extraction' %resultsType)



        index = self.get_row_index(resultsType)



        val_list     = [self.get_mod_cur_meas()[index],

                        self.get_mod_avg_meas()[index],

                        self.get_mod_max_meas()[index]]



        val_lim_list = [self.get_mod_cur_lim_meas()[index],

                        self.get_mod_avg_lim_meas()[index],

                        self.get_mod_max_lim_meas()[index]]



        val_list_str = ','.join(val_list)



        loggerCmw.debug(val_list_str)



        val_lim_list_str = ','.join(val_lim_list)



        loggerCmw.debug(val_lim_list_str)



        return val_list_str, val_lim_list_str



    def init_meas(self):

        if self.init_meas_flag:
            self.instrObj.write('INIT:%s:MEAS:MEValuation' %self.rat)
            self.waitForRDY()


    def enable_all_meas(self):



        self.instrObj.write('CONF:WCDM:MEAS:MEV:RES:ALL ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON,ON')



        rf_cf.pause(duration_s=2, poll_time_sec=1, desc="")



    def get_last_dummy_row_for_evm_array(self):

        """

        get UE average power and limit check result

        populate the other values with dummy information

        previously these corresponded to "Out of Tolerance"

        and "Slot Number" for CMU200 but these are not used for CMW500

        """



        func_name = sys._getframe(0).f_code.co_name

        loggerCmw = logging.getLogger(__name__ + func_name)



        #index = self.MEV_MOD_DICT['UEpower'] + 1



        index = self.get_row_index(keyValue='UEpower')



        dummy_1 = "NAV"     # Not available

        dummy_2 = "NAV"



        ue_avg_power = self.get_mod_avg_meas()[index]

        last_row_meas_str = ','.join([ue_avg_power,dummy_1,dummy_2])

        loggerCmw.debug('last meas row is %s' %last_row_meas_str)



        ue_avg_power_lim = self.get_mod_avg_lim_meas()[index]

        last_row_meas_lim_str = ','.join([ue_avg_power_lim, dummy_1, dummy_2])

        loggerCmw.debug('last meas lim check row is %s' %last_row_meas_lim_str)



        return last_row_meas_str, last_row_meas_lim_str



    def get_wcdma_mod_overview_results(self):



        self.init_meas()



        self.get_mod_meas_from_instr()



        evm_rms_row, evm_rms_lim_row = self.get_results_array_from_modulation(resultsType='EVMrms')



        evm_peak_row, evm_peak_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeak')



        magErr_rms_row, magErr_rms_lim_row = self.get_results_array_from_modulation(resultsType='MagErrorRMS')



        magErr_peak_row, magErr_peak_lim_row = self.get_results_array_from_modulation(resultsType='MagErrorPeak')



        phaseErr_rms_row, phaseErr_rms_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorRMS')



        phaseErr_peak_row, phaseErr_peak_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorPeak')



        iq_offset_row, iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')



        iq_imbalance_row, iq_imbalance_lim_row = self.get_results_array_from_modulation(resultsType='IQimbalance')



        carr_freq_err_row, carr_freq_err_lim_row = self.get_results_array_from_modulation(resultsType='CarrFreqErr')



        transit_time_err_row, transit_time_err_lim_row = self.get_results_array_from_modulation(resultsType='TransTimeErr')



        ue_pwr_row, ue_pwr_err_lim_row = self.get_results_array_from_modulation(resultsType='UEpower')



        ue_pwr_steps_row, ue_pwr_steps_lim_row = self.get_results_array_from_modulation(resultsType='PowerSteps')



        phase_disc_row, phase_disc_lim_row = self.get_results_array_from_modulation(resultsType='PhaseDisc')





        mod_meas = ','.join([evm_rms_row, evm_peak_row, magErr_rms_row,

                             magErr_peak_row, phaseErr_rms_row, phaseErr_peak_row,

                             iq_offset_row, iq_imbalance_row, carr_freq_err_row,

                             transit_time_err_row, ue_pwr_row, ue_pwr_steps_row,

                             phase_disc_row])



        mod_meas_lim = ','.join([evm_rms_lim_row, evm_peak_lim_row,  magErr_rms_lim_row,

                                 magErr_peak_lim_row, phaseErr_rms_lim_row, phaseErr_peak_lim_row,

                                 iq_offset_lim_row, iq_imbalance_lim_row, carr_freq_err_lim_row,

                                 transit_time_err_lim_row, ue_pwr_err_lim_row, ue_pwr_steps_lim_row,

                                 phase_disc_lim_row])





        return mod_meas, mod_meas_lim



    def set_meas_ctrl_stats(self, num_slots_per_stats_cycle=50):

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCOunt:MODulation %s'

                             %(self.rat, num_slots_per_stats_cycle))

        rf_cf.pause(duration_s=1, poll_time_sec=1, desc="")





    def get_evm_meas(self, num_cycles=50):



        self.set_meas_ctrl_stats(num_slots_per_stats_cycle=num_cycles)



        self.init_meas()



        self.get_mod_meas_from_instr()



        if self.get_meas_valid()== False:



            errMsg = "Not able to get valid measurements from CMW500"

            raise ExGeneral(errMsg)





        evm_peak_row, evm_peak_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeak')



        evm_rms_row, evm_rms_lim_row = self.get_results_array_from_modulation(resultsType='EVMrms')



        evm_iq_offset_row, evm_iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')



        evm_carr_freq_err_row, evm_carr_freq_err_lim_row = self.get_results_array_from_modulation(resultsType='CarrFreqErr')



        # peak code domain error

        # use dummy values as this is not reported by CMW500

        peak_cde_row ="NCAP,NCAP,NCAP"

        peak_cde_lim_row = "NAV,NAV,NAV"



        # get last row consisting of UE power, Out of Tolerance, Slot Number

        last_row, last_row_lim = self.get_last_dummy_row_for_evm_array()



        evm_meas = ','.join([evm_peak_row, evm_rms_row, evm_iq_offset_row,

                             evm_carr_freq_err_row, peak_cde_row, last_row])



        evm_meas_lim = ','.join([evm_peak_lim_row, evm_rms_lim_row,  evm_iq_offset_lim_row,

                                 evm_carr_freq_err_lim_row, peak_cde_lim_row, last_row_lim])





        return evm_meas, evm_meas_lim



    def get_perr_meas(self):



        self.init_meas()



        self.get_mod_meas_from_instr()



        if self.get_meas_valid()== False:



            errMsg = "Not able to get valid measurements from CMW500"

            raise ExGeneral(errMsg)





        perr_peak_row, perr_peak_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorPeak')



        perr_rms_row, perr_rms_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorRMS')



        evm_iq_offset_row, evm_iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')



        evm_carr_freq_err_row, evm_carr_freq_err_lim_row = self.get_results_array_from_modulation(resultsType='CarrFreqErr')



        # peak code domain error

        # use dummy values as this is not reported by CMW500

        peak_cde_row ="NCAP,NCAP,NCAP"

        peak_cde_lim_row = "NAV,NAV,NAV"



        # get last row consisting of UE power, Out of Tolerance, Slot Number

        #last_row, last_row_lim = self.get_last_dummy_row_for_evm_array()



        perr_meas = ','.join([perr_peak_row, perr_rms_row, evm_iq_offset_row,

                             evm_carr_freq_err_row, peak_cde_row])



        perr_meas_lim = ','.join([perr_peak_lim_row, perr_rms_lim_row,  evm_iq_offset_lim_row,

                                 evm_carr_freq_err_lim_row, peak_cde_lim_row])





        return perr_meas, perr_meas_lim



    """

    def get_perr_meas(self):



        func_name = sys._getframe(0).f_code.co_name



        loggerMeas = logging.getLogger(__name__ + func_name)



        self.instrObj.write('INIT:WCDMA:MEAS:MEValuation')



        self.waitForRDY()



        slot_num = self.get_slot_num()



        meas_period_str = self.get_meas_period()



        offset = 1  # firs element is reliability indicator



        if meas_period_str == 'FULLSLOT':



            array_index = slot_num + offset



        else:



            array_index = int(slot_num * 2) + offset



        loggerMeas.debug('Indexing into %s of the measurement array' %array_index)



        cmd = 'FETCh:WCDMa:MEAS:MEValuation:TRACe:PERRor:PEAK:CURRent?'

        tmpVal = self.extract_val_from_cmd(cmdquery=cmd, index=array_index)

        if self.get_meas_valid() == True:

            perr_peak_curr = tmpVal

        else:

            return



        cmd = 'FETCh:WCDMa:MEAS:MEValuation:TRACe:PERRor:PEAK:AVERage?'

        tmpVal = self.extract_val_from_cmd(cmdquery=cmd, index=array_index)

        if self.get_meas_valid() == True:

            perr_avg_curr = tmpVal

        else:

            return



        cmd = 'FETCh:WCDMa:MEAS:MEValuation:TRACe:PERRor:PEAK:MAXimum?'

        tmpVal = self.extract_val_from_cmd(cmdquery=cmd, index=array_index)

        if self.get_meas_valid() == True:

            perr_max_curr = tmpVal

        else:

            return



        #pass

    """



    def extract_val_from_cmd(self, cmdquery, index):

        rely_index = 0

        extracted_val = None

        responseStr = self.instrObj.read(cmdquery)

        responseList = responseStr.split(',')

        self.set_rely_ind (relyStr=self.MEAS_OK)

        if responseList[rely_index] == self.MEAS_OK:

            self.set_rely_ind (relyStr=self.MEAS_OK)

            extracted_val = responseList[index]

        else:

            self.set_rely_ind (relyStr=responseList[rely_index])

        return extracted_val



    def check_ul_detection_mode(self):

        expected_mode = 'A3G'

        det_mode = self.instrObj.read('CONFigure:%s:MEAS:MEValuation:DMODe:MODulation?'
                                       %self.rat)

        if det_mode == expected_mode:

            pass

        else:

            errMsg = ("Detection mode for UL signals is %s, should be %s"

                      %(det_mode,expected_mode))

            raise ExGeneral(errMsg)



    def start_meas(self):



        self.instrObj.write('INIT:WCDMA:MEAS:MEValuation')









if __name__ == '__main__':

    pass

