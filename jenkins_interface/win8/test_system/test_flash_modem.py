#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        modem flash
# Purpose:
#
# Author:      joashr
#
# Created:     14/08/2013

#-------------------------------------------------------------------------------


# standard library imports
import os, sys, traceback, subprocess, time, re

try:
    import test_env
except ImportError:
    (abs_path, name)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(abs_path.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env

import test_BuildDownload as testBuild

from pl1_testbench_framework.common.instr.PsuBench import PsuCheckOn, PsuBenchOn, PsuBenchOff

from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port

from pl1_testbench_framework.jenkins_interface.common.utils.csv_verdict import writeVerdictFile, removeVerdictFile

import pl1_testbench_framework.common.com.modem as modem

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec

import pl1_testbench_framework.common.globals.test_globals as tg

import pl1_testbench_framework.jenkins_interface.common.parser.reg_expr as reg_expr

from pl1_testbench_framework.common.utils.os_utils import insertPause

import threading


class RunCmd(threading.Thread):
    def __init__(self, cmd, cwd=None, shell=True, timeout=120):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout
        self.cwd = cwd
        self.shell=shell

    def run(self):

        self.StDout = ""

        self.StDerr = ""

        if self.cwd is None:

            self.sub_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)

        else:

            self.sub_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell, cwd=self.cwd)

        self.StDout, self.StDerr = self.sub_process.communicate()

        if self.StDout != "":

            print "cmd output =>"

            print  self.StDout

        if self.StDerr != "":

            #print "err output =>"

            #print  self.StDerr

            pass


    def Run(self):

        runStatus = tg.SUCCESS

        self.start()

        self.join(self.timeout)

        if self.is_alive():

            print "=> Timeout exceeded"

            self.sub_process.terminate()      #use self.p.kill() if process needs a kill -9

            self.join(timeout=5)

            runStatus = tg.FAIL


        return runStatus,self.StDout, self.StDerr



