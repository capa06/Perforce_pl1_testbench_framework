'''
Created on 11 Jul 2013

Line.__doc__ <placeholder>
Basic structure pointing to a line (row or column)

@author: fsaracino
'''
from Point import Point

class Line(Point):
    '''
    classdocs
    '''
    def __init__(self, p0, nrow, ncol):
        Point.__init__(self, p0.x, p0.y)
        self.nrow  = nrow
        self.ncol  = ncol
                
    def __str__(self):
        return  "<%s> : start=(%d, %d), nrow=%d, ncol=%d"    % (self.__class__.__name__, self.x, self.y, self.nrow, self.ncol)


#*************************************************************
# Note: use the following specialised classes to define a line
#*************************************************************

class HLine(Line):
    def __init__(self, p0, ncol):
        Line.__init__(self, p0, 1, ncol)


            
class VLine(Line):
    def __init__(self, p0, nrow):
        Line.__init__(self, p0, nrow, 1)


if __name__ == "__main__":
    pass
