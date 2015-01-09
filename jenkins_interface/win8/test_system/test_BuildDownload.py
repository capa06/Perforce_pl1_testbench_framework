#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        BuildDownload
# Purpose:
#
# Author:      joashr
#
# Created:     14/08/2013

#-------------------------------------------------------------------------------

from urllib import urlopen

import os,re,sys,shutil

(abs_path, name)=os.path.split(os.path.abspath(__file__))

try:
    import test_env
except ImportError:
    test_env_dir=os.sep.join(abs_path.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


import subprocess

import time

import traceback

import pl1_testbench_framework.common.com.modem as modem

import pl1_testbench_framework.common.globals.test_globals as tg

from pl1_testbench_framework.common.com.Serial_ComPortDet import auto_detect_port, poll_for_port

from pl1_testbench_framework.common.utils.os_utils import insertPause

from pl1_testbench_framework.common.instr.PsuBench import PsuCheckOn, PsuBenchOn, PsuBenchOff, PsuBenchPowerCycle

from pl1_testbench_framework.jenkins_interface.common.parser.testConfigParser import TestConfigParser

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as ec

from pl1_testbench_framework.jenkins_interface.common.utils.csv_verdict import writeVerdictFile, removeVerdictFile

import pl1_testbench_framework.jenkins_interface.common.parser.reg_expr as reg_expr



def run_cmd(cmd, shell=True, cwd=None, timeout=120, time_step=0.5):

    # Utility function to run a command as a subprocess with a timeout

    print "%s" % (cmd)

    if cwd is None:

        sub_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

    else:

         sub_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, cwd=cwd)

    remaining_time=timeout

    while remaining_time>=0 and sub_process.poll() is None:

        time.sleep(time_step)

        remaining_time-=time_step


    StDout, StDerr = sub_process.communicate()

    if StDout != "":

        print "cmd output => %s" %StDout

    if StDerr != "":

        print "err output => %s" %StDerr

    if sub_process.poll() is None:

        print "=> Timeout exceeded"

        StStatus=sub_process.poll()

        return sub_process,StDout,StDerr,StStatus

    return None

'''
def check_for_modem_port():

    func_name = sys._getframe(0).f_code.co_name

    logger = logging.getLogger(__name__ + func_name)

    if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

        logger.info("modem com port successfully found")

        insertPause(tsec=10, desc="delay after finding modem port")

        return tg.SUCCESS

    else:

        logger.info("modem com port not found")

        return tg.FAIL
'''

def get_supported_variant_list():

    supported_variant_list = ['i500-121-1725-ti-att-mbim',
                              'nvidia-p2341-win7_internal']
    return supported_variant_list


