'''
Created on 31 Jul 2013

@author: fsaracino
'''


# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
import time
import re

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','common', 'struct']))


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
from Struct import Struct

# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from StructXml import StructXml
from CsvReport import CsvReport


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
class TableSnrLte(CsvReport):
    '''
    classdocs
    '''
    FILEXML_TEMPLATE=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct', 'template', 'structxml_table_snr.xml'])
    SNR_MIN    = -3
    SNR_MAX    = 33
    
    def __init__(self, fname):
        self.fname          = fname

        self.table          = {}
        self.table_header_l = None
        self.key_idx        = None
        self.snr_bler0_idx  = None
        self.snr_bler1_idx  = None
        self.bler_thrshld   = float('1E-4')
        
        self.snr_increase   = 0
        self.snr_decrease   = 0
        self.stop_event     = 0
        self.skip_event     = 0
        

        tmp_h=StructXml(xmlfile=self.FILEXML_TEMPLATE, struct_name='table_s', node_name='snr')
        self.frmt_header = tmp_h.get_fieldname_list()
        del tmp_h
        CsvReport.__init__(self, self.fname, self.frmt_header, cleanup=0)
        
        self._table_init()
        self.load()

        
    # **********************************************************
    # Private methods
    # ********************************************************** 
    def _table_init(self):
        # Create table if it does not exists and insert header
        if not os.path.isfile(self.fname): 
            self.append_entry_header()
    
    def _set_index(self):
        logger=logging.getLogger('TableSnrLte._load_entry')
        
        self.key_idx       = self.table_header_l.index('key') 
        self.snr_bler0_idx = self.table_header_l.index('snr_bler0')
        self.snr_bler1_idx = self.table_header_l.index('snr_bler1')
        
        if 0:
            logger.debug("key_idx       : %s" % self.key_idx)
            logger.debug("snr_bler1_idx : %s" % self.snr_bler1_idx)
            logger.debug("snr_bler0_idx : %s" % self.snr_bler0_idx)
         
              
    def _load_entry(self, val_l):
        logger=logging.getLogger('TableSnrLte._load_entry')

        if 1:
            logger.debug("table['%s'] : {'snr_bler1': %s, 'snr_bler0':%s}" % (val_l[self.key_idx],  val_l[self.snr_bler1_idx], val_l[self.snr_bler0_idx]))
        self.table.update({val_l[self.key_idx]:{'snr_bler1' :val_l[self.snr_bler1_idx], 'snr_bler0' :val_l[self.snr_bler0_idx]}})


    # **********************************************************
    # Public methods
    # **********************************************************
    def set_snr_increase(self):
        self.snr_decrease = 0
        self.snr_increase = 1

    def set_snr_decrease(self):
        self.snr_decrease = 1
        self.snr_increase = 0

    def reset_events(self):
        self.stop_event     = 0
        self.skip_event     = 0

    def reset_event_stop(self):
        self.stop_event     = 0
        
    def reset_event_skip(self):
        self.skip_event     = 0

        
        
        
         
    def load(self):
        logger=logging.getLogger('TableSnrLte.load')
        try:
            with open(self.fname,'r') as fd:
                # Process header
                line=fd.readline() 
                if line == "" :
                    logger.warning("Empty file: %s" % self.fname)
                    return 1
        
                # Create a list and remove any special character and space from the keys value
                self.table_header_l = [re.sub('[\n\t\r]', '' , x.strip()) for x in line.split(',')]
                if 1: logger.debug("table_header_l : %s" % self.table_header_l)
                
                # Check information stored into file
                if self.table_header_l != self.get_header():
                    logger.error("Malformed SNR table: %s" % self.table_header_l)
                    sys.exit(CfgError.ERRCODE_TEST_FAILURE_PARAMCONFIG)
                    
                self._set_index()
                
                # Process measurements
                while True:
                    line=fd.readline() 
                    if line == "" : break
                                                
                    # Create a list and remove any special character and leading space from the values
                    value_l = [re.sub('[\n\t\r]', '' , x.lstrip()) for x in line.split(',')]
                    if 1: logger.debug("value_l : %s" % value_l)
                    self._load_entry(value_l)

                         
            fd.close()         
        except IOError:
            logger.error("ERROR: opening file %s" % self.fname)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

    
    def build_key(self, chtype, tm, txants, nhrtx, mcs, carrier):
        logger=logging.getLogger('TableSnrLte.build_key')
        key="%s_tm_%d_txants_%d_nhrtx_%02d_dlmcs_%s_%s" % (('none' if chtype is None else chtype.lower()), 
                                                             tm, 
                                                             txants, 
                                                             (0 if nhrtx is None else nhrtx), 
                                                             ('amc' if mcs is None else ('%02d' % mcs)),
                                                             carrier.lower())
        if 0: logger.debug("key : %s" % key)
        return key        
    
    def view(self):        
        logger=logging.getLogger('TableSnrLte.view')
        for key in sorted(self.table.keys()):
            logger.info("%s: {snr_bler1:%s, snr_bler0:%s}" %(key, self.table[key]['snr_bler1'], self.table[key]['snr_bler0']))    

    
    def save(self):
        logger=logging.getLogger('TableSnrLte.save')
        
        if os.path.isfile(self.fname):
            os.remove(self.fname)
        
        self.append_entry_header()
        
        for key in sorted(self.table.keys()):
            self.append_entry([key, self.table[key]['snr_bler1'], self.table[key]['snr_bler0']])


    def insert(self, val_l):        
        #logger=logging.getLogger('TableSnrLte.insert')    
        self._load_entry(val_l)
            
    
    def update(self, key, snr, bler_meas):        
        logger=logging.getLogger('TableSnrLte.update')
        
        if (bler_meas > 1) or (bler_meas<0):
            logger.warning("Invalid BLER : %s. Skipping table update" % bler_meas)
            return   
        try:
            if (bler_meas <= self.bler_thrshld):
                self.table[key]['snr_bler0'] = snr
                if self.snr_increase: 
                    self.stop_event=1
                logger.debug("updated table_snr[%s]['snr_bler0']=%s, stop_condition=%s" % (key, self.table[key]['snr_bler0'], self.stop_condition()))
            elif (bler_meas >= (1-self.bler_thrshld)):
                self.table[key]['snr_bler1'] = snr
                if self.snr_decrease: 
                    self.stop_event=1   
                logger.debug("updated table_snr[%s]['snr_bler1']=%s, stop_condition=%s" % (key, self.table[key]['snr_bler1'], self.stop_condition()))
        except KeyError:
            self.table.update({key:{'snr_bler1':None, 'snr_bler0':None}})
            if (bler_meas <= self.bler_thrshld):
                self.table[key]['snr_bler0'] = snr
                self.table[key]['snr_bler1'] = min(self.SNR_MIN, snr)
                
                if self.snr_increase: 
                    self.stop_event=1
                logger.debug("updated table_snr[%s]['snr_bler0']=%s, stop_condition=%s" % (key, self.table[key]['snr_bler0'], self.stop_condition()))
            elif (bler_meas >= (1-self.bler_thrshld)):
                self.table[key]['snr_bler1'] = max(snr, self.SNR_MAX)

                self.table[key]['snr_bler1'] = snr
                if self.snr_decrease: 
                    self.stop_event=1   
                logger.debug("updated table_snr[%s]['snr_bler1']=%s, stop_condition=%s" % (key, self.table[key]['snr_bler1'], self.stop_condition()))
            else:
                pass
                
                
    def detect_skip_condition(self, chtype, tm, txants, nhrtx, mcs, carrier, snr):
        logger=logging.getLogger('TableSnrLte.detect_skip_condition')
        # SKIP condition triggered on FIXED scheduler only (mcs==None)            
        if (not mcs is None):
            # Search for lower mcs
            mcs_lower, mcs_upper = None, None
            for dlmcs in range(mcs, -1, -1):
                key =  self.build_key(chtype, tm, txants, nhrtx, dlmcs, carrier)
                try:
                    tmp = self.table[key]
                except KeyError:
                    continue
                else:
                    mcs_lower=dlmcs
                    break
            # Search for upper mcs                
            for dlmcs in range(mcs, 29, 1):
                key =  self.build_key(chtype, tm, txants, nhrtx, dlmcs, carrier)
                try:
                    tmp = self.table[key]
                except KeyError:
                    continue
                else:
                    mcs_upper=dlmcs
                    break
            
            if 1: logger.debug("selected mcs_lower=%s, mcs_upper=%s" % (mcs_lower, mcs_upper))
    
            # Reset skip event
            self.skip_event=0
            
            # Set stkip event                
            if (not mcs_lower is None) and (snr < float(self.table[self.build_key(chtype, tm, txants, nhrtx, mcs_lower, carrier)]['snr_bler1'])):
                self.skip_event=1
            elif (not mcs_upper is None) and (snr > float(self.table[self.build_key(chtype, tm, txants, nhrtx, mcs_upper, carrier)]['snr_bler0'])):
                self.skip_event=1
            else:
                pass
        else:
            # AMC scheduler    
            # Reset skip event. Only stop event will be considered for the AMC scheduler            
            self.skip_event=0

        
        return self.skip_event
    
    
    def stop_condition(self):
        return self.stop_event

    
    def __str__(self):
        print "%s" % self.fname
        print "%s" % self.frmt_header
        print "%s" % self.frmt_msg
        return ""


if __name__ == "__main__":
    
    pass