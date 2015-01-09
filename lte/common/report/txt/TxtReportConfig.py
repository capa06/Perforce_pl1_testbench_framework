'''
Created on 24 Sep 2014

@author: fsaracino
'''




# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
import time


# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-5])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'txt']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from TxtReport import TxtReport


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
#class CsvReportBlerLte(StructXmlCsvReportBlerLte, CsvReport):
class TxtReportConfig(TxtReport):
    
    def __init__(self, fname, report_name='txtconfig'):
        
        self.fname = fname
        TxtReport.__init__(self, self.fname)

    def append_tlv(self, tag, val):
        self.append("%-30s : %s" % (tag, self._val_2_str(val)))
    
    def append_test_configuration(self, testunit_s):
        self.append("%-30s : %s" % ('testid',        self._val_2_str(testunit_s.common.testid)))
        self.append("%-30s : %s" % ('rat',           self._val_2_str(testunit_s.common.rat)))
        self.append("%-30s : %s" % ('testtype',      self._val_2_str(testunit_s.common.testtype)))
        self.append("%-30s : %s" % ('descr',         self._val_2_str(testunit_s.common.descr)))
        self.append("%-30s : %s" % ('PCC.',          self._val_2_str('')))        
        self.append("%-30s : %s" % ('    dmode',     self._val_2_str(testunit_s.pcc.dmode)))
        self.append("%-30s : %s" % ('    dlulconf',  self._val_2_str(testunit_s.pcc.dlulconf)))
        self.append("%-30s : %s" % ('    ssconf',    self._val_2_str(testunit_s.pcc.ssconf)))
        self.append("%-30s : %s" % ('    bwmhz',     self._val_2_str(testunit_s.pcc.bwmhz)))
        self.append("%-30s : %s" % ('    rfband',    self._val_2_str(testunit_s.pcc.rfband)))
        self.append("%-30s : %s" % ('    earfcn',    self._val_2_str(testunit_s.pcc.earfcn)))
        self.append("%-30s : %s" % ('    cp',        self._val_2_str(testunit_s.pcc.cp)))
        self.append("%-30s : %s" % ('    tm',        self._val_2_str(testunit_s.pcc.tm)))
        self.append("%-30s : %s" % ('    txants',    self._val_2_str(testunit_s.pcc.txants)))
        self.append("%-30s : %s" % ('    pmi',       self._val_2_str(testunit_s.pcc.pmi)))
        self.append("%-30s : %s" % ('    rsepre',    self._val_2_str(testunit_s.pcc.rsepre)))
        self.append("%-30s : %s" % ('    pa',        self._val_2_str(testunit_s.pcc.pa)))
        self.append("%-30s : %s" % ('    pb',        self._val_2_str(testunit_s.pcc.pb)))
        self.append("%-30s : %s" % ('    chtype',    self._val_2_str(testunit_s.pcc.chtype)))
        self.append("%-30s : %s" % ('    snr',       self._val_2_str(testunit_s.pcc.snr)))
        self.append("%-30s : %s" % ('    doppler',   self._val_2_str(testunit_s.pcc.doppler)))
        self.append("%-30s : %s" % ('    schedtype', self._val_2_str(testunit_s.pcc.schedtype)))
        self.append("%-30s : %s" % ('    harq',      self._val_2_str(testunit_s.pcc.harq)))
        self.append("%-30s : %s" % ('    dlmcs',     self._val_2_str(testunit_s.pcc.dlmcs)))
        self.append("%-30s : %s" % ('    dlnprb',    self._val_2_str(testunit_s.pcc.dlnprb)))
        self.append("%-30s : %s" % ('    dlrbstart', self._val_2_str(testunit_s.pcc.dlrbstart)))
        self.append("%-30s : %s" % ('    ulmcs',     self._val_2_str(testunit_s.pcc.ulmcs)))
        self.append("%-30s : %s" % ('    ulnprb',    self._val_2_str(testunit_s.pcc.ulnprb)))
        self.append("%-30s : %s" % ('    ulrbstart', self._val_2_str(testunit_s.pcc.ulrbstart)))
        if not testunit_s.scc is None:
            self.append("%-30s : %s" % ('SCC.',          self._val_2_str('')))
            self.append("%-30s : %s" % ('    dmode',     self._val_2_str(testunit_s.scc.dmode)))
            self.append("%-30s : %s" % ('    dlulconf',  self._val_2_str(testunit_s.scc.dlulconf)))
            self.append("%-30s : %s" % ('    ssconf',    self._val_2_str(testunit_s.scc.ssconf)))
            self.append("%-30s : %s" % ('    bwmhz',     self._val_2_str(testunit_s.scc.bwmhz)))
            self.append("%-30s : %s" % ('    rfband',    self._val_2_str(testunit_s.scc.rfband)))
            self.append("%-30s : %s" % ('    earfcn',    self._val_2_str(testunit_s.scc.earfcn)))
            self.append("%-30s : %s" % ('    cp',        self._val_2_str(testunit_s.scc.cp)))
            self.append("%-30s : %s" % ('    tm',        self._val_2_str(testunit_s.scc.tm)))
            self.append("%-30s : %s" % ('    txants',    self._val_2_str(testunit_s.scc.txants)))
            self.append("%-30s : %s" % ('    pmi',       self._val_2_str(testunit_s.scc.pmi)))
            self.append("%-30s : %s" % ('    rsepre',    self._val_2_str(testunit_s.scc.rsepre)))
            self.append("%-30s : %s" % ('    pa',        self._val_2_str(testunit_s.scc.pa)))
            self.append("%-30s : %s" % ('    pb',        self._val_2_str(testunit_s.scc.pb)))
            self.append("%-30s : %s" % ('    chtype',    self._val_2_str(testunit_s.scc.chtype)))
            self.append("%-30s : %s" % ('    snr',       self._val_2_str(testunit_s.scc.snr)))
            self.append("%-30s : %s" % ('    doppler',   self._val_2_str(testunit_s.scc.doppler)))
            self.append("%-30s : %s" % ('    schedtype', self._val_2_str(testunit_s.scc.schedtype)))
            self.append("%-30s : %s" % ('    harq',      self._val_2_str(testunit_s.scc.harq)))
            self.append("%-30s : %s" % ('    dlmcs',     self._val_2_str(testunit_s.scc.dlmcs)))
            self.append("%-30s : %s" % ('    dlnprb',    self._val_2_str(testunit_s.scc.dlnprb)))
            self.append("%-30s : %s" % ('    dlrbstart', self._val_2_str(testunit_s.scc.dlrbstart)))
            self.append("%-30s : %s" % ('    ulmcs',     self._val_2_str(testunit_s.scc.ulmcs)))
            self.append("%-30s : %s" % ('    ulnprb',    self._val_2_str(testunit_s.scc.ulnprb)))
            self.append("%-30s : %s" % ('    ulrbstart', self._val_2_str(testunit_s.scc.ulrbstart)))
        
if __name__ == '__main__':    
    pass

