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


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class CsvReport(object):
    '''
    classdocs
    '''
    def __init__(self, fname, frmt_header, cleanup=1):
        self.fname       = fname
        self.frmt_header = frmt_header
        self.cleanup     = cleanup
        self.frmt_msg    = '%s, '*(len(frmt_header)-1)+'%s\n'
        if self.cleanup: 
            self._create()

    def _create(self):
        logger=logging.getLogger('CsvReport._create')
        try:
            if os.path.isfile(self.fname):
                os.remove(self.fname) 
            fpath=os.path.split(self.fname)[0]
            if not os.path.exists(fpath): 
                os.makedirs(fpath)
            #with open(self.fname,'a') as fd:
            #    fd.write(self.frmt_msg % tuple(self.frmt_header))
        except IOError:
            logger.error("ERROR: opening file %s" % self.fname)
            #raise IOError                          # Propagate error
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)


    def append_tlv(self, tag, val):
        logger=logging.getLogger('CsvReport.append_tlv')
        try:
            with open(self.fname,'a') as fd: 
                fd.write("%s:,%s\n" % (tag, val))
            fd.close()         
        except IOError:
            logger.error("ERROR: opening file %s" % self.fname)
            #raise IOError                          # Propagate error
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)


    def append_entry_header(self):
        logger=logging.getLogger('CsvReport.append_entry_header')
        if not os.path.isfile(self.fname): 
            self.append_entry(self.get_header())
        else:
            logger.warning("file already exists, skipping header insertion")

    def append_entry(self, msg_l):
        logger=logging.getLogger('CsvReport.append')
        try:
            if not os.path.isfile(self.fname): 
                self._create()            
            with open(self.fname,'a') as fd: 
                fd.write(self.frmt_msg % tuple(msg_l))       
            fd.close()         
        except IOError:
            logger.error("ERROR: opening file %s" % self.fname)
            #raise IOError                          # Propagate error
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
            
            
    def get_header(self):
        return self.frmt_header


    def get_filename(self):
        return self.fname

    
    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.frmt_header
        print "%s" % self.frmt_msg
        return ""

if __name__ == "__main__":
    
    pass
