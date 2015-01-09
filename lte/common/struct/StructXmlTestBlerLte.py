'''
Created on 24 May 2014

@author: fsaracino
'''


# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging

from xml.etree.ElementTree import parse


# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'error']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'tools']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'csv', 'struct']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError  import CfgError
from Struct    import Struct
from StructXml import StructXml
from StructXmlTestUnitLte import StructXmlTestUnitLte
from StructXmlTestStepLte import StructXmlTestStepLte
from StructXmlCsvReportBlerLte import StructXmlCsvReportBlerLte




# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class StructXmlTestBlerLte(object):
    
    FILEXML_TESTCONFIG_TEMPLATE        = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common','struct', 'template', 'structxml_testconfig_template.xml'])     
    FILEXML_TESTUNIT_LTE_TEMPLATE      = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct', 'template', 'structxml_testunit_lte_template.xml'])
    FILEXML_TESTSTEP_LTE_TEMPLATE      = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct', 'template', 'structxml_teststep_lte_template.xml'])
    FILEXML_CVSREPORTBLER_LTE_TEMPLATE = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct', 'template', 'structxml_csvreportbler_lte_template.xml'])

    def __init__(self, testconfig_s, testunit_s, struct_name=None):    
        logger=logging.getLogger('StructXmlTestBlerLte.__init__')
        
        self.STRUCTNAME  = struct_name
        #self.XMLFILE     = xmlfile
        self.FIELDNAME_L = []
        # Initialise structures from XML template
        self.testconfig_s = StructXml(xmlfile=self.FILEXML_TESTCONFIG_TEMPLATE, struct_name=("%s.testconfig_s" % self.STRUCTNAME), node_name='opts')
        self.testunit_s   = StructXmlTestUnitLte(xmlfile=self.FILEXML_TESTUNIT_LTE_TEMPLATE, struct_name="%s.testunit_s" % self.STRUCTNAME)
        self.teststep_s   = StructXmlTestStepLte(xmlfile=self.FILEXML_TESTSTEP_LTE_TEMPLATE, struct_name="%s.teststep_s" % self.STRUCTNAME)
        self.csvreport_s  = StructXmlCsvReportBlerLte(xmlfile=self.FILEXML_CVSREPORTBLER_LTE_TEMPLATE, struct_name="%s.csvreport_s" % self.STRUCTNAME)
        
        # Remove scc substructure if not present
        if testunit_s.scc is None:
            self.testunit_s.scc = None
            self.teststep_s.scc = None
            
        # Merge input structures
        self.testconfig_s.struct_merge(testconfig_s)
        self.testunit_s.struct_merge(testunit_s)

        # Copy common values form testunit_s to teststep_s
        self.teststep_s.common.struct_merge(self.testunit_s.common)

        # Iterators
        self.param_subtest_iter     = Struct()
        self.param_subtest_iter.pcc = Struct()
        self.param_subtest_iter.scc = Struct()
    
        self.param_config_iter      = Struct()
        self.param_config_iter.pcc  = Struct()
        self.param_config_iter.scc  = Struct()

        self.param_sweep_iter       = Struct()
        self.param_sweep_iter.pcc   = Struct()
        self.param_sweep_iter.scc   = Struct()
        
        self.totalsteps             = 0
        self.compute_total_steps()                   
        
        # TODO:
        # create testunit iterator function initialising teststep structure

    # ************************************************************************************
    # Iterators
    # ************************************************************************************
    def param_subtest_iterator(self):
        #logger=logging.getLogger('StructTestBler.param_subtest_iterator')
        
        if not self.testunit_s.scc is None:
            # ---------------------------------------------            
            # Carrier Aggregation
            # ---------------------------------------------
            self.param_subtest_iter.pcc.dmode=self.testunit_s.pcc.dmode
            self.param_subtest_iter.scc.dmode=self.testunit_s.scc.dmode
            
            self.param_subtest_iter.pcc.cp=self.testunit_s.pcc.cp
            self.param_subtest_iter.scc.cp=self.testunit_s.scc.cp

            self.param_subtest_iter.pcc.nhrtx=self.testunit_s.pcc.harq['NHRTX']
            self.param_subtest_iter.pcc.riv  =self.testunit_s.pcc.harq['RIV']
            
            # SCC use same HARQ settings of PCC 
            #self.param_subtest_iter.scc.nhrtx=self.testunit_s.scc.harq['NHRTX']
            #self.param_subtest_iter.scc.riv  =self.testunit_s.scc.harq['RIV']
            self.param_subtest_iter.scc.nhrtx=self.param_subtest_iter.pcc.nhrtx
            self.param_subtest_iter.scc.riv  =self.param_subtest_iter.pcc.riv
            
            for pcc_chtype_idx in range(len(self.testunit_s.pcc.chtype)):
                #for scc_chtype_idx in range(len(self.testunit_s.scc.chtype)):
    
                self.param_subtest_iter.pcc.chtype=None if self.testunit_s.pcc.chtype[pcc_chtype_idx] is None else self.testunit_s.pcc.chtype[pcc_chtype_idx].upper()
                #self.param_subtest_iter.scc.chtype=None if self.testunit_s.scc.chtype[scc_chtype_idx] is None else self.testunit_s.scc.chtype[scc_chtype_idx].upper()
                self.param_subtest_iter.scc.chtype=self.param_subtest_iter.pcc.chtype
                
                for pcc_bwmhz_idx in range(len(self.testunit_s.pcc.bwmhz)):
                    for scc_bwmhz_idx in range(len(self.testunit_s.scc.bwmhz)):
                        self.param_subtest_iter.pcc.bwmhz=self.testunit_s.pcc.bwmhz[pcc_bwmhz_idx]
                        self.param_subtest_iter.scc.bwmhz=self.testunit_s.scc.bwmhz[scc_bwmhz_idx]
           
                        for pcc_rfband_idx in range(len(self.testunit_s.pcc.rfband)):
                            for scc_rfband_idx in range(len(self.testunit_s.scc.rfband)):
                                self.param_subtest_iter.pcc.rfband=self.testunit_s.pcc.rfband[pcc_rfband_idx]
                                self.param_subtest_iter.scc.rfband=self.testunit_s.scc.rfband[scc_rfband_idx]

                                if self.testunit_s.pcc.dmode=='TDD':
                                    for pcc_dlulconf_idx in range(len(self.testunit_s.pcc.dlulconf)):
                                        for scc_dlulconf_idx in range(len(self.testunit_s.scc.dlulconf)):
                                            self.param_subtest_iter.pcc.dlulconf=self.testunit_s.pcc.dlulconf[pcc_dlulconf_idx]
                                            self.param_subtest_iter.scc.dlulconf=self.testunit_s.scc.dlulconf[scc_dlulconf_idx]

                                            for pcc_ssconf_idx in range(len(self.testunit_s.pcc.ssconf)):
                                                for scc_ssconf_idx in range(len(self.testunit_s.scc.ssconf)):
                                                    self.param_subtest_iter.pcc.ssconf=self.testunit_s.pcc.ssconf[pcc_ssconf_idx]
                                                    self.param_subtest_iter.scc.ssconf=self.testunit_s.scc.ssconf[scc_ssconf_idx]
                                else:
                                    self.param_subtest_iter.pcc.dlulconf= None
                                    self.param_subtest_iter.pcc.ssconf  = None
                                    self.param_subtest_iter.scc.dlulconf= None
                                    self.param_subtest_iter.scc.ssconf  = None
                                
                                yield self.param_subtest_iter
        else:
            # ---------------------------------------------
            # Single  Carrier
            # ---------------------------------------------
            self.param_subtest_iter.pcc.dmode=self.testunit_s.pcc.dmode
            self.param_subtest_iter.pcc.cp=self.testunit_s.pcc.cp
            self.param_subtest_iter.pcc.nhrtx=self.testunit_s.pcc.harq['NHRTX']
            self.param_subtest_iter.pcc.riv=self.testunit_s.pcc.harq['RIV']
            
            for pcc_chtype_idx in range(len(self.testunit_s.pcc.chtype)):
                self.param_subtest_iter.pcc.chtype=None if self.testunit_s.pcc.chtype[pcc_chtype_idx] is None else self.testunit_s.pcc.chtype[pcc_chtype_idx].upper()  
                    
                for pcc_bwmhz_idx in range(len(self.testunit_s.pcc.bwmhz)):
                    self.param_subtest_iter.pcc.bwmhz=self.testunit_s.pcc.bwmhz[pcc_bwmhz_idx]
               
                    for pcc_rfband_idx in range(len(self.testunit_s.pcc.rfband)):
                        self.param_subtest_iter.pcc.rfband=self.testunit_s.pcc.rfband[pcc_rfband_idx]
    
                        if self.testunit_s.pcc.dmode=='TDD':
                            for pcc_dlulconf_idx in range(len(self.testunit_s.pcc.dlulconf)):
                                self.param_subtest_iter.pcc.dlulconf=self.testunit_s.pcc.dlulconf[pcc_dlulconf_idx]
    
                                for pcc_ssconf_idx in range(len(self.testunit_s.pcc.ssconf)):
                                    self.param_subtest_iter.pcc.ssconf=self.testunit_s.pcc.ssconf[pcc_ssconf_idx]
                        else:
                            self.param_subtest_iter.pcc.dlulconf= None
                            self.param_subtest_iter.pcc.ssconf  = None
                        
                        yield self.param_subtest_iter
                                
                                

    def param_config_iterator(self):
        #logger=logging.getLogger('StructTestBler.param_config_iterator')

        if not self.testunit_s.scc is None:
            # ---------------------------------------------            
            # Carrier Aggregation
            # ---------------------------------------------        
            self.param_config_iter.pcc.schedtype=self.testunit_s.pcc.schedtype
            self.param_config_iter.scc.schedtype=self.testunit_s.scc.schedtype
                
            for pcc_pa_idx in range(len(self.testunit_s.pcc.pa)):
                for scc_pa_idx in range(len(self.testunit_s.scc.pa)):
                    self.param_config_iter.pcc.pa=self.testunit_s.pcc.pa[pcc_pa_idx]
                    self.param_config_iter.scc.pa=self.testunit_s.scc.pa[scc_pa_idx]

                    for pcc_pb_idx in range(len(self.testunit_s.pcc.pb)):
                        for scc_pb_idx in range(len(self.testunit_s.scc.pb)):
                            self.param_config_iter.pcc.pb=self.testunit_s.pcc.pb[pcc_pb_idx]
                            self.param_config_iter.scc.pb=self.testunit_s.scc.pb[scc_pb_idx]
            
                            for pcc_tm_idx in range(len(self.testunit_s.pcc.tm[self.param_subtest_iter.pcc.bwmhz])):
                                for scc_tm_idx in range(len(self.testunit_s.scc.tm[self.param_subtest_iter.scc.bwmhz])):
                                    self.param_config_iter.pcc.tm=self.testunit_s.pcc.tm[self.param_subtest_iter.pcc.bwmhz][pcc_tm_idx]
                                    self.param_config_iter.scc.tm=self.testunit_s.scc.tm[self.param_subtest_iter.scc.bwmhz][scc_tm_idx]
     
                                    for pcc_txants_idx in range(len(self.testunit_s.pcc.txants[self.param_config_iter.pcc.tm])):
                                        for scc_txants_idx in range(len(self.testunit_s.scc.txants[self.param_config_iter.scc.tm])):
                                            self.param_config_iter.pcc.txants=self.testunit_s.pcc.txants[self.param_config_iter.pcc.tm][pcc_txants_idx]
                                            self.param_config_iter.scc.txants=self.testunit_s.scc.txants[self.param_config_iter.scc.tm][scc_txants_idx]

                                            for pcc_pmi_idx in range(len(self.testunit_s.pcc.pmi[self.param_config_iter.pcc.tm][self.param_config_iter.pcc.txants])):
                                                for scc_pmi_idx in range(len(self.testunit_s.scc.pmi[self.param_config_iter.scc.tm][self.param_config_iter.scc.txants])):
                                                    self.param_config_iter.pcc.pmi=self.testunit_s.pcc.pmi[self.param_config_iter.pcc.tm][self.param_config_iter.pcc.txants][pcc_pmi_idx]
                                                    self.param_config_iter.scc.pmi=self.testunit_s.scc.pmi[self.param_config_iter.scc.tm][self.param_config_iter.scc.txants][scc_pmi_idx]
                                                                        
                                                    yield self.param_config_iter
                                                
        else:
            # ---------------------------------------------            
            # Single Aggregation
            # ---------------------------------------------        
            self.param_config_iter.pcc.schedtype=self.testunit_s.pcc.schedtype
            
            for pcc_pa_idx in range(len(self.testunit_s.pcc.pa)):
                self.param_config_iter.pcc.pa=self.testunit_s.pcc.pa[pcc_pa_idx]

                for pcc_pb_idx in range(len(self.testunit_s.pcc.pb)):
                    self.param_config_iter.pcc.pb=self.testunit_s.pcc.pb[pcc_pb_idx]
                
                    for pcc_tm_idx in range(len(self.testunit_s.pcc.tm[self.param_subtest_iter.pcc.bwmhz])):
                        self.param_config_iter.pcc.tm=self.testunit_s.pcc.tm[self.param_subtest_iter.pcc.bwmhz][pcc_tm_idx]
         
                        for pcc_txants_idx in range(len(self.testunit_s.pcc.txants[self.param_config_iter.pcc.tm])):
                            self.param_config_iter.pcc.txants=self.testunit_s.pcc.txants[self.param_config_iter.pcc.tm][pcc_txants_idx]

                            for pcc_pmi_idx in range(len(self.testunit_s.pcc.pmi[self.param_config_iter.pcc.tm][self.param_config_iter.pcc.txants])):
                                self.param_config_iter.pcc.pmi=self.testunit_s.pcc.pmi[self.param_config_iter.pcc.tm][self.param_config_iter.pcc.txants][pcc_pmi_idx]
                                                                            
                                yield self.param_config_iter

    
    def param_sweep_iterator(self):
        #logger=logging.getLogger('StructTestBler.param_sweep_iterator')
        if not self.testunit_s.scc is None:
            # ---------------------------------------------            
            # Carrier Aggregation
            # ---------------------------------------------
            for pcc_earfcn_idx in range(len(self.testunit_s.pcc.earfcn[self.param_subtest_iter.pcc.rfband])):
                for scc_earfcn_idx in range(len(self.testunit_s.scc.earfcn[self.param_subtest_iter.scc.rfband])):      
                    self.param_sweep_iter.pcc.earfcn=self.testunit_s.pcc.earfcn[self.param_subtest_iter.pcc.rfband][pcc_earfcn_idx]
                    self.param_sweep_iter.scc.earfcn=self.testunit_s.scc.earfcn[self.param_subtest_iter.scc.rfband][scc_earfcn_idx]

                    for pcc_rsepre_idx in range(len(self.testunit_s.pcc.rsepre)):
                        for scc_rsepre_idx in range(len(self.testunit_s.scc.rsepre)):
                            self.param_sweep_iter.pcc.rsepre=self.testunit_s.pcc.rsepre[pcc_rsepre_idx]
                            self.param_sweep_iter.scc.rsepre=self.testunit_s.scc.rsepre[scc_rsepre_idx]

                            for pcc_doppler_idx in range(len(self.testunit_s.pcc.doppler)):
                                for scc_doppler_idx in range(len(self.testunit_s.scc.doppler)):
                                    self.param_sweep_iter.pcc.doppler=self.testunit_s.pcc.doppler[pcc_doppler_idx]
                                    self.param_sweep_iter.scc.doppler=self.testunit_s.scc.doppler[scc_doppler_idx]
                
                                    for pcc_snr_idx in range(len(self.testunit_s.pcc.snr)):
                                        self.param_sweep_iter.pcc.snr=self.testunit_s.pcc.snr[pcc_snr_idx]
                                        self.param_sweep_iter.scc.snr=self.param_sweep_iter.pcc.snr

                                        #for scc_snr_idx in range(len(self.testunit_s.scc.snr)):
                                        #self.param_sweep_iter.scc.snr=self.testunit_s.scc.snr[scc_snr_idx]
                
                                        for pcc_dlmcs_idx in range(len(self.testunit_s.pcc.dlmcs[self.param_subtest_iter.pcc.bwmhz])):
                                            for scc_dlmcs_idx in range(len(self.testunit_s.scc.dlmcs[self.param_subtest_iter.scc.bwmhz])):
                                                self.param_sweep_iter.pcc.dlmcs=self.testunit_s.pcc.dlmcs[self.param_subtest_iter.pcc.bwmhz][pcc_dlmcs_idx]
                                                self.param_sweep_iter.scc.dlmcs=self.testunit_s.scc.dlmcs[self.param_subtest_iter.scc.bwmhz][scc_dlmcs_idx]
            
                                                for pcc_dlnprb_idx in range(len(self.testunit_s.pcc.dlnprb[self.param_subtest_iter.pcc.bwmhz])):
                                                    for scc_dlnprb_idx in range(len(self.testunit_s.scc.dlnprb[self.param_subtest_iter.scc.bwmhz])):
                                                        self.param_sweep_iter.pcc.dlnprb=self.testunit_s.pcc.dlnprb[self.param_subtest_iter.pcc.bwmhz][pcc_dlnprb_idx]
                                                        self.param_sweep_iter.scc.dlnprb=self.testunit_s.scc.dlnprb[self.param_subtest_iter.scc.bwmhz][scc_dlnprb_idx]
            
                                                        for pcc_dlrbstart_idx in range(len(self.testunit_s.pcc.dlrbstart[self.param_subtest_iter.pcc.bwmhz])):
                                                            for scc_dlrbstart_idx in range(len(self.testunit_s.scc.dlrbstart[self.param_subtest_iter.scc.bwmhz])):
                                                                self.param_sweep_iter.pcc.dlrbstart=self.testunit_s.pcc.dlrbstart[self.param_subtest_iter.pcc.bwmhz][pcc_dlrbstart_idx]
                                                                self.param_sweep_iter.scc.dlrbstart=self.testunit_s.scc.dlrbstart[self.param_subtest_iter.scc.bwmhz][scc_dlrbstart_idx]
            
                                                                for pcc_ulmcs_idx in range(len(self.testunit_s.pcc.ulmcs[self.param_subtest_iter.pcc.bwmhz])):
                                                                    for scc_ulmcs_idx in range(len(self.testunit_s.scc.ulmcs[self.param_subtest_iter.scc.bwmhz])):
                                                                        self.param_sweep_iter.pcc.ulmcs=self.testunit_s.pcc.ulmcs[self.param_subtest_iter.pcc.bwmhz][pcc_ulmcs_idx]
                                                                        self.param_sweep_iter.scc.ulmcs=self.testunit_s.scc.ulmcs[self.param_subtest_iter.scc.bwmhz][scc_ulmcs_idx]
                                    
                                                                        for pcc_ulnprb_idx in range(len(self.testunit_s.pcc.ulnprb[self.param_subtest_iter.pcc.bwmhz])):
                                                                            for scc_ulnprb_idx in range(len(self.testunit_s.scc.ulnprb[self.param_subtest_iter.scc.bwmhz])):
                                                                                self.param_sweep_iter.pcc.ulnprb=self.testunit_s.pcc.ulnprb[self.param_subtest_iter.pcc.bwmhz][pcc_ulnprb_idx]
                                                                                self.param_sweep_iter.scc.ulnprb=self.testunit_s.scc.ulnprb[self.param_subtest_iter.scc.bwmhz][scc_ulnprb_idx]
                                    
                                                                                for pcc_ulrbstart_idx in range(len(self.testunit_s.pcc.ulrbstart[self.param_subtest_iter.pcc.bwmhz])):
                                                                                    for scc_ulrbstart_idx in range(len(self.testunit_s.scc.ulrbstart[self.param_subtest_iter.scc.bwmhz])):
                                                                                        self.param_sweep_iter.pcc.ulrbstart=self.testunit_s.pcc.ulrbstart[self.param_subtest_iter.pcc.bwmhz][pcc_ulrbstart_idx]
                                                                                        self.param_sweep_iter.scc.ulrbstart=self.testunit_s.scc.ulrbstart[self.param_subtest_iter.scc.bwmhz][scc_ulrbstart_idx]
                                                                                        
                                                                                        yield self.param_sweep_iter           
        else:
            # ---------------------------------------------            
            # Single Aggregation
            # ---------------------------------------------        
            for pcc_earfcn_idx in range(len(self.testunit_s.pcc.earfcn[self.param_subtest_iter.pcc.rfband])):
                self.param_sweep_iter.pcc.earfcn=self.testunit_s.pcc.earfcn[self.param_subtest_iter.pcc.rfband][pcc_earfcn_idx]

                for pcc_rsepre_idx in range(len(self.testunit_s.pcc.rsepre)):
                    self.param_sweep_iter.pcc.rsepre=self.testunit_s.pcc.rsepre[pcc_rsepre_idx]

                    for pcc_doppler_idx in range(len(self.testunit_s.pcc.doppler)):
                        self.param_sweep_iter.pcc.doppler=self.testunit_s.pcc.doppler[pcc_doppler_idx]
        
                        for pcc_snr_idx in range(len(self.testunit_s.pcc.snr)):
                            self.param_sweep_iter.pcc.snr=self.testunit_s.pcc.snr[pcc_snr_idx]
        
                            for pcc_dlmcs_idx in range(len(self.testunit_s.pcc.dlmcs[self.param_subtest_iter.pcc.bwmhz])):
                                self.param_sweep_iter.pcc.dlmcs=self.testunit_s.pcc.dlmcs[self.param_subtest_iter.pcc.bwmhz][pcc_dlmcs_idx]
        
                                for pcc_dlnprb_idx in range(len(self.testunit_s.pcc.dlnprb[self.param_subtest_iter.pcc.bwmhz])):
                                    self.param_sweep_iter.pcc.dlnprb=self.testunit_s.pcc.dlnprb[self.param_subtest_iter.pcc.bwmhz][pcc_dlnprb_idx]
        
                                    for pcc_dlrbstart_idx in range(len(self.testunit_s.pcc.dlrbstart[self.param_subtest_iter.pcc.bwmhz])):
                                        self.param_sweep_iter.pcc.dlrbstart=self.testunit_s.pcc.dlrbstart[self.param_subtest_iter.pcc.bwmhz][pcc_dlrbstart_idx]
        
                                        for pcc_ulmcs_idx in range(len(self.testunit_s.pcc.ulmcs[self.param_subtest_iter.pcc.bwmhz])):
                                            self.param_sweep_iter.pcc.ulmcs=self.testunit_s.pcc.ulmcs[self.param_subtest_iter.pcc.bwmhz][pcc_ulmcs_idx]
                                
                                            for pcc_ulnprb_idx in range(len(self.testunit_s.pcc.ulnprb[self.param_subtest_iter.pcc.bwmhz])):
                                                self.param_sweep_iter.pcc.ulnprb=self.testunit_s.pcc.ulnprb[self.param_subtest_iter.pcc.bwmhz][pcc_ulnprb_idx]
                                
                                                for pcc_ulrbstart_idx in range(len(self.testunit_s.pcc.ulrbstart[self.param_subtest_iter.pcc.bwmhz])):
                                                    self.param_sweep_iter.pcc.ulrbstart=self.testunit_s.pcc.ulrbstart[self.param_subtest_iter.pcc.bwmhz][pcc_ulrbstart_idx]
                                                                                    
                                                    yield self.param_sweep_iter           
    

    def compute_total_steps(self):
        
        logger=logging.getLogger('StructTestBler.compute_total_steps')
        
        for self.param_subtest_iter in self.param_subtest_iterator():
            
            for self.param_config_iter in self.param_config_iterator():
                
                for self.param_sweep_iter in self.param_sweep_iterator():
     
                    self.totalsteps += 1    


    # ************************************************************************************
    # Functions to update the current test configuration stored into teststep structure
    # ************************************************************************************
    def struct_teststep_init(self, param_subtest=1, param_config=1, param_sweep=1):
        logger=logging.getLogger('%s.struct_teststep_init' % self.STRUCTNAME)
        if param_subtest:        
            # Init subtest parameters
            self.teststep_s.pcc.dmode     = None
            self.teststep_s.pcc.cp        = None
            self.teststep_s.pcc.chtype    = None
            self.teststep_s.pcc.bwmhz     = None
            self.teststep_s.pcc.rfband    = None
            self.teststep_s.pcc.dlulconf  = None
            self.teststep_s.pcc.ssconf    = None
            self.teststep_s.pcc.nhrtx     = None
            self.teststep_s.pcc.riv       = None        
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.dmode    = None
                self.teststep_s.scc.cp       = None
                self.teststep_s.scc.chtype   = None
                self.teststep_s.scc.bwmhz    = None
                self.teststep_s.scc.rfband   = None
                self.teststep_s.scc.dlulconf = None
                self.teststep_s.scc.ssconf   = None
                self.teststep_s.scc.nhrtx    = None
                self.teststep_s.scc.riv      = None        
            logger.debug("Initialised subtest parameters")

        if param_config:                
            # Update config parameters
            self.teststep_s.pcc.schedtype = None    
            self.teststep_s.pcc.pa        = None
            self.teststep_s.pcc.pb        = None        
            self.teststep_s.pcc.tm        = None 
            self.teststep_s.pcc.txants    = None
            self.teststep_s.pcc.pmi       = None
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.schedtype = None    
                self.teststep_s.scc.pa        = None
                self.teststep_s.scc.pb        = None        
                self.teststep_s.scc.tm        = None 
                self.teststep_s.scc.txants    = None
                self.teststep_s.scc.pmi       = None
            logger.debug("Initialised configuration parameters")

        if param_sweep:            
            # Update sweep parameters
            self.teststep_s.pcc.earfcn    = None
            self.teststep_s.pcc.rsepre    = None
            self.teststep_s.pcc.doppler   = None
            self.teststep_s.pcc.snr       = None
            self.teststep_s.pcc.dlmcs     = None
            self.teststep_s.pcc.dlnprb    = None
            self.teststep_s.pcc.dlrbstart = None
            self.teststep_s.pcc.ulmcs     = None
            self.teststep_s.pcc.ulnprb    = None
            self.teststep_s.pcc.ulrbstart = None
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.earfcn    = None
                self.teststep_s.scc.rsepre    = None
                self.teststep_s.scc.doppler   = None
                self.teststep_s.scc.snr       = None
                self.teststep_s.scc.dlmcs     = None
                self.teststep_s.scc.dlnprb    = None
                self.teststep_s.scc.dlrbstart = None
                self.teststep_s.scc.ulmcs     = None
                self.teststep_s.scc.ulnprb    = None
                self.teststep_s.scc.ulrbstart = None
            logger.debug("Initialised sweep parameters")


    def struct_teststep_update(self, param_subtest=1, param_config=1, param_sweep=1):
        logger=logging.getLogger('%s.struct_teststep_update' % self.STRUCTNAME)
        
        if param_subtest:
            # Update subtest parameters
            self.teststep_s.pcc.dmode     = self.param_subtest_iter.pcc.dmode
            self.teststep_s.pcc.cp        = self.param_subtest_iter.pcc.cp
            self.teststep_s.pcc.chtype    = self.param_subtest_iter.pcc.chtype
            self.teststep_s.pcc.bwmhz     = self.param_subtest_iter.pcc.bwmhz
            self.teststep_s.pcc.rfband    = self.param_subtest_iter.pcc.rfband
            self.teststep_s.pcc.dlulconf  = self.param_subtest_iter.pcc.dlulconf
            self.teststep_s.pcc.ssconf    = self.param_subtest_iter.pcc.ssconf
            self.teststep_s.pcc.nhrtx     = self.param_subtest_iter.pcc.nhrtx
            self.teststep_s.pcc.riv       = self.param_subtest_iter.pcc.riv        
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.dmode    = self.param_subtest_iter.scc.dmode
                self.teststep_s.scc.cp       = self.param_subtest_iter.scc.cp
                self.teststep_s.scc.chtype   = self.param_subtest_iter.scc.chtype
                self.teststep_s.scc.bwmhz    = self.param_subtest_iter.scc.bwmhz
                self.teststep_s.scc.rfband   = self.param_subtest_iter.scc.rfband
                self.teststep_s.scc.dlulconf = self.param_subtest_iter.scc.dlulconf
                self.teststep_s.scc.ssconf   = self.param_subtest_iter.scc.ssconf
                self.teststep_s.scc.nhrtx    = self.param_subtest_iter.scc.nhrtx
                self.teststep_s.scc.riv      = self.param_subtest_iter.scc.riv
            logger.debug("Updated subtest parameters")

        if param_config:
            # Update config parameters
            self.teststep_s.pcc.schedtype = self.param_config_iter.pcc.schedtype    
            self.teststep_s.pcc.pa        = self.param_config_iter.pcc.pa
            self.teststep_s.pcc.pb        = self.param_config_iter.pcc.pb        
            self.teststep_s.pcc.tm        = self.param_config_iter.pcc.tm 
            self.teststep_s.pcc.txants    = self.param_config_iter.pcc.txants
            self.teststep_s.pcc.pmi       = self.param_config_iter.pcc.pmi
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.schedtype = self.param_config_iter.scc.schedtype    
                self.teststep_s.scc.pa        = self.param_config_iter.scc.pa
                self.teststep_s.scc.pb        = self.param_config_iter.scc.pb        
                self.teststep_s.scc.tm        = self.param_config_iter.scc.tm 
                self.teststep_s.scc.txants    = self.param_config_iter.scc.txants
                self.teststep_s.scc.pmi       = self.param_config_iter.scc.pmi
            logger.debug("Updated config parameters")

        if param_sweep:                
            # Update sweep parameters
            self.teststep_s.pcc.earfcn    = self.param_sweep_iter.pcc.earfcn
            self.teststep_s.pcc.rsepre    = self.param_sweep_iter.pcc.rsepre
            self.teststep_s.pcc.doppler   = self.param_sweep_iter.pcc.doppler
            self.teststep_s.pcc.snr       = self.param_sweep_iter.pcc.snr
            self.teststep_s.pcc.dlmcs     = self.param_sweep_iter.pcc.dlmcs
            self.teststep_s.pcc.dlnprb    = self.param_sweep_iter.pcc.dlnprb
            self.teststep_s.pcc.dlrbstart = self.param_sweep_iter.pcc.dlrbstart
            self.teststep_s.pcc.ulmcs     = self.param_sweep_iter.pcc.ulmcs
            self.teststep_s.pcc.ulnprb    = self.param_sweep_iter.pcc.ulnprb
            self.teststep_s.pcc.ulrbstart = self.param_sweep_iter.pcc.ulrbstart
            if not self.testunit_s.scc is None:
                self.teststep_s.scc.earfcn    = self.param_sweep_iter.scc.earfcn
                self.teststep_s.scc.rsepre    = self.param_sweep_iter.scc.rsepre
                self.teststep_s.scc.doppler   = self.param_sweep_iter.scc.doppler
                self.teststep_s.scc.snr       = self.param_sweep_iter.scc.snr
                self.teststep_s.scc.dlmcs     = self.param_sweep_iter.scc.dlmcs
                self.teststep_s.scc.dlnprb    = self.param_sweep_iter.scc.dlnprb
                self.teststep_s.scc.dlrbstart = self.param_sweep_iter.scc.dlrbstart
                self.teststep_s.scc.ulmcs     = self.param_sweep_iter.scc.ulmcs
                self.teststep_s.scc.ulnprb    = self.param_sweep_iter.scc.ulnprb
                self.teststep_s.scc.ulrbstart = self.param_sweep_iter.scc.ulrbstart
            logger.debug("Updated sweep parameters")

    
    def struct_teststep_update_defaults(self):
        logger=logging.getLogger('%s.struct_teststep_update_defaults' % self.STRUCTNAME)
        self.teststep_s.pcc.rsepre=self.testunit_s.pcc.rsepre[0]
        self.teststep_s.pcc.earfcn=self.testunit_s.pcc.earfcn[self.teststep_s.pcc.rfband][0]
        self.teststep_s.pcc.snr=max(self.testunit_s.pcc.snr) if not self.testunit_s.pcc.snr is None else None 
        
        if not self.testunit_s.scc is None:
            self.teststep_s.scc.rsepre=self.testunit_s.scc.rsepre[0]
            self.teststep_s.scc.earfcn=self.testunit_s.scc.earfcn[self.teststep_s.scc.rfband][0]
            self.teststep_s.scc.snr=max(self.testunit_s.scc.snr) if not self.testunit_s.scc.snr is None else None 
        logger.debug("Updated default parameters")

    
    # ************************************************************************************
    # Functions to log the content of the structures
    # ************************************************************************************        
    def struct_testconfig_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        logger.info("*****************************************************************************************")
        logger.info("Test configuration structure:")
        logger.info("*****************************************************************************************")
        self.testconfig_s.struct_log()

    def struct_testunit_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        logger.info("*****************************************************************************************")
        logger.info("Test unit structure:")
        logger.info("*****************************************************************************************")
        self.testunit_s.struct_log()

    def struct_teststep_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        logger.info("*****************************************************************************************")
        logger.info("Test step structure:")
        logger.info("*****************************************************************************************")
        self.teststep_s.struct_log()

    def struct_csvreport_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        logger.info("*****************************************************************************************")
        logger.info("Test CSV report structure:")
        logger.info("*****************************************************************************************")
        self.csvreport_s.struct_log()

    def struct_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        self.struct_testconfig_log()
        self.struct_testunit_log()
        logger.info("*******************")
        logger.info("Total steps : %s" % self.totalsteps)
        logger.info("*******************")
        self.struct_teststep_log()
        self.struct_csvreport_log()
            
if __name__ == '__main__':
    pass
    
    
    
    
        
        
        
        
        
    
