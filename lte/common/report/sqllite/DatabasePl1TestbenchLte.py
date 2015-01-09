'''
Created on 28 Nov 2013

@author: jlucas, fsaracino
'''

import os, sys, logging, time, sqlite3, re

# =============================================================================
# DEFINE LOCAL PATHS 
# =============================================================================
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-5])
    #print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))


 
# =============================================================================
# IMPORT USER DEFINED LIBRARY 
# =============================================================================
from DatabasePl1Testbench import DatabasePl1Testbench
from CfgError import CfgError
from icera_utils import parseModemInfo, getBranch, getPlatform, getVariant

# =============================================================================
# GLOBAL VARIABLES 
# =============================================================================


# =============================================================================
# GLOBAL FUNCTIONS 
# =============================================================================
def csvParseMeasLte(fname, key_l):
    """
    Description:
     
      filter CSV result file applying the rules defined in key_l, where key_l is a list of the keywords to select from the measurement sheet
    
    Input parameters:
        fname     : csv filename  
        key_l     : key filters to select columns from the table stored into file
    
    Output:
      the function returns two dictionary structures [config_dict, entry_dict]
      
      config_dict contains the info related to the test environment
       
      config_dict := {'timestamp':<value>, 'branch':<value>, 'variant':<value>, 'clnum':<value>, 'mod_files':<value>, 'platform':<value>}
    
      entry_dict  := { 'key0' : [x(1,1), x(1,2),...,x(1,N)],
                       'key1' : [x(2,1), x(2,2),...,x(2,N)],
                                       ...
                       'keyM' : [x(M,1), x(M,2),...,x(M,N)]}    
    """
    logger=logging.getLogger('csvParseMeasLte')

    # Initialise result structures 
    config_dict = {'timestamp':'None', 
                   'platform' :'None',
                   'testtype' :'None',                    
                   'branch'   :'None', 
                   'clnum'    :'None', 
                   'mod_files':'None', 
                   'p4webrev' :'None', 
                   'testid'   :'None', 
                   'descr'    :'None', 
                   'cmwinfo'  :'None', 
                   'modeminfo':'None'}
    
    entry_dict  = {}
    for key in range(len(key_l)): entry_dict[key_l[key]]=[]
    
    # Define rules for retrieving the configuration
    timestamp_re = re.compile(r".*date.*,\s*(\S*\s*\S*).*$")
    platform_re  = re.compile(r".*Platform\s*:\s*(.*?)\s")
    #variant_re   = re.compile(r".*Variant\s*:\s*(\S*).*$")
    testtype_re   = re.compile(r".*testtype\s*,\s*(\S*)\s*.*$")    
    
    branch_re    = re.compile(r".*Branch name\s*:\s*(\S*).*$")
    clnum_re     = re.compile(r".*Changelist\s+:\s*CL(\d+)")
    mod_files_re = re.compile(r".*Number of modified files\s+:\s(\d+)")
    p4webrev_re  = re.compile(r".*P4webrev\s*:\s*(\S*)\s*")
    
    testid_re    = re.compile(r".*test_ID.*,\s*(\d+).*$")
    descr_re     = re.compile(r".*descr\s*,\s*(.*?)\n")
    cmwinfo_re   = re.compile(r".*cmwinfo\s*,\s*\[(.*?)\]")
    modeminfo_re = re.compile(r".*modeminfo\s*,\s*(.*?)\n")

    # Check file existence
    if not os.path.isfile(fname):
        logger.error("FILE NOT FOUND: %s" % fname)
        sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
        
    # Open file
    with open(fname, 'r') as fd:    

        state=0             # INIT=0,  STATES: { 0: looking for entry header,  1:reading entries } 
        
        while True:
            
            line=fd.readline() 
            
            # Break on EOF
            if line == "" : break

            # Convert CSV line into list and remove any space within the items
            line_l=[x.strip() for x in line.split(',')]

            if state==0:   
                # Still looking for the ENTRY HEADER. Seacrh for CONFIG info
                #line = line.replace('\n','')
                if branch_re.search(line):
                    res=branch_re.findall(line)
                    if (res[0][0:3] == "css"):
                        config_dict['branch']=parseModemInfo(res[0])
                    else:
                        config_dict['branch']=res[0]    
                    logger.debug("FOUND branch: %s" % config_dict['branch'])                    
                if testtype_re.search(line):
                    res=testtype_re.findall(line)
                    logger.debug("FOUND testtype: %s" % res[0])
                    config_dict['testtype']=res[0]
                if descr_re.search(line):
                    res=descr_re.findall(line)
                    logger.debug("FOUND descr: %s" % res[0])
                    config_dict['descr']=res[0]
                if cmwinfo_re.search(line):
                    res=cmwinfo_re.findall(line)
                    logger.debug("FOUND cmwinfo: %s" % res[0])
                    config_dict['cmwinfo']=res[0]
                if modeminfo_re.search(line):
                    res=modeminfo_re.findall(line)
                    config_dict['modeminfo']=re.sub('[\n\r]+', ' ', res[0])
                    logger.debug("FOUND modeminfo: %s" % config_dict['modeminfo'])
                if clnum_re.search(line):
                    res=clnum_re.findall(line)
                    logger.debug("FOUND clnum: %s" % res[0])
                    config_dict['clnum']=res[0]
                if platform_re.search(line):
                    res=platform_re.findall(line)
                    logger.debug("FOUND platform: %s" % res[0])
                    config_dict['platform']=res[0]
                if mod_files_re.search(line):
                    res=mod_files_re.findall(line)
                    logger.debug("FOUND mod_files: %s" % res[0])
                    config_dict['mod_files']=res[0]
                if p4webrev_re.search(line):
                    res=p4webrev_re.findall(line)
                    logger.debug("FOUND p4webrev: %s" % res[0])
                    config_dict['p4webrev']=res[0]
                if timestamp_re.search(line):
                    res=timestamp_re.findall(line)
                    logger.debug("FOUND timestamp: %s" % res[0])
                    config_dict['timestamp']=res[0]
                if testid_re.search(line):
                    res=testid_re.findall(line)
                    logger.debug("FOUND testid: %s" % res[0])
                    config_dict['testid']=res[0]

                # Check if header entry
                if (line_l[0].strip()).upper() == 'TESTID':                
     
                    # Check if any invalid KEY 
                    key_invalid_l = filter( lambda x: x not in line_l, key_l)
                    key_valid_l   = [x for x in key_l if x not in key_invalid_l] 
                    
                    logger.debug("INVALID KEY LIST : %s" % key_invalid_l) 
                    logger.debug("VALID KEY LIST   : %s" % key_valid_l) 

                    # Retrieve the column index
                    colidx_l = [line_l.index(x) for x in key_valid_l]
                    z=zip(key_valid_l, colidx_l)
                    if 0:
                        for i in range(len(z)): 
                            logger.debug("key '%s' mapped on column %s" % (z[i][0], z[i][1]))
                        
                    # Switch state
                    state=1                    
                    continue
                
            # Append entry values into the entry dictionary 
            if state==1: 
                for i in range(len(z)):
                    entry_dict[z[i][0]].append(line_l[z[i][1]])
            
     
    return (config_dict, entry_dict) 


