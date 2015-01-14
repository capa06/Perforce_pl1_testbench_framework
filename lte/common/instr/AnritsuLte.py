__author__ = 'chuyiq'
#! /usr/bin/env python

#######################################################################################################################
#
# Anritsu500 instrument driver class
#
#######################################################################################################################

# ********************************************************************
# IMPORT SYSTEM COMPONENTS
# ********************************************************************
import os
import sys
import logging
import time
import math
import re


# ********************************************************************
# DEFINE USER'S PATHS
# ********************************************************************
try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'instr']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'instr']))



# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from Anritsu import Anritsu
#from AnritsuLte import *

from CfgError import CfgError
#from os_utils import *
from cfg_lte import LTE_BW_MHZ_2_CFIMIN

from Struct    import Struct
from StructXml import StructXml


# ****************************************************************************************************
# GLOBAL VARIABLES
# ****************************************************************************************************



# ****************************************************************************************************
# GLOBAL FUNCTIONS
# ****************************************************************************************************
class AnritsuLte(Anritsu):
    CHECK_TABLE               = { 0:'PASS', 1:'FAIL' }
    Anritsu_LTE_BWMHZ             = {1.4:'1.4MHZ', 3:'3MHZ', 5:'5MHZ', 10:'10MHZ', 15:'15MHZ', 20:'20MHZ'}  #Anritsu MT8820C specific
    Anritsu_LTE_NPRB0             = {1.4:6, 3:6, 5:6, 10:6, 15:12, 20:12}
    Anritsu_LTE_SNR0              = 30

    Anritsu_LTE_MOD               = {'QPSK':'QPSK', '16QAM':'16QAM', '64QAM':'64QAM' }
    Anritsu_LTE_TM                = {1:'SINGLE', 2:'TX_DIVERSITY', 3:'OPEN_LOOP', 4:'CLOSED_LOOP_MULTI'}

    #Anritsu_LTE_TX42_PMI_TABLE    = range(0,3)
    #Anritsu_LTE_PA                = { 0:'ZERO', -3: 'N3DB',-6:'N6DB'}
    #Anritsu_LTE_TXANTS            = { 1:'ONE',   2:  'TWO', 4:'FOUR'}
    #Anritsu_LTE_PMI               = { 0: 'PMI0', 1: 'PMI1', 2: 'PMI2', 3: 'PMI3',
    #                              4: 'PMI4', 5: 'PMI5', 6: 'PMI6', 7: 'PMI7',
    #                              8: 'PMI8', 9: 'PMI9',10:'PMI10',11:'PMI11',
    #                             12:'PMI12',13:'PMI13',14:'PMI14',15:'PMI15'}

    Anritsu_LTE_RFBAND            = { 0: '0', 1: '1', 2:'2',  3: '3', 4: '4', 5:'5',  6: '6', 7: '7',
                                  8: '8', 9: '9',10:'10',11:'11',12:'12',13:'13',14:'14',15:'15',
                                 16:'16',17:'17',18:'18',19:'19',20:'20',21:'21',22:'22',23:'23',
                                 24:'24',25:'25',26:'26',27:'27',28:'28',29:'29',30:'30',31:'31',
                                 33:'33',34:'34',35:'35',36:'36',37:'37',38:'38',39:'39',40:'40',
                                 41:'41',44:'44'}

    #Anritsu_LTE_CFI_2_RPDCCH = {1:'ON', 2:'OFF', 3:'OFF'}
    Anritsu_LTE_NPRB0 = {1.4:3, 3:6, 5:6, 10:6, 15:12, 20:12}
    #Anritsu_LTE_CQI_REPORTING = {"RMC":"PER", "UDCH":"PER", "UDTT":"PER", "CQI,FWB":"PER", "CQI,FCPR":"PER", "CQI,FCRI":"PER" }

    #Anritsu_LTE_RAT = {'LTE_FDD':'FDD', 'LTE_FDD_CA':'FDD', 'LTE_TDD':'TDD', 'FDD':'FDD', 'TDD':'TDD'}








    Anritsu_LTE_MEAS_XMLFILE_TEMPLATE = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct', 'template', 'structxml_Anritsu500_lte_meas_template.xml'])


    def __init__(self, name, ip_addr, rat, xmlfile_config='structxml_Anritsu500_config_lte.xml'):

        self.rat             = rat
        self.param_check     = 0


        Anritsu.__init__(self, name, ip_addr)

        self.xmlfile_config = xmlfile_config
        self.common_config   = StructXml(xmlfile=xmlfile_config, struct_name=("%s.common_config" % self.name), node_name='common')
        self.pcc_config      = StructXml(xmlfile=xmlfile_config, struct_name=("%s.pcc_config" % self.name), node_name='pcc')
        self.scc_config      = StructXml(xmlfile=xmlfile_config, struct_name=("%s.scc_config" % self.name), node_name='scc')
        if len(self.scc_config.get_fieldname_list()) == 0:
            self.scc_config  = None
        self.log_config()

        self._meas_create()
        self._meas_init()



    def _meas_create(self):
        self.meas                = Struct()

        self.meas_dlbler_s       = Struct()
        self.meas_dlbler_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_dlbler_s.pcc" % self.name), node_name='dlbler')
        self.meas_dlbler_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_dlbler_s.scc" % self.name), node_name='dlbler')

        self.meas_ulbler_s       = Struct()
        self.meas_ulbler_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_ulbler_s.pcc" % self.name), node_name='ulbler')
        self.meas_ulbler_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_ulbler_s.scc" % self.name), node_name='ulbler')

        self.meas_dlthr_s       = Struct()
        self.meas_dlthr_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_dlthr_s.pcc" % self.name), node_name='dlthr')
        self.meas_dlthr_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_dlthr_s.scc" % self.name), node_name='dlthr')

        self.meas_rank_s       = Struct()
        self.meas_rank_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_rank_s.pcc" % self.name), node_name='rank')
        self.meas_rank_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_rank_s.scc" % self.name), node_name='rank')

        self.meas_cqi_s       = Struct()
        self.meas_cqi_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_cqi_s.pcc" % self.name), node_name='cqi')
        self.meas_cqi_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_cqi_s.scc" % self.name), node_name='cqi')

        self.meas_pmi_s       = Struct()
        self.meas_pmi_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_pmi_s.pcc" % self.name), node_name='pmi')
        self.meas_pmi_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_pmi_s.scc" % self.name), node_name='pmi')

        self.meas_harq_s       = Struct()
        self.meas_harq_s.pcc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_harq_s.pcc" % self.name), node_name='harq')
        self.meas_harq_s.scc   = StructXml(xmlfile=self.Anritsu_LTE_MEAS_XMLFILE_TEMPLATE, struct_name=("%s.meas_harq_s.scc" % self.name), node_name='harq')


    # ***************************
    # Private methods
    # ***************************
    def _meas_init(self):

        self.meas.period_nsf = None
        self.meas.period_sec = None
        self.meas.timeout    = None
        self.meas.check      = None

        self.meas_dlbler_s.pcc.struct_init()
        self.meas_dlbler_s.scc.struct_init()

        self.meas_ulbler_s.pcc.struct_init()
        self.meas_ulbler_s.scc.struct_init()

        self.meas_dlthr_s.pcc.struct_init()
        self.meas_dlthr_s.scc.struct_init()

        self.meas_rank_s.pcc.struct_init()
        self.meas_rank_s.scc.struct_init()

        self.meas_cqi_s.pcc.struct_init()
        self.meas_cqi_s.scc.struct_init()

        self.meas_pmi_s.pcc.struct_init()
        self.meas_pmi_s.scc.struct_init()

        self.meas_harq_s.pcc.struct_init()
        self.meas_harq_s.scc.struct_init()

    # ***************************
    # Public methods
    # ***************************
    def checkpoint(self):
        logger = logging.getLogger("%s._checkpoint_init" % self.name)
        # Summary
        logger.info("*****************************************************************************************")
        logger.info("CHECKPOINT for Anritsu500 configuration : %s" % ('FAIL' if self.param_check else 'PASS'))
        logger.info("*****************************************************************************************")
        if self.param_check:
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_PARAM_CHECK)

    def log_config(self):
        logger=logging.getLogger("%s.log_config" % self.name)
        logger.info("*****************************************************************************************")
        logger.info(" Anritsu500 initial configuration for %s" % self.rat)
        logger.info("*****************************************************************************************")
        logger.info(" COMMON: ")
        logger.info("**********")
        self.common_config.struct_log()
        logger.info(" PCC: ")
        logger.info("**********")
        self.pcc_config.struct_log()
        if not self.scc_config is None:
            logger.info(" SCC: ")
            logger.info("**********")
            self.scc_config.struct_log()
        logger.info("*****************************************************************************************")




    def lte_config_init(self, init_s):
        logger = logging.getLogger("%s.config_bler_init" % self.name)

        ## Set measurement period
        #self.lte_set_measurement_period(init_s)

        ## Disable all interferer
        self.lte_config_channel_none(init_s)

        # Configure duplex mode
        self.lte_config_duplex_mode(init_s)

        ## Configure scenario
        self.lte_config_scenario(init_s)


        # Configure downlink power levels
        self.lte_config_downlink_power_levels(init_s)

        ## Configure security
        self.lte_config_security(init_s)

        ## Configure RF
        self.lte_config_rf(init_s)
        self.lte_config_cp(init_s)
        self.lte_config_srs(init_s)
        self.lte_config_uplink_power_control(init_s)

        ## Configure Connection
        self.lte_config_connection(init_s)
        self.lte_config_cfi(init_s)
        self.lte_config_tm_pmi_txants(init_s)
        #self.lte_config_scheduler(init_s)
        self.lte_config_scheduler_attach(init_s)
        self.lte_config_harq(init_s)

        # Configure propagation scenario
        self.lte_config_channel(init_s)
        if 0:
            self.lte_config_rsepre(init_s)
            self.lte_update_scheduler(init_s)

        #self._checkpoint_init(init_s)
        self.checkpoint()
        logger.info("CONFIGURED Anritsu500 for attach")


        """
        self.write("SENSe:LTE:SIGN:UL:APPower:PATHloss?")
        self.write("SENSe:LTE:SIGN:UL:APPower:EPPPower?")
        self.write("SENSe:LTE:SIGN:UL:APPower:EOPower?")
        """




    def lte_config_scenario(self, init_s):
        logger = logging.getLogger('%s.lte_config_scenario' % self.name)

        if not init_s.scc is None:
            # ----------------------------
            # Carrier Aggregation scenario
            # ----------------------------
            if init_s.pcc.tm == 1:
                logger.error("Carrier Agregation scenario not supported by Anritsu yet : TM %s" % init_s.pcc.tm)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)


        else:
            # ----------------------------
            # Single Carrier scenario
            # ----------------------------
            if init_s.pcc.tm == 1:

                # Configure scenario for SC SISO
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                    # SC SISO with fading simulator
                    logger.error('Fading Mode not supported.')
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    # SC SISO without fading simulator
                    self._param_write("SCENARIO", self.common_config.routing_siso, 'siso')
                # Configure attenuation SC SISO


            elif (init_s.pcc.tm in [2,3,4]) and (init_s.pcc.txants==2):

                # Configure scenario for SC MIMO2x2
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                    # SC MIMO2x2 with fading simulator
                    logger.error('Fading Mode not supported.')
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    # SC MIMO2x2 without fading simulator
                    self._param_write("SCENARIO", self.common_config.routing_mimo2x2, 'mimo2x2')

                # Configure attenuation SC MIMO2x2

            elif (init_s.pcc.tm in [2,3,4]) and (init_s.pcc.txants==4):
                logger.error("Transmission mode not supported yet : TM %s" % init_s.pcc.tm)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)


    def lte_config_duplex_mode(self, init_s):
        logger = logging.getLogger("%s.lte_config_duplex_mode" % self.name)
        self._param_write("FRAMETYPE",init_s.pcc.dmode, 'duplex-mode')
        logger.info("CONFIGURED duplex mode")


    def lte_config_downlink_power_levels(self, init_s):
        logger = logging.getLogger('AnritsuLteBler.lte_config_downlink_power_levels')
        # Configure DL Power Level for PCC
        self._param_write("PDCCHPWR", init_s.pcc.rsepre, 'pcc.rsepre') #PDCCCH power=-30~0 dB
        self._param_write('OCNG_IDLE', self.pcc_config.ocng,'pcc_ocng_idel')

        if not init_s.scc is None:
            self._param_write("OLVL_EPRE", init_s.scc.rsepre, 'scc.rsepre')
            self._param_write("OCNG_CON", self.scc_config.ocng, 'scc_ocng_con')
            self._param_write("PDSCH_P_A", self.Anritsu_LTE_PA[init_s.scc.pa], 'scc.pa')
            self._param_write("PDSCH_P_B", init_s.scc.pb,'scc.pb')
        logger.info("CONFIGURED downlink power levels")


    def lte_config_security(self, init_s):
        logger = logging.getLogger("%s.lte_config_security" % self.name)
        self._param_write('AUTHENT','on','Authentication on')
        self._param_write("AUTHENT_ALGO", "XOR", 'XOR')
        self._param_write("INTEGRITY", "SNOW3G", 'Snow3G')
        logger.info("CONFIGURED security mode")


    def lte_config_rf(self, init_s):
        logger = logging.getLogger("%s._config_rf" % self.name)

        self._param_write("BAND", self.Anritsu_LTE_RFBAND[init_s.pcc.rfband], 'pcc.rfband')
        self._param_write("DLFREQ", init_s.pcc.earfcn, 'pcc.earfcn')
        self._param_write("CELLID", self.pcc_config.cellid, 'pcc.cellID')
        self._param_write("BANDWIDTH", self.Anritsu_LTE_BWMHZ[init_s.pcc.bwmhz], 'pcc bwmhz')
        if not init_s.scc is None:
            logger.error("Configuration not supported yet : %s" % init_s.scc)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        logger.info("CONFIGURED RF")


    def lte_config_cp(self, init_s):
        logger = logging.getLogger("%s.lte_config_cp" % self.name)
        #self._param_write("", init_s.pcc.cp, 'cp')
        logger.info("CONFIGURED CP")


    def lte_config_srs(self, init_s):
        logger = logging.getLogger("%s.lte_config_srs" % self.name)
        #self._param_write("CONFigure:LTE:SIGN:CELL:SRS:ENABle", self.common_config.cell_srs, 'srs')
        logger.info("CONFIGURED SRS")


    def lte_config_uplink_power_control(self, init_s):
        logger = logging.getLogger("%s._configure_uplink_power_control" % self.name)

        #self._param_write("CONFigure:LTE:SIGN:UL:APPower:EASettings", self.common_config.enable_ulpwrctrl_eas, "Enhanced power control")
        self._param_write('TCPPAT','AUTO','power contronl patern: AUTO')
        self._param_write('POWOFFSE','0.0','power control offset: 0.0')
        self._param_write('MAXULPWR',self.self.common_config.pmax,'Pmax')

        logger.info("CONFIGURED uplink power control")


    def lte_config_connection(self, init_s):
        logger = logging.getLogger("%s.lte_config_connection" % self.name)

        self._param_write('GROUPHOP',self.common_config.ghopping,'group hopping')
        self._param_write("UECAT", self.common_config.uecat, 'uecat') #value=CAT1 to CAT7
        self._param_write("UE_CAT?", self.common_config.uecat_reported, 'uecat report')
        self._param_write("PCYCLE", self.common_config.dpcycle, 'paging cycle')
        self._param_write("SIB2_NS", self.common_config.aseission, 'ASEmission')
        self._param_write("FILTERCOEF", self.common_config.fcoefficient, 'Filter Coefficient')#FC4 or FC8
        #self._param_write("CONFigure:LTE:SIGN:CONNection:FCOefficient", self.common_config.fcoefficient, 'FCOefficient')

        # Test or Data Application Mode
        self._param_write("RLCMODE", self.common_config.rlcmode, 'RLC mode')
        self._param_write("RRCRELEASE", self.common_config.krrc, 'Keep RRC') #ON or OFF, initial ON
        self._param_write("DNSSERVERIPRES", self.common_config.krrc, 'DNS response') #ON or OFF, initial OFF
        '''
        self._param_write("CONFigure:LTE:SIGN:CONNection:CTYPe", self.common_config.ctype, 'connection type')
        self._param_write("CONFigure:LTE:SIGN:CONNection:TMODe", self.common_config.tmode, 'test mode')
        self._param_write("CONFigure:LTE:SIGN:CONNection:RLCMode", self.common_config.rlcmode, 'RLC mode')
        self._param_write("CONFigure:LTE:SIGN:CONNection:SIBReconfig", self.common_config.sibreconf, 'SIB reconf')
        self._param_write("CONFigure:LTE:SIGN:CONNection:KRRC", self.common_config.krrc, 'Keep RRC')

        self._param_write("CONFigure:LTE:SIGN:CONNection:DLPadding", self.common_config.dlpadding, 'DL padding')
        self._param_write("CONFigure:LTE:SIGN:CONNection:DLEinsertion", self.common_config.dleinsertion, 'DL Error insertion')
        self._param_write("CONFigure:LTE:SIGN:CONNection:SDNSpco", self.common_config.sdnspco, 'Send DNS')
        '''
        logger.info("CONFIGURED connection")


    def lte_config_cfi(self, init_s):
        logger = logging.getLogger("%s.lte_config_cfi" % self.name)

        logger.info("PCC reduced PDCCH : %s" % self.Anritsu_LTE_CFI_2_RPDCCH[LTE_BW_MHZ_2_CFIMIN[init_s.pcc.bwmhz]])
        #self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:PDCCh:RPDCch", self.Anritsu_LTE_CFI_2_RPDCCH[LTE_BW_MHZ_2_CFIMIN[init_s.pcc.bwmhz]], 'pcc_cfi')
        if not init_s.scc is None:
            logger.info("SCC reduced PDCCH : %s" % self.Anritsu_LTE_CFI_2_RPDCCH[LTE_BW_MHZ_2_CFIMIN[init_s.scc.bwmhz]])
            #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:PDCCh:RPDCch", self.Anritsu_LTE_CFI_2_RPDCCH[LTE_BW_MHZ_2_CFIMIN[init_s.scc.bwmhz]], 'scc_cfi')

        logger.info("CONFIGURED CFI")


    def lte_config_tm_pmi_txants(self, init_s):
        logger = logging.getLogger("%s.lte_config_tm_pmi_txants" % self.name)

        # Check TXANTS
        if (not init_s.scc is None):
            if (init_s.pcc.txants != init_s.scc.txants):
                logger.error("Mismatch between numtxants[PCC]=%s and numtxants[SCC]=%s :" % (init_s.pcc.txants, init_s.scc.txants))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        # Check TM
        if not init_s.pcc.tm in [1, 2, 3, 4]:
            logger.error("PCC invalid or unsupported TM: %s" % init_s.pcc.tm)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        # Configure TM and PMI
        self._param_write('ANTCONFIG', self.Anritsu_LTE_TM[init_s.pcc.tm], 'pcc_txscheme')
        if not init_s.pcc.pmi is None:
            self._param_write("MATRIX", self.Anritsu_LTE_PMI[init_s.pcc.pmi], 'pcc_pmi')

        if not init_s.scc is None:
            if not init_s.scc.tm in [1,2,3,4]:
                logger.error("SCC invalid or unsupported TM: %s" % init_s.scc.tm)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            if init_s.pcc.tm in [2,3,4] and init_s.scc.tm in [1]:
                logger.error("Invalid TM configuration: TM[PCC]=%s. TM[SCC]=%s" % (init_s.pcc.tm, init_s.scc.tm))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            elif init_s.pcc.tm in [1] and init_s.scc.tm in [2,3,4]:
                logger.error("Invalid TM configuration: TM[PCC]=%s. TM[SCC]=%s" % (init_s.pcc.tm, init_s.scc.tm))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            else:
                pass

            # Configure TM and PMI
            #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:TSCHeme", self.Anritsu_LTE_TM[init_s.scc.tm], 'scc_txscheme')
            if not init_s.scc.pmi is None:
                logger.error('Carrier Agregation not supported yet')
                #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:PMATrix", self.Anritsu_LTE_PMI[init_s.scc.pmi], 'pcc_pmi')

        # Set TXANTS
        #self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:NENBantennas", self.Anritsu_LTE_TXANTS[init_s.pcc.txants], 'txants')
        if not init_s.scc is None:
            logger.error('Carrier Agregation not supported yet')
            #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:NENBantennas", self.Anritsu_LTE_TXANTS[init_s.scc.txants], 'txants')

        logger.info("CONFIGURED TM/PMI/TXANTS")


    def lte_config_scheduler_attach(self, init_s):
        logger = logging.getLogger("%s.lte_config_scheduler_attach" % self.name)

        # Use RMC scheduler for ATTACH
        schedtype="RMC"
        #self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", "RMC", 'pcc.schedtype')
        self._param_write('CHCODING','RMC','pcc.chcoding:RMC')
        self._param_write('SCHEDULING','STATIC','pcc.schedtype')
        self._param_write('CQIINTERVAL','10','CQI reporting interval')#5-40ms, initial 5ms
        self._param_write('CQI_RANGE','5','CQI counting range')#0-15, initial 3
        if not init_s.scc is None:
            logger.error('Function not supported yet')
            #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", "RMC", 'scc.schedtype')

        if self.Anritsu_LTE_CQI_REPORTING[schedtype]=='PER':
            logger.error('Function not supported yet')
            #self._param_write("CONFigure:LTE:SIGN:CQIReporting:ENABle", self.Anritsu_LTE_CQI_REPORTING[schedtype], 'cqi_reporting')
            #self._param_write("CONFigure:LTE:SIGN:CQIReporting:PCC:CINDex", self.pcc_config.cqi_index, 'cqi_index')
            if self.Anritsu_LTE_CQI_REPORTING[schedtype]=='PER':
                logger.error('Function not supported yet')
                #self._param_write("CONFigure:LTE:SIGN:CQIReporting:SCC:CINDex", self.scc_config.cqi_index, 'cqi_index')



    def lte_config_scheduler(self, init_s):
        logger = logging.getLogger("%s.lte_config_scheduler" % self.name)
        '''
        if init_s.pcc.schedtype=='UDCH':
            schedtype="UDCH"
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", schedtype, 'pcc.schedtype')
            # DL config
            param="%s,0,QPSK,4" % self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz]
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:UDCHannels:DL", param, "pcc.dlscheduling" )
            # UL config
            param="6,0,QPSK,4"
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:UDCHannels:UL", param, "pcc.ulscheduling" )

        elif init_s.pcc.schedtype=='UDTT':
            schedtype="UDTT"
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", schedtype, 'pcc.schedtype')
            for sf_idx in range(0,10):
                param="%s,%s,0,QPSK,4" % (sf_idx, self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz])
                # DL config
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
                # UL config
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)

        elif init_s.pcc.schedtype == 'CQI':
            # NOTE: 1. not possible to change the CQI index
            #       2. CQI reporting should be turned automatically to PERIODIC
            if init_s.pcc.tm == 4:
                schedtype = "CQI,FCPR"
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", schedtype, 'pcc.schedtype')
                param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz]
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FCPR:DL", param, 'sched_cqi_pmi_ri')

            elif init_s.pcc.tm == 3:
                schedtype = "CQI,FCRI"
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", schedtype, 'pcc.schedtype')
                param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz]
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FCRI:DL", param, 'sched_cqi_ri')

            else:
                schedtype = "CQI,FWB"
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:STYPe", schedtype, 'pcc.schedtype')
                param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz]
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FWBCqi:DL", param, 'sched_cqi')

            # PCC UL config
            for sf_idx in range(0,10):
                param="%s,%s,0,QPSK,4" % (sf_idx, self.Anritsu_LTE_NPRB0[init_s.pcc.bwmhz])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
        else:
            logger.error("PCC invalid scheduler type : %s" % init_s.pcc.schedtype)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not init_s.scc is None:
            if init_s.scc.schedtype=='UDCH':
                schedtype="UDCH"
                self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", schedtype, 'pcc.schedtype')
                # DL config
                param="%s,0,QPSK,4" % self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz]
                self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:UDCHannels:DL", param, "pcc.dlscheduling" )
                # SCC UL config
                #param="6,0,QPSK,4"
                #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:UDCHannels:UL", param, "pcc.ulscheduling" )

            elif init_s.scc.schedtype=='UDTT':
                schedtype="UDTT"
                self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", schedtype, 'pcc.schedtype')
                for sf_idx in range(0,10):
                    param="%s,%s,0,QPSK,4" % (sf_idx, self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz])
                    # DL config
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                    # SCC UL config
                    #self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)

            elif init_s.scc.schedtype == 'CQI':
                # NOTE: 1. not possible to change the CQI index
                #       2. CQI reporting should be turned automatically to PERIODIC
                if init_s.scc.tm == 4:
                    schedtype = "CQI,FCPR"
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", schedtype, 'scc.schedtype')
                    param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz]
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FCPR:DL", param, 'sched_cqi_pmi_ri')
                elif init_s.scc.tm == 3:
                    schedtype = "CQI,FCRI"
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", schedtype, 'scc.schedtype')
                    param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz]
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FCRI:DL", param, 'sched_cqi_ri')
                else:
                    schedtype = "CQI,FWB"
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:STYPe", schedtype, 'scc.schedtype')
                    param = "%s,0,DET" % self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz]
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FWBCqi:DL", param, 'sched_cqi')

                ## SCC UL config
                #for sf_idx in range(0,10):
                #    param="%s,%s,0,QPSK,4" % (sf_idx, self.Anritsu_LTE_NPRB0[init_s.scc.bwmhz])
                #    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)

            else:
                logger.error("SCC invalid scheduler type : %s" % init_s.scc.schedtype)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        '''
        logger.info("CONFIGURED scheduling information")

    def lte_update_scheduler(self, init_s):
        logger = logging.getLogger("%s.lte_update_scheduler" % self.name)

        from cfg_lte import GetDLModulation, GetULModulation, LTE_DL_IMCS_2_ITBS_QM, LTE_UL_IMCS_2_ITBS_QM

        # Configure TX scheme
        self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:TSCHeme", self.Anritsu_LTE_TM[init_s.pcc.tm], 'pcc.tm')
        if not init_s.scc is None:
            self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:TSCHeme", self.Anritsu_LTE_TM[init_s.scc.tm], 'scc.tm')

        # Reconfigure DL scheduler
        if init_s.pcc.schedtype=='UDCH':
            # DL config
            param = "%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:UDCHannels:DL", param, "pcc_dlscheduling" )
            # UL config
            param = "%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:UDCHannels:UL", param, "pcc_ulscheduling")


        elif init_s.pcc.schedtype=='UDTT':
            # DL config
            param = "0,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "1,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "2,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "3,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "4,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "5,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "6,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "7,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "8,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            param = "9,%s,%s,%s,%s" %(init_s.pcc.dlnprb, init_s.pcc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:DL", param)
            # UL config
            param = "0,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "1,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "2,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "3,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "4,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "5,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "6,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "7,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "8,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)
            param = "9,%s,%s,%s,%s" % (init_s.pcc.ulnprb, init_s.pcc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.pcc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.pcc.ulmcs][0])
            self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)

        elif init_s.pcc.schedtype=='CQI':
            # DL config
            param="%s,%s,DET" % (init_s.pcc.dlnprb, init_s.pcc.dlrbstart)
            if init_s.pcc.tm == 4:
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FCPR:DL", param, "pcc_dlscheduling")
            elif init_s.pcc.tm == 3:
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FCRI:DL", param, "pcc_dlscheduling")
            else:
                self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:FWBCqi:DL", param, "pcc_dlscheduling")
            # UL config
            for sf_idx in range(0,10):
                param="%s,6,0,QPSK,4" % sf_idx
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:UDTTibased:UL", param)

        if not init_s.scc is None:
            if init_s.scc.schedtype=='UDCH':
                # DL config
                param = "%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:UDCHannels:DL", param, "scc_dlscheduling" )
                #UL config
                #param = "%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:UDCHannels:UL", param, "scc_ulscheduling")

            elif init_s.scc.schedtype=='UDTT':
                # Dl config
                param = "0,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "1,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "2,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "3,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "4,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "5,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "6,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "7,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "8,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                param = "9,%s,%s,%s,%s" %(init_s.scc.dlnprb, init_s.scc.dlrbstart, self.Anritsu_LTE_MOD[GetDLModulation(init_s.scc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.scc.dlmcs][0])
                self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:DL", param)
                #UL config
                if 0:
                    param = "0,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "1,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "2,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "3,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "4,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "5,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "6,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "7,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "8,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)
                    param = "9,%s,%s,%s,%s" % (init_s.scc.ulnprb, init_s.scc.ulrbstart, self.Anritsu_LTE_MOD[GetULModulation(init_s.scc.ulmcs)], LTE_UL_IMCS_2_ITBS_QM[init_s.scc.ulmcs][0])
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)

            elif init_s.scc.schedtype=='CQI':
                # DL config
                param="%s,%s,DET" % (init_s.scc.dlnprb, init_s.scc.dlrbstart)
                if init_s.scc.tm == 4:
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FCPR:DL", param, "scc_dlscheduling")
                elif init_s.pcc.tm == 3:
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FCRI:DL", param, "scc_dlscheduling")
                else:
                    self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:FWBCqi:DL", param, "scc_dlscheduling")
                # UL config
                if 0:
                    param="%s,6,0,QPSK,4" % sf_idx
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:UDTTibased:UL", param)

        logger.info("UPDATED scheduling information")


    def lte_config_harq(self, init_s):
        logger = logging.getLogger("%s.lte_config_dlharq" % self.name)

        if (init_s.pcc.nhrtx is None):
            #self._param_write("CONFigure:LTE:SIGN:CONNection:HARQ:DL:ENABle", "OFF", 'harq')
            self._param_write('MAXHARQTX','1','HARQ off')
        else:
            if (not init_s.pcc.riv is None):
                self._param_write("MAXHARQTX", init_s.pcc.nhrtx, 'pcc.nhrtx')
                #self._param_write("CONFigure:LTE:SIGN:CONNection:HARQ:DL:NHT", init_s.pcc.nhrtx, 'pcc.nhrtx')
                #self._param_write("CONFigure:LTE:SIGN:CONNection:HARQ:DL:RVCSequence", "UDEF", 'harqmode')
                #self._param_write("CONFigure:LTE:SIGN:CONNection:HARQ:DL:UDSequence:LENGth", len(init_s.pcc.riv.split(' ')), 'pcc.nhrtx')
                #self._param_write("CONFigure:LTE:SIGN:CONNection:HARQ:DL:UDSequence", init_s.pcc.riv.replace(' ',','), 'pcc.riv')
            else:
                logger.error("Invalid HARQ setting: (nhrtx=%s, riv=%s)" % (init_s.scc.schedtype, init_s.pcc.riv))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not (init_s.scc is None):
            logger.warning("SCC HARQ indipendent configuration is not available. PCC and SCC have same settings for HARQ")
            pass
        logger.info("CONFIGURED harq")


    def lte_config_rsepre(self, init_s):
        logger = logging.getLogger("%s.lte_config_rsepre" % self.name)
        self._param_write("OLVL_EPRE", init_s.pcc.rsepre, 'pcc.rsepre')
        logger.debug("Changed PCC RSEPRE level to %s [dBm]" % init_s.pcc.rsepre)
        if not init_s.scc is None:
            logger.error('Function not supported yet')
            #self._param_write("CONFigure:LTE:SIGN:DL:SCC:RSEPre:LEVel", init_s.scc.rsepre, 'scc.rsepre')
            #logger.debug("Changed SCC RSEPRE level to %s [dBm]" % init_s.scc.rsepre)
        self.lte_config_snr(init_s)

        logger.info("UPDATED rsepre")

    # **********************************************************************************************************
    # PROPAGATION CHANNEL CONFIGUARTION FUNCTIONS
    # **********************************************************************************************************
    def lte_config_channel(self, init_s):
        logger = logging.getLogger("%s.lte_config_channel" % self.name)
        if init_s.pcc.chtype is None:
            self.lte_config_channel_none(init_s)
            logger.info("Disabled source interferer")
        else:
            if init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS:
                self.lte_config_channel_fsim(init_s)
                logger.info("Configured FSIM")

            elif init_s.pcc.chtype.upper()=='AWGN':
                self.lte_config_channel_awgn(init_s)
                self._param_write('AWGNLVL','ON','AWGN level on')
                logger.info("Configured AWGN generator")

            elif init_s.pcc.chtype.upper() in ['STCHL','STCHM','STCHH']:
                self.lte_config_channel_static(init_s)
                logger.info("Configured Static Channel")

            else:
                logger.error("PCC invalid propagation scenario %s" % init_s.pcc.chtype)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        logger.info("CONFIGURED propagation scenario")


    def lte_config_channel_none(self, init_s):
        #logger = logging.getLogger("%s.lte_config_channel_none" % self.name)
        self.lte_fsim_int_toggle(state='OFF', carrier='PCC')
        self.lte_external_awgn_toggle(state='OFF', carrier='PCC')
        self.lte_static_channel_toggle(state='OFF', carrier='PCC')
        if not init_s.scc is None:
            self.lte_fsim_int_toggle(state='OFF', carrier='SCC')
            self.lte_external_awgn_toggle(state='OFF', carrier='SCC')
            self.lte_static_channel_toggle(state='OFF', carrier='SCC')


    def lte_config_channel_fsim(self, init_s):
        #logger = logging.getLogger("%s.lte_config_channel_fsim" % self.name)
        self.lte_external_awgn_toggle(state='OFF', carrier='PCC')
        self.lte_static_channel_toggle(state='OFF', carrier='PCC')
        self.lte_fsim_int_toggle(state='ON', carrier='PCC')
        self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:STANdard", init_s.pcc.chtype, 'pcc.chtype')
        if (init_s.pcc.tm in [2,3,4]) and (init_s.pcc.txants==4):
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:RESTart:MODE", "TRIG", 'pcc.fsim.mode')
        else:
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:RESTart:MODE", "AUTO", 'pcc.fsim.mode')
        self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:GLOBal:SEED", 0, 'pcc.fsim.seed')
        self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:ILOSs:MODE", "NORM", 'pcc.fsim.iloss')
        if not init_s.pcc.snr is None:
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:AWGN:ENABle", "ON", 'pcc.fsim.awgn')
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:AWGN:BWIDth:RATio", 1, 'pcc.fsim.bw_ratio')
        else:
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:AWGN:ENABle", "OFF", 'pcc.fsim.awgn')

        if not init_s.scc is None:
            self.lte_external_awgn_toggle(state='OFF', carrier='SCC')
            self.lte_static_channel_toggle(state='OFF', carrier='SCC')
            self.lte_fsim_int_toggle(state='ON', carrier='SCC')
            self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:STANdard", init_s.scc.chtype, 'scc.chtype')
            if (init_s.pcc.tm in [2,3,4]) and (init_s.pcc.txants==4):
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:RESTart:MODE", "TRIG", 'scc.fsim.mode')
            else:
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:RESTart:MODE", "AUTO", 'scc.fsim.mode')
            self._param_write("CONFigure:LTE:SIGN:FADing:sCC:FSIMulator:GLOBal:SEED", 0, 'scc.fsim.seed')
            self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:ILOSs:MODE", "NORM", 'scc.fsim.iloss')
            if not init_s.scc.snr is None:
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:AWGN:ENABle", "ON", 'scc.fsim.awgn')
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:AWGN:BWIDth:RATio", 1, 'scc.fsim.bw_ratio')
            else:
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:AWGN:ENABle", "OFF", 'scc.fsim.awgn')

        self.lte_config_snr(init_s, use_default_snr=1)



    def lte_config_channel_awgn(self, init_s):
        logger = logging.getLogger("%s.lte_config_channel_awgn" % self.name)

        self.lte_fsim_int_toggle(state='OFF', carrier='PCC')
        self.lte_static_channel_toggle(state='OFF', carrier='PCC')
        self.lte_external_awgn_toggle(state='ON', carrier='PCC')
        if not init_s.scc is None:
            self.lte_fsim_int_toggle(state='OFF', carrier='SCC')
            self.lte_static_channel_toggle(state='OFF', carrier='SCC')
            self.lte_external_awgn_toggle(state='ON', carrier='SCC')

        self.lte_config_snr(init_s, use_default_snr=1)
        logger.info("Configured AWGN generator")


    def lte_config_channel_static(self, init_s):
        logger = logging.getLogger("%s.lte_config_channel_static" % self.name)

        self.lte_fsim_int_toggle(state='OFF', carrier='PCC')
        self.lte_external_awgn_toggle(state='ON', carrier='PCC')
        self.lte_static_channel_toggle(state='ON', carrier='PCC')
        if not init_s.pcc.chtype is None:
            if (init_s.pcc.chtype in ['STCHL', 'STCHM', 'STCHH']) and (init_s.pcc.txants in [2,4]):
                coeff_m = self.Anritsu_LTE_STCH_COEFF[init_s.pcc.chtype][init_s.pcc.txants]
                if init_s.pcc.txants==2:
                    logger.info("Static channel MIMO TX2x2 configuration:")
                    #self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:SCHModel", coeff_m, 'STCHL.TX2x2)')
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:SCHModel", coeff_m)
                else:
                    logger.info("Static channel MIMO TX4x2 configuration:")
                    #self._param_write("CONFigure:LTE:SIGN:CONNection:PCC:SCHModel:MIMO42", coeff_m, 'STCHL.TX4x2)')
                    self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:PCC:SCHModel:MIMO42", coeff_m)
            else:
                logging.error("PCC invalid static channel configuration: chtype=%s, txants=%s" % (init_s.pcc.chtype, init_s.pcc.txants))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        else:
            logging.error("PCC invalid static channel configuration: chtype=%s, txants=%s" % (init_s.pcc.chtype, init_s.pcc.txants))
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not init_s.scc is None:
            self.lte_fsim_int_toggle(state='OFF', carrier='SCC')
            self.lte_static_channel_toggle(state='ON', carrier='SCC')
            self.lte_external_awgn_toggle(state='ON', carrier='SCC')

            if not init_s.scc.chtype is None:
                if (init_s.scc.chtype in ['STCHL', 'STCHM', 'STCHH']) and (init_s.scc.txants in [2,4]):
                    coeff_m = self.Anritsu_LTE_STCH_COEFF[init_s.scc.chtype][init_s.scc.txants]
                    if init_s.scc.txants==2:
                        logger.info("Static channel MIMO TX2x2 configuration:")
                        #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:SCHModel", coeff_m, 'STCHL.TX2x2)')
                        self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:SCHModel", coeff_m)
                    else:
                        logger.info("Static channel MIMO TX4x2 configuration:")
                        #self._param_write("CONFigure:LTE:SIGN:CONNection:SCC:SCHModel:MIMO42", coeff_m, 'STCHL.TX4x2)')
                        self._param_write_nocheck("CONFigure:LTE:SIGN:CONNection:SCC:SCHModel:MIMO42", coeff_m)
                else:
                    logging.error("PCC invalid static channel configuration: chtype=%s, txants=%s" % (init_s.scc.chtype, init_s.scc.txants))
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            else:
                logging.error("PCC invalid static channel configuration: chtype=%s, txants=%s" % (init_s.scc.chtype, init_s.scc.txants))
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        self.lte_config_snr(init_s, use_default_snr=-1)


    def lte_fsim_int_toggle(self, state, carrier):
        logger = logging.getLogger("%s.lte_fsim_int_toggle" % self.name)
        num_iter, NUM_ITER_MAX = 0, 10
        POLL_INTERVAL = 2

        state   = state.upper()
        carrier = carrier.upper()

        if not state in ['ON','OFF']:
            logger.error("Invalid state %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not carrier in ['PCC','SCC']:
            logger.error("Invalid carrier %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        cmd       = "CONFigure:LTE:SIGN:FADing:%s:FSIMulator:ENABle" % carrier
        completed = (self._param_read(cmd) == state)

        while (not completed) and (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("Turning %s internal fader: iteration %d of %d" % (state, num_iter, NUM_ITER_MAX))
            completed = (self._param_write(cmd, state, 'fsim') == 0)
            if completed: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logger.error("SCPI command failure")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_SCPI_FAILURE)
        logger.info("LTE internal fading simulator turned %s" % state)


    def lte_external_awgn_toggle(self, state, carrier):
        logger = logging.getLogger("%s.lte_external_awgn_toggle" % self.name)
        num_iter, NUM_ITER_MAX = 0, 5
        POLL_INTERVAL = 2

        state   = state.upper()
        carrier = carrier.upper()

        if not state in ['ON','OFF']:
            logger.error("Invalid state %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not carrier in ['PCC','SCC']:
            logger.error("Invalid carrier %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        #cmd       = "CONFigure:LTE:SIGN:DL:%s:AWGN" % carrier
        cmd='AWGNLVL'
        readback  = self._param_read(cmd)
        completed = (readback == state) or ((state == "ON") and (readback != "OFF"))


        while (not completed) and (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("Turning %s external AWGN: iteration %d of %d" % (state, num_iter, NUM_ITER_MAX))
            self._param_write_nocheck(cmd, state)
            readback  = self._param_read(cmd)
            completed = (readback == state) or ((state == "ON") and (readback != "OFF"))
            if completed: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logger.error("SCPI command failure")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_SCPI_FAILURE)

        logger.info("LTE external AWGN interferer turned %s" % state)


    def lte_static_channel_toggle(self, state, carrier):
        logger = logging.getLogger("%s.lte_static_channel_toggle" % self.name)
        num_iter, NUM_ITER_MAX = 0, 10
        POLL_INTERVAL = 2

        state   = state.upper()
        carrier = carrier.upper()

        if not state in ['ON','OFF']:
            logger.error("Invalid state %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not carrier in ['PCC','SCC']:
            logger.error("Invalid carrier %s. TEST ABORTED" % state)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        cmd       = "CONFigure:LTE:SIGN:CONNection:%s:SCHModel:ENABle" % carrier
        completed = (self._param_read(cmd) == state)

        while (not completed) and (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("Turning %s static channel: iteration %d of %d" % (state, num_iter, NUM_ITER_MAX))
            completed = (self._param_write(cmd, state, 'static_channel') == 0)
            if completed: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logger.error("SCPI command failure")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_SCPI_FAILURE)
        logger.info("LTE static channel turned %s" % state)


    def lte_config_snr(self, init_s, use_default_snr=0):
        logger = logging.getLogger("%s.lte_config_snr" % self.name)
        if not init_s.pcc.chtype is None:
            if not init_s.pcc.snr is None:
                logger.info("PCC SNR update for %-10s: %s)" % (init_s.pcc.chtype, (self.Anritsu_LTE_SNR0 if use_default_snr else init_s.pcc.snr)))
                pcc_awgn_level= (-self.Anritsu_LTE_SNR0) if use_default_snr else (-init_s.pcc.snr)
                if init_s.pcc.chtype in ['AWGN', 'STCHL', 'STCHM', 'STCHH']:
                    self._param_write("AWGNPWR", pcc_awgn_level, 'pcc_awgn_level')#AWGN power level -30dB-5dB

                if (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                    self._param_write("AWGNPWR", init_s.pcc.snr, 'pcc.fsim.snr')
            else:
                logger.error("PCC invalid SNR : None")
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not init_s.scc is None:
            if not  init_s.scc.chtype is None:
                if not init_s.scc.snr is None:
                    logger.info("SCC SNR update for %-10s: %s)" % (init_s.scc.chtype, (self.Anritsu_LTE_SNR0 if use_default_snr else init_s.scc.snr)))
                    scc_awgn_level= (init_s.scc.rsepre-self.Anritsu_LTE_SNR0) if use_default_snr else (init_s.scc.rsepre-init_s.scc.snr)
                    if init_s.scc.chtype in ['AWGN', 'STCHL', 'STCHM', 'STCHH']:
                        self._param_write("AWGNPWR", scc_awgn_level, 'scc_awgn_level')
                    if (init_s.scc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                        self._param_write("AWGNPWR", init_s.scc.snr, 'scc.fsim.snr')
                else:
                    logger.error("SCC invalid SNR : None")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)


    def lte_config_doppler(self, init_s):
        logger = logging.getLogger("%s.lte_config_doppler" % self.name)

        if (not init_s.pcc.doppler is None) and (not init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
            logger.error("Doppler shifth N/A for AWGN/Static/None channel")
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        elif (not init_s.pcc.doppler is None) and (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:DSHift:MODE", "USER", 'pcc.doppler.mode')
            self._param_write("CONFigure:LTE:SIGN:FADing:PCC:FSIMulator:DSHift", init_s.pcc.doppler, 'pcc.doppler.shift')
            logger.info("PCC Updated doppler shift for chtype %s: %s[Hz]" % (init_s.pcc.chtype, init_s.pcc.doppler))
        else:
            pass

        if not init_s.scc is None:
            if (not init_s.scc.doppler is None) and (not init_s.scc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                logger.error("Doppler shifth N/A for AWGN/Static/None channel")
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            elif (not init_s.scc.doppler is None) and (init_s.scc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:DSHift:MODE", "USER", 'scc.doppler.mode')
                self._param_write("CONFigure:LTE:SIGN:FADing:SCC:FSIMulator:DSHift", init_s.scc.doppler, 'scc.doppler.shift')
                logger.info("SCC Updated doppler shift for chtype %s: %s[Hz]" % (init_s.scc.chtype, init_s.scc.doppler))
            else:
                pass


    def lte_config_earfcn(self, carrier, earfcn):
        logger = logging.getLogger("%s.lte_config_earfcn" % self.name)
        if not carrier in ['PCC','SCC']:
            logger.error("Invalid carrier %s. TEST ABORTED" % carrier)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            self._param_write("CONFigure:LTE:SIGN:RFSettings:%s:CHANnel:DL" % carrier, earfcn, '%s.earfcn' % carrier.lower())
            self.insert_pause(2)
    # *********************************
    # READINGS
    # *********************************
    """
    def lte_dut_measreport_enable(self):
        logger = logging.getLogger("%s.lte_dut_measreport_enable" % self.name)
        self._param_write("CONFigure:LTE:SIGN:UEReport:ENABle", "ON", 'ue_report')
        logger.info("UE measurements report enabled")


    def lte_dut_measreport_disable(self):
        logger = logging.getLogger("%s.lte_dut_measreport_disable" % self.name)
        self._param_write("CONFigure:LTE:SIGN:UEReport:ENABle", "OFF", 'ue_report')
        logger.info("UE measurements report disabled")


    def lte_dut_measreport_read(self):
        logger = logging.getLogger("%s.lte_dut_measreport_read" % self.name)
        rsrp_dBm, rsrq_dB = None, None

        rsrp       = self._param_read("SENSe:LTE:SIGN:UEReport:PCC:RSRP")
        rsrp_range = self._param_read("SENSe:LTE:SIGN:UEReport:PCC:RSRP:RANGe")
        rsrq       = self._param_read("SENSe:LTE:SIGN:UEReport:PCC:RSRQ")
        rsrq_range = self._param_read("SENSe:LTE:SIGN:UEReport:PCC:RSRQ:RANGe")

        logger.info("RSRP       : %s" % rsrp)
        logger.info("RSRP range : %s" % rsrp_range)
        logger.info("RSRQ       : %s" % rsrq)
        logger.info("RSRQ range : %s" % rsrq_range)
        try:
            rsrp_dBm=0.5*(float(rsrp_range.split(',')[0])+float(rsrp_range.split(',')[1]))
            rsrq_dB=0.5*(float(rsrq_range.split(',')[0])+float(rsrq_range.split(',')[1]))
        except:
            logger.warning("UE measurements not available")
        return [rsrp_dBm, rsrq_dB]


    def lte_read_params_pddch(self):
        logger = logging.getLogger('lte_read_params_pddch')
        pdcch_size      = self.read("SENSe:LTE:SIGN:CONNection:PDCCh:PSYMbols?")
        pdcch_aggrlevel = self.read("SENSe:LTE:SIGN:CONNection:PDCCh:PSYMbols?")
        logger.info("--------------------------------------")
        logger.info("PDCCH size [symbols] : %s" % pdcch_size)
        logger.info("PDCCH Aggr Level     : %s" % pdcch_aggrlevel)
        logger.info("--------------------------------------")

    def lte_read_cell_pwrlvl(self):
        logger=logging.getLogger('lte_read_cell_pwrlvl')
        logger.info("-----------------------------------------")
        logger.info("             Power Levels                ")
        logger.info("-----------------------------------------")
        rd_fsim_state     = self.read("CONFigure:LTE:SIGN:FADing:FSIMulator:ENABle?")
        rd_chstatic_state = self.read("CONFigure:LTE:SIGN:CONNection:SCHModel:ENABle?")
        rd_extawgn_state  = self.lte_external_awgn_getstate()
        logger.info("--------------------------------------")
        logger.info(" Internal Fading simulator : %s" % rd_fsim_state)
        logger.info(" Static channel            : %s" % rd_chstatic_state)
        logger.info(" External AWGN simulator   : %s" % rd_extawgn_state)
        logger.info("--------------------------------------")
        if rd_fsim_state == 'ON':
            self.lte_read_fsim_int_pwrlvl()
        if rd_chstatic_state=='ON' or rd_extawgn_state=='ON':
            self.lte_read_awgn_ext_pwrlvl()
        if rd_chstatic_state=='ON':
            self.lte_read_params_channel_static()

    def lte_read_params_channel_static(self):
        logger = logging.getLogger('lte_read_params_channel_static')
        ch_model  = self.read("CONFigure:LTE:SIGN:CONNection:SCHModel?")
        ch_matrix = self.read("CONFigure:LTE:SIGN:CONNection:PMATrix?")
        logger.info("--------------------------------------")
        logger.info("Static channel model : %s"  % ch_model)
        logger.info("Static channel matrix : %s" % ch_matrix)
        logger.info("--------------------------------------")

    def lte_read_fsim_int_pwrlvl(self):
        logger = logging.getLogger('lte_fading_pwrlvl_read')
        pwr_level=Struct()
        pwr_level.noise_sysbw    = self.read("CONFigure:LTE:SIGN:FADing:POWer:NOISe?")
        pwr_level.noise_totbw    = self.read("CONFigure:LTE:SIGN:FADing:POWer:NOISe:TOTal?")
        pwr_level.s_plus_n_totbw = self.read("CONFigure:LTE:SIGN:FADing:POWer:SUM?")

        logger.info("--------------------------------------")
        logger.info("Power Noise in System BW : %.02f [dBm]" % float(pwr_level.noise_sysbw))
        logger.info("Power Noise in  Total BW : %.02f [dBm]" % float(pwr_level.noise_totbw))
        logger.info("      (S+N) in System BW : %.02f [dBm]" % float(pwr_level.s_plus_n_totbw))
        logger.info("--------------------------------------")
        return pwr_level

    def lte_read_awgn_ext_pwrlvl(self):
        logger = logging.getLogger('lte_read_awgn_ext_pwrlvl')
        try:
            pwr_level  = self.read("CONFigure:LTE:SIGN:DL:AWGN?")
            logger.info("--------------------------------------")
            logger.info("EXT AWGN Power Level : %.02f [dBm]" % float(pwr_level))
            logger.info("--------------------------------------")
        except:
            logger.warning("EXT AWGN power level not available")
            pwr_level  = None
        return pwr_level

    def lte_read_params_cqi(self):
        logger    = logging.getLogger('lte_read_params_cqi')
        cqi_state = self.read("CONFigure:LTE:SIGN:CQIReporting:ENABle?")
        cqi_index = self.read("CONFigure:LTE:SIGN:CQIReporting:CINDex:FDD?")
        logger.info("--------------------------------------")
        logger.info("CQI report : %s" % cqi_state)
        logger.info("CQI index  : %s" % cqi_index)
        logger.info("--------------------------------------")
    """


    # *********************************
    # MEASUREMENTS
    # *********************************
    def lte_get_measurement_period(self, init_s):
        self.lte_set_measurement_period(init_s)
        return self.meas.period_nsf


    def lte_set_measurement_period(self, init_s):
        logger = logging.getLogger('%s.lte_set_measurement_period' % self.name)

        DEFAULT_MEAS_PERIOD_NSF = 10000

        self.meas.period_nsf = DEFAULT_MEAS_PERIOD_NSF
        pcc_meas_period      = DEFAULT_MEAS_PERIOD_NSF
        scc_meas_period      = DEFAULT_MEAS_PERIOD_NSF

        if init_s.scc is None:
            if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                self.meas.period_nsf = self.Anritsu_LTE_MEAS_PERIOD_NSF[init_s.pcc.chtype]
        else:
            if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                pcc_meas_period = self.Anritsu_LTE_MEAS_PERIOD_NSF[init_s.pcc.chtype]

            if (not init_s.scc.chtype is None) and (init_s.scc.chtype in self.Anritsu_LTE_FADING_CHANNELS):
                scc_meas_period = self.Anritsu_LTE_MEAS_PERIOD_NSF[init_s.scc.chtype]

                self.meas.period_nsf = max(pcc_meas_period, scc_meas_period)

        self.meas.period_sec = self.meas.period_nsf*0.001
        self.meas.timeout    = 3*self.meas.period_sec
        self.meas.check      = self.meas.period_sec + 2
        logger.debug("-------------------------------------")
        logger.debug("Measurement period set to %s [sec]   " % self.meas.period_sec)
        logger.debug(" - timeout %s [sec]                  " % self.meas.timeout)
        logger.debug(" - check %s   [sec]                  " % self.meas.check)
        logger.debug("-------------------------------------")


    def lte_meas_bler_fetch(self, init_s):

        logger = logging.getLogger('%s.lte_meas_bler_fetch' % self.name)

        # Init mease structures
        self._meas_init()

        # Update measurement period
        self.lte_set_measurement_period(init_s)

        # Configure BLER measurements
        self._param_write("CONFigure:LTE:SIGN:EBLer:REPetition", "SING", 'single shot')
        self._param_write("CONFigure:LTE:SIGN:EBLer:SCONdition", "NONE", 'stop condition')
        self._param_write("CONFigure:LTE:SIGN:EBLer:SFRames", self.meas.period_nsf, 'meas_period')


        # Wait for measurements RDY
        num_iter, NUM_ITER_MAX = 0, int(math.ceil(self.meas.timeout/self.meas.check))
        while ( num_iter < NUM_ITER_MAX ):                                                                                                                                    # Initialise and start BLER measurements
            num_iter += 1
            self.write("STOP:LTE:SIGN:EBLer")
            #self.write("ABORt:LTE:SIGN:EBLer")
            self.write("INIT:LTE:SIGN:EBLer")
            self.insert_pause(self.meas.check)
            logger.debug("FETCHING DLBLER MEAS: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            state=self.read("FETCh:LTE:SIGN:EBLer:STATe?")
            logger.debug("FETCH STATE : %s" % state)
            if (state == 'RDY') : break

        if num_iter==NUM_ITER_MAX:
            logger.error("CWM not responding to query on measurements")
            self.write("ABORt:LTE:SIGN:EBLer")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_TIMEOUT)

        # Fetch measurements
        pcc_meas_dlbler_l = None
        scc_meas_dlbler_l = None
        pcc_meas_ulbler_l = None

        if (state == 'RDY'):
            pcc_meas_dlbler_str = self.read("FETCh:LTE:SIGN:EBLer:PCC:ABSolute?")
            pcc_meas_dlbler_l   = pcc_meas_dlbler_str.split(',')
            logger.debug("pcc_meas_dlbler_l : %s" % pcc_meas_dlbler_l)

            pcc_meas_ulbler_str = self.read("FETCh:LTE:SIGN:EBLer:Uplink?")
            pcc_meas_ulbler_l   = pcc_meas_ulbler_str.split(',')
            logger.debug("pcc_meas_ulbler_l : %s" % pcc_meas_dlbler_l)

            if not init_s.scc is None:
                # Fetch measurements
                scc_meas_dlbler_str = self.read("FETCh:LTE:SIGN:EBLer:SCC:ABSolute?")
                scc_meas_dlbler_l   = scc_meas_dlbler_str.split(',')
                logger.debug("scc_meas_dlbler_l : %s" % scc_meas_dlbler_l)
        else:
            logger.error("CWM not responding to query on measurements")
            self.write("ABORt:LTE:SIGN:EBLer")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_TIMEOUT)

        # Build measurements structure, format the values and check the validity
        try:
            # DL measurements
            self.meas_dlbler_s.pcc.dlrely       = int(pcc_meas_dlbler_l[0])
            self.meas_dlbler_s.pcc.ack          = int(pcc_meas_dlbler_l[1])
            self.meas_dlbler_s.pcc.nack         = int(pcc_meas_dlbler_l[2])
            self.meas_dlbler_s.pcc.sf_total     = int(pcc_meas_dlbler_l[3])
            self.meas_dlbler_s.pcc.dlthr        = float(pcc_meas_dlbler_l[4])
            self.meas_dlbler_s.pcc.dlthr_min    = float(pcc_meas_dlbler_l[5])
            self.meas_dlbler_s.pcc.dlthr_max    = float(pcc_meas_dlbler_l[6])
            self.meas_dlbler_s.pcc.dtx          = int(pcc_meas_dlbler_l[7])
            self.meas_dlbler_s.pcc.sf_scheduled = int(pcc_meas_dlbler_l[8])
            self.meas_dlbler_s.pcc.cqi          = int(pcc_meas_dlbler_l[9]) if (pcc_meas_dlbler_l[9] !='INV') else 0

            ## UL measurements
            self.meas_ulbler_s.pcc.ulrely       = int(pcc_meas_ulbler_l[0])
            self.meas_ulbler_s.pcc.ulbler       = float(pcc_meas_ulbler_l[1])
            self.meas_ulbler_s.pcc.ulthr        = 0 if (pcc_meas_ulbler_l[2] == 'NCAP') else float(pcc_meas_ulbler_l[2])
            self.meas_ulbler_s.pcc.crc_pass     = int(pcc_meas_ulbler_l[3])
            self.meas_ulbler_s.pcc.crc_fail     = int(pcc_meas_ulbler_l[4])

            if not init_s.scc is None:
                # DL measurements
                self.meas_dlbler_s.scc.dlrely       = int(scc_meas_dlbler_l[0])
                self.meas_dlbler_s.scc.ack          = int(scc_meas_dlbler_l[1])
                self.meas_dlbler_s.scc.nack         = int(scc_meas_dlbler_l[2])
                self.meas_dlbler_s.scc.sf_total     = int(scc_meas_dlbler_l[3])
                self.meas_dlbler_s.scc.dlthr        = float(scc_meas_dlbler_l[4])
                self.meas_dlbler_s.scc.dlthr_min    = float(scc_meas_dlbler_l[5])
                self.meas_dlbler_s.scc.dlthr_max    = float(scc_meas_dlbler_l[6])
                self.meas_dlbler_s.scc.dtx          = int(scc_meas_dlbler_l[7])
                self.meas_dlbler_s.scc.sf_scheduled = int(scc_meas_dlbler_l[8])
                self.meas_dlbler_s.scc.cqi          = int(scc_meas_dlbler_l[9]) if (scc_meas_dlbler_l[9] !='INV') else 0
        except ValueError:
                logger.error("Anritsu INVALID MEASUREMENT")
                sys.exit(CfgError.ERRCODE_SYS_Anritsu_INVMEAS)
        else:
            if self.meas_dlbler_s.pcc.dlrely:
                logger.error("Anritsu UNRELIABLE MEASUREMENT, PCC dlrely = %s" % self.meas_dlbler_s.pcc.dlrely)
                sys.exit(CfgError.ERRCODE_SYS_Anritsu_INVMEAS)
            if (not init_s.scc is None) and self.meas_dlbler_s.scc.dlrely:
                logger.error("Anritsu UNRELIABLE MEASUREMENT, SCC dlrely = %s" % self.meas_dlbler_s.scc.dlrely)
                sys.exit(CfgError.ERRCODE_SYS_Anritsu_INVMEAS)

        if 1:
            self.meas_dlbler_s.pcc.struct_log()
            self.meas_dlbler_s.scc.struct_log()
            self.meas_ulbler_s.pcc.struct_log()

        self.lte_meas_dlthr(init_s)
        self.lte_meas_csi(init_s)
        self.lte_meas_harq(init_s)


    def _lte_compute_average_dlthr_per_cw(self, meas):
        #logger = logging.getLogger('%s._lte_compute_average_dlthr_per_cw' % self.name)
        meas_l = meas.split(' ')[1:]
        dlthr_l = [float(x) for x in meas_l[1::2]]
        N = len(dlthr_l)
        if N> 0:
            dlthr_avrg_Mbps = sum(dlthr_l)/N*0.001
        else:
            dlthr_avrg_Mbps = None
        return dlthr_avrg_Mbps

    def lte_meas_dlthr(self, init_s):
        logger = logging.getLogger('%s.lte_meas_dlthr' % self.name)

        #dlthr_cw1_Mbps = self.read("SENSe:LTE:SIGN:CONNection:ETHRoughput:DL:PCC:STReam1?").replace(',', ' ')
        dlthr_cw1_Mbps = self.read("FETCh:LTE:SIGN:EBLer:TRACe:THRoughput:PCC:STReam1?").replace(',', ' ')
        if 0: logger.debug("PCC RAW MEAS DLTHR CW1 : %s" % dlthr_cw1_Mbps)
        try:
            self.meas_dlthr_s.pcc.dlthr_cw1 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw1_Mbps))
        except ValueError:
            self.meas_dlthr_s.pcc.dlthr_cw1 = None
        logger.debug("PCC DLTHR CW1 : %s[Mbps]" % self.meas_dlthr_s.pcc.dlthr_cw1)

        if init_s.pcc.tm in [3, 4]:
            dlthr_cw2_Mbps = self.read("FETCh:LTE:SIGN:EBLer:TRACe:THRoughput:PCC:STReam2?").replace(',', ' ')
            if 0: logger.debug("PCC RAW MEAS DLTHR CW2 : %s" % dlthr_cw2_Mbps)
            try:
                self.meas_dlthr_s.pcc.dlthr_cw2 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw2_Mbps))
            except ValueError:
                self.meas_dlthr_s.pcc.dlthr_cw2 = None
            logger.debug("PCC DLTHR CW2 : %s[Mbps]" % self.meas_dlthr_s.pcc.dlthr_cw2)

        if not init_s.scc is None:
            dlthr_cw1_Mbps = self.read("FETCh:LTE:SIGN:EBLer:TRACe:THRoughput:SCC:STReam1?").replace(',', ' ')
            if 0: logger.debug("SCC RAW MEAS DLTHR CW1 : %s" % dlthr_cw1_Mbps)
            try:
                self.meas_dlthr_s.scc.dlthr_cw1 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw1_Mbps))
            except ValueError:
                self.meas_dlthr_s.scc.dlthr_cw1 = None
            logger.debug("SCC DLTHR CW1 : %s[Mbps]" % self.meas_dlthr_s.scc.dlthr_cw1)
            if init_s.scc.tm in [3, 4]:
                dlthr_cw2_Mbps = self.read("FETCh:LTE:SIGN:EBLer:TRACe:THRoughput:SCC:STReam2?").replace(',', ' ')
                if 0: logger.debug("SCC RAW MEAS DLTHR CW2 : %s" % dlthr_cw2_Mbps)
                try:
                    self.meas_dlthr_s.scc.dlthr_cw2 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw2_Mbps))
                except ValueError:
                    self.meas_dlthr_s.scc.dlthr_cw2 = None
                logger.debug("SCC DLTHR CW2 : %s[Mbps]" % self.meas_dlthr_s.scc.dlthr_cw2)

    def lte_meas_harq(self, init_s):
        logger = logging.getLogger('%s.lte_meas_harq' % self.name)
        if (init_s.pcc.nhrtx >= 2) and (init_s.pcc.nhrtx <= 4):
            self.meas_harq_s.pcc.harq_cw1 = self.read("FETCh:LTE:SIGN:EBLer:PCC:HARQ:STReam1:TRANsmission:ABSolute?").replace(',', ' ')
            logger.debug("PCC HARQ CW1 : %s" % self.meas_harq_s.pcc.harq_cw1)
            if init_s.pcc.tm in [3, 4]:
                self.meas_harq_s.pcc.harq_cw2 = self.read("FETCh:LTE:SIGN:EBLer:PCC:HARQ:STReam2:TRANsmission:ABSolute?").replace(',', ' ')
                logger.debug("PCC HARQ CW2 : %s" % self.meas_harq_s.pcc.harq_cw2)
        if not init_s.scc is None:
            if (init_s.scc.nhrtx >= 2) and (init_s.scc.nhrtx <= 4):
                self.meas_harq_s.scc.harq_cw1 = self.read("FETCh:LTE:SIGN:EBLer:SCC:HARQ:STReam1:TRANsmission:ABSolute?").replace(',', ' ')
                logger.debug("SCC HARQ CW1 : %s" % self.meas_harq_s.scc.harq_cw1)
                if init_s.scc.tm in [3, 4]:
                    self.meas_harq_s.scc.harq_cw2 = self.read("FETCh:LTE:SIGN:EBLer:SCC:HARQ:STReam2:TRANsmission:ABSolute?").replace(',', ' ')
                    logger.debug("SCC HARQ CW2 : %s" % self.meas_harq_s.scc.harq_cw2)


    def lte_meas_csi(self, init_s):
        logger = logging.getLogger('%s.lte_meas_csi' % self.name)

        if not init_s.pcc.tm in [1]:
            self.meas_rank_s.pcc.rank=self.read("FETCh:LTE:SIGN:EBLer:PCC:RI?").replace(',', ' ')
            logger.debug("PCC RI : %s" % self.meas_rank_s.pcc.rank)

        self.meas_cqi_s.pcc.cqi_cw1=self.read("FETCh:LTE:SIGN:EBLer:TRACe:CQIReporting:PCC:STReam1?").replace(',', ' ')
        logger.debug("PCC CQI CW1: %s" % self.meas_cqi_s.pcc.cqi_cw1)
        if init_s.pcc.tm in [4]:
            self.meas_cqi_s.pcc.cqi_cw2=self.read("FETCh:LTE:SIGN:EBLer:TRACe:CQIReporting:PCC:STReam2?").replace(',', ' ')
            logger.debug("PCC CQI CW2: %s" % self.meas_cqi_s.pcc.cqi_cw2)
        if init_s.pcc.tm in [4]:
            self.meas_pmi_s.pcc.pmi_ri1=self.read("FETCh:LTE:SIGN:EBLer:PCC:PMI:RI1?").replace(',', ' ')
            logger.debug("PCC PMI RI1: %s" % self.meas_pmi_s.pcc.pmi_ri1)
            self.meas_pmi_s.pcc.pmi_ri2=self.read("FETCh:LTE:SIGN:EBLer:PCC:PMI:RI2?").replace(',', ' ')
            logger.debug("PCC PMI RI2: %s" % self.meas_pmi_s.pcc.pmi_ri2)

        if not init_s.scc is None:
            if not init_s.scc.tm in [1]:
                self.meas_rank_s.scc.rank=self.read("FETCh:LTE:SIGN:EBLer:SCC:RI?").replace(',', ' ')
                logger.debug("SCC RI : %s" % self.meas_rank_s.scc.rank)

            self.meas_cqi_s.scc.cqi_cw1=self.read("FETCh:LTE:SIGN:EBLer:TRACe:CQIReporting:SCC:STReam1?").replace(',', ' ')
            logger.debug("SCC CQI CW1: %s" % self.meas_cqi_s.scc.cqi_cw1)
            if init_s.scc.tm in [4]:
                self.meas_cqi_s.scc.cqi_cw2=self.read("FETCh:LTE:SIGN:EBLer:TRACe:CQIReporting:SCC:STReam2?").replace(',', ' ')
                logger.debug("SCC CQI CW2: %s" % self.meas_cqi_s.scc.cqi_cw2)
            if init_s.scc.tm in [4]:
                self.meas_pmi_s.scc.pmi_ri1=self.read("FETCh:LTE:SIGN:EBLer:SCC:PMI:RI1?").replace(',', ' ')
                logger.debug("SCC PMI RI1: %s" % self.meas_pmi_s.scc.pmi_ri1)
                self.meas_pmi_s.scc.pmi_ri2=self.read("FETCh:LTE:SIGN:EBLer:SCC:PMI:RI2?").replace(',', ' ')
                logger.debug("SCC PMI RI2: %s" % self.meas_pmi_s.scc.pmi_ri2)




    def lte_meas_maxthr_read(self):
        logger = logging.getLogger('lte_meas_maxthr_read')
        max_dlthr='%s' % self.read("SENSe:LTE:SIGN:CONNection:ETHRoughput:DL:ALL?")
        max_ulthr='%s' % self.read("SENSe:LTE:SIGN:CONNection:ETHRoughput:UL?")
        max_dlthr='%.6f' % float(max_dlthr)
        max_ulthr='%.6f' % float(max_ulthr)
        logger.info("------------------------------------------------")
        logger.info("Expected MAX DLTHR[Mbps] = %s" % max_dlthr)
        logger.info("Expected MAX ULTHR[Mbps] = %s" % max_ulthr)
        logger.info("------------------------------------------------")
        return max_dlthr, max_ulthr



    # ***************************
    # PROCEDURES
    # ***************************
    def lte_cell_on(self):
        logger=logging.getLogger('AnritsuLteBler.lte_cell_on')
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5

        self.lte_cell_off()


        cell_state = self.read("CALLSTAT?")

        logger.debug("Initial Cell state %s" % cell_state)
        cell_on = (cell_state == "2")

        while ( (not cell_on) and (num_iter < NUM_ITER_MAX)):
            num_iter += 1
            logger.info("Turning cell ON: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            self.write("CALLPROC ON")# CALL PROCESSING FUNCTION ON

            cell_state=self.read("CALLSTAT?")

            cell_on=(cell_state == "2")
            if cell_on: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logging.error("Anritsu TIMEOUT turning the cell ON. TEST ABORTED")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_TIMEOUT)
        return cell_on


    def lte_cell_off(self):
        logger=logging.getLogger('AnritsuLteBler.lte_cell_off')
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5


        cell_state = self.read("SOURce:LTE:SIGNaling:CELL:STATe?")

        logger.debug("Initial Cell state %s" % cell_state)
        cell_off = (cell_state == "OFF")

        while ( (not cell_off) and (num_iter < NUM_ITER_MAX)):
            num_iter += 1
            logger.info("Turning cell OFF: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            self.write("SOURce:LTE:SIGN:CELL:STATe OFF")

            cell_state=self.read("SOURce:LTE:SIGNaling:CELL:STATe?")

            cell_off=(cell_state == "OFF")
            if cell_off: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logging.error("CWM TIMEOUT turning the cell OFF. TEST ABORTED")
            sys.exit(CfgError.ERRCODE_SYS_Anritsu_TIMEOUT)
        return cell_off


    def lte_dut_attach(self):
        logger = logging.getLogger('AnritsuLteBler.lte_dut_attach')

        attached=False
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5

        logger.info("DUT_ATTACH_PROCEDURE:")


        cell_state = self.read("SOURce:LTE:SIGNaling:CELL:STATe?")    # Get the current state


        if (cell_state == "OFF"):
            self.cell_on()

        while ( num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("ATTACH_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read('FETCh:LTE:SIGN:PSWitched:STATe?')

            attached=(dut_state == 'ATT')
            if attached: break
            time.sleep(POLL_INTERVAL)

        logger.info("DUT final state %s " % dut_state)

        return attached


    def lte_dut_connect(self):

        logger = logging.getLogger('AnritsuLteBler.lte_dut_connect')

        connected=False
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5


        curr_state = self.read("FETCh:LTE:SIGN:PSWitched:State?")

        logger.debug("DUT_Connect(): DUT initial state : %s " % curr_state)

        if (curr_state != "ATT"):
            logger.error("DUT must be attached before the connection")
            return connected

        self.write("CALL:LTE:SIGN:PSWitched:ACTion CONNect")

        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("CONNECT_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("FETCh:LTE:SIGN:PSWitched:State?")

            connected = (dut_state == 'CEST')
            if connected : break
            time.sleep(POLL_INTERVAL)

        logger.info("DUT final state : %s " % dut_state)
        return connected


    def lte_dut_disconnect(self):

        logger = logging.getLogger('AnritsuLteBler.lte_dut_disconnect')

        disconnected=True
        num_iter, NUM_ITER_MAX = 0, 10
        POLL_INTERVAL = 2

        # Get the current state
        curr_state = self.read("FETCh:LTE:SIGN:PSWitched:State?")
        logger.debug("DUT initial state : %s " % curr_state)
        if (curr_state != "CEST"):
            logger.error("DUT must be connected before the disconnection")
            return disconnected
        self.write("CALL:LTE:SIGN:PSWitched:ACTion DISConnect")
        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("DISCONNECT_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("FETCh:LTE:SIGN:PSWitched:State?")
            disconnected = (dut_state == 'ATT')
            if disconnected : break
            time.sleep(POLL_INTERVAL)

        logger.debug("DUT final state : %s " % dut_state)
        return disconnected


    def lte_dut_detach(self):

        logger = logging.getLogger('AnritsuLteBler.lte_dut_detach')

        detached=True
        num_iter, NUM_ITER_MAX = 0, 10
        POLL_INTERVAL = 2

        # Get the current state
        curr_state = self.read("FETCh:LTE:SIGN:PSWitched:State?")
        logger.debug("DUT_Detach(): DUT initial state : %s " % curr_state)
        if (curr_state != "CEST") and (curr_state != "ATT"):
            logger.error("DUT must be ATTACHED or CONNECTED before detaching")
            return detached
        self.write("CALL:LTE:SIGN:PSWitched:ACTion DETach")


        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("DETACH_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("FETCh:LTE:SIGN:PSWitched:State?")
            detached = (dut_state== 'ON')
            if detached: break
            time.sleep(POLL_INTERVAL)

        logger.debug("DUT_Detach(): DUT final state : %s " % dut_state)

        return detached


if __name__ == '__main__':
    pass
