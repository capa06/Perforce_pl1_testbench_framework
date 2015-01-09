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
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from str_converter import val2Str, str2Val

# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class Struct(object):
    
    # Access it via Struct.SUPPORTED_TYPES 
    
    def __init__(self, field_l=[], struct_name=None):
        """
          FIELDNAME_L = [ ('field_name', 'field_value') ]  
        """
        
        self.STRUCTNAME   = self.__class__.__name__ if struct_name == None else struct_name
        self.FIELDNAME_L  = []

        if field_l:
            self._add_fields(field_l)
        else:
            # Create an empty structure 
            pass
    
    # -------------------------------------------- #
    #           PRIVATE METHODS                    #
    # -------------------------------------------- #
    def _add_fields(self, field_l):
        from str_converter import val2Str, str2Val 
        # Add fields to the structure
        for field in field_l:
            var_name  = val2Str(field[0])
            if ( (field[1] is None) or (field[1]=='None')):
                var_value=None
            else:
                var_value = str2Val(field[1])
            self.FIELDNAME_L.append(var_name)
            setattr(self, var_name, var_value)

    # -------------------------------------------- #
    #           PUBLIC METHODS                     #
    # -------------------------------------------- #
    def add_field(self, var_name, value=None): 
        # Add fields to the structure
        self.FIELDNAME_L.append(var_name)
        setattr(self, var_name, value)
    
        
    def set_field(self, var_name, value):
        # Update value. Note it is possible to update the field value accessing the structure directly
        logger=logging.getLogger('%s.set_field' % self.STRUCTNAME)
        setattr(self, var_name, value)
        logger.debug("added %s.%s = %s" % (self.STRUCTNAME, var_name, value))

    
    def delete_field(self, var_name):
        logger=logging.getLogger('%s.delete_field' % self.STRUCTNAME)
        try:
            self.FIELDNAME_L.remove(var_name)
            delattr(self, var_name)
        except ValueError:
            logger.warning("%s.%s not present. Nothing to do"  % (self.STRUCTNAME, var_name))
        else:
            logger.debug("removed %s.%s" % (self.STRUCTNAME, var_name))

    def struct_init(self):  
        logger=logging.getLogger('%s.struct_init' % self.STRUCTNAME)
        for idx in range(len(self.FIELDNAME_L)):
            var_name  = self.FIELDNAME_L[idx]
            setattr(self, var_name, None)
        logger.debug('Reset %s completed' % self.STRUCTNAME)

    
    def struct_merge(self, entry_s):
        logger=logging.getLogger('%s.struct_merge' % self.STRUCTNAME)
        if len(entry_s.FIELDNAME_L)>0:
            for var_name in entry_s.FIELDNAME_L:
                src_value = eval("entry_s.%s" % var_name)      
                setattr(self, var_name, src_value)
        logger.debug("Merged %s --> %s" % (entry_s.STRUCTNAME, self.STRUCTNAME))        
            
    def struct_log(self, excl_l=None):  
        logger=logging.getLogger('%s.struct_log' % self.STRUCTNAME)
        if len(self.FIELDNAME_L)>0:
            logger.info("--------------------------------------")
        else:
            logger.info("%s is empty" % self.STRUCTNAME)       
        for idx in range(len(self.FIELDNAME_L)):
            var_name  = self.FIELDNAME_L[idx]
            var_value = eval('self.%s' % var_name)
            if (not excl_l is None) and (var_name in excl_l):
                pass
            else:
                logger.info("%s.%-15s \t: %s" % (self.STRUCTNAME, var_name, var_value))

    def struct_2_str(self):  
        res = "" 
        for idx in range(len(self.FIELDNAME_L)):
            var_name  = self.FIELDNAME_L[idx]
            var_value = eval('self.%s' % var_name)      
            res +=("%s.%-15s \t: %s\n" % (self.STRUCTNAME, var_name, var_value))
        return res
    
    
    def get_fieldname_list(self):
        return self.FIELDNAME_L
    
            
    def __str__(self):
        if len(self.FIELDNAME_L)>0:
            print "--------------------------------------"       
        else:
            print "%s is empty" % self.STRUCTNAME       
        for idx in range(len(self.FIELDNAME_L)):
            var_name  = self.FIELDNAME_L[idx]
            var_value = eval('self.%s' % var_name)
            print "%s.%-15s \t: %s" % (self.STRUCTNAME, var_name, var_value)
        return ""


if __name__ == '__main__':
    pass
    
    
    

    
