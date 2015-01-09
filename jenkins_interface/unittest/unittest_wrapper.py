#-------------------------------------------------------------------------------
# Name:        unittest_wrapper
# Purpose:     wrapper script to call the correct unitest
#
# Author:      joashr
#
# Created:     23/09/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys, re, traceback

import logging

import shutil, re


(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))


try:
    import test_env
except ImportError:
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env

import pl1_testbench_framework.common.globals.test_globals as tg

from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath

import pl1_testbench_framework.jenkins_interface.common.parser.reg_expr as reg_expr

from pl1_testbench_framework.common.config.CfgError import CfgError

from pl1_testbench_framework.common.utils.subprocess_helper import SubProcess

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec

from pl1_testbench_framework.jenkins_interface.common.utils.csv_verdict import writeVerdictFile, removeVerdictFile

import logging
import os
import nose

from nose.plugins.xunit import Xunit
from nose.plugins import Plugin

# custom xunit PlugIn
class Customxunit(Xunit):
    """This plugin provides test results in the standard XUnit XML format."""
    name = 'customxunit'
    score = 1500
    encoding = 'UTF-8'
    error_report_file = None

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--customxunit-file', action='store',
            dest='xunit_file', metavar="FILE",
            default=env.get('NOSE_XUNIT_FILE', 'nosetests.xml'),
            help=("Path to xml file to store the xunit report in. "
                  "Default is nosetests.xml in the working directory "
                  "[NOSE_XUNIT_FILE]"))

    def _getCapturedStdout(self):
        return ''


def get_supported_variant_list():

    supported_variant_list = ['i500-121-1725-ti-att-mbim',
                              'nvidia-p2341-win7_internal']
    return supported_variant_list

def get_supported_jobs():

    supported_jobs_list = ['per_cl', 'weekly', 'nightly']

    return supported_jobs_list


def get_jenkins_job_params():

    import argparse

    description_msg="""
    Download ristretto package build
       python unittest.wrapper.py -r=<RAT> -u=<URL> -t=<jobtype> -g
       e.g. python unittest_wrapper.py -r=WCDMA -u=http://bs.nvidia.com/systems/datacard-builds/software/releases/core/cr5.br/CL749234-i500-121-1725-ti--d9e96824 -t=per_cl -g
    """
    parser = argparse.ArgumentParser(description=description_msg)
    parser.add_argument('-r', '--rat', type = str, default='[LTE_FDD, WCDMA]', help="choose the rat")

    parser.add_argument('-u', '--url', type = str, help='build URL')
    parser.add_argument('-g', '--genericBuild', help="special build option", action="store_true")

    parser.add_argument('-t', '--testtype', type = str, choices=get_supported_jobs())

    selection = {}

    args = parser.parse_args()

    if len(sys.argv) > 1 :

        selection['url'] = args.url

        selection['rat'] = args.rat


        if str(args.genericBuild) == "True":
            selection['genericBuild'] = 1
        else:
            selection['genericBuild'] = 0

        selection['testtype'] = args.testtype

    return selection



def get_config_params_from_file(filename='jenkins_config.txt'):
    '''
    get variant and url from jenkins_config.txt file
    '''

    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

    config_file_path = os.sep.join(cmdpath.split(os.sep)[:]+[filename])

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
    except IOError:
        print "Cannot read configuration from %s" %config_file_path
        print traceback.format_exc()
        exit()


def write_config_file(filename='jenkins_config.txt', dictionary={}):

    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

    config_file_path = os.sep.join(cmdpath.split(os.sep)[:]+[filename])

    config_file_dir =os.path.split(config_file_path)[0]


    if not os.path.exists(config_file_dir):
        os.makedirs(config_file_dir)

    try:
        with open(config_file_path,'w') as fd:
            for key in dictionary.keys():
                fd.write("%s=%s\n" %(key, dictionary[key]))
            fd.close()
    except IOError:
        print "Cannot read configuration from %s" %config_file_path
        print traceback.format_exc()
        exit()

def copy_folder(source_f, dest_f):
    # copy from source_f to dest_f
    if os.path.isdir(source_f):
        if not os.listdir(source_f):
            print ("dir %s is empty so will not be copied to %s"
                   %(source_f, dest_f))
            return
        else:
            print "copying from %s to %s" %(source_f, dest_f)
            shutil.copytree(source_f, dest_f)



