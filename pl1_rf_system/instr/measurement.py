#-------------------------------------------------------------------------------
# Name:        measurement
# Purpose:     measurement class for cmu measurements
#
# Author:      joashr
#
# Created:     30/05/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


class measurement(object):

    def __init__(self, rowDict, colDict):

        self.rowDict = rowDict

        self.colDict = colDict

        len_rowDict = len(rowDict)

        len_colDict = len(colDict)

        self.meas_2d_array = [['INV' for x in xrange(len_colDict+1)]
                               for x in xrange(len_rowDict+1)]

        self.limit_2d_array = [['INV' for x in xrange(len_colDict)]
                               for x in xrange(len_rowDict)]



    def set_meas_2d_array(self, row, listValues=""):

        self.meas_2d_array[row] = listValues


    def set_limit_2d_array(self, row, listValues=""):

        self.limit_2d_array[row] = listValues

    def get_meas_2d_array(self):

        return self.meas_2d_array

    def get_limit_2d_array(self):

        return self.limit_2d_array


    def populate_2d_array(self, meas_val_list="", limit_val_list=""):
        """
        val_list is the raw list of comma separated measurement values from the
        test equipment, these values are used to populate 2d array
        """

        numrows = len(self.meas_2d_array)
        numcols = len(self.meas_2d_array[0])
        len_2d_array = numrows * numcols

        # convert evm measurements into list
        meas_list = meas_val_list.split(',')
        meas_array = meas_list[0:len_2d_array]

        # populate 2d array for evm measurements
        rowCount = 0
        NUM_MEAS_PER_ROW = 3
        for idx in range(len(meas_array)):
            if idx % NUM_MEAS_PER_ROW == 0:
                tmpList = meas_array[idx:idx+NUM_MEAS_PER_ROW]
                rowNum = idx/NUM_MEAS_PER_ROW
                #meas_2d_array[rowNum] = tmpList
                self.set_meas_2d_array(row=rowNum, listValues=tmpList)


        # convert limit check into list
        limit_list = limit_val_list.split(',')
        limit_array = limit_list[0:len_2d_array]

        # populate 2d array for limit check measurements
        rowCount = 0
        NUM_MEAS_PER_ROW = 3
        for idx in range(len(limit_array)):
            if idx % NUM_MEAS_PER_ROW == 0:
                tmpList = limit_array[idx:idx+NUM_MEAS_PER_ROW]
                rowNum = idx/NUM_MEAS_PER_ROW
                #evm_limit_2d_array[rowNum] = tmpList
                self.set_limit_2d_array(row=rowNum, listValues=tmpList)


    def display_slot_power_tol(self):
        """
        UE Power Current, Out of Tolerance, Slot Number (WCDMA)
        """

        # get the last row in 2d array corresponding to
        # UE Power Current, Out of Tolerance, Slot Number (WCDMA)
        (power, tol, slot_num) = self.get_meas_2d_array()[-1]

        power = '%.2f' % float(power)
        tol = '%.1f' % float(tol)
        slot_num = int(slot_num)

        print "\n"
        print "Slot Number       : %6s     "    % slot_num
        print "UE Power          : %6s dBm "    % power
        print "Out of Tolerance  : %6s %%  "    % tol


    def display_meas(self):

        self.display_slot_power_tol()

        dummyStr        =  "%-20s"   % ""
        current_str     =  "%15s"    % "Current"
        average_str     =  "%15s"    % "Average"
        max_min_str     =  "%15s"    % "Max/min"

        title_str = dummyStr + current_str + average_str + max_min_str

        print title_str

        invalid_list = []
        rowCount = 0

        for row in self.get_meas_2d_array()[0:-1]:
            rowHeaderStr = "%-20s"    %self.rowDict[rowCount]
            rowStr =""
            displayStr = ""
            for val in row:
                try:
                    valStr = '%.3f' % float(val)
                except ValueError:
                    valueFieldStr = "%s_%s" %(self.rowDict[rowCount],
                                              self.colDict[rowCount])
                    invalid_list.append(valueFieldStr)
                    valStr = val

                valStr = "%15s" %valStr
                displayStr = displayStr + valStr
            print rowHeaderStr + displayStr

            rowCount +=1

        print "\n"

        if invalid_list:
            for invalid_meas in invalid_list:
                print invalid_meas

    def display_limit(self):

            dummyStr        =  "%-20s"   % ""
            current_str     =  "%15s"    % "Current Limit"
            average_str     =  "%15s"    % "Average Limit"
            max_min_str     =  "%15s"    % "Max/min Limit"

            title_str = dummyStr + current_str + average_str + max_min_str
            print title_str

            dictLim = {}
            dictKeys = {'NMAU':'Underflow of tolerance value not matching, underflow',
                        'NMAL':'Tolerance value exceeded not matching, overflow',
                        'INV' :'Measurement invalid invalid',
                        'OK'  :'Result within the tolerance'}

            rowCount = 0
            for row in self.get_limit_2d_array():
                rowHeaderStr = "%-20s"    %self.rowDict[rowCount]
                rowStr =""
                displayStr = ""
                for val in row:
                    valStr = val
                    valStr = "%15s" %valStr
                    dictLim[val] = 1
                    displayStr = displayStr + valStr
                print rowHeaderStr + displayStr

                rowCount +=1

            banner = "=" * 45
            print "%-20s%s" %("Data Limit Key", banner)
            for key in dictLim.keys():
                print "%s: %s" %(key, dictKeys[key])
            print "\n"


if __name__ == '__main__':

    rowDict_EVM = {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',
                   3:'Carrier_freq_err', 4:'Peak_Code_Dom_err'}
    colDict_EVM = {0:'Current', 1:'Average', 2:'Max/Min'}

    evm = measurement(rowDict=rowDict_EVM, colDict=colDict_EVM)

    measValues = ("1.221938E+001,9.723330E+000,1.221938E+001,"
                  "3.533220E+000,3.447068E+000,3.542662E+000,"
                  "-4.763864E+001,-4.746898E+001,-4.601485E+001,"
                  "-2.134094E+002,-2.142639E+002,-2.173767E+002,"
                  "-3.469299E+001,-3.516338E+001,-3.452356E+001,"
                  "-8.295995E+000,1.000000E+002,3")

    limitValues = "OK,OK,OK,OK,OK,OK,OK,OK,OK,NMAU,NMAU,NMAU,OK,OK,OK"

    evm.populate_2d_array(meas_val_list=measValues, limit_val_list=limitValues)

    evm.display_meas()

    evm.display_limit()

