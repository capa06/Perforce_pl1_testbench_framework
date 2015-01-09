#-------------------------------------------------------------------------------
#
# Author:      joashr
#
# Created:     29/11/2013
#
# Addapted from pl1testbench
#-------------------------------------------------------------------------------


import os, sys, time

#import pl1_wcdma_testbench.test_env
import pl1_testbench_framework.test_env

#from pl1_wcdma_testbench.common.config.cfg_conf import cfg_conf
from pl1_testbench_framework.wcdma.common.config.cfg_conf import cfg_conf


class CsvReportBler(object):

    '''
    Defines CVS report for BLER test
    '''

    bler_params  = [ 'TESTID', 'RFBAND', 'UARFCN', 'CHTYPE', 'DATARATE    ', 'SNR', 'POWER', 'TXANTS']
    bler_meas    = [ 'DLRELY', 'BER', 'BLER', 'DLBLER', 'LOSTBLOCKS', 'PNDiscontinuity']
    bler_verdict = [ 'DL VERDICT']
    pwr_meas     = [ 'Imin[mA]', 'Iavrg[mA]', 'Imax[mA]', 'Ideviation', 'PWRmin[mW]@3.8V', 'PWRavrg[mW]@3.8V', 'PWRmax[mW]@3.8V' ]


    def __init__(self, test_s, test_conf, csv_fname, pwrmeas):

        self.fname       = csv_fname
        self.time        = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        self.modeminfo   = test_s.modeminfo
        self.testID      = test_s.testID
        self.testtype    = test_s.testtype

        self.rfband      = test_s.rfband
        self.uarfcn_dic  = test_s.uarfcn_dic
        self.chtype      = test_s.chtype
        self.datarate    = test_s.datarate
        self.snr         = test_s.snr
        self.rfpower     = test_s.rfpower
        self.txants      = test_s.txants
        self.cmwinfo     = test_s.cmwinfo

        # ********************************************
        # REPORT HEADER
        # ********************************************
        self.header_frmt = "%s, %s\n"
        self.header = [('date[yyyy/mm/dd]', self.time),
                       ('id','['+ str(self.testID)+']'),
                       ('testtype',   self.testtype),
                       ('rfband',     '['+' '.join(str(x) for x in self.rfband)+']'),
                       ('uarfcn',     self.uarfcn_dic),
                       ('chtype',     '['+' '.join(str(x) for x in self.chtype)+']'),
                       ('datarate',   '['+'  '.join(str(x) for x in self.datarate )+']'),
                       ('snr',         '['+' '.join(str(x) for x in self.snr)+']'),
                       ('rfpower',     str(self.rfpower)),
                       ('txants', self.txants),
                       ('modeminfo',  self.modeminfo),
                       ('cmwinfo',    '['+' '.join(str(x) for x in self.cmwinfo)+']')]

        # ********************************************
        # REPORT MESSAGE
        # ********************************************
        self.msg_header = self.bler_params + self.bler_meas + self.bler_verdict

        if pwrmeas:
            self.msg_header = self.msg_header + self.pwr_meas

        self.msg_frmt='%s, '*(len(self.msg_header)-1)+'%s\n'

        # Init CSV report file
        self.create()

    def create(self):
        try:
            fpath=os.path.split(self.fname)[0]
            if not os.path.exists(fpath):
                os.makedirs(fpath)
            if os.path.isfile(self.fname):
                os.remove(self.fname)
            self.wr_header()
            self.wr_msg_header()

        except IOError:
            print "ERROR: opening file %s" % self.fname
            raise IOError                          # Propagate error

    def wr_header(self):
        with open(self.fname,'a') as fd:
            for (row_head, val) in self.header:
                fd.write(self.header_frmt %(row_head, val))

    def wr_msg_header(self):
        with open(self.fname,'a') as fd:
            fd.write(self.msg_frmt % tuple(self.msg_header))

    def append(self, data_list):
        try:
            if not os.path.isfile(self.fname):
                self.create()
            with open(self.fname,'a') as fd:
                fd.write(self.msg_frmt % tuple(data_list))

        except IOError:
            print "ERROR: opening file %s" % self.fname
            raise IOError                          # Propagate error

    """
    def set_modem_info(self, modeminfo=""):
        self.modeminfo = modeminfo

    def set_cmwinfo(self, cmwinfo=""):
        self.cmwinfo=cmwinfo
    """


if __name__ == '__main__':

    #from pl1_wcdma_testbench.common.config.test_plan import test_plan
    from pl1_testbench_framework.wcdma.common.config.test_plan import test_plan
    #from pl1_wcdma_testbench.common.config.cfg_test import cfg_test
    from pl1_testbench_framework.wcdma.common.config.cfg_test import cfg_test

    conf = cfg_conf(cmwip = '10.21.141.148', ctrlif = 'AT', pwrmeas = 0,
                    loglevel="INFO", test2execute=['0'], usimemu = 0,
                    psugwip='10.21.141.174', psugpib=5)


    testID_list = sorted(test_plan.keys())

    single_test_list = []
    single_test_list.append(testID_list[0])

    for testID in single_test_list:
        curr_test = cfg_test(testID)
        print curr_test
        csv_f='WCDMA_TestReport_testID_%s_testType_%s.csv' % (curr_test.testID, curr_test.testtype)
        csv_abs_f= os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'results', 'current', csv_f])
        print csv_abs_f
        report_s=CsvReportBler(curr_test, conf, csv_abs_f, conf.pwrmeas)


