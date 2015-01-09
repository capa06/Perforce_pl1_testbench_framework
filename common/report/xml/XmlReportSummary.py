'''
Created on 27 Oct 2014

@author: fsaracino
'''

import os
import sys
import logging
import traceback
import re



# =============================================================================
# DEFINE LOCAL PATHS 
# =============================================================================
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))




 
# =============================================================================
# IMPORT USER DEFINED LIBRARY 
# =============================================================================
from CfgError import CfgError

# =============================================================================
# GLOBAL VARIABLES 
# =============================================================================
def csv2Xml(file_csv, tag):
    report_xml_h = XmlReportSummary(file_csv, tag)
    report_xml_h.open()
    report_xml_h.csv2xml()
    report_xml_h.close()
    del report_xml_h

# =============================================================================
# HTML LTE TEST REPORT GENERATOR 
# =============================================================================
class XmlReportSummary(object):
    '''
    classdocs
    '''

    def __init__(self, file_csv, tag, name='XmlReportSummary'):
        '''
        Constructor
        '''
        
        self.name         = name
        self.file_csv     = file_csv        
        self.tag          = tag.lower()
        self.fd_csv       = None
        
        self.file_xml     = os.path.splitext(self.file_csv)[0]+'.xml'        
        self.fd_xml       = None
        
        self.TITLE           = '<?xml version="1.0" encoding="UTF-8"?>'
        self.TESTSUITE       = {'name': "%s.nosetests", 'tests':0, 'errors':0, 'failures':0, 'skip':0}
        
        self.testid_key_idx  = None
        self.verdict_key_idx = None
        self.time_key_idx    = None
        self.message_key_idx = None


    # ------------------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------------------
    def _open(self):
        logger=logging.getLogger("%s.open" % self.name)
        try:
            self.fd_csv = open(self.file_csv, 'r')
        except:
            logger.error("Could not open CSV report file : %s" % self.file_csv)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        if os.path.isfile(self.file_xml):
            os.remove(self.file_xml)
        
        try:
            self.fd_xml = open(self.file_xml, 'w')
        except:
            print traceback.format_exc()
            logger.error("Could not open XML report file : %s" % self.file_xml)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        
    def _close(self):
        if not self.fd_csv is None:
            self.fd_csv.close()
        if not self.fd_xml is None:
            self.fd_xml.close()
    
    
    def _update_testsuite_statistics(self):
        logger=logging.getLogger("%s._update_testsuite_statistics" % self.name)

        try:
            self.fd_xml = open(self.file_xml, 'r+')
            self.fd_xml.readline()
            tag="""<testsuite name="%s" tests="%s" failures="%s" errors="%s" skip="%s">""" % (self.TESTSUITE['name'], 
                                                                                              self.TESTSUITE['tests'], 
                                                                                              self.TESTSUITE['failures'], 
                                                                                              self.TESTSUITE['errors'],
                                                                                              self.TESTSUITE['skip'])
            self.insert_tag(tag, level=0)
            self.fd_xml.close()
        except:
            print traceback.format_exc()
            logger.error("Could not open XML report file : %s" % self.file_xml)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
            

    # ------------------------------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------------------------------
    def insert_tag(self, tag, level):
        logger=logging.getLogger("%s.insert_tag" % self.name)
        msg=('\t'*level+'%s\n' % tag)
        self.fd_xml.write(msg)
        if 0: logger.debug("Inserted XML tag : %s" % tag)
        
            
    def open(self):
        self._open()
        self.insert_tag(self.TITLE, level=0)
        tag="""<testsuite name="%s" tests="%s" failures="%s" errors="%s" skip="%s">""" % (self.TESTSUITE['name'], 
                                                                                          self.TESTSUITE['tests'], 
                                                                                          self.TESTSUITE['failures'], 
                                                                                          self.TESTSUITE['errors'],
                                                                                          self.TESTSUITE['skip'])
        self.insert_tag(tag, level=0)

                
    def close(self):
        self.insert_tag('</testsuite>',level=0)
        self._close()
        self._update_testsuite_statistics()


    def csv2xml(self):
        logger=logging.getLogger("%s.csv2xml" % self.name)
        
        line_idx=0 
        while True:
            line=self.fd_csv.readline() 
            if line == "" : break
            line_l=line.split(',') 
            if line_idx==0:
                header_l= [ re.sub(r'[\s|\r\n|\r]', r'', x) for x in line_l]
                if 0: logger.debug("header_l : %s" % header_l)

                self.testid_key_idx  = header_l.index('testid')
                self.verdict_key_idx = header_l.index('verdict')
                self.msgtype_key_idx = header_l.index('return_state')
                self.message_key_idx = header_l.index('description')
                self.time_key_idx    = header_l.index('duration_sec')
                
            else:
                entry_l= [ re.sub(r'[\s|\r|\r\n]', r'', x) for x in line_l]
                if 0: logger.debug("entry_l : %s" % entry_l)
                
                self.TESTSUITE['tests'] +=1
                
                tag="""<testcase classname="%s.testplan_lte" name="testid_%010d" time="%s">""" % (self.tag, int(entry_l[self.testid_key_idx]), entry_l[self.time_key_idx])
                self.insert_tag(tag, level=1)

                if entry_l[self.verdict_key_idx].upper()=='PASS':
                    pass
                elif entry_l[self.verdict_key_idx].upper() in ['FAIL', 'FAILURE']:
                    self.TESTSUITE['failures'] +=1
                    # TODO: adapt this entry to follow Joash's guideline
                    tag="""<failure type="%s" message="%s"></failure>""" % (entry_l[self.msgtype_key_idx], entry_l[self.message_key_idx])
                    self.insert_tag(tag, level=2)
                else:
                #elif entry_l[self.verdict_key_idx].upper()=='INCONCLUSIVE':
                    self.TESTSUITE['errors'] +=1
                    self.TESTSUITE['skip'] +=1
                    # TODO: adapt this entry to follow Joash's guideline
                    tag="""<skipped type="%s" message="%s"></skipped>""" % (entry_l[self.msgtype_key_idx], entry_l[self.message_key_idx])
                    self.insert_tag(tag, level=2)
             
                self.insert_tag('</testcase>', level=1)
                
            line_idx += 1

        self.TESTSUITE['tests'] = max(line_idx-1, 0) 
               


        
if __name__ == '__main__':
    
    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
    file_csv=os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], 'common', 'report', 'xml', 'LTE_FDD_CMW500_TestReport_SUMMARY.csv')
    if 0:
        report_xml_h = XmlReportSummary(file_csv)
        report_xml_h.open()
        report_xml_h.csv2xml()
        report_xml_h.close()
    else:
        csv2Xml(file_csv)
        