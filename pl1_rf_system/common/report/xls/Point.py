'''
Created on 11 Jul 2013

Point.__doc__ <placeholder>
Basic structure pointing to a single cell

@author: fsaracino
'''

class Point(object):
    '''
    '''
        
    def __init__(self, x0, y0):
        self.x = x0
        self.y = y0
    
    def AddPoint (self, v):
        self.x += v.x
        self.y += v.y

    def SetPoint (self, p):
        self.x = p.x
        self.y = p.y
        
    def GetPoint (self):
        return (self.x, self.y)
        
    def __str__(self):
        return "<%s => (%d, %d)>" % (self.__class__.__name__, self.x, self.y)
    
if __name__ == "__main__":
	pass
	
     
     
      

