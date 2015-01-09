'''
Created on 11 Jul 2013

Line.__doc__ <placeholder>
Basic structure pointing to a line (row or column)

@author: fsaracino
'''
from Point import Point
from Line import HLine, VLine


from xlsxwriter.workbook import Workbook


class XLS_HLine(HLine):
    def __init__(self, p0, ncol, value, style):
        HLine.__init__(self, p0, ncol)
        self.value=value
        self.style=style

    def XLS_WriteLine(self, wsheet):
        # Check if merge is required
        if ( self.ncol > 1 ):
            wsheet.merge_range(self.x, self.y, self.x, self.y+self.ncol-1, self.value, self.style)
        else:
            # 1x1 line
            wsheet.write(self.x, self.y, self.value, self.style)


    def __str__(self):
        print "start  : (%d, %d)"    % (self.x, self.y)
        print "nrow     :  %d"       % self.nrow
        print "ncol     :  %d"       % self.ncol
        print "value    :  %s"       % self.value
        print "style    :  %s"       % self.style
        return ""
    
    
    
class XLS_VLine(VLine):
    def __init__(self, p0, nrow, value, style):
        VLine.__init__(self, p0, nrow)
        self.value=value
        self.style=style

    def XLS_WriteLine(self, wsheet):
        
        # Check if merge is required
        if ( self.nrow > 1 ):
            wsheet.merge_range(self.x, self.y, self.x+self.nrow-1,  self.y, self.value, self.style);
        else:
            wsheet.write(self.x, self.y, self.value, self.style)

    def __str__(self):
        print "start  : (%d, %d)"    % (self.x, self.y)
        print "nrow     :  %d"       % self.nrow
        print "ncol     :  %d"       % self.ncol
        print "value    :  %s"       % self.value
        print "style    :  %s"       % self.style
        return ""



class XLS_XLabel(XLS_VLine, XLS_HLine):
    def __init__(self):
        self.label_list=[]



class XLS_YLabel(XLS_VLine, XLS_HLine):
    def __init__(self):
        self.label_list=[]



class XLS_HdrLabel(XLS_VLine, XLS_HLine):
    def __init__(self):
        self.label_list=[]



if __name__ == "__main__":
    pass

