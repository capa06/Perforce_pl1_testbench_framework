__author__ = 'chuyiq'
#! /usr/bin/env python

#######################################################################################################################
#
# Anritsu instrument driver class
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
    LTE_BWMHZ             = {1.4:'1.4MHZ', 3:'3MHZ', 5:'5MHZ', 10:'10MHZ', 15:'15MHZ', 20:'20MHZ'}  #Anritsu MT8820C specific
    LTE_NPRB0             = {1.4:6, 3:6, 5:6, 10:6, 15:12, 20:12}
    LTE_SNR0              = 30

    LTE_MOD               = {'QPSK':'QPSK', '16QAM':'16QAM', '64QAM':'64QAM' }
    LTE_TM                = {1:'SINGLE', 2:'TX_DIVERSITY', 3:'OPEN_LOOP', 4:'CLOSED_LOOP_MULTI'}

    #LTE_TX42_PMI_TABLE    = range(0,3)
    LTE_PA                = { 0:'0DB', -3: '-3DB',-6:'-6DB'}
    #LTE_TXANTS            = { 1:'ONE',   2:  'TWO', 4:'FOUR'}
    #LTE_PMI               = { 0: 'PMI0', 1: 'PMI1', 2: 'PMI2', 3: 'PMI3',
    #                              4: 'PMI4', 5: 'PMI5', 6: 'PMI6', 7: 'PMI7',
    #                              8: 'PMI8', 9: 'PMI9',10:'PMI10',11:'PMI11',
    #                             12:'PMI12',13:'PMI13',14:'PMI14',15:'PMI15'}

    LTE_RFBAND            = { 0: '0', 1: '1', 2:'2',  3: '3', 4: '4', 5:'5',  6: '6', 7: '7',
                                  8: '8', 9: '9',10:'10',11:'11',12:'12',13:'13',14:'14',15:'15',
                                 16:'16',17:'17',18:'18',19:'19',20:'20',21:'21',22:'22',23:'23',
                                 24:'24',25:'25',26:'26',27:'27',28:'28',29:'29',30:'30',31:'31',
                                 33:'33',34:'34',35:'35',36:'36',37:'37',38:'38',39:'39',40:'40',
                                 41:'41',44:'44'}

    #LTE_CFI_2_RPDCCH = {1:'ON', 2:'OFF', 3:'OFF'}
    LTE_CFI={1.4:'4',3:'2',5:'2',10:'1',15:'1',20:'1'}
    LTE_NPRB0 = {1.4:3, 3:6, 5:6, 10:6, 15:12, 20:12}
    LTE_CQI_REPORTING = {"RMC":"PER", "UDCH":"PER", "UDTT":"PER", "CQI,FWB":"PER", "CQI,FCPR":"PER", "CQI,FCRI":"PER" }

    #LTE_RAT = {'LTE_FDD':'FDD', 'LTE_FDD_CA':'FDD', 'LTE_TDD':'TDD', 'FDD':'FDD', 'TDD':'TDD'}








   


    def __init__(self, name, ip_addr, rat, xmlfile_config='structxml_Anritsu_lte_config.xml'):

        self.rat             = rat
        self.param_check     = 0


        Anritsu.__init__(self, name, ip_addr)

        self.xmlfile_config = xmlfile_config

        self.common_config   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.common_config" % self.name), node_name='common')
        self.pcc_config      = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.pcc_config" % self.name), node_name='pcc')
        self.scc_config      = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.scc_config" % self.name), node_name='scc')
        if len(self.scc_config.get_fieldname_list()) == 0:
            self.scc_config  = None
        self.log_config()

        self._meas_create()
        self._meas_init()



    def _meas_create(self):
        self.meas                = Struct()

        self.meas_dlbler_s       = Struct()
        self.meas_dlbler_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_dlbler_s.pcc" % self.name), node_name='dlbler')
        self.meas_dlbler_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_dlbler_s.scc" % self.name), node_name='dlbler')

        self.meas_ulbler_s       = Struct()
        self.meas_ulbler_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_ulbler_s.pcc" % self.name), node_name='ulbler')
        self.meas_ulbler_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_ulbler_s.scc" % self.name), node_name='ulbler')

        self.meas_dlthr_s       = Struct()
        self.meas_dlthr_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_dlthr_s.pcc" % self.name), node_name='dlthr')
        self.meas_dlthr_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_dlthr_s.scc" % self.name), node_name='dlthr')

        self.meas_rank_s       = Struct()
        self.meas_rank_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_rank_s.pcc" % self.name), node_name='rank')
        self.meas_rank_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_rank_s.scc" % self.name), node_name='rank')

        self.meas_cqi_s       = Struct()
        self.meas_cqi_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_cqi_s.pcc" % self.name), node_name='cqi')
        self.meas_cqi_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_cqi_s.scc" % self.name), node_name='cqi')

        self.meas_pmi_s       = Struct()
        self.meas_pmi_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_pmi_s.pcc" % self.name), node_name='pmi')
        self.meas_pmi_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_pmi_s.scc" % self.name), node_name='pmi')

        self.meas_harq_s       = Struct()
        self.meas_harq_s.pcc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_harq_s.pcc" % self.name), node_name='harq')
        self.meas_harq_s.scc   = StructXml(xmlfile=self.xmlfile_config, struct_name=("%s.meas_harq_s.scc" % self.name), node_name='harq')


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
        logger.info("CHECKPOINT for Anritsu configuration : %s" % ('FAIL' if self.param_check else 'PASS'))
        logger.info("*****************************************************************************************")
        if self.param_check:
            sys.exit(CfgError.ERRCODE_SYS_CMW_PARAM_CHECK)

    def log_config(self):
        logger=logging.getLogger("%s.log_config" % self.name)
        logger.info("*****************************************************************************************")
        logger.info(" Anritsu initial configuration for %s" % self.rat)
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
        #self.lte_config_cp(init_s)
        #self.lte_config_srs(init_s)
        self.lte_config_uplink_power_control(init_s)

        ## Configure Connection
        self.lte_config_connection(init_s)
        self.lte_config_cfi(init_s)
        self.lte_config_tm_pmi_txants(init_s)
        self.lte_config_scheduler(init_s)

        self.lte_config_harq(init_s)

        # Configure propagation scenario
        self.lte_config_channel(init_s)
        self.lte_config_scheduler_attach(init_s)
        if 0:
            self.lte_config_rsepre(init_s)
            self.lte_update_scheduler(init_s)

        #self._checkpoint_init(init_s)
        self.checkpoint()
        logger.info("CONFIGURED Anritsu for attach")


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

                # Configure scenario for CA SISO
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                    logger.error("Fading Channel not supported by Anritsu")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    self._param_write('DLSCC','1','1 scc configureed siso')
                # Configure attenuation CA SISO


            elif init_s.pcc.tm in [2,3,4]:

                # Configure CA MIMO2x2 scenario
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                    logger.error("Fading Channel not supported by Anritsu")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    self._param_write('DLSCC','1','1 scc configured for 2x2 mimo ')
                # Configure attenuation CA MIMO2x2
                #self._param_write("CONFigure:LTE:SIGN:RFSettings:SCC:EATTenuation:OUTPut1", self.scc_config.eatt_out1, 'scc_att_out1')
                #self._param_write("CONFigure:LTE:SIGN:RFSettings:SCC:EATTenuation:OUTPut2", self.scc_config.eatt_out2, 'scc_att_out2')

            else:
                logger.error("Transmission mode not supported yet : TM %s" % init_s.pcc.tm)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

            # Set SCC MODE
            self._parame_write('ACT_SCC1','ON','scc_mode activated')

        else:
            # ----------------------------
            # Single Carrier scenario
            # ----------------------------
            if init_s.pcc.tm == 1:

                # Configure scenario for SC SISO
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                    # SC SISO with fading simulator
                    logger.error('Fading Mode not supported.')
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    # SC SISO without fading simulator
                    self._param_write("ANTCONFIG",self.LTE_TM[init_s.pcc.tm], 'siso')
                # Configure attenuation SC SISO


            elif (init_s.pcc.tm in [2,3,4]) and (init_s.pcc.txants==2):

                # Configure scenario for SC MIMO2x2
                if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                    # SC MIMO2x2 with fading simulator
                    logger.error('Fading Mode not supported.')
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                else:
                    # SC MIMO2x2 without fading simulator
                    self._param_write("ANTCONFIG",self.LTE_TM[init_s.pcc.tm], 'mimo2x2')

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
        self._param_write("PSSPWR", self.pcc_config.pss_poffest, 'pcc_pss.pwroffs') #PSS POWER -30 TO 0 DB
        self._param_write("SSSPWR", self.pcc_config.sss_poffest,'pcc_sss.pwroffs') #SSS POWER
        self._param_write("PBCHPWR", self.pcc_config.pbch_poffest,'pcc_PBCH.pwroffs')
        self._param_write("PCFICHPWR", self.pcc_config.pcfich_poffest, 'pcc_pcfich.pwroffs')
        self._param_write("PHICHPWR", self.pcc_config.phich_poffest, 'pcc_phich.pwroffs')
        self._param_write("PDCCHPWR", self.pcc_config.pdcch_poffest, 'pcc_pdcch.pwroffs')
        self._param_write("OLVL_EPRE", init_s.pcc.rsepre, 'pcc.rsepre') #OLVL RSEPRE power
        #self._param_write('OCNG_CON', self.pcc_config.ocng,'pcc_ocng_idel')
        self._param_write("PDSCH_P_A", self.LTE_PA[init_s.pcc.pa], 'pcc.pa')
        self._param_write("PDSCH_P_B", init_s.pcc.pb,'pcc.pb')
        if not init_s.scc is None:
            self._param_write("OLVL_EPRE", init_s.scc.rsepre, 'scc.rsepre')
            self._param_write("OCNG_CON", self.scc_config.ocng, 'scc_ocng_con')
            self._param_write("PDSCH_P_A", self.LTE_PA[init_s.scc.pa], 'scc.pa')
            self._param_write("PDSCH_P_B", init_s.scc.pb,'scc.pb')
        logger.info("CONFIGURED downlink power levels")


    def lte_config_security(self, init_s):
        logger = logging.getLogger("%s.lte_config_security" % self.name)
        self._param_write('AUTHENT','ON','Authentication ON')
        self._param_write("AUTHENT_ALGO", "XOR", 'XOR')
        self._param_write("INTEGRITY", "SNOW3G", 'Snow3G')
        logger.info("CONFIGURED security mode")


    def lte_config_rf(self, init_s):
        logger = logging.getLogger("%s._config_rf" % self.name)
        self._param_write("BAND", self.LTE_RFBAND[init_s.pcc.rfband], 'pcc.rfband')
        self._param_write("DLCHAN", init_s.pcc.earfcn, 'pcc.earfcn')
        self._param_write("CELLID", self.pcc_config.cellid, 'pcc.cellID')
        self._param_write("BANDWIDTH", self.LTE_BWMHZ[init_s.pcc.bwmhz], 'pcc bwmhz')
        if not init_s.scc is None:
            logger.error("Configuration not supported yet : %s" % init_s.scc)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        logger.info("CONFIGURED RF")





    def lte_config_uplink_power_control(self, init_s):
        logger = logging.getLogger("%s._configure_uplink_power_control" % self.name)
        self._param_write('TPCPAT','AUTO','power contronl patern: AUTO')
        self._param_write('POWOFFSET','0.0','power control offset: 0.0')
        self._param_write('MAXULPWR',self.common_config.pmax,'Pmax')
        logger.info("CONFIGURED uplink power control")


    def lte_config_connection(self, init_s):
        logger = logging.getLogger("%s.lte_config_connection" % self.name)
        self._param_write('GROUPHOP',self.common_config.ghopping,'group hopping')
        self._param_write("UECAT", 'CAT'+str(self.common_config.uecat), 'uecat') #value=CAT1 to CAT7
        #self._param_write("UE_CAT? FLAG", self.common_config.uecat_reported, 'uecat report')
        self._param_write("PCYCLE", self.common_config.dpcycle, 'paging cycle')
        self._param_write("SIB2_NS", self.common_config.aseission, 'ASEmission')
        self._param_write("FILTERCOEF", self.common_config.fcoefficient, 'Filter Coefficient')#FC4 or FC8

        # Test or Data Application Mode
        self._param_write("RLCMODE", self.common_config.rlcmode, 'RLC mode')
        self._param_write("RRCRELEASE", self.common_config.krrc, 'Keep RRC') #ON or OFF, initial ON
        self._param_write("DNSSERVERIPRES", self.common_config.krrc, 'DNS response') #ON or OFF, initial OFF

        logger.info("CONFIGURED connection")


    def lte_config_cfi(self, init_s):
        logger = logging.getLogger("%s.lte_config_cfi" % self.name)
        self._param_write('CFI',self.LTE_CFI[init_s.pcc.bwmhz],'pcc cfi pattern')
        logger.info("PCC reduced PDCCH : %s" % self.LTE_CFI[init_s.pcc.bwmhz])
        if not init_s.scc is None:
            logger.info("SCC reduced PDCCH : %s" % self.LTE_CFI_2_RPDCCH[LTE_BW_MHZ_2_CFIMIN[init_s.scc.bwmhz]])

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
        self._param_write('ANTCONFIG', self.LTE_TM[init_s.pcc.tm], 'pcc_txscheme')
        if not init_s.pcc.pmi is None:
            self._param_write("MATRIX", self.LTE_PMI[init_s.pcc.pmi], 'pcc_pmi')

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
            if not init_s.scc.pmi is None:
                logger.error('Carrier Agregation not implemented yet')

        # Set TXANTS
        if not init_s.scc is None:
            logger.error('Carrier Agregation not implemented yet')

        logger.info("CONFIGURED TM/PMI/TXANTS")


    def lte_config_scheduler_attach(self, init_s):
        logger = logging.getLogger("%s.lte_config_scheduler_attach" % self.name)

        # Use RMC scheduler for ATTACH
        schedtype="RMC"
        self._param_write('CHCODING','RMC','pcc.chcoding:RMC')
        self._param_write('SCHEDULING','STATIC','pcc.schedtype')
        self._param_write('CQIINTERVAL','5','CQI reporting interval')#5 or 40ms, initial 5ms
        self._param_write('CQI_RANGE','5','CQI counting range')#0-15, initial 3
        if not init_s.scc is None:
            logger.error('Function not supported yet')
        '''
        if self.LTE_CQI_REPORTING[schedtype]=='PER':
            logger.error('Function not supported yet')
            if self.LTE_CQI_REPORTING[schedtype]=='PER':
                logger.error('Function not supported yet')
        '''


    def lte_config_scheduler(self, init_s):
        logger = logging.getLogger("%s.lte_config_scheduler" % self.name)
        self._param_write('ULIMCS',init_s.pcc.ulmcs,'ul mcs')
        self._param_write('ULRB_START',init_s.pcc.ulrbstart,'ULBR Start')
        self._param_write('DLIMCS1',init_s.pcc.dlmcs,'dl mcs')
        self._param_write('DLIMCS2',init_s.pcc.dlmcs,'dl mcs')
        self._param_write('DLIMCS3',init_s.pcc.dlmcs,'dl mcs')

        '''
        self.write('ULIMCS 5')
        #self.write('ULRMC_RB 50')
        self.write('ULRB_START 0')
        self.write('DLIMCS1 15')
        self.write('DLIMCS2 15')
        self.write('DLIMCS3 15')

        #from cfg_lte import GetDLModulation, GetULModulation, LTE_DL_IMCS_2_ITBS_QM, LTE_UL_IMCS_2_ITBS_QM
        print init_s.pcc.snr, init_s.param_sweep_iter.pcc.dlmcs,init_s.pcc.bwmhz,init_s.pcc.rsepre
        '''
        #self.LTE_MOD[GetDLModulation(init_s.pcc.dlmcs)], LTE_DL_IMCS_2_ITBS_QM[init_s.pcc.dlmcs][0]

        logger.info("CONFIGURED scheduling information")




    def lte_config_harq(self, init_s):
        logger = logging.getLogger("%s.lte_config_dlharq" % self.name)

        if (init_s.pcc.nhrtx is None):
            self._param_write('MAXHARQTX','1','HARQ off')
        else:
            if (not init_s.pcc.riv is None):
                self._param_write("MAXHARQTX", init_s.pcc.nhrtx, 'pcc.nhrtx')
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
            if init_s.pcc.chtype.upper()=='AWGN':
                self.lte_config_channel_awgn(init_s)
                self._param_write('AWGNLVL','ON','AWGN level on')
                logger.info("Configured AWGN generator")

            else:
                logger.error("PCC invalid propagation scenario %s" % init_s.pcc.chtype)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        logger.info("CONFIGURED propagation scenario")


    def lte_config_channel_none(self, init_s):
        #logger = logging.getLogger("%s.lte_config_channel_none" % self.name)
        self.lte_fsim_int_toggle(state='OFF', carrier='PCC')
        self.lte_external_awgn_toggle(state='OFF', carrier='PCC')
        #self.lte_static_channel_toggle(state='OFF', carrier='PCC')
        if not init_s.scc is None:
            self.lte_fsim_int_toggle(state='OFF', carrier='SCC')
            self.lte_external_awgn_toggle(state='OFF', carrier='SCC')
            self.lte_static_channel_toggle(state='OFF', carrier='SCC')




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
                coeff_m = self.LTE_STCH_COEFF[init_s.pcc.chtype][init_s.pcc.txants]
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
                    coeff_m = self.LTE_STCH_COEFF[init_s.scc.chtype][init_s.scc.txants]
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
        '''
        #cmd       = "CONFigure:LTE:SIGN:FADing:%s:FSIMulator:ENABle" % carrier
        completed = (self._param_read(cmd) == state)

        while (not completed) and (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("Turning %s internal fader: iteration %d of %d" % (state, num_iter, NUM_ITER_MAX))
            completed = (self._param_write(cmd, state, 'fsim') == 0)
            if completed: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logger.error("SCPI command failure")
            sys.exit(CfgError.ERRCODE_SYS_SCPI_FAILURE)
        logger.info("LTE internal fading simulator turned %s" % state)
        '''

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
        '''
        if (num_iter == NUM_ITER_MAX):
            logger.error("SCPI command failure")
            sys.exit(CfgError.ERRCODE_SYS_SCPI_FAILURE)
        '''
        logger.info("LTE external AWGN interferer turned %s" % state)




    def lte_config_snr(self, init_s, use_default_snr=0):
        logger = logging.getLogger("%s.lte_config_snr" % self.name)
        if not init_s.pcc.chtype is None:
            if not init_s.pcc.snr is None:
                logger.info("PCC SNR update for %-10s: %s)" % (init_s.pcc.chtype, (self.LTE_SNR0 if use_default_snr else init_s.pcc.snr)))
                pcc_awgn_level= (-self.LTE_SNR0) if use_default_snr else (-init_s.pcc.snr)
                if init_s.pcc.chtype in ['AWGN', 'STCHL', 'STCHM', 'STCHH']:
                    self._param_write("AWGNPWR", pcc_awgn_level, 'pcc_awgn_level')#AWGN power level -30dB-5dB

                if (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                    self._param_write("AWGNPWR", init_s.pcc.snr, 'pcc.fsim.snr')
            else:
                logger.error("PCC invalid SNR : None")
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        if not init_s.scc is None:
            if not  init_s.scc.chtype is None:
                if not init_s.scc.snr is None:
                    logger.info("SCC SNR update for %-10s: %s)" % (init_s.scc.chtype, (self.LTE_SNR0 if use_default_snr else init_s.scc.snr)))
                    scc_awgn_level= (init_s.scc.rsepre-self.LTE_SNR0) if use_default_snr else (init_s.scc.rsepre-init_s.scc.snr)
                    if init_s.scc.chtype in ['AWGN', 'STCHL', 'STCHM', 'STCHH']:
                        self._param_write("AWGNPWR", scc_awgn_level, 'scc_awgn_level')
                else:
                    logger.error("SCC invalid SNR : None")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)




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
            if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                self.meas.period_nsf = self.LTE_MEAS_PERIOD_NSF[init_s.pcc.chtype]
        else:
            if (not init_s.pcc.chtype is None) and (init_s.pcc.chtype in self.LTE_FADING_CHANNELS):
                pcc_meas_period = self.LTE_MEAS_PERIOD_NSF[init_s.pcc.chtype]

            if (not init_s.scc.chtype is None) and (init_s.scc.chtype in self.LTE_FADING_CHANNELS):
                scc_meas_period = self.LTE_MEAS_PERIOD_NSF[init_s.scc.chtype]

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
        self._param_write("TPUT_MEAS", "ON", 'Throughput Measurement ON')
        self._param_write("CQI_MEAS", "ON", 'CQI Measurement ON')
        self._param_write("TPUT_SAMPLE", self.meas.period_nsf, 'Number of Sample')
        #self.write('MOD_MEAS OFF')

        # Wait for measurements RDY
        num_iter, NUM_ITER_MAX = 0, int(math.ceil(self.meas.timeout/self.meas.check))
        while ( num_iter < NUM_ITER_MAX ):                                                                                                                                    # Initialise and start BLER measurements
            num_iter += 1
            self.write("S2")
            self.insert_pause(self.meas.check)
            logger.debug("FETCHING DLBLER MEAS: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            state=self.read("MSTAT?")
            logger.debug("FETCH STATE : %s" % state)
            if (state == '0') :
                break
            elif(state=='5'):
                call_state=self.read('CALLSTAT?')
                if(call_state=='1'):
                    self.lte_dut_attach()
                    self.lte_dut_connect()
                elif(call_state=='2'):
                    self.lte_dut_connect()

        if num_iter==NUM_ITER_MAX:
            logger.error("Anritsu not responding to query on measurements")
            self.write("MEASSTOP")
            sys.exit(CfgError.ERRCODE_SYS_TIMEOUT)

        # Fetch measurements
        pcc_meas_dlbler_l = None
        scc_meas_dlbler_l = None
        pcc_meas_ulbler_l = None

        if (state == '0'):
            pcc_meas_dlbler_str = self.read("TPUT? TTL")
            pcc_meas_dlbler_l   = pcc_meas_dlbler_str.split(',')
            logger.debug("pcc_meas_dlbler_l : %s" % pcc_meas_dlbler_l)

            pcc_meas_ulbler_str = self.read("TPUT? TTL")
            pcc_meas_ulbler_l   = pcc_meas_ulbler_str.split(',')
            logger.debug("pcc_meas_ulbler_l : %s" % pcc_meas_dlbler_l)

            if not init_s.scc is None:
                # Fetch measurements
                scc_meas_dlbler_str = self.read("TPUT_BLER? SCC1")
                scc_meas_dlbler_l   = scc_meas_dlbler_str.split(',')
                logger.debug("scc_meas_dlbler_l : %s" % scc_meas_dlbler_l)
        else:
            logger.error("Anritsu not responding to query on measurements")
            self.write("MEASSTOP")
            sys.exit(CfgError.ERRCODE_SYS_TIMEOUT)

        # Build measurements structure, format the values and check the validity
        try:
            # DL measurements
            self.meas_dlbler_s.pcc.dlrely       = float(self.read("TPUT? PER"))
            self.meas_dlbler_s.pcc.ack          = int(self.read("TPUT_BLERTRANSMIT? PCC"))-int(self.read("TPUT_BLERCNTNACK? PCC"))
            self.meas_dlbler_s.pcc.nack         = int(self.read("TPUT_BLERCNTNACK? PCC"))
            self.meas_dlbler_s.pcc.sf_total     = int(self.read("TPUT_SAMPLE?"))
            self.meas_dlbler_s.pcc.dlthr        = float(self.read("TPUT?"))
            self.meas_dlbler_s.pcc.dlthr_min    = float(self.read("TPUT?"))
            self.meas_dlbler_s.pcc.dlthr_max    = float(self.read("TPUT?"))
            self.meas_dlbler_s.pcc.dtx          = int(self.read("TPUT_BLERCNTDTX?"))
            self.meas_dlbler_s.pcc.sf_scheduled = int(self.read("TPUT_BLERTRANSMIT?"))
            self.meas_dlbler_s.pcc.cqi          = float(self.read("CQI?")) #if (pcc_meas_dlbler_l[9] !='INV') else 0

            ## UL measurements
            self.meas_ulbler_s.pcc.ulrely       = float(self.read("UL_TPUT? PER"))
            self.meas_ulbler_s.pcc.ulbler       = float(self.read("UL_TPUT_BLER?"))
            self.meas_ulbler_s.pcc.ulthr        = float(self.read("UL_TPUT?"))
            self.meas_ulbler_s.pcc.crc_pass     = int(self.read("UL_TPUT_BLERRECEIVE?"))-int(self.read("UL_TPUT_BLERCNT?"))
            self.meas_ulbler_s.pcc.crc_fail     = int(self.read("UL_TPUT_BLERCNT?"))

            if not init_s.scc is None:
                # DL measurements
                self.meas_dlbler_s.scc.dlrely       = int(self.read("TPUT? PER SCC1"))
                self.meas_dlbler_s.scc.ack          = int(self.read("TPUT_BLERTRANSMIT? SCC1"))-int(self.read("TPUT_BLERCNTNACK? SCC1"))
                self.meas_dlbler_s.scc.nack         = int(self.read("TPUT_BLERCNTNACK? SCC1"))
                self.meas_dlbler_s.scc.sf_total     = int(self.read("TPUT_SAMPLE?"))
                self.meas_dlbler_s.scc.dlthr        = float(self.read("TPUT? SCC1"))
                self.meas_dlbler_s.scc.dlthr_min    = float(self.read("TPUT? SCC1"))
                self.meas_dlbler_s.scc.dlthr_max    = float(self.read("TPUT? SCC1"))
                self.meas_dlbler_s.scc.dtx          = int(self.read("TPUT_BLERCNTDTX? SCC1"))
                self.meas_dlbler_s.scc.sf_scheduled = int(self.read("TPUT_BLERTRANSMIT? SCC1"))
                self.meas_dlbler_s.scc.cqi          = int(scc_meas_dlbler_l[9]) if (scc_meas_dlbler_l[9] !='INV') else 0
        except ValueError:
                logger.error("Anritsu INVALID MEASUREMENT")
                sys.exit(CfgError.ERRCODE_SYS_INVMEAS)
        '''
        else:
            if self.meas_dlbler_s.pcc.dlrely:
                logger.error("Anritsu UNRELIABLE MEASUREMENT, PCC dlrely = %s" % self.meas_dlbler_s.pcc.dlrely)
                sys.exit(CfgError.ERRCODE_SYS_INVMEAS)
            if (not init_s.scc is None) and self.meas_dlbler_s.scc.dlrely:
                logger.error("Anritsu UNRELIABLE MEASUREMENT, SCC dlrely = %s" % self.meas_dlbler_s.scc.dlrely)
                sys.exit(CfgError.ERRCODE_SYS_INVMEAS)
        '''
        if 1:
            self.meas_dlbler_s.pcc.struct_log()
            self.meas_dlbler_s.scc.struct_log()
            self.meas_ulbler_s.pcc.struct_log()

        self.lte_meas_dlthr(init_s)
        self.lte_meas_csi(init_s)
        #self.lte_meas_harq(init_s)


    def _lte_compute_average_dlthr_per_cw(self, meas):
        #logger = logging.getLogger('%s._lte_compute_average_dlthr_per_cw' % self.name)
        #dlthr_avrg_Mbps = float(self.read('TPUT?'))*0.001
        dlthr_avrg_Mbps=meas
        '''
        meas_l = meas.split(' ')[1:]
        dlthr_l = [float(x) for x in meas_l[1::2]]
        N = len(dlthr_l)
        if N> 0:
            dlthr_avrg_Mbps = float(self.read('TPUT?'))*0.001
        else:
            dlthr_avrg_Mbps = None
        '''
        return dlthr_avrg_Mbps

    def lte_meas_dlthr(self, init_s):
        logger = logging.getLogger('%s.lte_meas_dlthr' % self.name)

        #dlthr_cw1_Mbps = self.read("SENSe:LTE:SIGN:CONNection:ETHRoughput:DL:PCC:STReam1?").replace(',', ' ')
        dlthr_cw1_Mbps = float(self.read("TPUT_CW0?"))*0.001
        if 0: logger.debug("PCC RAW MEAS DLTHR CW1 : %s" % dlthr_cw1_Mbps)
        try:
            self.meas_dlthr_s.pcc.dlthr_cw1 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw1_Mbps))
        except ValueError:
            self.meas_dlthr_s.pcc.dlthr_cw1 = None
        logger.debug("PCC DLTHR CW1 : %s[Mbps]" % self.meas_dlthr_s.pcc.dlthr_cw1)

        if init_s.pcc.tm in [3, 4]:
            dlthr_cw2_Mbps = float(self.read("TPUT_CW1?"))*0.001
            if 0: logger.debug("PCC RAW MEAS DLTHR CW2 : %s" % dlthr_cw2_Mbps)
            try:
                self.meas_dlthr_s.pcc.dlthr_cw2 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw2_Mbps))
            except ValueError:
                self.meas_dlthr_s.pcc.dlthr_cw2 = None
            logger.debug("PCC DLTHR CW2 : %s[Mbps]" % self.meas_dlthr_s.pcc.dlthr_cw2)

        if not init_s.scc is None:
            dlthr_cw1_Mbps = float(self.read("TPUT_CW0? SCC1"))*0.001
            if 0: logger.debug("SCC RAW MEAS DLTHR CW1 : %s" % dlthr_cw1_Mbps)
            try:
                self.meas_dlthr_s.scc.dlthr_cw1 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw1_Mbps))
            except ValueError:
                self.meas_dlthr_s.scc.dlthr_cw1 = None
            logger.debug("SCC DLTHR CW1 : %s[Mbps]" % self.meas_dlthr_s.scc.dlthr_cw1)
            if init_s.scc.tm in [3, 4]:
                dlthr_cw2_Mbps = float(self.read("TPUT_CW1? SCC1"))*0.001
                if 0: logger.debug("SCC RAW MEAS DLTHR CW2 : %s" % dlthr_cw2_Mbps)
                try:
                    self.meas_dlthr_s.scc.dlthr_cw2 = float(self._lte_compute_average_dlthr_per_cw(dlthr_cw2_Mbps))
                except ValueError:
                    self.meas_dlthr_s.scc.dlthr_cw2 = None
                logger.debug("SCC DLTHR CW2 : %s[Mbps]" % self.meas_dlthr_s.scc.dlthr_cw2)




    def lte_meas_csi(self, init_s):
        logger = logging.getLogger('%s.lte_meas_csi' % self.name)

        if not init_s.pcc.tm in [1]:
            self.meas_rank_s.pcc.rank=self.read("RI? 1")
            logger.debug("PCC RI : %s" % self.meas_rank_s.pcc.rank)



    def lte_meas_maxthr_read(self):
        logger = logging.getLogger('lte_meas_maxthr_read')
        max_dlthr='%s' % float(self.read("TPUT?"))*0.001
        max_ulthr='%s' % float(self.read("UL_TPUT?"))*0.001
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
        cell_on = (cell_state == "1")

        while ( (not cell_on) and (num_iter < NUM_ITER_MAX)):
            num_iter += 1
            logger.info("Turning cell ON: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            self.write("CALLPROC ON")# CALL PROCESSING FUNCTION ON

            cell_state=self.read("CALLSTAT?")

            cell_on=(cell_state == "1")
            if cell_on: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logging.error("Anritsu TIMEOUT turning the cell ON. TEST ABORTED")
            sys.exit(CfgError.ERRCODE_SYS_TIMEOUT)
        return cell_on


    def lte_cell_off(self):
        logger=logging.getLogger('AnritsuLteBler.lte_cell_off')
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5


        cell_state = self.read("CALLSTAT?")

        logger.debug("Initial Cell state %s" % cell_state)
        cell_off = (cell_state < "2")

        while ( (not cell_off) and (num_iter < NUM_ITER_MAX)):
            num_iter += 1
            logger.info("Turning cell OFF: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            self.write("CALLPROC OFF")

            cell_state=self.read("CALLSTAT?")

            cell_off=(cell_state<'2')
            #print cell_state+'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
            if cell_off: break
            time.sleep(POLL_INTERVAL)

        if (num_iter == NUM_ITER_MAX):
            logging.error("Anritsu TIMEOUT turning the cell OFF. TEST ABORTED")
            sys.exit(CfgError.ERRCODE_SYS_TIMEOUT)
        return cell_off


    def lte_dut_attach(self):
        logger = logging.getLogger('AnritsuLteBler.lte_dut_attach')

        attached=False
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5

        logger.info("DUT_ATTACH_PROCEDURE:")


        cell_state = self.read("CALLSTAT?")    # Get the current state


        if (cell_state == "0"):
            self.cell_on()

        while ( num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("ATTACH_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read('CALLSTAT?')

            attached=(dut_state == '2')
            if attached: break
            time.sleep(POLL_INTERVAL)

        logger.info("DUT final state %s " % dut_state)

        return attached


    def lte_dut_connect(self):

        logger = logging.getLogger('AnritsuLteBler.lte_dut_connect')

        connected=False
        num_iter, NUM_ITER_MAX = 0, 20
        POLL_INTERVAL = 5


        curr_state = self.read("CALLSTAT?")

        logger.debug("DUT_Connect(): DUT initial state : %s " % curr_state)

        if (curr_state != "2"):
            logger.error("DUT must be attached before the connection")
            return connected

        self.write("CALLSA")

        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("CONNECT_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("CALLSTAT?")

            connected = (dut_state == '6')
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
        curr_state = self.read("CALLSTAT?")
        logger.debug("DUT initial state : %s " % curr_state)
        if (curr_state != "6"):
            logger.error("DUT must be connected before the disconnection")
            return disconnected
        self.write("CALLSO")
        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("DISCONNECT_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("CALLSTAT?")
            disconnected = (dut_state == '2')
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
        curr_state = self.read("CALLSTAT?")
        logger.debug("DUT_Detach(): DUT initial state : %s " % curr_state)
        if (curr_state != "6") and (curr_state != "2"):
            logger.error("DUT must be ATTACHED or CONNECTED before detaching")
            return detached
        self.write("CALLPROC OFF")


        while (num_iter < NUM_ITER_MAX):
            num_iter += 1
            logger.info("DETACH_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            dut_state=self.read("CALLSTAT?")
            detached = (dut_state== '0')
            if detached: break
            time.sleep(POLL_INTERVAL)

        logger.debug("DUT_Detach(): DUT final state : %s " % dut_state)

        return detached


if __name__ == '__main__':
    from lte.common.struct.StructXmlTestBlerLte import StructXmlTestBlerLte
    #anr=AnritsuLte('anr','10.21.141.234','FDD','structxml_Anritsu_lte_config.xml')
    #anr.lte_cell_on()
    #time.sleep(5)
    #anr.lte_cell_off()
    #anr.lte_cell_on()
    #anr.lte_dut_attach()
    #anr.lte_dut_connect()
    #anr.write('CALLSA')
    #anr.lte_dut_disconnect()
    #anr.lte_dut_detach()
    #anr.checkpoint()
    #testbler_s=StructXmlTestBlerLte('lte_testconfig.xml', 'structxml_Anritsu_lte_config.xml', struct_name='testbler_s')
    #anr.lte_config_init(testbler_s.testbler_s)
    pass
