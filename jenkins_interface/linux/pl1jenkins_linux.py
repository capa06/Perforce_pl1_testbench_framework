#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        pl1jenkins_linux.py
# Purpose:
#              Jenkins interface for starting the pl1testbench
#              (Linux version)
# Author:      fsaracino
#
# Created:     14/04/2014
#
#-------------------------------------------------------------------------------

from urllib import urlopen
from xml.etree.ElementTree import parse

import os
import sys
import re
import logging
import time
import shutil

import traceback

# ********************************************************************
# DEFINE USER'S PATHS
# ********************************************************************

(cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))

try:
    os.environ['PL1JENKINS_ROOT_FOLDER']
except:
    os.environ['PL1JENKINS_ROOT_FOLDER']=os.sep.join(cmdpath.split(os.sep)[:-3]+['pl1jenkins_linux'])


# ********************************************************************
# IMPORT USER DEFINED PATHS
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','common']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','common','com']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','common','config']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','common','tools']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','tools']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib','tools','bin']))
sys.path.append(os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['instr']))


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from cfg_multilogging import cfg_multilogging

from utilities_file import wgetFile, untarFile, removeDir, runCmd, runTestbench

from subprocess_helper import SubProcess


class Struct(object): pass



class Jenkins(object):
    def __init__(self, param_s):

        # *****************************************************************
        # STATIC PROPERTIES
        # *****************************************************************

        # Test setup configuration
        self.INFO_URL                       = None
        self.LOCAL_P4_ROOT                  = None
        self.LOCAL_TMPDIR                   = os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['tmp'])
        self.LOCAL_SETUPCONFIG_XML          = os.path.join(os.environ['PL1JENKINS_ROOT_FOLDER'],'test_config.xml')


        self.TESTBENCH_DIR_ROOT             = os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:-1]+['pl1_testbench_framework'])

        self.TESTBENCH_DIR_RESULT           = { 'LTE_FDD'  : os.path.join(self.TESTBENCH_DIR_ROOT, 'lte', 'results', 'latest'),
                                                'LTE_TDD'  : os.path.join(self.TESTBENCH_DIR_ROOT, 'lte', 'results', 'latest'),
                                                'WCDMA'    : os.path.join(self.TESTBENCH_DIR_ROOT, 'wcdma', 'results', 'latest'),
                                                'RF'       : os.path.join(self.TESTBENCH_DIR_ROOT, 'pl1_rf_system', 'results', 'latest')}

        self.TESTBENCH_FILE_EXECUTABLE      = os.path.join(self.TESTBENCH_DIR_ROOT, 'run_pl1testbench_lte.py')
        self.TESTBENCH_FILE_XMLCONFIG       = os.path.join(self.TESTBENCH_DIR_ROOT, 'structxml_testconfig.xml')
        

        self.TESTBENCH_FILE_SUMMARY         = os.path.join(self.TESTBENCH_DIR_RESULT[param_s.rat], "%s_CMW500_TestReport_SUMMARY.csv" % param_s.rat)

        if param_s.rat.upper() == "RF":
            self.TESTBENCH_FILE_SUMMARY         = os.path.join(self.TESTBENCH_DIR_RESULT[param_s.rat], "%s_FACTORY_TestReport_SUMMARY.csv" % param_s.rat)


        self._jenkins_config(self.LOCAL_SETUPCONFIG_XML)

        # *****************************************************************
        # DYNAMIC PROPERTIES
        # *****************************************************************
        self.jenkins_url                    = param_s.url
        self.testbench_opt_log              = param_s.log
        self.testbench_opt_rat              = param_s.rat
        self.testbench_opt_jobtype          = param_s.jobtype

        # Select the testplan
        self.testbench_opt_test2execute     = self._set_test2execute(param_s.rat, param_s.jobtype)

        # Set parameters for downloading and flashing the package
        if 1:
            # Retrieve platform info from the URL link
            self._variant                       = self._set_variant()
            self._branch                        = self._set_branch()
            self._changelist                    = self._set_changelist()
            self._p4webrev                      = self._set_p4webrev()
            self._ristretto_package             = self._get_ristretto_package()
            self._local_toolsdir                = self._set_local_toolsdir()
            self._local_pckgdir                 = self._set_local_pckgdir()
        else:
            # Debug
            self._variant                       = "nvidia-p2341-win7"


        # Read setup specific configuration from XML file
        self._platform_tag              = None
        self._enable_scdu               = None
        self._scdu_ip                   = None

        self._enable_flash_via_debugger = None
        self._icera_ada_ip              = None
        self._icera_ada_scdu_port       = None
        self._icera_swd_scdu_port       = None

        self._enable_psu                = None
        self._psu_gwip                  = None
        self._psu_gpib                  = None

        self._test_config(self.LOCAL_SETUPCONFIG_XML)

        self.testbench_hw_psu               = { 'name':'E3631A', 'ip': None,           'gpib': self._psu_gpib }
        self.testbench_hw_lan2gpibgw        = { 'name':'E5810A', 'ip': self._psu_gwip, 'gpib': None }


        # ----------------
        # Clean folders from previous run
        self.remove_dir(self.LOCAL_TMPDIR)
        os.makedirs(self.LOCAL_TMPDIR)
        self.remove_dir(self.TESTBENCH_DIR_RESULT[self.testbench_opt_rat])

        self.scdu_off_all(self._scdu_ip, tsec=2)

    # ***************************************************************************** #
    #  PRIVATE METHODS FOR ENVIRONMENT CONFIGURATION                                #
    # ***************************************************************************** #
    def _jenkins_config(self, xmlfile):
        logger=logging.getLogger('Jenkins._jenkins_config')
        if not os.path.isfile(xmlfile):
            logger.error("Could not find XML configuration file : %s" % xmlfile)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        tree              = parse(xmlfile)
        section           = tree.find('jenkins_config')

        if not section is None:
            self.INFO_URL       = section.find('info_url').text
            self.LOCAL_P4_ROOT  = section.find('local_p4_root').text
        if 1:
            logger.info("-------------------------------------------")
            logger.info("  info_url                  : %s" % self.INFO_URL)
            logger.info("  local_p4 root             : %s" % self.LOCAL_P4_ROOT)
            logger.info("-------------------------------------------")


    def _test_config(self, xmlfile):
        logger=logging.getLogger('Jenkins._get_test_config')
        if not os.path.isfile(xmlfile):
            logger.error("Could not find XML configuration file : %s" % xmlfile)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        tree              = parse(xmlfile)
        #mapping           = {}

        section            = tree.find(self._variant)
        if not section is None:
            self._platform_tag = section.find('platform_tag').text

            # Switched Cabinet Unit
            try:
                self._enable_scdu = int(section.find('enable_scdu').text)
            except ValueError:
                self._enable_scdu = 0
            self._scdu_ip = section.find('scdu_ip').text if self._enable_scdu else None

            # Icera-ada debugger
            try:
                self._enable_flash_via_debugger  = int(section.find('enable_flash_via_debugger').text)
            except ValueError:
                self._enable_flash_via_debugger  = 0

            if self._enable_flash_via_debugger:
                self._icera_ada_ip              = section.find('icera_ada_ip').text
                try:
                    self._icera_ada_scdu_port   = int(section.find('icera_ada_scdu_port').text)
                except ValueError:
                    logger.error("invalid configuration for the icera-ada scdu port")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

            # AC adapter configuration
            try:
                self._enable_psu     = int(section.find('enable_psu').text)
            except ValueError:
                self._enable_psu     = 0

            if self._enable_psu:
                self._icera_swd_scdu_port = None
                self._psu_gwip = section.find('psu_gwip').text
                try:
                    self._psu_gpib    = int(section.find('psu_gpib').text)
                except ValueError:
                    logger.error("invalid configuration for PSU GPIB port")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            else:
                try:
                    self._icera_swd_scdu_port = int(section.find('icera_swd_scdu_port').text) if self._enable_scdu else None
                except ValueError:
                    logger.error("invalid configuration for the icera-swd scdu port")
                    sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        else:
            logger.error("unable to locate variant: %s" % self._variant)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        logger.info("-------------------------------------------")
        logger.info("VARIANT : %s" % self._variant)
        logger.info("-------------------------------------------")
        logger.info("  platform_tag              : %s" % self._platform_tag)
        logger.info("  enable_scdu               : %s" % self._enable_scdu)
        logger.info("  scdu_ip                   : %s" % self._scdu_ip)
        logger.info("  enable_flash_via_debugger : %s" % self._enable_flash_via_debugger)
        logger.info("  icera_ada_ip              : %s" % self._icera_ada_ip)
        logger.info("  icera_ada_scdu_port       : %s" % self._icera_ada_scdu_port)
        logger.info("  icera_swd_scdu_port       : %s" % self._icera_swd_scdu_port)
        logger.info("  enable_psu                : %s" % self._enable_psu)
        logger.info("  psu_gwip                  : %s" % self._psu_gwip)
        logger.info("  psu_gpib                  : %s" % self._psu_gpib)

        logger.info("-------------------------------------------")


    def _set_variant(self):
        logger=logging.getLogger('Jenkins._set_variant')
        variant_url=os.path.join(self.jenkins_url,'VARIANT')
        try:
            txt = urlopen(variant_url).read()
        except IOError:
            logger.error("URL failure: %s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_TIMEOUT)

        variant=txt.replace('\n','')
        if variant == "":
            logger.error("NO VARIANT INFO DETECTED")
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        logger.info("variant : %s" % variant)
        return variant


    def _set_branch(self):
        logger=logging.getLogger('Jenkins._set_branch')
        branch_url=os.path.join(self.jenkins_url,'BRANCH')
        try:
            txt = urlopen(branch_url).read()
        except IOError:
            logger.error("URL failure: %s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_TIMEOUT)

        branch=txt.replace('\n','')
        if branch == "":
            logger.error("NO BRANCH INFO DETECTED")
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        logger.info("branch : %s" % branch)
        return branch


    def _set_changelist(self):
        logger=logging.getLogger('Jenkins._set_changelist')
        changelist_url=os.path.join(self.jenkins_url,'CHANGELIST')
        try:
            txt = urlopen(changelist_url).read()
        except IOError:
            logger.error("URL failure: %s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_TIMEOUT)

        changelist=txt.replace('\n','')
        if changelist == "":
            logger.error("NO CHANGELIST INFO DETECTED")
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        logger.info("changelist : %s" % changelist)
        return changelist


    def _set_p4webrev(self):
        logger=logging.getLogger('Jenkins._set_p4webrev')
        p4webrev_url=os.path.join(self.jenkins_url,'P4WEBREV')
        try:
            txt = urlopen(p4webrev_url).read()
        except IOError:
            logger.error("URL failure: %s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_TIMEOUT)

        p4webrev=txt.replace('\n','')
        logger.info("p4webrev : %s" % p4webrev)
        return p4webrev


    def _get_ristretto_package(self):
        logger=logging.getLogger('Jenkins._get_ristretto_package')
        pattern = re.compile(r"<[A|a] [H|h][R|r][E|e][F|f]=\"(ristretto_package_.+\.tar\.gz)\">")
        ristretto_package = None
        try:
            txt = urlopen(self.jenkins_url).read()
        except IOError:
            logger.error("URL failure: %s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_TIMEOUT)

        res=pattern.search(txt)
        if res:
            ristretto_package=res.group(1)
            if 1: logger.debug("FOUND RISTRETTO PACKAGE=%s in URL=%s" % (ristretto_package, self.jenkins_url))
        else:
            logger.error("RISTRETTO PACKAGE INFO NOT FOUND in URL=%s" % self.jenkins_url)
            sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
        return ristretto_package


    def _set_local_pckgdir(self):
        logger=logging.getLogger('Jenkins._set_local_pckgdir')
        local_pckgdir=os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['build'])
        if not os.path.isdir(local_pckgdir):
            logger.debug("Creating local build folder: %s" % local_pckgdir)
            os.makedirs(local_pckgdir)
        return local_pckgdir


    def _set_local_toolsdir(self):
        logger=logging.getLogger('Jenkins._set_local_toolsdir')
        local_toolsdir=os.path.join(self.LOCAL_P4_ROOT, self._branch, r"bin")

        if os.path.isdir(local_toolsdir):
            removeDir(local_toolsdir)

        try:
            logger.debug("Creating folder : %s" % local_toolsdir)
            os.makedirs(local_toolsdir)
        except:
            logger.error("Could not create folder : %s" % local_toolsdir)
            sys.exit(CfgError.ERRCODE_TEST_FAILURE)

        return local_toolsdir


    def _set_test2execute(self, rat, jobtype):
        logger=logging.getLogger('Jenkins._test2execute')
        test2execute=None

        if rat.upper()=='LTE_FDD':
            if jobtype.lower()=='per_cl':
                test2execute="structxml_testconfig_fdd_percl.xml"
            elif jobtype.lower()=='nightly':
                #test2execute="[1,11,16]"
                test2execute="structxml_testconfig_fdd_nightly.xml"
            elif jobtype.lower()=='weekly':
                #test2execute="[10]"
                test2execute="structxml_testconfig_fdd_weekly.xml"
            else:
                logger.error("INVALID %s JOB TYPE : %s" % (rat, jobtype))
                sys.exit(CfgError.ERRCODE_TEST_UNKNOWN_JOBTYPE)

            #Replace the configuration file in the pl1testbench root
            file_src = os.path.join(self.TESTBENCH_DIR_ROOT, test2execute)
            #file_dst = os.path.join(self.TESTBENCH_DIR_ROOT[self.testbench_opt_rat], "structxml_testconfig.xml")
            try:
                if os.path.isfile(self.TESTBENCH_FILE_XMLCONFIG):
                    os.remove(self.TESTBENCH_FILE_XMLCONFIG)
                shutil.copy(file_src, self.TESTBENCH_FILE_XMLCONFIG)
            except shutil.Error:
                logger.error("shutil error copying config files: (%s --> %s)" % (file_src, self.TESTBENCH_FILE_XMLCONFIG))
            except IOError:
                logger.error("IOError copying config files: (%s --> %s)" % (file_src, self.TESTBENCH_FILE_XMLCONFIG))


        elif rat.upper()=='LTE_TDD':
            if jobtype.lower()=='per_cl':
                test2execute="structxml_testconfig_tdd_percl.xml"

            # Replace the configuration file in the pl1testbench root
            file_src = os.path.join(self.TESTBENCH_DIR_ROOT, test2execute)
            #file_dst = os.path.join(self.TESTBENCH_DIR_ROOT, "structxml_testconfig.xml")
            try:
                if os.path.isfile(self.TESTBENCH_FILE_XMLCONFIG):
                    os.remove(self.TESTBENCH_FILE_XMLCONFIG)
                shutil.copy(file_src, self.TESTBENCH_FILE_XMLCONFIG)
            except shutil.Error:
                logger.error("shutil error copying config files: (%s --> %s)" % (file_src, self.TESTBENCH_FILE_XMLCONFIG))
            except IOError:
                logger.error("IOError copying config files: (%s --> %s)" % (file_src, self.TESTBENCH_FILE_XMLCONFIG))

        elif rat.upper()=='WCDMA':
            pass

        elif rat.upper()=='RF':
            pass

        else:
                logger.error("INVALID RAT : %s" % rat)
                sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)

        return test2execute



    def _poll_serial(self):
        from Serial_ComPortDet import poll_for_port

        logger=logging.getLogger('Jenkins._poll_serial')
        if poll_for_port(portName="Modem_port") is None:
            logger.error("No active serial port found")
            sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)


    # ***************************************************************************** #
    #  PRIVATE METHODS FOR CHECKING THE MODEM INFO                                  #
    # ***************************************************************************** #
    def _parse_modeminfo(self, msg_enc):
        import subprocess
        icera_aes = os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib', 'common', 'icera', 'icera-aes'])
        icera_b64 = os.sep.join(os.environ['PL1JENKINS_ROOT_FOLDER'].split(os.sep)[:]+['lib', 'common', 'icera', 'icera-b64'])
        logger=logging.getLogger('Jenkins._parse_modeminfo')
        logger.debug("decoding modem info")
        cmd='echo -n %s | %s -d | %s -d -p 9TfyKtMO+hoPyscfR15GEw8PYlzNPvMksp5wwSvxbMI=' % (msg_enc, icera_b64, icera_aes)

        res=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
        if res=="" :
            res="NA"
        else:
            res=re.sub('[\n\t\r]', '' ,res)
        return res


    def _get_branch(self, msg):
        logger=logging.getLogger('Jenkins._get_branch')
        msg_str = re.sub('[\n\t\r]', ' ' , msg)
        branch_re=re.compile(r".*Branch name\s*:\s*(\S*)\s*")
        branch=None
        if branch_re.search(msg_str):
            res=branch_re.findall(msg_str)[0]
            if (res[0:3] == "css"):
                branch=self._parse_modeminfo(res)
            else:
                branch=res
        branch=re.sub('[\n\t\r]', ' ' , branch)
        logger.debug("found branch: %s" % branch)
        return branch


    def _get_platform(self, msg):
        logger=logging.getLogger('Jenkins._platform')
        msg_str = re.sub('[\n\t\r]', ' ' , msg)
        platform_re=re.compile(r".*Platform\s*:\s*icera\.(.*?)\s*")
        platform=None
        if platform_re.search(msg_str):
            platform=platform_re.findall(msg_str)[0]
        logger.debug("found platform : %s" % platform)
        return platform


    def _get_platform_target(self, msg):
        logger=logging.getLogger('Jenkins._get_platform_target')
        platform_target='.'.join(msg.split('_'))
        logger.debug("platform target : %s" % platform_target)
        return platform_target


    def _get_variant(self, msg):
        logger=logging.getLogger('Jenkins._get_variant')
        msg_str = re.sub('[\n\t\r]', ' ' , msg)
        variant_re=re.compile(r".*Variant\s*:\s*(\S*)\s*")
        variant=None
        if variant_re.search(msg_str):
            res=variant_re.findall(msg_str)[0]
            if (res[0:3] == "css"):
                variant=self._parse_modeminfo(res)
            else:
                variant=res
        variant=re.sub('[\n\t\r]', '' , variant)
        logger.debug("found variant: %s" % variant)
        return variant


    def _get_changelist(self, msg):
        logger=logging.getLogger('Jenkins._get_changelist')
        msg_str = msg.replace('\n',' ')
        changelist_re=re.compile(r".*Changelist\s+:\s*CL(\d+)\s*")
        changelist=None
        if changelist_re.search(msg_str):
            changelist=changelist_re.findall(msg_str)[0]
        logger.debug("found changelist: %s" % changelist)
        return changelist


    # ***************************************************************************** #
    #  PRIVATE METHODS FOR VERDICT PROCESSING                                       #
    # ***************************************************************************** #
    def _create_verdict_status_file(self, filename):
        logger=logging.getLogger("Jenkins._create_verdict_status_file")

        fpath    = os.path.split(filename)[0]

        try:
            # Create destination folder if it does not exists
            if not os.path.exists(fpath):
                logger.debug("Creating destination folder: %s" % fpath)
                os.makedirs(fpath)

            # Remove existing file
            if os.path.isfile(filename):
                logger.debug("Removing existing file : %s" % filename)
                os.remove(filename)

            # Create verdict status file
            logger.debug("Creating status verdict file : %s" % filename)
            fd=open(filename, 'w')

        except IOError:
            logger.error("FAILURE CREATING VERDICT STATUS FILE: %s" % filename)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        else:
            fd.close()



    # ***************************************************************************** #
    #                          PUBLIC METHODS                                       #
    # ***************************************************************************** #
    def psu_off(self, tsec=2):
        logger=logging.getLogger('Jenkins._psu_off')
        from PsuBench import PsuBench
        psu_h=PsuBench(psu_gwip=self._psu_gwip, psu_gpib=self._psu_gpib, psu_reset=1)
        psu_h.off()
        psu_h.insert_pause(tsec)
        del psu_h
        logger.info("PSU OFF")


    def psu_on(self, tsec=25):
        logger=logging.getLogger('Jenkins.psu_on')
        from PsuBench import PsuBench
        psu_h=PsuBench(psu_gwip=self._psu_gwip, psu_gpib=self._psu_gpib, psu_reset=0)
        psu_h.on()
        psu_h.insert_pause(tsec)
        del psu_h
        logger.info("PSU ON")


    def psu_activate(self):
        logger=logging.getLogger('Jenkins.psu_activate')
        self.psu_off()
        self.psu_on()
        logger.info("PSU ACTIVATED")


    def scdu_off_all(self, scdu_ip, tsec=20):
        import pexpect, time
        tsec_offs=5
        logger=logging.getLogger('Jenkins.scdu_off_all')
        child = pexpect.spawn(r"telnet %s" % scdu_ip)
        child.expect('Username: ')
        child.sendline('jenkins\r')
        child.expect('Password: ')
        child.sendline('automation\r')
        for port_num in [1,2,7,8]: #range(1,9):
            logger.info("Turning OFF %s:.A%d ... Sleeping for %s [sec]" % (scdu_ip, int(port_num), tsec))
            cmd=r"off .A%d" % int(port_num)
            child.sendline(cmd)
            time.sleep(tsec)
        child.sendline("sleep %s" % tsec)
        child.close()
        self.insert_pause(tsec_offs)


    def scdu_off(self, scdu_ip, scdu_port, tsec=20):
        import pexpect, time
        tsec_offs=5
        logger=logging.getLogger('Jenkins.scdu_off')
        logger.info("Turning OFF %s:.A%d ... Sleeping for %s [sec]" % (scdu_ip, int(scdu_port), tsec))
        child = pexpect.spawn(r"telnet %s" % scdu_ip)
        child.expect('Username: ')
        child.sendline('jenkins\r')
        child.expect('Password: ')
        child.sendline('automation\r')
        cmd=r"off .A%d" % int(scdu_port)
        child.sendline(cmd)
        cmd=r"sleep %d" % int(tsec)
        child.sendline(cmd)
        time.sleep(tsec)
        child.close()
        self.insert_pause(tsec_offs)


    def scdu_on(self, scdu_ip, scdu_port, tsec=20):
        import pexpect, time
        tsec_offs=5
        logger=logging.getLogger('Jenkins.scdu_on')
        logger.info("Turning ON %s:.A%d ... Sleeping for %s [sec]" % (scdu_ip, int(scdu_port), tsec))
        child = pexpect.spawn('telnet %s\r' % scdu_ip)
        child.expect('Username: ')
        child.sendline('jenkins\r')
        child.expect('Password: ')
        child.sendline('automation\r')
        cmd=r"on .A%d" % int(scdu_port)
        child.sendline(cmd)
        cmd=r"sleep %d" % int(tsec)
        child.sendline(cmd)
        time.sleep(tsec)
        child.close()
        self.insert_pause(tsec_offs)


    def download_ristretto_package(self, url_file, dst_dir):
        logger=logging.getLogger('Jenkins.download_ristretto_package')
        logger.debug("Downloading file %s into folder %s" % (url_file, dst_dir))
        res=wgetFile(url_file, dst_dir, timeout = 240)
        return res


    def modem_activate(self, tsec=10):
        logger=logging.getLogger('Jenkins.modem_activate')
        com_active = False
        # Deactivate debugger
        if self._enable_flash_via_debugger:
            self.scdu_off(self._scdu_ip, self._icera_ada_scdu_port, tsec)
        # Activate modem
        if self._enable_psu:
            self.psu_activate()
        elif self._enable_scdu and (not self._icera_swd_scdu_port is None):
            self.scdu_off(self._scdu_ip, self._icera_swd_scdu_port, tsec)
            self.scdu_on(self._scdu_ip, self._icera_swd_scdu_port, tsec=30)
        else:
            logger.warning("modem activation commad not sent")

        try:
            self._poll_serial()
            com_active = True
            return com_active
        except:
            return com_active


        logger.debug("Modem activated")


    def modem_nverase(self):
        logger=logging.getLogger('Jenkins.modem_nverase')

        from AT_Modem import AT_Modem
        try:
            com_h = AT_Modem()
            com_h.modem_nverase()
        except:
            logger.error("Cannot access serial port")
            sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)
        com_h.close()


    def start_modem_firmware(self):
        import shutil
        from utilities_file import flashModemViaDebugger


        logger=logging.getLogger('Jenkins.start_modem_firmware')

        # Download RISTRETTO tar.gz package
        # --------------------------------------------------------------------------------------------------------------------
        ristretto_package_url        = os.path.join(self.jenkins_url, self._ristretto_package)
        ristretto_package_local_path = os.path.join(self._local_pckgdir, self._ristretto_package)

        if not os.path.isfile(ristretto_package_local_path):
            # Retrieve it from the URL path
            if self.download_ristretto_package(ristretto_package_url, self._local_pckgdir):
                logger.error("FAILED WGET RISTRETTO PACKAGE %s" % ristretto_package_url)
                sys.exit(CfgError.ERRCODE_TEST_FAILURE)
        else:
            logger.info("Package already downloaded")

        # Prepare folder for flash
        # --------------------------------------------------------------------------------------------------------------------
        src_file = os.path.join(os.environ['PL1JENKINS_ROOT_FOLDER'],'lib','common','tools','flash-autobuild-package.sh')
        shutil.copy(src_file, self._local_toolsdir)

        # Turn off all ports
        # --------------------------------------------------------------------------------------------------------------------
        #self.scdu_off_all(self._scdu_ip, tsec=10)

        # Turn off idera-ada and modem
        # --------------------------------------------------------------------------------------------------------------------
        if self._enable_scdu:
            self.scdu_off(self._scdu_ip, self._icera_ada_scdu_port, tsec=10)

        if self._enable_psu:
            self.psu_off(tsec=10)
        else:
            if self._enable_scdu:
                self.scdu_off(self._scdu_ip, self._icera_swd_scdu_port, tsec=10)

        # Turn on modem
        # --------------------------------------------------------------------------------------------------------------------
        if self._enable_psu:
            self.psu_on(tsec=40)
        elif self._enable_scdu and (not self._icera_swd_scdu_port is None):
                self.scdu_on(self._scdu_ip, self._icera_swd_scdu_port, tsec=40)
        else:
            logger.warning("modem not turnad off")

        # Turn on debugger
        # --------------------------------------------------------------------------------------------------------------------
        if self._enable_scdu:
            self.scdu_on(self._scdu_ip, self._icera_ada_scdu_port, tsec=40)

        # Flash ristretto package and start modem
        # --------------------------------------------------------------------------------------------------------------------
        cmd_path          = os.path.join(self._local_toolsdir, 'flash-autobuild-package.sh')
        cmd_dir           = self._local_toolsdir
        cmd               = "%s %s %s %s" % (cmd_path, ristretto_package_local_path, self._icera_ada_ip, self.LOCAL_TMPDIR)
        proc_filename     = os.path.join(self.LOCAL_TMPDIR, 'proc_out.txt')
        proc_timeout_sec  = 180
        logger.debug("cmd            : %s" %  cmd)
        logger.debug("proc_filename  : %s" %  proc_filename)
        flashModemViaDebugger(cmd, cmd_dir, proc_timeout_sec)

        # Turn off debugger
        # --------------------------------------------------------------------------------------------------------------------
        if self._enable_scdu:
            self.scdu_off(self._scdu_ip, self._icera_ada_scdu_port, tsec=5)

        # Power cycle modem
        # --------------------------------------------------------------------------------------------------------------------
        if self._enable_psu:
            self.psu_off(tsec=5)
            self.psu_on(tsec=25)
        elif self._enable_scdu and (not self._icera_swd_scdu_port is None):
            self.scdu_off(self._scdu_ip, self._icera_swd_scdu_port, tsec=5)
            self.scdu_on(self._scdu_ip, self._icera_swd_scdu_port, tsec=25)
        else:
            logger.warning("modem power cycle commands not issued")



    def check_modem_info(self):
        logger=logging.getLogger("Jenkins.check_modem_info")

        from Serial_ComPortDet import auto_detect_port
        from AT_Modem import AT_Modem

        check_dict = { 0 :'PASS', 1:'FAIL' }

        try:
            com_h = AT_Modem()
            modeminfo=com_h.modem_info()
        except:
            logger.error("Cannot access serial port")
            sys.exit(CfgError.ERRCODE_SYS_SERIAL_CONN)
        else:
            com_h.close()

        branch          = self._get_branch(modeminfo)
        variant         = self._get_variant(modeminfo)
        changelist      = self._get_changelist(modeminfo)

        check_point  = 0
        logger.info("------------------")

        # Branch
        if 0: logger.debug("check branch: %s ?= %s" % (branch, self._branch))
        if branch is None:
            check_flag   = 1
        else:
            #check_flag   = 0 if ( branch in self._branch)     else 1
            if (( branch in self._branch) or ( self._branch in branch)):
                check_flag=0
            else:
                check_flag=1

        check_point += check_flag
        logger.info("branch checkpoint ? \t%s" % check_dict[check_flag])

        # Changelist
        if 0: logger.debug("check changelist: %s ?= %s"% (changelist, self._changelist))
        if changelist is None:
            check_flag   = 1
        else:
            check_flag   = 0 if ( changelist==self._changelist)   else 1
        check_point += check_flag
        logger.info("changelist checkpoint ? \t%s" % check_dict[check_flag])

        # Variant
        if 0: logger.debug("check variant: %s ?= %s" % (variant, self._variant))
        if variant is None:
            check_flag   = 1
        else:
            if (( variant in self._variant) or ( self._platform_tag in variant)):
                check_flag=0
            else:
                check_flag=1
        check_point += check_flag
        logger.info("variant checkpoint ? \t%s" % check_dict[check_flag])

        return check_point


    def run_testbench(self):
        logger=logging.getLogger("Jenkins.run_testbench")

        logger.debug("Starting pl1testbench: ")
        logger.debug("-----------------------")
        logger.debug("  root_dir       : %s" % self.TESTBENCH_DIR_ROOT)
        logger.debug("  main           : %s" % self.TESTBENCH_FILE_EXECUTABLE)
        logger.debug("  result_dir     : %s" % self.TESTBENCH_DIR_RESULT[self.testbench_opt_rat])
        logger.debug("  summary        : %s" % self.TESTBENCH_FILE_SUMMARY)
        logger.debug("-----------------------")
        logger.debug("with options:          ")
        logger.debug("  loglevel       : %s" % self.testbench_opt_log)
        logger.debug("  rat            : %s" % self.testbench_opt_rat)
        logger.debug("  test2execute   : %s" % self.testbench_opt_test2execute)
        logger.debug("-----------------------")


        try:
            import test_env
        except ImportError:
            test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
            sys.path.append(test_env_dir)
            import test_env

        from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath

        if self.testbench_opt_rat.upper() == "WCDMA":
            
            dir_wcdma_unittest = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface','test_WCDMA'])
            
            AddSysPath(dir_wcdma_unittest)
            
            final_f = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:] + ['jenkins_interface', 'linux', 'results', 'final'])

            res = self.execute_wcdma_unittest(jenkins_upload_f=final_f)
            
            if self._enable_psu:
                logger.info("Switching off the power supply")
                try:
                    self.psu_off()
                except Exception:
                    logger.info("POWER SUPPLY SWITCH OFF ERROR")
                    print traceback.format_exc()

        elif self.testbench_opt_rat.upper() == "RF":

            #sys.path.append(self.TESTBENCH_DIR_ROOT[self.testbench_opt_rat])

            # remove logging handlers which could have been configured previously
            for handler in logging.root.handlers[:]:
                logging.root.removeHandler(handler)

            import pl1_testbench_framework.pl1_rf_system.pl1_rf_system_test_env
    
            import pl1_rf_system.runTest as rf
            
            res_str = 'INCONCLUSIVE'
    
            res_str = rf.runTestExternal(testType=self.testbench_opt_jobtype,
                                         branch=self._branch,
                                         variant=self._variant)

            # change string to integer value to that this aligns with config error table
            res = {'PASS':CfgError.ERRCODE_TEST_PASS , 
                   'FAIL':CfgError.ERRCODE_TEST_FAILURE, 
                   'INCONCLUSIVE':CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE}[res_str.upper()]

            if self._enable_psu:
                logger.info("Switching off the power supply")
                try:
                    self.psu_off()
                except Exception:
                    logger.info("POWER SUPPLY SWITCH OFF ERROR")
                    print traceback.format_exc()


        else:
            cmd_run = r"python %s -xml %s" % (self.TESTBENCH_FILE_EXECUTABLE, self.TESTBENCH_FILE_XMLCONFIG)
            if self._enable_psu:
                cmd_run += " -psu %s -psugwip %s -psugpib %s" % (self._enable_psu, self._psu_gwip, self._psu_gpib)
            elif self._enable_scdu:
                cmd_run += " -scdu %s -scdu_ip %s -scdu_port %s" % (self._enable_scdu, self._scdu_ip, self._icera_swd_scdu_port)
            else:
                pass
            logger.info("RUNNING CMD : %s" % cmd_run)

            if self.testbench_opt_jobtype == 'weekly':
                timeout = (14*60*60)
            else:
                timeout = (3*60*60)

            res=runTestbench(cmd_run, timeout = timeout)

        if self._enable_psu:
            try:
                self.psu_off()
            except Exception:
                logger.error("PSU switch off error")
                print traceback.format_exc()
        else:
            if self._enable_scdu:
                self.scdu_off(self._scdu_ip, self._icera_swd_scdu_port, tsec=5)

        return res


    def execute_wcdma_unittest(self, jenkins_upload_f):
        
        import nose

        #from nose.plugins.xunit import Xunit
        #from nose.plugins import Plugin
        
        from pl1_testbench_framework.common.utils.addSystemPath import AddSysPath
        
        from pl1_testbench_framework.jenkins_interface.unittest.unittest_wrapper import Customxunit
        
        path_to_wcdma_unittests = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface','unittest','test_WCDMA'])
        
        AddSysPath(path_to_wcdma_unittests)

        nose_module_arg_l = []
        
        result = CfgError.ERRCODE_TEST_PASS 
    
        if self.testbench_opt_jobtype.upper() == "PER_CL":
    
            nose_module = 'test_wcdma_per_cl'
    
            nose_module_arg_l.append(nose_module)
    
            destfilename = 'wcdma_tests_per_cl.xml'
    
    
        elif self.testbench_opt_jobtype.upper() == "NIGHTLY":
    
            nose_module='test_wcdma_nightly'
    
            nose_module_arg_l.append(nose_module)
    
            destfilename = 'wcdma_tests_nightly.xml'
    
    
        elif self.testbench_opt_jobtype.upper() == "WEEKLY":
    
            nose_module = 'test_wcdma_weekly'
    
            nose_module_arg_l.append(nose_module)
    
            destfilename = 'wcdma_tests_weekly.xml'
    
    
        destfilepath = os.sep.join(jenkins_upload_f.split(os.sep)[:]+[destfilename])
    
        xunit_dst_option = r'--customxunit-file=' + destfilepath
    
        # note that the first arg in argv is ignored by nose
        # arbritrarily given '1'
        args = ['1'] + nose_module_arg_l + ['-v', '-s', '--nologcapture', '--match=^test', '--with-customxunit', xunit_dst_option]
    
        print "nose.run addplugins=[Customxunit()] %s" %args
        
        result_str=nose.run(addplugins=[Customxunit()], argv=args)
        
        
        if result_str == True:
            
            result = CfgError.ERRCODE_TEST_PASS 
        
        else:
            
            result = CfgError.ERRCODE_TEST_FAILURE 

        return result

    def process_verdict(self):
        logger=logging.getLogger("Jenkins.process_verdict")

        VERDICT_PASS         = 'PASS'
        VERDICT_FAILURE      = 'FAILURE'
        VERDICT_INCONCLUSIVE = 'INCONCLUSIVE'

        verdict_file_status  = { VERDICT_PASS         : self.testbench_opt_rat +"_CMW500_STATUS_SUCCESS.txt",
                                 VERDICT_FAILURE      : self.testbench_opt_rat +"_CMW500_STATUS_FAILURE.txt",
                                 VERDICT_INCONCLUSIVE : self.testbench_opt_rat +"_CMW500_STATUS_UNSTABLE.txt"}

        # Process summary file
        # -----------------------------------------------------------------------------
        verdict              = None
        try:
            if not os.path.isfile(self.TESTBENCH_FILE_SUMMARY):
                logger.error("VERDICT FILE NOT FOUND: %s" % self.TESTBENCH_FILE_SUMMARY)
                sys.exit(CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE)

            with open(self.TESTBENCH_FILE_SUMMARY, 'r') as fd:
                # Process header
                # --------------
                line=fd.readline()
                if line == "" :
                    # EOF detected. Marking the test as inconclusive
                    logger.info("VERDICT FILE EMPTY : %s" % self.TESTBENCH_FILE_SUMMARY)
                    sys.exit(CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE)

                # Retrieve verdict column
                line_l=[x.strip() for x in (line.lower()).split(',')]
                if 0: logger.debug("Found verdict header : %s" % line_l)
                if 'verdict' in line_l:
                    verdict_idx=line_l.index('verdict')
                    if 0: logger.debug("verdict : col_idx = %s" % verdict_idx)
                else:
                    logger.error("VERDICT COLUMN NOT FOUND IN FILE : %s" % self.TESTBENCH_FILE_SUMMARY)
                    sys.exit(CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE)

                # Process body
                # --------------
                while True:
                    line=fd.readline()
                    if line == "" : break
                    line_l=[x.strip() for x in (line.upper()).split(',')]
                    if re.match('[p|P][a|A][s|S][s|S]', line_l[verdict_idx], re.I):
                        verdict= VERDICT_PASS
                        continue
                    elif re.match('[f|F][a|A][i|I][l|L]', line_l[verdict_idx], re.I):
                        verdict= VERDICT_FAILURE
                        break
                    else:
                        verdict= VERDICT_INCONCLUSIVE
                        break
                logger.info("VERDICT : %s" % verdict)
                fd.close()

        except IOError:
            logger.error("IO ERROR on verdict file : %s" % self.TESTBENCH_FILE_SUMMARY)
            verdict= VERDICT_INCONCLUSIVE

        except SystemExit:
            verdict= VERDICT_INCONCLUSIVE

        # Create verdict status file
        # -----------------------------------------------------------------------------
        status_file=os.path.join(self.TESTBENCH_DIR_RESULT[self.testbench_opt_rat], verdict_file_status[verdict])
        self._create_verdict_status_file(status_file)

        return verdict


    def process_result(self, verdict, descr):
        logger=logging.getLogger("Jenkins.process_result")

        filename = os.path.join(self.TESTBENCH_DIR_RESULT[self.testbench_opt_rat], self.testbench_opt_rat + "_CMW500_testVerdict.csv")
        fpath    = os.path.split(filename)[0]

        try:
            if not os.path.exists(fpath):
                os.makedirs(fpath)

            with open(filename,'a') as fd:
                fd.write("%s,%s\n" %(verdict, descr))
            fd.close()
            logger.debug("%s,%s" %(verdict, descr))

        except IOError:
            logger.error("ERROR: opening file %s" % filename)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)


    def insert_pause(self, tsec=5):
        logger=logging.getLogger("Jenkins.insert_pause")
        elapsed_time = 0
        sleep_time   = int(tsec/5) if (tsec > 5) else 1
        logger.info("pause %s [sec]" % tsec)
        while (elapsed_time < tsec):
            logger.info("  remaining time : %s" % (tsec-elapsed_time))
            time.sleep(sleep_time)
            elapsed_time += sleep_time


    def remove_dir(self, path):
        logger=logging.getLogger('Jenkins.remove_dir')
        logger.debug("Removing folder %s" % path)
        res=removeDir(path, timeout = 240)
        return res


    def log_jenkins(self):
        logger=logging.getLogger("Jenkins.log_jenkins")
        logger.info("------------------")
        logger.info("jenkins_url       : %s" % self.jenkins_url)
        logger.info("branch            : %s" % self._branch)
        logger.info("changelist        : %s" % self._changelist)
        logger.info("p4webrev          : %s" % self._p4webrev)
        logger.info("ristretto_package : %s" % self._ristretto_package)
        logger.info("------------------")
        logger.info("variant           : %s" % self._variant)
        logger.info("platform_tag      : %s" % self._platform_tag)
        logger.info("ada_ip            : %s" % self._icera_ada_ip)
        logger.info("scdu_ip           : %s" % self._scdu_ip)
        logger.info("scdu_ada_port     : %s" % self._icera_ada_scdu_port)
        logger.info("scdu_swd_port     : %s" % self._icera_swd_scdu_port)
        logger.info("------------------")
        logger.info("p4_pckgdir        : %s" % self._local_pckgdir)
        logger.info("p4_toolsdir       : %s" % self._local_toolsdir)
        logger.info("------------------")


    def __str__(self):
        print "------------------"
        print "jenkins_url       : %s" % self.jenkins_url
        print "branch            : %s" % self._branch
        print "changelist        : %s" % self._changelist
        print "p4webrev          : %s" % self._p4webrev
        print "ristretto_package : %s" % self._ristretto_package
        print "------------------"
        print "variant           : %s" % self._variant
        print "platform_tag      : %s" % self._platform_tag
        print "ada_ip            : %s" % self._icera_ada_ip
        print "scdu_ip           : %s" % self._scdu_ip
        print "scdu_ada_port     : %s" % self._icera_ada_scdu_port
        print "scdu_swd_port     : %s" % self._icera_swd_scdu_port
        print "------------------"
        print "local_pckgdir     : %s" % self._local_pckgdir
        print "local_toolsdir    : %s" % self._local_toolsdir
        print "------------------"
        return ""



