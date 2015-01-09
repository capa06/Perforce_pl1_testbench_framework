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
class StructXmlTestUnitLte(StructXml):
    
    def __init__(self, xmlfile, struct_name):    
        logger=logging.getLogger('StructXmlTestUnitLte.__init__')
        
        self.STRUCTNAME  = struct_name
        self.XMLFILE     = xmlfile
        self.FIELDNAME_L = []
        
        # Create substructures
        self.NODE_L=['common', 'pcc', 'scc']
        for node in self.NODE_L:
            setattr(self, node, eval("StructXml(xmlfile=xmlfile, struct_name=(struct_name + '.' + node), node_name=node)"))
                
        # Invalidate empty structures
        for node in self.NODE_L:
            var_name='.'.join(['self', node, 'FIELDNAME_L'])
            if len(eval(var_name))==0:
                setattr(self, node, None)
                    
    def struct_merge(self, entry_s):
        logger=logging.getLogger('%s.struct_merge' % self.STRUCTNAME)
        
        if len(entry_s.FIELDNAME_L)>0:
            for var_name in entry_s.FIELDNAME_L:
                src_value = eval("entry_s.%s" % var_name)      
                setattr(self, var_name, src_value)
        # OK
        #if (not entry_s.common is None):
        #    for var_name in entry_s.common.FIELDNAME_L:
        #        src_value = eval("entry_s.common.%s" % var_name)      
        #        setattr(self.common, var_name, src_value)
        for node in entry_s.NODE_L:
            if eval("(not entry_s.%s is None)" % node):
                for var_name in eval("entry_s.%s.FIELDNAME_L" % node):
                    src_value = eval("entry_s.%s.%s" % (node,var_name))      
                    setattr(eval("self.%s" % node), var_name, src_value)
                    
        logger.debug("Merged %s --> %s" % (entry_s.STRUCTNAME, self.STRUCTNAME))        
        
                            
    def struct_log(self):
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        
        for var_name in self.FIELDNAME_L:
            logger.info("%-15s: %s" % (var_name, eval('self.%s' % var_name)))
        
        for node in self.NODE_L:
            try:
                eval("self.%s.struct_log()" % node)
            except AttributeError:       
                pass  # Do nothing in case None structure
             
            
if __name__ == '__main__':
    pass
        
        
        
        
        
        
    
