'''
Created on 23 Mar 2014

@author: FRA
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
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))



# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************



# *************************************************************************** 
#                          API PUBLIC FUNCTIONS
# *************************************************************************** 
def str2Val(data_str):
    import ast
    res=ast.literal_eval(data_str)
    return res
    
def val2Str(data_val):
    res=str(data_val)
    return res



if __name__ == '__main__':
    pass
