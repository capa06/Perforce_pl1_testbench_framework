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
from Struct import Struct

# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class StructXml(Struct):
    
    def __init__(self, xmlfile, struct_name, node_name):    
        logger=logging.getLogger('StructXml.__init__')
        # Build the field list from the xml file
        if os.path.isfile(xmlfile):
            if 0:
                logger.debug("xml file     : %s" % xmlfile)
                logger.debug("struct name  : %s" % struct_name)
                logger.debug("node name    : %s" % node_name)
            
            # Retrieve the lists of fields
            field_l = []    

            try:
                tree    = parse(xmlfile)
                section = tree.find(node_name)
            except:
                logger.error("Failed parsing XML file : %s" % xmlfile)
                sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
            if section is None:
                logger.warning("XML node '%s' not found" % node_name)
            else:
                for node in section.iter('field'):
                    field = (node.attrib.get('name'), str(node.text))
                    field_l.append(field)
                    if 0: logger.debug("field=%s,  value=%s" % (node.attrib.get('name'),  node.text))
        else:
            logger.error("File not found: %s" % xmlfile)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
        
        # Initialize the structure 
        Struct.__init__(self, field_l=field_l, struct_name=struct_name)
    
    
                
            
if __name__ == '__main__':
    
    pass
