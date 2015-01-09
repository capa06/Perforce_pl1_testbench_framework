'''
Created on 28 Nov 2013

@author: jlucas, fsaracino, joashr
'''

import os, sys, logging, time, sqlite3, re

# =============================================================================
# DEFINE LOCAL PATHS
# =============================================================================

try:
    import test_env
except ImportError:
    (cmdpath, cmdname)=os.path.split(os.path.abspath(__file__))
    test_env_dir=os.sep.join(cmdpath.split(os.sep)[:-4])
    sys.path.append(test_env_dir)
    import test_env


# =============================================================================
# IMPORT USER DEFINED LIBRARY
# =============================================================================


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

SELECTALL_HEADER_LIST=['result_id',
                       'testrun_id',
                       'platform_id',
                       'param_id',
                        'valid',
                        'dlrely',
                        'dlthr',
                        'dlbler',
                        'cqi',
                        'ack',
                        'nack',
                        'dtx',
                        'sf_total',
                        'sf_scheduled',
                        'ulrely',
                        'ulthr',
                        'ulbler',
                        'crc_pass',
                        'crc_fail',
                        'current_mA',
                        'rirely',
                        'numRI1',
                        'numRI2',
                        'platform_id',
                        'platform',
                        'aux_info',
                        'testrun_id',
                        'timestamp',
                        'branch',
                        'clnum',
                        'mod_files',
                        'param_id',
                        'testinfo_id',
                        'rfband',
                        'earfcn',
                        'bwmhz',
                        'chtype',
                        'snr',
                        'rsepre',
                        'pa',
                        'pb',
                        'tm',
                        'txants',
                        'pmi',
                        'schedtype',
                        'dlmcs',
                        'dlnprb',
                        'dlrbstart',
                        'ulmcs',
                        'ulnprb',
                        'ulrbstart',
                        'testinfo_id',
                        'rat',
                        'testid',
                        'descr']

CURRENT_MEAS_NOT_APPL = -1  # current meas not applicable so default value used
POWER_MEAS_NOT_APPL = -1    # power meas not applicable so default value used

# =============================================================================
# GLOBAL FUNCTIONS
# =============================================================================

# Icera decoders
icera_aes = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-aes'])
icera_b64 = os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera', 'icera-b64'])


def ParseModemInfo(msg_enc):
    """
        Decode modem info
    """
    import subprocess
    logging.debug("ParseModemInfo()...")
    if sys.platform in ['cygwin', 'win32']:
        cmd='echo/|set /p=%s| %s -d | %s -d -p 9TfyKtMO+hoPyscfR15GEw8PYlzNPvMksp5wwSvxbMI=' % (msg_enc, icera_b64, icera_aes)
    elif  sys.platform in ['linux', 'linux2', 'linux3']:
        cmd='echo -n %s | %s -d | %s -d -p 9TfyKtMO+hoPyscfR15GEw8PYlzNPvMksp5wwSvxbMI=' % (msg_enc, icera_b64, icera_aes)
    else:
        print "Unkown platform, nothing to do"
        return None
    res=subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()[0]
    if res=="" : res="NA"
    return res


def GetBranch(msg):
    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    branch_re=re.compile(r".*Branch name\s*:\s*(\S*).*$")
    branch='NA'
    if branch_re.search(msg_str):
        res=branch_re.findall(msg_str)
        if (res[0][0:3] == "css"):
            # Encoded string
            branch=ParseModemInfo(res[0])
        else:
            # string not encoded
            branch=res[0]
    logging.debug(">> GetBranch() : %s" % branch)
    return branch


def GetPlatform(msg):
    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    platform_re=re.compile(r".*Platform\s*:\s*(.*?)\s")
    platform='NA'
    if platform_re.search(msg_str):
        platform=platform_re.findall(msg)[0]
    logging.debug(">> GetPlatform() : %s" % platform)
    return platform


def GetVariant(msg):
    # Define rules for retrieving the configuration
    msg_str = msg.replace('\n','')
    variant_re=re.compile(r".*Variant\s*:\s*(\S*).*$")
    variant='N/A'
    if variant_re.search(msg_str):
        res=variant_re.findall(msg)
        if (res[0][0:3] == "css"):
            # Encoded string
            variant=ParseModemInfo(res[0])
        else:
            # string not encoded
            variant=res[0]
    logging.debug(">> GetVariant() : %s" % variant)
    return variant


def CsvParseMeas(fname, key_l):
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
    logging.debug("CsvParseMeas()...")

    # Initialise result structures
    config_dict = {'timestamp':'N/A', 'platform':'N/A', 'branch':'N/A', 'clnum':'N/A', 'mod_files':'N/A', 'testid':'N/A', 'descr':'N/A'}
    entry_dict  = {}
    for key in range(len(key_l)): entry_dict[key_l[key]]=[]

    # Define rules for retrieving the configuration
    branch_re=re.compile(r".*Branch name\s*:\s*(\S*).*$")
    #variant_re=re.compile(r".*Variant\s*:\s*(\S*).*$")
    clnum_re=re.compile(r".*Changelist\s+:\s*CL(\d+)")
    platform_re=re.compile(r".*Platform\s*:\s*(.*?)\s")
    mod_files_re=re.compile(r".*Number of modified files\s+:\s(\d+)")
    timestamp_re=re.compile(r".*date.*,\s*(\S*\s*\S*).*$")
    testid_re=re.compile(r".*id.*,\s*\[(\d+)\].*$")
    testtype_re=re.compile(r".*testtype.*,\s*(.*?)\s")
    # Check file existence
    if not os.path.isfile(fname):
        print("WARNING::CsvFilter():: File %s not found. Filter function not applied")
        return (config_dict, entry_dict)


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
                        config_dict['branch']=ParseModemInfo(res[0])
                    else:
                        config_dict['branch']=res[0]
                    logging.debug("FOUND branch: %s" % config_dict['branch'])
                if clnum_re.search(line):
                    res=clnum_re.findall(line)
                    logging.debug("FOUND clnum: %s" % res[0])
                    config_dict['clnum']=res[0]
                if platform_re.search(line):
                    res=platform_re.findall(line)
                    logging.debug("FOUND platform: %s" % res[0])
                    config_dict['platform']=res[0]
                if mod_files_re.search(line):
                    res=mod_files_re.findall(line)
                    logging.debug("FOUND mod_files: %s" % res[0])
                    config_dict['mod_files']=res[0]
                if timestamp_re.search(line):
                    res=timestamp_re.findall(line)
                    logging.debug("FOUND timestamp: %s" % res[0])
                    config_dict['timestamp']=res[0]
                if testid_re.search(line):
                    res=testid_re.findall(line)
                    logging.debug("FOUND testid: %s" % res[0])
                    config_dict['testid']=res[0]
                if testtype_re.search(line):
                    res=testtype_re.findall(line)
                    logging.debug("FOUND testtype: %s" % res[0])
                    config_dict['descr']=res[0]

                # Check if header entry
                if (line_l[0].strip()).upper() == 'TESTID':

                    # Check if any invalid KEY
                    key_invalid_l = filter( lambda x: x not in line_l, key_l)
                    key_valid_l   = [x for x in key_l if x not in key_invalid_l]

                    logging.debug("INVALID KEY LIST : %s" % key_invalid_l)
                    logging.debug("VALID KEY LIST   : %s" % key_valid_l)

                    # Retrieve the column index
                    colidx_l = [line_l.index(x) for x in key_valid_l]
                    z=zip(key_valid_l, colidx_l)
                    if 0:
                        for i in range(len(z)):
                            logging.debug("key '%s' mapped on column %s" % (z[i][0], z[i][1]))

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
def DB_destroy(dbname):
    logging.debug("DB_destroy()...")
    db_h=results_db(dbname)
    db_h.destroy()
    del db_h

def DB_CheckPermission(dbname):
    if sys.platform in ['cygwin', 'win32']:
        cmd="attrib -r %s" % dbname
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd="chmod +w %s" % dbname
    else:
        logging.warning("DB_CheckPermission(): UNKNOW PLATFORM %s" % sys.platform)
    os.system(cmd)

