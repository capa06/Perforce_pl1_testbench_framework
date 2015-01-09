#!/usr/bin/env python

#######################################################################################################################
#
# $Source: /home/cvs/test/python_utils/dmm.py,v $
# $Author: fsaracino $
# $Revision: #1 $
# $DateTime: 2014/11/03 18:01:42 $
#
#######################################################################################################################

import os, time, re, sys, logging

sys.path.append(os.sep.join(os.path.abspath('..').split(os.sep)[:]+['common', 'config']))

from vxi_11 import vxi_11_connection



class Agilent_34401A(vxi_11_connection):
    default_lock_timeout=5000
    idn_head='HEWLETT-PACKARD,34401A,0,11-5-3'
    

dmm_l= { '34401a-0': {'IP': r'10.21.141.145', 'GPIB_PORT' : r'gpib0,12'}, 
         '34401a-1': {'IP': r'10.21.141.145', 'GPIB_PORT' : r'gpib0,12'}}

# PSU specific command parameters
dmm_meas_channel_l=['DC_V', 'DC_I']




class DmmControl(object):
    
    def __init__(self, dmm_name):
        
        if not dmm_name in dmm_l.keys():
            raise Exception('must use -p [ %s ]' % ' | '.join(sorted(dmm_l.keys())))
        self.open(dmm_name)
        
    def open(self, dmm_name):    
        self.name=dmm_name
        self.gwip = dmm_l[dmm_name]['IP']
        self.gpib_addr = dmm_l[dmm_name]['GPIB_PORT']
        self.block_size=512
        self.currdc_buff=[]
        self.currdc_min=0
        self.currdc_avrg=0
        self.currdc_max=0
        self.currdc_dev=0
        self.dev = Agilent_34401A(self.gwip, device=self.gpib_addr, timeout=2)
        logging.info("Connected to DMM: name=%s, gwip=%s, port=%s\n" % (self.name, self.gwip, self.gpib_addr))
        self.reset()
        logging.debug("Reset completed\n")
    
    
    def reset(self):
        self.dev.write('*PSC 1')
        self.dev.write('*CLS')
        self.dev.write('*RST')    
    
    def config(self, channel):
        if not channel in dmm_meas_channel_l:
            logging.error('DmmControl.set(): Invalid channel %s. Skipping configuration ' % (channel))
            return 1
        logging.info("%s configuring channel %s" % (self.name, channel))
        if channel.upper()=='DC_I':
            # Measurements configuration
            self.dev.write('SENSe:FUNCtion "CURRent:DC"')            
            self.dev.write('SENSe:CURRent:DC:RANGe MAXimum')            
            self.dev.write('SENSe:CURRent:DC:RANGe:AUTO OFF')            
            self.dev.write('SENSe:CURRent:DC:Resolution MINimum')
            self.dev.write('SENSe:CURRent:DC:NPLCycles 0.2')
            
            # Trigger configuration
            self.dev.write('TRIGger:SOURce IMMediate')
            self.dev.write('TRIGger:DELay 0')
            self.dev.write('SAMPLe:COUNt %s' % self.block_size)
            self.dev.write('TRIGger:COUNt 1')

            # Math configuration
#            self.dev.write("CALCulate:STATe ON")
#            self.dev.write("CALCulate:FUNCtion AVERage")

                           
    def read_config(self, channel):
        if not channel in dmm_meas_channel_l:
            logging.error('DmmControl.set(): Invalid channel %s. Skipping configuration ' % (channel))
            return 1
        logging.info("%s Reading configuration for channel %s" % (self.name, channel))
        
        if channel.upper()=='DC_I':                        
            cmd_l=[ 'SENSe:FUNCtion?', 
                    'SENSe:CURRent:DC:RANGe?',
                    'SENSe:CURRent:DC:RANGe:AUTO?',
                    'SENSe:CURRent:DC:Resolution?',
                    'SENSe:CURRent:DC:NPLCycles?',
#                    'CALCulate:FUNCtion?',
#                    'CALCulate:STATe?',
                    'TRIGger:SOURce?',
                    'TRIGger:DELay?',
                    'SAMPLe:COUNt?',
                    'TRIGger:COUNt?']
            
            for cmd in cmd_l:
                self.dev.write(cmd)
                res=self.dev.read()
                logging.debug("%s %s" % (cmd, res[2]))


    def meas_fetch(self, channel):
        if not channel in dmm_meas_channel_l:
            logging.error('DmmControl.set(): Invalid channel %s. Skipping measurement' % (channel))
            return 1
        logging.info("%s Reading measurements for channel %s" % (self.name, channel))

        t0_msec=int(round(time.time() * 1000))
        
        # Trigger configuration
        self.dev.write('INITiate')
        time.sleep(0.050)        

        #Init measurements
        self.currdc_min=0
        self.currdc_avrg=0
        self.currdc_max=0
        self.currdc_dev=0
        self.currdc_buff=[]
        
        nread=0
        while (nread < self.block_size):
            self.dev.write('DATA:POINTs?')
            res=self.dev.read()
            nread=int(res[2])
 
        self.dev.write('FETCH?')
        readings = self.dev.read()
        read_l=[x.strip() for x in readings[2].split(',')]
        #logging.debug("CURRENT READING: LEN=%s, READ=%s" %(len(read_l), read_l))
        logging.debug("CURRENT READING: LEN=%s, READ=%s ..." %(len(read_l), read_l[0:3]))
        for x in read_l: 
            self.currdc_buff.append(x)
        t1_msec=int(round(time.time() * 1000))    
        logging.debug("Elapsed time %s [msec]" % (t1_msec-t0_msec))
        self.math_currdc(1)
