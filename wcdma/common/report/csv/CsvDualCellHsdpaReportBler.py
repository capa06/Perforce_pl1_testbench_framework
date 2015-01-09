#-------------------------------------------------------------------------------
# Name:        CsvDualCellHsdpaReportBler
# Purpose:     Inherited from CsvReportBler
#              Produce Dual Cell HSDPA Bler Report Mesaurements
#
# Author:      joashr
#
# Created:     28/01/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, time

from CsvReportBler import CsvReportBler

class CsvDualCellHsdpaReportBler(CsvReportBler):

    '''
    Defines CVS report for HSPA BLER test
    '''

    bler_params  = [ 'TESTID', 'RFBAND', 'UARFCN', 'CHTYPE', 'DATARATE', 'SNR', 'POWER', 'TXANTS', 'SCHEDTYPE', 'MODULATION', 'Ki', 'NUM_HSDSCH_CODES', 'SNR_2', 'POWER_2', 'MODULATION_2', 'Ki_2', 'NUM_HSDSCH_CODES_2']
    bler_meas    = [ 'NSF', 'TARGET Tput(Mbps)', 'DL_TPUT(Mbps)', 'DL_BLER', 'TOL(%)', 'CQI', 'SENT(%)', 'ACK(%)', 'NACK(%)', 'DTX(%)', 'TARGET Tput_2(Mbps)', 'DL_TPUT_2(Mbps)', 'DL_BLER_2', 'CQI_2', 'SENT_2(%)', 'ACK_2(%)', 'NACK_2(%)', 'DTX_2(%)']
    bler_verdict = [ 'DL VERDICT']
    pwr_meas     = [ 'Imin[mA]', 'Iavrg[mA]', 'Imax[mA]', 'Ideviation', 'PWRmin[mW]@3.8V', 'PWRavrg[mW]@3.8V', 'PWRmax[mW]@3.8V' ]


    def __init__(self, test_s, test_conf, csv_fname, pwrmeas):

        self.fname              = csv_fname
        self.time               = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
        self.modeminfo          = test_s.modeminfo
        self.testID             = test_s.testID
        self.testtype           = test_s.testtype

        self.rfband             = test_s.rfband
        self.uarfcn_dic         = test_s.uarfcn_dic
        self.chtype             = test_s.chtype
        self.datarate           = test_s.datarate
        self.snr                = test_s.snr_1
        self.rfpower            = test_s.rfpower_1
        self.txants             = test_s.txants

        self.txants             = test_s.txants
        self.schedtype          = test_s.schedtype
        self.modulation         = test_s.modulation_1
        self.ki                 = test_s.ki_1
        self.num_hsdsch_codes   = test_s.num_hsdsch_codes_1
        self.cmwinfo            = test_s.cmwinfo

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
                       ('schedtype', self.schedtype),
                       ('modulation', self.modulation),
                       ('Ki', self.ki),
                       ('Num HSDSCH code', self.num_hsdsch_codes),
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


if __name__ == '__main__':
    import os
    from test_plan import test_plan
    from cfg_test import cfg_test
    from cfg_test_dc_hsdpa import cfg_test_dc_hsdpa
    from cfg_conf import cfg_conf

    conf = cfg_conf(cmwip = '10.21.140.206', ctrlif = 'AT', pwrmeas = 0,
                    loglevel="INFO", test2execute=['0'], usimemu = 0,
                    psugwip='10.21.141.174', psugpib=5)


    testID_list = sorted(test_plan.keys())

    single_test_list = []
    single_test_list.append(testID_list[2])


    for testID in single_test_list:
        #curr_test = cfg_test(testID)
        cur_test_testtype = test_plan[testID]['TESTTYPE']
        if cur_test_testtype == 'DCHSDPA_BLER_PERF':
            curr_test = cfg_test_dc_hsdpa(testID)
            curr_test.set_cmwinfo(cmwinfo="n/a")
            print curr_test
            csv_f='WCDMA_TestReport_testID_%s_testType_%s.csv' % (curr_test.testID, curr_test.testtype)
            csv_abs_f= os.sep.join(os.environ['PL1_WCDMA_TEST_ROOT'].split(os.sep)[:]+['results', 'current', csv_f])
            print csv_abs_f
            report_s=CsvDualCellHsdpaReportBler(curr_test, conf, csv_abs_f, conf.pwrmeas)

            param_list = ["1", "1", "10700", 'None', 'dl_Hsdpa_ul_Hsupa', "30", "-60", "1", 'UDCH', '64-QAM', "62", "15"]
            meas_list = ['4000', '21096000.000', '20689900.000', '1.925', "5", '30', '98.075', '98.037', '1.963', '0.000']
            verdict_s = "PASS"
            msg_s = param_list + meas_list + [verdict_s]

            report_s.append(msg_s)