def get_status_list(directory):

    #p = re.compile('.*CMW500_STATUS.*.txt', re.I)
    p = re.compile('.*STATUS.*.txt', re.I)

    status_file_l = []

    fileList = [ f for f in os.listdir(directory)  ]
    for fileName in fileList:
        absfileName = os.path.join(directory,fileName)
        if p.match(fileName):
            status_file_l.append(fileName)

    return status_file_l

def status_verdict_filename(directory, status_file_l):

    """
    single consolidated status file for Jenkins
    calculated from list of status files, one for each rat
    """

    p_success = re.compile('.*SUCCESS.*', re.I)
    p_fail = re.compile('.*FAIL.*', re.I)
    p_unstable = re.compile('.*UNSTABLE.*', re.I)

    status_success = False
    status_fail = False
    status_unstable = False

    for fileName in status_file_l:
        if p_unstable.match(fileName):
            status_unstable = True
        elif p_fail.match(fileName):
            status_fail = True
        elif p_success.match(fileName):
            status_success = True
        else:
            print "unknown: %s" %fileName
            print "Unsupported verdict file %s" %fileName
            status_unstable = True

    if status_unstable:
        print "overall verdict is inconclusive"
        return "STATUS_UNSTABLE.txt"
    elif status_fail:
        print "overall verdict is fail"
        return "STATUS_FAILURE.txt"
    elif status_success:
        print "overall verdict is success"
        return "STATUS_SUCCESS.txt"


def remove_files(directory, file_l):
    for fileName in file_l:
        absfileName = os.path.join(directory,fileName)
        if os.path.isfile(absfileName):
            print "remove %s" %absfileName
            os.remove(absfileName)

def writeStatusFile(directory, fileName):

    absStatusFileName = os.sep.join(directory.split(os.sep)[:]+[fileName])

    with open(absStatusFileName,'w') as fd:
        fd.write("")
        fd.close()
        print "Status file created is %s" %absStatusFileName

def flash_build(jenkins_dict, flash_results_dir):

    try:

        import pl1_testbench_framework.jenkins_interface.win8.test_system.test_flash_modem as test_flash

        branch = reg_expr.get_branch_from_url(url=jenkins_dict['url'])

        if os.path.isdir(flash_results_dir):

            shutil.rmtree(flash_results_dir)

        print "Jenkins url: %s" %(jenkins_dict['url'])

        print "Jenkins branch: %s" %branch

        print "variant = %s" %jenkins_dict['variant']

        if jenkins_dict['genericBuild']:

            print "Generic build selected!"


        jenkins_dict['powerSupply'] = 1


        my_download = test_flash.testBuild.DownloadPackage(variant=jenkins_dict['variant'], branch = branch,
                                                           http_build_url = jenkins_dict['url'],
                                                           b_special_build = jenkins_dict['genericBuild'],
                                                           testVerdictFileDir=flash_results_dir)

        if my_download.download_modem_binaries(param='ristretto_package' ) == tg.SUCCESS:

            test_flash.writeVerdictFile(verdict="PASS", descr="DOWNLOAD_SUCCESSFUL",
                                        testVerdictDir=flash_results_dir)
        else:
            test_flash.writeVerdictFile(verdict="INCONCLUSIVE",
                                        descr="DOWNLOAD_FAIL_CODE_UNDEF",
                                        testVerdictDir=flash_results_dir)
            return tg.FAIL

        flash_dir = my_download.getFlashBinDir()

        tools_dir = my_download.get_tools_dir()

        fw_update = test_flash.TestFirmwareUpdate(variant=jenkins_dict['variant'],
                                                  autobuild_url = my_download.http_build_url,
                                                  tools_dir = tools_dir,
                                                  flash_binaries_dir = flash_dir,
                                                  p4webrev=my_download.get_p4WebTxt(),
                                                  branch = branch,
                                                  results_dir=flash_results_dir,
                                                  testVerdictDir=flash_results_dir)

        status = fw_update.test_FirmwareUpdate()

        if status == test_flash.ec.ERRCODE_SUCCESS:

            print "Return code : %s, flash successful" %status

            return tg.SUCCESS

        else:

            print "Return code: %s, flash unsuccessful, cause" %(status, test_flash.ec.error_table[status])

            return tg.FAIL

    except SystemExit:

        exc_info = sys.exc_info()

        state=int('%s' % exc_info[1])

        test_flash.writeVerdictFile(verdict="INCONCLUSIVE", descr=test_flash.ec.error_table[state],
                                    testVerdictDir=flash_results_dir)

        print "Return code : %s, flash unsuccessful, cause %s" %(state, test_flash.ec.error_table[state])

        return tg.FAIL

    except Exception:

        print traceback.format_exc()

        status = test_flash.ec.ERRCODE_UNHANDLED_EXECEPTION

        test_flash.writeVerdictFile(verdict="INCONCLUSIVE", descr=test_flash.ec.error_table[status],
                                    testVerdictDir=flash_results_dir)
        return tg.FAIL


