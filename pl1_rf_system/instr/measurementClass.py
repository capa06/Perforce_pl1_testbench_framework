#-------------------------------------------------------------------------------
# Name:        measurementClass.py
# Purpose:     measurement class for cmu and cmw measurements
#
# Author:      joashr
#
# Created:     30/05/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, time, re,  logging

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

import pl1_rf_system_test_env


from pl1_rf_system.common.user_exceptions import *

import pl1_rf_system.common.rf_common_globals as cg

class MeasurementClass(object):

    #PASS = 1
    #FAIL = 0

    PASS = cg.PASS
    FAIL = cg.FAIL

    #verdict_dict = {0:'FAIL', 1:'PASS'}
    verdict_dict = {FAIL:'FAIL', PASS:'PASS'}

    dictKeys = {'NMAU'  :'Underflow of tolerance value not matching, underflow',
                'NMAL'  :'Tolerance value exceeded not matching, overflow',
                'INV'   :'Measurement invalid invalid',
                'OK'    :'Result within the tolerance'}

    dictKeys_Cmw500 = {'ULEU'  : 'User limit violation upper',
                       'ULEL'  : 'User limit violation lower',
                       'OFL'   : 'Overflow',
                       'UFL'   : 'Underflow',
                       'INV'   : 'Invalid',
                       'NAV'   : 'Not Available',
                       'NCAP'  : 'Not Captured'}

    dictKeys.update(dictKeys_Cmw500)

    dictKeysValidLim = {'NMAU' : 'Underflow of tolerance value not matching, underflow',
                        'NMAL' : 'Tolerance value exceeded not matching, overflow',
                        'OK'   : 'Result within the tolerance',
                        'ULEU' : 'User limit violation upper',
                        'ULEL' : 'User limit violation lower'}

    def __init__(self, rowDict, colDict, instrName):

        self.rowDict = rowDict

        self.colDict = colDict

        len_rowDict = len(rowDict)

        len_colDict = len(colDict)

        # extra row for
        # # UE Power Current, Out of Tolerance, Slot Number (WCDMA)#
        # applicable for CMU200 only

        if instrName == "CMW500":
            self.meas_2d_array = [['INV' for x in xrange(len_colDict)]
                                   for x in xrange(len_rowDict)]

            self.limit_2d_array = [['INV' for x in xrange(len_colDict)]
                                   for x in xrange(len_rowDict)]

        else:
            self.meas_2d_array = [['INV' for x in xrange(len_colDict)]
                                   for x in xrange(len_rowDict+1)]

            self.limit_2d_array = [['INV' for x in xrange(len_colDict)]
                                   for x in xrange(len_rowDict+1)]


        self.dummyCharWidth = 20    # dummy column width for meas display
        self.colCharWidth = 15      # standard column width for meas display

        self.rowTemplate = []   # this the mapping for index to row heading

        self.selected_2d_array = []

        self.selected_limit_2d_array =[]

        current_str = "Current"
        average_str = "Average"
        max_min_str = "Max/Min"

        dummyStr     = '{0:<{1}s}'.format('',self.dummyCharWidth)
        col_1_str    = '{0:>{1}s}'.format(current_str,self.colCharWidth)
        col_2_str    = '{0:>{1}s}'.format(average_str,self.colCharWidth)
        col_3_str    = '{0:>{1}s}'.format(max_min_str,self.colCharWidth)

        underline_col_1      = '{0:>{1}s}'.format('='*len(current_str),self.colCharWidth)
        underline_col_2      = '{0:>{1}s}'.format('='*len(average_str),self.colCharWidth)
        underline_col_3      = '{0:>{1}s}'.format('='*len(max_min_str),self.colCharWidth)

        self.col_title_str = dummyStr + col_1_str + col_2_str + col_3_str
        self.underline_str = dummyStr + underline_col_1 + underline_col_2 + underline_col_3

        #self.set_subTestTitle(testDesc)
        self.subTestTitle =""

        self.verdict = "FAIL"


    def set_verdictStr(self, valKey):

        validKeyList = [self.PASS, self.FAIL]

        if valKey not in validKeyList:
            err_msg = ('Invalid verdict, the list of values is %s '
                       %validKeyList)
            raise ExMeas(err_msg)

        self.verdict = self.verdict_dict[valKey]

    def set_meas_2d_array(self, row, listValues=""):

        self.meas_2d_array[row] = listValues


    def set_limit_2d_array(self, row, listValues=""):
        self.limit_2d_array[row] = listValues

    def set_subTestTitle(self, subTestTitle=""):

        # centre the subTestTitle text e.g. ==== DUMMY =====
        subTestTitle = " " + subTestTitle + " "
        len_subTestTitle = len(subTestTitle)
        total_len = len(self.col_title_str)
        first_part_len = (total_len - len_subTestTitle)/2
        last_part_len = total_len - first_part_len - len_subTestTitle
        if len_subTestTitle < total_len:
            title_heading = '{0:>{1}s}{2:>{3}s}{4:>{5}s}'.format('*'*first_part_len, first_part_len,
                                                                 subTestTitle, len_subTestTitle,
                                                                 '*'*last_part_len, last_part_len)
        else:
            title_heading = '{0:>10s}{1:>{2}s}{3:>10s}'.format('*'*10,subTestTitle,len(subTestTitle),'*'*10)

        self.subTestTitle = title_heading


    def get_subTestTitle(self):

        return self.subTestTitle

    def get_meas_2d_array(self):

        return self.meas_2d_array

    def get_limit_2d_array(self):

        return self.limit_2d_array

    def get_selected_limit_2d_array(self):

        return self.selected_limit_2d_array


    def get_dummyCharWidth(self):

        return self.dummyCharWidth

    def get_colCharWidth(self):

        return self.colCharWidth

    def getVerdictStr(self):

        return self.verdict

    def get_col_title_str(self):

        return self.col_title_str


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
                self.set_meas_2d_array(row=rowNum, listValues=tmpList)


        # convert limit check into list
        limit_list = limit_val_list.split(',')
        limit_array = limit_list[0:len_2d_array]

        # populate 2d array for spec limit check measurements
        rowCount = 0
        NUM_MEAS_PER_ROW = 3
        for idx in range(len(limit_array)):
            if idx % NUM_MEAS_PER_ROW == 0:
                tmpList = limit_array[idx:idx+NUM_MEAS_PER_ROW]
                rowNum = idx/NUM_MEAS_PER_ROW
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


    def get_selected_2d_array(self, selectedRowDict):
        """
        gets specific rows from the complete 2d array of measurements
        """
        func_name = sys._getframe(0).f_code.co_name
        loggerMeas = logging.getLogger(__name__ + func_name)
        loggerMeas.debug ("Will try to select row(s) %s from %s row list"
                          %(selectedRowDict.values(),self.rowDict.values()))

        for keys in selectedRowDict.keys():
            if keys not in self.rowDict.keys():
                err_msg = ('selected row index :%s not in the permitted list %s'
                           %(keys,self.rowDict.keys()))
                raise ExMeas(err_msg)


        numrows = len(selectedRowDict.keys())
        numcols = len(self.meas_2d_array[0])
        len_2d_array = numrows * numcols

        self.selected_2d_array = [['INV' for x in xrange(numcols)]
                                   for x in xrange(numrows)]


        self.selected_limit_2d_array = [['INV' for x in xrange(numcols)]
                                         for x in xrange(numrows)]


        # populate selected rows in the 2d results array
        rowIndex = 0
        self.rowTemplate = []
        for row in range(len(self.get_meas_2d_array())):
            if row in selectedRowDict:
                self.selected_2d_array[rowIndex] = self.get_meas_2d_array()[row]
                rowIndex += 1
                self.rowTemplate.append(row)

        loggerMeas.debug (self.selected_2d_array)

        loggerMeas.debug ("Row list extraction successful!")


        # populate 2d array for limit check measurements
        rowIndex = 0
        for row in range(len(self.get_limit_2d_array())):
            if row in selectedRowDict:
                self.selected_limit_2d_array[rowIndex] = self.get_limit_2d_array()[row]
                rowIndex += 1

        return self.selected_2d_array, self.selected_limit_2d_array


    def display_meas(self, type_flag=1):
        """
        type_flag = 0, do not display slot, power and tolerance
        type_flag = 1, display slot, power and tolerance
        from the last row, not applicable for WCDMA overview
        and should be set to 0 in this instance
        """

        print self.get_subTestTitle()

        if type_flag==1:
            self.display_slot_power_tol()


        print self.col_title_str
        print self.underline_str

        invalid_list = []
        rowCount = 0

        for row in self.get_meas_2d_array()[0:-1]:
            rowHeaderStr = '{0:<{1}s}'.format(self.rowDict[rowCount], self.get_dummyCharWidth())
            rowStr =""
            val_idx = 0
            displayStr = ""
            for val in row:
                try:
                    valStr = '%.3f' % float(val)
                except ValueError:
                    valueFieldStr = "%s_%s" %(self.rowDict[rowCount],
                                              self.colDict[val_idx])
                    invalid_list.append(valueFieldStr)
                    valStr = val

                valStr = "%15s" %valStr
                displayStr = displayStr + valStr
                val_idx +=1
            print rowHeaderStr + displayStr

            rowCount +=1

        if invalid_list:
            invalid_str = "Invalid measurements"
            self.print_str_underline(string = invalid_str, char="=")
            for invalid_meas in invalid_list:
                print invalid_meas

        print "\n"

    def display_selected_meas(self):

        print "\n"

        print self.get_subTestTitle()

        print self.col_title_str
        print self.underline_str

        invalid_list = []

        rowCount = 0
        for row in self.selected_2d_array[:]:
            rowHeaderStr = '{0:<{1}s}'.format(self.rowDict[self.rowTemplate[rowCount]], self.get_dummyCharWidth())
            rowStr =""
            displayStr = ""
            val_idx = 0
            for val in row:
                try:
                    valStr = '%.3f' % float(val)
                except ValueError:
                    valueFieldStr = "%s_%s" %(self.rowDict[self.rowTemplate[rowCount]],
                                              self.colDict[val_idx])
                    invalid_list.append(valueFieldStr)
                    valStr = val

                valStr = '{0:>{1}s}'.format(valStr, self.get_colCharWidth())
                displayStr = displayStr + valStr
                val_idx +=1
            print rowHeaderStr + displayStr

            rowCount +=1

        if invalid_list:

            invalid_str = "Invalid measurements"
            self.print_str_underline(string = invalid_str, char="=")

            for invalid_meas in invalid_list:
                print invalid_meas

        print "\n"

    def print_str_underline(self, string, char):
        str_len = len(string)
        print '\n{0:{1}s}'.format(string, str_len)
        print '{0:{1}s}'.format(char*str_len, str_len)
        return

    def display_limit(self):

        print self.col_title_str
        print self.underline_str

        dictLim = {}

        rowCount = 0
        for row in self.get_limit_2d_array():
            rowHeaderStr = '{0:<{1}s}'.format(self.rowDict[rowCount], self.get_dummyCharWidth())
            rowStr =""
            displayStr = ""
            for val in row:
                valStr = val
                valStr = '{0:>{1}s}'.format(valStr, self.get_colCharWidth())
                dictLim[val] = 1
                displayStr = displayStr + valStr
            print rowHeaderStr + displayStr

            rowCount +=1

        data_limit_str = "Data Limit String Codes"

        self.print_str_underline(string=data_limit_str, char="=")
        for key in dictLim.keys():
            print "%s: %s" %(key, self.dictKeys[key])

        print "\n"


    def display_limit_selected_meas(self):

        print self.col_title_str
        print self.underline_str

        dictLim = {}

        rowCount = 0
        for row in self.get_selected_limit_2d_array():
            rowHeaderStr = '{0:<{1}s}'.format(self.rowDict[self.rowTemplate[rowCount]], self.get_dummyCharWidth())
            rowStr =""
            displayStr = ""
            val_idx = 0
            for val in row:
                valStr = val
                valStr = '{0:>{1}s}'.format(valStr, self.get_colCharWidth())
                dictLim[val] = 1
                displayStr = displayStr + valStr
            print rowHeaderStr + displayStr

            rowCount +=1

        data_limit_str = "Data Limit String Codes"

        self.print_str_underline(string=data_limit_str, char="=")
        for key in dictLim.keys():
            print "%s: %s" %(key, self.dictKeys[key])

        print "\n"

    def getTestVerdict(self, array_2d_val):
        """
        get verdict from 2d array values from display_limit_selected_meas or
        display_limit method
        """
        for row in array_2d_val[:]:
            for val in row:
                if val.upper() != "OK":
                    self.set_verdictStr(valKey=self.FAIL)
                    return self.getVerdictStr()

        self.set_verdictStr(valKey=self.PASS)
        return self.getVerdictStr()



    def display_end_title(self):
        print "*" * len(self.col_title_str)
        print "\n"


