'''
Created on 27 Oct 2014

@author: fsaracino
'''

import os
import sys
import logging
import time
import traceback



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


# =============================================================================
# HTML LTE TEST REPORT GENERATOR 
# =============================================================================
class HtmlReport(object):
    '''
    classdocs
    '''

    def __init__(self, file_html, name='HtmlReport'):
        '''
        Constructor
        '''
        
        self.name         = name
        self.file_html    = file_html
        self.fd           = None

    # ------------------------------------------------------------------------
    # COMMON METHODS
    # ------------------------------------------------------------------------
    def _open(self):
        logger=logging.getLogger("%s.open" % self.name)
        try:
            self.fd = open(self.file_html, 'w')
        except:
            logger.error("Could not open HTML report file : %s" % self.file_html)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        
    def _close(self):
        if not self.fd is None:
            self.fd.close()

    
    def _insert_head(self, level):
        """
          Configure the HTML document down to the BODY level
        """
        #logger=logging.getLogger("%s.insert_head" % self.name)

        self.insert_tag('<HEAD>', level)

        self.insert_tag('<TITLE>LTE TEST REPORT</TITLE>', level+1)    
        self.insert_tag('<LINK REL="HOME" HREF="index.html">', level+1)
        self.insert_tag('<META NAME="AUTHOR" CONTENT="fsaracino@nvidia.com">', level+1)
        self.insert_tag('<META NAME="COPYRIGHT" content="&copy; 2014 NVIDIA LTD">', level+1)
        self.insert_tag('<META NAME="KEYWORDS" CONTENT="pl1testbench,LTE">', level+1)
        self.insert_tag('<META NAME="DATE" CONTENT="2014-10-29T08:49:37+00:00">', level+1)
        self.insert_tag('<STYLE TYPE="text/css">', level+1)
        self.insert_tag('<!-- BODY          {                                                                   color: #000000;                       background: #FFFFFF } -->', level+2) 
        self.insert_tag('<!-- H1            { border:  2px solid #FFFFFF; font-style: bold;   font-size : 16pt; color: #FFFFFF;  text-align: center;  background: #009325 } -->', level+2)
        self.insert_tag('<!-- H2            { border:  1px solid #FFFFFF; font-style: bold;   font-size : 14pt; color: #000000;  text-align: left;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- H3            { border:  1px solid #FFFFFF; font-style: bold;   font-size : 12pt; color: #000000;  text-align: left;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- P             { border:  1px solid #FFFFFF; font-style: bold;   font-size : 10pt; color: #000000;  text-align: left;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- a             { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #0000FF;  text-align: left;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- .table_conf_header { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #FFFFFF;  text-align: left;    background: #009325 } -->', level+2)  
        self.insert_tag('<!-- .table_conf_entry  { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #000000;  text-align: left;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- .table_meas_header { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #FFFFFF;  text-align: center;    background: #009325 } -->', level+2)
        self.insert_tag('<!-- .table_meas_entry  { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #000000;  text-align: center;    background: #FFFFFF } -->', level+2)
        self.insert_tag('<!-- .table_meas_entry_failure { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #000000;  text-align: center;    background: #FF0000 } -->', level+2)
        self.insert_tag('<!-- .table_meas_entry_inconcl { border:  1px solid #FFFFFF; font-style: bold;   font-size :  9pt; color: #000000;  text-align: center;    background: #FFFF00 } -->', level+2)
        self.insert_tag('</STYLE>', level+1)
        
        self.insert_tag('</HEAD>', level)
    

    def insert_tag(self, tag, level):
        logger=logging.getLogger("%s.insert_tag" % self.name)
        msg=('\t'*level+'%s\n' % tag)
        self.fd.write(msg)
        if 0: logger.debug("Inserted HTML tag : %s" % tag)
        
    def open(self):
        logger=logging.getLogger("%s.open" % self.name)
        self._open()
        # Head
        self.insert_tag(tag='<!DOCTYPE HTML NVIDIA Modem Test Report>', level=0)
        self.insert_tag(tag='<HTML>', level=0)
        self._insert_head(level=1)
        self.insert_tag(tag='<BODY>',  level=1)


    def close(self):
        logger=logging.getLogger("%s.close" % self.name)
        self.insert_tag(tag='</BODY>',  level=1)
        self.insert_tag(tag='</HTML>', level=0)
        self._close()


    # ------------------------------------------------------------------------
    # CUSTOM METHODS
    # ------------------------------------------------------------------------
               


        
if __name__ == '__main__':
    
    pass