def DB_import_from_file_meas(dbname, filename):

    logging.debug("DB_import_from_file_meas()...")
    logging.debug("DB_import_from_file_meas()...FILE %s" % filename)

    # Get database connection object instance
    db_h=results_db(dbname)

    # Open database connection
    db_h.connect()

    keywords_l=['TESTID', 'BWMHZ', 'RFBAND', 'EARFCN', 'CHTYPE', 'SNR', 'RSEPRE', 'PA', 'PB', 'TM', 'TXANTS', 'PMI', 'SCHEDTYPE', 'DLMCS', 'DLNPRB', 'DLRBSTART', 'ULMCS', 'ULNPRB', 'ULRBSTART', 'DLRELY', 'DLTHR[Mbps]', 'DLBLER', 'CQI', 'ACK', 'NACK', 'DTX', 'NSF', 'SCHED', 'ULRELY', 'ULTHR[Mbps]', 'ULBLER', 'CRC PASS', 'CRC FAIL', 'BEST DLTHR[Mbps]', 'BEST ULTHR[Mbps]', 'TOLERANCE', 'DL VERDICT', 'UL VERDICT']

    table_config, table_entry=CsvParseMeas(fname=filename, key_l=keywords_l)

    # Debug
    if 0:
        logging.debug(">>> TEST CONFIG:")
        for k,v in table_config.iteritems():
            logging.debug("table_config[%s] = %s" % (k, v))
    if 0:
        logging.debug(">>> TEST RESULTS:")
        for k,v in table_entry.iteritems():
            logging.debug("table_entry[%s] = %s" % (k, v))

    # Add platform
    platform_id=db_h.add_platform(table_config['platform'], aux_info="N/A")
    logging.info("SELECTED: platform_id:%s, platform:%s" % (platform_id, table_config['platform']))

    # Add test info
    testinfo_id=db_h.add_testinfo(testid=table_config['testid'], descr=table_config['descr'] )
    logging.info("SELECTED: testinfo_id:%s, testid:%s, descr:%s" % (testinfo_id, table_config['testid'], table_config['descr']))

    # Add test_run
    testrun_id=db_h.add_testrun(timestamp=table_config['timestamp'], branch=table_config['branch'], clnum=table_config['clnum'], mod_files=table_config['mod_files'])
    logging.info("SELECTED: testrun_id:%s, timestamp=%s, branch:%s, clnum:%s, mod_files:%s" % (testrun_id, table_config['timestamp'], table_config['branch'], table_config['clnum'], table_config['mod_files']))

    # Add param_set and results
    total_entries=len(table_entry[keywords_l[0]])
    for idx in range(total_entries):
        # Format the data to store into the datatbase
        rfband=table_entry['RFBAND'][idx]
        # FIXME: change EARFCN format in the PL1TESTBENCH
        earfcn=int(float(table_entry['EARFCN'][idx]))
        bwmhz=table_entry['BWMHZ'][idx]
        chtype=table_entry['CHTYPE'][idx]
        snr=table_entry['SNR'][idx]
        rsepre=table_entry['RSEPRE'][idx]
        pa=table_entry['PA'][idx]
        pb=table_entry['PB'][idx]
        tm=table_entry['TM'][idx]
        txants=table_entry['TXANTS'][idx]
        pmi=table_entry['PMI'][idx]
        schedtype='AMC' if table_entry['SCHEDTYPE'][idx]=='CQI' else 'FIXED'
        dlmcs=table_entry['DLMCS'][idx]
        dlnprb=table_entry['DLNPRB'][idx]
        dlrbstart=table_entry['DLRBSTART'][idx]
        ulmcs=table_entry['ULMCS'][idx]
        ulnprb=table_entry['ULNPRB'][idx]
        ulrbstart=table_entry['ULRBSTART'][idx]

        # Add param set
        param_id=db_h.add_param_set(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)
        logging.info("SELECTED: param_id:%d, %s",param_id, (testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))

        # Add results
        valid=1
        dlrely=table_entry['DLRELY'][idx]
        dlthr=table_entry['DLTHR[Mbps]'][idx]
        dlbler=table_entry['DLBLER'][idx]
        cqi=table_entry['CQI'][idx]
        ack=table_entry['ACK'][idx]
        nack=table_entry['NACK'][idx]
        dtx=table_entry['DTX'][idx]
        sf_total=table_entry['NSF'][idx]
        sf_scheduled=table_entry['SCHED'][idx]
        ulrely=table_entry['ULRELY'][idx]
        ulthr=table_entry['ULTHR[Mbps]'][idx]
        ulbler=table_entry['ULBLER'][idx]
        crc_pass=table_entry['CRC PASS'][idx]
        crc_fail=table_entry['CRC FAIL'][idx]
        current_mA=0
        rirely=0
        numRI1=0
        numRI2=0

        result_id=db_h.add_result(testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, current_mA, rirely, numRI1, numRI2)
        logging.info("SELECTED: result_id:%d, %s",result_id, (testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, current_mA, rirely, numRI1, numRI2))

    # Commit data
    db_h.conn.commit()

    # Close database connection
    db_h.disconnect()

    del db_h
    return 0



