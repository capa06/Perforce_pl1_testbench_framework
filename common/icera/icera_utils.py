'''
Created on 14 Jul 2014

@author: fsaracino
'''


# ********************************************************************
# IMPORT SYSTEM MODULES
# ********************************************************************
import os
import sys
import logging
import re


# ********************************************************************
# IMPORT USER DEFINED PATHS
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath('').split(os.sep)[0:-2])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
# ********************************************************************
# IMPORT USER DEFINED LIBRARY 
# ********************************************************************
#from CfgError import CfgError


# ********************************************************************
# GLOBAL VARIABLES
# ********************************************************************
# Icera decoders
icera_aes = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-aes'])
icera_b64 = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-b64'])


def parseModemInfo(msg_enc):    
    """
        Decode modem info
    """
    import subprocess
    logger=logging.getLogger('parseModemInfo')
    if sys.platform in ['cygwin', 'win32']:
        cmd='echo/|set /p=%s| %s -d | %s -d -p 9TfyKtMO+hoPyscfR15GEw8PYlzNPvMksp5wwSvxbMI=' % (msg_enc, icera_b64, icera_aes)
    elif  sys.platform in ['linux', 'linux2', 'linux3']:
        cmd='echo -n %s | %s -d | %s -d -p 9TfyKtMO+hoPyscfR15GEw8PYlzNPvMksp5wwSvxbMI=' % (msg_enc, icera_b64, icera_aes)
    else:
        print "Unkown platform, nothing to do"
        return None
    res=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
    if res=="" : res="NA"
    logger.debug("res : %s" % res)
    return res 


def getBranch(msg):
    logger=logging.getLogger('getBranch')

    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    branch_re=re.compile(r".*Branch name\s*:\s*(\S*).*$")
    branch='NA'
    if branch_re.search(msg_str):
        res=branch_re.findall(msg_str)
        if (res[0][0:3] == "css"):
            # Encoded string
            branch=parseModemInfo(res[0])
        else:
            # string not encoded
            branch=res[0]    
    logger.debug("res : %s" % branch)
    return branch


def getPlatform(msg):
    logger=logging.getLogger('getPlatorm')
    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    platform_re=re.compile(r".*Platform\s*:\s*(.*?)\s")
    platform='NA'
    if platform_re.search(msg_str):
        print platform_re.findall(msg)
        platform=platform_re.findall(msg)[0]
    logger.debug("res : %s" % platform)
    return platform


def getVariant(msg):
    logger=logging.getLogger('getVariant')
    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    variant_re=re.compile(r".*Variant\s*:\s*(\S*).*$")
    variant='None'
    if variant_re.search(msg_str):
        res=variant_re.findall(msg)
        if (res[0][0:3] == "css"):
            # Encoded string
            variant=parseModemInfo(res[0])
        else:
            # string not encoded
            variant=res[0]    
    logger.debug("res : %s" % variant)
    return variant
    
if __name__ == '__main__':
    pass