def copy_files(source_f, dest_f):
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

def execute_wcdma_unittest(jenkins_upload_f, jobtype):

    nose_module_arg_l = []

    if jobtype.upper() == "PER_CL":

        nose_module = 'test_wcdma_per_cl'

        nose_module_arg_l.append(nose_module)

        destfilename = 'wcdma_tests_per_cl.xml'


    elif jobtype.upper() == "NIGHTLY":

        nose_module='test_wcdma_nightly'

        nose_module_arg_l.append(nose_module)

        destfilename = 'wcdma_tests_nightly.xml'


    elif jobtype.upper() == "WEEKLY":

        nose_module = 'test_wcdma_weekly'

        nose_module_arg_l.append(nose_module)

        destfilename = 'wcdma_tests_weekly.xml'


    destfilepath = os.sep.join(jenkins_upload_f.split(os.sep)[:]+[destfilename])

    xunit_dst_option = r'--customxunit-file=' + destfilepath

    # note that the first arg in argv is ignored by nose
    # arbritrarily given '1'
    args = ['1'] + nose_module_arg_l + ['-v', '-s', '--nologcapture', '--match=^test', '--with-customxunit', xunit_dst_option]

    print "nose.run addplugins=[Customxunit()] %s" %args

    result=nose.run(addplugins=[Customxunit()], argv=args)

def execute_factory_tests(jenkins_upload_f, jobtype, branch, variant):


    import pl1_testbench_framework.pl1_rf_system.pl1_rf_system_test_env

    import pl1_rf_system.runTest as rf

    results_dir = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['pl1_rf_system', 'results', 'latest'])

    res_str = rf.runTestExternal(testType=jobtype,
                                 branch=branch,
                                 variant=variant)

    summaryFilePath = getSummaryFilePath(results_dir=results_dir,
                                         rat="RF")

    disable_root_logging()

    if summaryFilePath:

        getVerdict(summaryFilePath=summaryFilePath, rat="RF")

        # copy from latest_f to final_f
        # final_f is the one uploaded to Jenkins server
        copy_files(source_f=results_dir, dest_f=jenkins_upload_f)

    else:

        print "RF Factory Summary File from %s could not be found" % results_dir

        filenamePrefix = "RF_CMW500"

        writeVerdictFile(verdict="INCONCLUSIVE",
                         descr=ec.error_table[ec.ERRCODE_REGEX],
                         testVerdictDir=jenkins_upload_f,
                         filenamePrefix=filenamePrefix)

    return res_str

