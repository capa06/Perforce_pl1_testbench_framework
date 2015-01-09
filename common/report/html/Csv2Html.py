'''
Created on 11 Aug 2013

@author: fsaracino
'''

import logging, os


def HtmlHead(fd):
    """
      Configure the HTML document down to the BODY level
    """
    fd.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n')
    fd.write('<HTML>\n')

    # HEAD and STYLE
    fd.write('\t<HEAD>\n')
    fd.write('\t\t<TITLE>Tab Title</TITLE>\n')
    fd.write('<META name="author" content="fsaracino@nvidia.com">\n')
    fd.write('<META name="copyright" content="&copy; 2013 NVIDIA LTD">\n')
    fd.write('<META name="keywords" content="pl1testbench,LTE,PL1">\n')
    fd.write('<META name="date" content="2013-10-27T08:49:37+00:00">\n')

    fd.write('\t\t<STYLE>\n')
    fd.write('\t\t\t   BODY {  background: #FFFFFF; color: #000000}\n')
    fd.write('\t\t\t      H1 {  border:   2px solid #000000; font-style: italic; font-size : 18pt; color: #000000;  text-align: center}\n')
    fd.write('\t\t\t      P {  border:  0px solid #FFFFFF; font-style: italic; font-size : 14pt; color: #000000;  text-align: left}\n')
    fd.write('\t\t\t  TABLE {  border:  1px solid #000000; border-collapse: collapse; cellspacing :"2"; cellpadding : "4"}\n')
    fd.write('\t\t\t CAPTION {  font-style: italic; font-size : 10pt; color: #FF0000;  text-align: left}\n')
    fd.write('\t\t\t   THEAD {  font-style: italic; font-size :  8pt; color: #0000FF}\n')
    fd.write('\t\t\t   TFOOT {  font-style: italic; font-size :  8pt; color: #0000FF}\n')

    fd.write('\t\t\t     TH {  border:  1px solid #000000; font-style: bold; font-size :  9pt; color: #FFFFFF;  text-align: left;  background: #009325 }\n')
    fd.write('\t\t\t     TD {  border:  1px solid #000000; font-style: bold; font-size :  9pt; color: #000000;  text-align: left }\n')
    fd.write('\t\t</STYLE>\n')
    fd.write('\t</HEAD>\n')

    fd.write('\t<BODY>\n')


def HtmlAddSection(fd, stype, descr, level=2):
    stype_l=['H1', 'P']

    if not stype in stype_l:
        logging.error("Invalid section type : %s. Nothing to do" % stype)
        return 1

    if not stype in ['H1']:
        msg=('\t'*level+'<HR>\n')
        fd.write(msg)

    msg=('\t'*level+'<%s>%s</%s>\n'%(stype, descr, stype))
    fd.write(msg)


def HtmlOpenTable(fd, summary, width=400, level=2):
    msg=('\t'*level+'<TABLE summary="%s"; width=%s>\n'%(summary, width))
    fd.write(msg)


def HtmlCloseTable(fd, level=2):
    msg=('\t'*level+'</TABLE>\n')
    fd.write(msg)


def HtmlAddEntry(fd, entrytype, entry_l, level=2):

    entrytype_l = ['TagVal', 'Header', 'Data']

    if not entrytype in entrytype_l:
        logging.error("Invalid entry type : %s. Nothing to do" % entrytype)
        return 1

    if entrytype=='TagVal':
        msg=('\t'*level+'<TR>\n')
        fd.write(msg)
        msg=('\t'*(level+1)+'<TH>%s</TH>\n' % entry_l[0])
        fd.write(msg)
        msg=('\t'*(level+1)+'<TD>%s</TD>\n' % entry_l[1].replace('\r','<BR>'))
        fd.write(msg)
        msg=('\t'*level+'</TR>\n')
        fd.write(msg)

    elif entrytype=='Header':
        msg=('\t'*level+'<TR>\n')
        fd.write(msg)
        for j in range(len(entry_l)):
            msg=('\t'*(level+1)+'<TH>%s</TH>\n' % entry_l[j])
            fd.write(msg)
        msg=('\t'*level+'</TR>\n')
        fd.write(msg)

    elif entrytype=='Data':
        msg=('\t'*level+'<TR>\n')
        fd.write(msg)
        for j in range(len(entry_l)):
            msg=('\t'*(level+1)+'<TD>%s</TD>\n' % entry_l[j])
            fd.write(msg)
        msg=('\t'*level+'</TR>\n')
        fd.write(msg)
    else:
        pass



