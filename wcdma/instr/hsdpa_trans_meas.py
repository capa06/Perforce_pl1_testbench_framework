#-------------------------------------------------------------------------------
# Name:        hsdpa_trans_meas
# Purpose:     class for recording HSDPA Transmissions table from CMW500
#
# Author:      joashr
#
# Created:     16/01/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, logging


class hsdpa_trans_meas:
    '''
    Class used as structure to gather hsdpa ack stats from the CMW500
    '''

    def __init__(self, txNum):
        self.trans_num        = str(txNum)
        self.sent             = "-1"
        self.ack              = "-1"
        self.nack             = "-1"
        self.dtx              = "-1"


    def get_trans_num(self):

        return self.trans_num

    def set_results_list(self, reading):
        '''
        set the results for HSDPA ACK measurements
        typically returned by 'FETCh:WCDMa:SIGN:HACK:THRoughput:CARRier<carrier>:ABSolute?'
        '''
        self.sent     = reading[0]
        self.ack      = reading[1]
        self.nack     = reading[2]
        self.dtx      = reading[3]

    def get_list(self):
        meas_list = [self.sent, self.ack, self.nack, self.dtx]
        return meas_list

    def __str__(self):

        try:
            self.sent ='%.3f' % float(self.sent)
        except:
            pass
        try:
            self.ack = '%.3f' % float(self.ack)
        except:
           pass
        try:
            self.nack = '%.3f' % float(self.nack)
        except:
            pass
        try:
            self.dtx = '%.3f' % float(self.dtx)
        except:
            pass

        trans_str = "%18s"   %self.trans_num
        sent_str =  "%15s"   %self.sent
        ack_str  =  "%15s"   %self.ack
        nack_str =  "%15s"   %self.nack
        dtx_str  =  "%15s"   %self.dtx
        result_str = trans_str + sent_str + ack_str + nack_str + dtx_str

        return result_str



if __name__ == '__main__':
    trans_str = "0,9.780000E+001,9.778459E+001,2.215406E+000,0.000000E+000,2.166667E+000,9.846154E+001,1.538462E+000,0.000000E+000,3.333333E-002,1.000000E+002,0.000000E+000,0.000000E+000,0.000000E+000,INV,INV,INV"
    trans_list = trans_str.split(',')
    NUM_MEAS_PER_TX = 4
    trans_meas= [ (-1) for j in range(NUM_MEAS_PER_TX)]
    for idx in range(NUM_MEAS_PER_TX):
        # first transmission is 1 rather than 0 to align
        # with cmw500 display
        trans_meas[idx] = hsdpa_trans_meas(idx+1)

    valid_meas = 0  # denote valid measurement
    transmission_index = 0 # index for hsdpa_trans_meas class
    for idx in range(len(trans_list)):
        if idx == 0:
            # first value is the reliability indicator
            # valid measurement is 0
            valid_meas = trans_list[idx]
            continue
        if ((idx - 1) % NUM_MEAS_PER_TX) == 0:
            # keep getting the next 4 values
            # each set of values correspond to measurements
            # for ecah transmission
            if valid_meas == '0':
                tmpList = trans_list[idx:idx+NUM_MEAS_PER_TX]
                trans_meas[transmission_index].set_results_list(tmpList)
                transmission_index += 1

    # display
    trans_num_str =  "%18s"   % "Transmission [%]"
    sent_str      =  "%15s"   % "Sent"
    ack_str       =  "%15s"   % "ACK"
    nack_str      =  "%15s"   % "NACK"
    dtx_str       =  "%15s"   % "DTX"
    title_str = trans_num_str + sent_str + ack_str + nack_str + dtx_str
    print title_str

    for idx in range(NUM_MEAS_PER_TX):
        print trans_meas[idx]




