'''
Created on 10 Sep 2014

@author: FRA
'''

# ********************************************************************
# IMPORT PYTHON LIBRARIES
# ********************************************************************
import os
import sys
import logging
import time
import re
import subprocess
import threading
try:
    import fcntl
except:
    pass


# ********************************************************************
# DEFINE MODULE ROOT FOLDER
# ********************************************************************

'''
try:
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[0:-3])
'''

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env



# ********************************************************************
# DEFINE PATH(s) TO EXTERNAL LIBRARIES
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))



# ********************************************************************
# DEFINE PATH(s) TO LOCAL LIBRARIES
# ********************************************************************


# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************


# ********************************************************************
# GLOBALS
# ********************************************************************
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'globals']))
import test_globals as tg

# ***************************************************************************
#                          API PUBLIC FUNCTIONS
# ***************************************************************************

def runCmdBlockingMode(cmd_l):
    logger=logging.getLogger('runCmdBlockingMode')
    import subprocess

    cmd_out    = None

    try:
        pipe = subprocess.Popen(cmd_l, bufsize= 0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        logger.error(str(e))
        return False

    while 1:
        line = pipe.stdout.readline()
        if len(line)>0:
            line = re.sub(r'[\n|\r]', r'', line)
            logger.info(line)
            if cmd_out is None:
                cmd_out = line
            else:
                cmd_out += (line + os.linesep)
        if pipe.returncode is None:
            pipe.poll()
        else:
            break

    return pipe.returncode, cmd_out




def runCmdBlockingModeTimeout(cmd_l, timeout_sec):
    # Return :   None   TIMEOUT
    # Return :   0      OK
    # Return :   <any>  ERROR


    logger=logging.getLogger('runCmdBlockingModeTimeout')

    import subprocess
    cmd_out    = None

    try:
        pipe = subprocess.Popen(cmd_l, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        logger.error(str(e))
        return False

    t0=time.localtime()                                             # Probe start time

    while 1:
        line = pipe.stdout.readline()
        if len(line)>0:
            line = re.sub(r'[\n|\r]', r'', line)
            logger.info(line)
            if cmd_out is None:
                cmd_out = line
            else:
                cmd_out += (line + os.linesep)
        if pipe.returncode is None:
            t1=time.localtime()                                          # Probe current time
            dt_sec=time.mktime(t1)-time.mktime(t0)                       # Compute elapsed time [sec]
            if dt_sec > timeout_sec:
                break
            pipe.poll()
        else:
            break

    if pipe.returncode is None:
        logger.error("command execution timeout( = %s[sec]): %s" % (timeout_sec, (' '.join(cmd_l))))
    elif not pipe.returncode==0:
        logger.error("command execution error (return status = %s): %s" % (pipe.returncode, (' '.join(cmd_l))))
    else:
        logger.debug("command execution success (return status = %s): %s" % (pipe.returncode, (' '.join(cmd_l))))

    return pipe.returncode, cmd_out


class RetrieveSubProcessOutput(threading.Thread):
    def __init__(self, process, cwd, cmd, fileHandler = None, filename = None):
        threading.Thread.__init__(self)
        self.ThreadTag = "%s" % re.sub("Thread-", "", self.getName())

        logger=logging.getLogger('RetrieveSubProcessOutput.__init__')
        if 0: logger.debug("%s: CWD = %s" % (self.ThreadTag, cwd))
        if 0: logger.debug("%s: CMD = %s" % (self.ThreadTag, cmd))
        self.process = process
        self.txt = ""
        self.txtSinceLastTime = ""
        self.fileHandler = fileHandler
        self.filename = filename
        self.outputLock = threading.RLock()


    def run(self):
        logger=logging.getLogger('RetrieveSubProcessOutput.run')
        if tg.DEBUG_TRACE: logger.debug(">>")

        self.outputLock.acquire()
        if not self.fileHandler:
            # Create a bridge between the process.stdout and the thread
            try:
                while self.process.poll() is None:
                    try:
                        output = self.process.stdout.read()
                        self.txtSinceLastTime += output
                        self.txt += output
                        # Remove any redundant newline
                        logger.info(re.sub('[\r\n]+$','', output))
                    except IOError, e:
                        pass
                        #logger.debug("IOError, Repeating")
                    #output = os.read(self.process.stdout.fileno(),2048)
                    time.sleep(0.05)
                try:
                    # in case process is over before retrieving output, make one shot read
                    output = self.process.stdout.read()
                    self.txtSinceLastTime += output
                    self.txt += output
                    # Remove any redundant newline
                    logger.info(re.sub('[\r\n]+$','', output))
                except IOError, e:
                    pass
                except ValueError, e:
                    # Here is stdout is already closed
                    pass
            except OSError, e:
                pass

        if tg.DEBUG_TRACE: logger.debug("<<")
        self.outputLock.release()


    def retrieveOutput(self):
        logger=logging.getLogger('RetrieveSubProcessOutput.retrieveOutput')
        if tg.DEBUG_TRACE: logger.debug(">>")

        self.outputLock.acquire()
        if self.fileHandler:
            self.fileHandler.close()
            # Doing in this way, no matter how big is the file
            with open(self.filename, 'r') as newFileHandler:
                while True:
                    line=newFileHandler.readline()
                    if line == "" : break
                    logger.info(re.sub('[\r\n]+$','', line))
            newFileHandler.close()
            try:
                os.remove(self.filename)
            except:
                pass

        self.outputLock.release()
        if tg.DEBUG_TRACE: logger.debug("<<")
        return self.txt


    def retrieveOutputSinceLastTime(self):
        logger=logging.getLogger('RetrieveSubProcessOutput.retrieveOutputSinceLastTime')
        if tg.DEBUG_TRACE: logger.debug(">>")
        output = self.txtSinceLastTime
        self.txtSinceLastTime = ""
        if tg.DEBUG_TRACE: logger.debug("<<")
        return output



class SubProcess:
    def __init__(self, cmd, shell = True, cwd = os.path.abspath(""), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, fileHandler = False, filename=None):

        logger=logging.getLogger('SubProcess.__init__')

        if tg.DEBUG_TRACE:
            logger.debug(">>")
            logger.debug("RUN CMD = %s" % cmd)
            logger.debug("CWD = %s" % cwd)

        if fileHandler:
            if filename is None:
                filename = os.path.join(os.environ["TEMP"], "%s-subproc_stdout.txt" % str(time.time()))
            fh = open(filename, "w")
            self.process = subprocess.Popen(cmd, shell=True, cwd=cwd, stdin=stdin, stdout=fh, stderr=stderr) #, close_fds=True)
        else:
            success = False
            retrial = 0
            while (not success) and retrial < 2:
                if retrial != 0:
                    logger.debug("############## Subprocess retrial #%d" % retrial)
                retrial += 1
                self.process = subprocess.Popen(cmd, shell=True, cwd=cwd, stdin=stdin, stdout=stdout, stderr=stderr) #, close_fds=True)
                if stdout != subprocess.PIPE:
                    break
                if self.process.stdout != None:
                    if sys.platform != "win32":
                        fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
                    success = True

        if stdout != sys.stdout:
            if fileHandler:
                self.outputRetriever = RetrieveSubProcessOutput(self.process, cwd, cmd, fh, filename)
            else:
                self.outputRetriever = RetrieveSubProcessOutput(self.process, cwd, cmd)
            self.outputRetriever.start()

        if tg.DEBUG_TRACE: logger.debug("<<")


    def writeIntoProcess(self, line):
        logger=logging.getLogger('SubProcess.writeIntoProcess')
        if tg.DEBUG_TRACE: logger.debug(">>")
        logger.info(line)
        self.process.communicate(line)
        if tg.DEBUG_TRACE: logger.debug("<<")



    def retrieveProcessOutput(self):
        logger=logging.getLogger('SubProcess.retrieveProcessOutput')
        if tg.DEBUG_TRACE: logger.debug(">>")
        output=""
        if (self.process.poll() is None):
            output = self.outputRetriever.retrieveOutputSinceLastTime()
            if tg.DEBUG_TRACE: logger.debug("<<")
            return output


    def expect(self, pattern, timeout = 10):
        logger=logging.getLogger('SubProcess.expect')
        if tg.DEBUG_TRACE: logger.debug(">>")
        self.patternMatch = None
        startTime = time.time()
        output = ""
        logger.debug("Waiting for pattern : %s" % pattern)
        while (time.time() - startTime) < timeout:
            output += self.retrieveProcessOutput()
            # Remove special characters
            #output = re.sub('[\n\r]+', ' ', output)
            logger.info("#%s#\n" % output)

            if type(pattern) == str:
                #logger.debug("PATTERN STRING: %s" % pattern)
                if re.search(pattern, output) is None:
                    time.sleep(3)
                else:
                    logger.debug("Found pattern : %s" % pattern)
                    return True
            elif type(pattern) == list:
                #logger.info("PATTERN LIST: %s" % pattern)
                for i in range(len(pattern)):
                    logger.debug(">> PATTERN STRING[%s]: %s" % (i, pattern))
                    if re.search(pattern[i], output):
                        logger.info("There is a match with list item %d" % i)
                        self.patternMatch = i
                        return True
                    time.sleep(1)
        logger.debug("Pattern did not show up before timeout")
        return False



    def clearProcessOutput(self):
        logger=logging.getLogger('SubProcess.clearProcessOutput')
        if tg.DEBUG_TRACE: logger.debug(">>")
        if (self.process.poll() is None):
            self.outputRetriever.retrieveOutputSinceLastTime()
        if tg.DEBUG_TRACE: logger.debug("<<")


    def isAlive(self):
        return (self.process.poll() is None)


    def kill(self):
        logger=logging.getLogger('SubProcess.kill')
        if tg.DEBUG_TRACE: logger.debug(">>")
        try:
            self.process.kill()
        except:
            pass
        if tg.DEBUG_TRACE: logger.debug("<<")


    def waitForProcessAndRetrieveOutput(self, timeout=15, display = False):
        logger=logging.getLogger('SubProcess.waitForProcessAndRetrieveOutput')
        if tg.DEBUG_TRACE: logger.debug(">>")

        self.hasTimeout = False
        startTime = time.time()
        while (self.process.poll() is None) and ((time.time() - startTime) < timeout):
            time.sleep(0.05)
        if time.time() - startTime >= timeout:
            if display:
                logger.error( "Process is unresponsive (timeout = %s s)..." % timeout)
            #self.outputRetriever.stop()
            self.kill()
            self.hasTimeout = True
        output = self.outputRetriever.retrieveOutput()

        if self.hasTimeout:
            logger.debug(">>> cmd timeout")

        if tg.DEBUG_TRACE: logger.debug("<<")
        return (output, self.hasTimeout)


    @property
    def returnCode(self):
        if self.hasTimeout:
            return 1
        else:
            return self.process.returncode

    def waitForProcess(self, timeout=15, display = False):
        logger=logging.getLogger('SubProcess.waitForProcess')
        if tg.DEBUG_TRACE: logger.debug(">>")

        self.hasTimeout = False
        startTime = time.time()
        while (self.process.poll() is None) and ((time.time() - startTime) < timeout):
            pass
        if time.time() - startTime >= timeout:
            if display:
                logger.error( "Process is unresponsive (timeout = %s s)..." % timeout)
            self.kill()
            self.hasTimeout = True
        if tg.DEBUG_TRACE: logger.debug("<<")
        return self.hasTimeout


if __name__ == '__main__':
    pass

