#-------------------------------------------------------------------------------
# Name:        cmw500.py
# Purpose:
#
# Author:      joashr
#
# Created:     12/11/2013
#-------------------------------------------------------------------------------

import os, sys, time,  logging, math, re


try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-2])
    sys.path.append(test_env_dir)
    import test_env


from pl1_testbench_framework.common.instr.vxi_11 import vxi_11_connection

from pl1_testbench_framework.wcdma.common.config.cfg_test import cfg_test

from pl1_testbench_framework.common.config.CfgError import CfgError

from pl1_testbench_framework.wcdma.instr.ber import ber

from pl1_testbench_framework.wcdma.instr.hsdpa_ack_meas import hsdpa_ack_meas

from pl1_testbench_framework.wcdma.instr.hsdpa_trans_meas import hsdpa_trans_meas

from pl1_testbench_framework.common.utils.user_defined_types import enum

import pl1_testbench_framework.wcdma.common.config.umts_utilities as umts_utils

import pl1_testbench_framework.wcdma.common.parser.xml_utils as xml_utils

import pl1_testbench_framework.common.instr.Cmw as cmw

class rohde_and_schwarz_CMW500(vxi_11_connection):
    default_lock_timeout=20000

class conn_config:
    """
    class structure for the connection configuration parameters for the CMW
    """

    # rmc data rate list for CMW500
    DL_RMC_DATARATE_LIST = ["R12K2", "R64K", "R144K", "R384K"]
    UL_RMC_DATARATE_LIST = ["R12K2", "R64K", "R144K", "R384K", "R768K"]

    def __init__(self):

        self.ul_rmc_rate       = ""
        self.dl_rmc_rate       = ""

    def __str__(self):
        print "---------------------------------------------"
        print "  ul_data_rate      : %s" % self.ul_rmc_rate
        print "  dl_data_rate      : %s" % self.dl_rmc_rate
        print "---------------------------------------------"
        return ""

    def set_rmc_data_rate(self, datarate_str):
        """
        get ul and dl rmc data rate
        """

        return (self.check_data_rate(datarate_str))

    def check_data_rate(self, datarate_str):

        """
        check that the date rate is supported by the cmw tester
        returns 1 if supported, otherwise 0
        """
        check_pass = 1

        dl_rmc_dataRate_dic = dict.fromkeys(self.DL_RMC_DATARATE_LIST, 1)
        ul_rmc_dataRate_dic = dict.fromkeys(self.UL_RMC_DATARATE_LIST, 1)

        matchObj = re.match('dl_(R.*)_ul_(R.*)', datarate_str, re.I)

        if matchObj:
            self.dl_rmc_rate = matchObj.group(1)
            self.ul_rmc_rate = matchObj.group(2)

            try:
                dl_rmc_dataRate_dic[self.dl_rmc_rate.upper()]
            except KeyError:
                print "dl data rate %s is not supported from RMC rate selection %s" %(self.dl_rmc_rate, datarate_str)
                print "supported rates are %s" %self.DL_RMC_DATARATE_LIST
                check_pass = 0

            try:
                ul_rmc_dataRate_dic[self.ul_rmc_rate.upper()]
            except KeyError:
                print "ul data rate %s is not supported from RMC rate selection %s " %(self.ul_rmc_rate, datarate_str)
                print "supported rates are %s" %self.UL_RMC_DATARATE_LIST
                check_pass = 0

        else:
            print "RMC data rate %s is not supported" %datarate_str
            print "or the data rate is in the wrong format!"
            print "supported RMC rates are"
            for dl_rmc_rate in self.DL_RMC_DATARATE_LIST:
                for ul_rmc_rate in self.UL_RMC_DATARATE_LIST:
                    print "dl_%s_ul_%s" %(dl_rmc_rate, ul_rmc_rate)
            check_pass = 0

        return check_pass


