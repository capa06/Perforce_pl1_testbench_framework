#-------------------------------------------------------------------------------
# Name:        verdict.py
# Purpose:     class for recodin the test verdict
#
# Author:      joashr
#
# Created:     11/06/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import rf_common_globals as rf_global

class Verdict(object):
    """
    Class to assist setting verdict of test scripts correctly.
    To get a consistent ID numbering of checks, make sure that
    the same number of checks are always done regardless of script parameter settings
    """
    def __init__(self):
        self.FAIL_flag = False
        self.FAIL_info_list = []
        self.PASS_flag = False
        self.PASS_info_list = []
        self.ERROR_flag = False
        self.ERROR_list = []

    def _CreateListItem(self, meas_id="", info=""):
        item_dict = dict()
        item_dict["ID"] = meas_id
        item_dict["Info"]=info
        return item_dict

    def _PrintList(self, item_dict_list):
        for item in item_dict_list:
            space = "   "
            print " # %-80s:\t%-10s" % (item["ID"], item["Info"])

    def PrintFailed (self):
        self._PrintList(self.FAIL_info_list)

    def PrintPassed (self):
        self._PrintList(self.PASS_info_list)

    def PrintErrors (self):
        for err in self.ERROR_list:
            print " # %-60s" % err

    def RecordError (self,error=""):
        self.ERROR_flag = True
        self.ERROR_list.append(error)

    def CheckFailed(self, info="", meas_id=""):
        self.FAIL_flag = True
        item_dict=self._CreateListItem(meas_id=meas_id, info=info)
        self.FAIL_info_list.append(item_dict)
        # print "CheckFailed info=%s, meas_id=%s" % (info, meas_id)
        # exit(0)

    def CheckPassed(self, info="", meas_id=""):
        self.PASS_flag = True
        item_dict=self._CreateListItem(info=info, meas_id=meas_id)
        self.PASS_info_list.append(item_dict)

    def Check(self, P = True, info="", meas_id=""):
        item_dict=self._CreateListItem(info=indo, meas_id=meas_id)
        if P: # PASS
            self.PASS_flag = True
            self.PASS_info_list.append(item_dict)
        else:
            self.FAIL_flag = True
            self.FAIL_info_list.append(item_dict)

    def _PrintHeading(self, text, total_heading_len):
        len_text = len(" " + text + " ")
        first_part_len = (total_heading_len - len_text)/2
        last_part_len = total_heading_len - first_part_len - len_text
        if len_text < total_heading_len:
            title_heading = '{0:>{1}s}{2:>{3}s}{4:>{5}s}'.format(' '*first_part_len, first_part_len,
                                                                 text, len_text,
                                                                 ' '*last_part_len, last_part_len)
        else:
            title_heading = '{0:>10s}{1:>{2}s}{3:>10s}'.format('*'*10,text,len(text),'*'*10)

        print "\n" + "*"*total_heading_len
        print title_heading
        print "*"*total_heading_len


    def GetSummaryVerdict(self, col_len):

        if self.PASS_flag == False and self.FAIL_flag == False:
            text = 'TEST VERDICT: INCONCLUSIVE'
            self._PrintHeading(text=text, total_heading_len=col_len)
            return rf_global.verdict_dict[rf_global.INCONC]

        elif self.PASS_flag == False and self.FAIL_flag == True:
            text = "TEST VERDICT: FAIL (all checks failing)"
            self._PrintHeading(text=text, total_heading_len=col_len)
            self._PrintList(self.FAIL_info_list)
            print "\n\n"
            return rf_global.verdict_dict[rf_global.FAIL]

        elif self.PASS_flag == True and self.FAIL_flag == False:
            text = "TEST VERDICT: PASS (all checks passing)"
            self._PrintHeading(text=text, total_heading_len=col_len)
            self._PrintList(self.PASS_info_list)
            print "\n\n"
            return rf_global.verdict_dict[rf_global.PASS]

        elif self.PASS_flag == True and self.FAIL_flag == True:
            text = "TEST VERDICT: FAIL (but some checks passing)"
            self._PrintHeading(text=text, total_heading_len=col_len)
            print "\nFailing checks:"
            print "---------------"
            self._PrintList(self.FAIL_info_list)
            print "\nPassing checks:"
            print "---------------"
            self._PrintList(self.PASS_info_list)
            print "\n\n"
            return rf_global.verdict_dict[rf_global.FAIL]


if __name__ == '__main__':

        verdictObj = Verdict()
        verdictObj.GetSummaryVerdict(col_len = 40)