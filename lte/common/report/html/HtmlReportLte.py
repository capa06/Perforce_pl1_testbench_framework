'''
Created on 11 Aug 2013

@author: fsaracino
'''


# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
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


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'html']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from HtmlReport import HtmlReport

    
# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
def htmlReportLte(file_conf, file_meas):    
    file_html=os.path.splitext(file_meas)[0]+'.html'
    report_html_h = HtmlReportLte(file_html)
    if os.path.exists(file_html):
        os.remove(file_html)
    report_html_h.open()
    report_html_h.append_title()

    report_html_h.conf2html(file_conf)
    report_html_h.meas2html(file_meas)
    report_html_h.close()


class HtmlReportLte(HtmlReport):
        
    def __init__(self, file_html):
        HtmlReport.__init__(self, file_html, name='HtmlReportLte')        
        self.TITLE            = 'LTE TEST REPORT'
        self.SECTION_CONF     = 'Test Configuration'
        self.SECTION_MEAS     = 'Test Measurements'
        self.CELLPADDING      = 3
        self._carrier_idx      = None
        self._verdict_dl_idx   = None
        self._verdict_ul_idx   = None
        self._rank_idx         = None     
        self._cqi_cw1_idx      = None     
        self._cqi_cw2_idx      = None     
        self._pmi_ri1_idx      = None     
        self._pmi_ri2_idx      = None     
        self._harq_cw1_idx     = None     
        self._harq_cw2_idx     = None
        self._meas_idx_l       = []
        
        

        
    def append_title(self):
        #logger=logging.getLogger("%s.append_title" % self.name)
        self.insert_tag(tag='<H1>%s</H1>' % self.TITLE,  level=2)
        
    def open_table(self, table_name, level=2):
        self.insert_tag('<H2>%s</H2>' % table_name,  level)
        self.insert_tag('<TABLE>', level)
        self.insert_tag('<TBODY >', level+1)
    
    def close_table(self, level=2):
        #logger=logging.getLogger("%s.close_table_modeminfo" % self.name)
        self.insert_tag('</TBODY >', level+1)
        self.insert_tag('</TABLE>', level)
 
    def update_table_conf(self, line_l, level=4):
        #logger=logging.getLogger("%s.append_title" % self.name)
        for line in line_l:
            self.insert_tag('<TR ><TD CLASS="table_conf_entry">%s</TD> </TR>' % line, level)
    
    def update_table_meas(self, tag, line_l, level=4):
        #logger=logging.getLogger("%s.append_title" % self.name)
        self.insert_tag('<TR >', level)
        
        if tag.lower()=='header':
            self._carrier_idx=line_l.index('carrier')
            self._verdict_dl_idx = line_l.index('verdict_dl')
            self._verdict_ul_idx = line_l.index('verdict_ul')
            
            self._rank_idx       = line_l.index('rank')     
            self._cqi_cw1_idx    = line_l.index('cqi_cw1')    
            self._cqi_cw2_idx    = line_l.index('cqi_cw2')    
            self._pmi_ri1_idx    = line_l.index('pmi_ri1')    
            self._pmi_ri2_idx    = line_l.index('pmi_ri2')   
            self._harq_cw1_idx   = line_l.index('harq_cw1') 
            self._harq_cw2_idx   = line_l.index('harq_cw2')
            self._meas_idx_l.append(self._rank_idx)
            self._meas_idx_l.append(self._cqi_cw1_idx)
            self._meas_idx_l.append(self._cqi_cw2_idx)
            self._meas_idx_l.append(self._pmi_ri1_idx)
            self._meas_idx_l.append(self._pmi_ri2_idx)
            self._meas_idx_l.append(self._harq_cw1_idx)
            self._meas_idx_l.append(self._harq_cw2_idx)
            
            for idx in range(len(line_l)):
                if idx not in self._meas_idx_l:
                    self.insert_tag('<TD CLASS="table_meas_header">%s</TD>' % re.sub(r'[\r\n|\r]', r'', line_l[idx]), level+1)
        else:
            if (re.match('[n|N][o|O][n|N][e|E]', line_l[self._verdict_dl_idx], re.I) or (re.match('[p|P][c|C][c|C]', line_l[self._carrier_idx]) and re.match('[n|N][o|O][n|N][e|E]', line_l[self._verdict_ul_idx]))):
                frmt='table_meas_entry_inconcl'
            elif (re.match('[f|F][a|A][i|I][l|L]', line_l[self._verdict_dl_idx], re.I)) or (re.match('[f|F][a|A][i|I][l|L]', line_l[self._verdict_ul_idx], re.I)):
                frmt='table_meas_entry_failure'
            else:
                frmt='table_meas_entry'
            for idx in range(len(line_l)):
                if idx not in self._meas_idx_l:
                    self.insert_tag('<TD CLASS="%s">%s</TD>' % (frmt, re.sub(r'[\r\n|\r]', r'', line_l[idx])), level+1)
        self.insert_tag('</TR >', level)
    
    
    def conf2html(self, file_conf):
        logger=logging.getLogger('conf2html')

        # Open test configuration table
        self.open_table(self.SECTION_CONF)
        
        # Read configuration file
        if not os.path.isfile(file_conf):
            logger.warning("Test configuration file not found: %s" % file_conf)
            return -1
        with open(file_conf, 'r') as fd_conf:
            msg=fd_conf.read()
        msg_l = msg.split('\n')
        fd_conf.close()
        
        # Update test configuration table
        self.update_table_conf(msg_l)
        
        # Close test configuration table
        self.close_table()
        
    
    def meas2html(self, file_meas):
        logger=logging.getLogger('meas2html')

        # Open test configuration table
        self.open_table(self.SECTION_MEAS)

        # Read configuration file
        if not os.path.isfile(file_meas):
            logger.warning("Test measurements file not found: %s" % file_meas)
            return -1

        with open(file_meas, 'r') as fd_meas:    
            state=1             #  1: entry header, 2:entry 
            while True:
                line=fd_meas.readline() 
                if line == "" : break
                line_l=[ x.strip() for x in line.split(',')]
                if state==1:
                    self.update_table_meas('header', line_l, level=4)               
                    state=2
                else:
                    self.update_table_meas('entry', line_l, level=4)                      
        fd_meas.close()

        # Close test configuration table
        self.close_table()
        

if __name__ == '__main__':
    
    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
    file_conf_txt = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'html', '20141103_122741_CMW500_TestReport', 'LTE_FDD_CMW500_TestConf_testID_00103.txt'])
    file_meas_csv = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'html', '20141103_122741_CMW500_TestReport', 'LTE_FDD_CMW500_TestMeas_testID_00103.csv'])
    
    htmlReportLte(file_conf_txt, file_meas_csv)