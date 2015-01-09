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
class TxtReport(object):
    '''
    classdocs
    '''
    def __init__(self, fname):
        self.fname       = fname
        self._create()

    def _create(self):
        logger=logging.getLogger('TxtReport._create')
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


    def append(self, data_s):
        logger=logging.getLogger('TxtReport.append')
        try:
            with open(self.fname,'a') as fd: 
                fd.write("%s\n" % self._val_2_str(data_s))
            fd.close()         
        except IOError:
            logger.error("ERROR: opening file %s" % self.fname)
            #raise IOError                          # Propagate error
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
    
    
    def _val_2_str(self, data_s):
        """
        Transform data structure into a string
        """
        data_str=""
        if type(data_s) is float :
            data_str = '%.2f' % data_s        
        if type(data_s) is int :
            data_str = '%s' % data_s        
        if type(data_s) is str :           
            data_str = data_s               
        if type(data_s) is list :
            data_str=   '[' 
            for k in data_s:
                data_str += " %s," %  self._val_2_str(k)
            data_str = data_str[:-1] + ' ]'             
                         
        elif type(data_s) is tuple:
            data_str=   '('
            for k in data_s:
                data_str += " %s," %  self._val_2_str(k)
            data_str = data_str[:-1] + ' )'             
    
        elif type(data_s) is set:
            data_str=   '['
            for k in data_s:
                data_str += " %s," % self._val_2_str(k)
            data_str = data_str[:-1] + ' ]'             
            
        elif type(data_s) is dict:
            data_str=   '{' 
            for k, v in sorted(data_s.iteritems()):
                data_str += " %s:%s," % (k, self._val_2_str(v))
            data_str = data_str[:-1] + ' }'             
        else:
            pass
                
        return data_str

    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.frmt_header
        print "%s" % self.frmt_msg
        return ""
    

if __name__ == "__main__":
    
    pass
    
    
    
    