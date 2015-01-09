#-------------------------------------------------------------------------------
# Name:        pl1_rf_system_test_env
# Purpose:     define environment variables for RF modem tests
#
# Author:      joashr
#
# Created:     19/09/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, site

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

pl1_rf_system_module_parent = os.sep.join(cmdpath.split(os.sep)[:-1])


try:
    os.environ['PL1_RF_SYSTEM_ROOT']
except KeyError:
    os.environ['PL1_RF_SYSTEM_ROOT'] = os.sep.join(cmdpath.split(os.sep)[:])
    print ">> Setting up RF environment variable(s)"
    print ">> os.environ['PL1_RF_SYSTEM_ROOT']=%s" % os.environ['PL1_RF_SYSTEM_ROOT']
    site.addsitedir(pl1_rf_system_module_parent)

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    print test_env_dir
    sys.path.append(test_env_dir)
    import test_env





