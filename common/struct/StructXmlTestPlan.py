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
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'error']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'tools']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from StructXml import StructXml

# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class StructXmlTestPlan(StructXml):
    
    def __init__(self, xmlfile, struct_name):    
        logger=logging.getLogger('StructXmlTestPlan.__init__')
        self.NODE_NAME ='testlist'
        StructXml.__init__(self, xmlfile=xmlfile, struct_name=struct_name, node_name=self.NODE_NAME)
        self._scan_testfiles()
        
        self.testplan_iterator = None
        
    def _get_path_abs(self, path_rel):
        import re
        #path_abs = re.sub('[\\\/]', os.sep, path_rel)
        path_abs = path_rel.replace('/', os.sep)  
        path_abs = os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], path_abs)
        return path_abs
        
    def _scan_testfiles(self):
        logger=logging.getLogger("%s._scan_testfiles()" % self.STRUCTNAME)
        logger.debug("scanning test plan files...")
        for var_name in self.FIELDNAME_L:
            path_rel = eval("self.%s" % var_name)
            path_abs = self._get_path_abs(path_rel)
            if not os.path.isfile(path_abs):
                logger.error("Testplan file not found : %s" % path_abs)
                sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
            else:
                logger.debug("FILE EXIST ? (%s, %s)" % (os.path.isfile(path_abs), path_abs))
        logger.debug("check: PASSED")
    
    def struct_testplan_iterator(self):
        #logger=logging.getLogger("%s.struct_testunit_iterator" % self.STRUCTNAME)
        for var_name in self.FIELDNAME_L:
            path_rel = eval("self.%s" % var_name)
            self.testplan_iterator  = self._get_path_abs(path_rel)
            yield self.testplan_iterator
            
    def get_testid_list(self):
        testid_l =[]
        for testunit in self.get_fieldname_list():
            testid_l.append(int(testunit.replace('testunit_','')))
        return testid_l
            
if __name__ == '__main__':
    pass
