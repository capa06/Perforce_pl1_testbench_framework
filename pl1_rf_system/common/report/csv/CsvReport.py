#-------------------------------------------------------------------------------
# Name:        CsvReport
# Purpose:     Csv summary report
#
# Author:      joashr
#
# Created:     17/06/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import logging, os, sys


(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

try:
    os.environ['PL1_RF_SYSTEM_ROOT']
except KeyError:
    os.environ['PL1_RF_SYSTEM_ROOT'] = os.sep.join(cmdpath.split(os.sep)[:-3])
    print ">> os.environ['PL1_RF_SYSTEM_ROOT']=%s" % os.environ['PL1_RF_SYSTEM_ROOT']
    sys.path.append(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]))


from addSystemPath import AddSysPath
AddSysPath(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['common']))
AddSysPath(os.sep.join(os.environ['PL1_RF_SYSTEM_ROOT'].split(os.sep)[:]+['common', 'config']))

from user_exceptions import *

class CsvReport(object):
    '''
    classdocs
    '''
    verdict={ 0:'PASS', 1:'FAIL', 2:'INVALID'}

    def __init__(self, fname, frmt_header, frmt_msg, modeminfo, instrswinfo ):
        self.fname       = fname
        self.frmt_header = frmt_header
        self.frmt_msg    = frmt_msg
        self.create()
        self.instr_sw_written = False

    def get_full_path_name(self):
        return self.fname

    def create(self):
        func_name = sys._getframe(0).f_code.co_name
        loggerTest = logging.getLogger(__name__ + func_name)
        try:
            fpath=os.path.split(self.fname)[0]
            if not os.path.exists(fpath):
                loggerTest.debug("%s path does not exist, will create" %fpath)
                os.makedirs(fpath)
            if not os.path.isfile(self.fname):
                with open(self.fname,'a') as fd:
                    fd.write(self.frmt_msg % tuple(self.frmt_header))
        except IOError:
            errMsg = ("ERROR: opening file %s" % self.fname)
            loggerTestr.error(errMsg)
            raise ExGeneral(errMsg)

    def append(self, msg_l):
        try:
            with open(self.fname,'a') as fd:
                fd.write(self.frmt_msg % tuple(msg_l))
            fd.close()

        except IOError:
            logging.error("ERROR: opening file %s" % self.fname)
            #raise IOError                          # Propagate error
            sys.exit(code.ERRCODE_SYS_FILE_IO)


    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.frmt_header
        print "%s" % self.frmt_msg
        return ""

if __name__ == "__main__":
    import os, time
    from enableLogging import enable_logging
    enable_logging(loglevel = "debug")

    csv_f='CMU200_TestReport_SUMMARY.csv'
    fpath = os.path.dirname(os.path.abspath(__file__))

    csv_abs_f= os.sep.join(fpath.split(os.sep)[:]+[csv_f])

    csv_frmt_h = ['TestID', 'Verdict', 'Start Time', 'End Time', 'Duration [sec]']
    csv_frmt_msg = '%s, %s, %s, %s, %s\n'

    t0=time.localtime()
    time.sleep(2)
    csv_report=CsvReport(csv_abs_f, csv_frmt_h, csv_frmt_msg, modeminfo="", instrswinfo="")
    t1=time.localtime()                                            # Probe end time
    t0_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t0)
    t1_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t1)
    dt=time.mktime(t1)-time.mktime(t0)                             # Compute duration [sec]
    testID = 1
    testVerdict = 'PASS'
    result = 0

    csv_report.append([testID, testVerdict, t0_frmt, t1_frmt , dt])