if __name__ == '__main__':

    from common.enableLogging import enable_logging

    enable_logging(loglevel = "info")

    rowDict_EVM = {0:'EVM_peak', 1:'EVM_rms', 2:'IQ_origin_offset',
                   3:'Carrier_freq_err', 4:'Peak_Code_Dom_err'}
    colDict_EVM = {0:'Current', 1:'Average', 2:'Max/Min'}

    evm = MeasurementClass(rowDict=rowDict_EVM, colDict=colDict_EVM, instrName='cmu200')

    measValues = ("1.221938E+001,9.723330E+000,1.221938E+001,"
                  "3.533220E+000,3.447068E+000,3.542662E+000,"
                  "-4.763864E+001,-4.746898E+001,-4.601485E+001,"
                  "-2.134094E+002,-2.142639E+002,-2.173767E+002,"
                  "-3.469299E+001,-3.516338E+001,-3.452356E+001,"
                  "-8.295995E+000,1.000000E+002,3")


    measValues = ("1.221938E+001,9.723330E+000,1.221938E+001,"
                  "3.533220E+000,3.447068E+000,3.542662E+000,"
                  "-4.763864E+001,-4.746898E+001,-4.601485E+001,"
                  "NAV,-2.142639E+002,-2.173767E+002,"
                  "-3.469299E+001,-3.516338E+001,-3.452356E+001,"
                  "-8.295995E+000,1.000000E+002,3")

    limitValues = "OK,OK,OK,OK,OK,OK,OK,OK,OK,NMAU,NMAU,NMAU,OK,OK,OK"

    evm.populate_2d_array(meas_val_list=measValues, limit_val_list=limitValues)

    #dict_s = {0:'EVM_peak', 3:'Carrier_freq_err'}
    dict_s = {3:'Carrier_freq_err'}
    meas_desc = "EVM Selected Measurements"
    evm.set_subTestTitle(subTestTitle = meas_desc)
    evm.get_selected_2d_array(selectedRowDict=dict_s)
    evm.display_selected_meas()
    evm.display_limit_selected_meas()
    verdictStr = evm.getTestVerdict(array_2d_val=evm.get_selected_limit_2d_array())
    print "%s: %s" %(meas_desc, verdictStr)
    evm.display_end_title()


    evm.set_subTestTitle(subTestTitle = "EVM Full Measurements")
    evm.display_meas()
    evm.display_limit()
    verdictStr = evm.getTestVerdict(array_2d_val=evm.get_limit_2d_array())
    print "%s: %s" %(meas_desc, verdictStr)
    evm.display_end_title()