def execute_lte_test(jenkins_upload_f, rat, jobtype):

    testbench_file_executable = os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], 'run_pl1testbench_lte.py')

    if rat.upper() == "LTE_FDD" :

        if jobtype.upper() == "PER_CL":

            testbench_file_xmlconfig="lte_testconfig_fdd_percl.xml"

        elif jobtype.upper() == "NIGHTLY":

            testbench_file_xmlconfig="lte_testconfig_fdd_nightly.xml"

        elif jobtype.upper() == "WEEKLY":

            testbench_file_xmlconfig="lte_testconfig_fdd_weekly.xml"

        else:
            print("INVALID %s JOB TYPE : %s" % ("LTE", jobtype))
            filenamePrefix = "LTE_FDD_CMW500"
            # write verdict file to final_f
            writeVerdictFile(verdict="INCONCLUSIVE",
                             descr=ec.error_table[ec.ERRCODE_UNKNOWN_JOBTYPE],
                             testVerdictDir=jenkins_upload_f,
                             filenamePrefix=filenamePrefix)
            return

    elif rat.upper() == "LTE_TDD":

        if jobtype.upper() == "PER_CL":

            testbench_file_xmlconfig="lte_testconfig_tdd_percl.xml"

        else:
            filenamePrefix = "%s_CMW500" %rat
            writeVerdictFile(verdict="INCONCLUSIVE",
                             descr=ec.error_table[ec.ERRCODE_UNKNOWN_JOBTYPE],
                             testVerdictDir=jenkins_upload_f,
                             filenamePrefix=filenamePrefix)


    testbench_file_xmlconfig = os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], testbench_file_xmlconfig)

    results_dir = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'results', 'latest'])

    summaryFile = os.sep.join(results_dir.split(os.sep)[:]+['LTE_CMW500_TestReport_SUMMARY.csv'])

    cmd_run = r"python %s -xml %s" % (testbench_file_executable, testbench_file_xmlconfig)

    print ("RUNNING CMD : %s" % cmd_run)

    if jobtype.upper() == 'WEEKLY':
        timeout = (14*60*60)
    else:
        timeout = (3*60*60)

    enable_logging(loglevel="Debug")

    res=runTestbench(cmd_run, timeout = timeout)

    disable_root_logging()

    summaryFilePath = getSummaryFilePath(results_dir=results_dir, rat=rat)

    if summaryFilePath:

        getVerdict(summaryFilePath=summaryFilePath, rat=rat.upper())

        # copy from latest_f to final_f
        # final_f is the one uploaded to Jenkins server
        copy_files(source_f=results_dir, dest_f=jenkins_upload_f)

    else:

        print "LTE Test Summary File from %s could not be found" % results_dir

        filenamePrefix = "%s_CMW500" %rat_mod

        writeVerdictFile(verdict="INCONCLUSIVE",
                         descr=ec.error_table[ec.ERRCODE_REGEX],
                         testVerdictDir=jenkins_upload_f,
                         filenamePrefix=filenamePrefix)

    return res


def getSummaryFilePath(results_dir, rat):

    fileNamePath = None

    p = re.compile('%s.*SUMMARY.csv' %rat, re.I)

    fileList = [ f for f in os.listdir(results_dir)  ]

    for fileName in fileList:

        if p.match(fileName):

            fileNamePath = os.sep.join(results_dir.split(os.sep)[:]+[fileName])

            return fileNamePath

    return fileNamePath



def getVerdict(summaryFilePath, rat):

    import ntpath

    summaryFileName = ntpath.basename(summaryFilePath)

    results_dir = os.path.dirname(summaryFilePath)

    test_prefix = rat.upper() + '_CMW500'


    verdict = ec.ERRCODE_SUCCESS
    test_inconclusive = 0
    test_invalid = 0
    test_fail = 0
    test_pass = 0

    try:
        file_h = open(summaryFilePath)
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
                             testVerdictDir=results_dir,
                             filenamePrefix=test_prefix)

            verdict = ec.ERRCODE_TEST_INCONCLUSIVE

        elif test_fail:

            writeVerdictFile(verdict="FAILURE",
                             descr=ec.error_table[ec.ERRCODE_TEST_FAIL],
                             testVerdictDir=results_dir,
                             filenamePrefix=test_prefix)

            verdict = ec.ERRCODE_TEST_FAIL

        elif test_pass:

            writeVerdictFile(verdict="PASS",
                             descr=ec.error_table[ec.ERRCODE_SUCCESS],
                             testVerdictDir=results_dir,
                             filenamePrefix=test_prefix)

            verdict = ec.ERRCODE_SUCCESS

        else:

            print "Code should not enter here"
            writeVerdictFile(verdict="INCONCLUSIVE",
                             descr=ec.error_table[ec.ERRCODE_INVALID_VERDICT],
                             testVerdictDir=results_dir,
                             filenamePrefix=test_prefix)

            verdict = ec.ERRCODE_TEST_INCONCLUSIVE


        file_h.close()

        return verdict

    except IOError:
        print "## Error: file %s not created" %summaryFilePath
        print traceback.format_exc()
        verdict = ec.ERRCODE_SUMMARY_FILE_NOT_FOUND
        writeVerdictFile(verdict="INCONCLUSIVE",
                        descr=ec.error_table[ec.ERRCODE_SUMMARY_FILE_NOT_FOUND],
                        testVerdictDir=results_dir,
                        filenamePrefix=test_prefix)
        return verdict



def runTestbench(cmd, timeout = 240):

    proc = SubProcess(cmd)

    (output, hasTimeout) = proc.waitForProcessAndRetrieveOutput(timeout)
    if hasTimeout:
        print("Modem software timeout")
    elif proc.returnCode == 0:
        print("Modem software executed successfully")
    else:
        print("Something went wrong (return code: %s)" % proc.returnCode)

    res = proc.returnCode
    return res


