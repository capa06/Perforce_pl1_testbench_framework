#-------------------------------------------------------------------------------
# Name:        common_testbench
# Purpose:
#
# Author:      joashr
#
# Created:     25/09/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import sys, os, subprocess, argparse, logging, re, shutil, time
import traceback

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


import test_env
import unittest

from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec
from pl1_testbench_framework.jenkins_interface.common.utils.csv_verdict import writeVerdictFile, removeVerdictFile


def setUpModule():

    pass


def tearDown(self):

    pass


class common_testbench(unittest.TestCase):

    def setUp(self):

        self.orig_sys_path = sys.path


    @classmethod
    def get_config_params_from_file(cls, filename='jenkins_config.txt'):
        '''
        get variant and url from jenkins_config.txt file
        '''

        (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

        config_file_path = os.sep.join(cmdpath.split(os.sep)[:-1]+[filename])

        url_p = re.compile('url\s*=\s*(.*)', re.I)
        variant_p = re.compile('variant\s*=\s*(.*)', re.I)
        generic_build_p = re.compile('genericBuild\s*=\s*(.*)', re.I)


        try:
            for line in open(config_file_path):
                line = line[:-1]
                m_url = url_p.match(line)
                m_variant = variant_p.match(line)
                m_generic_build = generic_build_p.match(line)
                if m_url:
                    url = m_url.group(1)
                    print "url read from file is %s" %url

                elif m_variant:
                    variant = m_variant.group(1)
                    print "variant read from file is %s" %variant

                elif m_generic_build:
                    generic_build = int(m_generic_build.group(1))
                    print "generic build option read from file is %i" %generic_build

                    return (url, variant, generic_build)
        except IOError:
            print "Cannot read configuration from %s" %config_file_path
            print traceback.format_exc()
            raise KeyboardInterrupt

    @classmethod
    def rm_old_results_files(cls, results_dir):
        if os.path.isdir(results_dir):
            fileList = [ f for f in os.listdir(results_dir)  ]
            for fileName in fileList:
                absfileName = os.path.join(results_dir,fileName)
                if os.path.isfile(absfileName):
                    print "removing file %s .." %absfileName
                    os.remove(absfileName)
                elif os.path.isdir(absfileName):
                    print "removing dir %s .." %absfileName
                    shutil.rmtree(absfileName, ignore_errors=True)
                else:
                    print "will not remove %s as it is neither a file or directory" %absfileName
        else:
            pass


    @classmethod
    def flash_build(cls):

        import pl1_jenkins.test_system.test_execution as test_exec


        cls.url, cls.variant, cls.generic_build = cls.get_config_params_from_file()

        jenkins = {}

        jenkins['url'] = cls.url

        jenkins['variant'] = cls.variant

        jenkins['special_build'] = int(cls.generic_build)

        jenkins['testjob'] = "per_cl"

        branch = test_exec.testBuild.get_branch_from_url(url=jenkins['url'])

        print "Jenkins url: %s" %(jenkins['url'])

        print "Jenkins branch: %s" %branch

        print "variant = %s" %jenkins['variant']

        if jenkins['special_build']:

                print "Special build selected!"

        testVerdict = 0

        testRunStatus = 0

        cls.test = None

        cls.test = test_exec.TestRunExecution(variant=jenkins['variant'], rat=cls.rat,
                                              jobtype=jenkins['testjob'],
                                              testVerdictFileDir=cls.latest_f)


        flash_status = 0

        cls.test.set_results_dir(directory=cls.latest_f)


        flash_status = cls.test.build_flash_modem(url=jenkins['url'],
                                                  branch=branch,
                                                  b_sepecial_build=jenkins['special_build'])

        if flash_status != 0:

            state = int(flash_status)

            print "Build-Flash failure, pl1testbench will not be executed"

            test_exec.writeVerdictFile(verdict="INCONCLUSIVE", descr=test_exec.ec.error_table[state],
                                       destinationPath=cls.test.get_results_dir(),
                                       filenamePrefix=cls.test.get_verdict_file_prefix(),
                                       testVerdictDir=cls.latest_f)

            print "Return code : %s, flash unsuccesful, cause %s" %(state,
                                                                   test_exec.ec.error_table[state])

            raise KeyboardInterrupt

        else:

            print "Build-Flash successful, will proceed to execute pl1testbench"

        # remove logging handlers which could have been configured previously
        for handler in logging.root.handlers[:]:

            logging.root.removeHandler(handler)

    def checkFileExist(self, fileToCheck, folder):
        b_fileExist = 0
        print "Will check to see if %s is in %s" %(fileToCheck, folder)
        if not os.path.isdir(folder):
            print "folder %s does not exist" %folder
            return b_fileExist
        fileList = [ f for f in os.listdir(folder)  ]
        for fileName in fileList:
            if fileToCheck == fileName:
                print "filename %s already exists, will append results" %fileToCheck
                b_fileExist = 1
                break
        return b_fileExist

    def merge_files(self, fileToMerge, mergeToFile):
        """
        merge test summary file from fileToMerge(*TestReport_Summary*) to
        mergeToFile(*TestReport_Summary*). Do not append(merge) the header of fileToMerge
        report as this is included in the mergeToFile. This is required because
        each test case generates a TestReport_Summary of the same name and after
        all the unit tests are complete we would like a consolidated report

        fileToMerge and mergeToFile should contain the absolute path

        """

        print "Will try to append contents from %s to %s" %(fileToMerge, mergeToFile)

        if not os.path.isfile(fileToMerge):
            print "file to merge %s does not exist, file merge will be aborted!" %fileToMerge
            return


        fileToMergeH = open(fileToMerge)
        lineList = []
        status_header_found = False # i.e. TestID, Verdict etc
        for line in fileToMergeH:
            line = line[:-1]
            cols = line.split(',')
            if re.match('\s*TestID', cols[0], re.I):
                status_header_found = True
                continue
            if status_header_found:
                lineList.append(line)

        fileToMergeH.close()

        with open(mergeToFile,"a") as myMergedFile:
            for line in lineList:
                myMergedFile.write(line)
                myMergedFile.write("\n")

    def copy_results_to_latest_f(self):
        """
        Copy results from sub_test to ..pl1_jenkins\test_system\results\latest for windows
        ../pl1_testbench_framework/jenkins_interface/linux/results/latest for linux
        """

        p = re.compile('.*TestReport_SUMMARY.*', re.I)

        if self.subtest_results_f=="":
            return

        if os.path.isdir(self.subtest_results_f):
            fileList = [ f for f in os.listdir(self.subtest_results_f)  ]
            for fileName in fileList:
                absfileName = os.path.join(self.subtest_results_f,fileName)
                if p.match(fileName):
                    print "Checking if summary file %s already exists in %s" %(fileName, fileList)
                    if self.checkFileExist(fileToCheck=fileName, folder=self.latest_f):
                        print "Yes, summary file exists"
                        existingReportSummaryFile = os.path.join(self.latest_f,fileName)
                        self.merge_files(fileToMerge=absfileName,
                                         mergeToFile=existingReportSummaryFile)
                        continue
                    else:
                        print "Summary file does not exist, no append operation required!"
                        print "Will continue as normal"

                if os.path.isfile(absfileName):
                    if not os.path.isdir(self.latest_f):
                        print "%s does not exist" %self.latest_f
                        os.makedirs(self.latest)
                        print "%s successfully created" %self.latest_f
                    print "copying file %s to dir %s" %(absfileName, self.latest_f)
                    shutil.copy(absfileName, self.latest_f)
                else:
                    print "will not copy %s as it is neither a file or directory" %absfileName
        else:
            pass

    @classmethod
    def copy_files(cls, source_f, dest_f):
        """
        add all files from source folder to destination folder
        """
        if os.path.isdir(source_f):
            fileList = [ f for f in os.listdir(source_f)  ]
            for fileName in fileList:
                absfileName = os.path.join(source_f,fileName)

                if os.path.isfile(absfileName):
                    if not os.path.isdir(dest_f):
                        print "dir %s does not exist" %dest_f
                        os.makedirs(dest_f)
                        print "%s successfully created" %dest_f
                    print "copying file %s to dir %s" %(absfileName, dest_f)
                    shutil.copy(absfileName, dest_f)
                else:
                    print "will not copy %s as it is not a file" %absfileName
        else:
            print "%s is not a directory" %source_f

    @classmethod
    def get_verdict_from_summmary_file(cls):

            # summary file in test.summary points to ...<rat>\results\latest
            # want to look at ...pl1_jenkins\test_system\results\latest
            # as this is the merged summary file that we can process
            # to get the overall Jenkins status STATUS_xx.txt

            test_summary_file_path = cls.summaryFile
            import ntpath
            # extract filenane from absolute filepath
            test_summary_filename = ntpath.basename(cls.get_summary_file_path())

            new_test_summary_file_path = os.sep.join(cls.latest_f.split(os.sep)[:]+[test_summary_filename])

            # results directory for Jenkins status file
            cls.set_results_dir(directory=cls.latest_f)

            # now perform processing in new path location
            cls.set_summary_file_path(path=new_test_summary_file_path)

            # get verdict from merged test summary file and write Jenkins
            # status file
            cls.getVerdict()

    @classmethod
    def set_results_dir(cls, directory):
        cls.results_dir = directory
        return

    @classmethod
    def get_results_dir(cls):
        return cls.results_dir

    @classmethod
    def set_summary_file_path(cls, path):
        cls.summaryFile = path
        return

    @classmethod
    def get_summary_file_path(cls):
        return cls.summaryFile

    @classmethod
    def get_verdict_file_prefix(cls):
        test_prefix = cls.rat.upper() + '_CMW500'
        return test_prefix

    @classmethod
    def getVerdict(cls):
        # class method gets the verdict from the merged test summary file
        # for the tests comprising the test class and writes STATUS_xx.txt
        # indicating SUCCESS, FAIL or INCONCLUSIVE

        #import pl1_jenkins.common.error_codes as ec
        #from pl1_jenkins.test_system.csv_verdict import writeVerdictFile

        verdict = ec.ERRCODE_SUCCESS
        test_inconclusive = 0
        test_invalid = 0
        test_fail = 0
        test_pass = 0
        try:
            file_h = open(cls.get_summary_file_path())
            linenumber = 0
            colNumVerdict = None
            for line in file_h:
                # remove new line
                line = line[:-1]
                cols = line.split(',')
                if re.match('\s*TestID', cols[0], re.I):
                    foundTitleLine = True
                    print " ".join('%-20s' %col for col in cols)
                    # now found col num for verdict
                    colNum = 0
                    for colHead in cols:
                        if re.match('\s*verdict', colHead, re.I):
                            # col number found for verdict
                            colNumVerdict = colNum
                            break
                        colNum += 1
                    if not colNumVerdict:
                        print "Cannot find verdict column"
                        verdict = ec.ERRCODE_TEST_INCONCLUSIVE
                        test_inconclusive = 1
                        break
                    else:
                        continue

                if colNumVerdict:
                    if re.match('\s*pass', cols[colNumVerdict], re.I):
                        test_pass = True
                    elif re.match('\s*fail', cols[colNumVerdict], re.I):
                        test_fail = True
                    elif re.match('\s*inconclusive', cols[colNumVerdict], re.I):
                        test_inconclusive = True
                    else:
                        test_invalid = True
                        print "Unknown column verdict : %s" %cols[colNumVerdict]
                        verdict = ec.ERRCODE_INVALID_VERDICT

                    print " ".join('%-20s' %col for col in cols)


                linenumber += 1

            # end of for for loop


            if test_inconclusive:

                writeVerdictFile(verdict="INCONCLUSIVE",
                                 descr=ec.error_table[ec.ERRCODE_TEST_INCONCLUSIVE],
                                 testVerdictDir=cls.get_results_dir(),
                                 filenamePrefix=cls.get_verdict_file_prefix())

                verdict = ec.ERRCODE_TEST_INCONCLUSIVE

            elif test_fail:

                writeVerdictFile(verdict="FAILURE",
                                 descr=ec.error_table[ec.ERRCODE_TEST_FAIL],
                                 testVerdictDir=cls.get_results_dir(),
                                 filenamePrefix=cls.get_verdict_file_prefix())

                verdict = ec.ERRCODE_TEST_FAIL

            elif test_pass:

                writeVerdictFile(verdict="PASS",
                                 descr=ec.error_table[ec.ERRCODE_SUCCESS],
                                 testVerdictDir=cls.get_results_dir(),
                                 filenamePrefix=cls.get_verdict_file_prefix())

                verdict = ec.ERRCODE_SUCCESS

            else:

                print "Code should not enter here"

                writeVerdictFile(verdict="INCONCLUSIVE",
                                 descr=ec.error_table[ec.ERRCODE_INVALID_VERDICT],
                                 testVerdictDir=cls.get_results_dir(),
                                 filenamePrefix=cls.get_verdict_file_prefix())


            file_h.close()

            return verdict

        except IOError:
            print "## Error: file %s not created" %cls.get_summary_file_path()
            print traceback.format_exc()
            verdict = ec.ERRCODE_SUMMARY_FILE_NOT_FOUND
            writeVerdictFile(verdict="INCONCLUSIVE",
                            descr=ec.error_table[ec.ERRCODE_SUMMARY_FILE_NOT_FOUND],
                            testVerdictDir=cls.get_results_dir(),
                            filenamePrefix=cls.get_verdict_file_prefix())
            return verdict

    def tearDown(self):

        sys.path = self.orig_sys_path

        self.copy_results_to_latest_f()

        for handler in logging.root.handlers[:]:

            logging.root.removeHandler(handler)

    @classmethod
    def tearDownClass(cls):
        print "Tear down class"

        # get overall test verdict from TestReport_SUMMARY file
        # Jenkins latest results folder
        try:

            cls.get_verdict_from_summmary_file()

            # remove test verdict file
            removeVerdictFile(filenamePrefix=cls.get_verdict_file_prefix(),
                              testVerdictDir=cls.latest_f)

            if sys.platform in ['cygwin', 'win32']:
                
                cls.final_f = os.sep.join(os.environ['TEST_SYSTEM_ROOT_FOLDER'].split(os.sep)[:] + ['results', 'final'])
                
            else:
                
                cls.final_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['jenkins_interface', 'linux', 'results', 'final'])

            # copy results files to final_f
            cls.copy_files(source_f=cls.latest_f, dest_f=cls.final_f)


        except Exception:
            print "Cannot tear down the class"
            print traceback.format_exc()


if __name__ == '__main__':
    pass