def DB_wcdma_import_from_file_meas(dbname, filename, testType):

    logging.debug("DB_wcdma_import_from_file_meas()...")
    logging.debug("DB_wcdma_import_from_file_meas()...FILE %s" % filename)

    # Get database connection object instance
    db_h=results_db(dbname)

    # Open database connection
    db_h.connect()

    if testType == 'BLER_PERF':
        keywords_l=['TESTID', 'RFBAND', 'UARFCN', 'CHTYPE', 'DATARATE', 'SNR', 'POWER', 'TXANTS', 'DLRELY', 'BER', 'BLER', 'DLBLER', 'LOSTBLOCKS', 'PNDiscontinuity', 'DL VERDICT', 'Imin[mA]', 'Iavrg[mA]', 'Imax[mA]', 'Ideviation', 'PWRmin[mW]@3.8V', 'PWRavrg[mW]@3.8V', 'PWRmax[mW]@3.8V' ]
    elif testType == 'HSPA_BLER_PERF' :
        keywords_l=['TESTID', 'RFBAND', 'UARFCN', 'CHTYPE', 'DATARATE', 'SNR', 'POWER', 'TXANTS', 'SCHEDTYPE', 'MODULATION', 'Ki', 'NUM_HSDSCH_CODES', 'NSF', 'TARGET Tput(Mbps)', 'DL_TPUT(Mbps)', 'DL_BLER', 'TOL(%)', 'CQI', 'SENT(%)', 'ACK(%)', 'NACK(%)', 'DTX(%)', 'DL VERDICT', 'Imin[mA]', 'Iavrg[mA]', 'Imax[mA]', 'Ideviation', 'PWRmin[mW]@3.8V', 'PWRavrg[mW]@3.8V', 'PWRmax[mW]@3.8V']
    elif testType == 'DCHSDPA_BLER_PERF':
        keywords_l=['TESTID', 'RFBAND', 'UARFCN', 'CHTYPE', 'DATARATE', 'SNR', 'POWER', 'TXANTS', 'SCHEDTYPE', 'MODULATION', 'Ki', 'NUM_HSDSCH_CODES', 'SNR_2', 'POWER_2', 'MODULATION_2', 'Ki_2', 'NUM_HSDSCH_CODES_2', 'NSF', 'TARGET Tput(Mbps)', 'DL_TPUT(Mbps)', 'DL_BLER', 'TOL(%)', 'CQI', 'SENT(%)', 'ACK(%)', 'NACK(%)', 'DTX(%)', 'TARGET Tput_2(Mbps)', 'DL_TPUT_2(Mbps)', 'DL_BLER_2', 'CQI_2', 'SENT_2(%)', 'ACK_2(%)', 'NACK_2(%)', 'DTX_2(%)', 'DL VERDICT', 'Imin[mA]', 'Iavrg[mA]', 'Imax[mA]', 'Ideviation', 'PWRmin[mW]@3.8V', 'PWRavrg[mW]@3.8V', 'PWRmax[mW]@3.8V']
    else:
        logging.warning("Unknown test type %s" % testType)
        # Close database connection
        db_h.disconnect()
        return

    #keywords_l=['TESTID', 'BWMHZ', 'RFBAND', 'EARFCN', 'CHTYPE', 'SNR', 'RSEPRE', 'PA', 'PB', 'TM', 'TXANTS', 'PMI', 'SCHEDTYPE', 'DLMCS', 'DLNPRB', 'DLRBSTART', 'ULMCS', 'ULNPRB', 'ULRBSTART', 'DLRELY', 'DLTHR[Mbps]', 'DLBLER', 'CQI', 'ACK', 'NACK', 'DTX', 'NSF', 'SCHED', 'ULRELY', 'ULTHR[Mbps]', 'ULBLER', 'CRC PASS', 'CRC FAIL', 'BEST DLTHR[Mbps]', 'BEST ULTHR[Mbps]', 'TOLERANCE', 'DL VERDICT', 'UL VERDICT']

    table_config, table_entry=CsvParseMeas(fname=filename, key_l=keywords_l)

    # Debug
    if 0:
        logging.debug(">>> TEST CONFIG:")
        for k,v in table_config.iteritems():
            logging.debug("table_config[%s] = %s" % (k, v))
    if 0:
        logging.debug(">>> TEST RESULTS:")
        for k,v in table_entry.iteritems():
            logging.debug("table_entry[%s] = %s" % (k, v))

    # Add platform
    platform_id=db_h.add_platform(table_config['platform'], aux_info="N/A")
    logging.info("SELECTED: platform_id:%s, platform:%s" % (platform_id, table_config['platform']))

    # Add test info
    testinfo_id=db_h.add_testinfo(testid=table_config['testid'], descr=table_config['descr'], rat="WCDMA" )
    logging.info("SELECTED: testinfo_id:%s, testid:%s, descr:%s" % (testinfo_id, table_config['testid'], table_config['descr']))

    # Add test_run
    testrun_id=db_h.add_testrun(timestamp=table_config['timestamp'], branch=table_config['branch'], clnum=table_config['clnum'], mod_files=table_config['mod_files'])
    logging.info("SELECTED: testrun_id:%s, timestamp=%s, branch:%s, clnum:%s, mod_files:%s" % (testrun_id, table_config['timestamp'], table_config['branch'], table_config['clnum'], table_config['mod_files']))




    if 1:
        # Add param_set and results
        total_entries=len(table_entry[keywords_l[0]])
        for idx in range(total_entries):
            if testType == 'BLER_PERF':
                w_param_id=db_h.add_wcdma_bler_perf_test_param_set(testinfo_id=testinfo_id, idx=idx, table_entries=table_entry)
                result_id=db_h.add_wcdma_bler_perf_test_result(testrun_id, platform_id, w_param_id, idx, table_entry)
                logging.info("SELECTED: result_id:%d, %s",result_id, (testrun_id, platform_id, w_param_id))
            elif testType == 'HSPA_BLER_PERF':
                w_param_id=db_h.add_wcdma_hspa_test_param_set(testinfo_id=testinfo_id, idx=idx, table_entries=table_entry)
                result_id=db_h.add_wcdma_hspa_test_result(testrun_id, platform_id, w_param_id, idx, table_entry)
                logging.info("SELECTED: result_id:%d, %s",result_id, (testrun_id, platform_id, w_param_id))
            elif testType == 'DCHSDPA_BLER_PERF':
                w_param_id=db_h.add_wcdma_dc_hspa_test_param_set(testinfo_id=testinfo_id, idx=idx, table_entries=table_entry)
                result_id=db_h.add_wcdma_dc_hspa_test_result(testrun_id, platform_id, w_param_id, idx, table_entry)
                logging.info("SELECTED: result_id:%d, %s",result_id, (testrun_id, platform_id, w_param_id))
            else:
                logger_test.warning("Unknown test type %s. TestID %s SKIPPED" % (curr_test.testtype, curr_test.testID))


    # Commit data
    db_h.conn.commit()

    # Close database connection
    db_h.disconnect()

    del db_h
    return 0


def DB_export_to_file(dbname, equery, filename):

    logging.debug("DB_export()...")
    logging.debug("DB_export()...FILE %s" % filename)

    # Check database
    if not os.path.isfile(dbname):
        logging.warning("DB_export_to_file():: database %s not found. Export ABORTED" % dbname)
        return -1

    # Clean data from any previous test
    if os.path.isfile(filename):
        os.remove(filename)

    # Create destination folder, if does not exists
    fpath=os.path.split(filename)[0]
    if not os.path.exists(fpath):
        logging.debug("Creating destination folder: %s" % fpath)
        os.makedirs(fpath)

    # Get database connection object instance
    db_h=results_db(dbname)

    # Open database connection
    db_h.connect()

    # Complete header
    selectall_header_l= SELECTALL_HEADER_LIST

    # Extract the export header from EQUERY
    select_str=re.findall(r'SELECT\s*(.*?)\s*FROM',equery)[0]
    logging.debug("SELECT QUERY header %s" % select_str)
    if select_str=='*':
        selectout_header_l = selectall_header_l
    else:
        selectout_header_l = select_str.split(',')

    selectout_entry_frmt='%s, '*(len(selectout_header_l)-1)+'%s\n'

    try:
        db_h.cursor.execute(equery)
        if db_h.cursor:
            with open(filename,'a') as fd:
                fd.write(selectout_entry_frmt % tuple(selectout_header_l))
                for result in db_h.cursor:
                    fd.write(selectout_entry_frmt % tuple(result))
        else:
            logging.debug("export_to_csv(), no entry found in database %s" % dbname)
    except TypeError:
        logging.error("export_to_csv(), SELECT failure")
        return -1
    except IOError:
        logging.error("ERROR: opening file %s" % filename)
        return -1
    else:
        logging.debug("Data exported into file %s" % filename)

        # Close database connection
        db_h.disconnect()

    del db_h
    return 0


def DB_export_bestscore(dbname, equery):

    logging.debug("DB_export_bestscore()...")

    res= (None, None, None)

    # Get database connection object instance
    db_h=results_db(dbname)

    # Open database connection
    db_h.connect()

    # Complete header
    selectall_header_l= SELECTALL_HEADER_LIST

    # Extract the export header from EQUERY
    select_str=re.findall(r'SELECT\s*(.*?)\s*FROM',equery)[0]

    logging.debug("SELECT QUERY header %s" % select_str)
    if select_str=='*':
        selectout_header_l = selectall_header_l
    else:
        selectout_header_l = select_str.split(',')

#    selectout_entry_frmt='%s, '*(len(selectout_header_l)-1)+'%s\n'

    try:
        print equery
        db_h.cursor.execute(equery)
        if db_h.cursor:
            for result in db_h.cursor:
                branch = result[0]
                clnum  = result[1]
                dlthr  = result[2]
                res=(branch, clnum, dlthr)
        else:
            logging.debug("DB_export_bestscore(), no entry found in database %s" % dbname)
    except TypeError:
        logging.error("DB_export_bestscore(), SELECT failure")
        return (None, None, None)
    else:
        logging.debug("DB_export_bestscore() completed")
        # Close database connection
        db_h.disconnect()

    return res


def DB_SetQueryBestScore(modeminfo, testparams, varname):
    logging.debug(">>>> DB_SetQueryBestScore()...")
    branch  = GetBranch(modeminfo)
    bwmhz     = testparams[1]
    chtype    = testparams[4]
    snr       = testparams[5]
    rsepre    = testparams[6]
    pa        = testparams[7]
    pb        = testparams[8]
    tm        = testparams[9]
    txants    = testparams[10]
    pmi       = testparams[11]
    schedtype = 'AMC' if testparams[12]=='CQI' else 'FIXED'
    dlmcs     = testparams[13]
    dlnprb    = testparams[14]
    dlrbstart = testparams[15]
    ulmcs     = testparams[16]
    ulnprb    = testparams[17]
    ulrbstart = testparams[18]