def enable_logging(loglevel="Info"):

    logname= os.path.splitext(os.path.basename(__file__))[0]

    logfile  = logname  + '.LOG'

    loglevel = loglevel.upper()

    cfg_multilogging(loglevel, logfile)

def disable_root_logging():

    # remove logging handlers which could have been configured previously
    for handler in logging.root.handlers[:]:

        logging.root.removeHandler(handler)

def main():

    jenkins_job = get_jenkins_job_params()

    if jenkins_job:

        print "Jenkins url: %s" %(jenkins_job['url'])

        branch = reg_expr.get_branch_from_url(url=jenkins_job['url'])

        print "Jenkins branch: %s" %branch

        rat_l=re.sub(r'[\[\]\s]', '', jenkins_job['rat']).split(',')

        print "Selected RAT = %s" %rat_l

        print "test type = %s" %jenkins_job['testtype']

        variant = reg_expr.get_variant_from_url(url=jenkins_job['url'])

        if not variant:
            print "Cannot extract variant from %s" %jenkins_job['url']
            return
        else:
            jenkins_job['variant'] = variant
            if jenkins_job['variant'] in get_supported_variant_list():
                pass
            else:
                print "variant %s is not supported" %jenkins_job['variant']
                print "list of supported variants is %s" % get_supported_variant_list()
                return

        print "variant = %s" %jenkins_job['variant']

        print "generic build option = %s" %jenkins_job['genericBuild']

        write_config_file(dictionary=jenkins_job)

        get_config_params_from_file()

    else:

        print "No command line options specified!"
        return

    xml_abs_path = os.sep.join(cmdpath.split(os.sep)[:]+['nosetests.xml'])

    import time

    ts=time.strftime("%Y%m%d_%H%M%S", time.localtime())

    # folder for local results storage
    final_storage_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['jenkins_interface', 'win8', 'test_system', 'results', ts + '_TestReport'])

    # final folder to store all the consolidated test results for all rats
    # it is the contents of this folder that is uploaded by Jenkins
    final_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['jenkins_interface', 'win8', 'test_system', 'results', 'final'])

    # results folder for each rat
    results_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['jenkins_interface' 'win8', 'test_system', 'results', 'latest'])

    # remove
    if os.path.isdir(final_f):

        shutil.rmtree(final_f)

    if flash_build(jenkins_dict=jenkins_job, flash_results_dir=final_f) == tg.FAIL:
        return
    else:
        pass


    disable_root_logging()

    # if flash successful then remove directory containing results of the flash
    # operation as this same directory will be poulated  with the test results
    if os.path.isdir(final_f):

        shutil.rmtree(final_f)

    for rat in rat_l :


        if rat == 'WCDMA':

            dir_wcdma = os.sep.join(cmdpath.split(os.sep)[:]+['test_WCDMA'])
            AddSysPath(dir_wcdma)

            execute_wcdma_unittest(jenkins_upload_f=final_f,
                                   jobtype=jenkins_job['testtype'])


        elif rat == 'LTE_FDD' or rat == 'LTE_TDD' or rat == 'LTE' :

            if rat.upper() == 'LTE':

                rat = 'LTE_FDD'

            res = execute_lte_test(jenkins_upload_f=final_f,
                                   rat = rat,
                                   jobtype = jenkins_job['testtype'])


        elif rat.upper() == "RF" :

            res_str = execute_factory_tests(jenkins_upload_f=final_f,
                                            jobtype=jenkins_job['testtype'],
                                            branch=branch,
                                            variant=variant)

        else:

            print "rat %s is not supported" % rat
            writeVerdictFile(verdict="INCONCLUSIVE",
                            descr=ec.error_table[ec.ERRCODE_UNSUPPORTED_RAT],
                            testVerdictDir=final_f,
                            filenamePrefix="")
            return


    status_file_list = get_status_list(directory=final_f)

    remove_files(directory=final_f, file_l=status_file_list)

    new_status_filename = status_verdict_filename(directory=final_f,
                                                  status_file_l=status_file_list)

    writeStatusFile(directory=final_f, fileName=new_status_filename)

    copy_folder(source_f=final_f, dest_f=final_storage_f)



if __name__ == '__main__':

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    enable_logging(loglevel="Debug")

    main()






