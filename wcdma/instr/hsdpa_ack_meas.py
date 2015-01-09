#-------------------------------------------------------------------------------
# Name:        hsdpa_ack_meas
# Purpose:     class for recording HSDPA ACK stats from CMW500
#
# Author:      joashr
#
# Created:     16/01/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, logging

class hsdpa_ack_meas:
    '''
    Class used as structure to gather hsdpa ack stats from the CMW500
    '''

    def __init__(self, carrier=1):
        self.reliability      = "-1"      # Min Tput
        self.absCurrent       = "-1"      # Current Tput
        self.absMaximum       = "-1"      # Max possible Tput
        self.absMinimum       = "-1"      # Min Tput
        self.absScheduled     = "-1"      # Scheduled Tput
        self.maxPossible      = "-1"      # Max possible Tput
        self.absTotalCurrent  = "-1"      # Current Tput - sum of both carriers
        self.totalMaxPos      = "-1"      # Max possible Tput - sum of both carriers
        self.absTotalAverage  = "-1"      # Average Tput calxulated from a sum of both carriers
        self.absAverage       = "-1"      # Average Tput
        self.carrier          = carrier

    def set_results_list(self, reading):
        '''
        set the results for HSDPA ACK measurements
        typically returned by 'FETCh:WCDMa:SIGN:HACK:THRoughput:CARRier<carrier>:ABSolute?'
        '''

        self.reliability     = reading[0]
        self.absCurrent      = reading[1]
        self.absMaximum      = reading[2]
        self.absMinimum      = reading[3]
        self.absScheduled    = reading[4]
        self.maxPossible     = reading[5]
        self.absTotalCurrent = reading[6]
        self.totalMaxPos     = reading[7]
        self.absTotalAverage = reading[8]
        self.absAverage      = reading[9]

    def get_avgTputMbps(self):
        avgTputMbps = float(self.absAverage)/1000000
        avgTputMbps = '%.3f' % float(avgTputMbps)
        return avgTputMbps

    def get_maxTputMbps(self):
        maxTputMbps = float(self.absMaximum)/1000000
        maxTputMbps = '%.3f' % float(maxTputMbps)
        return maxTputMbps

    def __str__(self):
        titleStr = "CMW500 HSDPA ACK stats" + " for carrier %s:" %self.carrier
        print ""
        print titleStr
        print "-------------------------------------"
        print "  Reliability                   : %s"   % self.reliability
        print "  Current Tput                  : %s"   % self.absCurrent
        print "  Max Tput                      : %s"   % self.absMaximum
        print "  Min Tput                      : %s"   % self.absMinimum
        print "  Scheduled Tput                : %s"   % self.absScheduled
        print "  Max possible Tput             : %s"   % self.maxPossible
        print "  Current Tput - sum carriers   : %s"   % self.absTotalCurrent
        print "  Max Tput - sum carriers       : %s"   % self.totalMaxPos
        print "  Avg Tput - sum carriers       : %s"   % self.absTotalAverage
        print "  Avg Tput                      : %s"   % self.absAverage

        return ""

if __name__ == '__main__':
    hsdpa_ack_meas = hsdpa_ack_meas()
    print hsdpa_ack_meas
