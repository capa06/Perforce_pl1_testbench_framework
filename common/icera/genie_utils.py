'''
Created on 14 Jul 2014

@author: fsaracino
'''


# ********************************************************************
# IMPORT SYSTEM MODULES
# ********************************************************************
import os
import sys
import time
import logging

from multiprocessing import Process

# ********************************************************************
# IMPORT USER DEFINED PATHS
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath('').split(os.sep)[0:-2])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass


# ********************************************************************
# GLOBAL VARIABLES
# ********************************************************************
# Icera logs
log_iom_f    = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current', 'output.iom'])
log_db_f     = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current', 'output.ix'])
geanielog_cmd_iom   = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera_log_serial -t %s' % log_iom_f])

# Icera decoders
icera_aes = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-aes'])
icera_b64 = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-b64'])




def GenieLogStart(enable_flag):
    global geanielog_cmd_iom
    if enable_flag:
        # Start IOM process
        log_proc=Process(target=os.system, args=(geanielog_cmd_iom,))
        time.sleep(2)                                                                                    
        log_proc.start()
        logging.debug("**************>>>>> Started IOM procid = %s" %  log_proc.pid)

    
def GenieLogCollect(enable_flag, filename):
    if enable_flag: 
        logging.debug("Collecting Genie logs into file : %s" % filename)
        GenieLogKill(enable_flag)  
        GenieLogDump(filename)


def GenieLogKill(enable_flag):
    if enable_flag:
        if sys.platform in ['cygwin', 'win32']:
            os.system('taskkill /f /t /im icera_log_serial.exe')
        elif sys.platform in ['linux', 'linux2', 'linux3']:
            os.system('killall -v icera_log_serial')
        else:
            logging.warning(">> GenieLogKill(): OS not supported. No process killed")
    time.sleep(2)                                                                                    

    
def GenieLogDump(logfile):
    # Format logfile names
    log_glp_f    = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current', '%s.glp' % logfile])
    #log_dec_f    = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current', '%s.iot' % logfile])

    # Prepare commands
    geanielog_cmd_db    = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera_log_serial -e %s' % log_db_f])
    geanielog_cmd_glp   = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'genie-log-file convert %s %s %s' % (log_iom_f, log_db_f, log_glp_f)]) 
    #geanielog_cmd_dec   = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'genie-log-file decode %s %s' % (log_glp_f, log_dec_f)])

    # TRACEGEN
    proc_log=Process(target=os.system, args=(geanielog_cmd_db,))
    time.sleep(2)                                                                                    
    proc_log.start()
    logging.debug("Collecting tracegen procid = %s" %  proc_log.pid)
    proc_log.join()
    # GLP
    proc_log=Process(target=os.system, args=(geanielog_cmd_glp,))
    time.sleep(2)                                                                                    
    proc_log.start()
    logging.debug("Creating GLP = %s" %  proc_log.pid)
    proc_log.join()
        
    # DECODE
    #proc_log=Process(target=os.system, args=(geanielog_cmd_dec,))
    #InsertPause(2)                                                                                    
    #proc_log.start()
    #logging.debug("Decoding GLP = %s" %  proc_log.pid)
    #proc_log.join()

    GenieLogClean()


def GenieLogClean():
    global log_db_f
    global log_iom_f
    # Clean data from any previous test
    if os.path.isfile(log_db_f):
        os.remove(log_db_f)
        logging.debug(">> Removed genie log : %s" % log_db_f)
    if os.path.isfile(log_iom_f):
        os.remove(log_iom_f)
        logging.debug(">> Removed genie log : %s" % log_iom_f)



def GenieLogErase(enable_flag, status):
    GenieLogClean()
    if (not status) and enable_flag:
        currdir=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current'])        
        currdir=os.path.normpath(currdir)
        filelist = [ f for f in os.listdir(currdir) if f.endswith(".glp") ]
        for filename in filelist:
            fullname=os.path.join(os.path.abspath(currdir), filename)
            os.remove(fullname)
            logging.debug("Removed logfile : %s" % f)
            
            
if __name__ == '__main__':
    pass