def HtmlBody(fd):
    # H1
    fd.write('\t\t<H1>CMW500 PL1 Test Report</H1>\n')
    fd.write('\t\t<HR>\n')

    # P: Description
    fd.write('\t\t<P>Description:</P>\n')
    fd.write('\t\t<HR>\n')

    # P: Configuration
    fd.write('\t\t<P>Configuration:</P>\n')
    fd.write('\t\t<HR>\n')

    # P: Measurements
    fd.write('\t\t<P>Measurements:</P>\n')
    fd.write('\t\t<HR>\n')

    # P: Results
    fd.write('\t\t<P>Result:</P>\n')
    fd.write('\t\t<HR>\n')

def HtmlTail(fd):
    fd.write('\t</BODY>\n')
    fd.write('</HTML>\n')


def Csv2Html(fname_src, figure_params=[], layout_params=[]):

    """
      Convert  CSV report (PERF test) to HTML file
    """

    if not os.path.isfile(fname_src):
        logging.error("WARNING::Csv2Html():: File %s not found. HTML report generation skipped")
        return(1,'')

    # Build HTML file destination name
    fname_dst=os.path.splitext(fname_src)[0]+'.html'
    fd_dst= open(fname_dst, 'w')

    HtmlHead(fd_dst)
    HtmlAddSection(fd_dst, 'H1', 'PL1 Test Report', 2)

    # Oper SRC and DST files
    with open(fname_src, 'r') as fd_src:
        line_idx=0
        state=0                         # 0: header, 1: entry header, 2:entry

        HtmlAddSection(fd_dst, 'P', 'Test Configuration', 2)

        HtmlOpenTable(fd_dst, summary="Test Summary", width=1000, level=2)

        while True:
            line=fd_src.readline()
            if line == "" : break
            line_l=line.split(',')
            if line_l[0] == 'TESTID':
                state=1

                HtmlCloseTable(fd_dst, level=2)

                HtmlAddSection(fd_dst, 'P', 'Measurements', 2)
                HtmlOpenTable(fd_dst, summary="Test Measurements", width=3000, level=2)

            if state==0:
                # Summary information in TagVal format
                #print line_l
                HtmlAddEntry(fd_dst, entrytype='TagVal', entry_l=line_l, level=3)

            elif state==1:
                HtmlAddEntry(fd_dst, entrytype='Header', entry_l=line_l, level=3)
                state=2
            else:
                HtmlAddEntry(fd_dst, entrytype='Data', entry_l=line_l, level=3)

            line_idx += 1

        # EOF, close the measurements table
        HtmlCloseTable(fd_dst, level=2)

    #TODO: use a predefined layout
#    if figure_params:
#        ws1 = wb.add_worksheet('Figures')
#        if not layout_params:
#            # Insert plots without any layout
#            row_offs=20
#            col_offs=0
#            for idx in range(len(figure_params)):
#                row=idx*row_offs
#                col=col_offs
#                ws1.insert_image(row, col, figure_params[idx], {'x_offset': 0, 'y_offset': 0, 'x_scale': 0.60, 'y_scale': 0.64})
#        else:
#            # Insert plots using the specified layout
#            row_offs=20
#            col_offs=8
#            MAX_TM=4
#            for idx in range(len(layout_params)):
#                nx=layout_params[idx][0]
#                ny=layout_params[idx][1]
#                nz=layout_params[idx][2]
#                row=(nx*MAX_TM+nz)*row_offs
#                col=ny*col_offs
#                ws1.insert_image(row, col, figure_params[idx], {'x_offset': 0, 'y_offset': 0, 'x_scale': 0.60, 'y_scale': 0.64})
#
    HtmlTail(fd_dst)

    fd_src.close()
    fd_dst.close()

    return(0, fname_dst)



if __name__ == '__main__':
	pass


