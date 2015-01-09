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
from xlsxwriter.workbook import Workbook

# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass


# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************


# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))


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
def csv2Xls(file_csv):
    logger=logging.getLogger('csv2Xls')
  
    """
      Convert  CSV report (PERF test) to XLS file 
    """

    if not os.path.isfile(file_csv):
        print("WARNING::Csv2Xls_PERF():: File %s not found. XLS report generation skipped")
        return(1,'')

    
    file_xlsx=os.path.splitext(file_csv)[0]+'.xlsx'
    logger.debug("Creating file report : %s" % file_xlsx)
    
    
    # Configure logging

    # Open XLS structures
    wb = Workbook(file_xlsx)
    ws = wb.add_worksheet('Measurements')
    label_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : True,  'border' : 1, 'align' : 'left', 'valign'   : 'vcenter', 'color': 'white', 'fg_color' : '#098529' })
    entry_merged_format_hdr= wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'left', 'valign'   : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
    entry_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'center', 'valign' : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })

    #entry_format       =wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'center', 'valign'  : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
          
    # Oper SRC and DST files
    with open(file_csv, 'r') as fd_src:    
        line_idx=0
        state=0             # 0: header, 1: entry header, 2:entry 
        while True:
            line=fd_src.readline() 
            if line == "" : break
            line_l=line.split(',')
            if line_l[0] == 'TESTID':
                state=1
            
            if state==0:
                # Save header                
                hlabel=XLS_HLine(Point(line_idx,0), 2, line_l[0].upper(), label_merged_format)
                hlabel.XLS_WriteLine(ws)
                hentry=XLS_HLine(Point(line_idx,2), 7, line_l[1].upper(), entry_merged_format_hdr)
                hentry.XLS_WriteLine(ws)
                del hlabel, hentry
            
            elif state==1:
                xlsline_l=line_l
                # Move values to the worksheet    
                for j in range(len(xlsline_l)):
#                    hlabel=XLS_HLine(Point(line_idx,j), 1, xlsline_l[j].upper(), label_merged_format)
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
                        
    # Close and save the workbook
    wb.close()
       
    return(0, file_xlsx)



if __name__ == '__main__':
    
    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
    
    