class DownloadPackage(object):

    SUPPORTED_VARIANT_LIST = get_supported_variant_list()

    def __init__(self, variant, branch, http_build_url="", b_special_build = 0,
                 testVerdictFileDir=""):


        xmlfile = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'test_config.xml'])

        testConfigObj = TestConfigParser(xmlfile=xmlfile, variant=variant)

        self.psu_gwip                  = testConfigObj.get_psu_gwip()
        self.psu_gpib                  = testConfigObj.get_psu_gpib()

        self.ristretto_package = False

        self.test_system_root_dir = os.environ['TEST_SYSTEM_ROOT_FOLDER']


        pl1_framework_sw_tools_dir = (os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface']+['common']+['swtools']))

        self.common_lib_tools_dir = (os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface']+['win8']+['lib']+['tools']))

        # refers to main.br mapped to //swtools/main.br
        sw_tools_main_br_dir = (os.sep.join(pl1_framework_sw_tools_dir.split(os.sep)[:]+['main.br']))

        # refer to drivers mapped to //software/main.br/drivers in perforce
        # placed in the same directory in pl1_testbench_framework for convenience
        main_br_dir = sw_tools_main_br_dir

        self.sw_tools_release_br_dir = (os.sep.join(pl1_framework_sw_tools_dir.split(os.sep)[:]+['release.br']))

        # directory for icera_datafile.exe
        self.modem_utils_dir = (os.sep.join(sw_tools_main_br_dir.split(os.sep)[:]+['modem-utils']))

        self.flash_bin_dir = False

        self.build_dir = False

        self.download_unstrip_package = False

        self.drivers_dir = (os.sep.join(pl1_framework_sw_tools_dir.split(os.sep)[:]+['drivers']))

        if variant not in self.SUPPORTED_VARIANT_LIST:
            print "variant %s is not currently supported" %variant
            print "list of supported variants are %s" %self.SUPPORTED_VARIANT_LIST
            sys.exit(ec.ERRCODE_UNSUPPORTED_VARIANT)

        self.variant = variant

        self.build_dir = r'C:\Build'

        base_build_dir = os.path.join(self.build_dir, 'Firmwares')

        self.branch_name = branch

        self.branch_build_dir = os.path.join(base_build_dir, branch)

        self.http_build_url = http_build_url

        self.b_special_build = b_special_build

        self.build_cl_dir= ""

        self.build_url = ""

        self.target_cl = ""

        self.special_build_dirname = ""

        self.p4WebTxt = ""

        self.chip_id_filename = "chip_id.txt"

        self.testVerdictFileDir= testVerdictFileDir

        removeVerdictFile(testVerdictDir=self.testVerdictFileDir)

        if self.b_special_build:

            self.special_build_dirname = "CL_Special_build"

            print "Special build has been selected"


        #power_cycle_modem()
        PsuBenchPowerCycle(psu_gwip=self.psu_gwip,
                           psu_gpib=self.psu_gpib,
                           setVolts=3.8,
                           Imax_A=5)

        if modem.check_for_modem_port() == tg.FAIL:

            sys.exit(ec.ERRCODE_COM_PORT_DETECT)


    def log_message(self,info,text):

        print '>>>>> '+info+': '+text

        return



    def report_error(self,text):

        print '>>>>> '+text

        return



    def CheckDirPackage(self, CL_Dir):

        if os.path.isdir(os.path.join(self.branch_build_dir,self.variant)) == True:

            if os.path.isdir(os.path.join(self.branch_build_dir,self.variant,CL_Dir)) == False:

                os.makedirs(os.path.join(self.branch_build_dir,self.variant,CL_Dir))

        else:

            os.makedirs(os.path.join(self.branch_build_dir,self.variant))

            if os.path.isdir(os.path.join(self.branch_build_dir,self.variant,CL_Dir)) == False:

                os.makedirs(os.path.join(self.branch_build_dir,self.variant,CL_Dir))


    def get_tools_dir(self):

        # this is the swtools release directory
        return self.sw_tools_release_br_dir


    def get_modem_utils_dir(self):

        return self.modem_utils_dir

    def get_drivers_dir(self):

        return self.drivers_dir

    def get_build_url(self):

        if self.http_build_url:

            matchObj = re.match( r'http:(.*)', self.http_build_url, re.M|re.I)

            if matchObj:

                self.build_url =  matchObj.group(1)

                print "Jenkins Build URL %s" %self.build_url

            else:

                print "Url link %s is in the wrong format" %self.http_build_url

                sys.exit(ec.ERRCODE_URL_WRONG_FORMAT)

        else:

            if self.branch_name == 'pl1_dev.br':

                self.build_url =reg_expr.get_latest_url_from_autobuild("//software/teams/phy/pl1_dev.br/", self.variant)

            elif self.branch_name == 'main.br':

                self.build_url =reg_expr.get_latest_url_from_autobuild("//software/main.br/", self.variant)

            elif self.branch_name == 'rf_dev.br':

                self.build_url =reg_expr.get_latest_url_from_autobuild("//software/teams/phy/rf_dev.br", self.variant)

            elif self.branch_name == 'pl1_stable.br':

                self.build_url = reg_expr.get_latest_url_from_autobuild("//software/teams/phy/pl1_stable.br", self.variant)

            elif self.branch_name == 'cr4.br':

                self.build_url =reg_expr.get_latest_url_from_autobuild("//software/releases/core/cr4.br/", self.variant)

            else:

                print "branch %s not supported" %self.branch_name

                sys.exit(ec.ERRCODE_BRANCH_NOT_SUPPORTED)

            print "Latest build URL from Autobuild log file for %s" %(self.branch_name)

            print "%s" %self.build_url

        self.http_build_url = 'http:'+ self.build_url

    def removDir(self, path):

        if os.path.isdir(path):

            try:

                shutil.rmtree(path)

                print "rmtree %s" %path

            except WindowsError:

                print "cannnot remove directory %s, check that the file(s) within this dir are not being used by another process" %path

                print "continuing anyway"


    def rm_old_build_dirs(self):

        abs_variant_path = os.path.join(self.branch_build_dir, self.variant)

        if os.path.exists(abs_variant_path):

            dirList = [ listObj for listObj in os.listdir(abs_variant_path) if os.path.isdir(os.path.join(abs_variant_path, listObj))]

            sortedDirList = sorted(dirList)

            numDir = len(sortedDirList)

            numDirToKeep = 5

            if numDir > numDirToKeep:

                dirToDeleteList = sortedDirList[:(numDir-numDirToKeep)]

                for dirname in dirToDeleteList:

                    dirpath = os.path.join(abs_variant_path, dirname)

                    self.removDir(dirpath)
        else:

            print "directory path %s does not exist" %(abs_variant_path)

            print "No direcories will be removed"

    def set_target_cl(self, target_cl_str = ""):

        self.target_cl = target_cl_str

    def get_target_cl(self):

        return self.target_cl


    def checkPackageCL(self, cl_str, package_str):

        target_cl_str = ""

        target_cl_str =reg_expr.extract_target_cl(url_link = self.http_build_url)

        self.target_cl = target_cl_str

        if self.target_cl == cl_str:

            print "target cl: %s matches package_cl: %s in %s" %(self.target_cl, cl_str, package_str)

        else:

            print "target cl: %s does not match package_cl: %s in %s" %(self.target_cl, cl_str, package_str)

            print "Autobuild package build discrepancy!!"

            print "Abandoning test..."

            sys.exit(ec.ERRCODE_CHECK_PKG_CL_FAIL)

    def CheckFlashDir(self):

        ristretto_package = reg_expr.get_ristretto_package(self.http_build_url)

        if ristretto_package != None:

            CL_Dir = re.compile(r'CL[0-9]+').findall(ristretto_package)[0]

            self.checkPackageCL(cl_str=CL_Dir, package_str = ristretto_package)

            flash_binaries_dirname = "binaries_%s" %(self.variant)

            ristrettoDir = "ristretto_package_%s_%s" %(self.variant, CL_Dir)

            flashDirToCheck = os.path.join(self.branch_build_dir, self.variant, CL_Dir,  ristrettoDir, flash_binaries_dirname)

            print "Check if %s exists" %(flashDirToCheck)

            if os.path.exists(flashDirToCheck):

                print '##### Flash binaries directory already exists #####'

                self.setFlashBinDir(flashDirToCheck)

                # read chip id from modem
                current_chip_id  = modem.get_chip_id_wrapper()

                # now check the previous chip id to ensure that the board has not changed
                chip_file_full_path = (os.path.join(self.getFlashBinDir(), self.chip_id_filename))

                if os.path.isfile(chip_file_full_path):

                    chip_id_from_file = self.read_chip_id_from_file()

                    if chip_id_from_file == current_chip_id:

                        print "current chip id %s matches chip id %s read from file" %(current_chip_id, chip_id_from_file)

                        return True

                    else:

                        print "current chip id %s does not match chip id %s read from file!" %(current_chip_id, chip_id_from_file)

                        print "Board change detected. Will recreate device config flash file"

                        self.write_chip_id_file(data=current_chip_id)

                        self.recreate_device_config_flash_file(chip_id=current_chip_id)

                        return True

                else:

                    print "Cannot find chip_id from %s" %self.getFlashBinDir()

                    print "Will recreate device config flash file"

                    self.write_chip_id_file(data=current_chip_id)

                    self.recreate_device_config_flash_file(chip_id=current_chip_id)

                    return True

            else:

                # flashDirToCheck does not exist
                return False

        return False

    def recreate_device_config_flash_file(self, chip_id):

        deviceConfig_bin_path = (os.path.join(self.getFlashBinDir(), "deviceConfig.bin"))

        print "Will try to remove %s" %deviceConfig_bin_path

        self.remove_file(filepath=deviceConfig_bin_path)

        self.create_device_bin_file(chip_id=chip_id)


    def setFlashBinDir(self, flash_bin_dir):

        self.flash_bin_dir = flash_bin_dir

        print "flash bin dir = %s" %(flash_bin_dir)

    def getFlashBinDir(self):

        return self.flash_bin_dir

    def getBranchBuildDir(self):

        return self.branch_build_dir

    def create_device_bin_file(self, chip_id):

        OEM_FACT_KEY_PATH = (os.sep.join(self.get_drivers_dir().split(os.sep)[:]+['private', 'arch', 'keys', 'dev-OEM_FACT', 'key0']))

        deviceConfig_xml_path = (os.path.join(self.flash_bin_dir, "deviceConfig.xml"))

        icera_datafile_exe_path = (os.path.join(self.get_modem_utils_dir(), "icera_datafile.exe"))

        #run_cmd("%s --asn1_cust none -k %s --chip 9040 -c %s --pcid %s" %(icera_datafile_exe_path, OEM_FACT_KEY_PATH, deviceConfig_xml_path, chip_id ))

        run_cmd("%s -k %s --chip 9040 -c %s --pcid %s" %(icera_datafile_exe_path, OEM_FACT_KEY_PATH, deviceConfig_xml_path, chip_id ))

        run_cmd('%s %s %s' % ('rename', 'local_deviceConfig.wrapped', 'deviceConfig.bin'))

        run_cmd('%s %s %s' % ('move', 'deviceConfig.bin', self.flash_bin_dir))


    def remove_file(self, filepath):

        try:

            os.remove(filepath)

            print "file removal successful"

        except WindowsError:

            print "WindowsError: Cannot remove %s" %filepath

            print "Continuing anyway ..."


    def read_chip_id_from_file(self):

        chip_id_file_path = (os.path.join(self.getFlashBinDir(), self.chip_id_filename))

        fileToRead = open(chip_id_file_path)

        line = fileToRead.readline()

        chip_id = line.rstrip()

        return chip_id


    def write_chip_id_file(self, data=""):

        dest_chip_file_full_path = (os.path.join(self.flash_bin_dir, self.chip_id_filename))

        # write file to local directory

        origin_chip_file_full_path = (os.path.join(self.test_system_root_dir, self.chip_id_filename))

        with open(origin_chip_file_full_path, 'w') as fd:

            fd.write("%s" %data)

        fd.close

        # move chip_id file to binaries directory

        if os.path.isfile(dest_chip_file_full_path):

            print "will remove existing chip_id file at %s" %dest_chip_file_full_path

            self.remove_file(dest_chip_file_full_path)

        run_cmd('%s %s %s' % ('move', origin_chip_file_full_path, self.flash_bin_dir))


    def create_device_config_flash_file(self):

        chip_id = ""

        maxNumRetries = 2

        retryNum = 0

        while retryNum < maxNumRetries:

            chip_id = modem.get_chip_id_wrapper()

            if chip_id:

                self.create_device_bin_file(chip_id=chip_id)

                self.write_chip_id_file(data=chip_id)

                break

            else:

                print "Retry %s of %s" %((retryNum+1),maxNumRetries)

                print "cannot create local deviceConfig.bin file"

                try:

                    PsuBenchOff(psu_gwip=self.psu_gwip, psu_gpib=self.psu_gpib)

                except:

                    print "unable to switch off psu"

                    sys.exit(ec.ERRCODE_PSU_COMM_ERR)

                time.sleep(10)

                try:

                    PsuBenchOn(psu_gwip=self.psu_gwip, psu_gpib=self.psu_gpib)

                except:

                    sys.exit(ec.ERRCODE_PSU_COMM_ERR)

                if poll_for_port(portName="Modem_port", timeout_sec=60, poll_time_sec=5):

                    print "modem com port successfully found"

                    time.sleep(10)

                    chip_id = modem.get_chip_id_wrapper()

                    self.create_device_bin_file(chip_id=chip_id)

                    break

                else:

                    print "modem com port not found"

                    print"Not able to obtain the chip id!"

                    sys.exit(ec.ERRCODE_COM_PORT_DETECT)


            retryNum +=1

    def create_platform_config_flash_file(self):

        if self.variant == 'i500-121-1725-ti-att-mbim':

            platform_config_xml_path = (os.path.join(self.flash_bin_dir, "platformConfig_i500-121-1725-ti_revb01_100.xml"))

        elif self.variant == 'nvidia-p2341-win7_internal':

            platform_config_xml_path = (os.path.join(self.flash_bin_dir, "platformConfig_p2341.xml"))

        else:

            sys.exit(ec.ERRCODE_UNSUPPORTED_VARIANT)

        icera_datafile_exe_path = (os.path.join(self.get_modem_utils_dir(), "icera_datafile.exe"))

        run_cmd("%s --platcfg %s" %(icera_datafile_exe_path, platform_config_xml_path ))

        run_cmd('%s %s %s' % ('rename', 'local_platformConfig.wrapped', 'platformConfig.bin'))

        run_cmd('%s %s %s' % ('move', 'platformConfig.bin', self.flash_bin_dir))


    def create_product_config_flash_file(self):


        OEM_FIELD_KEY_PATH = (os.sep.join(self.get_drivers_dir().split(os.sep)[:]+['private', 'arch', 'keys', 'dev-OEM_FIELD', 'key0']))


        product_config_xml_path = (os.path.join(self.flash_bin_dir, "productConfig.xml"))

        icera_datafile_exe_path = (os.path.join(self.get_modem_utils_dir(), "icera_datafile.exe"))

        run_cmd("%s --asn1_cust none -k %s --chip 9040 -p %s -n 0" %(icera_datafile_exe_path, OEM_FIELD_KEY_PATH, product_config_xml_path ))

        run_cmd('%s %s %s' % ('rename', 'local_productConfig.wrapped', 'productConfig.bin'))

        run_cmd('%s %s %s' % ('move', 'productConfig.bin', self.flash_bin_dir))


    def set_build_cl_dir(self, abs_path_dir):

        self.build_cl_dir = abs_path_dir

    def get_build_cl_dir(self):

        return self.build_cl_dir

    def set_p4WebTxt(self, txt):

        self.p4WebTxt = txt

    def get_p4WebTxt(self):

        return(self.p4WebTxt)

    def download_modem_binaries(self, param):
        """
        download flash file binaries to PC
        if download successful return 0
        else sys.exit(ERROR_CODE) this hould be
        handled by outer function try, execpt
        """
        SUCCESS = 0

        ret_val = SUCCESS

        self.get_build_url()

        if self.b_special_build == 0:

            flash_package_exists = self.CheckFlashDir()

            if flash_package_exists:

                return ret_val

        self.ristretto_package = False

        url = self.http_build_url

        self.modembuild_url= url

        package_exists = False

        build_cl_dir = ""

        if param == 'ristretto_package':

            self.ristretto_package = reg_expr.get_ristretto_package(self.modembuild_url)

            if self.ristretto_package != None:

                self.rm_old_build_dirs()

                if self.b_special_build == 0:

                    CL_Dir = re.compile(r'CL[0-9]+').findall(self.ristretto_package)[0]

                else:

                    CL_Dir = self.special_build_dirname


                build_cl_dir = os.path.join(self.branch_build_dir,self.variant,CL_Dir)

                self.set_build_cl_dir(build_cl_dir)

                if self.b_special_build:

                    self.removDir(build_cl_dir)

                self.CheckDirPackage(CL_Dir)


        download_cmd = "wget -q"

        if self.modembuild_url.endswith("/"):

            self.modembuild_url=self.modembuild_url[:-1]


        if self.ristretto_package:

            # Ristretto Package

            print '##### Download Ristretto Package #####'

            self.ristretto_package_url = "/".join([self.modembuild_url , self.ristretto_package])

            self.unstrip_package_url = "/".join([self.modembuild_url , 'unstripped-exe.tar.gz'])

            self.log_message('INFO','Ristretto Package URL: %s' % self.ristretto_package_url)

            self.log_message('INFO','%s %s' %(download_cmd, self.ristretto_package_url))

            error = False; error1 = False

            error = run_cmd('%s %s' % (download_cmd, self.ristretto_package_url))

            if self.download_unstrip_package:

                error1 = run_cmd('%s %s' % (download_cmd, self.unstrip_package_url))

            if error or error1:

                self.report_error('Failed to download Ristretto package')

                sys.exit(ec.ERRCODE_DOWNLOAD_RISTR_PKG_FAIL)

            # Get P4WebRev file

            self.ristretto_p4webrev_url = "/".join([self.modembuild_url , 'P4WEBREV'])

            error = run_cmd('%s %s' % (download_cmd, self.ristretto_p4webrev_url))

            if error:

                self.report_error('Failed to download P4WEBREV for Ristretto package')

                sys.exit(ec.ERRCODE_P4WEBREV_DOWNLOAD_FAIL)

            else:

                P4WebTxt = urlopen('P4WEBREV').read().strip()

                print '>>> P4WebRev:',P4WebTxt

                if P4WebTxt != '':

                    self.set_p4WebTxt(txt=P4WebTxt)

                    run_cmd('%s %s %s' % ('move', 'P4WEBREV',build_cl_dir))

                else:

                    run_cmd("del "+ 'P4WEBREV')

            self.log_message('INFO','Untar Ristretto Package')

            if (sys.platform == 'win32'):

                print "tools dir : %s" %self.common_lib_tools_dir

                tar_extracter_path = (os.path.join(self.common_lib_tools_dir, "TarTool.exe"))

                run_cmd("%s %s " %(tar_extracter_path, self.ristretto_package))

                if self.download_unstrip_package:

                    run_cmd("%s unstripped-exe.tar.gz" %tar_extracter_path)

                matchObj = re.match( r'(.*ristretto_package.*).tar.gz', self.ristretto_package, re.M|re.I)

                if matchObj:

                    unzipped_ristretto_dir = matchObj.group(1)

                    flash_binaries_dirname = "binaries_%s" %(self.variant)


                    run_cmd('%s %s %s' % ('move', unzipped_ristretto_dir, build_cl_dir))

                    flash_bin_dir = os.path.join(build_cl_dir, unzipped_ristretto_dir, flash_binaries_dirname)

                    self.setFlashBinDir(flash_bin_dir)

                    self.create_platform_config_flash_file()

                    self.create_device_config_flash_file()

                    if self.download_unstrip_package:

                        run_cmd('%s %s %s' % ('move', 'unstripped-exe', build_cl_dir))

            else:

                run_cmd("tar -zxf " + self.ristretto_package + " -C " + self.working_dir )

                run_cmd("tar -zxf " + 'unstripped-exe.tar.gz' + " -C " + self.working_dir )


            run_cmd("del "+ self.ristretto_package)

            if self.download_unstrip_package:

                run_cmd("del "+ 'unstripped-exe.tar.gz')

            return ret_val

        else:

            self.report_error('No Ristretto package for: %s' % (self.modembuild_url))

            sys.exit(ec.ERRCODE_NO_RISTR_PKG)


def extract_cmd_line_options():
    import argparse

    description_msg="""
    Download ristretto package build
       python test_BuildDownload.py -u=http://bs.nvidia.com/systems/datacard-builds/software/releases/core/cr5.br/CL796291-90aaf35f/i500-121-1725-ti-att-mbim -g
       python test_execution.py -r=WCDMA -u=http://bs.nvidia.com/systems/datacard-builds/software/releases/core/cr5.br/CL796291-90aaf35f/i500-121-1725-ti-att-mbim -t=per_cl -g
    """
    parser = argparse.ArgumentParser(description=description_msg)
    parser.add_argument('-u', '--url', type = str, help='build URL')
    parser.add_argument('-g', '--genericBuild', help="special build option", action="store_true")

    args = parser.parse_args()

    return {'url':args.url, 'special_build':args.genericBuild}

if __name__ == '__main__':

    import logging

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'

    loglevel = 'DEBUG'

    cfg_multilogging(loglevel, logfile)

    logger=logging.getLogger(logname)

    SUCCESS = 0

    variant = {1:'i500-121-1725-ti-att-mbim', 2:'nvidia-p2341-win7_internal'}[2]

    branch = {1:'main.br', 2:'pl1_dev.br', 3:'cr4.br'}[2]

    jenkins = {}

    # indicates whether to use the command line or not
    # not using the comand line allows execution from IDE
    # rather than specifying options from command line
    use_command_line_bool = 0

    if use_command_line_bool:

        try:
            jenkins = extract_cmd_line_options()
        except:
            print traceback.format_exc()
            print "failed to parse the command line options"
            sys.exit(ec.ERRCODE_COMMAAND_LINE_OPTION_FAIL)

        assert jenkins['url'], 'url is not given on the command line'
        branch = reg_expr.get_branch_from_url(url=jenkins['url'])
        variant =reg_expr.get_variant_from_url(url=jenkins['url'])
        if not variant:
            print "Cannot extract variant from %s" %jenkins['url']
            sys.exit(ec.ERRCODE_COMMAAND_LINE_OPTION_FAIL)
        else:
            jenkins['variant'] = variant
            if jenkins['variant'] in get_supported_variant_list():
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


    print "Jenkins url: %s" %(jenkins['url'])

    print "Jenkins branch: %s" %branch

    print "variant = %s" %jenkins['variant']

    if jenkins['special_build']:

        print "Special build selected!"

    try:

        # hard code use of power supply for test purposes only
        # so that we can run from IDE rather than DOS command prompt
        # where the power supply option has to be explicitly specified
        my_download = DownloadPackage(variant = jenkins['variant'],
                                      branch = branch,
                                      http_build_url = jenkins['url'],
                                      b_special_build = jenkins['special_build'])

        ## ------------------------------------ RISTRETTO --------------------------------------------- ##

        if my_download.download_modem_binaries(param='ristretto_package' ) == SUCCESS:

            writeVerdictFile(verdict="PASS", descr="PASS")

        else:

            writeVerdictFile(verdict="INCONCLUSIVE", descr="DOWNLOAD_FAIL_CODE_UNDEF")


    except SystemExit:

        exc_info = sys.exc_info()

        state=int('%s' % exc_info[1])
        print state

        writeVerdictFile(verdict="INCONCLUSIVE", descr=ec.error_table[state])

        print "Return code : %s, flash unsuccesful, cause %s" %(state, ec.error_table[state])


    except Exception:

        print traceback.format_exc()

        ret_code = ec.ERRCODE_UNHANDLED_EXECEPTION

        print "return code: %s, cause %s" %(ec.ERRCODE_UNHANDLED_EXECEPTION,
                                            ec.error_table[ec.ERRCODE_UNHANDLED_EXECEPTION])

        writeVerdictFile(verdict="INCONCLUSIVE", descr=ec.error_table[ec.ERRCODE_UNHANDLED_EXECEPTION])
