#-------------------------------------------------------------------------------
# Name:        rf system test common_functions.py
# Purpose:     common functions used in pl1_rf_system regression testing
#
# Author:      joashr
#
# Created:     16/05/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re, shutil, os, logging, time, sys

try:
    import pl1_rf_system_test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir = os.sep.join(cmdpath.split(os.sep)[:-1])
    sys.path.append(test_env_dir)
    import pl1_rf_system_test_env

from pl1_rf_system.common.user_exceptions import *

def get_rat_from_testcategory(test_cat="",cmd_rat=False):
    p = re.compile( r'(\w*)(_\w*)' )
    m = p.match(test_cat)
    ratmap = {'WCDMA':'3G','GSM':'2G','LTE':'LTE'}
    errMsg = ""
    rat = None
    if m:
        rat = m.group(1)
        if rat.upper() == 'GSM' or rat.upper() == 'WCDMA' or rat.upper() == 'LTE':
            if cmd_rat:
                return ratmap[rat.upper()]
            else:
                return rat
        else:
            errMsg = "RAT %s is not supported, format of TESTTYPE is <RAT>_*" %rat
            errMsg = errMsg + ("\nwhere RAT is GSM or WCDMA or LTE")
            raise ExGeneral(errMsg)
    else:
            errMsg = "RAT is not supported, format of TESTTYPE is <RAT>_*"
            errMsg = errMsg + ("\nwhere RAT is GSM or WCDMA or LTE")
            raise ExGeneral(errMsg)

def remove_dir(dir_path):
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except WindowsError:
            print "cannnot remove directory %s, check that the file is not being used by another process" %dir_path
            print "continuing anyway"


def pause(duration_s, poll_time_sec=1, desc=""):
    logger_test = logging.getLogger('pause')
    remaining_time = duration_s
    logger_test.debug("Wait time %s secs : "%(duration_s) + desc)
    while remaining_time > 0:
        time.sleep(poll_time_sec)
        remaining_time -= poll_time_sec
        logger_test.debug("remaining time %s" %remaining_time)

def convert_dict_keys_to_upper(dictionary):
    keys = dictionary.keys()
    values = dictionary.values()

    newKeys = [keyValue.upper() for keyValue in keys]
    newDict = dict(zip(newKeys, values))
    return newDict

def run_script(cmd):
    from subprocess import Popen, PIPE
    print "%s" %cmd
    pipe = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr =  pipe.communicate()
    print stdout
    if stderr:
        print stderr
    return pipe.returncode

def print_dict(dictionary):
    for k in dictionary.keys():
        print"%-20s => %s" %(k, dictionary[k])

