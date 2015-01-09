#-------------------------------------------------------------------------------
# Name:        cmw_lte_meas.py
# Purpose:
#
# Author:      joashr
#
# Created:     16/07/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, logging, time

#(abs_path, name)=os.path.split(os.path.abspath(__file__))

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-1])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *

import pl1_rf_system.common.rf_common_globals as rf_global

import pl1_rf_system.common.rf_common_functions as rf_cf

from pl1_rf_system.instr.cmw_wcdma_meas import Wcdma_meas


def reformat(list1, list2):
    """
    alternate the elemnts from both lists e.g.
    list1 = [1, 2, 3]
    list2 = [4, 5, 6]
    new_list = [1, 3, 2, 4, 3, 5]
    """
    new_list = []
    new_string = ""
    for x,y in list(zip(list1,list2)):
        new_list.append(x)
        new_list.append(y)

    return new_list

class Lte_meas(Wcdma_meas):

    """"
    measurment class for LTE measurements from CMW500
    """

    MEAS_OK = "0"


    # below aligns to output of

    # FETCh:LTE:MEAS<i>:MEValuation:MODulation:CURRent?

    # integer number value corresponds to paramter position to

    # results array

    MEV_MOD_DICT={'Reliability':1, 'OutOfTol':2, 'EVM_RMSlow':3,
                  'EVM_RMShigh':4, 'EVMpeakLow':5, 'EVMpeakHigh':6, 'MErr_RMSlow':7,
                  'MErr_RMShigh':8, 'MErrPeakLow':9, 'MErrPeakHigh':10, 'PErr_RMSlow':11,
                  'PErr_RMSh':12, 'PErrPeakLow':13, 'PErrPeakHigh':14, 'IQoffset':15,
                  'FreqError':16, 'TimingError':17, 'TXpower':18, 'PeakPower':19,
                  'RBpower':20, 'EVM_DMRSl':21, 'EVM_DMRSh':22, 'MErr_DMRSl':23,
                  'MErr_DMRSh':24, 'PErr_DMRSl':25, 'PErr_DMRSh':26, 'GainImbal':27,
                  'QuadError':28}

    # below aligns to output of

    # FETCh:LTE:MEAS<i>:MEValuation:MODulation:EXTReme?

    # integer number value corresponds to paramter position to

    # results array

    MEV_MOD_DICT_EX={'Reliability':1, 'OutOfTol':2, 'EVM_RMSlow':3,
                  'EVM_RMShigh':4, 'EVMpeakLow':5, 'EVMpeakHigh':6, 'MErr_RMSlow':7,
                  'MErr_RMShigh':8, 'MErrPeakLow':9, 'MErrPeakHigh':10, 'PErr_RMSlow':11,
                  'PErr_RMSh':12, 'PErrPeakLow':13, 'PErrPeakHigh':14, 'IQoffset':15,
                  'FreqError':16, 'TimingError':17,  'TXpowerMin':18, 'TXpowerMax':19,
                  'PeakPowerMin':20, 'PeakPowerMax':21,'RBpowerMin':22, 'RBpowerMax':23,
                  'EVM_DMRSl':24, 'EVM_DMRSh':25, 'MErr_DMRSl':26, 'MErr_DMRSh':27,
                  'PErr_DMRSl':28, 'PErr_DMRSh':29, 'GainImbal':30,
                  'QuadError':31}

    # Instrument Reliability Indicator
    REL_INDIC_DICT={'0':'OK', '1':'Measurement Timeout):', '2':'Capture Buffer Overflow',
                    '3':'INPUT Overdriven', '4':'INPUT Underdriven', '6':'Trigger Timeout',
                    '7':'Acquisition Error', '8':'Sync Error', '9':'Uncal',
                    '15':'Reference Frequency Error', '16':'RF Not Available',
                    '17':'RF Level not Settled', '18':'RF Frequency not Settled',
                    '19':'Call not Established', '20':'Call Type not Usable',
                    '21':'Call Lost', '23':'Missing Option', '101':'Firmware Error',
                    '102':'Unidentified Error', '103':'Parameter Error' }

    def __init__(self, instrObj=None):

        self.rat = "LTE"

        self.instrObj = instrObj

        self.rely_ind = "-1"    # measurement relaibility indicato

        self.meas_valid = False

        self.slot_for_stats = 0      # this is the slot number for stats and analysis
                                     # maps to Slot Number (Table)

        self.duplex_mode = None

        # this is the row index (0 based) measurement name dictionary mapping trmplate
        # for the measurement list
        # {0:'EVM_RMSlow', 1: 'EVM_RMShigh'}
        self.rowIndex_measName_dict = {}

        self.init_meas_flag = True


    def set_init_meas_flag (self,flag):
        self.init_meas_flag = flag

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


    def check_duplex_mode(self, exp_frame_structure):

        cur_frame_structure = self.instrObj.read('CONFigure:%s:MEAS:FSTRucture?'
                                                   %self.rat)
        if cur_frame_structure == exp_frame_structure:
            pass
        else:
            errMsg = ('Queried frame structure %s does not match duplex mode'
                      %cur_frame_structure)
            raise ExGeneral(errMsg)

    def set_duplex_mode(self, duplex_mode="FDD"):

        self.duplex_mode = duplex_mode
        self.instrObj.write('CONFigure:%s:MEAS:DMODe %s'
                     %(self.rat, duplex_mode))

    def get_duplex_mode(self):

        if self.duplex_mode:

            return self.duplex_mode

        else:
            errMsg = ("Duplex mode has not been set!")
            raise ExGeneral(errMsg)


    def set_default_general_settings(self, duplex_mode='FDD'):

        duplex_mode_dict = {'FDD':'T1', 'TDD':'T2'}

        try:
            frame_structure = duplex_mode_dict[duplex_mode.upper()]
            logging.info('Duplex mode %s selected' %duplex_mode)
        except:
            errMsg = ("Duplex mode %s is not supported. List of LTE duplex modes are %s"
                      %(duplex_mode, duplex_mode_dict.keys()))
            raise ExGeneral(errMsg)

        # <Mode> FDD | TDD
        self.set_duplex_mode(duplex_mode=duplex_mode)
        self.check_duplex_mode(exp_frame_structure=frame_structure)

        self.set_rf_freqMHz(freqMHz=1950)

        # external attaenuation setting

        self.set_rf_ext_att_in(atten_dB=0)

        # set the expected nominal power

        self.set_rf_exp_power(power_dBm=0)

        self.set_rf_user_margin(value_dB=12)

        self.set_mixer_level_offset_dB(val=0)

        self.set_freq_offset_Hz(freq=0)




    def set_mixer_level_offset_dB(self, val):

        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:MLOFfset %s'
                            %(self.rat, val))


    def set_freq_offset_Hz(self, freq):
        self.instrObj.write('CONFigure:%s:MEAS:RFSettings:FOFFset %s'
                             %(self.rat,freq))


    def set_cyclic_prefix(self, val="NORMal"):

        valid_cyclic_prefix = {'NORMAL':'NORMal', 'EXTENDED':'EXTended'}

        cmw_cyclic_prefix_str = self.get_val_from_allowed_values(dictionary=valid_cyclic_prefix,
                                                                 keyVal=val)

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:CPRefix %s'
                            %(self.rat, cmw_cyclic_prefix_str))

        self.cyclic_prefix = val.upper()

    def get_cyclic_prefix(self):

        return self.cyclic_prefix



    def set_ul_dl_conf(self, ul_dl_conf=0):
        self.instrObj.write('CONFigure:LTE:MEAS:MEValuation:ULDL %s'
                            %(ul_dl_conf))

    def set_special_subframe_conf(self, conf=0):
        self.instrObj.write('CONFigure:LTE:MEAS:MEValuation:SSUBframe %s'
                             %(conf))

    def get_val_from_allowed_values(self, dictionary, keyVal):
        try:
            dictVal = dictionary[keyVal.upper()]
            return dictVal
        except KeyError:
            errMsg = ("%s is not supported. List of supported values is %s"
                       %(keyVal, dictionary.keys()))
            raise ExGeneral(errMsg)


    def set_channel_bw_MHz (self, bwMHz=20):

        supported_bw_map_dict = {'1.4':'B014', '3':'B030', '5':'B050',
                                 '10':'B100', '15':'B150', '20':'B200'}
        cmw_bw_str = self.get_val_from_allowed_values(dictionary = supported_bw_map_dict,
                                                      keyVal = str(bwMHz))

        self.instrObj.write('CONFigure:%s:MEAS:CBANdwidth %s'
                             %(self.rat, cmw_bw_str))


    def set_conf_chtype_detection(self, chtype="PUSCh"):

        #<ChannelType> AUTO | PUSCh | PUCCh
        supported_chtype_dict = {'AUTO':'AUTO', 'PUSCH':'PUSCh', 'PUCCH':'PUCCh'}
        cmw_chtype_str = self.get_val_from_allowed_values(dictionary = supported_chtype_dict,
                                                          keyVal = chtype)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:CTYPe %s'
                             %(self.rat, cmw_chtype_str))

        self.chtype_detection = chtype

    def  get_conf_chtype_detection(self):

        return self.chtype_detection

    def set_pucch_format(self, pucch_format='F1'):
        # <PUCCHFormat> F1 | F1A | F1B | F2 | F2A | F2B
        supported_format_dict = {'F1':'F1','F1A':'F1A', 'F1B':'F1B',
                                 'F2':'F2', 'F2A':'F2A', 'F2B':'F2B'}
        cmw_pucch_format_str = self.get_val_from_allowed_values(dictionary = supported_format_dict,
                                                                keyVal = pucch_format)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:PFORmat %s'
                             %(self.rat, cmw_pucch_format_str))

    def set_nw_signaling_val(self, val="NS01"):
        supported_nw_values = {'NS01':'NS01','NS02':'NS02', 'NS03':'NS03', 'NS04':'NS04',
                               'NS05':'NS05', 'NS06':'NS06', 'NS07':'NS07', 'NS08':'NS08',
                               'NS09':'NS09', 'NS10':'NS10'}
        cmw_nw_sig_val_str = self.get_val_from_allowed_values(dictionary=supported_nw_values,
                                                              keyVal=val)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:NSValue %s'
                             %(self.rat, cmw_nw_sig_val_str))

    def set_rb_allocation_auto(self, auto="ON"):
        """
        Enables or disables the automatic detection of the RB configuration
        """
        allowable_auto_val_dict = {'OFF':'OFF', 'ON':'ON'}
        auto_str = self.get_val_from_allowed_values(dictionary = allowable_auto_val_dict,
                                                                 keyVal = auto)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:RBALlocation:AUTO %s'
                            %(self.rat, auto_str))

        if auto == "ON":
            self.rb_allocation_auto = "ON"
        else:
            self.rb_allocation_auto = "OFF"

    def get_rb_allocation_auto(self):

        return self.rb_allocation_auto

    def conf_measurement_subframe(self,
                                  subframeOffset=8,
                                  subframeCount=10,
                                  measSubframe=5):

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MSUBframes %s, %s, %s'
                            %(self.rat, subframeOffset, subframeCount, measSubframe))

    def config_mod_evm_len(self):
        prefix_B014 = 5 if self.get_cyclic_prefix()=="NORMAL" else 28
        prefix_B030 = 12 if self.get_cyclic_prefix()=="NORMAL" else 58
        prefix_B050 = 32 if self.get_cyclic_prefix()=="NORMAL" else 124
        prefix_B100 = 66 if self.get_cyclic_prefix()=="NORMAL" else 250
        prefix_B150 = 102 if self.get_cyclic_prefix()=="NORMAL" else 374
        prefix_B200 = 136 if self.get_cyclic_prefix()=="NORMAL" else 504

        prefix_ext_B014 = 28
        prefix_ext_B030 = 58
        prefix_ext_B050 = 124
        prefix_ext_B100 = 250
        prefix_ext_B150 = 374
        prefix_ext_B200 = 504

        prefix_list = [prefix_B014, prefix_B030, prefix_B050,
                       prefix_B100, prefix_B150, prefix_B200]
        prefix_ext_list = [prefix_ext_B014, prefix_ext_B030, prefix_ext_B050,
                           prefix_ext_B100, prefix_ext_B150, prefix_ext_B200]
        # convert list to string values
        concat_list = prefix_list + prefix_ext_list
        concat_list = [str(val) for val in concat_list]
        evm_list_str = ','.join(concat_list)

        self.instrObj.write('CONFigure:LTE:MEAS:MEValuation:MODulation:EWLength %s' %evm_list_str)

    def set_modulation_ul(self, modScheme):
        # Selects the modulation scheme used by the LTE uplink signal
        supported_mod_values = {'AUTO':'AUTO','QPSK':'QPSK','Q16':'Q16', 'Q64':'Q64'}
        cmw_mod_str = self.get_val_from_allowed_values(dictionary=supported_mod_values,
                                                       keyVal=modScheme)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MODulation:MSCHeme %s'
                            %(self.rat, cmw_mod_str))


    def set_up_meas_control(self):

        func_name = sys._getframe(0).f_code.co_name

        loggerCmw = logging.getLogger(__name__ + func_name)

        #<Repetition> SINGleshot | CONTinuous

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:REPetition SINGleshot'
                            %self.rat)

        # <StopCondition> NONE | SLFail

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCONdition None'
                            %(self.rat))

        #<MeasurementMode> NORMal | TMODe | MELMode
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MMODe NORMal'
                             %self.rat)

        # <MeasOnException> OFF | ON
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MOEXception OFF' %self.rat)

        if self.get_duplex_mode() == "TDD":

            self.set_ul_dl_conf(ul_dl_conf=0)

            self.set_special_subframe_conf(conf=0)

        # <CyclicPrefix> NORMal | EXTended
        """
        cyclic_prefix = "NORMal"
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:CPRefix %s'
                            %(self.rat, cyclic_prefix))
        """

        self.set_cyclic_prefix(val="NORMal")

        self.set_channel_bw_MHz(bwMHz='20')

        self.set_conf_chtype_detection(chtype="PUSCh")

        if self.get_conf_chtype_detection() == "PUCCH":

            self.set_pucch_format(pucch_format='F1')

        # set the networking signaling value
        self.set_nw_signaling_val(val="NS01")

        # set view filter
        # <NRBViewFilter>
        # Number of allocated resource blocks
        # Range: 	1  to  100
        # *RST:	1, OFF
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:NVFilter OFF'
                             %self.rat)

        # Specifies, enables or disables the channel type view filter
        #<ChannelType> PUSCh | PUCCh
        # PUSCh: measure only physical uplink shared channel
        #PUCCh: measure only physical uplink control channel
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:CTVFilter OFF'
                           %self.rat)

        self.set_rb_allocation_auto(auto="ON")

        if self.get_rb_allocation_auto == "OFF":
            offsetRB = 0
            self.instrObj.write('CONFigure:%s:MEAS:MEValuation:RBALlocation:ORB %s'
                                %(self.rat, offsetRB))
            NoRB = 100 # assumes 20 MHz bandwidth
            self.instrObj.write('CONFigure:%s:MEAS:MEValuation:RBALlocation:NRB %s'
                                 %(self.rat, NoRB))
        else:
            loggerCmw.debug('Manual RB allocation will not be applied as RB Allocation set to Auto')

        # physical layer cell ID
        phy_cell_id = 0
        self.instrObj.write ('CONFigure:%s:MEAS:MEValuation:PLCid %s'
                              %(self.rat, phy_cell_id))

        # Specifies the delta sequence shift value
        DeltaSeqShift = 0
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:DSSPusch %s'
                            %(self.rat, DeltaSeqShift))

        # Specifies whether group hopping is used or not
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:GHOPping OFF' %self.rat)

        self.conf_measurement_subframe()

        self.set_up_modulation()

        self.config_spectrum()

        self.config_power_meas()

        self.config_bler_meas()

        self.config_trigger()

        # enables measurement
        self.enable_meas()


    def set_up_modulation(self):

        self.set_modulation_ul(modScheme='QPSK')

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCOunt:MODulation 20' %self.rat)

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SRS:ENABle OFF'%self.rat)

        self.config_mod_evm_len()

        #Enables or disables EVM exclusion periods for slots with detected channel type "PUCCH".
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MODulation:EEPeriods:PUCCh ON'
                            %(self.rat))

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MODulation:EEPeriods:PUSCh:LEADing OFF'
                             %(self.rat))

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:MODulation:EEPeriods:PUSCh:LAGGing OFF'
                            %(self.rat))


    def config_spectrum(self):
        # spectrum emission mask
        statsCount = 20
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCOunt:SPECtrum:SEMask %s'
                             %(self.rat, statsCount))

        #<MeasFilter> BANDpass | GAUSs
        measFilter = "BAND"
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SPECtrum:SEMask:MFILter %s'
                             %(self.rat, measFilter))

        # adjacent channel leakage ratio
        statsCount = 20
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCOunt:SPECtrum:ACLR %s'
                            %(self.rat, statsCount))
        utra1_enable = "ON"
        utra2_enable = "ON"
        eutra_enable = "OFF"

        self.instrObj.write ('CONFigure:%s:MEAS:MEValuation:SPECtrum:ACLR:ENABle %s, %s, %s'
                             %(self.rat, utra1_enable, utra2_enable, eutra_enable))


    def config_power_meas(self):
        # Specify power measurement settings:
        # GOO: General ON/OFF time mask
        # PPSRs: PUCCH/PUSCH transmission before and after an SRS
        # SBLanking: SRS blanking time mask

        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:PDYNamics:TMASk GOO' %self.rat)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:PDYNamics:AEOPower:LAGGing 0' %self.rat)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:PDYNamics:AEOPower:LEADing 0' %self.rat)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:POWer:HDMode OFF' %self.rat)
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:SCOunt:POWer 20' %self.rat)

    def config_bler_meas(self):
        """
        Specifies the statistic count (number of measured subframes) and the number of
        scheduled subframes per radio frame for the BLER measurement. BLER is a single
        shot measurement.
        """
        # <Subframes>       Number of subframes to be measured
        # <SchedSubfrPerFr> Number of scheduled subframes per radio frame in the generated
        #                   downlink signal
        subframes = 10000
        sched_subframes_per_frame = 9
        self.instrObj.write('CONFigure:%s:MEAS:MEValuation:BLER:SFRames %s, %s'
                             %(self.rat, subframes, sched_subframes_per_frame))


    def set_trig_source(self, source='IF_Power'):
        valid_sources = {'FreeRunFastSync':'\'Free Run (Fast Sync)\'',
                         'FreeRunNoSync':'\'Free Run (No Sync)\'',
                         'IF_Power': '\'IF Power\'',
                         'Base1_External_TRIG_A': '\'Base1: External TRIG A\'',
                         'Base1_External_TRIG_B': '\'Base1: External TRIG B\''}

        valid_sources = rf_cf.convert_dict_keys_to_upper(valid_sources)
        cmw_trig_src = self.get_val_from_allowed_values(dictionary=valid_sources,
                                                        keyVal=source.upper())

        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:SOURce %s'
                             %(self.rat, cmw_trig_src))

    def set_trig_sync_mode(self, syncMode="Normal"):
        sync_mode_values = {'NORMal':'NORMal',
                            'ENHanced': 'ENHanced'}
        sync_mode_values=rf_cf.convert_dict_keys_to_upper(sync_mode_values)

        cmw_sync_str = self.get_val_from_allowed_values(dictionary=sync_mode_values,
                                                        keyVal=syncMode.upper())
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:SMODe %s'
                             %(self.rat, cmw_sync_str))

    def set_trig_acq_mode(self, acquisitionMode="Slot"):
        """
        Selects whether the R&S CMW synchronizes to a slot boundary or to a subframe
        boundary. The parameter is relevant for "Free Run (Fast Sync)" and for list mode
        measurements with Synchronization Mode = Enhanced.
        """
        acq_mode_values = {'SLOT':'SLOT',
                           'SUBFRAME': 'SUBFRAME'}

        cmw_acq_mode_str = self.get_val_from_allowed_values(dictionary=acq_mode_values,
                                                        keyVal=acquisitionMode.upper())
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:AMODe %s'
                             %(self.rat, cmw_acq_mode_str))

    def set_trig_delay(self, delay_us=0):
        """Defines a time delaying the start of the measurement relative to the trigger event. This
        setting has no influence on "Free Run" measurements."""
        delay_s = delay_us / 1e6
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:DELay %s' %(self.rat, delay_s))

    def config_trigger(self):
        self.set_trig_source(source='FreeRunFastSync')
        #<Slope> REDGe | FEDGe
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:SLOPe REDGe' %self.rat)

        # Defines the trigger threshold for power trigger sources.
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:THReshold -20' %self.rat)

        self.set_trig_delay(0)

        #Selects the maximum time that the R&S CMW will wait for a trigger event before it
        #stops the measurement in remote control mode or indicates a trigger timeout in manual
        #operation mode. This setting has no influence on "Free Run" measurements.
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:TOUT 0.1' %self.rat)

        #Sets a minimum time during which the IF signal must be below the trigger threshold
        #before the trigger is armed so that an IF power trigger event can be generated.
        self.instrObj.write('TRIGger:%s:MEAS:MEValuation:MGAP 2' %self.rat)

        self.set_trig_sync_mode(syncMode="Normal")

        self.set_trig_acq_mode(acquisitionMode="Slot")


    def get_mod_meas_from_instr(self):

        for modType in ['CURRENT', 'AVERAGE', 'EXTREME']:

            reading = self.instrObj.read('FETCh:%s:MEAS:MEValuation:MODulation:%s?'
                                         %(self.rat, modType))

            reading = reading.split(',')

            reliability_indicator = reading[0]

            self.set_rely_ind(relyStr=reliability_indicator)

            if self.get_meas_valid() != True:

                return

            reading_lim = self.instrObj.read('CALCulate:%s:MEAS:MEValuation:MODulation:%s?'
                                             %(self.rat, modType))

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

    def get_row_index(self, keyValue, fetchType=""):
        """
        gets the index position of keyValue in dictionary
        fetchType corresponds to FETCH SCPI measurement
        type which can be "current", "average" or "extreme"
        e.g.
        FETCh:LTE:MEAS<i>:MEValuation:MODulation:CUURent?
        FETCh:LTE:MEAS<i>:MEValuation:MODulation:AVERage?
        FETCh:LTE:MEAS<i>:MEValuation:MODulation:EXTReme?
        """
        func_name = sys._getframe(0).f_code.co_name

        logger_test = logging.getLogger(__name__ + " " + func_name)

        try:
            validList = {'CURRENT':1, 'AVERAGE':1, 'EXTREME':1}[fetchType.upper()]
        except KeyError:
            errMsg = ("%s is not supported, the list of supported values is %s" %
                      (fetchType, validList.keys()))

            raise ExGeneral(errMsg)

        # index is 1 based so subract 1 to get the zero based list index
        if fetchType.upper() == 'CURRENT' or fetchType.upper() == 'AVERAGE':
            index = self.MEV_MOD_DICT[keyValue] -  1
        else:
            try:
                index = self.MEV_MOD_DICT_EX[keyValue] -  1
            except KeyError:
                newKeyValue={'TXPOWER':'TXpowerMax', 'PEAKPOWER':'PeakPowerMax',
                             'RBPOWER':'RBpowerMax'}[keyValue.upper()]

                logger_test.debug("meas param %s does not exist in list of measurements" %keyValue)
                logger_test.debug("returned by FETCh:LTE:MEAS<i>:MEValuation:MODulation:EXTReme?")
                logger_test.debug("will extract %s instead" %newKeyValue)

                index = self.MEV_MOD_DICT_EX[newKeyValue] -  1

        return index

    def get_results_array_from_modulation(self, resultsType):

        """
        extract measurements data from the modulation measurements performed
        by get_mod_meas_from_instr
        get measurement in the form
        Current    #Average    #Extreme
        for measX
        # where measX can be EVM_RMSlow, EVM_RMShigh etc,
        # e.g. current EVM(RMS)    Average EVM(RMS)   Extreme EVM(RMS)
        """

        validTypeDict = self.MEV_MOD_DICT.copy()

        validTypeDict.update(self.MEV_MOD_DICT_EX)

        try:

            check = validTypeDict[resultsType]

        except KeyError:

            errMsg = ('Results type %s is not supported' %resultsType)

            errMsg +=('List of supported types are %s' %validTypeDict.keys())

            raise ExGeneral(errMsg)

        func_name = sys._getframe(0).f_code.co_name

        loggerCmw = logging.getLogger(__name__ + func_name)

        loggerCmw.debug('%s results row extraction' %resultsType)

        index_0 = self.get_row_index(resultsType, fetchType='Current')
        index_1 = self.get_row_index(resultsType, fetchType='Average')
        index_2 = self.get_row_index(resultsType, fetchType='Extreme')

        try:

            val_list     = [self.get_mod_cur_meas()[index_0],
                            self.get_mod_avg_meas()[index_1],
                            self.get_mod_max_meas()[index_2]]

            val_lim_list = [self.get_mod_cur_lim_meas()[index_0],
                            self.get_mod_avg_lim_meas()[index_1],
                            self.get_mod_max_lim_meas()[index_2]]

            val_list_str = ','.join(val_list)

            loggerCmw.debug(val_list_str)

            val_lim_list_str = ','.join(val_lim_list)

            loggerCmw.debug(val_lim_list_str)

        except IndexError:
            errMsg = " CMW Modulation measurment Index Error"
            self.RecordError(errMsg)

        return val_list_str, val_lim_list_str


    def enable_meas(self):
        """
        Enables or disables the evaluation of results and shows or hides the
        views in the multi evaluation measurement
        """
        evm="ON"; MagnitudeError="ON"; PhaseError="ON"; InbandEmissions="OFF"
        EVMversusC="ON"; IQ="ON"; EquSpecFlatness="OFF"; TXMeasurement="ON"
        SpecEmMask="ON"; ACLR="ON"; RBAllocTable="OFF"; PowerMonitor="OFF"
        BLER="OFF"; PowerDynamics="OFF"

        meas_enable_list = [evm, MagnitudeError, PhaseError, InbandEmissions,
                            EVMversusC, IQ, EquSpecFlatness, TXMeasurement,
                            SpecEmMask, ACLR, RBAllocTable, PowerMonitor,
                            BLER, PowerDynamics]

        meas_enable_list_str = ','.join(meas_enable_list)

        self.instrObj.write('CONFigure:LTE:MEAS:MEValuation:RESult:ALL %s' %meas_enable_list_str)

    def raise_rely_error(self):

        rely_ind = self.get_rely_ind()

        errMsg = "\nNot able to get valid measurements from CMW500"

        try:

            errMsg += ('\nReliability Indicator %s => %s' %(rely_ind, self.REL_INDIC_DICT[rely_ind]))

        except IndexError:

            errMsg += ('\nReliability Indicator %s' %rely_ind)

        raise ExGeneral(errMsg)


    def get_mod_overview_results(self, num_cycles=50):

        self.set_meas_ctrl_stats(num_slots_per_stats_cycle=num_cycles)

        self.init_meas()

        self.get_mod_meas_from_instr()

        if self.get_meas_valid()== False:

            self.raise_rely_error()


        map_dict = {}
        # get Current, Average, Extreme for EVM RMS, low and high
        evm_rms_l_row, evm_rms_l_lim_row = self.get_results_array_from_modulation(resultsType='EVM_RMSlow')
        evm_rms_h_row, evm_rms_h_lim_row = self.get_results_array_from_modulation(resultsType='EVM_RMShigh')
        map_dict[0]='EVM_RMSlow'
        map_dict[1]='EVM_RMShigh'

        # get Current, Average, Extreme for EVM Peak, low and high
        evm_peak_l_row, evm_peak_l_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeakLow')
        evm_peak_h_row, evm_peak_h_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeakHigh')
        map_dict[2]='EVMpeakLow'
        map_dict[3]='EVMpeakHigh'

        merr_rms_low, merr_rms_lim_low = self.get_results_array_from_modulation(resultsType='MErr_RMSlow')
        map_dict[4]='MErr_RMSlow'
        merr_rms_hi, merr_rms_lim_hi = self.get_results_array_from_modulation(resultsType='MErr_RMShigh')
        map_dict[5]='MErr_RMShigh'
        merr_peak_low, merr_peak_lim_low = self.get_results_array_from_modulation(resultsType='MErrPeakLow')
        map_dict[6]='MErrPeakLow'
        merr_peak_hi, merr_peak_lim_hi = self.get_results_array_from_modulation(resultsType='MErrPeakHigh')
        map_dict[7]='MErrPeakHigh'
        perr_rms_low, perr_rms_lim_low = self.get_results_array_from_modulation(resultsType='PErr_RMSlow')
        map_dict[8]='PErr_RMSlow'
        perr_rms_hi, perr_rms_lim_hi = self.get_results_array_from_modulation(resultsType='PErr_RMSh')
        map_dict[9]='PErr_RMSh'
        perr_pk_low, perr_pk_lim_low = self.get_results_array_from_modulation(resultsType='PErrPeakLow')
        map_dict[10]='PErrPeakLow'
        perr_pk_hi, perr_pk_lim_hi = self.get_results_array_from_modulation(resultsType='PErrPeakHigh')
        map_dict[11]='PErrPeakHigh'

        iq_offset_row, iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')
        map_dict[12]='IQoffset'

        freq_err_row, freq_err_lim_row = self.get_results_array_from_modulation(resultsType='FreqError')
        map_dict[13]= 'FreqError'

        timing_err_row, timing_err_lim_row = self.get_results_array_from_modulation(resultsType='TimingError')
        map_dict[14]='TimingError'

        tx_power_row, tx_power_lim_row  = self.get_results_array_from_modulation(resultsType='TXpower')
        map_dict[14]='TXpower'

        peak_power_row, peak_power_lim_row = self.get_results_array_from_modulation(resultsType='PeakPower')
        map_dict[16]='PeakPower'

        rb_pwr, rb_lim_pwr = self.get_results_array_from_modulation(resultsType='RBpower')
        map_dict[17]='RBpower'


        # DMRS refers to the demodulation reference signal within PUCCH and PUSCH.
        evm_dmrs_l_row, evm_dmrs_l_lim_row  = self.get_results_array_from_modulation(resultsType='EVM_DMRSl')
        map_dict[18]='EVM_DMRSl'
        evm_dmrs_h_row, evm_dmrs_h_lim_row = self.get_results_array_from_modulation(resultsType='EVM_DMRSh')
        map_dict[19]='EVM_DMRSh'

        merr_dmrs_lo, merr_dmrs_lim_lo = self.get_results_array_from_modulation(resultsType='MErr_DMRSl')
        map_dict[20]='MErr_DMRSl'
        merr_dmrs_hi, merr_dmrs_lim_hi = self.get_results_array_from_modulation(resultsType='MErr_DMRSh')
        map_dict[21]='MErr_DMRSh'
        perr_dmrs_lo, perr_dmrs_lim_lo = self.get_results_array_from_modulation(resultsType='PErr_DMRSl')
        map_dict[22]='PErr_DMRSl'
        perr_dmrs_hi, perr_dmrs_lim_hi = self.get_results_array_from_modulation(resultsType='PErr_DMRSh')
        map_dict[23]='PErr_DMRSh'
        gain_imb, gain_lim_imb = self.get_results_array_from_modulation(resultsType='GainImbal')
        map_dict[24]='GainImbal'
        quad_err, quad_lim_err = self.get_results_array_from_modulation(resultsType='QuadError')
        map_dict[25]='QuadError'


        mod_meas = ','.join([evm_rms_l_row, evm_rms_h_row, evm_peak_l_row, evm_peak_h_row,
                            merr_rms_low, merr_rms_hi, merr_peak_low, merr_peak_hi,
                            perr_rms_low, perr_rms_hi, perr_pk_low, perr_pk_hi,
                            iq_offset_row, freq_err_row, timing_err_row, tx_power_row,
                            peak_power_row, rb_pwr, evm_dmrs_l_row, evm_dmrs_h_row,
                            merr_dmrs_lo, merr_dmrs_hi, perr_dmrs_lo , perr_dmrs_hi,
                            gain_imb, quad_err])

        mod_meas_lim = ','.join([evm_rms_l_lim_row, evm_rms_h_lim_row, evm_peak_l_lim_row, evm_peak_h_lim_row,
                                 merr_rms_lim_low, merr_rms_lim_hi, merr_peak_lim_low, merr_peak_lim_hi,
                                 perr_rms_lim_low, perr_rms_lim_hi, perr_pk_lim_low, perr_pk_lim_hi,
                                 iq_offset_lim_row, freq_err_lim_row, timing_err_lim_row, tx_power_lim_row,
                                 peak_power_lim_row, rb_lim_pwr, evm_dmrs_l_lim_row, evm_dmrs_h_lim_row,
                                 merr_dmrs_lim_lo, merr_dmrs_lim_hi, perr_dmrs_lim_lo, perr_dmrs_lim_hi,
                                 gain_lim_imb, quad_lim_err])


        return mod_meas, mod_meas_lim, map_dict



    def get_evm_meas(self, num_cycles=50):

        self.set_meas_ctrl_stats(num_slots_per_stats_cycle=num_cycles)

        self.init_meas()

        self.get_mod_meas_from_instr()

        if self.get_meas_valid()== False:

            self.raise_rely_error()

        map_dict= {}

        # get Current, Average, Extreme for EVM RMS, low and high
        evm_rms_l_row, evm_rms_l_lim_row = self.get_results_array_from_modulation(resultsType='EVM_RMSlow')
        evm_rms_h_row, evm_rms_h_lim_row = self.get_results_array_from_modulation(resultsType='EVM_RMShigh')
        map_dict[0]='EVM_RMSlow'
        map_dict[1]='EVM_RMShigh'


        # get Current, Average, Extreme for EVM Peak, low and high
        evm_peak_l_row, evm_peak_l_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeakLow')
        evm_peak_h_row, evm_peak_h_lim_row = self.get_results_array_from_modulation(resultsType='EVMpeakHigh')
        map_dict[2]='EVMpeakLow'
        map_dict[3]='EVMpeakHigh'

        # DMRS refers to the demodulation reference signal within PUCCH and PUSCH.
        evm_dmrs_l_row, evm_dmrs_l_lim_row  = self.get_results_array_from_modulation(resultsType='EVM_DMRSl')
        evm_dmrs_h_row, evm_dmrs_h_lim_row = self.get_results_array_from_modulation(resultsType='EVM_DMRSh')
        map_dict[4]='EVM_DMRSl'
        map_dict[5]='EVM_DMRSh'

        iq_offset_row, iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')
        map_dict[6]='IQoffset'

        freq_err_row, freq_err_lim_row = self.get_results_array_from_modulation(resultsType='FreqError')
        map_dict[7]='FreqError'

        timing_err_row, timing_err_lim_row = self.get_results_array_from_modulation(resultsType='TimingError')
        map_dict[8]='TimingError'

        tx_power_row, tx_power_lim_row  = self.get_results_array_from_modulation(resultsType='TXpower')
        map_dict[9]='TXpower'

        peak_power_row, peak_power_lim_row = self.get_results_array_from_modulation(resultsType='PeakPower')
        map_dict[10]='TXpower'

        evm_meas = ','.join([evm_rms_l_row, evm_rms_h_row, evm_peak_l_row, evm_peak_h_row,
                             evm_dmrs_l_row, evm_dmrs_h_row, iq_offset_row,
                             freq_err_row, timing_err_row, tx_power_row, peak_power_row ])


        evm_meas_lim = ','.join([evm_rms_l_lim_row, evm_rms_h_lim_row, evm_peak_l_lim_row,
                                 evm_peak_h_lim_row, evm_dmrs_l_lim_row, evm_dmrs_h_lim_row,
                                 iq_offset_lim_row, freq_err_lim_row, timing_err_lim_row,
                                 tx_power_lim_row, peak_power_lim_row])


        return evm_meas, evm_meas_lim, map_dict


    def get_perr_meas(self):

        self.init_meas()

        self.get_mod_meas_from_instr()

        if self.get_meas_valid()== False:

            errMsg = "Not able to get valid measurements from CMW500"

            raise ExGeneral(errMsg)

        map_dict= {}

        perr_peak_row, perr_peak_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorPeak')
        map_dict[0]='PhErrorPeak'

        perr_rms_row, perr_rms_lim_row = self.get_results_array_from_modulation(resultsType='PhErrorRMS')
        map_dict[1]='PhErrorRMS'

        evm_iq_offset_row, evm_iq_offset_lim_row = self.get_results_array_from_modulation(resultsType='IQoffset')
        map_dict[2]='IQoffset'

        evm_carr_freq_err_row, evm_carr_freq_err_lim_row = self.get_results_array_from_modulation(resultsType='CarrFreqErr')
        map_dict[3]='CarrFreqEr'

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


        return perr_meas, perr_meas_lim, map_dict




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



if __name__ == '__main__':

    pass

