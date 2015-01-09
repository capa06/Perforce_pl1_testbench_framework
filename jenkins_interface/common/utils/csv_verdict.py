'''
Created on 13 Feb 2014

@author: joashr
'''


import os, sys, shutil, ntpath, re, traceback

fpath = os.path.dirname(os.path.abspath(__file__))

try:
    import test_env
except ImportError:
    test_env_dir=os.sep.join(fpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec

def writeVerdictFile(verdict="PASS", descr="PASS",
                     filenamePrefix='', testVerdictDir=""):
    """
    create sSTATUS_xxx.txt file and testVerdict.csv file
    and copy these from ..\pl1_jenkins\results\current\--- to
    destinationPath directory
    filenamePrefix) is the prefix to be added to the various cvs and html reports
    """
    csv_report=CsvJenkinsVerdict(filenamePrefix,
                                 testVerdictDir=testVerdictDir)
    csv_report.write(verdict = verdict, desc=descr)

    # always remove current status file, if any, before
    # creating a new one, this ensures that there is only
    # one status file
    csv_report.removeStatusFileFromSource()
    csv_report.removeStatusFileFromDestination(dst_path=testVerdictDir)
    statusFileName = csv_report.createStatusFile(verdict=verdict)


def removeVerdictFile(filenamePrefix='', testVerdictDir=""):
    csv_report=CsvJenkinsVerdict(filenamePrefix=filenamePrefix, testVerdictDir=testVerdictDir)
    csv_report.remove()


class CsvJenkinsVerdict(object):
    '''
    classdocs
    '''
    verdict={ 0:'PASS', 1:'FAIL', 2:'INVALID'}

    def __init__(self, filenamePrefix='', testVerdictDir=""):

        self.filenamePrefix = filenamePrefix

        if self.filenamePrefix == '':
            self.csvVerdictFileName = 'testVerdict.csv'
        else:
            self.csvVerdictFileName = self.filenamePrefix + '_' + 'testVerdict.csv'

        fpath = os.path.dirname(os.path.abspath(__file__))

        self.testVerdictDir = testVerdictDir

        if testVerdictDir:
            csv_abs_f = os.sep.join(self.testVerdictDir.split(os.sep)[:]+[self.csvVerdictFileName])
        else:
            csv_abs_f = os.sep.join(fpath.split(os.sep)[:]+['results','current']+[self.csvVerdictFileName])

        self.fname    = csv_abs_f

        self.fnameParDir = os.path.abspath(os.path.join(csv_abs_f, os.pardir))


    def get_full_fpath(self):

        return self.fname

    def get_filenamePrefix(self):

        return self.filenamePrefix


    def get_absVerdictFilePath(self):

        return self.fname

    def remove(self):

        fpath = os.path.dirname(os.path.abspath(__file__))

        if os.path.isfile(self.get_full_fpath()):
            print "will try to remove %s" %self.get_full_fpath()
            try:
                os.remove(self.get_full_fpath())
                print "file removal successful"
            except WindowsError:
                print "WindowsError: Cannot remove %s" %self.get_full_fpath()
                print "Continuing anyway ..."

            except Exception:
                print traceback.format_exc()
                print "Cannot remove %s" %self.get_full_fpath()
                print "Continuing anyway ..."

        else:
            print "file %s does not exist!" %self.get_full_fpath()
            print "continuing anyway ..."


    def removeStatusFileFromSource(self):

        statusFileList = ["STATUS_SUCCESS.txt", "STATUS_FAILURE.txt", "STATUS_UNSTABLE.txt"]

        for statusFile in statusFileList:

            if self.get_filenamePrefix() == '':
                pass
            else:
                statusFile = self.get_filenamePrefix() + '_' + statusFile

            absStatusFilePath = os.sep.join(self.fnameParDir.split(os.sep)[:]+[statusFile])

            if os.path.isfile(absStatusFilePath):
                print "will try to remove %s" %absStatusFilePath

                try:
                    os.remove(absStatusFilePath)
                    print "file removal successful"
                except WindowsError:
                    print "WindowsError: Cannot remove %s" %absStatusFilePath
                    print "Continuing anyway ..."
                except Exception:
                    print traceback.format_exc()
                    print "Non fatal error, continuing anyway ..."


    def removeStatusFileFromDestination(self, dst_path):

        statusFileList = ["STATUS_SUCCESS.txt", "STATUS_FAILURE.txt", "STATUS_UNSTABLE.txt"]

        for statusFile in statusFileList:

            statusFile = self.get_filenamePrefix() + statusFile

            dstFilePath = os.sep.join(dst_path.split(os.sep)[:]+[statusFile])

            if os.path.isfile(dstFilePath):
                print "will try to remove %s" %dstFilePath

                try:
                    os.remove(dstFilePath)
                    print "file removal successful"
                except WindowsError:
                    print "WindowsError: Cannot remove %s" %dstFilePath
                    print "Continuing anyway ..."


    def copy(self, fullDestFilePath):

        ret_val = 1

        parentDir = os.path.abspath(os.path.join(fullDestFilePath, os.pardir))

        if not os.path.exists(parentDir):
            print "dir %s does not exist" %parentDir
            print "will try to create"
            try:
                os.makedirs(parentDir)
                print "dir successfully created"
            except:
                ret_val = 0
                print "cannot create dir"
                return ret_val
        try:
            orgFileName = ntpath.basename(fullDestFilePath)
            abs_origFileName = os.sep.join(self.fnameParDir.split(os.sep)[:]+[orgFileName])

            if os.path.isfile(fullDestFilePath):
                print "file %s exists, will overwrite anyway" %fullDestFilePath

            print "Will copy from %s to %s" %(abs_origFileName, fullDestFilePath)
            shutil.copyfile(abs_origFileName, fullDestFilePath)
            print "Copy successful"
            ret_val = 1
            return ret_val

        except:
            print "Copy unsuccessful"
            ret_val = 0
            return ret_val


    def write(self, verdict="PASS", desc=""):
        try:
            fpath=os.path.split(self.fname)[0]

            if not os.path.exists(fpath):
                os.makedirs(fpath)

            with open(self.fname,'w') as fd:
                fd.write("%s,%s\n" %(verdict, desc))
            fd.close()
            print "Jenkins verdict file %s" %self.fname
            print "%s,%s" %(verdict, desc)

        except IOError:
            print "ERROR: opening file %s" % self.fname
            sys.exit(ec.ERRCODE_VERDICT_FILE_OPEN_FAIL)

    def createStatusFile(self, verdict):
        """
        create empty
        STATUS_ SUCCESS.txt, STATUS_UNSTABLE.txt, STATUS_FAILURE.txt
        depending on the verdict
        """

        if re.match('pass', verdict, re.I):
            if self.get_filenamePrefix() == '':
                statusFileName = "STATUS_SUCCESS.txt"
            else:
                statusFileName = self.get_filenamePrefix() + '_' +  "STATUS_SUCCESS.txt"

        elif re.match('fail', verdict, re.I):
            if self.get_filenamePrefix() == '':
                statusFileName = "STATUS_FAILURE.txt"
            else:
                statusFileName = self.get_filenamePrefix() + '_' + "STATUS_FAILURE.txt"
        elif re.match('incon', verdict, re.I):
            if self.get_filenamePrefix() == '':
                statusFileName = "STATUS_UNSTABLE.txt"
            else:
                statusFileName = self.get_filenamePrefix() + '_' + "STATUS_UNSTABLE.txt"
        else:
            print "Verdict file status :%s is not recognised" %verdict
            if self.get_filenamePrefix() == '':
                statusFileName = "STATUS_UNSTABLE.txt"
            else:
                statusFileName = self.get_filenamePrefix() + '_' +  "STATUS_UNSTABLE.txt"

        absStatusFileName = os.sep.join(self.fnameParDir.split(os.sep)[:]+[statusFileName])

        try:
            # there should only be one status file, 'w' ensures that
            # the file is always overwritten
            with open(absStatusFileName,'w') as fd:
                fd.write("")
                fd.close()
                print "Status file created is %s" %absStatusFileName

            statusFileName = ntpath.basename(absStatusFileName)

            return statusFileName

        except IOError:
            print "ERROR: opening file %s" % absStatusFileName
            sys.exit(ec.ERRCODE_STATUS_FILE_OPEN_FAIL)


    def __str__(self):
        print "%s" % self.fname
        return ""

if __name__ == "__main__":

    removeVerdictFile()

    testVerdict ="Fail"

    fpath = os.path.dirname(os.path.abspath(__file__))
    statusFilePath = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['pl1_wcdma_testbench','results','latest'])
    resultsPath = os.sep.join(fpath.split(os.sep)[:]+['results','test'])


    writeVerdictFile(verdict = testVerdict,
                     descr=ec.error_table[ec.ERRCODE_VERDICT_FILE_OPEN_FAIL],
                     testVerdictDir=resultsPath,
                     filenamePrefix='WCDMA_CMW500')

    removeVerdictFile()


    writeVerdictFile(verdict = testVerdict,
                 descr=ec.error_table[ec.ERRCODE_VERDICT_FILE_OPEN_FAIL],
                 testVerdictDir=resultsPath,
                 filenamePrefix='WCDMA_CMW500')