# =============================================================================
# DATABASE API FUNCTIONS 
# =============================================================================
def databaseImportLte(dbname, filename):
    
    from CsvReportBler import bler_params, bler_meas, prev_meas, thr_verdict, pwr_meas
    
    logger=logging.getLogger('databaseImportLte')
    logger.info("Import LTE test measurements from file : %s" % filename)
    
    # Get database connection object instance
    db_h=DatabasePl1TestbenchLte(dbname)
    
    # Open database connection                                                
    db_h.connect()
           
    keywords_l = bler_params + bler_meas + prev_meas + thr_verdict + pwr_meas
    
    table_config, table_entry=csvParseMeasLte(fname=filename, key_l=keywords_l)
        
    # Debug
    if 0:
        logger.debug(">>> TEST CONFIG:")
        for k,v in table_config.iteritems(): 
            logger.debug("table_config[%s] = %s" % (k, v))
    if 0:
        logger.debug(">>> TEST RESULTS:")            
        for k,v in table_entry.iteritems(): 
            logger.debug("table_entry[%s] = %s" % (k, v))   
           
    # Add platform
    platform_id=db_h.add_platform(table_config['platform'])
    logger.debug("SELECTED: platform_id:%s, platform:%s" % (platform_id, table_config['platform']))
    
    # Add test info
    testinfo_id=db_h.add_testinfo(testid=table_config['testid'], testtype=table_config['testtype'], descr=table_config['descr'])
    logger.debug("SELECTED: testinfo_id:%s, testid:%s, testtype:%s, descr:%s" % (testinfo_id, table_config['testid'], table_config['testtype'], table_config['descr']))
    
    # Add test_run
    testrun_id=db_h.add_testrun(timestamp=table_config['timestamp'], branch=table_config['branch'], clnum=table_config['clnum'], mod_files=table_config['mod_files'], p4webrev='None', cmwinfo=table_config['cmwinfo'], modeminfo=table_config['modeminfo'])
    #testrun_id=db_h.add_testrun(timestamp=table_config['timestamp'], branch=table_config['branch'], clnum=table_config['clnum'], mod_files=table_config['mod_files'], p4webrev='None', cmwinfo=table_config['cmwinfo'], modeminfo='None')
    logger.debug("SELECTED: testrun_id:%s, timestamp=%s, branch:%s, clnum:%s, mod_files:%s, p4webrev:%s, cmwinfo:%s, modeminfo=%s" % (testrun_id, table_config['timestamp'], table_config['branch'], table_config['clnum'], table_config['mod_files'], table_config['p4webrev'], table_config['cmwinfo'], 'None'))
    
    # Add param_set and results
    total_entries=len(table_entry[keywords_l[0]])
    for idx in range(total_entries):
        carrier  = table_entry['CARRIER'][idx]
        dmode    = table_entry['DMODE'][idx]   
        dlulconf  = int(table_entry['DLULCONF'][idx]) if table_entry['DLULCONF'][idx]!='None' else -1
        ssconf    = int(table_entry['SSCONF'][idx]) if table_entry['SSCONF'][idx]!='None' else -1
        bwmhz     = float(table_entry['BW[Mhz]'][idx])
        rfband    = int(table_entry['RFBAND'][idx])
        earfcn    = int(float(table_entry['EARFCN'][idx]))
        cp        = table_entry['CP'][idx]
        tm        = int(table_entry['TM'][idx])
        txants    = int(table_entry['TXANTS'][idx])
        pmi       = int(table_entry['PMI'][idx])
        rsepre    = float(table_entry['RSEPRE'][idx])
        pa        = int(table_entry['PA[dB]'][idx])
        pb        = int(table_entry['PB'][idx])
        chtype    = table_entry['CHTYPE'][idx]
        snr       = float(table_entry['SNR[dB]'][idx])
        doppler   = float(table_entry['DOPPLER[Hz]'][idx]) 
        schedtype = 'AMC' if table_entry['SCHEDTYPE'][idx]=='CQI' else 'FIXED'
        dlmcs     = int(table_entry['DLMCS'][idx])
        dlnprb    = int(table_entry['DLNPRB'][idx])
        dlrbstart = int(table_entry['DLRBSTART'][idx])
        ulmcs     = int(table_entry['ULMCS'][idx])
        ulnprb    = int(table_entry['ULNPRB'][idx])
        ulrbstart = int(table_entry['ULRBSTART'][idx])
            
        # Add param set
        param_id=db_h.add_param_set_lte(testinfo_id, (idx+1), carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)
        logger.debug("SELECTED: param_id:%d, %s",param_id, (testinfo_id, (idx+1), carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
                
        # Add results
        valid        = 1
        dlrely       = int(table_entry['DLRELY'][idx])
        dlthr        = float(table_entry['DLTHR[Mbps]'][idx])
        dlbler       = float(table_entry['DLBLER'][idx])
        cqi          = int(table_entry['CQI'][idx])
        ack          = int(table_entry['ACK'][idx])
        nack         = int(table_entry['NACK'][idx])
        dtx          = int(table_entry['DTX'][idx])
        sf_total     = int(table_entry['NSF'][idx])
        sf_scheduled = int(table_entry['SCHED'][idx])
        ulrely       = int(table_entry['ULRELY'][idx])
        ulthr        = float(table_entry['ULTHR[Mbps]'][idx])
        ulbler       = float(table_entry['ULBLER'][idx])
        crc_pass     = int(table_entry['CRC PASS'][idx])
        crc_fail     = int(table_entry['CRC FAIL'][idx])
        best_dlthr   = float(table_entry['BEST DLTHR[Mbps]'][idx])
        best_ulthr   = float(table_entry['BEST ULTHR[Mbps]'][idx])
        tolerance    = table_entry['TOLERANCE'][idx]
        verdict_dl   = table_entry['DL VERDICT'][idx]
        verdict_ul   = table_entry['UL VERDICT'][idx]
        try:
            current_mA   = float(table_entry['Iavrg[mA]'][idx])
        except:
            current_mA   = float(0)
        try:
            pwr3p8V_mW   = float(table_entry['PWRavrg[mW]@3.8V'][idx])
        except:
            pwr3p8V_mW   = float(0)
                                           
        result_id=db_h.add_result_set_lte(testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, best_dlthr, best_ulthr, tolerance, verdict_dl, verdict_ul, current_mA, pwr3p8V_mW)
        logger.debug("SELECTED: result_id:%d, %s",result_id, (testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, best_dlthr, best_ulthr, tolerance, verdict_dl, verdict_ul, current_mA, pwr3p8V_mW))
    
    # Commit data
    db_h.conn.commit()
        
    # Close database connection                                                
    db_h.disconnect()

    del db_h
    return 0


def databaseExportLte(dbname, filename):
    logger=logging.getLogger('databaseExportLte')
    
    res = 0
     
    # Check database
    if not os.path.isfile(dbname):
        logger.warning("database %s not found. Export ABORTED" % dbname)
        return -1
    
    # Clean data from any previous test
    if os.path.isfile(filename):
        os.remove(filename)
    
    # Create destination folder, if does not exists
    fpath=os.path.split(filename)[0]
    if not os.path.exists(fpath): 
        os.makedirs(fpath)
        logger.debug("Created destination folder: %s" % fpath)

    EQUERY_DATABASE=re.sub('[ |\t|\n]+',' ', r"""SELECT * FROM results
                INNER JOIN platforms ON results.platform_id=platforms.platform_id 
                INNER JOIN testruns ON results.testrun_id=testruns.testrun_id
                INNER JOIN params ON results.param_id=params.param_id 
                INNER JOIN testinfos ON params.testinfo_id=testinfos.testinfo_id;""")
        
    # Get database connection object instance
    db_h=DatabasePl1TestbenchLte(dbname)
    
    # Open database connection                                                
    db_h.connect()
    
    try:
        db_h.cursor.execute(EQUERY_DATABASE)
    
        # Extract header from cursor description
        query_header_l=[]
        if 0: print db_h.cursor.description
        for column in db_h.cursor.description:
            query_header_l.append(column[0])   
        logger.debug("QUERY HEADER : %s" % query_header_l)
        
        # Configure query line format 
        query_out_format='%s, '*(len(query_header_l)-1)+'%s\n'
        
        if db_h.cursor:
            with open(filename,'a') as fd:
                fd.write(query_out_format % tuple(query_header_l))
                for query_out in db_h.cursor:
                    fd.write(query_out_format % tuple(query_out))
            fd.close()
        else:
            logger.debug("export_to_csv(), no entry found in database %s" % filename)
    except TypeError:
        logger.error("export_to_csv(), SELECT failure")
        print sys.exc_info()
        res=-1
    except IOError:
        logger.error("ERROR: opening file %s" % filename)
        print sys.exc_info()
        res=-1
    else:
        logger.info("Data exported into file %s" % filename)
    
    # Close database connection                                                
    db_h.disconnect()

    del db_h    
    return res


def databaseSelectBestScoreLte(dbname, equery):
    logger=logging.getLogger('databaseSelectBestScoreLte')
    
    res= (None, None, None)
    
    # Get database connection object instance
    db_h=DatabasePl1TestbenchLte(dbname)
    
    # Open database connection                                                
    db_h.connect()
 
    try:
        if 0: print equery   
        db_h.cursor.execute(equery)
        if db_h.cursor:
            for result in db_h.cursor:
                branch = result[0]
                clnum  = result[1]
                dlthr  = result[2]
                res=(branch, clnum, dlthr)            
        else:
            logger.debug("DB_export_bestscore(), no entry found in database %s" % dbname)
    except TypeError:
        logger.error("DB_export_bestscore(), SELECT failure")
        return (None, None, None)
    else:
        logger.debug("DB_export_bestscore() completed")
        # Close database connection                                                
        db_h.disconnect()

    return res 


def databaseExportBestScoreLte(dbname, test_s, carrier, varname):
    """
    Input:
       dbname     : database name
       test_s     : test configuration structure
       carrier    : {'PCC', 'SCC'}
       varname    : {'dlthr', 'ulthr'}
    Output:
       (branch, clnum, score)
    """
    logger=logging.getLogger('databaseExportBestScoreLte')
    
    carrier=carrier.upper()
    varname= varname.lower()
    
    if not carrier in ['PCC', 'SCC']:
        logger.error("INVALID PARAMENTER: carrier %s" % carrier)
        sys.exit(CfgError.ERRCODE_SYS_PARAM_INVALID)
    if not varname in ['dlthr', 'ulthr']:
        logger.error("INVALID PARAMENTER: carrier %s" % carrier)
        sys.exit(CfgError.ERRCODE_SYS_PARAM_INVALID)
         
    # Configure query to extract the best score
    branch    = getBranch(test_s.modeminfo)
    platform  = getPlatform(test_s.modeminfo)

    equery=re.sub('[ |\t|\n]+',' ', r"""SELECT branch,clnum,MAX(%s) FROM lte_results
        INNER JOIN platforms ON lte_results.platform_id=platforms.platform_id 
        INNER JOIN testruns ON lte_results.testrun_id=testruns.testrun_id
        INNER JOIN lte_params ON lte_results.param_id=lte_params.param_id 
        INNER JOIN testinfos ON lte_params.testinfo_id=testinfos.testinfo_id
        WHERE branch=='%s' 
            AND platform=='%s'                        
            AND carrier== '%s' 
            AND dmode=='%s' 
            AND dlulconf==%s
            AND ssconf==%s
            AND bwmhz==%s
            AND rfband==%s
            AND earfcn==%s
            AND cp=='%s'
            AND tm==%s
            AND txants==%s
            AND pmi==%s
            AND rsepre==%s
            AND pa==%s
            AND pb==%s            
            AND chtype=='%s'
            AND snr==%s
            AND doppler=%s
            AND schedtype=='%s'
            AND dlmcs==%s
            AND dlnprb==%s
            AND dlrbstart==%s
            AND ulmcs==%s
            AND ulnprb==%s
            AND ulrbstart==%s;""" % (varname, 
                                     branch, 
                                     platform, 
                                     carrier, 
                                     eval("test_s.param_subtest_iter.%s.dmode" % carrier.lower()), 
                                     eval("test_s.param_subtest_iter.%s.dlulconf" % carrier.lower()) if not eval("test_s.param_subtest_iter.%s.dlulconf" % carrier.lower()) is None else -1, 
                                     eval("test_s.param_subtest_iter.%s.ssconf" % carrier.lower()) if not eval("test_s.param_subtest_iter.%s.ssconf" % carrier.lower()) is None else -1, 
                                     eval("test_s.param_subtest_iter.%s.bwmhz" % carrier.lower()), 
                                     eval("test_s.param_subtest_iter.%s.rfband" % carrier.lower()), 
                                     eval("test_s.param_sweep_iter.%s.earfcn" % carrier.lower()), 
                                     eval("test_s.param_subtest_iter.%s.cp" % carrier.lower()), 
                                     eval("test_s.param_config_iter.%s.tm" % carrier.lower()), 
                                     eval("test_s.param_config_iter.%s.txants" % carrier.lower()), 
                                     eval("test_s.param_config_iter.%s.pmi" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.rsepre" % carrier.lower()),
                                     eval("test_s.param_config_iter.%s.pa" % carrier.lower()),
                                     eval("test_s.param_config_iter.%s.pb" % carrier.lower()),
                                     eval("test_s.param_subtest_iter.%s.chtype" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.snr" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.doppler" % carrier.lower()),
                                     'AMC' if eval("test_s.%s.schedtype" % carrier.lower())=='CQI' else 'FIXED', 
                                     eval("test_s.param_sweep_iter.%s.dlmcs" % carrier.lower()), 
                                     eval("test_s.param_sweep_iter.%s.dlnprb" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.dlrbstart" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.ulmcs" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.ulnprb" % carrier.lower()),
                                     eval("test_s.param_sweep_iter.%s.ulrbstart" % carrier.lower())))
                                    
    logger.debug("EQUERY : %s" % equery)
    (branch, clnum, score) = databaseSelectBestScoreLte(dbname, equery)
    logger.debug("BESTSCORE %s %s  : branch: %s, clnum=%s, %s[Mbps]=%s" % (carrier, varname.upper(), branch, clnum, varname, score))
    
    return (branch, clnum, score)  


# =============================================================================
# DATABASE STRUCTURE FOR LTE PERFORMANCE MEASUREMENTS 
# =============================================================================
class DatabasePl1TestbenchLte(DatabasePl1Testbench):
    
    def __init__ (self, name):
        DatabasePl1Testbench.__init__(self, name)

    def get_param_id_lte(self, testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart):
        logger=logging.getLogger('get_param_id_lte')
        self.cursor.execute("""SELECT param_id FROM lte_params WHERE testinfo_id=? AND teststep=? AND carrier=?  AND dmode=?     AND dlulconf=? 
                                                               AND ssconf=?      AND bwmhz=?    AND rfband=?    AND earfcn=? 
                                                               AND cp=?          AND tm=?       AND txants=?    AND pmi=? 
                                                               AND rsepre=?      AND pa=?       AND pb=?        AND chtype=? 
                                                               AND snr=?        AND doppler=?   AND schedtype=? AND dlmcs=? 
                                                               AND dlnprb=?     AND dlrbstart=? AND ulmcs=?     AND ulnprb=? 
                                                               AND ulrbstart=?""", (testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
        result=self.cursor.fetchone()[0]
        logger.debug("Param set %s has ID %d",(testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart), result)
        return result

    def add_param_set_lte(self, testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart):
        logger=logging.getLogger('add_param_set_lte')
        try:
            return self.get_param_id_lte(testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)
        except TypeError:
            logger.debug("Creating record for lte_param set %s",(testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
            self.cursor.execute("INSERT INTO lte_params(testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
            return self.get_param_id_lte(testinfo_id, teststep, carrier, dmode, dlulconf, ssconf, bwmhz, rfband, earfcn, cp, tm, txants, pmi, rsepre, pa, pb, chtype, snr, doppler, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)


    def get_result_id_lte(self, testrun_id, platform_id, param_id):
        logger=logging.getLogger('get_result_id_lte')
        self.cursor.execute("SELECT result_id FROM lte_results WHERE testrun_id=? AND platform_id=? AND param_id=?",
                                                   (testrun_id,platform_id,param_id))
        result=self.cursor.fetchone()[0]
        logger.debug("Result for testrun_id %d, platform_id %d, param_id %d has ID %d", testrun_id, platform_id, param_id, result)
        return result


    def add_result_set_lte(self, testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, best_dlthr, best_ulthr, tolerance, verdict_dl, verdict_ul, current_mA, pwr3p8V_mW):
        logger=logging.getLogger('add_result_set_lte')
        try:
            return self.get_result_id_lte(testrun_id,platform_id,param_id)
        except TypeError:
            logger.debug("Creating result record for testrun_id %d, platform_id %d, param_id %d", testrun_id, platform_id, param_id)
            self.cursor.execute("INSERT INTO lte_results(testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, best_dlthr, best_ulthr, tolerance, verdict_dl, verdict_ul, current_mA, pwr3p8V_mW) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, best_dlthr, best_ulthr, tolerance, verdict_dl, verdict_ul, current_mA, pwr3p8V_mW))
            return self.get_result_id_lte(testrun_id, platform_id, param_id)

if __name__ == '__main__':

    from Struct import Struct
    from cfg_multilogging import cfg_multilogging
    cfg_multilogging('INFO', 'DatabasePl1TestbenchLte.LOG')
    logger=logging.getLogger('DatabasePl1Testbench')
    
    t0=time.localtime()
            
    # Define folders hierarchy
    dir_root           = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:])
    dir_database       = os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database', '20140925'])
    dir_export         = os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database', 'export', '20140925'])
    dir_import         = os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database', 'import', '20140925']) 

    file_database_l    = [os.sep.join(dir_database.split(os.sep)[:]+['perf_bestscore_20140925_win8.db']),
                          os.sep.join(dir_database.split(os.sep)[:]+['pl1testbench_lte_20140925_Linux.db']),
                          os.sep.join(dir_database.split(os.sep)[:]+['pl1testbench_lte_tdd_20140925_Linux.db'])]

    #file_database      = os.sep.join(dir_database.split(os.sep)[:]+['pl1testbench_lte_tdd_20140909.db'])
                                    
        
    #logger=cfg_logger_root('DEBUG', log_file)    
    logger.info("FOLDER HIERARCHY  :")
    logger.info("------------------------------------")
    logger.info("dir_root          : %s" % dir_root)
    logger.info("dir_database      : %s" % dir_database)
    logger.info("dir_export        : %s" % dir_export)                              
    
    for file_database in file_database_l: 

        logger.info("------------------------------------")
        logger.info("file_database     : %s"  % file_database)
        logger.info("------------------------------------")
    
              
        if 1:  
            logger.debug(">> Check table existence")
            logger.debug("........................") 
            db_h=DatabasePl1TestbenchLte(file_database)
            logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_PLATFORMS, db_h.table_exists(db_h.TABLE_PLATFORMS)))
            logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_TESTINFOS, db_h.table_exists(db_h.TABLE_TESTINFOS)))
            logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_LTE_PARAMS, db_h.table_exists(db_h.TABLE_LTE_PARAMS)))
            logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_TESTRUNS, db_h.table_exists(db_h.TABLE_TESTRUNS)))
            logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_LTE_RESULTS, db_h.table_exists(db_h.TABLE_LTE_RESULTS)))
            db_h.disconnect()
            del db_h
        
        if 0:
            logger.debug(">> Check table view")
            logger.debug("---------------------------------------") 
            db_h=DatabasePl1Testbench(file_database)
            db_h.table_view(db_h.TABLE_PLATFORMS)
            db_h.table_view(db_h.TABLE_TESTINFOS)
            db_h.table_view(db_h.TABLE_LTE_PARAMS)
            db_h.table_view(db_h.TABLE_TESTRUNS)
            db_h.table_view(db_h.TABLE_LTE_RESULTS)
            db_h.disconnect()
            del db_h
    
        if 0:
            file_import_lte=os.path.join(dir_import,'LTE_FDD_CA_CMW500_TestReport_testID_1000_testType_LTE_FDD_CA_PERCL_BLER.csv')
            databaseImportLte(file_database, file_import_lte)
        
        if 1:
            file_export_lte= os.path.join(dir_export, os.path.splitext(os.path.basename(file_database))[0]+'_sqllite_export.csv')
            databaseExportLte(dbname=file_database, filename=file_export_lte)   
    
        if 0:
            # Testbler structure
            testbler_s=Struct()
            
            testbler_s.modeminfo     = """OK
                Response for CMD(AT%IDBGTEST) : CODE = 0  MSG = AT%IDBGTEST
            
                Platform Information
                --------------------
                Public Chip ID           : 70274E2EDCAD6AA13D792D18CA3089F7B735C9AA
                Boot ROM                 : ice9040-A0 V1.1
                Digital baseband chip Id : ICE9045 (Vivalto 1)
                Digital baseband version : A02P
                
                Firmware Information
                --------------------
                Changelist               : CL730547
                Number of modified files : 0
                Branch name              : main.br
                Variant                  : i500-121-1722
                Archtype                 : modem
                Build id (Sha1 on exe)   : dd0b019aeee84671c684b5acb7010f07535f9f3c
                Sdk                      : 4.11a
                &__extmem_size           : 0x3b00000
                Noninit bottom addr      : 0x8bd0c954
                bt2 yaffs heap used      : 68152
                bt2 yaffs heap avail     : 196608
                dxp0 Afault stack ptr    : 0x8bb01800
                dxp1 Afault stack ptr    : 0x8bb03000
                dxp2 Afault stack ptr    : 0x8bb04800
                dxp0 heap size (Bytes)   : 2097152
                dxp1 heap size (Bytes)   : 13584640
                dxp2 heap size (Bytes)   : 2097152
                Platform                 : icera.i500-121-1722.2022.100
                Boot counter       AT%IDBGTEST
                  : 69
                
                Digest numbers
                --------------------
                Secondary boot digest    : 6AB37A07
                Loader digest            : CC101121
                Factory test digest      : 00000000
                Application digest       : 5DCD6BC2
                
                RFM Board Identifcation
                -------------------------
                RFM Board ID             : BRI-7996
                RFM Batch ID             : I500-121-1722-CA-B00!0102-0
                """
            
            testbler_s.testID        = 1000
            testbler_s.descr         = "Full duplex link BLER test for CL validation  FDD mode  Carrier Aggregation"          
            testbler_s.testtype      = 'TODO: add'
            testbler_s.pcc           = Struct()         
            testbler_s.pcc.dmode     = 'FDD'
            testbler_s.pcc.dlulconf  = -1            
            testbler_s.pcc.ssconf    = -1
            testbler_s.pcc.bwmhz     = 10
            testbler_s.pcc.rfband    = 4
            testbler_s.pcc.earfcn    = 2175
            testbler_s.pcc.cp        = 'NORM'                    
            testbler_s.pcc.tm        = 3
            testbler_s.pcc.txants    = 2
            testbler_s.pcc.pmi       = 0
            testbler_s.pcc.rsepre    = -82.8
            testbler_s.pcc.pa        = -3
            testbler_s.pcc.pb        = 1            
            testbler_s.pcc.chtype    = 'None'
            testbler_s.pcc.snr       = 30
            testbler_s.pcc.doppler   = 0
            testbler_s.pcc.schedtype = 'UDCH'
            testbler_s.pcc.dlmcs     = 28
            testbler_s.pcc.dlnprb    = 50
            testbler_s.pcc.dlrbstart = 0
            testbler_s.pcc.ulmcs     = 10
            testbler_s.pcc.ulnprb    = 50
            testbler_s.pcc.ulrbstart = 0
            testbler_s.scc           = Struct()         
            testbler_s.scc.dmode     = 'FDD'
            testbler_s.scc.dlulconf  = -1            
            testbler_s.scc.ssconf    = -1
            testbler_s.scc.bwmhz     = 10
            testbler_s.scc.rfband    = 17
            testbler_s.scc.earfcn    = 5790
            testbler_s.scc.cp        = 'NORM'                    
            testbler_s.scc.tm        = 3
            testbler_s.scc.txants    = 2
            testbler_s.scc.pmi       = 0
            testbler_s.scc.rsepre    = -82.8
            testbler_s.scc.pa        = -3
            testbler_s.scc.pb        = 1            
            testbler_s.scc.chtype    = 'None'
            testbler_s.scc.snr       = 30
            testbler_s.scc.doppler   = 0
            testbler_s.scc.schedtype = 'UDCH'
            testbler_s.scc.dlmcs     = 28
            testbler_s.scc.dlnprb    = 50
            testbler_s.scc.dlrbstart = 0
            testbler_s.scc.ulmcs     = 10
            testbler_s.scc.ulnprb    = 50
            testbler_s.scc.ulrbstart = 0
            
                    
            branch_ulthr, clnum_ulthr, score_ulthr             = databaseExportBestScoreLte(dbname=file_database, test_s=testbler_s, carrier='PCC', varname='ulthr')
            branch_dlthr_pcc, clnum_dlthr_pcc, score_dlthr_pcc = databaseExportBestScoreLte(dbname=file_database, test_s=testbler_s, carrier='PCC', varname='dlthr')
            if not testbler_s.scc is None:
                branch_dlthr_scc, clnum_dlthr_scc, score_dlthr_scc = databaseExportBestScoreLte(dbname=file_database, test_s=testbler_s, carrier='SCC', varname='dlthr')
        
    t1=time.localtime()
    dt=time.mktime(t1)-time.mktime(t0)
    logger.info("Time duration %d[sec]" % dt)
           
           
   
    
        

    
