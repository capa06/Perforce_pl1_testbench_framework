'''
Created on 11 Aug 2013

@author: fsaracino
'''

import os, sys

import pl1_rf_system.test_env


from common.report.xls.Point import Point
from common.report.xls.Line import HLine, VLine
from common.report.xls.XLS_Line import XLS_VLine, XLS_HLine, XLS_XLabel, XLS_YLabel, XLS_HdrLabel

from xlsxwriter.workbook import Workbook

def Csv2Xls(fname_src, figure_params=[], layout_params=[]):

    """
      Convert  CSV report (PERF test) to XLS file
    """

    if not os.path.isfile(fname_src):
        print("WARNING::Csv2Xls_PERF():: File %s not found. XLS report generation skipped")
        return(1,'')
    fname_dst=os.path.splitext(fname_src)[0]+'.xlsx'

    # Open XLS structures
    wb = Workbook(fname_dst)
    ws = wb.add_worksheet('Measurements')
    label_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : True,  'border' : 1, 'align' : 'left', 'valign'  : 'vcenter', 'color': 'white', 'fg_color' : '#098529' })
    entry_merged_format_hdr= wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'left', 'valign'  : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })
    entry_merged_format    = wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'center', 'valign'  : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })

    #entry_format       =wb.add_format({'size':9, 'italic' : False, 'bold' : False, 'border' : 1, 'align' : 'center', 'valign'  : 'vcenter', 'color': 'black', 'fg_color' : '#FFFFFF' })

    # Oper SRC and DST files
    with open(fname_src, 'r') as fd_src:
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

    #TODO: use a predefined layout
    if figure_params:
        ws1 = wb.add_worksheet('Figures')
        if not layout_params:
            # Insert plots without any layout
            row_offs=20
            col_offs=0
            for idx in range(len(figure_params)):
                row=idx*row_offs
                col=col_offs
                ws1.insert_image(row, col, figure_params[idx], {'x_offset': 0, 'y_offset': 0, 'x_scale': 0.60, 'y_scale': 0.64})
        else:
            # Insert plots using the specified layout
            row_offs=20
            col_offs=8
            MAX_TM=4
            for idx in range(len(layout_params)):
                nx=layout_params[idx][0]
                ny=layout_params[idx][1]
                nz=layout_params[idx][2]
                row=(nx*MAX_TM+nz)*row_offs
                col=ny*col_offs
                ws1.insert_image(row, col, figure_params[idx], {'x_offset': 0, 'y_offset': 0, 'x_scale': 0.60, 'y_scale': 0.64})

    # Close and save the workbook
    wb.close()

    return(0, fname_dst)

if __name__ == '__main__':
    pass