# **************************************************************************
# main()
# **************************************************************************

def pl1jenkins_linux(config_s):
    logger=logging.getLogger('pl1jenkins_linux()')

    logger.info("-----------------------------------------------")
    logger.info("Starting test with the following configuration:")
    logger.info("-----------------------------------------------")
    logger.info("      loglevel : %s" % config_s.log)
    logger.info("           url : %s" % config_s.url)
    logger.info("           rat : %s" % config_s.rat)
    logger.info("       jobtype : %s" % config_s.jobtype)
    logger.info("-----------------------------------------------")

    res=0
    try:
        # Instantiate Jenkins class
        test=Jenkins(config_s)
        test.log_jenkins()

        # Activate the modem in case any crash in th eprevious run
        com_active=test.modem_activate()

        # Check if modem firmware is already flashed
        if (com_active and test.check_modem_info()) or (not com_active):
            logger.info("---------------------------------- ")
            logger.info("Updating modem firmware... ")
            logger.info("---------------------------------- ")

            # Flash modem firmware
            test.start_modem_firmware()

            # Check modem info
            if test.check_modem_info():
                logger.error("Modem firmware update failure. Test aborted")
                sys.exit(CfgError.ERRCODE_TEST_FAILURE)
        else:
            logger.info("---------------------------------- ")
            logger.info("No modem firmware update required ")
            logger.info("----------------------------------")

        # Run testbench
        res=test.run_testbench()

    except SystemExit:
        exc_info = sys.exc_info()
        res=int('%s' % exc_info[1])

        # Process summary file and create verdict status file
        print traceback.format_exc()
        test.process_verdict()

        # Create a short description: {verdict, description}
        test.process_result(res, CfgError.MSG[res])

    else:
        # Process summary file and create verdict status file
        test.process_verdict()

        # Create a short description: {verdict, description}
        test.process_result(res, CfgError.MSG[res])

    return res



