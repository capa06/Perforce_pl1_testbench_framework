'''
Created on 11 Aug 2013

@author: fsaracino
'''


# ********************************************************************
# IMPOORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
import re
from xlsxwriter.workbook import Workbook

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


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'xls']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from Point import Point
from Line import HLine, VLine
from XLS_Line import XLS_VLine, XLS_HLine, XLS_XLabel, XLS_YLabel, XLS_HdrLabel


# ********************************************************************
# GLOBAL OBJECTS
# ********************************************************************
def csv2XlsLte(file_conf, file_meas):    
    file_xls=os.path.splitext(file_meas)[0]+'.xlsx'
    report_xls_h = Csv2XlsLte(file_xls)
    report_xls_h.csv2xls(file_conf, file_meas)
    del report_xls_h


class Csv2XlsLte(object):
    def __init__(self, file_xls):
        self.file_xls = file_xls
        
    def csv2xls(self, file_conf, file_meas):
        logger=logging.getLogger('csv2XlsLte')
      
        """
          Convert  CSV report (PERF test) to XLS file 
        """
        if not os.path.isfile(file_conf):
            logger.warning("XLS report generation skipped. File %s not found: %s" % file_conf)
            return -1
        
        if not os.path.isfile(file_meas):
            logger.warning("XLS report generation skipped. File %s not found: %s" % file_meas)
            return -1
        
        # Set XLS file name
        file_xlsx=os.path.splitext(file_meas)[0]+'.xlsx'
        logger.debug("Creating file report : %s" % file_xlsx)
        
        # Open XLS structures
        wb = Workbook(file_xlsx)
        ws = wb.add_worksheet('Measurements')
        label_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : True,  'border' : 1, 'align' : 'left', 'valign'   : 'vcenter', 'color': 'white', 'fg_color' : '#098529' })
    #    entry_merged_format_hdr= wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'left', 'valign'   : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
        entry_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'center', 'valign' : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
        entry_format           = wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 0, 'align' : 'left',  'valign'  : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
    
        line_idx=0
    
        # Convert configuration file
        with open(file_conf, 'r') as fd_conf:
            conf=fd_conf.read()
            conf=re.sub(r'[,]+', r' ', conf)
            xlsline_l=['Test configuration:']
            for j in range(len(xlsline_l)):
                hlabel=XLS_HLine(Point(line_idx, 0), 10, xlsline_l[j], label_merged_format)
                hlabel.XLS_WriteLine(ws)
                del hlabel
            line_idx += 1
            xlsline_l=[re.sub(r'[,]+', r' ', conf)]
            for j in range(len(xlsline_l)):
                hentry=XLS_HLine(Point(line_idx, 0), 10, xlsline_l[j], entry_format)
                hentry.XLS_WriteLine(ws)
                del hentry
            line_idx += 1               
        fd_conf.close()
    
        # Convert measurement file
        with open(file_meas, 'r') as fd_meas:    
            state=1             #  1: entry header, 2:entry 
            while True:
                line=fd_meas.readline() 
                if line == "" : break
                line_l=line.split(',') 
                if state==1:
                    xlsline_l=line_l
                    # Move values to the worksheet    
                    for j in range(len(xlsline_l)):
                        hlabel=XLS_HLine(Point(line_idx,j), 1, xlsline_l[j], label_merged_format)
                        hlabel.XLS_WriteLine(ws)
                        del hlabel                    
                    # Switch to next state
                    state=2
                else:
                    xlsline_l=line_l   
                    for j in range(len(xlsline_l)):
                        hentry=XLS_HLine(Point(line_idx,j), 1, xlsline_l[j], entry_merged_format)
                        hentry.XLS_WriteLine(ws)
                        del hentry
                line_idx += 1
        fd_meas.close()
                   
        # Close and save the workbook
        wb.close()
           
        return 0



if __name__ == '__main__':
    pass
