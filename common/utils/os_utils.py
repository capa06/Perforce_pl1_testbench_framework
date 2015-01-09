import os
import sys
#import re
import logging
import time
import errno
import shutil


from subprocess_helper import SubProcess

def pyCopyDir(src, dst):
    logger=logging.getLogger("pyCopyDir")
    try:
        shutil.copytree(src, dst)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            logger.error('directory copy failed: %s' % e)

def insertPause(tsec=5, desc=""):
    logger=logging.getLogger("insertPause")
    remaining_time = tsec
    sleep_time   = int(tsec/5) if (tsec > 5) else 1
    logger.info("pause %s [sec] " % (tsec) + desc)
    while (remaining_time > 0):
        logger.info("  remaining time : %s [sec]" % (remaining_time))
        time.sleep(sleep_time)
        remaining_time -= sleep_time

def removeDir(dirname):
    if sys.platform in ['cygwin', 'win32']:
        cmd=r"rmdir /s /q %s" % dirname
        print cmd
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd=r"rm -rf %s" % dirname
    else:
        logging.error("OS not supported : %s" % sys.platform)
    res=os.system(cmd)
    return res

def remove_dir(dir_path):
    logger=logging.getLogger("remove_dir")
    if os.path.exists(dir_path):
        try:
            shutil.rmtree(dir_path)
        except WindowsError:
            logging.error ("cannnot remove directory %s, check that the file is not being used by another process" %dir_path)
            logging.error("continuing anyway")

def copyDir(srcdir, dstdir):
    if sys.platform in ['cygwin', 'win32']:
        cmd=r"xcopy /e /q /i %s %s" % (srcdir, dstdir)
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd=r"cp -rf %s %s" % (srcdir, dstdir)
    else:
        logging.error("OS not supported : %s" % sys.platform)
    res=os.system(cmd)
    return res

def renameDir(srcdir, dstdir):
    if sys.platform in ['cygwin', 'win32']:
        cmd=r"rename %s %s" % (srcdir, dstdir)
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd=r"mv %s %s" % (srcdir, dstdir)
    else:
        logging.error("OS not supported : %s" % sys.platform)
    res=os.system(cmd)
    return res

def run_script(cmd):
    from subprocess import Popen, PIPE
    print "%s" %cmd
    pipe = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr =  pipe.communicate()
    print stdout
    if stderr:
        print stderr
    return pipe.returncode


def untarFile(filePath, destPath, timeout = 240):
    logger=logging.getLogger('untarFile')
    logger.debug("Untar file %s into %s" % (filePath, destPath))
    res = None
    (folder, filename) = os.path.split(filePath)
    proc = SubProcess("tar -zxvf %s -C %s" % (filename, destPath), cwd = folder, fileHandler = False)
    (output, hasTimeout) = proc.waitForProcessAndRetrieveOutput(timeout)
    if hasTimeout:
        logger.error("Untar did not complete before timeout")
    elif proc.returnCode == 0:
        logger.debug("Untar successful")
    else:
        logger.error("Something went wrong (return code: %s)" % proc.returnCode)
    res = proc.returnCode
    return res


def wgetFile(filePath, destPath, timeout = 240):
    logger=logging.getLogger('wgetFile')
    logger.debug("wget file %s into %s" % (filePath, destPath))
    res = None

    cmd="wget %s -P %s" % (filePath, destPath)
    proc = SubProcess(cmd, fileHandler = False)
    (output, hasTimeout) = proc.waitForProcessAndRetrieveOutput(timeout)

    if hasTimeout:
        logger.error("wget did not complete before timeout")
    elif proc.returnCode == 0:
        logger.debug("wget successful")
    else:
        logger.error("Something went wrong (return code: %s)" % proc.returnCode)
    res = proc.returnCode
    return res

def cleanRun():
    import subprocess
    # Remove any process left from the previous run
    if sys.platform in ['cygwin', 'win32']:
        cmd_l= ['taskkill /f /t /im icera_log_serial.exe', 'taskkill /f /t /im adb.exe']
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd_l= ['killall -v icera_log_serial', 'killall -v adb']
    else:
        logging.warning("cleanRun(): OS not supported. No process killed")
        return
    devnull = open(os.devnull, 'wb')
    for cmd in cmd_l:
        proc    = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=devnull)
        cmd_out = proc.stdout.readlines()
        #print cmd_out
    devnull.close()
    time.sleep(2)