class TestFirmwareUpdate(object):
    def __init__ (self, variant, autobuild_url,
                  flash_binaries_dir, tools_dir,
                  p4webrev="", branch="",
                  results_dir="",
                  filenamePrefix="",
                  testVerdictDir=""):

        self.DOWNLOADER_NAME = 'downloader.exe'
        self.DOWNLOADER_PATH_COMPLETE = (os.sep.join(tools_dir.split(os.sep)[:]+[ 'downloader', 'bin', 'bin.wx32', self.DOWNLOADER_NAME]))
        self.BUILDS_PATH_COMPLETE = ""
        self.chip_option="--chip 9040 "
        self.variant = variant
        self.autobuild_url = autobuild_url
        self.tools_dir = tools_dir
        self.perforce_cl = ""
        self.p4webrev=p4webrev
        self.branch=branch
        self.flash_binaries_dir = flash_binaries_dir
        self.maxNumRetries = 3
        self.results_dir = results_dir # results directory for storing core dump logs
        self.filenamePrefix = filenamePrefix
        self.testVerdictDir = testVerdictDir
        removeVerdictFile(filenamePrefix=filenamePrefix, testVerdictDir=self.testVerdictDir)


    def get_testVerdictDir(self):

        return self.testVerdictDir

    def __str__(self):
        print "--------------------------------------"
        print "Downloader Name      :   %s" %self.DOWNLOADER_NAME
        print "Tools dir            :   %s" %self.tools_dir
        print "Downloader Path      :   %s" %self.DOWNLOADER_PATH_COMPLETE
        print "Build directory      :   %s" %self.BUILDS_PATH_COMPLETE
        print "Chip option          :   %s" %self.chip_option
        print "Max num of retries   :   %s" %self.maxNumRetries
        print "Variant              :   %s" %self.variant
        print "Autobuild_url        :   %s" %self.autobuild_url
        print "p4webrev             :   %s" %self.p4webrev
        print "flash file dir       :   %s" %self.flash_binaries_dir
        print "Perforce CL          :   %s" %self.perforce_cl
        print "Jenkins verdict path :   %s" %self.verdictPath
        print "Results dir          :   %s" %self.results_dir

        return ""

    def get_results_dir(self):
        return self.results_dir

    def set_perforce_cl(self, cl):
        self.perforce_cl = cl

    def get_perforce_cl(self):
        return self.perforce_cl

    def get_downloader_path(self):
        return self.DOWNLOADER_PATH_COMPLETE

    def get_variant(self):
        return self.variant

    def set_build_dir(self):
        self.BUILDS_PATH_COMPLETE = self.flash_binaries_dir

    def get_build_dir(self):
        return self.BUILDS_PATH_COMPLETE

    def InitFirmwarePath(self):
        try:
            if sys.platform=="win32":
                if sys.platform in ['cygwin', 'win32']:
                    pass
                else:
                    print '>>> Unsupported Platform %s' %sys.platform
                    sys.exit(ec.ERRCODE_UNSUPPORTED_OS_PLATFORM)

            print "Downloader : %s" %os.path.abspath(self.get_downloader_path())

        except Exception, err:
            print traceback.format_exc()
            raise Exception("Downloader module setting function error")

    def DownloadFirmware(self):

        ret_val = ec.ERRCODE_SUCCESS

        Custom_List_Complete = ""

        #CustomerListFiles = ['loader.wrapped', 'secondary_boot.wrapped', 'modem.wrapped', 'deviceConfig.bin', 'productConfig.bin', 'platformConfig.bin', 'audioConfig.bin']
        #CustomerListFiles = ['loader.wrapped', 'modem.wrapped', 'deviceConfig.bin', 'productConfig.bin', 'platformConfig.bin', 'audioConfig.bin']
        CustomerListFiles = ['modem.wrapped', 'deviceConfig.bin', 'productConfig.bin', 'platformConfig.bin', 'audioConfig.bin']

        Custom_Path = self.BUILDS_PATH_COMPLETE

        for WrappedFiles in CustomerListFiles:

            Custom_List_Complete = Custom_List_Complete + "%s\%s" % (Custom_Path, WrappedFiles)+';'

        # workaround for Bug 1518483
        mode_switch = modem.switch_mode_1_3()
        if mode_switch == tg.FAIL:
            return ec.ERRCODE_BOOT_LOADER_MODE_FAIL


        com_port_str = "COM%s" %auto_detect_port("Modem_port")

        cmd = "%s -w 30 -d %s -f %s" % (self.DOWNLOADER_PATH_COMPLETE, com_port_str, Custom_List_Complete)
        cmd = "%s -w 30 -f %s" % (self.DOWNLOADER_PATH_COMPLETE, Custom_List_Complete)
        #cmd = "%s -v 3 -m 1 -d %s -f %s" % (self.DOWNLOADER_PATH_COMPLETE, com_port_str, Custom_List_Complete)

        # with standalone loader
        #cmd = "%s -l -w 30 -f %s" % (self.DOWNLOADER_PATH_COMPLETE, Custom_List_Complete)



        print "\nStarting a subprocess to execute the command:\n%s" % cmd

        sys.stdout.flush()

        StDout = ""

        StDerr = ""

        runStatus = tg.SUCCESS

        runStatus, StDout,StDerr = RunCmd(cmd=cmd, timeout=120).Run()

        if runStatus == tg.FAIL:

            if StDout != "":

                print "cmd output =>"

                print  StDout

            if StDerr != "":

                print "err output =>"

                print  StDerr

            ret_val = ec.ERRCODE_FLASH_TIMEOUT_ERROR

            return ret_val

        else:

            ReturnMessage = StDout


        if not re.search('Download Success', ReturnMessage, re.I) and not re.search(
                         'Firmware\s*Update\s*Succeeded', ReturnMessage, re.I) :

            print "err output =>"

            print  StDerr

            ret_val = ec.ERRCODE_FLASH_FAILURE

        else:

            print "Firmware Update Succeeded"

            ret_val = ec.ERRCODE_SUCCESS

        sys.stdout.flush()

        self.message = cmd

        return ret_val

    def flash_required(self, target_cl, target_p4webrev):
        """
        check if flashing a new build is actually required
        by checking current build CL and p4webrev with
        target CL and target p4webrev
        returns True if flash is required, otherwise false
        """

        b_flash_required = True

        modemInfo = ""
        modem_p4WebRevList = []

        modemInfo = modem.get_modem_info()
        modem_p4WebRevStr = reg_expr.get_p4webrevStringfrom_modem(modemInfo)
        modem_build_cl = reg_expr.get_build_cl_from_modem(modemInfo)

        print "Modem CL is %s, Target CL is %s" %(modem_build_cl, target_cl)
        if modem_build_cl == target_cl:
            print "Modem CL matches Target CL"
            target_p4webrevList = target_p4webrev.split(',')
            modem_p4WebRevList = modem_p4WebRevStr.split(',')
            print "Checking p4webrev's"
            print "Current modem p4webrev list: %s" %(modem_p4WebRevList)
            print "Target p4webrev list:        %s" %(target_p4webrevList)
            if sorted(modem_p4WebRevList) == sorted(target_p4webrevList):
                print "Current p4webrev list matches target p4webrev list"
                print "No software build flash required"
                b_flash_required = False
                return b_flash_required
            else:
                print "Current p4webrev list does not match target p4webrev list"
                b_flash_required = True
                return b_flash_required
        else:
            print "Current modem CL does not match the target CL, flash required"
            b_flash_required = True
            return b_flash_required

    def test_FirmwareUpdate(self):

        numReTry = 0

        res = 0

        SUCCESS = 0

        FAIL = -1

        target_cl_str = reg_expr.extract_target_cl(url_link = self.autobuild_url)

        if not self.flash_required(target_cl=target_cl_str,
                                   target_p4webrev=self.p4webrev):

            writeVerdictFile(verdict="PASS",
                             descr="FLASH_NOT_REQUIRED",
                             filenamePrefix=self.filenamePrefix,
                             testVerdictDir=self.get_testVerdictDir())

            return SUCCESS

        self.set_perforce_cl(target_cl_str)

        self.set_build_dir()

        self.InitFirmwarePath()

        while numReTry < self.maxNumRetries:

            sys.stdout.flush()

            print '--> Start Downloading firmware'

            download_fw_result = self.DownloadFirmware()

            if download_fw_result == SUCCESS:

                verify_flash_result = self.verifyFlash(numReTry)

                if verify_flash_result == SUCCESS:

                    res = SUCCESS

                    break

                else:

                    res = FAIL

                    download_fw_result = res

                    numReTry += 1

            else:
                # modem flash download failure
                if numReTry == self.maxNumRetries:

                    res = download_fw_result

                    duration_sec = 60

                    print "pausing %s to see if modem enters bootloader mode after second flash failure!" % duration_sec

                    insertPause(tsec=duration_sec)

                    modem_mode = modem.query_modem_mode()

                    if modem_mode != 0:

                        # cannot query mode or in boot loader mode, either way try to extract
                        # core dump

                        core_dump_filename = 'coredump_%s.log' %numReTry

                        modem.collect_full_core_dump(core_dump_dir=self.get_results_dir(), filename=core_dump_filename)

                    break

                else:

                    res = FAIL

                    duration_sec = 60

                    print "pausing %s to see if modem enters bootloader mode after flash failure!" %duration_sec

                    insertPause(tsec=duration_sec)

                    modem_mode = modem.query_modem_mode()

                    if modem_mode != 0:

                        core_dump_filename = 'coredump_%s.log' %numReTry

                        modem.collect_full_core_dump(core_dump_dir=self.get_results_dir(), filename=core_dump_filename)

                    numReTry += 1


        if res == SUCCESS:

            writeVerdictFile(verdict="PASS",
                             descr="SOFTWARE_BUILD_FLASH_SUCCESFUL",
                             filenamePrefix=self.filenamePrefix,
                             testVerdictDir=self.get_testVerdictDir())

        else:

            writeVerdictFile(verdict="INCONCLUSIVE",
                                      descr=ec.error_table[ec.ERRCODE_DOWNLOAD_GENERIC_FAIL],
                                      filenamePrefix=self.filenamePrefix,
                                      testVerdictDir=self.get_testVerdictDir())
            return download_fw_result

        return (res)

    def verifyFlash(self, iterNum):

        if modem.check_for_modem_port() == tg.FAIL:

            sys.exit(ec.ERRCODE_COM_PORT_DETECT)

        # auto-detect com ports after reboot
        # as these may have changed
        print "Will now try to display the modem information"
        modeminfo=""
        try:
            modemObj = modem.serialComms(timeout = 5)
        except:
            print'##### Fatal error - cannot communicate with modem com port for branch %s, %s, flash verification after reboot #####' %(self.branch, self.perforce_cl)
            sys.exit(ec.ERRCODE_COM_PORT_DETECT)

        modem_state = modemObj.check_state()
        modeminfo = modemObj.getInfo()
        modemObj.close()

        if modem_state == ec.ERRCODE_COM_PORT_DETECT:

            print'##### Fatal error - cannot communicate with modem com port for branch %s, %s after flash and reboot #####' %(self.branch, self.perforce_cl)

            sys.exit(ec.ERRCODE_COM_PORT_DETECT)

        elif modem_state == ec.ERRCODE_AT_PORT:

            print'##### Flash unsuccessful - cannot communicate with modem AT port for branch %s, %s after flash and reboot #####' %(self.branch, self.perforce_cl)
            print "Flash retry iteration %s of %s" %(iterNum + 1, self.maxNumRetries)

            return (ec.ERRCODE_AT_PORT)

        elif modem_state == ec.ERRCODE_WRONG_MODE:

            print'##### Flash unsuccessful - modem is in boot loader mode 1 for branch %s, %s after flash and reboot #####' %(self.branch, self.perforce_cl)
            print "Flash retry iteration %s of %s" %(iterNum + 1, self.maxNumRetries)

            return (ec.ERRCODE_WRONG_MODE)

        test_build_cl = modem.get_build_info_wrapper()

        if test_build_cl == self.perforce_cl:

            print modeminfo

            if self.p4webrev:

                print'##### Software Build %s %s p4webrev %s flashed #####' %(self.branch, test_build_cl, self.p4webrev)

            else:

                print'##### Software Build branch %s %s flashed #####' %(self.branch, test_build_cl)

            print'##### Variant %s flashed #####' %self.variant

            return (ec.ERRCODE_SUCCESS)

        else:

            if self.p4webrev:

                print '##### Software Build branch %s %s p4webrev %s flash failed #####' %(self.branch,test_build_cl, self.p4webrev)

            else:

                print '##### Software Build branch %s %s flash failed #####' %(self.branch, self.perforce_cl)

            return (ec.ERRCODE_FLASH_FAILURE)


