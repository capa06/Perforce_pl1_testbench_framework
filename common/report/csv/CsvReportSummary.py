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


# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
from CsvReport import CsvReport

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from StructXml import StructXml


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class CsvReportSummary(CsvReport):
    '''
    classdocs
    '''
    FILEXML_TEMPLATE=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv', 'template', 'csv_report_summary.xml'])
    
    def __init__(self, fname):
        self.fname       = fname
        tmp_h=StructXml(xmlfile=self.FILEXML_TEMPLATE, struct_name='csv_s', node_name='summary')
        self.frmt_header = tmp_h.get_fieldname_list()
        del tmp_h
        CsvReport.__init__(self, self.fname, self.frmt_header)
        self.append_entry_header()
    
    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.frmt_header
        print "%s" % self.frmt_msg
        return ""

if __name__ == "__main__":
    pass
