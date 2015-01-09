#-------------------------------------------------------------------------------
# Name:        testConfigParser
# Purpose:     xml parser for geeting the configuration from XML file
#
# Author:      joashr
#
# Created:     18/11/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, logging

from xml.etree.ElementTree import parse

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


from pl1_testbench_framework.common.config.CfgError import CfgError

import pl1_testbench_framework.jenkins_interface.common.errors.flash_error_codes as flash_err_code

class TestConfigParser(object):

    def __init__(self, xmlfile, variant):

        func_name = sys._getframe(0).f_code.co_name
        logger = logging.getLogger(__name__ + func_name)

        self.xmlfile = xmlfile

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
        self._variant         = "nvidia-p2341-win7_internal"

        if not os.path.isfile(xmlfile):
            logger.error("Could not find XML configuration file : %s" % xmlfile)
            #sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            sys.exit(flash_err_code.ERRCODE_TEST_CONFIG_XML_NOT_FOUND)

        tree              = parse(xmlfile)
        section           = tree.find(self._variant)

        if section is not None:
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
                    #sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                    sys.exit(flash_err_code.ERRCODE_INVALID_TEST_CONFIG_PARAM)

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
                    #sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                    sys.exit(flash_err_code.ERRCODE_INVALID_TEST_CONFIG_PARAM)
            else:
                try:
                    self._icera_swd_scdu_port = int(section.find('icera_swd_scdu_port').text) if self._enable_scdu else None
                except ValueError:
                    logger.error("invalid configuration for the icera-swd scdu port")
                    #sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
                    sys.exit(flash_err_code.ERRCODE_INVALID_TEST_CONFIG_PARAM)

        else:
            logger.error("unable to locate variant: %s" % self._variant)
            #sys.exit(CfgError.ERRCODE_TEST_PARAM_INVALID)
            sys.exit(flash_err_code.ERRCODE_INVALID_TEST_CONFIG_PARAM)

    def get_psu_gwip(self):
        return self._psu_gwip

    def get_psu_gpib(self):
        return self._psu_gpib

if __name__ == '__main__':

    # Configure logging
    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)

    xmlfile = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['jenkins_interface', 'test_config.xml'])

    variant="p2341-win7_internal"

    testConfigObj = TestConfigParser(xmlfile=xmlfile, variant=variant)

    psu_gwip = testConfigObj.get_psu_gwip()

    psu_gpib = testConfigObj.get_psu_gpib()

    print psu_gwip

    print psu_gpib
