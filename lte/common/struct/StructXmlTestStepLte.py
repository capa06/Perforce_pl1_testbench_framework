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
from StructXmlTestUnitLte import StructXmlTestUnitLte

# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class StructXmlTestStepLte(StructXmlTestUnitLte):
    
    def __init__(self, xmlfile, struct_name):    
        logger=logging.getLogger('StructXmlTestStepLte.__init__')        
        StructXmlTestUnitLte.__init__(self, xmlfile=xmlfile, struct_name=struct_name)                                                        
             
            
if __name__ == '__main__':
    pass

        
        
        
        
    
