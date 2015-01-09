#-------------------------------------------------------------------------------
# Name:        xml_utils
# Purpose:      xml parser
#
# Author:      joashr
#
# Created:     18/11/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os

from xml.etree.ElementTree import parse

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env


def get_params_from_xml(xml_file="", jenkins_linux=0):

    class Struct():
        pass

    param = Struct()

    print "Local test config xml file for WCDMA parameters : %s" %xml_file
    tree = parse(xml_file)

    wcdma = tree.find('wcdma')

    param.log          = wcdma.find('log').text
    param.cmwip        = wcdma.find('cmwip').text
    param.ctrlif       = wcdma.find('ctrlif').text
    param.test2execute = wcdma.find('test2execute').text
    param.pwrmeas      = int(wcdma.find('pwrmeas').text)
    param.usimemu      = int(wcdma.find('usimemu').text)

    param.psugpib      = wcdma.find('psugpib').text
    param.msglog       = int(wcdma.find('msglog').text)
    param.database     = wcdma.find('database').text

    param.cmwip        = wcdma.find('cmwip').text
    param.psugwip      = wcdma.find('psugwip').text

    try:
        param.remoteDB = int(wcdma.find('remoteDB').text)
    except:
        param.remoteDB = 0
    param.remoteDBname = wcdma.find('remoteDBname').text
    param.remoteDBhost = wcdma.find('remoteDBhost').text
    param.remoteDBuid  = wcdma.find('remoteDBuid').text
    try:
        param.remoteDBpwd  = '%s' %unicode(wcdma.find('remoteDBpwd').text, ('unicode-escape')).encode('latin-1')
    except:
        param.remoteDBpwd = None

    return param

def get_cmwip(xml_file):

    param = get_params_from_xml(xml_file=xml_file)

    return param.cmwip

def get_psugwip(xml_file):

    param = get_params_from_xml(xml_file=xml_file)

    return param.psugwip

if __name__ == '__main__':

    test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma', 'wcdma_test_config.xml'])

    cmwip = get_cmwip(xml_file=test_config_xml_path)

    psugwip = get_psugwip(xml_file=test_config_xml_path)

    print cmwip

    print psugwip
