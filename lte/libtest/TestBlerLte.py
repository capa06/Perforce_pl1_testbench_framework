'''
Created on 25 Jul 2013

@author: fsaracino
'''

# ********************************************************************
# IMPORT SYSTEM MODULES
# ********************************************************************
import sys
import os
import time
import math
import logging
import re

from threading import Thread
from multiprocessing import Process, Lock

# ********************************************************************
# IMPORT USER DEFINED PATHS
# ********************************************************************
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-3])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'instr']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'com']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera']))


sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'txt']))

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'xls']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'mysql']))

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'instr']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'txt']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'mysql']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'xls']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'report', 'html']))





# ********************************************************************
# IMPORT USER DEFINED COMPONENTS
# ********************************************************************
from CfgError import CfgError
from StructXml import StructXml
from StructXmlTestBlerLte import StructXmlTestBlerLte  


from CmwLte import CmwLte
from PsuBench import PsuBench
from Scdu import scduOff, scduOn

from ComLib import ComLib

from os_utils import insertPause

from icera_utils import parseModemInfo, getBranch, getPlatform, getVariant

#from Struct import Struct
#from TableSnrLte import TableSnrLte
##from genie_utils import *


from CsvReportBlerLte import CsvReportBlerLte
from TxtReportConfig import TxtReportConfig
from HtmlReportLte import htmlReportLte


from DatabaseMySqlPl1Testbench import mySqlCheckPermission
from DatabaseMySqlPl1TestbenchLte import DatabaseMySqlPl1TestbenchLte, mysqlImportBlerResults, mysqlSelectBestScore



# ********************************************************************
# GLOBAL VARIABLES HERE
# ********************************************************************
# Dump file
#dumpfile="dump_%s" % time.strftime("%Y%m%d_%H%M%S", time.localtime())
#dumpfilename=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['results', 'current', dumpfile+'.log'])

# Database
#dflt_database=os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'sqllite', 'database', 'database_pl1testbench.db'])                                       


# ********************************************************************
# LOCAL FUNCTIONS
# ********************************************************************
def getThroughputTolerance(chtype):
    # Set the test tolerance to use
    if chtype is None:
        tolerance=0.03
    else:
        if chtype.upper()=='AWGN':
            tolerance=0.03
        else:
            tolerance=0.05
    return tolerance

def getThroughputMbpsThresholdOffset(chtype):
    # Set the test tolerance to use
    THR_OFFS_MBPS=1
    if chtype is None:
        thr_offs_Mbps=0
    else:
        if chtype.upper()=='AWGN':
            thr_offs_Mbps=THR_OFFS_MBPS
        else:
            thr_offs_Mbps=THR_OFFS_MBPS
    return thr_offs_Mbps


def getModemConfig(ca_enabled, carrier, rfband, earfcn, usimemu):
    logger=logging.getLogger('getModemConfig')
    at_cmd_l =[]
    if carrier.upper()=='PCC':
        at_cmd_l =[ r'at+cfun=0', 
                    r'at%%inwmode=1,E%s,%s' % ((rfband,1) if ca_enabled else (rfband,3)),
                    r'at%inwmode=0,E,1', 
                    r'at%%ilteearfcn=%s' % (earfcn),
                    r'at%%isimemu=%s' % (usimemu)]
    elif carrier.upper()=='SCC':
        at_cmd_l =[ r'at+cfun=0', 
                    r'at%%inwmode=1,E%s,3' % (rfband),
                    r'at%inwmode=0,E,1', 
                    r'at%%ilteearfcn=%s' % (earfcn),
                    r'at%%isimemu=%s' % (usimemu)]
    else:
        pass
    logger.debug("%s modem configuration : %s" % (carrier, at_cmd_l))
    return at_cmd_l
        
        