#    variant = GetVariant(modeminfo)
    platform=GetPlatform(modeminfo)

    if 0:
        #print  "modeminfo : %s" % modeminfo
        print  "branch    : %s" % branch
        print  "platform  : %s" % platform
        print  "bwmhz     : %s" % bwmhz
        print  "chtype    : %s" % chtype
        print  "snr       : %s" % snr
        print  "rsepre    : %s" % rsepre
        print  "pa        : %s" % pa
        print  "pb        : %s" % pb
        print  "tm        : %s" % tm
        print  "txants    : %s" % txants
        print  "pmi       : %s" % pmi
        print  "schedtype : %s" % schedtype
        print  "dlmcs     : %s" % dlmcs
        print  "dlnprb    : %s" % dlnprb
        print  "dlrbstart : %s" % dlrbstart
        print  "ulmcs     : %s" % ulmcs
        print  "ulnprb    : %s" % ulnprb
        print  "ulrbstart : %s" % ulrbstart

    equery_bestscore=re.sub('[ |\t|\n]+',' ', r"""SELECT branch,clnum,MAX(%s) FROM results
        INNER JOIN platforms ON results.platform_id=platforms.platform_id
        INNER JOIN testruns ON results.testrun_id=testruns.testrun_id
        INNER JOIN params ON results.param_id=params.param_id
        INNER JOIN testinfos ON params.testinfo_id=testinfos.testinfo_id
        WHERE branch=='%s'
            AND platform='%s'
            AND bwmhz==%s
            AND chtype=='%s'
            AND snr==%s
            AND rsepre==%s
            AND pa==%s
            AND pb==%s
            AND tm==%s
            AND txants==%s
            AND pmi==%s
            AND schedtype=='%s'
            AND dlmcs==%s
            AND dlnprb==%s
            AND dlrbstart==%s
            AND ulmcs==%s
            AND ulnprb==%s
            AND ulrbstart==%s;""" % (varname, branch, platform, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
    logging.debug("EQUERY: %s" % equery_bestscore)
    return equery_bestscore


def DB_SelectBestScore(dbname, modeminfo, testparams):
    logging.debug(">> DB_SelectBestScore()...")
    dlthr_equery=DB_SetQueryBestScore(modeminfo, testparams, 'dlthr')
    dlthr_branch, dlthr_clnum, dlthr_score = DB_export_bestscore(dbname=dbname, equery=dlthr_equery)
    ulthr_equery=DB_SetQueryBestScore(modeminfo, testparams, 'ulthr')
    ulthr_branch, ulthr_clnum, ulthr_score = DB_export_bestscore(dbname=dbname, equery=ulthr_equery)
    return (dlthr_branch, dlthr_clnum, dlthr_score), (ulthr_branch, ulthr_clnum, ulthr_score)


# =============================================================================
# DATABASE STRUCTURE FOR PERFORMANCE MEASUREMENTS
# =============================================================================
class results_db(object):
    TABLE_PLATFORMS = 'platforms'
    TABLE_TESTINFOS = 'testinfos'
    TABLE_PARAMS    = 'params'
    TABLE_TESTRUNS  = 'testruns'
    TABLE_RESULTS   = 'results'

    name=None
    conn=None
    cursor=None

    def __init__ (self, name):
            # If database exists
            if os.path.exists(name):
                logging.debug("FOUND database           : %s" % name)
                # Check connection
                self.name   = name
                self.connect()
                self.cursor = self.conn.cursor()
                self.conn.execute("PRAGMA foreign_keys = ON;")
                #self.disconnect()
            else:
                try:
                    # Create destination folder, if does not exists
                    fpath=os.path.split(name)[0]
                    if not os.path.exists(fpath):
                        logging.debug("Creating destination folder: %s" % fpath)
                        os.makedirs(fpath)

                    self.name   = name
                    self.connect()
                    self.cursor = self.conn.cursor()
                    self.conn.execute("PRAGMA foreign_keys = ON;")

                    logging.debug("INITIALIZING database    : %s" % self.name)

                    self.conn.executescript("""
                        CREATE TABLE IF NOT EXISTS platforms (platform_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              platform        TEXT                NOT NULL,
                                                              aux_info        TEXT);

                        CREATE TABLE IF NOT EXISTS testinfos (testinfo_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              rat             TEXT                NOT NULL DEFAULT LTE_FDD,
                                                              testid          INTEGER UNSIGNED    NOT NULL,
                                                              descr           TEXT);

                        CREATE TABLE IF NOT EXISTS params (   param_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              testinfo_id     INTEGER             NOT NULL,
                                                              rfband          INTEGER             NOT NULL,
                                                              earfcn          INTEGER             NOT NULL,
                                                              bwmhz           REAL                NOT NULL,
                                                              chtype          TEXT                NOT NULL,
                                                              snr             REAL                NOT NULL,
                                                              rsepre          REAL                NOT NULL,
                                                              pa              INTEGER             NOT NULL,
                                                              pb              INTEGER             NOT NULL,
                                                              tm              INTEGER UNSIGNED    NOT NULL,
                                                              txants          INTEGER UNSIGNED    NOT NULL,
                                                              pmi             INTEGER UNSIGNED    NOT NULL,
                                                              schedtype       TEXT                NOT NULL,
                                                              dlmcs           INTEGER UNSIGNED,
                                                              dlnprb          INTEGER UNSIGNED,
                                                              dlrbstart       INTEGER UNSIGNED,
                                                              ulmcs           INTEGER UNSIGNED,
                                                              ulnprb          INTEGER UNSIGNED,
                                                              ulrbstart       INTEGER UNSIGNED,
                                                            FOREIGN KEY (testinfo_id) REFERENCES testinfos(testinfo_id));

                        CREATE INDEX IF NOT EXISTS param_lookup ON params (bwmhz,
                                                                           chtype,
                                                                           snr,
                                                                           pa,
                                                                           pb,
                                                                           tm,
                                                                           txants);

                        CREATE TABLE IF NOT EXISTS testruns ( testrun_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              timestamp       TIMESTAMP           NOT NULL,
                                                              branch          TEXT                NOT NULL,
                                                              clnum           INTEGER UNSIGNED    NOT NULL,
                                                              mod_files       INTEGER UNSIGNED    NOT NULL);

                        CREATE TABLE IF NOT EXISTS results (  result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              testrun_id      INTEGER             NOT NULL,
                                                              platform_id     INTEGER             NOT NULL,
                                                              param_id        INTEGER             NOT NULL,
                                                              valid           BOOL                NOT NULL,
                                                              dlrely          INTEGER,
                                                              dlthr           REAL,
                                                              dlbler          REAL,
                                                              cqi             INTEGER UNSIGNED,
                                                              ack             INTEGER UNSIGNED,
                                                              nack            INTEGER UNSIGNED,
                                                              dtx             INTEGER UNSIGNED,
                                                              sf_total        INTEGER UNSIGNED,
                                                              sf_scheduled    INTEGER UNSIGNED,
                                                              ulrely          INTEGER UNSIGNED,
                                                              ulthr           REAL,
                                                              ulbler          REAL,
                                                              crc_pass        INTEGER UNSIGNED,
                                                              crc_fail        INTEGER UNSIGNED,
                                                              current_mA      REAL,
                                                              rirely          INTEGER UNSIGNED,
                                                              numRI1          INTEGER UNSIGNED,
                                                              numRI2          INTEGER UNSIGNED,
                                                            FOREIGN KEY (testrun_id) REFERENCES testruns(testrun_id),
                                                            FOREIGN KEY (param_id) REFERENCES params(param_id),
                                                            FOREIGN KEY (platform_id) REFERENCES platforms(platform_id));

                        CREATE TABLE IF NOT EXISTS wcdma_params (    w_param_id       INTEGER     PRIMARY KEY AUTOINCREMENT,
                                                                     testinfo_id      INTEGER     NOT NULL,
                                                                     rfband           INTEGER     NOT NULL,
                                                                     uarfcn           INTEGER     NOT NULL,
                                                                     chtype           TEXT        NOT NULL,
                                                                     datarate         TEXT        NOT NULL,
                                                                     snr              REAL        NOT NULL,
                                                                     power            REAL        NOT NULL,
                                                                     txant            INTEGER     UNSIGNED NOT NULL,
                                                                     sched_type       TEXT        DEFAULT NA,
                                                                     modulation       TEXT        DEFAULT NA,
                                                                     ki               INTEGER     DEFAULT 0,
                                                                     num_hsdsch_codes INTEGER     DEFAULT 0,
																	 snr_2                REAL    DEFAULT 0.0,
                                                                     power_2              REAL    DEFAULT 0.0,
                                                                     modulation_2         TEXT,
                                                                     ki_2                 INTEGER     DEFAULT 0,
                                                                     num_hsdsch_codes_2   INTEGER     DEFAULT 0,
                                                                     FOREIGN KEY (testinfo_id) REFERENCES testinfos(testinfo_id));

                        CREATE TABLE IF NOT EXISTS wcdma_results (    result_id           INTEGER    PRIMARY KEY AUTOINCREMENT,
                                                                      testrun_id          INTEGER    NOT NULL,
                                                                      platform_id         INTEGER    NOT NULL,
                                                                      w_param_id          INTEGER    NOT NULL,
                                                                      dlrely              INTEGER    DEFAULT 0,
                                                                      dl_ber              REAL       DEFAULT 0.0,
                                                                      dl_bler             REAL       DEFAULT 0.0,
                                                                      lost_blocks         INTEGER    DEFAULT 0,
                                                                      pdn_discontinuity   INTEGER    DEFAULT 0,
                                                                      num_sf              INTEGER    DEFAULT 0,
                                                                      dl_target_thput     REAL       DEFAULT 0.0,
                                                                      dl_thput            REAL       DEFAULT 0.0,
                                                                      tol                 REAL       DEFAULT 0.0,
                                                                      cqi                 INTEGER    UNSIGNED DEFAULT 0,
                                                                      sent                REAL       DEFAULT 0.0,
                                                                      ack                 REAL       DEFAULT 0.0,
                                                                      nack                REAL       DEFAULT 0.0,
                                                                      dtx                 REAL       DEFAULT 0.0,
																	  dl_target_thput_2   REAL       DEFAULT 0.0,
                                                                      dl_thput_2          REAL       DEFAULT 0.0,
                                                                      dl_bler_2           REAL       DEFAULT 0.0,
                                                                      cqi_2               INTEGER    UNSIGNED DEFAULT 0,
                                                                      sent_2              REAL       DEFAULT 0.0,
                                                                      ack_2               REAL       DEFAULT 0.0,
                                                                      nack_2              REAL       DEFAULT 0.0,
                                                                      dtx_2               REAL       DEFAULT 0.0,
                                                                      dl_verdict          TEXT       DEFAULT NA,
                                                                      i_min               REAL       DEFAULT 0.0,
                                                                      i_avg               REAL       DEFAULT 0.0,
                                                                      i_max               REAL       DEFAULT 0.0,
                                                                      i_deviation         REAL       DEFAULT 0.0,
                                                                      pwr_min             REAL       DEFAULT 0.0,
                                                                      pwr_avg             REAL       DEFAULT 0.0,
                                                                      pwr_max             REAL       DEFAULT 0.0,
                                                                      FOREIGN KEY (testrun_id) REFERENCES testruns(testrun_id),
                                                                      FOREIGN KEY (w_param_id) REFERENCES wcdma_params(w_param_id),
                                                                      FOREIGN KEY (platform_id) REFERENCES platforms(platform_id));

                        CREATE TABLE IF NOT EXISTS pl1_db_info (     id            INTEGER    PRIMARY KEY AUTOINCREMENT,
                                                                     version       REAL       NOT NULL,
                                                                     desc          TEXT);

                        CREATE INDEX IF NOT EXISTS results_lookup ON results(platform_id,param_id);""")

                    self.conn.commit()
                    #self.disconnect()
                except sqlite3.OperationalError:
                    logging.error("Error initialising database %s" % self.name)
                    exit(1)
                else:
                    logging.debug("INITIALIZED database     : %s" % self.name)

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.name)
            logging.debug("CONNECT to database      : %s" % self.name)

    def disconnect(self):
        if not self.conn is None:
            self.conn.close()
            logging.debug("DISCONNECT from database : %s" % self.name)

    def destroy(self):
        if os.path.exists(self.name):
            #logging.debug("FOUND database : %s" % self.name)
            if not self.conn is None:
                self.disconnect()
            os.remove(self.name)
            logging.debug("DESTROYED database       : %s" % self.name)

    # =============================================================================
    # TABLE SPECIFIC FUNCTIONS
    # =============================================================================
    def table_exists(self, tablename):
        try:
            if self.conn==None:
                self.connect()
#            self.cursor.execute("""SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s';""" % tablename)
            self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
            result=(self.cursor.fetchone()[0] > 0)
        except sqlite3.OperationalError:
            logging.error("TABLE %s.table_exists()" % tablename)
            raise sqlite3.OperationalError
            return False
        else:
            return result


    def table_view(self, tablename):
        try:
            #TODO: also I could check if the table is empty
            if self.table_exists(tablename):
#                cursor_l = self.conn.execute("""SELECT * FROM %s ORDER BY rowid;""" % (tablename))
                cursor_l = self.conn.execute("""SELECT * FROM %s;""" % (tablename))
                if cursor_l:
                    for cursor in cursor_l:
                        print cursor
                else:
                    print 'TABLE "%s" EMPTY' % tablename
            else:
                logging.warning("%s.table_view(): table %s not found" % tablename)
        except sqlite3.OperationalError:
            logging.error("%s.table_view()" % tablename)
            raise sqlite3.OperationalError
        else:
            pass

    # =============================================================================
    # TABLE ENTRY FUNCTIONS
    # =============================================================================
    def get_platform_id(self, platform, aux_info):
#        self.c.execute("SELECT platform_id FROM platforms WHERE platform=? AND aux_info=?",(platform, aux_info))
        self.cursor.execute("SELECT platform_id FROM platforms WHERE platform=?", (platform,))
        result=self.cursor.fetchone()[0]
        logging.debug("Platform %s has ID %d",(platform, aux_info),result)
        return result

    def add_platform(self, platform, aux_info=""):
        try:
            return self.get_platform_id(platform, aux_info)
        except TypeError:
            self.cursor.execute("INSERT INTO platforms(platform,aux_info) VALUES (?,?)",(platform,aux_info))
            logging.debug("Created platform record for %s...",(platform, aux_info))
            return self.get_platform_id(platform, aux_info)

    def get_testinfo_id(self, testid, rat):
        self.cursor.execute("SELECT testinfo_id FROM testinfos WHERE testid=? AND rat=?", (testid, rat))
        result=self.cursor.fetchone()[0]
        #if result is None:
        #    logging.debug("Testinfo not found");
        #else:
        logging.debug("testid %s on rat %s, has ID %d", testid, rat, result)
        return result

    def add_testinfo(self, testid, descr, rat):
        try:
            return self.get_testinfo_id(testid, rat)
        except TypeError:
            self.cursor.execute("INSERT INTO testinfos(testid, rat, descr) VALUES (?,?,?)", (testid, rat, descr))
            logging.debug("Created testinfo record for %s...",(testid, rat, descr))
            return self.get_testinfo_id(testid, rat)

    def get_testrun_id(self, timestamp, branch, clnum, mod_files):
        self.cursor.execute("SELECT testrun_id FROM testruns WHERE timestamp=? AND branch=? AND clnum=? AND mod_files=?", (timestamp, branch, clnum, mod_files))
        result=self.cursor.fetchone()[0]
        logging.debug("Test run %s has ID %d",(timestamp, branch, clnum, mod_files), result)
        return result

    def add_testrun(self, timestamp, branch, clnum, mod_files):
        try:
            return self.get_testrun_id(timestamp, branch, clnum, mod_files)
        except TypeError:
            logging.debug("Create testrun record for %s", (timestamp, branch, clnum, mod_files))
            self.cursor.execute("INSERT INTO testruns(timestamp, branch, clnum, mod_files) VALUES (?,?,?,?)",(timestamp, branch, clnum, mod_files))
            return self.get_testrun_id(timestamp, branch, clnum, mod_files)

    def get_param_id (self, testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart):
        self.cursor.execute("""SELECT param_id FROM params WHERE testinfo_id=? AND rfband=? AND earfcn=? AND bwmhz=? AND chtype=? AND snr=? AND rsepre=?
                            AND pa=? AND pb=? AND tm=? AND txants=? AND pmi=? AND schedtype=? AND dlmcs=? AND dlnprb=? AND dlrbstart=? AND ulmcs=? AND ulnprb=? AND ulrbstart=?""",
                            (testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
        result=self.cursor.fetchone()[0]
        logging.debug("Param set %s has ID %d",(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart), result)
        return result

    def add_param_set (self, testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart):
        try:
            return self.get_param_id(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)
        except TypeError:
            logging.debug("Creating record for param set %s",(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
            self.cursor.execute("INSERT INTO params(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart))
            return self.get_param_id(testinfo_id, rfband, earfcn, bwmhz, chtype, snr, rsepre, pa, pb, tm, txants, pmi, schedtype, dlmcs, dlnprb, dlrbstart, ulmcs, ulnprb, ulrbstart)

    def get_result_id (self, testrun_id, platform_id, param_id):
        self.cursor.execute("SELECT result_id FROM results WHERE testrun_id=? AND platform_id=? AND param_id=?",
                                                   (testrun_id,platform_id,param_id))
        result=self.cursor.fetchone()[0]
        logging.debug("Result for testrun_id %d, platform_id %d, param_id %d has ID %d", testrun_id, platform_id, param_id, result)
        return result


    def add_result(self, testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, current_mA, rirely, numRI1, numRI2):
        try:
            return self.get_result_id(testrun_id,platform_id,param_id)
        except TypeError:
            logging.debug("Creating result record for testrun_id %d, platform_id %d, param_id %d", testrun_id, platform_id, param_id)
            self.cursor.execute("INSERT INTO results(testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, current_mA, rirely, numRI1, numRI2) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (testrun_id, platform_id, param_id, valid, dlrely, dlthr, dlbler, cqi, ack, nack, dtx, sf_total, sf_scheduled, ulrely, ulthr, ulbler, crc_pass, crc_fail, current_mA, rirely, numRI1, numRI2))
            return self.get_result_id(testrun_id, platform_id, param_id)

    # =============================================================================
    # WCDMA Tests specific - TABLE ENTRY FUNCTIONS
    # =============================================================================

    def get_wcdma_bler_perf_test_param_id (self, testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant):
        self.cursor.execute("""SELECT w_param_id FROM wcdma_params WHERE testinfo_id=? AND rfband=? AND uarfcn=? AND chtype=? AND datarate=? AND snr=? AND power=?
                            AND txant=?""",
                            (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant))
        result=self.cursor.fetchone()[0]
        logging.debug("WCDMA Param set %s has ID %d",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant), result)
        return result

    def add_wcdma_bler_perf_test_param_set (self, testinfo_id, idx, table_entries):
        rfband      = table_entries['RFBAND'][idx]
        uarfcn      = table_entries['UARFCN'][idx]
        chtype      = table_entries['CHTYPE'][idx]
        datarate    = table_entries['DATARATE'][idx]
        snr         = table_entries['SNR'][idx]
        power       = table_entries['POWER'][idx]
        txant       = table_entries['TXANTS'][idx]
        try:
            return self.get_wcdma_bler_perf_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant)
        except TypeError:
            logging.debug("Creating record for wcdma_params set %s",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant))
            self.cursor.execute("INSERT INTO wcdma_params(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant) VALUES (?,?,?,?,?,?,?,?)",
                      (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant))
            return self.get_wcdma_bler_perf_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant)


    def get_wcdma_result_id (self, testrun_id, platform_id, w_param_id):
        self.cursor.execute("SELECT result_id FROM wcdma_results WHERE testrun_id=? AND platform_id=? AND w_param_id=?",
                                                   (testrun_id, platform_id, w_param_id))
        result=self.cursor.fetchone()[0]
        logging.debug("Result for testrun_id %d, platform_id %d, w_param_id %d has ID %d", testrun_id, platform_id, w_param_id, result)
        return result


    def add_wcdma_bler_perf_test_result(self, testrun_id, platform_id, w_param_id, idx, table_entries):
        try:
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)
        except TypeError:
            dlrely              = table_entries['DLRELY'][idx]
            dl_ber              = table_entries['BER'][idx]
            dl_bler             = table_entries['DLBLER'][idx]
            lost_blocks         = table_entries['LOSTBLOCKS'][idx]
            pdn_discontinuity   = table_entries['PNDiscontinuity'][idx]
            dl_verdict          = table_entries['DL VERDICT'][idx]
            try:
                i_min               = table_entries['Imin[mA]'][idx]
                i_avg               = table_entries['Iavrg[mA]'][idx]
                i_max               = table_entries['Imax[mA]'][idx]
                i_deviation         = table_entries['Ideviation'][idx]
                pwr_min             = table_entries['PWRmin[mW]@3.8V'][idx]
                pwr_avg             = table_entries['PWRavrg[mW]@3.8V'][idx]
                pwr_max             = table_entries['PWRmax[mW]@3.8V'][idx]
            except IndexError:
                logging.debug('Power measurements set to default values as these could not be determined!')
                i_min               = CURRENT_MEAS_NOT_APPL
                i_avg               = CURRENT_MEAS_NOT_APPL
                i_max               = CURRENT_MEAS_NOT_APPL
                i_deviation         = CURRENT_MEAS_NOT_APPL
                pwr_min             = POWER_MEAS_NOT_APPL
                pwr_avg             = POWER_MEAS_NOT_APPL
                pwr_max             = POWER_MEAS_NOT_APPL

            logging.debug("Creating wcdma_results record for testrun_id %d, platform_id %d, w_param_id %d", testrun_id, platform_id, w_param_id)
            self.cursor.execute("INSERT INTO wcdma_results(testrun_id, platform_id, w_param_id, dlrely, dl_ber, dl_bler, lost_blocks, pdn_discontinuity, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (testrun_id, platform_id, w_param_id, dlrely, dl_ber, dl_bler, lost_blocks, pdn_discontinuity, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max))
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)

    def get_wcdma_hspa_test_param_id (self, testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes):
        self.cursor.execute("""SELECT w_param_id FROM wcdma_params WHERE testinfo_id=? AND rfband=? AND uarfcn=? AND chtype=? AND datarate=? AND snr=? AND power=?
                            AND txant=? AND sched_type=? AND modulation=? AND ki=? AND num_hsdsch_codes=?""",
                            (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes))
        result=self.cursor.fetchone()[0]
        logging.debug("WCDMA HSPA Param set %s has ID %d",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes), result)
        return result

    def add_wcdma_hspa_test_param_set (self, testinfo_id, idx, table_entries):
        rfband              = table_entries['RFBAND'][idx]
        uarfcn              = table_entries['UARFCN'][idx]
        chtype              = table_entries['CHTYPE'][idx]
        datarate            = table_entries['DATARATE'][idx]
        snr                 = table_entries['SNR'][idx]
        power               = table_entries['POWER'][idx]
        txant               = table_entries['TXANTS'][idx]
        sched_type          = table_entries['SCHEDTYPE'][idx]
        modulation          = table_entries['MODULATION'][idx]
        ki                  = table_entries['Ki'][idx]
        num_hsdsch_codes    = table_entries['NUM_HSDSCH_CODES'][idx]

        try:
            return self.get_wcdma_hspa_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes)
        except TypeError:
            logging.debug("Creating record for wcdma HSPA params set %s",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes))
            self.cursor.execute("INSERT INTO wcdma_params(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                      (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes))
            return self.get_wcdma_hspa_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes)

    def add_wcdma_hspa_test_result(self, testrun_id, platform_id, w_param_id, idx, table_entries):
        try:
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)
        except TypeError:
            num_sf              = table_entries['NSF'][idx]
            dl_target_thput     = table_entries['TARGET Tput(Mbps)'][idx]
            dl_thput            = table_entries['DL_TPUT(Mbps)'][idx]
            tol                 = table_entries['TOL(%)'][idx]
            cqi                 = table_entries['CQI'][idx]
            sent                = table_entries['SENT(%)'][idx]
            ack                 = table_entries['ACK(%)'][idx]
            nack                = table_entries['NACK(%)'][idx]
            dtx                 = table_entries['DTX(%)'][idx]
            dl_bler             = table_entries['DL_BLER'][idx]
            dl_verdict          = table_entries['DL VERDICT'][idx]
            try:
                i_min               = table_entries['Imin[mA]'][idx]
                i_avg               = table_entries['Iavrg[mA]'][idx]
                i_max               = table_entries['Imax[mA]'][idx]
                i_deviation         = table_entries['Ideviation'][idx]
                pwr_min             = table_entries['PWRmin[mW]@3.8V'][idx]
                pwr_avg             = table_entries['PWRavrg[mW]@3.8V'][idx]
                pwr_max             = table_entries['PWRmax[mW]@3.8V'][idx]
            except IndexError:
                logging.debug('Power measurements set to default values as these could not be determined!')
                i_min               = CURRENT_MEAS_NOT_APPL
                i_avg               = CURRENT_MEAS_NOT_APPL
                i_max               = CURRENT_MEAS_NOT_APPL
                i_deviation         = CURRENT_MEAS_NOT_APPL
                pwr_min             = POWER_MEAS_NOT_APPL
                pwr_avg             = POWER_MEAS_NOT_APPL
                pwr_max             = POWER_MEAS_NOT_APPL

            logging.debug("Creating wcdma HSPA results record for testrun_id %d, platform_id %d, w_param_id %d", testrun_id, platform_id, w_param_id)
            self.cursor.execute("INSERT INTO wcdma_results(testrun_id, platform_id, w_param_id, dl_bler, num_sf, dl_target_thput, dl_thput, tol, cqi, sent, ack, nack, dtx, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (testrun_id, platform_id, w_param_id, dl_bler, num_sf, dl_target_thput, dl_thput, tol, cqi, sent, ack, nack, dtx, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max))
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)

    def get_wcdma_dc_hspa_test_param_id (self, testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2):
        self.cursor.execute("""SELECT w_param_id FROM wcdma_params WHERE testinfo_id=? AND rfband=? AND uarfcn=? AND chtype=? AND datarate=? AND snr=? AND power=?
                            AND txant=? AND sched_type=? AND modulation=? AND ki=? AND num_hsdsch_codes=? AND snr_2=? AND power_2=? AND modulation_2=? AND ki_2=? AND num_hsdsch_codes_2=?""",
                            (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2))
        result=self.cursor.fetchone()[0]
        logging.debug("WCDMA DC HSPA Param set %s has ID %d",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2), result)
        return result

    def add_wcdma_dc_hspa_test_param_set (self, testinfo_id, idx, table_entries):
        rfband              = table_entries['RFBAND'][idx]
        uarfcn              = table_entries['UARFCN'][idx]
        chtype              = table_entries['CHTYPE'][idx]
        datarate            = table_entries['DATARATE'][idx]
        snr                 = table_entries['SNR'][idx]
        power               = table_entries['POWER'][idx]
        txant               = table_entries['TXANTS'][idx]
        sched_type          = table_entries['SCHEDTYPE'][idx]
        modulation          = table_entries['MODULATION'][idx]
        ki                  = table_entries['Ki'][idx]
        num_hsdsch_codes    = table_entries['NUM_HSDSCH_CODES'][idx]
        snr_2               = table_entries['SNR_2'][idx]
        power_2             = table_entries['POWER_2'][idx]
        modulation_2        = table_entries['MODULATION_2'][idx]
        ki_2                = table_entries['Ki_2'][idx]
        num_hsdsch_codes_2  = table_entries['NUM_HSDSCH_CODES_2'][idx]

        try:
            return self.get_wcdma_dc_hspa_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2)
        except TypeError:
            logging.debug("Creating record for wcdma DC HSPA params set %s",(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2))
            self.cursor.execute("INSERT INTO wcdma_params(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2))
            return self.get_wcdma_dc_hspa_test_param_id(testinfo_id, rfband, uarfcn, chtype, datarate, snr, power, txant, sched_type, modulation, ki, num_hsdsch_codes, snr_2, power_2, modulation_2, ki_2, num_hsdsch_codes_2)

    def add_wcdma_dc_hspa_test_result(self, testrun_id, platform_id, w_param_id, idx, table_entries):
        try:
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)
        except TypeError:
            num_sf              = table_entries['NSF'][idx]
            dl_target_thput     = table_entries['TARGET Tput(Mbps)'][idx]
            dl_thput            = table_entries['DL_TPUT(Mbps)'][idx]
            tol                 = table_entries['TOL(%)'][idx]
            cqi                 = table_entries['CQI'][idx]
            sent                = table_entries['SENT(%)'][idx]
            ack                 = table_entries['ACK(%)'][idx]
            nack                = table_entries['NACK(%)'][idx]
            dtx                 = table_entries['DTX(%)'][idx]
            dl_bler             = table_entries['DL_BLER'][idx]
            dl_verdict          = table_entries['DL VERDICT'][idx]
            try:
                i_min               = table_entries['Imin[mA]'][idx]
                i_avg               = table_entries['Iavrg[mA]'][idx]
                i_max               = table_entries['Imax[mA]'][idx]
                i_deviation         = table_entries['Ideviation'][idx]
                pwr_min             = table_entries['PWRmin[mW]@3.8V'][idx]
                pwr_avg             = table_entries['PWRavrg[mW]@3.8V'][idx]
                pwr_max             = table_entries['PWRmax[mW]@3.8V'][idx]
            except IndexError:
                logging.debug('Power measurements set to default values as these could not be determined!')
                i_min               = CURRENT_MEAS_NOT_APPL
                i_avg               = CURRENT_MEAS_NOT_APPL
                i_max               = CURRENT_MEAS_NOT_APPL
                i_deviation         = CURRENT_MEAS_NOT_APPL
                pwr_min             = POWER_MEAS_NOT_APPL
                pwr_avg             = POWER_MEAS_NOT_APPL
                pwr_max             = POWER_MEAS_NOT_APPL
            dl_target_thput_2   = table_entries['TARGET Tput_2(Mbps)'][idx]
            dl_thput_2          = table_entries['DL_TPUT_2(Mbps)'][idx]
            cqi_2               = table_entries['CQI_2'][idx]
            sent_2              = table_entries['SENT_2(%)'][idx]
            ack_2               = table_entries['ACK_2(%)'][idx]
            nack_2              = table_entries['NACK_2(%)'][idx]
            dtx_2               = table_entries['DTX_2(%)'][idx]
            dl_bler_2           = table_entries['DL_BLER_2'][idx]

            logging.debug("Creating wcdma DC HSPA results record for testrun_id %d, platform_id %d, w_param_id %d", testrun_id, platform_id, w_param_id)
            self.cursor.execute("INSERT INTO wcdma_results(testrun_id, platform_id, w_param_id, dl_bler, num_sf, dl_target_thput, dl_thput, tol, cqi, sent, ack, nack, dtx, dl_target_thput_2, dl_thput_2, dl_bler_2, cqi_2, sent_2, ack_2, nack_2, dtx_2, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (testrun_id, platform_id, w_param_id, dl_bler, num_sf, dl_target_thput, dl_thput, tol, cqi, sent, ack, nack, dtx, dl_target_thput_2, dl_thput_2, dl_bler_2, cqi_2, sent_2, ack_2, nack_2, dtx_2, dl_verdict, i_min, i_avg, i_max, i_deviation, pwr_min, pwr_avg, pwr_max))
            return self.get_wcdma_result_id(testrun_id, platform_id, w_param_id)


    def __str__(self):
        print "---------------------------------------"
        print "  db_file                     : %s" % self.name
        print "  conn                        : %s" % self.conn
        print "  cursor                      : %s" % self.cursor
        return ""


if __name__ == '__main__':

    from pl1_testbench_framework.common.config.cfg_multilogging import cfg_multilogging

    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)

    t0=time.localtime()

    # Define folders hierarchy
    root_dir           =os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['wcdma'])
    database_dir       =os.sep.join(root_dir.split(os.sep)[:]+['report','sqllite', 'database'])
    equery_dir         =os.sep.join(root_dir.split(os.sep)[:]+['report','sqllite', 'database'])
    log_file           =os.sep.join(root_dir.split(os.sep)[:]+['report','sqllite', 'database','perf_bestscore_db.LOG'])
    db_file            =os.sep.join(database_dir.split(os.sep)[:]+['perf_bestscore.db'])


    #logger=cfg_logger_root('DEBUG', log_file)
    print("FOLDER HIERARCHY  :")
    print("------------------------------------")
    print("root_dir          : %s" % root_dir)
    print("database_dir      : %s" % database_dir)
    print("export_dir        : %s" % equery_dir)
    print("FILES         :")
    print("------------------------------------")
    print("log_file           : %s " % log_file)
    print("db_file            : %s"  % db_file)


    logger_test=logging.getLogger('run_DB_Test')
    logger_test.debug("TEST.......DB.")

    if 0:
        print("DB SCHEMA    :")
        db_h=results_db(db_file)
        cursor_l = db_h.conn.execute("""SELECT tbl_name, sql from sqlite_master where type='table' AND tbl_name!='sqlite_sequence';""")
        #cursor_l = db_h.cursor.execute(".tables")
        if cursor_l:
            for cursor in cursor_l:
                print 'TABLE: %s, SCHEME: %s' % (cursor[0], cursor[1])
        else:
            print 'TABLES "%s" EMPTY' % tablename
        db_h.disconnect()
        del db_h

    if 0:
        print ">> Check table existence"
        print "---------------------------------------"
        db_h=results_db(db_file)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_PLATFORMS, db_h.table_exists(db_h.TABLE_PLATFORMS))
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_TESTINFOS, db_h.table_exists(db_h.TABLE_TESTINFOS))
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_PARAMS, db_h.table_exists(db_h.TABLE_PARAMS))
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_TESTRUNS, db_h.table_exists(db_h.TABLE_TESTRUNS))
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_RESULTS, db_h.table_exists(db_h.TABLE_RESULTS))
        db_h.disconnect()
        del db_h

    if 0:
        print ">> Check table view"
        print "---------------------------------------"
        db_h=results_db(db_file)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_PLATFORMS, db_h.table_exists(db_h.TABLE_PLATFORMS))
        db_h.table_view(db_h.TABLE_PLATFORMS)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_TESTINFOS, db_h.table_exists(db_h.TABLE_TESTINFOS))
        db_h.table_view(db_h.TABLE_TESTINFOS)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_PARAMS, db_h.table_exists(db_h.TABLE_PARAMS))
        db_h.table_view(db_h.TABLE_PARAMS)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_TESTRUNS, db_h.table_exists(db_h.TABLE_TESTRUNS))
        db_h.table_view(db_h.TABLE_TESTRUNS)
        print 'TABLE "%s" exists? %s' % (db_h.TABLE_RESULTS, db_h.table_exists(db_h.TABLE_RESULTS))
        db_h.table_view(db_h.TABLE_RESULTS)
        db_h.disconnect()
        del db_h

    if 0:
        print ">> Export entire database into CSV file"
        EQUERY_DATABASE=re.sub('[ |\t|\n]+',' ', r"""SELECT * FROM results
                INNER JOIN platforms ON results.platform_id=platforms.platform_id
                INNER JOIN testruns ON results.testrun_id=testruns.testrun_id
                INNER JOIN params ON results.param_id=params.param_id
                INNER JOIN testinfos ON params.testinfo_id=testinfos.testinfo_id;""")
        EQUERY_DATABASE_FILE= os.sep.join(equery_dir.split(os.sep)[:]+['equery_database.csv'])
        DB_export_to_file(dbname=db_file, equery=EQUERY_DATABASE, filename=EQUERY_DATABASE_FILE)

    if 0:

        print ">> Retrieve best score for a selected test"
        EQUERY_BESTSCORE=re.sub('[ |\t|\n]+',' ', r"""SELECT branch,clnum,MAX(dlthr) FROM results
                INNER JOIN platforms ON results.platform_id=platforms.platform_id
                INNER JOIN testruns ON results.testrun_id=testruns.testrun_id
                INNER JOIN params ON results.param_id=params.param_id
                INNER JOIN testinfos ON params.testinfo_id=testinfos.testinfo_id
                WHERE branch=='teams/phy/pl1_dev.br'
                    AND bwmhz==10
                    AND chtype=='None'
                    AND snr==30
                    AND rsepre==-60
                    AND pa==0
                    AND pb==1
                    AND tm==3
                    AND txants==2
                    AND pmi==0
                    AND schedtype=='FIXED'
                    AND dlmcs==28
                    AND dlnprb==50
                    AND dlrbstart==0
                    AND ulmcs==23
                    AND ulnprb==50
                    AND ulrbstart==0;""")
        EQUERY_BESTSCORE_FILE= os.sep.join(equery_dir.split(os.sep)[:]+['equery_bestscore.csv'])
        #DB_export_to_file(dbname=db_file, equery=EQUERY_BESTSCORE, filename=EQUERY_BESTSCORE_FILE)
        branch,clnum,score = DB_export_bestscore(dbname=db_file, equery=EQUERY_BESTSCORE)
        print branch
        print clnum
        print score

    if 1:
        print ">> DB_W_import_from_file_meas ....."
        filename = "/home/jsorathia/Perforce/jsorathia_ubuntu_812/software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_wcdma_testbench/results/20140619_153904_WCDMA_TestReport/WCDMA_CMW500_TestReport_testID_0_testType_BLER_PERF.csv"
        DB_wcdma_import_from_file_meas (db_file, filename=filename, testType='BLER_PERF')

        filename = "/home/jsorathia/Perforce/jsorathia_ubuntu_812/software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_wcdma_testbench/results/20140619_153904_WCDMA_TestReport/WCDMA_CMW500_TestReport_testID_1_testType_HSPA_BLER_PERF.csv"
        DB_wcdma_import_from_file_meas (db_file, filename=filename, testType='HSPA_BLER_PERF')
        #filename = "/home/jsorathia/Perforce/jsorathia_ubuntu_812/software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_wcdma_testbench/results/20140619_153904_WCDMA_TestReport/WCDMA_CMW500_TestReport_testID_2_testType_DCHSDPA_BLER_PERF.csv"
        filename = "/home/jsorathia/Perforce/jsorathia_ubuntu_812/software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_wcdma_testbench/results/20140703_115009_WCDMA_TestReport/WCDMA_CMW500_TestReport_testID_2_testType_DCHSDPA_BLER_PERF.csv"
        DB_wcdma_import_from_file_meas (db_file, filename=filename, testType='DCHSDPA_BLER_PERF')


    t1=time.localtime()
    dt=time.mktime(t1)-time.mktime(t0)                             # Compute duration [sec]
    logging.info("Time duration %d[sec]" % dt)






