#######################################################################################################################
#
# amu instrument driver class
#
#######################################################################################################################
import time

import cmu
from vxi_11 import vxi_11_connection
import logging
from cmu import rohde_and_schwarz_CMW500 as rohde_and_schwarz_CMW500

# *****************************************
# TODO: add the High speed traing scenarios
# *****************************************
amu_fading_channels   = [ "LMEPA5L",
                          "LMEPA5M",
                          "LMEPA5H",
                          "LMEVA5L",
                          "LMEVA5M",
                          "LMEVA5H",
                          "LMEVA70L",
                          "LMEVA70M",
                          "LMEVA70H",
                          "LMETU70L",
                          "LMETU70M",
                          "LMETU70H",
                          "LMETU300L",
                          "LMETU300M",
                          "LMETU300H"]


amu_fading_channels_to_3gpp={ "LMEPA5L"   :  "EPA5L_AMU",
                              "LMEPA5M"   :  "EPA5M_AMU",
                              "LMEPA5H"   :  "EPA5H_AMU",
                              "LMEVA5L"   :  "EVA5L_AMU",
                              "LMEVA5M"   :  "EVA5M_AMU",
                              "LMEVA5H"   :  "EVA5H_AMU",
                              "LMEVA70L"  : "EVA70L_AMU",
                              "LMEVA70M"  : "EVA70M_AMU",
                              "LMEVA70H"  : "EVA70H_AMU",
                              "LMETU70L"  : "ETU70L_AMU",
                              "LMETU70M"  : "ETU70M_AMU",
                              "LMETU70H"  : "ETU70H_AMU",
                              "LMETU300L" :"ETU300L_AMU",
                              "LMETU300M" :"ETU300M_AMU",
                              "LMETU300H" :"ETU300H_AMU"    
                             }

amu_meas_period_ms = {"LMEPA5L"     : 100000,
                      "LMEPA5M"     : 100000,
                      "LMEPA5H"     : 100000,
                      "LMEVA5L"     : 100000,
                      "LMEVA5M"     : 100000,
                      "LMEVA5H"     : 100000,
                      "LMEVA70L"    : 100000,
                      "LMEVA70M"    : 100000,
                      "LMEVA70H"    : 100000,
                      "LMETU70L"    : 100000,
                      "LMETU70M"    : 100000,
                      "LMETU70H"    : 100000,
                      "LMETU300L"   : 100000,
                      "LMETU300M"   : 100000,
                      "LMETU300H"   : 100000
                      }
                      
                      
class rohde_and_schwarz_AMU200(vxi_11_connection):
    default_lock_timeout=20000

