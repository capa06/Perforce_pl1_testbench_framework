#-------------------------------------------------------------------------------
# Name:        test_config
# Purpose:
#
# Author:      joashr
#
# Created:     23/08/2013
# Copyright:   (c) joashr 2013
#-------------------------------------------------------------------------------

import socket

# jenkins test global variables
SUCCESS = 0
FAIL = 1

"""
prefix_WCCDMA = 'WCDMA_CMW500_'
prefix_LTE    = 'LTE_CMW500_'
test_prefix   = ""

# note that this is the prefix for the STATUS.xxx and
# test verdict files used by Jenkins
def set_testPrefix(RAT=""):
    global test_prefix
    if RAT.upper() == "WCDMA":
        test_prefix ='WCDMA_CMW500_'
    elif RAT.upper() == "LTE":
        test_prefix ='LTE_CMW500_'
    elif RAT.upper() == 'RF':
        test_prefix ='RF_CMW500_'
    else:
        print "Unsupported RAT %s" %RAT
        print "default test prefix is used"
        test_prefix = ""
    #print test_prefix

def get_testPrefix():
    return test_prefix
"""
# for first slave PC, currently UKBLAB-JOASHR-W8LT
psugwip='10.21.140.131'
psugpib=5
cmwip='10.21.141.154'

# for second slave PC, currently JOASH-LT2
psugwip_2='10.21.140.206'
psugpib_2=5
cmwip_2='10.21.141.148'

# for local PC JOASHR-LT
psugwip_3='10.21.140.230'
psugpib_3=5
#cmwip_3='10.21.141.157'
cmwip_3='10.21.141.209'

test_instr = dict()
test_instr={'JOASHR-LT2':{'psugwip':psugwip_2, 'psugpib':psugpib_2, 'cmwip':cmwip_2},
            'UKBLAB-JOASHR-W8LT':{'psugwip':psugwip, 'psugpib':psugpib, 'cmwip':cmwip},
            'JOASHR-LT':{'psugwip':psugwip_3, 'psugpib':psugpib_3, 'cmwip':cmwip_3}}

hostname=socket.gethostname()
#print "hostname : %s" %hostname

def get_psugwip():

    psugwip=test_instr[hostname]['psugwip']
    return psugwip

def get_psugpib():

    psugpib=test_instr[hostname]['psugpib']
    return psugpib

def get_cmwip():

    cmwip=test_instr[hostname]['cmwip']
    return cmwip


#print "psugwip: %s" %get_psugwip()
#print "psugpib: %s" %get_psugpib()
#print "cmwip  : %s" %get_cmwip()