class CmuControl(cmw.Cmw):

    code = CfgError()

    # connecion_config cmw data rate mappings
    rate = dict()
    rate={'12.2':'A', '10.2':'B', '7.95':'C', '7.4':'D',
          '6.7':'E', '5.9':'F', '5.15':'G', '4.75':'H',
          'M':'M' }
    # note key 'M' is A + C + F + H

    # connection config cmw DL resources mappings
    DLResources = dict()
    DLResources={'1/32':'P0031', '1/30':'P0032','1/28':'P0036','1/26':'P0038',
                 '1/24':'P0042', '1/22':'P0045','1/20':'P0050', '1/18':'P0056',
                 '1/14':'P0071', '1/12':'P0083', '1/10':'P0100', '1/8':'P0125',
                 '1/6':'P0167', '1/4':'P0250','1/2':'P0500', '1':'P1000'}

    # specifies either CS, PS or combined CS and PS
    connTypeEnum  = enum('PS', 'CS', 'CS_PS')


    # this is the number of measurements corresponding to each HSDPA ACK Tx
    # and is fixed, refer to command
    NUM_MEAS_PER_TX         = 4
    MAX_NUM_HSDPA_CODES     = 16  # maximum number of HS-DSCH codes
    NO_MEASURED_FRAMES_STR  = '0'
    INVALID_BLER_MEAS       = -1


    def __init__(self, name, ip_addr):
        loggerCmw=logging.getLogger(__name__ + '__init__')
        self.name = name
        loggerCmw.debug ('init-routine')
        self.dev = None

        try:
            self.dev = rohde_and_schwarz_CMW500(ip_addr, timeout=10)
        except:
            loggerCmw.error("CMW500 CONNECTION FAILURE: cmwname=%s, cmwip=%s" % (self.name, ip_addr))
            sys.exit(self.code.ERRCODE_SYS_CMW_CONN)

        self.read("*RST")                  # Reset and query
        self.dev.write("*cls")
        while self.read("*OPC?") != "1": time.sleep(1)  # Wait until completion
        self.resultsFile = ""

        self.ber_meas = ber()
        carrier1=0
        carrier2=1
        MAX_NUM_CARRIERS = 2
        self.hsdpa_meas = [ (-1) for j in range(MAX_NUM_CARRIERS)]
        self.hsdpa_meas[carrier1] = hsdpa_ack_meas(carrier=1)
        self.hsdpa_meas[carrier2] = hsdpa_ack_meas(carrier=2)
        self.conn_config = conn_config()
        # connection type can be CS, PS or combined CS_PS, used in attach method
        self.connType = self.connTypeEnum.CS
        self.trans_meas_1= self.init_hsdpa_ack_trans_array() # for carrier 1
        self.trans_meas_2= self.init_hsdpa_ack_trans_array() # for carrier 2
        self.hsdpa_bler_1 = -1      # for carrier 1
        self.hsdpa_bler_2 = -1      # for carrier 2
        self.hsdpa_measured_subframes = -1
        self.medianCqi_1 = -1   # median CQI for carrier 1
        self.medianCqi_2 = -1   # median CQI for carrier 2
        self.hsdpa_configured_subframes = -1 # number od subframes to measure
        self.dc_hsdpa = 0       # dual cell hsdpa, default disabled

    def set_dc_hsdpa(self):
        self.dc_hsdpa = 1

    def get_dc_hsdpa(self):
        return self.dc_hsdpa

    def init_hsdpa_ack_trans_array(self):
        trans_meas= [ (-1) for j in range(self.NUM_MEAS_PER_TX)]
        for idx in range(self.NUM_MEAS_PER_TX):
            # first transmission is 1 rather than 0 to align
            # with cmw500 display
            trans_meas[idx] = hsdpa_trans_meas(txNum=idx+1)
        return trans_meas

    def set_num_scheduled_subframes(self, numSubframes):

        self.hsdpa_num_scheduled_subframes = numSubframes

    def get_num_scheduled_subframes(self):

        return (self.hsdpa_num_scheduled_subframes)


    def set_medianCqi(self, carrier = 1, val=-1):

        loggerCmw = logging.getLogger(__name__ + 'set_medianCqi')

        if carrier == 1:
            self.medianCqi_1 = val

        elif carrier == 2:
            self.medianCqi_2 = val

        else:
            loggerCmw.error("carrier %s is not supported" %carrier)

    def get_medianCqi(self, carrier=1):

        loggerCmw = logging.getLogger(__name__ + 'get_medianCqi')

        if carrier == 1:
            return self.medianCqi_1

        elif carrier == 2:
            return self.medianCqi_2

        else:
            loggerCmw.error("carrier %s is not supported" %carrier)


    def close(self):
        loggerCmw=logging.getLogger(__name__ + 'cmu.close')
        if self.dev:
            loggerCmw.debug('Close instrument connection')
            self.dev.disconnect
        else:
            loggerCmw.debug('Instrument connection already closed or not opened')

    def set_conn_type(self, conn=connTypeEnum.CS):
        self.connType = conn

    def get_conn_type(self):
        return self.connType

    def set_hsdpa_bler(self, dl_bler, carrier=1):
        if carrier == 1:
            self.hsdpa_bler_1 = dl_bler
        elif carrier == 2:
            self.hsdpa_bler_2 = dl_bler

    def get_hsdpa_bler(self, carrier=1):

        loggerCmw = logging.getLogger(__name__ + ' get_hsdpa_blers')
        if carrier == 1:
            return self.hsdpa_bler_1
        elif carrier == 2:
            return self.hsdpa_bler_2
        else:
            loggerCmw.error("carrier number %s is not supported" %carrier)


    def set_hsdpa_measured_subframes(self, numFrames):
        self.hsdpa_measured_subframes = numFrames

    def get_hsdpa_measured_subframes(self):
        return self.hsdpa_measured_subframes


    def waitForCompletion(self, timeout=30):
        self.wait_for_completion(timeout=timeout)

    def read(self, command):

        loggerCmw=logging.getLogger(__name__ + 'cmu.read')
        loggerCmw.debug ("   %s read command \"%s\"" % (self.name, command))

        numRetry = 0
        maxRetry = 1

        self.dev.write(command)
        while numRetry < maxRetry:
            reading = self.dev.read()[2].strip()
            if reading != "":
                break
            elif numRetry == maxRetry:
                loggerCmw.error (" Not able to read the following")
                loggerCmw.error ("   %s read command \"%s\"" % (self.name, command))
                loggerCmw.error ("   %s read response \"%s\"" % (self.name, reading))
                break
            time.sleep(0.5)
            numRetry +=1

        lettercount = 25
        readingshort = reading[0:lettercount]
        if len(reading)>lettercount:
            loggerCmw.debug ("   %s read response \"%s\"..........." % (self.name, readingshort))
        else:
            loggerCmw.debug ("   %s read response \"%s\"" % (self.name, reading))
        return reading

    """
    def reset(self):
        self.read("*RST")       # Reset and query
        self.WaitForCompletion()
        self.read("*CLS")      # Clear Status register and query
        self.WaitForCompletion()
        #while self.read("*OPC?") != "1": time.sleep(1)  # Wait until completion
    """

    def reset(self):
        self.waitForCompletion()
        self.write(r'*CLS')
        self.waitForCompletion()
        self.write("&ABO")
        self.write("&BRK")
        self.waitForCompletion()
        self.write("*RST")
        self.waitForCompletion()
        self.write("*CLS")
        self.waitForCompletion()
        self.write("&GTR")
        self.waitForCompletion()


    def change_cmu_state(self ,new_state, cmd=None, timeout=60):
        if (cmd):
            self.write('1;PROCedure:SIGNalling:ACTion %s' % cmd)
        state = ''
        while not (state == new_state):
            time.sleep(1)
            timeout -= 1
            if not (timeout > 0):
                print('ERROR - timed out waiting for CMU state to change to %s\n' % new_state)
                sys.exit(1)
            state =self.read('1;SENSe:SIGNalling:STATe?')


    #======================================================================
    # 3G FUNCTIONS
    #======================================================================
    def Cell_OFF(self):

        loggerCmw = logging.getLogger(__name__ + 'cmu.cell_OFF')

        #Get the current state
        cell_state = self.read("SOURce:WCDMa:SIGN:CELL:STATe?")
        loggerCmw.debug("Cell_OFF(): Initial Cell state %s" % cell_state)

        matchObj = None

        matchObj = re.match('OFF.*', cell_state, re.I)

        if not matchObj:
            loggerCmw.debug("Current Cell state is %s" %cell_state)
            loggerCmw.info("Turning CELL OFF")
            cmd_cmw="SOURce:WCDMa:SIGN:CELL:STATe OFF"
            self.write(cmd_cmw)
            cmd_query="SOURce:WCDMa:SIGN:CELL:STATe:ALL?"
            self.wait_response(scpi_query_cmd=cmd_query, exp_rsp="OFF,ADJ", timeout = 20)
        else:
            loggerCmw.debug("Current Cell state is %s" %cell_state)
            loggerCmw.debug("Cell is already turned off")
            loggerCmw.debug("SCPI command will not be sent again to the instrument!")


    def Cell_ON(self):
        loggerCmw = logging.getLogger(__name__ + 'cmu.cell_ON')

        #Get the current state
        cell_state = self.read("SOURce:WCDMa:SIGN:CELL:STATe?")
        loggerCmw.debug("Cell_ON():Initial Cell state %s" % cell_state)
        cell_on = False
        matchObj = re.match('OFF.*', cell_state, re.I)
        if matchObj:
            loggerCmw.info("Turning CELL ON")
            cmd_cmw="SOURce:WCDMa:SIGN:CELL:STATe ON"
            self.write(cmd_cmw)
            cmd_query="SOURce:WCDMa:SIGN:CELL:STATe:ALL?"
            cell_on = self.wait_response(scpi_query_cmd=cmd_query, exp_rsp="ON,ADJ", timeout = 30)
            if not cell_on:
                sys.exit(self.code.ERRCODE_SYS_CMW_CELL_ON)

    def readState(self):

        query_conn_state_str = ""

        if (self.get_conn_type() == self.connTypeEnum.CS):

            query_conn_state_str = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'

        elif (self.get_conn_type() == self.connTypeEnum.PS):

            query_conn_state_str = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'

        elif (self.get_conn_type() ==  self.connTypeEnum.CS_PS):

            query_conn_state_str    = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'

            query_conn_state_str2   = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'


        else:

            loggerCmw.error("Connection type %s is not supported!" %(self.get_conn_type()))

        curr_state = self.read(query_conn_state_str)

        self.wait_for_completion()

        return curr_state

    def dut_connect(self, poll_interval = 5, max_num_poll_intervals = 10 ):

        loggerCmw = logging.getLogger('dut_connect')

        connected = False

        # get the current state
        curr_state = self.read('FETCh:WCDMa:SIGN:PSWitched:STATe?')

        loggerCmw.debug("dut_connect(): DUT current state : %s " %curr_state)

        if (curr_state != "ATT"):

            loggerCmw.error("DUT must be attached before connection can be established")

            return connected

        query_conn_state_str = ""

        if (self.get_conn_type() == self.connTypeEnum.CS):

            self.write('CALL:WCDMa:SIGN:CSWitched:ACTion CONNect')

            query_conn_state_str = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'

        elif (self.get_conn_type() == self.connTypeEnum.PS):

            self.write('CALL:WCDMa:SIGN:PSWitched:ACTion CONNect')

            query_conn_state_str = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'

        elif (self.get_conn_type() ==  self.connTypeEnum.CS_PS):

            self.write('CALL:WCDMa:SIGN:CSWitched:ACTion CONNect')
            query_conn_state_str    = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'
            query_conn_state_str2   = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'


        else:

            loggerCmw.error("Connection type %s is not supported!" %(self.get_conn_type()))

            return connected

        num_poll_intervals = 0

        while (num_poll_intervals < max_num_poll_intervals):

            num_poll_intervals += 1

            loggerCmw.info("CONNECT_PROCEDURE: iteration %d of %d" % (num_poll_intervals, max_num_poll_intervals))

            connected = (self.read(query_conn_state_str) == 'CEST')

            if connected:

                break

            time.sleep(poll_interval)

        if (self.get_conn_type() ==  self.connTypeEnum.CS_PS):
            num_poll_intervals = 0

            while (num_poll_intervals < max_num_poll_intervals):

                num_poll_intervals += 1

                loggerCmw.info("CONNECT_PROCEDURE: iteration %d of %d" % (num_poll_intervals, max_num_poll_intervals))

                connected = (self.read(query_conn_state_str2) == 'CEST')

                if connected:

                    break

                time.sleep(poll_interval)


        loggerCmw.info("dut_connect(): DUT final state : %s " %self.read(query_conn_state_str) )

        return connected

    def dut_disconnect(self, poll_interval = 2, max_num_poll_intervals = 10):

        loggerCmw = logging.getLogger('dut_disconnect')

        disconnected=True

        if (self.get_conn_type() == self.connTypeEnum.PS):

            self.write('CALL:WCDMa:SIGN:PSWitched:ACTion CONNect')

            query_state_str = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'

            rel_conn_str = 'CALL:WCDMa:SIGN:PSWitched:ACTion DISConnect'


        elif (self.get_conn_type() == self.connTypeEnum.CS):

            query_state_str = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'

            rel_conn_str = 'CALL:WCDMa:SIGN:CSWitched:ACTion DISConnect'

        elif (self.get_conn_type() ==  self.connTypeEnum.CS_PS):
            query_state_str = 'FETCh:WCDMa:SIGN:CSWitched:STATe?'
            query_state_str2 = 'FETCh:WCDMa:SIGN:PSWitched:STATe?'
            rel_conn_str = 'CALL:WCDMa:SIGN:CSWitched:ACTion DISConnect'

        else:

            loggerCmw.error("Connection type %s is not supported!" %(self.get_conn_type()))

            return disconnected

        # Get the current state
        curr_state = self.read(query_state_str)

        loggerCmw.debug("dut_disconnect(): DUT initial state : %s " % curr_state)

        if (curr_state != "CEST"):

            loggerCmw.error("DUT must be connected before the disconnection")

            return disconnected

        self.write(rel_conn_str)

        num_poll_intervals = 0

        while (num_poll_intervals < max_num_poll_intervals):

            num_poll_intervals += 1

            loggerCmw.info("DISCONNECT_PROCEDURE: iteration %d of %d" % (num_poll_intervals, max_num_poll_intervals))

            if self.get_conn_type() == self.connTypeEnum.CS or self.get_conn_type() ==  self.connTypeEnum.CS_PS:

                disconnected = (self.read(query_state_str) == 'REG')
            else:
                disconnected = (self.read(query_state_str) == 'ATT')

            if disconnected : break

            time.sleep(poll_interval)

        if (self.get_conn_type() ==  self.connTypeEnum.CS_PS):
            num_poll_intervals = 0
            while (num_poll_intervals < max_num_poll_intervals):
                num_poll_intervals += 1
                loggerCmw.info("DISCONNECT_PROCEDURE: iteration %d of %d" % (num_poll_intervals, max_num_poll_intervals))
                disconnected = (self.read(query_state_str2) == 'ATT')
                if disconnected : break
                time.sleep(poll_interval)

        loggerCmw.debug("dut_disconnect(): DUT final state : %s " % self.read(query_state_str))

        self.waitForCompletion()

        return disconnected

    def dut_attach(self):

        loggerCmw = logging.getLogger('DUT_Attach')

        attached=False
        NUM_ITER_MAX = 10
        POLL_INTERVAL = 5

        loggerCmw.info("DUT_ATTACH_PROCEDURE:")

        while self.read("*OPC?") != "1": time.sleep(1)

        cell_state = self.read("SOURce:WCDMa:SIGN:CELL:STATe?")    # Get the current state

        if (cell_state == "OFF"):
            self.Cell_ON()

        num_iter = 0

        while ( num_iter < NUM_ITER_MAX):
            num_iter += 1
            loggerCmw.info("ATTACH_PROCEDURE: iteration %d of %d" % (num_iter, NUM_ITER_MAX))
            attached= (self.read('FETCh:WCDMa:SIGN:PSWitched:STATe?') == 'ATT')
            if attached: break
            time.sleep(POLL_INTERVAL)

        loggerCmw.info("dut_attach(): DUT final state : %s " % self.read("FETCh:WCDMa:SIGN:PSWitched:STATe?"))

        return attached


    def dut_detach(self, poll_interval = 2, max_num_poll_intervals = 10):

        loggerCmw = logging.getLogger('DUT_Detach')

        detached=True

        # Get the current state
        curr_state = self.read('FETCh:WCDMa:SIGN:PSWitched:STATe?')


        loggerCmw.debug("dut_detach(): DUT initial state : %s " % curr_state)

        if (curr_state != "CEST") and (curr_state != "ATT"):

            loggerCmw.error("DUT must be ATTACHED or CONNECTED before detaching")

            return detached

        self.write('CALL:WCDMa:SIGN:CSWitched:ACTion UNRegister')

        num_poll_intervals = 0

        while (num_poll_intervals < max_num_poll_intervals):

            num_poll_intervals += 1

            loggerCmw.info("DETACH_PROCEDURE: iteration %d of %d" % (num_poll_intervals, max_num_poll_intervals))

            detached = (self.read('FETCh:WCDMa:SIGN:PSWitched:STATe?') == 'ON')

            if detached: break

            time.sleep(poll_interval)

        loggerCmw.debug("dut_detach(): DUT final state : %s " % self.read('FETCh:WCDMa:SIGN:PSWitched:STATe?'))

        self.waitForCompletion()

        return detached

    def read_scenario(self ):
        instr_scenario = self.read('ROUTe:WCDMa:SIGN:SCENario?')
        return instr_scenario

    def set_scenario(self, scen = 'DEFAULT'):
        # scenario Standard Cell, dual carrier, standard cell fading, dual carrier fading
        #scen=""

        if scen == 'SCFading':
            self.write('ROUTe:WCDMa:SIGN:SCENario:SCFDiversity:INTernal RF1C,RX1,RF1C,TX1,RF2C,TX2')
            instr_scen = self.read_scenario()
            if instr_scen == "SCFD,INT":
                pass
            else:
                sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

        elif self.dc_hsdpa:
            scen="DCAR"
            self.write('ROUTe:WCDMa:SIGN:SCENario:%s RF1C,RX1,RF1C,TX1,RF1C,TX3' %scen)
            instr_scen = self.read_scenario()
            if scen == instr_scen:
                pass
            else:
                self.write('ROUTe:WCDMa:SIGN:SCENario:%s RF1C,RX1,RF1C,TX1,RF1C,TX2' %scen)
                instr_scen = self.read_scenario()
                if scen == instr_scen:
                    pass
                else:
                    sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)
        else:
            self.write('ROUTe:WCDMa:SIGN:SCENario:SCELl RF1C,RX1,RF1C,TX1')
            instr_scen = self.read_scenario()
            if instr_scen == 'SCEL':
                pass
            else:
                sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

    def set_default_rf_settings(self):

        # RF Frequency, band
        band = 1
        uarfcn = umts_utils.default_uarfcn(band)
        self.set_rf_band(band)
        self.set_uarfcn(uarfcn)

        # common for both carriers
        self.write('CONFigure:WCDMa:SIGN:RFSettings:EATTenuation:INPut 0')

        # RF Input and Output Attenuation
        self.set_ext_attenuation_rf_out(carrier=1, dB_att = 0)

        #RF Power DL
        powerdBm = -70
        self.set_rf_power_dbm(power=powerdBm, carrier=1)
        self.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier1:AWGN OFF')

        if self.dc_hsdpa:
            self.set_rf_power_dbm(power=powerdBm, carrier=2)
            self.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier2:AWGN OFF')

        #RF Power UL, expected nominal power settings
        self.write('CONFigure:WCDMa:SIGN:RFSettings:ENPMode ULPC')
        # RF settings complete ---------------------------------------------------------


    def set_ext_attenuation_rf_out(self, carrier=1, dB_att=0):

        self.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:EATTenuation:OUTPut %s' %(carrier, dB_att))


    def set_data_rate(self, datarate_str):

        loggerCmw=logging.getLogger(__name__ + ' set_data_rate')

        data_rate_valid = 0

        data_rate_valid = self.conn_config.set_rmc_data_rate(datarate_str)

        # change value of DPCH code for RMC data rate to remove channelisation
        # code overlap
        if data_rate_valid:

            if self.conn_config.dl_rmc_rate.upper() == 'R144K':

                self.set_dl_chan_code_level(dl_chan='DPCH', code=12, level_dB=-10.3)

            elif self.conn_config.dl_rmc_rate.upper() == 'R384K':

                self.set_dl_chan_code_level(dl_chan='DPCH', code=6, level_dB=-10.3)

            else:

                loggerCmw.debug (" using default value of 3 of DPCH code for %s" %self.conn_config.dl_rmc_rate.upper())

            self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:DRATe %s, %s'
                       %(self.conn_config.dl_rmc_rate, self.conn_config.ul_rmc_rate))

        return data_rate_valid

    def set_rf_band(self, band, carrier=1):
        # set band for carrier 1
        # carrier 2 band automatically set to the same as carrier 1 if dc-hsdpa configured
        self.write('CONFigure:WCDMa:SIGN:CARRier%s:BAND OB%s' %(carrier, band))

    def set_uarfcn(self, uarfcn, carrier=1):
        # set uarfcn for carrier 1
        # carrier 2 is automatically to 5MHz from carrier 1 if dc-hsdpa configured
        self.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:CHANnel:DL %s' %(carrier, uarfcn))

    def get_uarfcn(self, carrier=1):
        uarfcn = self.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:CHANnel:DL?' %carrier)
        return uarfcn

    def get_freq_Hz(self, carrier=1):
        freq_Hz = self.read('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:FREQuency:DL?' %carrier)
        return freq_Hz

    def set_rf_power_dbm(self, power, carrier=1):
        # can be set independently for carrier 1 and carrier 2 if dc-hsdpa configured
        self.write('CONFigure:WCDMa:SIGN:RFSettings:CARRier%s:COPower %s' %(carrier, power))


    def set_dl_chan_code_level(self, dl_chan="PICH", code=6, level_dB = -8.3):

        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:%s %s' %(dl_chan, level_dB))
        self.set_dl_chan_code(dl_chan=dl_chan, code=code)

    def set_dl_chan_code(self, dl_chan="PICH", code=6):
        self.write('CONFigure:WCDMa:SIGN:DL:CODE:%s %s' %(dl_chan, code))


    def hsdpa_physical_downlink_settings(self):
        """
        set physical downlink settings for carrier 1
        """

        config_list = []

        config_list.append ("")

        config_list.append ( "%-24s %-18s" % ("Channel( Carrier 1)", "Level"))
        config_list.append ( "%-24s %-18s" % ("==================",  "====="))

        pcpich_level = -10.2
        self.set_pcpich_code_level(carrier=1, leveldB=pcpich_level)
        config_list.append ( "%-24s %-18s" % ("P-CPICH", pcpich_level))

        psch_level = -15.2
        ssch_level = psch_level
        pccpch_level = -12.2
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PSCH %s' %psch_level)
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:SSCH %s' %ssch_level)
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PCCPch %s' %pccpch_level)
        config_list.append ( "%-24s %-18s" % ("P-SCH", psch_level))
        config_list.append ( "%-24s %-18s" % ("S-SCH", ssch_level))
        config_list.append ( "%-24s %-18s" % ("P-CCPCH", pccpch_level))


        # SCCPH power level and channelisation code
        sccpch_level = -12.2
        self.set_dl_chan_code_level(dl_chan='SCCPch', code=2, level_dB=sccpch_level)
        config_list.append ( "%-24s %-18s" % ("S-CCPCH", sccpch_level))

        # PICH power level and channelisation code
        pich_level = -15.2
        self.set_dl_chan_code_level(dl_chan='PICH', code=2, level_dB=pich_level)
        config_list.append ( "%-24s %-18s" % ("PICH", pich_level))

        # AICH power level and channelisation code
        aich_level = -15.2
        self.set_dl_chan_code_level(dl_chan='AICH', code=3, level_dB=aich_level)
        config_list.append ( "%-24s %-18s" % ("AICH", aich_level))

        # DPCH power and channelisation code
        dpch_level = -18.2
        self.set_dl_chan_code_level(dl_chan='DPCH', code=3, level_dB=dpch_level)
        config_list.append ( "%-24s %-18s" % ("DPCH", dpch_level))

        # F-DPCH power and channelisation ocde
        fdpch_level = -18.2
        self.set_dl_chan_code_level(dl_chan='FDPCh', code=6, level_dB=fdpch_level)
        config_list.append ( "%-24s %-18s" % ("F-DPCH", fdpch_level))

        # DPCH enhanced settings
        self.configure_enhanced_dl_dpch()

        # *****************************************************************************
        # Configure 2 HS-SCCH: level, channelization code, UE ID and dummy UE ID
        # *****************************************************************************
        hssch_level_1 = -20.2
        hssch_level_2 = -20.2
        self.set_hssch_level(hssch_num=1, carrier=1, leveldB=hssch_level_1)
        self.set_hssch_level(hssch_num=2, carrier=1, leveldB=hssch_level_2)
        self.set_hssch_code(hssch_num=1, carrier=1, codeNum=2)
        self.set_hssch_code(hssch_num=2, carrier=1, codeNum=7)
        config_list.append ( "%-24s %-18s" % ("HS-SCCH #1", hssch_level_1))
        config_list.append ( "%-24s %-18s" % ("HS-SCCH #2", hssch_level_2))

        self.set_default_ue_id_hssch(carrier=1)

        # HS-PDSCH Enhanced Settings
        self.set_hsdsch_mpo(carrier=1, control="AUTO", pwrOffsetManual="")
        # unscheduled frame type for HSDPA
        # possible types are 'DUMMy', 'DTX'
        self.hsdsch_unsched_frames(carrier=1, usFrameType='DUMMY')

        # *****************************************************************************
        # Configure HS-PDSCH: level and first channelization code number
        # *****************************************************************************

        hsdsch_level = -1.2
        self.set_hsdsch_level(carrier=1, leveldB = hsdsch_level)
        self.set_hsdsch_chanelisation_code(code=1, carrier=1)
        config_list.append ( "%-24s %-18s" % ("HS-PDSCH", hsdsch_level))


        # // *****************************************************************************
        # Set level and channelization code of E-AGCH, E-HICH and E-RGCH.
        # *****************************************************************************
        eagch_level = -20.2
        ehich_level = -20.2
        ergch_level = -20.2
        self.set_dl_chan_code_level(dl_chan='EAGCh', code=3, level_dB=eagch_level)
        self.set_dl_chan_code_level(dl_chan='EHICh', code=6, level_dB=ehich_level)
        self.set_dl_chan_code_level(dl_chan='ERGCh', code=6, level_dB=ergch_level)
        config_list.append ( "%-24s %-18s" % ("E-AGCH", eagch_level))
        config_list.append ( "%-24s %-18s" % ("E-HICH", ehich_level))
        config_list.append ( "%-24s %-18s" % ("E-RGCH", ergch_level))

        config_list.append ("")

        for line in config_list:
            print line

        if self.dc_hsdpa:

            self.hsdpa_physical_downlink_settings_carrier2()


    def hsdpa_fading_physical_downlink_settings(self, cpich_power, hs_pdsch_power):
        """
        set physical downlink settings for carrier 1 fading scenario
        """
        # Power levels (dB) From HSDPA fading test requirements:
        #    CPICH [-10, -12] dB
        pwr_PSCH   = -15
        pwr_SSCH   = -15
        pwr_SCCPCH = -15
        pwr_PCCPCH = -12
        #    HS-PDSCH [-3, -6] dB
        pwr_DPCH   = -15
        pwr_PICH   = -10
        pwr_AICH   = -10


        config_list = []

        config_list.append ("")

        config_list.append ( "%-24s %-18s" % ("Channel( Carrier 1)", "Level"))
        config_list.append ( "%-24s %-18s" % ("==================",  "====="))


        self.set_pcpich_code_level(carrier=1, leveldB=cpich_power)
        config_list.append ( "%-24s %-18s" % ("P-CPICH", cpich_power))


        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PSCH %s' %pwr_PSCH)
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:SSCH %s' %pwr_SSCH)
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PCCPch %s' %pwr_PCCPCH)
        config_list.append ( "%-24s %-18s" % ("P-SCH", pwr_PSCH))
        config_list.append ( "%-24s %-18s" % ("S-SCH", pwr_SSCH))
        config_list.append ( "%-24s %-18s" % ("P-CCPCH", pwr_PCCPCH))


        # SCCPH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='SCCPch', code=2, level_dB=pwr_SCCPCH)
        config_list.append ( "%-24s %-18s" % ("S-CCPCH", pwr_SCCPCH))

        # PICH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='PICH', code=2, level_dB=pwr_PICH)
        config_list.append ( "%-24s %-18s" % ("PICH", pwr_PICH))

        # AICH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='AICH', code=3, level_dB=pwr_AICH)
        config_list.append ( "%-24s %-18s" % ("AICH", pwr_AICH))

        # DPCH power and channelisation code
        self.set_dl_chan_code_level(dl_chan='DPCH', code=3, level_dB=pwr_DPCH)
        config_list.append ( "%-24s %-18s" % ("DPCH", pwr_DPCH))

        # F-DPCH power and channelisation ocde
        #fdpch_level = -18.2
        #self.set_dl_chan_code_level(dl_chan='FDPCh', code=6, level_dB=fdpch_level)
        #config_list.append ( "%-24s %-18s" % ("F-DPCH", fdpch_level))

        # DPCH enhanced settings
        #self.configure_enhanced_dl_dpch()
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:SSCode OFF')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:POFFset 0')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:TOFFset 0')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:PHASe PCPich')

        # *****************************************************************************
        # Configure 2 HS-SCCH: level, channelization code, UE ID and dummy UE ID
        # *****************************************************************************
        hssch_level_1 = -12.0
        hssch_level_2 = -12.0
        self.set_hssch_level(hssch_num=1, carrier=1, leveldB=hssch_level_1)
        self.set_hssch_level(hssch_num=2, carrier=1, leveldB=hssch_level_2)
        self.set_hssch_code(hssch_num=1, carrier=1, codeNum=2)
        self.set_hssch_code(hssch_num=2, carrier=1, codeNum=7)
        config_list.append ( "%-24s %-18s" % ("HS-SCCH #1", hssch_level_1))
        config_list.append ( "%-24s %-18s" % ("HS-SCCH #2", hssch_level_2))

        self.set_default_ue_id_hssch(carrier=1)

        # HS-PDSCH Enhanced Settings
        self.set_hsdsch_mpo(carrier=1, control="AUTO", pwrOffsetManual="")
        # unscheduled frame type for HSDPA
        # possible types are 'DUMMy', 'DTX'
        self.hsdsch_unsched_frames(carrier=1, usFrameType='DUMMY')

        # *****************************************************************************
        # Configure HS-PDSCH: level and first channelization code number
        # *****************************************************************************

        self.set_hsdsch_level(carrier=1, leveldB = hs_pdsch_power)
        self.set_hsdsch_chanelisation_code(code=1, carrier=1)
        config_list.append ( "%-24s %-18s" % ("HS-PDSCH", hs_pdsch_power))

        config_list.append ("")

        for line in config_list:
            print line




    def hsdpa_physical_downlink_settings_carrier2(self):
        """
        set physical downlink settings for carrier 1
        """
        carrier = 2

        config_list = []

        config_list.append ( "%-24s %-18s" % ("Channel( Carrier 2)", "Level"))
        config_list.append ( "%-24s %-18s" % ("==================",  "====="))

        pcpich_level = -11
        self.set_pcpich_code_level(carrier=carrier, leveldB=pcpich_level)
        config_list.append ( "%-24s %-18s" % ("P-CPICH", pcpich_level))


        # *****************************************************************************
        # Configure 2 HS-SCCH: level, channelization code, UE ID and dummy UE ID
        # *****************************************************************************
        hssch_level_1 = -18.0
        hssch_level_2 = -18.0
        self.set_hssch_level(hssch_num=1, carrier=carrier, leveldB=hssch_level_1)
        self.set_hssch_level(hssch_num=2, carrier=carrier, leveldB=hssch_level_2)
        self.set_hssch_code(hssch_num=1, carrier=carrier, codeNum=2)
        self.set_hssch_code(hssch_num=2, carrier=carrier, codeNum=7)

        config_list.append ( "%-24s %-18s" % ("HS-SCCH #1", hssch_level_1))
        config_list.append ( "%-24s %-18s" % ("HS-SCCH #2", hssch_level_2))

        self.set_default_ue_id_hssch(carrier=carrier)

        # HS-PDSCH Enhanced Settings
        self.set_hsdsch_mpo(carrier=carrier, control="AUTO", pwrOffsetManual="")
        self.hsdsch_unsched_frames(carrier=carrier, usFrameType='DUMMY')

        # *****************************************************************************
        # Configure HS-PDSCH: level and first channelization code number
        # *****************************************************************************
        hsdsch_level = -1.6
        self.set_hsdsch_level(carrier=carrier, leveldB = hsdsch_level)
        self.set_hsdsch_chanelisation_code(carrier=carrier, code=1)
        config_list.append ( "%-24s %-18s" % ("HS-PDSCH", hsdsch_level))

        config_list.append ("")

        for line in config_list:
            print line


    def set_hssch_level(self, hssch_num, carrier, leveldB):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:LEVel:HSSCch%s %s'
                   %(carrier, hssch_num, leveldB))

    def set_hssch_code(self, hssch_num, carrier, codeNum):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:CODE:HSSCch%s %s'
                    %(carrier, hssch_num, codeNum))

    def set_default_ue_id_hssch(self, carrier=1):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:HSSCch1:UEID #HAAAA' %carrier)
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:HSSCch2:UEID #HAAAA'%carrier)
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:HSSCch1:IDDummy #H5555' %carrier)
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:HSSCch2:IDDummy #H12AA' %carrier)

    def set_hsdsch_level(self, carrier=1, leveldB=-1):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:LEVel:HSPDsch %s' %(carrier, leveldB))

    def set_hsdsch_chanelisation_code(self, code, carrier=1):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:CODE:HSPDsch %s'
                   %(carrier, code))

    def set_hsdsch_mpo(self, carrier, control="AUTO", pwrOffsetManual=""):
        """
        configure measurement power offset for HS-DSCH
        """
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:ENHanced:HSPDsch:POFFset %s'
                    %(carrier, control))

    def hsdsch_unsched_frames(self, carrier=1, usFrameType='DUMMY'):
        """
        Defines the transmission in unscheduled HS-DSCH subframes.
        """
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:ENHanced:HSPDsch:USFRames %s'
                    %(carrier, usFrameType))

    def set_pcpich_code_level(self, carrier=1, leveldB=0):
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier%s:LEVel:PCPich %s' %(carrier, leveldB))

    def check_code_conflict(self):

        str_rsp = self.read('CONFigure:WCDMa:SIGN:DL:CARRier1:CODE:CONFlict?')

        matchObj = re.match('ON', str_rsp, re.I)

        if matchObj:

            return 1

        else:

            return 0

    def physical_downlink_settings(self):

        # Physical DL Settings
        self.write('CONFigure:WCDMa:SIGN:DL:CARRier:LEVel:PCPich -3.3')

        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PSCH -8.3')
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:SSCH -8.3')
        self.write('CONFigure:WCDMa:SIGN:DL:LEVel:PCCPch -5.3')

        # SCCPH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='SCCPch', code=2, level_dB=-5.3)

        # PICH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='PICH', code=2, level_dB=-8.3)

        # AICH power level and channelisation code
        self.set_dl_chan_code_level(dl_chan='AICH', code=3, level_dB=-8.3)

        # DPCH power and channelisation code
        self.set_dl_chan_code_level(dl_chan='DPCH', code=3, level_dB=-10.3)

        # F-DPCH power and channelisation ocde
        self.set_dl_chan_code_level(dl_chan='FDPCh', code=6, level_dB=-10.3)

        # AICH enhanced settings
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:AICH:TTIMing 3')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:AICH:ACKNowledge POSitive')

        # DPCH enhanced settings
        self.configure_enhanced_dl_dpch()
        """
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:SSCode OFF')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:POFFset 0')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:TOFFset 8')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:PHASe PCPich')
        """


    def configure_enhanced_dl_dpch(self):
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:SSCode OFF')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:POFFset 0')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:TOFFset 8')
        self.write('CONFigure:WCDMa:SIGN:DL:ENHanced:DPCH:PHASe PCPich')

    def physical_uplink_settings(self):

        # Physical Uplink Settings
        self.write('CONFigure:WCDMa:SIGN:UL:MUEPower 33')
        self.write('CONFigure:WCDMa:SIGN:UL:UEPClass:REPorted ON')
        self.write('CONFigure:WCDMa:SIGN:UL:POFFset -80')
        self.write('CONFigure:WCDMa:SIGN:UL:SCODe #H0')

        # Open Loop Power Control
        self.write('CONFigure:WCDMa:SIGN:UL:OLPControl:CVALue -29')
        self.write('CONFigure:WCDMa:SIGN:UL:OLPControl:INTerference -80')
        self.read('SENSe:WCDMa:SIGN:UL:OLPControl:EIPPower?')

        # PRACH
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:SIGNature #B1111111111111111')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:SUBChannels #B000000000001')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:MRETrans 6')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:AICH 1')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:SSIZe 3')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:PREamble:MCYCles 2')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:MESSage:POFFset -5')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:MESSage:LENGth 0.02')
        self.write('CONFigure:WCDMa:SIGN:UL:PRACh:DRXCycle 8')

        # for TPC use default settings - send SCPI commands at later date

        # Beta C, Beta D settings for RMC's, Voice and Video
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:RMC1 8, 15') # RMC 12.2
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:RMC2 5, 15') # RMC 64
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:RMC3 4, 15') # RMC 144
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:RMC4 5, 15') # RMC 384
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:RMC4 4, 15') # RMC 768
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:VOICe 11, 15')
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:VIDeo 9, 15')

    def add_hsdpa_uplink_settings(self, BetaC=8, BetaD = 15, DeltaACK=5,
                                  DeltaNACK=5, DeltaCQI=2):

        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:HSDPa %s,%s,%s,%s,%s'
                    %(BetaC, BetaD, DeltaACK, DeltaNACK, DeltaCQI))


    def add_hsupa_uplink_settings(self):
        # deltaE-DPCCH
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:HSUPa:EDPCch 5')
        # number of reference E-TFCI's
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:HSUPa:ETFCi:NUMBer 1')
        # reference E-TFCI
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:HSUPa:ETFCi:REFerence 11,67,71,75,81,90,100,127')
        # power offset for each reference E-TFCI
        self.write('CONFigure:WCDMa:SIGN:UL:GFACtor:HSUPa:ETFCi:POFFset 4,18,23,26,27,28,29,29')

    def config_hsupa_settings(self, hsupa_cat='6', tti_ms='2'):

        loggerCmw = logging.getLogger(__name__ + ' config_hsupa_settings')

        tti_ms = str(tti_ms)

        if tti_ms == '10':
            self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:TTI M10')
        elif tti_ms == '2':
            self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:TTI M2')
        else:
            loggerCmw.error("HSUPA %s is not supported!" %(tti_ms))
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:PDU 656')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:UECategory:MANual %s' %(hsupa_cat))
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:UECategory:REPorted OFF')
        # use E-TFCI table 0
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:ETFCi:TINDex 0')

        # *****************************************************************************
        # Configure HARQ RV configuration, minimum set E-TFCI, happy bit delay
        # condition, puncturing limit non-max, maximum channelisation code and
        # initial serving grant.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:HRVersion RV0')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:ETFCi:MSET 9')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:HBDC 100')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:PLPLnonmax 0.84')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:MCCode S224')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:ISGRant OFF')

        # *****************************************************************************
        # Configure the HARQ profile: power offset and max retransmissions.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:HARQ:POFFset 0')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:HARQ:RETX 7')

        # *****************************************************************************
        # Configure E-AGCH settings:
        # E-RNTIs of UE, absolute grant pattern (length, indices, scopes and types),
        # pattern repetition and unscheduled TTIs.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:UEID #HAAAA, #H12AA')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:PATTern:LENGth 1')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:PATTern:INDex 31')
        # OFF: absolute grant applies to all HARQ processes
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:PATTern:SCOPe OFF')

        # OFF: use primary UE-ID
        # ON: use secondary UE-ID
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:PATTern:TYPE OFF')

        # Specifies whether the absolute grant pattern shall be transmitted only
        # once or continuously.
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:PATTern:REPetition CONT')

        # DUMMy: send absolute grants to dummy UE-IDs
        # DTX: switch E-AGCH off
        # Defines the transmission in unscheduled TTIs, for max Tput all should
        # be scheduled
        self.write('CONFigure:WCDMa:SIGN:CELL:HSUPa:EAGCh:UTTI DTX')

        # *****************************************************************************
        # Configure E-RGCH / E-HICH settings:
        # disable fill-up frames with dummies
        # E-HICH: react on UL CRC, signature 1
        # E-RGCH: signature 3, continuous user defined 4-bit pattern 0011
        # *****************************************************************************
        # only relevevant for 10ms frame, fill up frames with dummies
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:EHRCh:FUFDummies ON")
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:EHICh:MODE CRC")
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:EHICh:SIGNature 1")
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:ERGCh:SIGNature 0")
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:ERGCh:MODE CONT")
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:ERGCh:PATTern:LENGth 1")

        # 0 = DOWN, 1 = UP, - = DTX
        self.write("CONFigure:WCDMa:SIGN:CELL:HSUPa:ERGCh:PATTern \'00000000\'")

    def config_hsdpa_settings(self, modulation='64-QAM', numCodes='15', ki=62):
        """
        hsdpa configuration
        """

        numCodes = int(numCodes)
        # manually set HSDPA category
        if self.dc_hsdpa:
            hsdpa_cat = str(24)
        else:
            hsdpa_cat = str(14)

        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:UECategory:MANual %s' %hsdpa_cat)
        # disable reported UE category
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:UECategory:REPorted OFF')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:TYPE UDEFined')
        self.set_hsdpa_inter_tti(carrier=1, tti_num=1)
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:UDEFined:HARQ 6')
        self.set_hsdpa_tbi(carrier=1, ki=ki)
        self.set_hsdsch_num_codes(carrier=1, numCodes=numCodes)
        self.set_hsdpa_modulation(carrier=1, modulation=modulation)

        if self.dc_hsdpa:
            self.config_hsdpa_settings_carrier2(modulation='64-QAM', numCodes='15', ki=62)

    def config_hsdpa_fading_settings(self):
        """
        hsdpa fading configuration
        """
        # manually set HSDPA category
        if self.dc_hsdpa:
            hsdpa_cat = str(24)
        else:
            hsdpa_cat = str(14)
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:UECategory:MANual %s' %hsdpa_cat)

        # disable reported UE category
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:UECategory:REPorted OFF')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:TYPE CQI')

        # HSDPA Fading CQI Settings:
        self.config_hsdpa_cqi_settings()

    def config_hsdpa_cqi_settings(self):
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier2:HSDPa:CQI:ENABle ON')
        self.write('CONFigure:WCDMa:SIGN:CELL:HSDPa:CQI:TINDex FOLLow')


    def config_hsdpa_settings_carrier2(self, modulation='64-QAM', numCodes='15', ki=62):
        """
        hsdpa configuration for carrier 2
        """

        carrier = 2
        self.set_hsdpa_inter_tti(carrier=carrier, tti_num=1)
        self.set_hsdpa_tbi(carrier=carrier, ki=ki)
        self.set_hsdsch_num_codes(carrier=carrier, numCodes=int(numCodes))
        self.set_hsdpa_modulation(carrier=carrier, modulation=modulation)


    def set_hsdpa_tbi(self, carrier=1, ki=62):
        kiStr = self.check_hsdpa_tbi(ki)
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier%s:HSDPa:UDEFined:TBLock %s' %(carrier, kiStr))

    def set_hsdpa_inter_tti(self, carrier=1, tti_num=1):
        """
        Minimum distance between two consecutive transmission time intervals in which
        the HS-DSCH is allocated to the UE
        """
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier%s:HSDPa:UDEFined:TTI %s'
                    %(carrier, tti_num))

    def check_hsdpa_tbi(self, ki):
        """
        check for valid hsdpa transport block size index
        """
        loggerCmw = logging.getLogger(__name__ + ' check_hsdpa_tbi')
        if ki >=0 and ki <= 62:
            return ki
        else:
            loggerCmw.error('non valid ki, valid range is 0 to 62')
            sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

    def set_hsdsch_num_codes(self, carrier=1, numCodes=15):
        numCodesStr = self.check_num_hsdsch_codes(numCodes)
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier%s:HSDPa:UDEFined:NCODes %s'
                    %(carrier, numCodesStr))


    def check_num_hsdsch_codes(self, numCodes):

        loggerCmw = logging.getLogger(__name__ + ' check_num_hsdsch_codes')

        if numCodes >= 1 and numCodes <= 15:
            return numCodes
        else:
            loggerCmw.error('number of HSDSCH codes %s not supported, valid range is 1 to 15' %numCodes)
            sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)

    def set_hsdpa_modulation(self, carrier=1, modulation='64-QAM'):
        modulation_str = self.check_hsdpa_modulation(modulation)
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier%s:HSDPa:UDEFined:MODulation %s'
                    %(carrier, modulation_str))

    def check_hsdpa_modulation(self, modulation):

        loggerCmw = logging.getLogger(__name__ + ' check_hsdpa_modulation')

        if modulation == "QPSK":
            return "QPSK"
        elif modulation == "16-QAM":
            return "Q16"
        elif modulation == "64-QAM":
            return "Q64"
        else:
            loggerCmw.error('modulation %s not recognised, values supported are QPSK, 16-QAM and 64-QAM' %modulation)
            sys.exit(self.code.ERRCODE_TEST_FAILURE_PARAMCONFIG)


    def connection_config(self):

        #Select test mode as UE terminated call type and specify SRB data rate
        self.write('CONFigure:WCDMa:SIGN:CONNection:UETerminate Test')
        self.write('CONFigure:WCDMa:SIGN:CONNection:SRBData R3K4, R3K4')

        # note that this is only required if  TMODe type is set to voice
        self.write('CONFigure:WCDMa:SIGN:CONNection:VOICe:CODec NB')
        self.write('CONFigure:WCDMa:SIGN:CONNection:VOICe:AMR:NARRow %s' %self.rate['12.2'])

        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:TYPE RMC')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:DRATe R12K2, R12K2')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:TMODe MODE2')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:RLCMode TRAN')
        # note that SCPI command below is only relevant when
        # when an RMC with symmetric DL/UL data rate is used.
        # just put in a check for this
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:UCRC ON')

        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:DLRessources %s' %self.DLResources['1'])
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:RMC:DATA PRBS9')

    def hspa_connection_config(self):
        self.write('CONFigure:WCDMa:SIGN:CONNection:UETerminate Test')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:TYPE HSPA')

        #CSPS: Establish both an RMC connection in the CS domain and
        #      an HSPA test mode connection in the PS domain.

        #CSOPs: Establish only an RMC connection in the CS domain.
        #       You can trigger an HSPA connection setup manually later on if desired.

        # *****************************************************************************
        # Configure the HSPA test mode:
        # test mode procedure, PRBS9 as data pattern, 10% CRC errors.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:PROCedure CSPS')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:DIRection HSPA')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:DATA PRBS9')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:EINSertion 10')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:EINSertion OFF')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:USDU 29360')

    def hspa_fading_connection_config(self):

        loggerCmw = logging.getLogger(__name__ + 'hspa_fading_connection_config')

        #Select test mode as UE terminated call type and specify SRB data rate
        self.write('CONFigure:WCDMa:SIGN:CONNection:UETerminate Test')
        self.write('CONFigure:WCDMa:SIGN:CONNection:SRBData R3K4, R3K4')

        # *****************************************************************************
        # Configure general test mode settings: Select test mode type and keep test
        # loop during reconfiguration.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:TYPE HSPA')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:KTLReconfig ON')


        # *****************************************************************************
        # Configure the HSPA test mode:
        # test mode procedure, PRBS9 as data pattern, 10% CRC errors.
        # *****************************************************************************
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:PROCedure CSPS')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:DIRection HSDPA')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:DATA PRBS9')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:EINSertion OFF')
        self.write('CONFigure:WCDMa:SIGN:CONNection:TMODe:HSPA:USDU 29360')

    def hsdpa_internal_fading_initial_config(self, fad_profile, noise_level):

        loggerCmw = logging.getLogger(__name__ + 'hsdpa_internal_fading_initial_config')
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle OFF")
        #self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard %s" %fad_profile)
        #self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:RESTart:MODE AUTO")
        #self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:GLOBal:SEED 0")
        #self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ILOSs:MODE NORMal")
        #self.wait_for_completion()
        self.write("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:ENABle ON")
        self.write("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:NOISe %s" %noise_level)
        self.write("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:NOISe %s" %noise_level)
        self.wait_for_completion()

        # Confirm the setting - Debug info
        loggerCmw.debug(">>>> Internal Fading simulator")
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:ENABle? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:ENABle?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:SNRatio? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:SNRatio?"))


    def reconfig_internal_fading(self, fad_profile, noise_level):

        loggerCmw = logging.getLogger(__name__ + 'reconfig_internal_fading')

        #self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard %s" %fad_profile)
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle ON")
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard %s" %fad_profile)
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:RESTart:MODE AUTO")
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:GLOBal:SEED 0")
        self.write("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ILOSs:MODE NORMal")
        self.wait_for_completion()

        self.write("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:NOISe %s" %noise_level)
        self.write("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:NOISe %s" %noise_level)
        self.wait_for_completion()

        # Confirm the setting - Debug info
        loggerCmw.debug(">>>> Internal Fading simulator")
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:FSIMulator:ENABle?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:FSIMulator:STANdard?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:ENABle? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:ENABle?"))
        loggerCmw.debug("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:SNRatio? %s" % self.read("CONFigure:WCDMa:SIGN:FADing:CARRier:AWGN:SNRatio?"))



    def network_settings(self):

        # specify index for primary scrambling code and activate PS domain
        self.write('CONFigure:WCDMa:SIGN:CELL:CARRier1:SCODe #H0')
        self.write('CONFigure:WCDMa:SIGN:CELL:PSDomain ON')

        # Specify network identities: MCC, MNC, network operation mode,
        self.write('CONFigure:WCDMa:SIGN:CELL:MCC 001')
        self.write('CONFigure:WCDMa:SIGN:CELL:MNC 01, D2')
        self.write('CONFigure:WCDMa:SIGN:CELL:NTOPeration M1')
        self.write('CONFigure:WCDMa:SIGN:CELL:LAC #H1')
        self.write('CONFigure:WCDMa:SIGN:CELL:RAC #B1')
        self.write('CONFigure:WCDMa:SIGN:CELL:URA #B1')
        self.write('CONFigure:WCDMa:SIGN:CELL:RNC #B1')
        self.write('CONFigure:WCDMa:SIGN:CELL:IDENtity #B1')
        self.write('CONFigure:WCDMa:SIGN:CELL:IDNode #B1')
        self.write('CONFigure:WCDMa:SIGN:CELL:BINDicator OFF')

        # Security Settings
        self.write('CONFigure:WCDMa:SIGN:CELL:SECurity:AUTHenticat ON')
        self.write('CONFigure:WCDMa:SIGN:CELL:SECurity:ENABle ON')
        self.write('CONFigure:WCDMa:SIGN:CELL:SECurity:SKEY #H000102030405060708090A0B0C0D0E0F')
        self.write('CONFigure:WCDMa:SIGN:CELL:SECurity:OPC #H00000000000000000000000000000000')
        self.write('CONFigure:WCDMa:SIGN:CELL:SECurity:SIMCard C3G')

        # Configure UE identity settings: use and set the default IMSI.
        self.write('CONFigure:WCDMa:SIGN:CELL:UEIDentity:USE ON')
        self.write("CONFigure:WCDMa:SIGN:CELL:UEIDentity:IMSI \'001010123456063\'")

        #Enable CS registration and PS attach. Enable IMEI request
        self.write('CONFigure:WCDMa:SIGN:CELL:REQuest:ADETach ON')
        self.write('CONFigure:WCDMa:SIGN:CELL:REQuest:IMEI ON')

        #Configure cell reselection information
        self.write('CONFigure:WCDMa:SIGN:CELL:RESelection:SEARch -32, -32, -32')
        self.write('CONFigure:WCDMa:SIGN:CELL:RESelection:QUALity -24, -115')

        #Configure timers and counters
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:T3212 0')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:T3312 0')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:OSYNch 4')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:PREPetitions 3')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:PPIF 18')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:ATOFfset 0')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:N313 N20')
        self.write('CONFigure:WCDMa:SIGN:CELL:TOUT:T313 3')

        #Configure reject causes
        self.write('CONFigure:WCDMa:SIGN:CELL:RCAuse:LOCation OFF')
        self.write('CONFigure:WCDMa:SIGN:CELL:RCAuse:ATTach OFF')

        # Enable UE measurement report, set interval between two report messages
        # and enable the evaluation of all information elements
        self.write('CONFigure:WCDMa:SIGN:UEReport:ENABle ON')
        self.write('CONFigure:WCDMa:SIGN:UEReport:RINTerval 1')
        self.write('CONFigure:WCDMa:SIGN:UEReport:CCELl:ENABle ON,ON,ON,ON,ON,ON')


    def initialConfig(self):
        """
        conf_s is class reference to test setup configuration
        test_plan_params is structure for current test within the test plan
        Above information is used to configure the CMW
        """

        loggerCmw = logging.getLogger('initialConfig')

        self.set_scenario()

        self.set_default_rf_settings()

        self.physical_downlink_settings()

        self.physical_uplink_settings()

        self.connection_config()

        self.network_settings()

        self.set_conn_type(conn= self.connTypeEnum.CS)

        self.waitForCompletion()

    def max_hspa_tputConfig(self, modulation='64-QAM', numHsdschCodes=15, ki = 62,
                            hsupa_cat=6, tti_ms = 10, dc_hsdpa=0):
        """
        Note that this applies to HSDPA Cat 14, HSUPA Cat 6 for the moment
        """

        loggerCmw = logging.getLogger('config_max_hspa_tput')

        if dc_hsdpa:

            self.set_dc_hsdpa()

            loggerCmw.info('dc-hsdpa configured')

        self.set_scenario()

        self.set_default_rf_settings()

        self.hspa_connection_config()

        self.hsdpa_physical_downlink_settings()

        self.config_hsdpa_settings(modulation= modulation, numCodes=numHsdschCodes, ki=ki)

        self.physical_uplink_settings()

        self.add_hsdpa_uplink_settings()

        self.add_hsupa_uplink_settings()

        self.config_hsupa_settings(hsupa_cat=hsupa_cat,tti_ms=tti_ms )

        # indicate PS connection for attach procedure
        self.set_conn_type(conn= self.connTypeEnum.PS)

    def hsdpa_fading_test_init_config(self, cpich_power, pdsch_power, chtype, dc_hsdpa=0):
        """
        Note that this applies to HSDPA Fading test scenario only
        """

        loggerCmw = logging.getLogger('hsdpa_fading_Config')

        self.set_scenario(scen = 'SCFading')

        self.set_default_rf_settings()

        self.hsdpa_internal_fading_initial_config(chtype, -90)

        self.hspa_fading_connection_config()

        self.hsdpa_fading_physical_downlink_settings(cpich_power, pdsch_power)

        self.config_hsdpa_fading_settings()

        # indicate PS connection for attach procedure
        self.set_conn_type(conn = self.connTypeEnum.PS)


    def conf_hsdpa_ack_meas(self, timeout_sec=10):

        # *****************************************************************************
        # Configure repetition mode and number of HSDPA subframes to be measured.
        # *****************************************************************************

        loggerCmw = logging.getLogger('conf_hsdpa_ack_meas')

        self.write('CONFigure:WCDMa:SIGN1:HACK:TOUT %s' %timeout_sec)
        self.write('CONFigure:WCDMa:SIGN:HACK:REPetition SINGleshot')
        self.write('CONFigure:WCDMa:SIGN:HACK:MSFRames %s' %self.get_num_scheduled_subframes())
        self.write('CONFigure:WCDMa:SIGN:HACK:HARQ ALL')

    def get_instr_hsdpa_bler(self, carrier=1, testType="DEFAULT"):
        """
        called from get_hsdpa_ack_meas
        Read HSDPA BLER obtained in the last measurement
        without re-starting the measurement.
        """
        loggerCmw = logging.getLogger('get_hsdpa_bler')
        bler_str = self.read('FETCh:WCDMa:SIGN:HACK:BLER:CARRier%s?' %carrier)
        bler_list = bler_str.split(',')

        #bler = -1
        reliabilityList = ['4', '8']
        bler = self.INVALID_BLER_MEAS
        reliability = bler_list[0]
        if ((reliability == '0') or ((testType == 'HSPA_FADING_PERF') and (reliability in reliabilityList))):
        #if reliability == '0':
            bler = bler_list[1]
            bler = '%.3f' % float(bler)
        else:
            loggerCmw.debug("Reliabilty indicator is %s" %reliability)
            invalid_bler = bler_list[1]
            loggerCmw.debug("bler is %.3f" % float(invalid_bler))

        return bler

    def abort_hsdpa_ack_meas(self):
        """
        Abort HSDPA ACK measurements
        """
        loggerCmw = logging.getLogger('abort_hsdpa_ack_meas')
        self.write('ABORt:WCDMa:SIGN:HACK')
        loggerCmw.info("Aborting HSDPA ACK measurement")
        time.sleep(1)

    def abort_ber_meas(self):
        """
        Abort WCDMA BER measurements
        """
        loggerCmw = logging.getLogger('abort_ber_meas')
        self.write('ABORt:WCDMa:SIGN:BER')
        loggerCmw.info("Aborting BER measurements")
        time.sleep(1)

    def get_measured_subframes(self, testType='DEFAULT'):
        """
        Return the total number of already measured HSDPA subframes
        this should equal the expected number of subframes
        """
        reliabilityList = ['4', '8']
        loggerCmw = logging.getLogger('get_measured_subframes')
        numSf_str = self.read('FETCh:WCDMa:SIGN:HACK:MSFRames?')
        numSf_list = numSf_str.split(',')

        num = -1
        measured_subframes = self.NO_MEASURED_FRAMES_STR
        reliability = numSf_list[0]

        if ((reliability == '0') or ((testType == 'HSPA_FADING_PERF') and (reliability in reliabilityList))):
            measured_subframes = numSf_list[1]
        else:
            loggerCmw.info("Measurements are not reliable, reliability indicator %s" %reliability)

        return measured_subframes

    def get_ack_trans_meas(self, carrier=1, testType='DEFAULT'):

        loggerCmw = logging.getLogger('get_ack_trans_mea')

        trans_str = self.read('FETCh:WCDMa:SIGN:HACK:TRANsmission:CARRier%s?' %carrier)
        trans_list = trans_str.split(',')
        loggerCmw.debug('HSDPA ACK Trans stats %s' %trans_list)

        valid_meas = '0'    # denote valid measurement
        transmission_index = 0 # index for hsdpa_trans_meas class
        reliabilityList = ['4', '8']

        for idx in range(len(trans_list)):
            if idx == 0:
                # first value is the reliability indicator
                # valid measurement is 0
                valid_meas = trans_list[idx]
                continue
            if ((idx - 1) % self.NUM_MEAS_PER_TX) == 0:
                # keep getting the next 4 values
                # each set of values correspond to measurements
                # for ecah transmission
                if ((valid_meas == '0') or ((testType == 'HSPA_FADING_PERF') and (valid_meas in reliabilityList))):
                    tmpList = trans_list[idx:idx+ self.NUM_MEAS_PER_TX]
                    #self.trans_meas[transmission_index].set_results_list(tmpList)
                    if carrier == 1:
                        self.trans_meas_1[transmission_index].set_results_list(tmpList)
                    elif carrier == 2:
                        self.trans_meas_2[transmission_index].set_results_list(tmpList)
                    else:
                        loggerCmw.error('carrier number %s is not supported' %carrier)
                        break
                    transmission_index += 1
                else:
                    loggerCmw.error('Invalid HACK measurement')
                    break

    def display_ack_trans_meas(self, carrier=1):

        """
        Return all results of the "Transmissions" table row by row
        for HSDPA ACK, refer to SCPI command
        FETCh:WCDMa:SIGN<i>:HACK:TRANsmission:CARRier<carrier>?
        """

        loggerCmw = logging.getLogger(__name__ + ' display_ack_trans_meas')

        # format should match with formatting in hsdpa_trans_meas class
        trans_num_str =  "%18s"   % "Transmission [%]"
        sent_str      =  "%15s"   % "Sent"
        ack_str       =  "%15s"   % "ACK"
        nack_str      =  "%15s"   % "NACK"
        dtx_str       =  "%15s"   % "DTX"

        print ""
        carrierStr = "Carrier %s" %carrier
        print "%18s"  %carrierStr
        title_str = trans_num_str + sent_str + ack_str + nack_str + dtx_str
        print title_str

        if carrier == 1:
            for idx in range(self.NUM_MEAS_PER_TX):
                print self.trans_meas_1[idx]
        elif carrier == 2:
            for idx in range(self.NUM_MEAS_PER_TX):
                print self.trans_meas_2[idx]
        else:
            loggerCmw.error("Number of carriers %s is not supported" %carrier)

        print ""    # just add blank line
        return


    def get_hsdpa_ack_meas(self, numSubframes=2000, testType = 'DEFAULT'):

        """
        Get HSDPA ACK measurements
        Returns 1 if successful, otherwise 0
        """

        # perform HSDPA ACK measurements

        loggerCmw = logging.getLogger('get_hsdpa_ack_meas')

        self.set_num_scheduled_subframes(numSubframes)

        # determine the timeout per measurement
        # work out approximate time for numSubframes
        # (numSubframes * 0.002 = 10)
        meas_timeout_sec = int ( (self.get_num_scheduled_subframes() * 0.002) + 10 )

        meas_sample_time_sec = 2

        self.conf_hsdpa_ack_meas(timeout_sec=meas_timeout_sec)

        self.write('INIT:WCDMA:SIGN:HACK')

        self.waitForCompletion()

        num_iter = 0

        NUM_ITER_MAX = int(math.ceil(meas_timeout_sec/meas_sample_time_sec))
        reliabilityList = ['4', '8']

        loggerCmw.info("Obtaining HSDPA measurements for instrument. Please be patient ...")

        while ( num_iter < NUM_ITER_MAX ):

            num_iter += 1

            loggerCmw.debug("FETCHING HSDPA ACK MEAS: iteration %d of %d" % (num_iter, NUM_ITER_MAX))

            state=self.read('FETCh:WCDMa:SIGN:HACK:STATe?')

            loggerCmw.debug("FETCH STATE : %s" % state)

            if (state == 'RDY') :

                break

            loggerCmw.debug("Waiting for %02f [sec]... " % meas_sample_time_sec)

            time.sleep(meas_sample_time_sec)

        if state == 'RDY':

            avgCqi_1_str=self.read('FETCh:WCDMa:SIGN:HACK:MCQI:CARRier1?')

            avgTput=self.read('FETCh:WCDMa:SIGN:HACK:TRACe:THRoughput:TOTal:AVERage?')

            avgCqi_1_list = avgCqi_1_str.split(',')

            if self.dc_hsdpa:

                avgCqi_2_str=self.read('FETCh:WCDMa:SIGN:HACK:MCQI:CARRier2?')

                avgCqi_2_list = avgCqi_2_str.split(',')

            if ((avgCqi_1_list[0] == "0") or ((testType == 'HSPA_FADING_PERF') and (avgCqi_1_list[0] in reliabilityList))):

                # valid CQI measurement
                loggerCmw.debug('Median CQI, carrier 1 : %s' %avgCqi_1_list[1])

                self.set_medianCqi(carrier=1, val=avgCqi_1_list[1])

            if self.dc_hsdpa:

                if avgCqi_2_list[0] == "0":

                    # valid CQI measurement
                    loggerCmw.debug('Median CQI, carrier 2 : %s' %avgCqi_2_list[1])

                    self.set_medianCqi(carrier=2, val=avgCqi_2_list[1])

            hspda_stats_str_1 = self.read('FETCh:WCDMa:SIGN:HACK:THRoughput:CARRier1:ABSolute?')
            hack_meas_list_1 = hspda_stats_str_1.split(',')
            loggerCmw.debug('HSDPA ACK stats %s' %hack_meas_list_1)

            if self.dc_hsdpa:
                hspda_stats_str_2 = self.read('FETCh:WCDMa:SIGN:HACK:THRoughput:CARRier2:ABSolute?')
                hack_meas_list_2 = hspda_stats_str_2.split(',')
                loggerCmw.debug('HSDPA ACK stats %s' %hack_meas_list_2)

        self.hsdpa_meas[0].set_results_list(hack_meas_list_1)

        if self.dc_hsdpa:

            self.hsdpa_meas[1].set_results_list(hack_meas_list_2)


        self.get_ack_trans_meas(carrier=1, testType=testType)

        if self.dc_hsdpa:

            self.get_ack_trans_meas(carrier=2)

        numMeasuredFrames = self.get_measured_subframes(testType=testType)

        if numMeasuredFrames == self.NO_MEASURED_FRAMES_STR:

            return 0

        self.set_hsdpa_measured_subframes(numMeasuredFrames)

        blerVal = self.get_instr_hsdpa_bler(carrier=1, testType=testType)

        if blerVal == self.INVALID_BLER_MEAS:

            loggerCmw.info("HSDPA BLER Measurement for carrier 1 is Invalid!")

            return 0

        self.set_hsdpa_bler(blerVal, carrier=1)

        if self.dc_hsdpa:

            blerVal = self.get_instr_hsdpa_bler(carrier=2, testType=testType)

            if blerVal == self.INVALID_BLER_MEAS:

                loggerCmw.info("HSDPA BLER Measurements for carrier 2 is Invalid!")

                return 0

            self.set_hsdpa_bler(blerVal, carrier=2)


        return 1

    def display_hsdpa_bler_cqi_subframes(self, carrier=1):

        print " Carrier %s DL BLER %s %% Median CQI %s Measured Subframes %s/%s \n" %(carrier,
                self.get_hsdpa_bler(carrier=carrier),self.get_medianCqi(carrier=carrier),
                self.get_hsdpa_measured_subframes(), self.get_num_scheduled_subframes() )

    def get_ber_meas(self, Tblocks=500):

        loggerCmw = logging.getLogger('ber_meas')

        loggerCmw.info("Obtaining BLER for closed loop test mode. Please be patient ...")

        T_sec= 2                   # Measurement period [sec]

        T_out=20                   # Measurements timeout

        T_check=T_sec              # Time between two consecutive fetch on measurements

        ber_meas_list=[]

        ber_meas_str=""

        self.write('CONFigure:WCDMa:SIGN:BER:REPetition SINGleshot')

        self.write('CONFigure:WCDMa:SIGN:BER:TBLocks %s' %Tblocks)

        self.write('STOP:WCDMa:SIGN:BER')

        self.write('INIT:WCDMa:SIGN:BER')

        self.waitForCompletion()

        num_iter = 0

        NUM_ITER_MAX = int(math.ceil(T_out/T_check))

        while ( num_iter < NUM_ITER_MAX ):

            num_iter += 1

            loggerCmw.debug("FETCHING DLBLER MEAS: iteration %d of %d" % (num_iter, NUM_ITER_MAX))

            state=self.read('FETCh:WCDMa:SIGN:BER:STATe?')

            self.read('FETCh:WCDMa:SIGN:BER:STATe:ALL?')

            loggerCmw.debug("FETCH STATE : %s" % state)

            if (state == 'RDY') :

                break

            loggerCmw.debug("Waiting for %02f [sec]... " % T_check)

            time.sleep(T_check)

        if state == 'RDY':

            ber_meas_str = self.read('FETCh:WCDMa:SIGN:BER?')

            ber_meas_list = ber_meas_str.split(',')

            loggerCmw.debug('fetch ber list : %s' %ber_meas_list)

        self.ber_meas.set_results_list(ber_meas_list)



    def get_ber_verdict(self, dlBlerLim = 3):
        """"
        must execute function get_ber_meas prior to calling this method
        """

        dlVerdict = "FAIL"

        if self.ber_meas.reliability == '0':

            dlbler = float(self.ber_meas.dlbler)

            if dlbler <= dlBlerLim :

                dlVerdict = "PASS"

            else:

                dlVerdict = "FAIL"

        elif self.ber_meas.reliability == '-1':

            logging.warning("WARNING: No DL BLER Measurements taken ")

            self.write("ABORt:WCDMa:SIGN:BER")

            sys.exit(self.code.ERRCODE_SYS_CMW_NO_MEAS)


        else:

            logging.error("ERROR: Invalid DL BLER measurements. CMW500 BASE SW v3.2.10 or later is required")

            dlVerdict    = 'INV'

            sys.exit(self.code.ERRCODE_SYS_CMW_INVMEAS)

        return dlVerdict

    def get_sw_version(self):

        cmwswinfo=self.read("SYSTem:BASE:OPTion:VERSion?")

        return cmwswinfo

    def checkSwVersion(self, msg_str):

        #CMW_WCDMA_Meas,V3.2.60

        check_l   = {'CMW_BASE':(3, 2, 12), 'CMW_WCDMA_Sig':(3, 2, 11)}
        verdict_d = {0:'PASS', 1:'FAIL', 2:'UNKNOWN'}

        if not msg_str:
            logging.debug("R&S CheckSwVersion(): msg_str empty, nothing to do")
            return

        result=[]

        for k,v in check_l.iteritems():
            verdict=2
            # Extract THE SW version string
            tmp=re.compile('%s,[V|v|X|x][0-9]+[.][0-9]+[.][0-9]+' % k)
            check_str=k
            if tmp.search(msg_str):
                # here if string is detected
                check_str=(tmp.search(msg_str)).group()
                # Extract the version number
                tmp=re.compile('[.0-9]+')
                xyz=((tmp.search(check_str)).group()).split('.')
                x=int(xyz[0])
                y=int(xyz[1])
                z=int(xyz[2])
                if ((x>v[0]) or (x==v[0] and y>v[1]) or (x==v[0] and y==v[1] and z>=v[2])):
                    verdict=0
                else:
                    verdict=1
                    logging.error("Incorrect SW version %s. Required v%s.%s.%s or later" % (check_str, v[0], v[1], v[2]))
                    sys.exit(self.code.ERRCODE_SYS_CMW_INCORRECT_SW_VERSION)
            else:
                verdict=2
            logging.info("%s check point ...%s" % (check_str, verdict_d[verdict]))
            result.append(check_str)

        return result


if __name__ == '__main__':

    import logging

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'

    loglevel = 'DEBUG'

    cfg_multilogging(loglevel, logfile)

    logger=logging.getLogger(logname)

    test_config_xml_path  = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma_test_config.xml'])

    cmwip = xml_utils.get_cmwip(xml_file = test_config_xml_path)
    cmw500=CmuControl(name="cmw500", ip_addr=cmwip)

    cmw500.set_dc_hsdpa()
    scen=cmw500.read_scenario()
    print scen

    cmw500.gotolocal()


    cmw500.close()

    pass

