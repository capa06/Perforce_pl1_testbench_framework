'''
Created on 31 Jul 2013

@author: fsaracino
'''

import logging, os, sys

import pl1_testbench_framework.test_env

from pl1_testbench_framework.common.config.CfgError import CfgError

class CsvReport(object):
    '''
    classdocs
    '''
    verdict={ 0:'PASS', 1:'FAIL', 2:'INVALID'}
    code = CfgError()

    def __init__(self, fname, frmt_header, frmt_msg):
        self.fname       = fname
        self.frmt_header = frmt_header
        self.frmt_msg    = frmt_msg
        self.create()

    def get_full_path_name(self):
        return self.fname

    def create(self):
        try:
            fpath=os.path.split(self.fname)[0]
            if not os.path.exists(fpath):
                os.makedirs(fpath)
            if not os.path.isfile(self.fname):
                with open(self.fname,'a') as fd:
                    fd.write(self.frmt_msg % tuple(self.frmt_header))
        except IOError:
            logging.error("ERROR: opening file %s" % self.fname)
            sys.exit(code.ERRCODE_SYS_FILE_IO)

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

    csv_f='CMW500_TestReport_SUMMARY.csv'
    fpath = os.path.dirname(os.path.abspath(__file__))
    csv_abs_f= os.sep.join(fpath.split(os.sep)[:]+[csv_f])

    csv_frmt_h = ['TestID', 'Verdict', 'Return State', 'Description', 'Start Time', 'End Time', 'Duration [sec]']
    csv_frmt_msg = '%s, %s, %s, %s, %s, %s, %s\n'

    t0=time.localtime()
    time.sleep(2)
    csv_report=CsvReport(csv_abs_f, csv_frmt_h, csv_frmt_msg)
    t1=time.localtime()                                            # Probe end time
    t0_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t0)
    t1_frmt=time.strftime("%Y/%m/%d %H:%M:%S", t1)
    dt=time.mktime(t1)-time.mktime(t0)                             # Compute duration [sec]
    testID = 1
    testVerdict = 'PASS'
    result = 0

    code = CfgError()
    csv_report.append([testID, testVerdict, result, code.MSG[result], t0_frmt, t1_frmt , dt])
