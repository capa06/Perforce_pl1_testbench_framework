'''
Created on 5 Aug 2013

@author: pl1team
'''

import sys

class cfg_conf(object):
    '''
    Class used as structure to gathe all the information related to the test setup configuration
        ctrlif = {'AT', 'KMT', 'TCPIP', 'STDIN', 'ADB'}
        pwrmeas = { 0=Disable, 1=Enable }
    '''

    def __init__(self, cmwip, ctrlif, pwrmeas, loglevel, test2execute, usimemu,
                 psugwip, psugpib, msglog=0, database=None, remoteDB = 0,
                         remoteDBhost = None, remoteDBuid = None,
                         remoteDBpwd = None, remoteDBname = None):
        '''
        Constructor
        '''
        self.cmwip        = cmwip
        #self.cmwname      = 'cmw500'
        self.ctrlif       = ctrlif
        self.pwrmeas      = pwrmeas
        self.loglevel     = loglevel
        self.test2execute = test2execute
        self.usimemu      = usimemu
        self.psugwip      = psugwip
        self.psugpib      = psugpib
        self.msglog       = msglog
        self.database     = database
        self.remoteDB     = remoteDB
        self.remoteDBhost = remoteDBhost
        self.remoteDBuid  = remoteDBuid
        self.remoteDBpwd  = remoteDBpwd
        self.remoteDBname = remoteDBname

    def __str__(self):

        print "Test Configuration:"
        print "-------------------"
        print "  cmwip        : %s" % self.cmwip
        #print "  cmwname      : %s" % self.cmwname
        print "  ctrlif       : %s" % self.ctrlif
        print "  pwrmeas      : %s" % self.pwrmeas
        print "  loglevel     : %s" % self.loglevel
        print "  test2execute : %s" % self.test2execute
        print "  usimemu      : %s" % self.usimemu
        print "  psugwip      : %s" % self.psugwip
        print "  psugpib      : %s" % self.psugpib
        print "  msglog       : %s" % self.msglog
        print "  database     : %s" % self.database
        print "  remoteDB     : %s" % self.remoteDB
        print "  remoteDBhost : %s" % self.remoteDBhost
        print "  remoteDBuid  : %s" % self.remoteDBuid
        print "  remoteDBname : %s" % self.remoteDBname
   

        return ""

if __name__ == "__main__":
    setup_conf=cfg_conf(cmwip='10.21.1.0', ctrlif='AT', pwrmeas=0, loglevel="INFO",
                        test2execute='[0]', usimemu=0, psugwip='10.22.141.174',
                        psugpib=5, msglog=1, database="c:\\wcdma\\database.db", remoteDB = 0,
                         remoteDBhost = 'testHost;', remoteDBuid = 'testuid',
                         remoteDBpwd = None, remoteDBname = 'testDB')
    print setup_conf


