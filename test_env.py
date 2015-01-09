#-------------------------------------------------------------------------------
# Name:        test_env
# Purpose:     sets up Jenkins enironment variables
#
# Author:      joashr
#
# Created:     21/10/2013
# Copyright:   (c) joashr 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, site

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

module_root_folder = os.sep.join(cmdpath.split(os.sep)[:-1])

try:
    os.environ['MODULE_ROOT_FOLDER']
except KeyError:
    os.environ['MODULE_ROOT_FOLDER'] = module_root_folder
    #print ">> os.environ['MODULE_ROOT_FOLDER']=%s" % os.environ['MODULE_ROOT_FOLDER']
    # set customised module search part rather than using PYTHONPATH envirnoment variable
    site.addsitedir(module_root_folder)

try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(cmdpath.split(os.sep)[:])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
    sys.path.append(os.environ['PL1TESTBENCH_ROOT_FOLDER'])

try:
    os.environ['TEST_SYSTEM_ROOT_FOLDER']
except KeyError:
    os.environ['TEST_SYSTEM_ROOT_FOLDER']  =  os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'win8', 'test_system'])
    #print ">> os.environ['TEST_SYSTEM_ROOT_FOLDER']=%s" % os.environ['TEST_SYSTEM_ROOT_FOLDER']