#        return (self.currdc_min, self.currdc_max, self.currdc_avrg, self.currdc_dev)
        
        
    def meas_read(self, channel):
        if not channel in dmm_meas_channel_l:
            logging.error('DmmControl.set(): Invalid channel %s. Skipping measurement' % (channel))
            return 1
        logging.info("%s Reading measurements for channel %s" % (self.name, channel))

        t0_msec=int(round(time.time() * 1000))
        
        # Trigger configuration
        self.dev.write('INITiate')
        time.sleep(0.050)        
        
        #Init measurements
        self.currdc_min=0
        self.currdc_avrg=0
        self.currdc_max=0
        self.currdc_dev=0
        self.currdc_buff=[]
        
        self.dev.write('READ?')
        nread, read_l  = 0, []
        
        while (nread < self.block_size):
            readings = self.dev.read()
            read_l=[x.strip() for x in readings[2].split(',')]
            nread = nread + len(read_l) 
            logging.debug("CURRENT READING: LEN=%s, READ=%s..." %(len(read_l), read_l[0:4]))
            for x in read_l: 
                self.currdc_buff.append(x)

        t1_msec=int(round(time.time() * 1000))    
        logging.debug("Elapsed time %s [msec]" % (t1_msec-t0_msec))
        self.math_currdc(1)
#        return (self.currdc_min, self.currdc_max, self.currdc_avrg, self.currdc_dev)


    def math_currdc(self, conv_factor=1):
        """
        Return Min:Max:Mean:Variance for the curr_dc measurements  
        """
        # From string to float
        meas_l=[]
        for idx in range(len(self.currdc_buff[0:4])):
            x = float(self.currdc_buff[idx])
            meas_l.append(x)
        # Compute MIN
        self.currdc_min  =min(meas_l)
        # Compute MAX
        self.currdc_max  =max(meas_l)
        # Compute MEAN
        self.currdc_avrg = sum(meas_l)/len(meas_l)
        # Compute DEVIATION
        delta_meas_l=[]
        for idx in range(len(meas_l)):
            x = (meas_l[idx]-self.currdc_avrg)**(2)
            delta_meas_l.append(x)
        self.currdc_dev  =(sum(delta_meas_l)/(len(delta_meas_l)-1))**(0.5)

        # Apply conversion factor
        self.currdc_min=conv_factor*self.currdc_min
        self.currdc_max=conv_factor*self.currdc_max
        self.currdc_avrg=conv_factor*self.currdc_avrg
        

    def on(self):
        #logging.info("Turning ON DMM name =%s" % (self.name))
        #TODO
        logging.error("Turn ON not implemented yet " % (self.name))
        #self.dev.write("OUTP ON")
    
    def off(self):
        #logging.info("Turning OFF DMM name =%s" % (self.name))
        #TODO
        logging.error("Turn OFF not implemented yet " % (self.name))
        #self.dev.write("OUTP OFF")
   
    def close(self):
        logging.info("Closing DMM connection name = %s\n" % (self.name))
        self.dev.disconnect



#######################################################################################################################

if __name__ == '__main__':
    
    import math
    
    #from threading import Thread
    from cfg_multilogging import cfg_logger_root
        
    logger_00 = cfg_logger_root('DEBUG', 'dmm.LOG')  
    logger_00.debug('START')    
    dmm = DmmControl('34401a-0')
    Irange='MAX'
    Ires='DEF'    
    dmm.config('DC_I')
    dmm.read_config('DC_I')
    
    idx, MAX_ITER=0, 10
    while (idx < MAX_ITER):
        print "Reading measurements: iteration %s of %s" % ((idx+1), MAX_ITER )
#        (Imin, Imax, Iavrg, Idev)=dmm.meas_read('DC_I')
        (Imin, Imax, Iavrg, Idev)=dmm.meas_fetch('DC_I')
        idx = idx+1
#        logging.info("Imin=%s, Imax=%s, Iavrg=%s, Idev=%s)" % (Imin, Imax, Iavrg, Idev))
        logging.info("Imin=%s, Imax=%s, Iavrg=%s, Idev=%s)" % (dmm.currdc_min, dmm.currdc_max, dmm.currdc_avrg, dmm.currdc_dev))
    
    #logging.debug("FINAL READING: LEN=%s, READ=%s" %(len(dmm.currdc_buff), dmm.currdc_buff))
    #dmm.math_currdc()
    
#    logging.info("Imin=%s, Imax=%s, Iavrg=%s, Idev=%s)" % (dmm.currdc_min, dmm.currdc_max, dmm.currdc_avrg, dmm.currdc_dev))
#    Voltage_V = 3.8
#    Pmin_mW    = Voltage_V*abs(dmm.currdc_min)
#    Pmax_mW    = Voltage_V*abs(dmm.currdc_max)
#    Pavrg_mW   = Voltage_V*abs(dmm.currdc_avrg)
#
#    logging.info("Pmin=%s, Pmax=%s, Pavrg=%s, Deviation=%s)" % (Pmin_mW, Pmax_mW, Pavrg_mW, dmm.currdc_dev))
    dmm.close()

    logger_00.debug('END')    
    
