'''
Created on 31 Jul 2013

@author: fsaracino
'''


# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
import time
import re

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-5])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','common', 'struct']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
from Struct import Struct
from StructXmlCsvReportBlerLte import StructXmlCsvReportBlerLte

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from StructXml import StructXml
from CsvReport import CsvReport


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
#class CsvReportBlerLte(StructXmlCsvReportBlerLte, CsvReport):
class CsvReportBlerLte(CsvReport):
    '''
    classdocs
    '''
    FILEXML_TEMPLATE=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','common', 'struct', 'template', 'structxml_csvreportbler_lte_template.xml'])
    
    def __init__(self, fname, pwrmeas, statistics=0, report_name='CsvReportBlerLte'):
        self.report_name    = report_name
        self.fname          = fname
        self.pwrmeas        = pwrmeas
        self.statistics     = statistics
        
        # 4. add function to write params and measurements into the file
        
        # Get CSV report entry structure
        self.entry_header_s = StructXmlCsvReportBlerLte(xmlfile=self.FILEXML_TEMPLATE, struct_name='%s.entry_header_s' % self.report_name)
        
        # Build the entry list for storing the info into the CSV file 
        self.header_entry_l = self._csventry_header()
        if 0: print len(self.header_entry_l), self.header_entry_l
                
        # Initialise CSV file
        CsvReport.__init__(self, self.fname, self.header_entry_l)

    # *******************************************************
    # Private methods
    # *******************************************************
    def _csventry_header(self):
        res  = self.entry_header_s.verdict.get_fieldname_list()
        res = res + self.entry_header_s.params.get_fieldname_list()
        res = res + self.entry_header_s.meas_bler.get_fieldname_list()
        if self.pwrmeas:
            res = res + self.entry_header_s.meas_pwr.get_fieldname_list()
        if self.statistics:
            res = res + self.entry_header_s.meas_dlthr.get_fieldname_list()
            res = res + self.entry_header_s.meas_rank.get_fieldname_list()
            res = res + self.entry_header_s.meas_cqi.get_fieldname_list()
            res = res + self.entry_header_s.meas_pmi.get_fieldname_list()
            res = res + self.entry_header_s.meas_harq.get_fieldname_list()
        return res
    
    # *******************************************************
    # Public methods
    # *******************************************************
    def report_update_params(self, teststep_s, carrier):
        logger=logging.getLogger('%s.report_update_params' % self.report_name)
        # teststep may be useless
        self.entry_header_s.params.teststep  = None
        self.entry_header_s.params.carrier   = carrier 
        self.entry_header_s.params.dmode     = teststep_s.dmode   
        self.entry_header_s.params.dlulconf  = teststep_s.dlulconf
        self.entry_header_s.params.ssconf    = teststep_s.ssconf
        self.entry_header_s.params.bwmhz     = teststep_s.bwmhz
        self.entry_header_s.params.rfband    = teststep_s.rfband
        self.entry_header_s.params.earfcn    = teststep_s.earfcn
        self.entry_header_s.params.cp        = teststep_s.cp
        self.entry_header_s.params.tm        = teststep_s.tm 
        self.entry_header_s.params.txants    = teststep_s.txants
        self.entry_header_s.params.pmi       = teststep_s.pmi
        self.entry_header_s.params.rsepre    = teststep_s.rsepre
        self.entry_header_s.params.pa        = teststep_s.pa
        self.entry_header_s.params.pb        = teststep_s.pb
        self.entry_header_s.params.chtype    = teststep_s.chtype
        self.entry_header_s.params.snr       = teststep_s.snr
        self.entry_header_s.params.doppler   = teststep_s.doppler
        self.entry_header_s.params.schedtype = teststep_s.schedtype
        self.entry_header_s.params.nhrtx     = teststep_s.nhrtx
        self.entry_header_s.params.riv       = teststep_s.riv
        self.entry_header_s.params.dlmcs     = teststep_s.dlmcs
        self.entry_header_s.params.dlnprb    = teststep_s.dlnprb
        self.entry_header_s.params.dlrbstart = teststep_s.dlrbstart
        self.entry_header_s.params.ulmcs     = teststep_s.ulmcs
        self.entry_header_s.params.ulnprb    = teststep_s.ulnprb
        self.entry_header_s.params.ulrbstart = teststep_s.ulrbstart        
        logger.debug("UPDATED params")
             

    def report_update_meas_bler(self, meas_dlbler_s, meas_ulbler_s):
        logger=logging.getLogger('%s.report_update_measbler' % self.report_name)
        self.entry_header_s.meas_bler.valid          = 1
        self.entry_header_s.meas_bler.dlrely         = meas_dlbler_s.dlrely
        self.entry_header_s.meas_bler.dlthr_Mbps     = '%.6f' % (meas_dlbler_s.dlthr*0.001)
        self.entry_header_s.meas_bler.dlthr_min_Mbps = '%.6f' % (meas_dlbler_s.dlthr_min*0.001)
        self.entry_header_s.meas_bler.dlthr_max_Mbps = '%.6f' % (meas_dlbler_s.dlthr_max*0.001)
        if (meas_dlbler_s.ack+meas_dlbler_s.nack+meas_dlbler_s.dtx)>0:
            self.entry_header_s.meas_bler.dlbler         = '%.6f' % (float(meas_dlbler_s.nack+meas_dlbler_s.dtx)/(meas_dlbler_s.ack+meas_dlbler_s.nack+meas_dlbler_s.dtx))
        else:
            self.entry_header_s.meas_bler.dlbler         = None
        self.entry_header_s.meas_bler.cqi            = meas_dlbler_s.cqi
        self.entry_header_s.meas_bler.ack            = meas_dlbler_s.ack
        self.entry_header_s.meas_bler.nack           = meas_dlbler_s.nack
        self.entry_header_s.meas_bler.dtx            = meas_dlbler_s.dtx
        self.entry_header_s.meas_bler.sf_total       = meas_dlbler_s.sf_total
        self.entry_header_s.meas_bler.sf_scheduled   = meas_dlbler_s.sf_scheduled
        self.entry_header_s.meas_bler.ulrely         = meas_ulbler_s.ulrely
        self.entry_header_s.meas_bler.ulthr_Mbps     = '%.6f' % (meas_ulbler_s.ulthr*0.001) if (not meas_ulbler_s.ulthr is None) else None 
        self.entry_header_s.meas_bler.ulbler         = '%.6f' % (meas_ulbler_s.ulbler*0.01) if (not meas_ulbler_s.ulbler is None) else None 
        self.entry_header_s.meas_bler.crc_pass       = meas_ulbler_s.crc_pass
        self.entry_header_s.meas_bler.crc_fail       = meas_ulbler_s.crc_fail
        
        logger.debug("UPDATED measbler")
        
    def report_update_meas_pwr(self, volt_V, current_mA):
        logger=logging.getLogger('%s.report_update_measpwr' % self.report_name)
        self.entry_header_s.meas_pwr.voltage_V  = '%.3f' % float(volt_V)
        self.entry_header_s.meas_pwr.current_mA = '%.3f' % float(current_mA)
        try:
            self.entry_header_s.meas_pwr.power_mW= '%.3f' % (float(volt_V)*float(current_mA))
        except:
            self.entry_header_s.meas_pwr.power_mW= None
        logger.debug("UPDATED measpwr: %s[V], %s[mA], %s[mW]" % (self.entry_header_s.meas_pwr.voltage_V, 
                                                                 self.entry_header_s.meas_pwr.current_mA,
                                                                 self.entry_header_s.meas_pwr.power_mW))

    
    
    def _build_verdict(self, throughput_Mbps, bestscore_Mbps, tolerance, threshold_offs_Mbps):
        """
        Description:
            build verdicts for measurements        
        """        
        thrshld  = max([ float((1-tolerance)*bestscore_Mbps-threshold_offs_Mbps), float(0)])    
        verdict  = 'FAIL' if ( float(throughput_Mbps) < thrshld ) else 'PASS' 
        
        return verdict

    def report_update_verdict_dl(self, best_dlthr, tolerance, threshold_offs_Mbps):
        logger=logging.getLogger('%s.report_update_verdict_dl' % self.report_name)
        if (not self.entry_header_s.meas_bler.dlthr_Mbps is None) and (not best_dlthr is None):
            self.entry_header_s.verdict.best_dlthr_Mbps = best_dlthr
            self.entry_header_s.verdict.tolerance       = tolerance
            self.entry_header_s.verdict.verdict_dl      = self._build_verdict(self.entry_header_s.meas_bler.dlthr_Mbps, best_dlthr, tolerance, threshold_offs_Mbps)
        else:
            self.entry_header_s.verdict.verdict_dl = None
        
        logger.debug("UPDATED verdict_dl")

    def report_update_verdict_ul(self, best_ulthr, tolerance, threshold_offs_Mbps):
        logger=logging.getLogger('%s.report_update_verdict_ul' % self.report_name)
        if (not self.entry_header_s.meas_bler.ulthr_Mbps is None) and (not best_ulthr is None):
            self.entry_header_s.verdict.best_ulthr_Mbps = best_ulthr
            self.entry_header_s.verdict.verdict_ul = self._build_verdict(self.entry_header_s.meas_bler.ulthr_Mbps, best_ulthr, tolerance, threshold_offs_Mbps)
        else:
            self.entry_header_s.verdict.verdict_ul = None
            
        logger.debug("UPDATED verdict_ul")
    
    def get_verdict_ul(self):
        verdict = None
        if (not self.entry_header_s.meas_bler.ulthr_Mbps is None):
            verdict = 'INCONCLUSIVE' if (self.entry_header_s.verdict.verdict_ul is None) else self.entry_header_s.verdict.verdict_ul              
        return verdict 
    
    def get_verdict_dl(self):
        verdict = None
        if (not self.entry_header_s.meas_bler.dlthr_Mbps is None):
            verdict = 'INCONCLUSIVE' if (self.entry_header_s.verdict.verdict_dl is None) else self.entry_header_s.verdict.verdict_dl              
        return verdict 

        #return (self.entry_header_s.verdict.verdict_dl if (not self.entry_header_s.verdict.verdict_dl is None) else 'INCONCLUSIVE')  
    
    
    def report_append_entry(self):
        logger=logging.getLogger('%s.report_update_measharq' % self.report_name)

        entry_l=[]
        field_l = self.entry_header_s.verdict.get_fieldname_list()
        for field in field_l:    
            entry_l.append(eval("self.entry_header_s.verdict.%s" % field))

        field_l = self.entry_header_s.params.get_fieldname_list()
        for field in field_l:    
            entry_l.append(eval("self.entry_header_s.params.%s" % field))
    
        field_l = self.entry_header_s.meas_bler.get_fieldname_list()
        for field in field_l:    
            entry_l.append(eval("self.entry_header_s.meas_bler.%s" % field))

        if self.pwrmeas:
            field_l = self.entry_header_s.meas_pwr.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_pwr.%s" % field))
        if self.statistics:
            field_l = self.entry_header_s.meas_dlthr.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_dlthr.%s" % field))

            field_l = self.entry_header_s.meas_rank.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_rank.%s" % field))

            field_l = self.entry_header_s.meas_cqi.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_cqi.%s" % field))

            field_l = self.entry_header_s.meas_pmi.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_pmi.%s" % field))

            field_l = self.entry_header_s.meas_harq.get_fieldname_list()
            for field in field_l:    
                entry_l.append(eval("self.entry_header_s.meas_harq.%s" % field))

        # Append the line to the CSV report
        self.append_entry(entry_l)


    # NOTE: there measurements will be stored into the database only
    def report_update_meas_dlthr(self, meas_dlthr_s):
        logger=logging.getLogger('%s.report_update_measdlthr' % self.report_name)
        self.entry_header_s.meas_dlthr.dlthr_cw1 = meas_dlthr_s.dlthr_cw1
        self.entry_header_s.meas_dlthr.dlthr_cw2 = meas_dlthr_s.dlthr_cw2
        logger.debug("UPDATED meas_dlthr")
         
    def report_update_meas_rank(self, meas_rank_s):
        logger=logging.getLogger('%s.report_update_meas_rank' % self.report_name)
        self.entry_header_s.meas_rank.rank = meas_rank_s.rank
        logger.debug("UPDATED meas_rank")

    def report_update_meas_cqi(self, meas_cqi_s):
        logger=logging.getLogger('%s.report_update_meas_cqi' % self.report_name)
        self.entry_header_s.meas_cqi.cqi_cw1 = meas_cqi_s.cqi_cw1
        self.entry_header_s.meas_cqi.cqi_cw2 = meas_cqi_s.cqi_cw2
        logger.debug("UPDATED meas_cqi")

    def report_update_meas_pmi(self, meas_pmi_s):
        logger=logging.getLogger('%s.report_update_meas_pmi' % self.report_name)
        self.entry_header_s.meas_pmi.pmi_ri1 = meas_pmi_s.pmi_ri1
        self.entry_header_s.meas_pmi.pmi_ri2 = meas_pmi_s.pmi_ri2
        logger.debug("UPDATED meas_cqi")

    def report_update_meas_harq(self, meas_harq_s):
        logger=logging.getLogger('%s.report_update_meas_harq' % self.report_name)
        self.entry_header_s.meas_harq.harq_cw1 = meas_harq_s.harq_cw1
        self.entry_header_s.meas_harq.harq_cw2 = meas_harq_s.harq_cw2
        logger.debug("UPDATED meas_harq")
        
    def struct_verdict_init(self):
        self.entry_header_s.verdict.struct_init()
    
    def report_log(self):
        logger=logging.getLogger('CsvReportBlerLte.report_log')
        logger.info("************************************************************")
        logger.info("CSV file report    : %s" % self.fname)
        #logger.info("entry header list  : %s" % self.header_entry_l)
        logger.info("power measurements : %s" % 'OFF' if self.pwrmeas==0 else 'ON')
        logger.info("************************************************************")
        self.entry_header_s.struct_log()
        
        
    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.header_entry_l
        print "%s" % self.frmt_msg
        return ""

if __name__ == "__main__":
    
    pass