# ********************************************************************
# MAIN TEST FUNCTION
# ********************************************************************
def TestBlerLte(testconf_s, testunit_s): 
    logger            = logging.getLogger('TestBlerLTE')
    logger.info("Placeholder")
    
    # Local instances
    return_state      = None  
    tester_h          = None
    com_h             = None
    psu_h             = None
    
    
    testbler_s        = None
    meas_pwr_s        = None
     
    csvreport_h       = None
    txtreport_h       = None
    #table_snr_h       = None

    db_check_permission = None
    
    tester_info         = None
    modem_info          = None
    
    MEAS_WARMUP_SEC    = 5

    try:   
        
        # Initialise resources
        # ................................................................
        # Local variables
        return_state = 0
        prev_pcc_rfband = None
        prev_scc_rfband = None
        prev_pcc_earfcn = None
        prev_scc_earfcn = None
        

        # Testbler top level structure
        testbler_s=StructXmlTestBlerLte(testconf_s, testunit_s, struct_name='testbler_s') 
        #testbler_s.struct_log()
                
        # Measurement structures
        meas_xmlfile_template    = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','common', 'struct', 'template', 'structxml_csvreportbler_lte_template.xml'])  
        meas_pwr_s               = StructXml(xmlfile=meas_xmlfile_template, struct_name='meas_pwr_s',   node_name='meas_pwr')
                


        # Connect to the tester
        # ................................................................
        if re.match('[c|C][m|M][w|W500]', testconf_s.testername, re.I| re.M):
            logger.info("Selected tester : %s@%s" % (testconf_s.testername, testconf_s.testerip))
            xmlfile_cmw500_config = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'instr', 'structxml_cmw500_lte_config.xml'])    
            tester_h = CmwLte(name=testconf_s.testername, ip_addr=testconf_s.testerip, rat=testunit_s.common.rat.lower(), xmlfile_config=xmlfile_cmw500_config)
            insertPause(2)
            # Retrieve and check CMW firmware version
            tester_h.lte_cell_off()
            tester_h.preset()
            tester_info = tester_h.check_sw_version()
            logger.info("CMW INFO : %s" % tester_info)
                
        # Connect to PSU
        # ................................................................
        if testconf_s.psu or testconf_s.pwrmeas:
            logger.info("Selected PSU via WLAN gateway: %s, %s" % (testconf_s.psugwip, testconf_s.psugpib))
            psu_h=PsuBench(psu_gwip=testconf_s.psugwip, psu_gpib=testconf_s.psugpib, psu_reset=1)
            psu_h.off()
            psu_h.insert_pause(2)
            psu_h.on()
            logger.info("PSU bench is ON")
            insertPause(tsec=30)
        else:
            if testconf_s.scdu:
                scduOff(testconf_s.scdu_ip, testconf_s.scdu_uid, testconf_s.scdu_pwd, testconf_s.scdu_port)
                scduOn(testconf_s.scdu_ip, testconf_s.scdu_uid, testconf_s.scdu_pwd, testconf_s.scdu_port)
            elif testconf_s.reboot:
                logger.info("modem reboot")
                com_h = ComLib(testconf_s.ctrlif)
                com_h.modem.reboot()
                com_h= None
        
        
                                                      
        # Connect to the UE 
        # ................................................................

        logger.info("Selected UE control interface : %s" % testconf_s.ctrlif)
        com_h = ComLib(testconf_s.ctrlif)
        com_h.modem.modem_clear_crashinfo()
        modem_info = com_h.modem.modem_info()
        logger.info("modem info:\n%s" % modem_info)
        # Extract branch anf platform from modem_info
        if testconf_s.ctrlif in ['AT']:
            branch    = getBranch(modem_info)
            platform  = getPlatform(modem_info)
        else:
            branch    = None
            platform  = modem_info
        logger.info("---------------------------------------")
        logger.info("Extracted info branch   : %s" % branch)
        logger.info("Extracted info platform : %s" % platform)
        logger.info("---------------------------------------")
            
        # Initialise configuration and measurements report files
        # ................................................................
        # Set report dir
        report_dir          = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte','results', 'current'])
        
        # Save test configuration into a file
        report_fileconf_txt = os.path.join(report_dir, '%s_CMW500_TestConf_testID_%05d.txt' % (testunit_s.common.rat, testunit_s.common.testid))
        txtreport_h         = TxtReportConfig(report_fileconf_txt)
        txtreport_h.append_tlv('timestamp', time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
        txtreport_h.append_test_configuration(testunit_s)
        txtreport_h.append_tlv('modem_info', modem_info)
        txtreport_h.append_tlv('tester_info', tester_info)
        
        # Config and measurement reports
        report_filemeas_csv = os.path.join(report_dir, '%s_CMW500_TestMeas_testID_%05d.csv' % (testunit_s.common.rat, testunit_s.common.testid))
        csvreport_h         = CsvReportBlerLte(report_filemeas_csv,  pwrmeas=testconf_s.pwrmeas, statistics=1)
        csvreport_h.append_entry_header()
        
        # Check database access grants 
        # ................................................................
        if testconf_s.remoteDB:
            db_check_permission = mySqlCheckPermission(testconf_s.remoteDBhost, testconf_s.remoteDBname, testconf_s.remoteDBuid, testconf_s.remoteDBpwd)
            logger.info("Database access granted: %s" % (db_check_permission))
        
#        # Instantiate SNR table and set the SNR increase/decrease flag 
#        # ................................................................
#        table_snr_file_csv = os.path.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'], 'lte', 'libtest', 'table_snr.csv')
#        table_snr_h = TableSnrLte(table_snr_file_csv)
#        testunit_s.pcc.snr=sorted(testunit_s.pcc.snr, key=float, reverse=True)
#        if not testunit_s.scc is None:
#            testunit_s.scc.snr=sorted(testunit_s.scc.snr, key=float, reverse=True)
#        table_snr_h.set_snr_decrease()
            

        # Loop through all the LTE cell configurations
        # ................................................................
        # Scan teststeps 
        stepidx_iter=iter(range(1, testbler_s.totalsteps+1,1))
        for testbler_s.param_subtest_iter in testbler_s.param_subtest_iterator():
            for testbler_s.param_config_iter in testbler_s.param_config_iterator():

#                # TODO:(check) Reset event table
#                # ................................................................
#                table_snr_h.reset_events()
                
                #Set entry parameters for attach
                # ................................................................
                # Initialise test current test structure
                testbler_s.struct_teststep_init(param_subtest=1, param_config=1, param_sweep=1)
                # Update configurations parameters for attach
                testbler_s.struct_teststep_update(param_subtest=1, param_config=1, param_sweep=0)
                # Set default parameters for attach
                testbler_s.struct_teststep_update_defaults()
                
                #Debug
                logger.info("  -----------------------------------------------")
                logger.info("PREPARING FOR ATTACH PROCEDURE")
                logger.info("  -----------------------------------------------")
                # Show default parameters for attach                
                testbler_s.struct_teststep_log()
         
                # Turn OFF and configure UE
                # ................................................................
                com_h.modem.modem_off()
                ca_flag = (not testbler_s.teststep_s.scc is None)
                if ca_flag and (int(testbler_s.teststep_s.scc.rfband) != prev_scc_rfband):
                    at_cmd_l = getModemConfig(ca_flag, 'SCC', testbler_s.teststep_s.scc.rfband, testbler_s.teststep_s.scc.earfcn, testconf_s.usimemu)
                    com_h.modem.modem_config(at_cmd_l)
                    prev_scc_rfband=int(testbler_s.teststep_s.scc.rfband)
                if (int(testbler_s.teststep_s.pcc.rfband) != prev_pcc_rfband):
                    at_cmd_l = getModemConfig(ca_flag, 'PCC', testbler_s.teststep_s.pcc.rfband, testbler_s.teststep_s.pcc.earfcn, testconf_s.usimemu)
                    com_h.modem.modem_config(at_cmd_l)                    
                    prev_pcc_rfband=int(testbler_s.teststep_s.pcc.rfband)
                else:
                    pass
                                                          
                # Configure cell 
                # ................................................................
                tester_h.lte_config_init(testbler_s.teststep_s)
                        
                # Cell ON
                # ................................................................
                tester_h.lte_cell_on()
     
                # Read power levels
                # ----------------------------------------------------------------                        
                # TODO

                # MS attach and connect
                # ----------------------------------------------------------------
                com_h.modem.modem_on()
                

                if not tester_h.lte_dut_attach():
                    logger.error("ATTACH FAILURE. Skipping BLER measurements")
                    sys.exit(CfgError.ERRCODE_TEST_FAILURE_ATTACH)
    
                if not tester_h.lte_dut_connect():  
                    logger.error("CONNECT FAILURE. Skipping BLER measurements")
                    sys.exit(CfgError.ERRCODE_TEST_FAILURE_CEST)        

                # Reconfigure DL scheduler
                # ----------------------------------------------------------------
                tester_h.lte_config_scheduler(testbler_s.teststep_s)

                
                # Start tracking EARFCN 
                # ---------------------------------------------------------------------------                
                prev_pcc_earfcn = int(testbler_s.teststep_s.pcc.earfcn)
                if not testbler_s.teststep_s.scc is None:
                    prev_scc_earfcn = int(testbler_s.teststep_s.scc.earfcn)

     
                # Loop through SWEEP parameters
                # ----------------------------------------------------------------                                
                for testbler_s.param_sweep_iter in testbler_s.param_sweep_iterator():
                    logger.debug("  -----------------------------------------------")
                    logger.debug("  MEASUREMENT PROCEDURE: iteration %s of %s" % (stepidx_iter.next(), testbler_s.totalsteps))
                    logger.debug("  -----------------------------------------------")

#                    # TODO:(check) stop condition
#                    # ---------------------------------------------------------------------------                                        
#                    if table_snr_h.stop_condition():
#                        logger.debug("Triggered STOP event, measurement skipped")
#                        continue
                    
                    testbler_s.struct_teststep_update(param_subtest=0, param_config=0, param_sweep=1)
                    testbler_s.struct_teststep_log()
                    
                    # Update tester configuration
                    # ---------------------------------------------------------------------------                    
                    # Execute intra-HHO if the EARFCN is changed 
                    if (int(testbler_s.teststep_s.pcc.earfcn) != prev_pcc_earfcn):
                        logger.info("Starting intraHHO on PCC EARFCN(start)= %s --> EARFCN(end)= %s" % (prev_pcc_earfcn, int(testbler_s.teststep_s.pcc.earfcn)))
                        tester_h.lte_config_earfcn('PCC', int(testbler_s.teststep_s.pcc.earfcn))
                        if tester_h.read_state()!='CEST':
                            logger.error('ATTACH FAILURE during PCC INTRA-HHO')          
                            sys.exit(CfgError.ERRCODE_TEST_FAILURE_INTRAHO)
                        logger.info("PCC IntraHHO SUCCESSFULL")
                        prev_pcc_earfcn=int(testbler_s.teststep_s.pcc.earfcn)

                    if not testbler_s.teststep_s.scc is None:
                        if (int(testbler_s.teststep_s.scc.earfcn) != prev_scc_earfcn):
                            logger.info("Starting intraHHO on SCC EARFCN(start)= %s --> EARFCN(end)= %s" % (prev_scc_earfcn, int(testbler_s.teststep_s.scc.earfcn)))
                            tester_h.lte_config_earfcn('SCC', int(testbler_s.teststep_s.scc.earfcn))                        
                            if tester_h.read_state()!='CEST':
                                logger.error('ATTACH FAILURE during PCC INTRA-HHO')          
                                sys.exit(CfgError.ERRCODE_TEST_FAILURE_INTRAHO)
                            logger.info("SCC IntraHHO SUCCESSFULL")
                            prev_scc_earfcn=int(testbler_s.teststep_s.scc.earfcn)
                    
                    tester_h.lte_config_rsepre(testbler_s.teststep_s)
                    tester_h.lte_config_doppler(testbler_s.teststep_s)
                    tester_h.lte_config_snr(testbler_s.teststep_s)
                    tester_h.lte_update_scheduler(testbler_s.teststep_s)
                    tester_h.checkpoint()
                         
                    # Read power levels
                    # ----------------------------------------------------------------
                    
#                    # TODO: check skip measurement trigger
#                    # ---------------------------------------------------------------------------
#                    table_snr_h.reset_event_skip()                                       
#                    carrier_l = ['PCC', 'SCC'] if (not testbler_s.teststep_s.scc is None) else ['PCC']
#                    for carrier in carrier_l:
#                        table_snr_h.detect_skip_condition(eval("testbler_s.teststep_s.%s.chtype" % carrier.lower()),
#                                                          eval("testbler_s.teststep_s.%s.tm" % carrier.lower()),
#                                                          eval("testbler_s.teststep_s.%s.txants" % carrier.lower()),
#                                                          eval("testbler_s.teststep_s.%s.nhrtx" % carrier.lower()),
#                                                          eval("testbler_s.teststep_s.%s.dlmcs" % carrier.lower()),
#                                                          carrier.lower(),
#                                                          eval("testbler_s.teststep_s.%s.snr" % carrier.lower()))
#                        
#                    
#                    if table_snr_h.skip_event:
#                        logger.debug("Triggered SKIP event, measurement skipped")
#                        continue
                        
                    try:
                        # COLLECT MEASUREMENTS
                        # ----------------------------------------------------------------                            
                        meas_done = 0
                        carrier_l = ['PCC', 'SCC'] if (not testbler_s.teststep_s.scc is None) else ['PCC']
                        for carrier in carrier_l:
                            if eval(" not testbler_s.teststep_s.%s is None" % carrier.lower()):
                                csvreport_h.report_update_params(eval("testbler_s.teststep_s.%s" % carrier.lower()), carrier)
            
                                # <Retrieve tester measurements>
                                if not  meas_done:
                                   
                                    if testconf_s.pwrmeas:
                                        logger.debug("Starting thread for power measurements")
                                        thr_pwr=Thread(target=psu_h.read)
                                        thr_pwr.daemon = True 
                                        thr_pwr.start()    

                                    # Allow testster to get ready for measurements
                                    insertPause(MEAS_WARMUP_SEC)
                                                                        
                                    # The measurements in all the carriers are collected in once shot   
                                    tester_h.lte_meas_bler_fetch(testbler_s.teststep_s)
                                    meas_done = 1

                                    if testconf_s.pwrmeas:
                                        thr_pwr.join()
                                        logger.info("PWR MEAS: voltage=%s[V], current = %s[mA]" % (psu_h.voltage_V, psu_h.current_mA))
                                        csvreport_h.report_update_meas_pwr(psu_h.voltage_V, psu_h.current_mA)
                                        
                                csvreport_h.report_update_meas_bler(eval("tester_h.meas_dlbler_s.%s" % carrier.lower()), eval("tester_h.meas_ulbler_s.%s" % carrier.lower()))
                                csvreport_h.report_update_meas_dlthr(eval("tester_h.meas_dlthr_s.%s" % carrier.lower()))
                                csvreport_h.report_update_meas_rank(eval("tester_h.meas_rank_s.%s" % carrier.lower()))
                                csvreport_h.report_update_meas_cqi(eval("tester_h.meas_cqi_s.%s" % carrier.lower()))
                                csvreport_h.report_update_meas_pmi(eval("tester_h.meas_pmi_s.%s" % carrier.lower()))
                                csvreport_h.report_update_meas_harq(eval("tester_h.meas_harq_s.%s" % carrier.lower()))
                         
#                                # TODO: Table SNR update (CQI scheduler?)
#                                # --------------------------------------------------------------------------- 
#
#                                table_snr_h.update(table_snr_h.build_key(eval("testbler_s.teststep_s.%s.chtype" % carrier.lower()), 
#                                                                         eval("testbler_s.teststep_s.%s.tm" % carrier.lower()), 
#                                                                         eval("testbler_s.teststep_s.%s.txants" % carrier.lower()),
#                                                                         eval("testbler_s.teststep_s.%s.nhrtx" % carrier.lower()),
#                                                                         eval("testbler_s.teststep_s.%s.dlmcs" % carrier.lower()),
#                                                                         carrier), 
#                                                                         csvreport_h.entry_header_s.params.snr, 
#                                                                         float(csvreport_h.entry_header_s.meas_bler.dlbler))

                                # Retrieve best score from database
                                # ---------------------------------------------------------------------------
                                if testconf_s.remoteDB and (db_check_permission in ["READ_ONLY", "READ_WRITE"]):
                                    dlbestscore_clnum, dlbestscore_thr_Mbps = mysqlSelectBestScore(testconf_s.remoteDBhost,
                                                                                                   testconf_s.remoteDBname,
                                                                                                   testconf_s.remoteDBuid,
                                                                                                   testconf_s.remoteDBpwd,
                                                                                                   testbler_s.teststep_s, 
                                                                                                   branch, 
                                                                                                   platform, 
                                                                                                   carrier, 
                                                                                                   'dlthr_Mbps')
                                    
                                    logger.info("%s DL BESTSCORE: clnum=%s, ulthr_Mbps=%s" % (carrier, dlbestscore_clnum, dlbestscore_thr_Mbps))

                                    if carrier=='PCC':
                                        ulbestscore_clnum, ulbestscore_thr_Mbps = mysqlSelectBestScore(testconf_s.remoteDBhost,
                                                                                                       testconf_s.remoteDBname,
                                                                                                       testconf_s.remoteDBuid,
                                                                                                       testconf_s.remoteDBpwd,
                                                                                                       testbler_s.teststep_s, 
                                                                                                       branch, 
                                                                                                       platform, 
                                                                                                       carrier, 
                                                                                                       'ulthr_Mbps')
                                        logger.info("%s UL BESTSCORE: clnum=%s, ulthr_Mbps=%s" % (carrier, ulbestscore_clnum, ulbestscore_thr_Mbps))

                                else:
                                    dlbestscore_thr_Mbps = None
                                    ulbestscore_thr_Mbps = None
                                                        
                                # Build verdict
                                # ---------------------------------------------------------------------------
                                tolerance  = getThroughputTolerance(eval("testbler_s.teststep_s.%s.chtype" % carrier.lower()))
                                offset     = getThroughputMbpsThresholdOffset(eval("testbler_s.teststep_s.%s.chtype" % carrier.lower()))
                                csvreport_h.struct_verdict_init()
                                csvreport_h.report_update_verdict_dl(dlbestscore_thr_Mbps, tolerance, offset)
                                if carrier=='PCC':
                                    csvreport_h.report_update_verdict_ul(ulbestscore_thr_Mbps, tolerance, offset)
                                    
                                # Update overall result
                                # ---------------------------------------------------------------------------
                                verdict = csvreport_h.get_verdict_dl()
                                if (not verdict is None):
                                    if ('FAIL' in verdict):
                                        return_state = CfgError.ERRCODE_TEST_FAILURE_REFTHR
                                    elif ('INCONCLUSIVE' in verdict):
                                        return_state = CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE if (not return_state) else return_state
                                verdict = csvreport_h.get_verdict_ul()
                                if (not verdict is None):
                                    if ('FAIL' in verdict):
                                        return_state = CfgError.ERRCODE_TEST_FAILURE_REFTHR
                                    elif ('INCONCLUSIVE' in verdict):
                                        return_state = CfgError.ERRCODE_TEST_FAILURE_INCONCLUSIVE if (not return_state) else return_state
                                 
                                if 1: csvreport_h.report_log()

                                csvreport_h.report_append_entry()
                                                                        
                    except SystemExit:
                        
                        exc_info = sys.exc_info()
                        return_state=int('%s' % exc_info[1])
                        if return_state==CfgError.ERRCODE_SYS_CMW_INVMEAS:
                            logger.warning("-------------------------------------------------------")                        
                            logger.warning("CMW500_INVALID_MEASUREMENTS. Skipping to next iteration")
                            logger.warning("-------------------------------------------------------")                                                
                            tester_h.reset()
                            tester_h.lte_cell_off()
                            break
                        elif return_state==CfgError.ERRCODE_SYS_CMW_TIMEOUT:
                            logger.warning("-------------------------------------------------------------")                        
                            logger.warning("CMW500 NOT PRODUCING MEASUREMENTS. Skipping to next iteration")
                            logger.warning("-------------------------------------------------------------")                                                
                            tester_h.reset()
                            tester_h.lte_cell_off()
                            break
                        else:
                            sys.exit(return_state)

                # Disconnect and turn OFF the UE
                # ................................................................
                tester_h.lte_dut_detach()
                com_h.modem.modem_off()

    
                # Cell OFF
                # ................................................................
                tester_h.lte_cell_off()
        
        
        # Convert reports
        # ................................................................
        htmlReportLte(report_fileconf_txt, report_filemeas_csv)

                                         
    except SystemExit:
        exc_info = sys.exc_info()
        return_state=int('%s' % exc_info[1])
    
    # Save table SNR
#    if  not table_snr_h is None:
#        table_snr_h.save()
    
    # Update database 
    if testconf_s.remoteDB and (db_check_permission in ["READ_WRITE"]):
        logger.info("Updating database")
        mysqlImportBlerResults(testconf_s.remoteDBhost,
                               testconf_s.remoteDBname,
                               testconf_s.remoteDBuid,
                               testconf_s.remoteDBpwd,
                               report_fileconf_txt, 
                               report_filemeas_csv)

    # Close connections
    logger.info("Closing communication objects")    
    if not com_h is None:
        com_h.modem.close()

    if not tester_h is None:
        tester_h.lte_cell_off()        
        tester_h.gotolocal()
        tester_h.close()

    if not psu_h is None:
        psu_h.off() 
        psu_h.close()

    return return_state

if __name__ == '__main__':
    pass
