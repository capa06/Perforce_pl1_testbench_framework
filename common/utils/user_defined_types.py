#-------------------------------------------------------------------------------
# Name:        user_defined_types
# Purpose:
#
# Author:      joashr
#
# Created:     17/11/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------



# ***************************************************************************
#                          API PUBLIC FUNCTIONS
# ***************************************************************************

# Enum type is not available in python 2.7.x
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


if __name__ == '__main__':
    Numbers  = enum('ZERO', 'ONE', 'TWO')
    print Numbers.ZERO