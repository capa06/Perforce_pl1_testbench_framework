#-------------------------------------------------------------------------------
# Name:        user_exceptions
# Purpose:
#
# Author:      joashr
#
# Created:     02/04/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

class ExGeneral(Exception):
    def __init__(self, message):
        self.message = message

class ExCmu200(ExGeneral):
    pass

class ExCmw500(ExGeneral):
    pass

class ExFail(ExGeneral):
    pass

class ExCmw(ExGeneral):
    pass

class ExMeas(ExGeneral):
    pass

class ExModem(ExGeneral):
    pass

class ExUtilities(ExGeneral):
    pass

class ExTestPlan(ExGeneral):
    pass

class ExCfgTest(ExGeneral):
    pass

class ExRunTest(ExGeneral):
    pass

class ExUserBreakPoint(ExGeneral):
    pass


class MyException(Exception):
    def __init__(self, tries=0):
        self.numtries = tries

if __name__ == '__main__':

    if __name__ == '__main__':
        try:
            raise ExCmu200('Cmu Exception Test Message')

        except ExGeneral, e:
            print '%s' %e.message

        else:
            print 'No exception'

        try:
            raise ExModem('Modem Exception Test Message')

        except ExGeneral, e:
            print '%s' %e.message