if __name__ == '__main__':

    import argparse

    # Configure ROOT logger
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    logger=cfg_multilogging('DEBUG', os.path.splitext(cmdname)[0]+'.LOG')
    logger=logging.getLogger('pl1jenkins_linux')


    PL1JENKINS_VER="1.0.0"

    # DEFINE COMMAND LINE OPTIONS AND PARSING FUNCTION
    # =============================================================================
    parser = argparse.ArgumentParser(prog=cmdname,
                                     formatter_class=argparse.RawDescriptionHelpFormatter, prefix_chars='-',
                                     usage='%(prog)s <cmd> <arg_s [<cmd> <args>]',
                                     description="""Description:\n  Jenkins Linux framework for PL1 testbench""",
                                     epilog="""Example:\n python pl1jenkins_linux.py -log=INFO -u=http://bs.nvidia.com/systems/datacard-builds/software/main.br/CL673206-i500-121-1725-ti-att--1e4a95ea -r=LTE_FDD -t=per_cl""")

    # Option for printing the script version
    # ---------------------------------------------------------------------------------------------------------------------------------------
    parser.add_argument('-v', '-version', action='version', version=('pl1jenkins_linux v'+PL1JENKINS_VER))
    parser.add_argument('-log', dest='log',      required=False, type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='DEBUG', help="Define logging level. Default='DEBUG'" )
    parser.add_argument('-u',   dest='url',      required=True,  type=str, help="Jenkins build URL" )
    parser.add_argument('-r',   dest='rat',      required=True,  type=str, choices=['LTE_FDD', 'LTE_TDD', 'WCDMA', 'RF'], help="RAT selector")
    parser.add_argument('-t',   dest='jobtype',  required=True,  type=str, choices=['per_cl', 'weekly', 'nightly'], help="Test plan selector")

    args=parser.parse_args()

    # Get Jenkins parameters
    # --------------------------------------------------------------------------------------------------------------------
    param_s=Struct()
    param_s.log          = args.log.upper()
    param_s.url          = args.url
    param_s.rat          = args.rat
    param_s.jobtype      = args.jobtype

    res = pl1jenkins_linux(param_s)

    logger.info("EXIT STATUS : (%s, %s)" % (res, CfgError.MSG[res]))
    exit(res)