if __name__ == '__main__':

    import logging

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'

    loglevel = 'DEBUG'

    cfg_multilogging(loglevel, logfile)

    logger=logging.getLogger(logname)


    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

    results_dir = cmdpath

    SUCCESS = 0

    variant = {1:'i500-121-1725-ti-att-mbim', 2:'nvidia-p2341-win7_internal'}[2]

    branch = {1:'main.br', 2:'pl1_dev.br', 3:'cr4.br'}[2]

    jenkins = {}

    # indicates whether to use the command line or not
    # not using the comand line allows execution from IDE
    # rather than specifying options from command line
    use_command_line_bool = 1

    if use_command_line_bool:

        try:
            jenkins = testBuild.extract_cmd_line_options()
        except:
            print traceback.format_exc()
            print "failed to parse the command line options"
            sys.exit(ec.ERRCODE_COMMAAND_LINE_OPTION_FAIL)

        assert jenkins['url'], 'url is not given on the command line'

        branch = reg_expr.get_branch_from_url(url=jenkins['url'])

        variant = reg_expr.get_variant_from_url(url=jenkins['url'])

        if not variant:
            print "Cannot extract variant from %s" %jenkins['url']
            sys.exit(ec.ERRCODE_COMMAAND_LINE_OPTION_FAIL)
        else:
            jenkins['variant'] = variant
            if jenkins['variant'] in testBuild.get_supported_variant_list():
                pass
            else:
                print "variant %s is not supported" %jenkins['variant']
                print "list of supported variants is %s" % get_supported_variant_list()
                sys.exit(ec.ERRCODE_COMMAAND_LINE_OPTION_FAIL)


    else:

        jenkins['variant'] = variant

        # if "" get the latest url from autobuild for the branch in question
        jenkins['url'] = ""

        jenkins['special_build'] = 0

    try:

        print "Jenkins url: %s" %(jenkins['url'])

        print "Jenkins branch: %s" %branch

        print "variant = %s" %jenkins['variant']

        if jenkins['special_build']:

            print "Special build selected!"


        # if no URL supplied then download the latest URL from branch
        my_download = testBuild.DownloadPackage(variant=jenkins['variant'], branch = branch,
                                                http_build_url = jenkins['url'],
                                                b_special_build = jenkins['special_build'])

        if my_download.download_modem_binaries(param='ristretto_package' ) == SUCCESS:

            writeVerdictFile(verdict="PASS", descr="PASS")

        else:

            writeVerdictFile(verdict="INCONCLUSIVE", descr="DOWNLOAD_FAIL_CODE_UNDEF")

        flash_dir = my_download.getFlashBinDir()

        tools_dir = my_download.get_tools_dir()

        fw_update = TestFirmwareUpdate(variant=jenkins['variant'],
                                       autobuild_url = my_download.http_build_url,
                                       tools_dir = tools_dir,
                                       flash_binaries_dir = flash_dir,
                                       p4webrev=my_download.get_p4WebTxt(),
                                       branch = branch,
                                       results_dir=results_dir)

        status = fw_update.test_FirmwareUpdate()


        if status == ec.ERRCODE_SUCCESS:

            print "Return code : %s, flash successful" %status

        else:

            print "Return code: %s, flash unsuccessful" %status


    except SystemExit:

        exc_info = sys.exc_info()

        state=int('%s' % exc_info[1])

        writeVerdictFile(verdict="INCONCLUSIVE", descr=ec.error_table[state])

        print "Return code : %s, flash unsuccessful, cause %s" %(state, ec.error_table[state])




