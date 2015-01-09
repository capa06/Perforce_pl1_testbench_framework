#-------------------------------------------------------------------------------
# Name:        RunCmd
# Purpose:     Run system cmd as a subprocess
#
# Author:      joashr
#
# Created:     13/03/2014
# Copyright:   (c) joashr 2014
# Licence:
#-------------------------------------------------------------------------------

import os, sys, threading, subprocess


class RunCmd(threading.Thread):

    SUCCESS=0
    FAIL=1

    def __init__(self, cmd, cwd=None, shell=True, timeout=120):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout
        self.cwd = cwd
        self.shell=shell

    def run(self):

        # the run method is executed by the Thread framework
        # in a new thread when we make RunCmd class instance

        self.StDout = ""

        self.StDerr = ""

        self.exit_code= ""

        if self.cwd is None:

            self.sub_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)

        else:

            self.sub_process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell, cwd=self.cwd)

        self.StDout, self.StDerr = self.sub_process.communicate()

        self.exit_code = self.sub_process.wait()

        if self.StDout != "":

            print "cmd output =>"

            print  self.StDout

            #print "EXIT CODE : %s\n" %self.exit_code

        if self.StDerr != "":

            print "err output =>"

            print  self.StDerr

            #print "EXIT CODE : %s\n" %self.exit_code


    def Run(self):

        runStatus = self.SUCCESS

        self.start()

        self.join(self.timeout)

        if self.is_alive():

            print "=> Timeout exceeded"

            self.sub_process.terminate()      #use self.p.kill() if process needs a kill -9

            self.join(timeout=5)

            runStatus = self.FAIL


        return runStatus,self.StDout, self.StDerr
