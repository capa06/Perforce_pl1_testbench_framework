__author__ = 'chuyiq'

#! /usr/bin/env python



#######################################################################################################################

#

# Anritsu MT8820C instrument driver class

#

#######################################################################################################################





# ********************************************************************

# IMPORT SYSTEM COMPONENTS

# ********************************************************************

import os
import sys
import logging
import time
import re
import visa

# ********************************************************************

# DEFINE USER'S PATHS

# ********************************************************************
try:

    os.environ['PL1TESTBENCH_ROOT_FOLDER']

except KeyError:

    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])

    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']

else:

    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))

# ********************************************************************

# IMPORT USER DEFINED COMPONENTS

# ********************************************************************


from CfgError import CfgError











# ****************************************************************************************************

# GLOBAL VARIABLES

# ****************************************************************************************************







# ****************************************************************************************************

# GLOBAL FUNCTIONS

# ****************************************************************************************************


class Anritsu(object):

    def __init__(self, name, ip_addr):

        self.name = name

        self.ip_addr = ip_addr

        logging.debug ('init-routine')
        ip_socket='TCPIP0::'+ip_addr+'::56001::SOCKET'
        rm = visa.ResourceManager()
        self.dev=rm.open_resource(ip_socket,read_termination='\n')
        self.dev.write("*CLS")

        self.resultsFile = ""



    # ***************************

    # Private methods

    # ***************************

    def _param_write(self, cmd, param, param_tag):

        cmd_wr = cmd + (" %s" % param)

        self.write(cmd_wr)

        check = self._param_write_check(cmd, param, param_tag)

        return check



    def _param_write_check(self, cmd, param, param_tag):

        logger = logging.getLogger('%s._param_config_check' % self.name)
        if cmd.find('?')!=-1:
            cmd_rd=cmd
        else:
            cmd_rd = cmd + "?"

        readback = self.read(cmd_rd)

        if ((type(param) is int) or (type(param) is float)):

            res = 0 if (float(param)==float(readback)) else 1

        else:

            res = 0 if (param in str(readback)) else 1

        logger.debug("CHECKPOINT %-15s : %s (%s, readback=%s)" % (param_tag, ('FAIL' if res else 'PASS'), param, readback))
        import msvcrt as m
        '''
        if res==1:
            print cmd,param,readback, m.getch()
        '''

        self.param_check += res

        return res



    def _param_write_nocheck(self, cmd, param):

        cmd_wr = cmd + (" %s" % param)

        self.write(cmd_wr)



    def _param_read(self, cmd):

        cmd_rd = cmd + "?"

        readback    = self.read(cmd_rd)

        return readback



    def _param_read_check(self, cmd, param):

        logger = logging.getLogger('%s._param_read_check' % self.name)

        cmd_rd = cmd + "?"

        readback    = self.read(cmd_rd)

        if ((type(param) is int) or (type(param) is float)):

            res         = 0 if (float(param)==float(readback)) else 1

        else:

            res         = 0 if (param in str(readback)) else 1

        logger.debug("CHECK READ : %-15s : %s (%s, readback=%s)" % (cmd, ('FAIL' if res else 'PASS'), param, readback))

        return res



    #======================================================================

    # Instrument access functionalities

    #======================================================================

    def close(self):
        self.write('GTL\n')
        self.dev.clear()
        self.dev.close()
        del self



    def reset(self):

        self.write('*CLS')

        self.write('MEASSTOP')

        self.write('CALLSO')

        self.write("*RST")

        self.wait_for_completion()

        self.write("*CLS")

        self.wait_for_completion()





    #def reboot(self):    # FOR CMU ONLY BUT THIS NEVER WORKED

        #self.write("*SYST:REB:ERR ON")
        #No command available for Anritsu8820C


    def gotolocal(self):

        self.write('GTL')



    def write(self, command):

        logger=logging.getLogger('%s.write' % self.name)

        logger.debug ("   %s write command \"%s\"" % (self.name, command))

        self.dev.write(command)

        self.wait_for_completion()


    def ask(self,command):
        logger=logging.getLogger('%s.write' % self.name)
        logger.debug("  %s write command \"%s\"" % (self.name,command))
        reading=self.dev.ask(command)
        return reading
    def preset(self):

        #self.write("SYSTem:RESet:ALL")
        self.write('PRESET')
        self.wait_for_completion()



    def read(self, command):

        logger=logging.getLogger('%s.read' % self.name)



        logger.debug ("   %s read command \"%s\"" % (self.name, command))

        self.dev.write(command)
        reading= self.dev.read()
        '''
        lettercount = 25

        readingshort = reading[0:lettercount]

        if len(reading)>lettercount:

            logger.debug ("   %s read response \"%s\"..........." % (self.name, readingshort))

        else:

            logger.debug ("   %s read response \"%s\"" % (self.name, reading))
        '''


        return reading



    def wait_response(self, scpi_query_cmd="", exp_rsp="", timeout = 5):

        logger = logging.getLogger('%s.wait_response' % self.name)



        if scpi_query_cmd == "":

            logger.error("no scpi command query")

            return

        else:

            logger.debug("Waiting for response: %s" %exp_rsp)

            start_time= int(time.time())

            elapsed_time = 0

            while elapsed_time <= timeout:

                status = self.read(scpi_query_cmd)

                logger.debug("response is: %s " %status)

                if status == exp_rsp:

                    logger.info("Expected response received within %s secs"  % timeout)

                    return True

                time.sleep(1)

                cum_time = int(time.time())

                elapsed_time = cum_time - start_time

                logger.debug (elapsed_time)



            logger.error("Expected response not received within %s secs"  % timeout)



            return False



    def wait_for_completion(self, timeout=30):

        num_iter      = 0

        NUM_ITER_MAX  = timeout

        POLL_INTERVAL = 1

        while (num_iter < NUM_ITER_MAX):

            completed=(self.read("*OPC?") == "1")

            if completed: break

            num_iter += 1

            time.sleep(POLL_INTERVAL)

        if num_iter == NUM_ITER_MAX:

            sys.exit(CfgError.ERRCODE_SYS_CMW_TIMEOUT)



    def read_state(self):

        #curr_state = self.read("FETCh:LTE:SIGN:PSWitched:State?")
        curr_state=self.ask('CALLSTAT?')  #Inquire the call processing status, response: 0 off, 1 idle, 2 idle(Regist), 3 Registration, 4, 5, 6 Connected, 13, 14, 15, 16, 17
        self.wait_for_completion()

        return curr_state



    def insert_pause(self, tsec):

        logger = logging.getLogger('%s.insert_pause' % self.name)

        remaining_time = tsec

        sleep_time   = 5  if (tsec > 5) else 1

        logger.info("pause %s [sec]" % tsec)

        while (remaining_time > 0):

            logger.info("  remaining time : %s [sec]" % (remaining_time))

            time.sleep(sleep_time)

            remaining_time -= sleep_time



    def check_sw_version(self):

        logger=logging.getLogger("%s.check_sw_version" % self.name)



        #check_l   = {'CMW_BASE':(3, 2, 50), 'CMW_LTE_Sig':(3, 2, 81), 'CMW_WCDMA_Sig':(3,2,50), 'CMW_GSM_Sig':(3,2,50), }
        #check_l   ={'ANR_BASE':'22.67 #008', 'ANR_WCDMA':'22,23, #008', 'ANR_GSM': '22,18,#006', 'ANR_LTE':'22,54,#009', }
        check_l   ={'Version':(24.67), 'WCDMA':(22.23), 'GSM': (22.18), 'LTE':(22.54),}
        verdict_d = {0:'PASS', 1:'FAIL', 2:'UNKNOWN'}



        #cmwswinfo=self.read("SYSTem:BASE:OPTion:VERSion?")

        version=self.read('MCFV?')+' '+self.read('MCMSV?') # Read Anritsu Firmware and Software version
        value=re.compile('[.0-9]+[.][0-9][0-9]').findall(version) # Extract Version
        key=re.compile('[a-zA-Z]+').findall(version)              #Extract Type of Version
        anrswinfo=dict(zip(key,value))
        #print anrswinfo
        self.wait_for_completion()

        logger.debug("System FW Version and SW Version? %s" % anrswinfo)



        if not anrswinfo:

            logger.warning("Failed retrieving Anritsu info. SW version may be incorrect")

            return 'None'



        result=[]

        for k,v in check_l.iteritems():

            verdict=2

            # Extract THE SW version string
            check_str=k
            for key,value in anrswinfo.iteritems():
                if k==key:
                    if value==v or value>v:
                        verdict=0
                        break
                    else:
                        verdict=1
                        logger.error("Incorrect SW version %s. Required v%s or later" % (check_str, v))
                        break
                else:
                    verdict=2

            logger.info("%s check point ...%s" % (check_str, verdict_d[verdict]))
            result.append(check_str)
            result.append(verdict_d[verdict])
        testerinfo = ' '.join(result)
        return testerinfo


    ##Function to be implemented
    #======================================================================

    # DEBUG functionalities

    #======================================================================
    '''
    def scpi_monitor_start(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ANALysis")

        self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ON")

        self.insert_pause(5)

        self.write("TRACe:REMote:MODE:DISPlay:ENABle LIVE")



    def scpi_monitor_stop(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle OFF")

        #if 1: self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        #raw_input("scpi_monitor_stop: Checkpoint")



    def scpi_error_count(self):

        tmp=self.write("SYSTem:ERRor:COUNt?")

        return tmp



    def scpi_error_queue(self):

        err_queue=self.write("SYSTem:ERRor:ALL?")

        print "ERROR QUEUE : %s" % err_queue



    def scpi_monitor_clear(self):

        self.write("TRACe:REMote:MODE:DISPlay:ENABle ANALysis")

        self.write("TRACe:REMote:MODE:DISPlay:CLEar")

        self.write("TRACe:REMote:MODE:DISPlay:ENABle OFF")

        self.insert_pause(5)



    #======================================================================

    # External fader functions

    #======================================================================

    def external_fader_scenario_siso(self, route_conf):

        self.write(r'ROUTe:LTE:SIGN:SCENario:SCFading %s' % route_conf)



    def external_fader_scenario(self, route_conf):

        self.write(r'ROUTe:LTE:SIGN:SCENario:TROFading:EXTernal %s' % route_conf)



    def digiIQin_conf(self, path_index, pep, lev):

        self.write(r'SENSe:LTE:SIGN:IQOut:PATH%s?' % path_index)

        self.write(r'CONFigure:LTE:SIGN:IQIN:PATH%s %s, %s' % (path_index, pep, lev))

    '''


if __name__ == '__main__':
    '''
    #import visa
    #visa.log_to_screen()
    anr=Anritsu('Anritsu','10.21.141.234')
    #anr.write('*IDN?')
    #anr.read('*IDN?')
    print anr.ask('*IDN?')
    #anr.write('TAGSEL? SYSINFO')
    print anr.read('MCFV?') #Firmware version
    print anr.read('MCMSV?') #Measuring software version
    print anr.read('MCOV?') #Tester OS version
    anr.write('CALLSA')
    anr.wait_for_completion()
    print anr.ask('*ESR?')
    print anr.ask('*STB?')
    anr.write('CALLSO')
    anr.wait_for_completion()
    anr.write('GTL\n')
    #print anr.ask('*ESR2?')
    anr.wait_for_completion()
    print anr.read_state()
    cwswinfo='3.2.50,3.2.81,3.2.81,3.2.82'
    print anr.check_sw_version()
    #time.sleep(2)
    anr.close()
    '''

    pass