class AmuControl:
    
    def __init__(self, cmu, name, ip_addr):
        self.cmw  = cmu
        self.name = name
        self.dev  = rohde_and_schwarz_AMU200(ip_addr, timeout=20)
        self.reset()
        self.configure_ext_reference()
        self.SAMPLE_RATE='100 MHz'
        

    def close(self):
        self.write("&GTL")
        self.dev.disconnect


    def reboot(self):    # FOR CMU ONLY BUT THIS NEVER WORKED
        self.write("*SYST:REB:ERR ON")


    def gotolocal(self):
        self.write("&GTL")


    def reset(self):
        self.write(r"*CLS")
        self.write("&ABO")
        self.write("&BRK")
        self.write("*RST")
        self.wait_for_completion()
        self.write("*CLS")
        self.write("&GTR")
    
    def wait_for_completion(self, timeout=30):
        num_iter      = 0
        NUM_ITER_MAX  = timeout
        POLL_INTERVAL = 2
        while (num_iter < NUM_ITER_MAX):
            completed=(self.read("*OPC?") == "1")
            if completed: break 
            num_iter += 1
            time.sleep(POLL_INTERVAL)
        if num_iter == NUM_ITER_MAX:
            sys.exit(ERRCODE_SYS_CMW_TIMEOUT)     
    
        
    def cmw_finish(self):                   # RV - UNCALLLLLLLLLLLLLLLLLL
        # Best to restore the display when finishing remote control
        self.write("SYSTem:DISPlay:UPDate OFF")


    def write(self, command):
        logger_03=logging.getLogger("cmu.write")
        logger_03.debug ("   %s write command \"%s\"" % (self.name, command))

        self.dev.write(command)
        #self.wait_for_completion(timeout=60)


    def read(self, command):

        logger_03=logging.getLogger("cmu.read")
        logger_03.debug ("   %s read command \"%s\"" % (self.name, command))

        self.dev.write(command)
        #self.wait_for_completion(timeout=60)
        reading = self.dev.read()[2].strip()
        lettercount = 25
        readingshort = reading[0:lettercount]
        if len(reading)>lettercount:
            logger_03.debug ("   %s read response \"%s\"..........." % (self.name, readingshort))
        else:
            logger_03.debug ("   %s read response \"%s\"" % (self.name, reading))
        return reading


    # ===================================================
    # External 10 MHz Reference
    # ===================================================        
    def configure_ext_reference(self):
        self.write("ROSCillator:SOURce EXT")
        self.write("ROSCillator:EXT:FREQ 10 MHz")
        logging.debug("AMU reference source   : %s" % self.read("ROSCillator:SOURce?"))
        logging.debug("AMU reference frequency: %s [MHz]" % self.read("ROSCillator:EXT:FREQ?"))
            

    # ===================================================
    # BB Input
    # ===================================================        
    def bbin_off(self, path_index):
        # Turn OFF BB module
        self.write("SOURce%s:BBIN:STATe OFF" % path_index)


    def bbin_on(self, path_index):
        # Turn ON all the components
        self.write("SOURce%s:BBIN:STATe ON" % path_index)
        # pause
        if 0:
            tsleep=2
            logging.info("Inserted pause %d [sec]" % tsleep)
            time.sleep(tsleep)
        else: 
            self.wait_for_completion()      
        
        
    def bbin_conf(self, path_index):

        self.bbin_off(path_index)
        # BB DIGITAL mode configuration    
        self.write("SOURce%s:BBIN:MODE DIGital" % path_index)
        self.write("SOURce%s:BBIN:OLOad:HOLD:RESet" % path_index)
        self.write("SOURce%s:BBIN:IQSWap OFF" % path_index)
        self.write("SOURce%s:BBIN:SRATe:SOURce USER" % path_index)
        self.write("SOURce%s:BBIN:SRATe %s" % (path_index, self.SAMPLE_RATE))
        self.write("SOURce%s:BBIN:SRATe:ACTual?" % path_index)
        self.write("SOURce%s:BBIN:DIGital:ASETting:STATe OFF" % path_index)
        self.write("SOURce%s:BBIN:CFACtor 15" % path_index)
        self.write("SOURce%s:BBIN:POWer:PEAK 0" % path_index)

        #BB ON
        self.bbin_on(path_index)
        


    # ===================================================
    # Fader
    # ===================================================        
    def fader_off(self, path_index):
        self.write("SOURce%s:FSIMulator:STATe OFF" % path_index)
    
    def fader_on(self, path_index):
        self.write("SOURce%s:FSIMulator:STATe ON" % path_index)
        tsleep=2
        logging.info("Inserted pause %d [sec]" % tsleep)
        time.sleep(tsleep)
    
    def fader_conf_siso(self, vfreqHz, default_profile='LMEPA5L'):        

        # turn off fading simulator blocks
        self.fader_off(path_index=1)
        # For one path is query only
        #self.write("SOURce:FSIMulator:ROUTe FAA")
        # activate standard delay
        self.write("SOURce1:FSIMulator:DELay:STATe ON")
        # use Virtual Frequency for computing the Doppler shift
        self.write("SOURce1:FSIMulator:SDEStination BB")
        # set virtual Frequency for the Doppler shift, default unit [Hz]          
        self.write("SOURce1:FSIMulator:FREQuency %s" % vfreqHz)
        #set the default unit for speed 
        self.write("SOURce1:FSIMulator:SPEed:UNIT KMH") 
        # keep speed constant in case RF changes to compute the Doppler shift 
        self.write("SOURce1:FSIMulator:KCONstant DSHift")
        # restart the fader automatically
        self.write("SOURce1:FSIMulator:RESTart:MODE AUTO")
        # turn off hopping mode
        self.write("SOURce1:FSIMulator:HOPPing:MODE OFF")
        # set insertion loss for fading simulator
        self.write("SOURce1:FSIMulator:ILOSs:MODE NORMal")
        # User defined static propagation path 
        self.write("SOURce1:FSIM:DEL:GRO1:PATH1:PROF SPATh")
        # Basic Delay range={0...0 sec}
        #self.write("SOURce1:FSIM:DEL:GRO1:PATH1:BDELay 0E-6")
        #Additional Delay range={0...40E-6 sec}
        self.write("SOURce1:FSIM:DEL:GRO1:PATH1:ADELay 0")
        # Basic Delay range={0...5242.87E-6 sec}
        #self.write("SOURce1:FSIM:DEL:GRO2:PATH1:BDELay 100E-6")
        self.write("SOURce1:FSIM:DEL:GRO2:PATH1:PROF SPATh")
        self.write("SOURce1:FSIM:DEL:GRO2:PATH1:BDELay 0")
        # Additional Delay range={0...40E-6 sec}
        self.write("SOURce1:FSIM:DEL:GRO2:PATH1:ADELay 0")
        
        self.write("SOURce1:FSIM:DEL:GRO1:PATH1:STATe OFF")
        self.write("SOURce1:FSIM:DEL:GRO2:PATH1:STATe ON")
               
        self.fader_on(path_index=1)


    def fader_update_delay(self, td_usec):
        self.write("SOURce1:FSIM:DEL:GRO2:PATH1:BDELay %sE-6" % td_usec)     

                   
    
    # ===================================================
    # IQ Digital OUT
    # ===================================================            
    def digital_iq_off(self, path_index):
        self.write("SOURce%s:IQ:OUTPut:DIGital:STATe OFF" % path_index)

    
    def digital_iq_on(self, path_index):
        # reset any previous overflow error
        #self.write("SOURce%s:IQ:OUTPut:DIGital:OFLow:HOLD:STATe RESet" % path_index)
        # turn on DIDI OUT IQ
        self.write("SOURce%s:IQ:OUTPut:DIGital:STATe ON" % path_index)
        # pause
        if 0:
            tsleep=2
            logging.info("Inserted pause %d [sec]" % tsleep)
            time.sleep(tsleep)
        else: 
            self.wait_for_completion()           
        # hold any overflow error
        self.write("SOURce%s:IQ:OUTPut:DIGital:OFLow:HOLD:STATe ON" % path_index)        
        

    def digital_iq_conf(self, path_index):
        # switch digital output off        
        self.digital_iq_off(path_index)
        
        # switch analog output off

        self.write("SOURce%s:IQ:OUTPut:ANALog:STATe OFF" % path_index)
        self.write("SOURce%s:IQ:OUTPut:POWer:VIA LEVel" % path_index)
        self.write("SOURce%s:IQ:OUTPut:DIGital:SRATe:SOURce USER" % path_index)
        self.write("SOURce%s:IQ:OUTPut:DIGital:SRATe %s" % (path_index, self.SAMPLE_RATE))
        
        self.write("SOURce%s:IQ:OUTPut:DISPlay DIGital" % path_index)
        self.write("SOURce%s:IQ:OUTPut:DISPlay:AINFormation ILOSs" % path_index)
        
        # turn on the IQ OT
        self.digital_iq_on(path_index)
        

    def digital_iq_read_level(self, path_index):
        if not path_index in [1, 2]:
            logging.error("digital_read_level_path():: INVALID PATH INDEX, range={1,2} :: %s" % path_index)
            logging.warning("digital_read_level_path():: default path_index=%d" % int(1))
            path_index=1    
        dig_lev=self.read("SOURce%d:IQ:OUTPut:DIGital:POWer:LEVel?" % int(path_index))
        dig_pep=self.read("SOURce%d:IQ:OUTPut:DIGital:POWer:PEP?" % int(path_index))
        return dig_pep, dig_lev 

    # ===================================================
    # Graphics
    # ===================================================            
    def graphics_off(self, path_index):
        self.write("SOURce%s:BB:GRAPhics:STATe OFF" % path_index)

    
    def graphics_on(self, path_index):
        self.write("SOURce%s:BB:GRAPhics:STATe ON" % path_index)
        # pause
        if 0:
            tsleep=2
            logging.info("Inserted pause %d [sec]" % tsleep)
            time.sleep(tsleep)
        else: 
            self.wait_for_completion()    


    def graphics_conf(self, path_index):
        self.graphics_off(path_index)
        
        self.write("SOURce%s:BB:GRAPhics:SMARt:STATe ON" % path_index)
        self.write("SOURce%s:BB:GRAPhics:MODE PSPectrum" % path_index)
        self.write("SOURce%s:BB:GRAPhics:TRIGger:SOURce SOFTware" % path_index)
        self.write("SOURce%s:BB:GRAPhics:SRATe:MODE FULL" % path_index)
        
        self.graphics_on(path_index)
        
