#-------------------------------------------------------------------------------
# Name:        reg_expr
# Purpose:     common regular regular expressions for parsing text
#
# Author:      joashr
#
# Created:     21/11/2014
# Copyright:   (c) joashr 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import os, sys, re
from urllib import urlopen

try:
    import test_env
except ImportError:
    (abs_path, name)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(abs_path.split(os.sep)[:-3])
    sys.path.append(test_env_dir)
    import test_env

import pl1_testbench_framework.jenkins_interface.common.globals.jenkins_globals as jenkins_globals


def get_latest_url_from_autobuild(branch, variant, description=""):

    """
    get latest autobuild url from the specified branch, variant, description
    refer to example below
    """

    txt = urlopen(jenkins_globals.INFO_URL).read()

    lines = re.split("\n", txt)


    if (description==""):

        pattern = 'Cust:(.+);Variant:%s;Label:(.+);Type:(.+);Date:[0-9]{8};Branch:%s\.\.\.@([0-9]+);Desc:(|.+);TBPath:(.+)' % (variant, branch)

        cl_index = 3

        url_index = 5

    else:

        pattern = 'Cust:(.+);Variant:%s;Label:(.+);Type:(.+);Date:[0-9]{8};Branch:%s\.\.\.\@([0-9]+);Desc:%s;TBPath:(.+)' % (variant, branch, description)

        cl_index = 3

        url_index = 4



    p4cl_list = []

    for line in lines:

        if re.search(pattern,line):

            p4cl_list.append((int(re.search(pattern,line).groups()[cl_index]),re.search(pattern,line).groups()[url_index]))



    if len(p4cl_list) > 0:

        original_p4cl_list = list(p4cl_list)

        original_p4cl_list.reverse()

        p4cl_list.sort(key=lambda tup: tup[0], reverse=True)



        latest_p4cl = p4cl_list[0][0]

        for i in range(len(original_p4cl_list)):

            if original_p4cl_list[i][0] == latest_p4cl:

                print '\n##### Branch: %s ############'%(branch)

                print '##### Variant: %s ############'%(variant)

                return original_p4cl_list[i][1]

    else:

        # no build corresponds to this request"

        return None


# http://bs.nvidia.com/systems/datacard-builds/software/teams/phy/pl1_dev.br/CL810405-609ee443/i500-121-1725-ti-att-mbim


def get_ristretto_package(url):

    """
    for the url in the following form
    http://bs.nvidia.com/systems/datacard-builds/software/teams/phy/pl1_dev.br/CL810405-609ee443/i500-121-1725-ti-att-mbim
    return the package name e.g. ristretto_package_i500-121-1725-ti-att-mbim_CL810405.tar.gz
    """

    txt = urlopen(url).read()

    pattern1 = '<A HREF="(ristretto_package_.+\.tar\.gz)">'

    pattern2 = '<a href="(ristretto_package_.+\.tar\.gz)">'

    if re.search(pattern1,txt):

        ristretto_package = re.search(pattern1, txt).groups()[0]

        return ristretto_package

    elif re.search(pattern2,txt):

        ristretto_package = re.search(pattern2, txt).groups()[0]

        return ristretto_package

    else:

        return None

def extract_target_cl(url_link):

    target_cl_str = ""

    m_obj = re.search(r'(CL\d+)', url_link, re.I)

    if m_obj:

        target_cl_str = m_obj.group(1)

        print "target build CL is %s" %target_cl_str

    else:

        print "not able to get the build CL"

    return (target_cl_str)


def get_branch_from_url(url):

    branch_str = ""
    m_obj = re.search(r'/(\w+.br)/', url, re.I)
    if m_obj:
        branch_str = m_obj.group(1)
    else:
        print "not able to get the branch"

    return branch_str

def get_variant_from_url(url=""):

    p = re.compile('.*/([\w-]+)$')
    m = p.match(url)

    if m:
        return m.group(1)
    else:
        return None


def get_p4webrevStringfrom_modem(modemInfo):
    """
    obtain p4webrev list from get_modem_info()
    """
    p4WebRevStr = ""

    m_obj = re.search(r'P4webrev\s+:\s*(\S+)', modemInfo, re.I)

    if m_obj:
        p4WebRevStr = m_obj.group(1)
        print "p4webrev is %s" %p4WebRevStr
        return p4WebRevStr

    else:
        print "not able to get p4webrev"
        return p4WebRevStr

def get_build_cl_from_modem(modemInfo):
    """
    obtain build CL from get_modem_info()
    """

    build_cl_str = ""

    m_obj = re.search(r'Changelist\s+:\s+(CL\d+)', modemInfo, re.I)
    if m_obj:
        build_cl_str = m_obj.group(1)
        print "build CL is %s" %build_cl_str
        return build_cl_str
    else:
        print "not able to get the build CL from"
        return build_cl_str

if __name__ == '__main__':
    import logging
    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging
    cfg_multilogging(log_level = "debug")

    variant = {1:'i500-121-1725-ti-att-mbim', 2:'nvidia-p2341-win7_internal'}[1]
    branch = {1:r"//software/main.br/",
              2:r"//software/teams/phy/pl1_dev.br/",
              3:r"//software/releases/core/cr4.br/"}[2]

    test_url=r"http://bs.nvidia.com/systems/datacard-builds/software/teams/phy/pl1_dev.br/CL810405-609ee443/i500-121-1725-ti-att-mbim"

    if 0:
        # test get_latest_url_from_autobuild function

        build_url = get_latest_url_from_autobuild(branch=branch, variant=variant)
        http_build_url = 'http:'+ build_url
        print http_build_url

    if 0:
        build_url = get_latest_url_from_autobuild(branch=branch, variant=variant)
        http_build_url = 'http:'+ build_url
        print http_build_url
        ristretto_package = get_ristretto_package(url=http_build_url)
        print ristretto_package
    if 0:
        extract_target_cl(url_link=test_url)

    if 0:
        branch=get_branch_from_url(url=test_url)
        print branch

    if 0:
        variant=get_variant_from_url(url=test_url)
        print variant

    if 1:
        import pl1_testbench_framework.common.com.modem as modem
        modemInfo = modem.get_modem_info()
        p4webrev = get_p4webrevStringfrom_modem(modemInfo)
        logging.info(p4webrev)
        modem_build_cl = get_build_cl_from_modem(modemInfo=modemInfo)
        logging.info(modem_build_cl)

