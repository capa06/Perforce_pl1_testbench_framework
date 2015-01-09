'''
Created on 28 Nov 2013

@author: jlucas, fsaracino
'''

import os, sys, logging, time, re, bz2
import MySQLdb as mydb



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

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'mysql']))

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'instr']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['lte', 'common', 'struct']))


 
# =============================================================================
# IMPORT USER DEFINED LIBRARY 
# =============================================================================
from DatabaseMySqlPl1Testbench import DatabaseMySqlPl1Testbench, mySqlCheckPermission, mySqlGetVersion
from CfgError import CfgError
from CmwLte import CmwLte

from icera_utils import parseModemInfo, getBranch, getPlatform, getVariant
from StructXml import StructXml
from StructXmlMySqlInterfaceLte import StructXmlMySqlInterfaceLte




# =============================================================================
# DATABASE API FUNCTIONS 
# =============================================================================

def mysqlImportBlerResults(host, dbname, uid, pwd, configfile_txt, measfile_csv):
    logger=logging.getLogger('mysqlImportBlerResults')
    try: 
        # Get database connection object instance
        db_h=DatabaseMySqlPl1TestbenchLte(host, dbname, uid, pwd)
        
        # Open database connection                                                
        db_h.database_connect()
        
        # Call import function
        db_h.import_bler_results(configfile_txt, measfile_csv)

    except:
        if not db_h is None:
            db_h.database_disconnect()
        logger.debug("FAILED import LTE BLER measurements")
        print sys.exc_info()
        sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
    else:
        db_h.conn.commit()
        db_h.database_disconnect()
        logger.info("SUCCESS imported files : (%s, %s)" % (configfile_txt, measfile_csv))
        del db_h
    

def mysqlExportBlerResults(host, dbname, uid, pwd, exportfile_csv):
    logger=logging.getLogger('mysqlExportBlerResults')
    try: 
        # Get database connection object instance
        db_h=DatabaseMySqlPl1TestbenchLte(host, dbname, uid, pwd)
        
        # Open database connection                                                
        db_h.database_connect()
        
        # Call import function
        db_h.export_bler_results(exportfile_csv)

    except:
        if not db_h is None:
            db_h.database_disconnect()
        logger.debug("FAILED export LTE BLER measurements")
        print sys.exc_info()
        sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
    else:
        db_h.conn.commit()
        db_h.database_disconnect()
        logger.info("SUCCESS exported database to file: %s" % (exportfile_csv))
        del db_h


def mysqlSelectBestScore(host, dbname, uid, pwd, entry_s, branch, platform, carrier, varname):
    """
    Input:
       host       : database host
       dbname     : database name
       uid        : database uid
       database   : database pwd       
       entry_s    : test configuration structure
       branch     : branch name (retrieved via at%idbgtest)
       platform   : platform (retrieved via at%idbgtest)      
       carrier    : {'PCC', 'SCC'}
       varname    : {'dlthr', 'ulthr'}
    Output:
       (clnum, bestscore_Mbps)
    """
    logger=logging.getLogger('mysqlSelectBestScore')
    
    
    clnum          = None
    bestscore_Mbps = None
    
    carrier=carrier.upper()

    if not carrier in ['PCC', 'SCC']:
        logger.error("INVALID PARAMENTER: carrier %s" % carrier)
        sys.exit(CfgError.ERRCODE_SYS_PARAM_INVALID)
        
    if not varname in ['dlthr_Mbps', 'ulthr_Mbps']:
        logger.error("INVALID PARAMENTER: carrier %s" % carrier)
        sys.exit(CfgError.ERRCODE_SYS_PARAM_INVALID)
        
    try:             
        # Get database connection object instance
        db_h=DatabaseMySqlPl1TestbenchLte(host, dbname, uid, pwd)
        
        # Open database connection                                                
        db_h.database_connect()
        
        # Call import function
        res = db_h.select_best_score(entry_s, branch, platform, carrier, varname)
        clnum, bestscore_Mbps = res[0], res[1]
    except:
        if not db_h is None:
            db_h.database_disconnect()
        logger.debug("FAILED retrieving best score")
        print sys.exc_info()
        sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
    else:
        db_h.conn.commit()
        db_h.database_disconnect()
        logger.info("FOUND BESTSCORE branch=%s, platform=%s, carrier=%s: clnum=%s, %s=%s" % (branch, 
                                                                                              platform,
                                                                                              carrier, 
                                                                                              clnum,
                                                                                              varname,
                                                                                              bestscore_Mbps))
        del db_h
    
    return (clnum, bestscore_Mbps)
     
# =============================================================================
# GLOBAL VARIABLES 
# =============================================================================
CMW_LTE_SCHEDTYPE_MAP={'UDTT'  : 'FIXED',
                       'UDCH'  : 'FIXED',
                        'CQI'  : 'AMC',
                        'FIXED': 'FIXED',
                          'AMC': 'AMC'}



# =============================================================================
# DATABASE STRUCTURE FOR LTE PERFORMANCE MEASUREMENTS 
# =============================================================================
class DatabaseMySqlPl1TestbenchLte(DatabaseMySqlPl1Testbench):
    
    def __init__ (self, host, dbname, uid, pwd):
        
        DatabaseMySqlPl1Testbench.__init__(self, host, dbname, uid, pwd)
        
        self.mysql_entry_s=StructXmlMySqlInterfaceLte(struct_name='mysql_entry_s')

        # Initialise key to table map
        self._key2table_map={}
        
        # Initialise table primary keys
        self.platform_id  = None
        self.testinfo_id  = None
        self.testrun_id   = None
        self.param_id     = None
        self.param_pcc_id = None
        self.result_id    = None
        
        #Initialise strings
        self.lte_params_args_str   = ', '.join(["%s" % x for x in self.mysql_entry_s.table_lte_params.get_fieldname_list()])
        self.lte_params_frmt_str   =  '%s,'*(len(self.mysql_entry_s.table_lte_params.get_fieldname_list())-1)+'%s'
        self.lte_params_values_str = ', '.join(["self.mysql_entry_s.table_lte_params.%s" % x for x in self.mysql_entry_s.table_lte_params.get_fieldname_list()])
        
        self.lte_results_args_str   = ', '.join(["%s" % x for x in self.mysql_entry_s.table_lte_results.get_fieldname_list()])
        self.lte_results_frmt_str   =  '%s,'*(len(self.mysql_entry_s.table_lte_results.get_fieldname_list())-1)+'%s'
        self.lte_results_values_str = ', '.join(["self.mysql_entry_s.table_lte_results.%s" % x for x in self.mysql_entry_s.table_lte_results.get_fieldname_list()])
        
        
    # =============================================================================
    # PRIVATE METHODS
    # =============================================================================
    def _set_key2table_map(self, key_l):
        logger=logging.getLogger('_set_key2table_map')
        for field in key_l:
            if field in self.mysql_entry_s.table_platforms.get_fieldname_list():
                #self._key2table_map[field] = ("mysql_entry_s.table_platforms.%s" % field)
                self._key2table_map[field] = ("self.mysql_entry_s.table_platforms")
            
            elif field in self.mysql_entry_s.table_testinfos.get_fieldname_list():
                #self._key2table_map[field] = ("mysql_entry_s.table_testinfos.%s" % field)
                self._key2table_map[field] = ("self.mysql_entry_s.table_testinfos")
    
            elif field in self.mysql_entry_s.table_testruns.get_fieldname_list():
                #self._key2table_map[field] = ("mysql_entry_s.table_testruns.%s" % field)
                self._key2table_map[field] = ("self.mysql_entry_s.table_testruns")
    
            elif field in self.mysql_entry_s.table_lte_params.get_fieldname_list():
                #self._key2table_map[field] = ("mysql_entry_s.table_lte_params.%s" % field)
                self._key2table_map[field] = ("self.mysql_entry_s.table_lte_params")
    
            elif field in self.mysql_entry_s.table_lte_results.get_fieldname_list():
                #self._key2table_map[field] = ("mysql_entry_s.table_lte_results.%s" % field)
                self._key2table_map[field] = ("self.mysql_entry_s.table_lte_results")
            else:
                self._key2table_map[field] = None
                logger.warning("Field not mapped : %s" % field)
    
        

    # *****************************************************************************#
    #  FUNCTIONS FOR READING THE FILES TO IMPORT                                   #
    # *****************************************************************************#    
    def _search_pattern(self, regxp, msg):
        if regxp.search(msg):
            res=regxp.findall(msg)
            return res[0]
        else:
            return None


    def _import_ltebler_config_from_txt(self, fname):
        logger=logging.getLogger('import_ltebler_config_from_txt')
        # Check file existence
        if not os.path.isfile(fname):
            logger.error("FILE NOT FOUND: %s" % fname)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)
        # Parse info
        try:
            fd = open(fname, "r")
            testconfig = fd.read()
            fd.close()
        except:
            logger.error("Cannot access file :%s" % fname)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)    
        else:
            if 0: 
                logger.debug("testconfig : %s" % testconfig)
            
            # Update platform 
            self.mysql_entry_s.table_platforms.platform  = self._search_pattern(re.compile(r".*Platform\s*:\s*(.*?)\s+"), testconfig)              
            self.mysql_entry_s.table_platforms.aux_info  = None  
            
            # Update testinfo
            self.mysql_entry_s.table_testinfos.testid   = self._search_pattern(re.compile(r".*testid\s*:\s*(\d*)"), testconfig)
            self.mysql_entry_s.table_testinfos.rat      = self._search_pattern(re.compile(r".*rat\s*:\s*(.*)"), testconfig)
            self.mysql_entry_s.table_testinfos.testtype = self._search_pattern(re.compile(r".*testtype\s*:\s*(.*)"), testconfig)
            self.mysql_entry_s.table_testinfos.descr    = self._search_pattern(re.compile(r".*descr\s*:\s*(.*)"), testconfig)
             
            #Update testruns
            self.mysql_entry_s.table_testruns.timestamp  = self._search_pattern(re.compile(r".*timestamp\s*:\s*(.*)"), testconfig)

            self.mysql_entry_s.table_testruns.branch     = self._search_pattern(re.compile(r".*Branch name\s*:\s*(.*)"), testconfig)
            if (not self.mysql_entry_s.table_testruns.branch is None) and (self.mysql_entry_s.table_testruns.branch[0:3] == "css"):
                # Decode string
                self.mysql_entry_s.table_testruns.branch=parseModemInfo(self.mysql_entry_s.table_testruns.branch)
            
            self.mysql_entry_s.table_testruns.clnum      = self._search_pattern(re.compile(r".*Changelist\s*:\s*CL(\d*)"), testconfig)
            self.mysql_entry_s.table_testruns.mod_files  = self._search_pattern(re.compile(r".*Number of modified files\s*:\s*(\d*)"), testconfig)
            self.mysql_entry_s.table_testruns.p4webrev   = self._search_pattern(re.compile(r".*P4webrev\s*:\s*(.*)"), testconfig)
            self.mysql_entry_s.table_testruns.testerinfo = self._search_pattern(re.compile(r".*tester_info\s*:\s*(.*)"), testconfig)

            self.mysql_entry_s.table_testruns.modeminfo  = None
             
            if 0:
                self.mysql_entry_s.struct_log()
                raw_input("Check config initialisation in mysql interface and press [ENTER]")
        

    def _import_ltebler_meas_from_csv(self, fname):
        logger=logging.getLogger('import_ltebler_meas_from_csv')
        
        # Check file existence
        if not os.path.isfile(fname):
            logger.error("FILE NOT FOUND: %s" % fname)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        # Open file
        config_saved = 0 
        with open(fname, 'r') as fd:
          
            # Process header
            line=fd.readline() 
            if line == "" :
                logger.warning("Empty file: %s" % fname)
                return 1
            
            # Create a list and remove any special character and space from the keys value
            key_l = [re.sub('[\n\t\r]', '' , x.strip()) for x in line.split(',')]
            if 0: logger.debug("key_l : %s" % key_l)
            
            # Map keys onto the interface structure 
            self._set_key2table_map(key_l)
    
            # Process measurements
            while True:
                line=fd.readline() 
                if line == "" : break
                
                # We are sure at least one measuremenst is present before storing the test configuration
                if not config_saved:
                    # Store test configuration info
                    self._write_database_config_entry()
                    config_saved=1
                    
                # Create a list and remove any special character and leading space from the values
                value_l = [re.sub('[\n\t\r]', '' , x.lstrip()) for x in line.split(',')]
                    
                # Create TLV list, 
                tlv_list = zip(key_l, value_l)
                
                # Set database structure interface
                self._set_database_entry(tlv_list)

                # Store BLER test measurements
                self._write_database_meas_entry()

            # Committ modifications            
            self._database_committ()
                
        return 0


    def _import_database_from_csv(self, fname):
        logger=logging.getLogger('import_database_from_csv')
        
        # Check file existence
        if not os.path.isfile(fname):
            logger.error("FILE NOT FOUND: %s" % fname)
            sys.exit(CfgError.ERRCODE_SYS_FILE_IO)

        # Open file
        with open(fname, 'r') as fd:
          
            # Process header
            line=fd.readline() 
            if line == "" :
                logger.warning("Empty file: %s" % fname)
                return 1
            
            # Create a list and remove any special character and space from the keys value
            key_l = [re.sub('[\n\t\r]', '' , x.strip()) for x in line.split(',')]
            if 0: logger.debug("key_l : %s" % key_l)
            
            # Map keys onto the interface structure 
            self._set_key2table_map(key_l)
    
            # Process measurements
            while True:
                line=fd.readline() 
                if line == "" : break
                
                    
                # Create a list and remove any special character and leading space from the values
                value_l = [re.sub('[\n\t\r]', '' , x.lstrip()) for x in line.split(',')]
                    
                # Create TLV list, 
                tlv_list = zip(key_l, value_l)
                
                # Set database structure interface
                self._set_database_entry(tlv_list)

                # Store test configuration info
                self._write_database_config_entry()

                #Store BLER test measurements
                self._write_database_meas_entry()
                
            # Committ modifications            
            self._database_committ()
                
        return 0


    def _set_database_entry(self, tlv_l):
        """
        tlv_l = [(tag, val)]
        """
        logger=logging.getLogger('._entry_format')
                
        if 1: 
            logger.debug("tlv_l : %s" % tlv_l)
        
        for idx in range(len(tlv_l)):
            tag, val = tlv_l[idx][0], tlv_l[idx][1]
            if not self._key2table_map[tag] is None:
                setattr(eval(self._key2table_map[tag]), tag, val)
            else:
                logger.warning("discarded not mapped tag : %s" % tag)           
        if 0:
            self.mysql_entry_s.struct_log()
            raw_input("Check entry in mysql interface and press [ENTER]")
            

    def _parse_meas_entry(self):
        #logger=logging.getLogger('_parse_meas_entry')
        
        # Parse LTE params
        self.mysql_entry_s.table_lte_params.carrier = self.mysql_entry_s.table_lte_params.carrier.upper()
        self.mysql_entry_s.table_lte_params.dmode = self.mysql_entry_s.table_lte_params.dmode.upper()
        try: 
            self.mysql_entry_s.table_lte_params.dlulconf = int(self.mysql_entry_s.table_lte_params.dlulconf)
            self.mysql_entry_s.table_lte_params.ssconf = int(self.mysql_entry_s.table_lte_params.ssconf)
        except:
            self.mysql_entry_s.table_lte_params.dlulconf = None
            self.mysql_entry_s.table_lte_params.ssconf = None

        self.mysql_entry_s.table_lte_params.bwmhz = float(self.mysql_entry_s.table_lte_params.bwmhz)
        self.mysql_entry_s.table_lte_params.earfcn = int(self.mysql_entry_s.table_lte_params.earfcn)
        self.mysql_entry_s.table_lte_params.cp = self.mysql_entry_s.table_lte_params.cp.upper() 
        self.mysql_entry_s.table_lte_params.tm = int(self.mysql_entry_s.table_lte_params.tm)
        self.mysql_entry_s.table_lte_params.txants = int(self.mysql_entry_s.table_lte_params.txants)
            
        try:
            self.mysql_entry_s.table_lte_params.pmi = int(self.mysql_entry_s.table_lte_params.pmi)                  
        except:
            self.mysql_entry_s.table_lte_params.pmi = None
                
        self.mysql_entry_s.table_lte_params.rsepre = float(self.mysql_entry_s.table_lte_params.rsepre)
        self.mysql_entry_s.table_lte_params.pa = int(self.mysql_entry_s.table_lte_params.pa)
        self.mysql_entry_s.table_lte_params.pb = int(self.mysql_entry_s.table_lte_params.pb)
            
        if self.mysql_entry_s.table_lte_params.chtype in CmwLte.CMW_LTE_FADING_CHANNELS:
            self.mysql_entry_s.table_lte_params.chtype = CmwLte.CMW_LTE_FADING_CHANNELS_TO_3GPP[self.mysql_entry_s.table_lte_params.chtype]
        else:
            self.mysql_entry_s.table_lte_params.chtype = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_params.chtype, re.I|re.M) else self.mysql_entry_s.table_lte_params.chtype.upper()  
        
        try:    
            self.mysql_entry_s.table_lte_params.snr = float(self.mysql_entry_s.table_lte_params.snr)                  
        except:
            self.mysql_entry_s.table_lte_params.snr = None

        try:    
            self.mysql_entry_s.table_lte_params.doppler = float(self.mysql_entry_s.table_lte_params.doppler)                  
        except:
            self.mysql_entry_s.table_lte_params.doppler = None

            
        self.mysql_entry_s.table_lte_params.schedtype = CMW_LTE_SCHEDTYPE_MAP[self.mysql_entry_s.table_lte_params.schedtype]
        
        try:
            self.mysql_entry_s.table_lte_params.nhrtx = None if int(self.mysql_entry_s.table_lte_params.nhrtx)==0 else int(self.mysql_entry_s.table_lte_params.nhrtx)                   
            self.mysql_entry_s.table_lte_params.riv = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_params.riv, re.I|re.M) else self.mysql_entry_s.table_lte_params.riv  
        except:
            self.mysql_entry_s.table_lte_params.nhrtx = None
            self.mysql_entry_s.table_lte_params.riv = None
        
        try:
            self.mysql_entry_s.table_lte_params.dlmcs = int(self.mysql_entry_s.table_lte_params.dlmcs)
        except:
            self.mysql_entry_s.table_lte_params.dlmcs = None
        try:
            self.mysql_entry_s.table_lte_params.dlnprb = int(self.mysql_entry_s.table_lte_params.dlnprb)
        except:
            self.mysql_entry_s.table_lte_params.dlnprb = None
        try:
            self.mysql_entry_s.table_lte_params.dlrbstart = int(self.mysql_entry_s.table_lte_params.dlrbstart)
        except:
            self.mysql_entry_s.table_lte_params.dlrbstart = None
        try:
            self.mysql_entry_s.table_lte_params.ulmcs = int(self.mysql_entry_s.table_lte_params.ulmcs)
        except:
            self.mysql_entry_s.table_lte_params.ulmcs = None
        try:
            self.mysql_entry_s.table_lte_params.ulnprb = int(self.mysql_entry_s.table_lte_params.ulnprb)
        except:
            self.mysql_entry_s.table_lte_params.ulnprb = None
        try:
            self.mysql_entry_s.table_lte_params.ulrbstart = int(self.mysql_entry_s.table_lte_params.ulrbstart)
        except:
            self.mysql_entry_s.table_lte_params.ulrbstart  = None

    
        # Parse LTE results
        self.mysql_entry_s.table_lte_results.valid           = int(self.mysql_entry_s.table_lte_results.valid)
        self.mysql_entry_s.table_lte_results.dlrely          = int(self.mysql_entry_s.table_lte_results.dlrely)
        self.mysql_entry_s.table_lte_results.dlthr_Mbps      = float(self.mysql_entry_s.table_lte_results.dlthr_Mbps)
        self.mysql_entry_s.table_lte_results.dlthr_min_Mbps  = float(self.mysql_entry_s.table_lte_results.dlthr_min_Mbps)
        self.mysql_entry_s.table_lte_results.dlthr_max_Mbps  = float(self.mysql_entry_s.table_lte_results.dlthr_max_Mbps)
        self.mysql_entry_s.table_lte_results.dlbler          = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.dlbler, re.I|re.M) else  float(self.mysql_entry_s.table_lte_results.dlbler) 
        self.mysql_entry_s.table_lte_results.cqi             = int(self.mysql_entry_s.table_lte_results.cqi)
        self.mysql_entry_s.table_lte_results.ack             = int(self.mysql_entry_s.table_lte_results.ack)
        self.mysql_entry_s.table_lte_results.nack            = int(self.mysql_entry_s.table_lte_results.nack)
        self.mysql_entry_s.table_lte_results.dtx             = int(self.mysql_entry_s.table_lte_results.dtx)
        self.mysql_entry_s.table_lte_results.sf_total        = int(self.mysql_entry_s.table_lte_results.sf_total)
        self.mysql_entry_s.table_lte_results.sf_scheduled    = int(self.mysql_entry_s.table_lte_results.sf_scheduled)
        
        try:
            self.mysql_entry_s.table_lte_results.ulrely      = int(self.mysql_entry_s.table_lte_results.ulrely)
        except:
            self.mysql_entry_s.table_lte_results.ulrely      = None
        try:
            self.mysql_entry_s.table_lte_results.ulthr_Mbps  = float(self.mysql_entry_s.table_lte_results.ulthr_Mbps)
        except:
            self.mysql_entry_s.table_lte_results.ulthr_Mbps  = None
        try:
            self.mysql_entry_s.table_lte_results.ulbler      = float(self.mysql_entry_s.table_lte_results.ulbler)
        except:
            self.mysql_entry_s.table_lte_results.ulbler      = None
        try:
            self.mysql_entry_s.table_lte_results.crc_pass    = int(self.mysql_entry_s.table_lte_results.crc_pass)
        except:
            self.mysql_entry_s.table_lte_results.crc_pass    = None
        try:
            self.mysql_entry_s.table_lte_results.crc_fail    = int(self.mysql_entry_s.table_lte_results.crc_fail)
        except:
            self.mysql_entry_s.table_lte_results.crc_fail    = None
                
        try:
            self.mysql_entry_s.table_lte_results.best_dlthr_Mbps  = float(self.mysql_entry_s.table_lte_results.best_dlthr_Mbps)
        except:
            self.mysql_entry_s.table_lte_results.best_dlthr_Mbps  = None  
        try:
            self.mysql_entry_s.table_lte_results.best_ulthr_Mbps  = float(self.mysql_entry_s.table_lte_results.best_ulthr_Mbps)
        except:
            self.mysql_entry_s.table_lte_results.best_ulthr_Mbps  = None
        try:
            self.mysql_entry_s.table_lte_results.tolerance        = float(self.mysql_entry_s.table_lte_results.tolerance)
        except:
            self.mysql_entry_s.table_lte_results.tolerance        = None
            
        self.mysql_entry_s.table_lte_results.verdict_dl           = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.verdict_dl, re.I|re.M) else self.mysql_entry_s.table_lte_results.verdict_dl  
        self.mysql_entry_s.table_lte_results.verdict_ul           = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.verdict_ul, re.I|re.M) else self.mysql_entry_s.table_lte_results.verdict_ul  

        try:
            self.mysql_entry_s.table_lte_results.voltage_V  = None if float(self.mysql_entry_s.table_lte_results.voltage_V)==0 else float(self.mysql_entry_s.table_lte_results.voltage_V)  
        except:
            self.mysql_entry_s.table_lte_results.voltage_V  = None  
        try:
            self.mysql_entry_s.table_lte_results.current_mA = None if float(self.mysql_entry_s.table_lte_results.current_mA)==0 else float(self.mysql_entry_s.table_lte_results.current_mA) 
        except:
            self.mysql_entry_s.table_lte_results.current_mA = None  
        try:
            self.mysql_entry_s.table_lte_results.power_mW   = None if float(self.mysql_entry_s.table_lte_results.power_mW)==0 else float(self.mysql_entry_s.table_lte_results.power_mW) 
        except:
            self.mysql_entry_s.table_lte_results.power_mW   = None  
        
        # FIXME: shall I insert the CSI/HARQ meas in the CSV file? 
        try:
            self.mysql_entry_s.table_lte_results.rank         = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.rank, re.I|re.M) else self.mysql_entry_s.table_lte_results.rank  
        except:
            self.mysql_entry_s.table_lte_results.rank         = None  
        try:
            self.mysql_entry_s.table_lte_results.dlthr_cw1    = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.dlthr_cw1, re.I|re.M) else self.mysql_entry_s.table_lte_results.dlthr_cw1  
        except:
            self.mysql_entry_s.table_lte_results.dlthr_cw1    = None
        try:
            self.mysql_entry_s.table_lte_results.dlthr_cw2    = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.dlthr_cw2, re.I|re.M) else self.mysql_entry_s.table_lte_results.dlthr_cw2  
        except:
            self.mysql_entry_s.table_lte_results.dlthr_cw2    = None
        try:
            self.mysql_entry_s.table_lte_results.cqi_cw1      = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.cqi_cw1, re.I|re.M) else self.mysql_entry_s.table_lte_results.cqi_cw1  
        except:
            self.mysql_entry_s.table_lte_results.cqi_cw1      = None
        try:
            self.mysql_entry_s.table_lte_results.cqi_cw2      = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.cqi_cw2, re.I|re.M) else self.mysql_entry_s.table_lte_results.cqi_cw2  
        except:
            self.mysql_entry_s.table_lte_results.cqi_cw2      = None
        try:
            self.mysql_entry_s.table_lte_results.pmi_ri1      = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.pmi_ri1, re.I|re.M) else self.mysql_entry_s.table_lte_results.pmi_ri1  
        except:
            self.mysql_entry_s.table_lte_results.pmi_ri1      = None
        try:
            self.mysql_entry_s.table_lte_results.pmi_ri2      = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.pmi_ri2, re.I|re.M) else self.mysql_entry_s.table_lte_results.pmi_ri2  
        except:
            self.mysql_entry_s.table_lte_results.pmi_ri2      = None
        try:
            self.mysql_entry_s.table_lte_results.harq_cw1     = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.harq_cw1, re.I|re.M) else self.mysql_entry_s.table_lte_results.harq_cw1  
        except:
            self.mysql_entry_s.table_lte_results.harq_cw1     = None
        try:
            self.mysql_entry_s.table_lte_results.harq_cw2     = None if re.match("[N|n][O|o][N|n][E|e]", self.mysql_entry_s.table_lte_results.harq_cw2, re.I|re.M) else self.mysql_entry_s.table_lte_results.harq_cw2  
        except:
            self.mysql_entry_s.table_lte_results.harq_cw2     = None



        

    # *****************************************************************************#
    #                              QUERIES                                         #
    # *****************************************************************************#    
    def _get_param_id_lte(self):
        logger=logging.getLogger('_get_param_id_lte')

        GET_QUERY  =  "SELECT param_id FROM lte_params WHERE testinfo_id='%s'" % self.mysql_entry_s.table_lte_params.testinfo_id
        GET_QUERY +=  " AND  carrier='%s'"   % self.mysql_entry_s.table_lte_params.carrier
        GET_QUERY +=  " AND  dmode='%s'"     % self.mysql_entry_s.table_lte_params.dmode
        GET_QUERY += (" AND  dlulconf='%s'"  % self.mysql_entry_s.table_lte_params.dlulconf) if not self.mysql_entry_s.table_lte_params.dlulconf  is None else " AND dlulconf is NULL"
        GET_QUERY += (" AND  ssconf='%s'"    % self.mysql_entry_s.table_lte_params.ssconf) if not self.mysql_entry_s.table_lte_params.ssconf    is None else " AND ssconf is NULL"
        GET_QUERY +=  " AND  bwmhz='%s'"     % self.mysql_entry_s.table_lte_params.bwmhz
        GET_QUERY +=  " AND  rfband='%s'"    % self.mysql_entry_s.table_lte_params.rfband
        GET_QUERY +=  " AND  earfcn='%s'"    % self.mysql_entry_s.table_lte_params.earfcn
        GET_QUERY +=  " AND  cp='%s'"        % self.mysql_entry_s.table_lte_params.cp
        GET_QUERY +=  " AND  tm='%s'"        % self.mysql_entry_s.table_lte_params.tm
        GET_QUERY +=  " AND  txants='%s'"    % self.mysql_entry_s.table_lte_params.txants
        GET_QUERY += (" AND  pmi='%s'"       % self.mysql_entry_s.table_lte_params.pmi) if not self.mysql_entry_s.table_lte_params.pmi    is None else " AND pmi is NULL"
        GET_QUERY +=  " AND  rsepre='%s'"    % self.mysql_entry_s.table_lte_params.rsepre
        GET_QUERY +=  " AND  pa='%s'"        % self.mysql_entry_s.table_lte_params.pa
        GET_QUERY +=  " AND  pb='%s'"        % self.mysql_entry_s.table_lte_params.pb
        GET_QUERY += (" AND  chtype='%s'"    % self.mysql_entry_s.table_lte_params.chtype) if not self.mysql_entry_s.table_lte_params.chtype     is None else " AND chtype is NULL"
        #GET_QUERY += (" AND  chtype='%s'"    % CmwLte.CMW_LTE_FADING_CHANNELS_TO_3GPP[self.mysql_entry_s.table_lte_params.chtype]) if not self.mysql_entry_s.table_lte_params.chtype is None else " AND chtype is NULL"
        GET_QUERY += (" AND  snr='%s'"       % self.mysql_entry_s.table_lte_params.snr) if not self.mysql_entry_s.table_lte_params.snr     is None else " AND snr is NULL"
        GET_QUERY += (" AND  doppler='%s'"   % self.mysql_entry_s.table_lte_params.doppler) if not self.mysql_entry_s.table_lte_params.doppler is None else " AND doppler is NULL"
        GET_QUERY +=  " AND  schedtype='%s'" % self.mysql_entry_s.table_lte_params.schedtype
        GET_QUERY += (" AND  nhrtx='%s'"     % self.mysql_entry_s.table_lte_params.nhrtx) if not self.mysql_entry_s.table_lte_params.nhrtx is None else " AND nhrtx is NULL"
        GET_QUERY += (" AND  riv='%s'"       % self.mysql_entry_s.table_lte_params.riv) if not self.mysql_entry_s.table_lte_params.riv is None else " AND riv is NULL"
        GET_QUERY += (" AND  dlmcs='%s'"     % self.mysql_entry_s.table_lte_params.dlmcs) if not self.mysql_entry_s.table_lte_params.dlmcs is None else " AND dlmcs is NULL"
        GET_QUERY += (" AND  dlnprb='%s'"    % self.mysql_entry_s.table_lte_params.dlnprb) if not self.mysql_entry_s.table_lte_params.dlnprb is None else " AND dlnprb is NULL"
        GET_QUERY += (" AND  dlrbstart='%s'" % self.mysql_entry_s.table_lte_params.dlrbstart) if not self.mysql_entry_s.table_lte_params.dlrbstart is None else " AND dlrbstart is NULL"
        GET_QUERY += (" AND  ulmcs='%s'"     % self.mysql_entry_s.table_lte_params.ulmcs) if not self.mysql_entry_s.table_lte_params.ulmcs is None else " AND ulmcs is NULL"
        GET_QUERY += (" AND  ulnprb='%s'"    % self.mysql_entry_s.table_lte_params.ulnprb) if not self.mysql_entry_s.table_lte_params.ulnprb is None else " AND ulnprb is NULL"
        GET_QUERY += (" AND  ulrbstart='%s'" % self.mysql_entry_s.table_lte_params.ulrbstart) if not self.mysql_entry_s.table_lte_params.ulrbstart is None else " AND ulrbstart is NULL"
        GET_QUERY += (";")      
        
        if 1: 
            logger.debug("GET_QUERY : %s" % GET_QUERY)
        
        self.cursor.execute(GET_QUERY)
        result=self.cursor.fetchone()[0]
        
        logger.debug("Param set %s has ID %d" % (eval(self.lte_params_values_str), result))
        return result



    def _get_result_id_lte(self):
        logger=logging.getLogger('_get_result_id_lte')
        GET_QUERY  =  "SELECT result_id FROM lte_results WHERE testrun_id='%s'" % self.mysql_entry_s.table_lte_results.testrun_id
        GET_QUERY +=  " AND  platform_id='%s'"   % self.mysql_entry_s.table_lte_results.platform_id
        GET_QUERY +=  " AND  param_id='%s'"      % self.mysql_entry_s.table_lte_results.param_id
        GET_QUERY +=  " AND  param_pcc_id='%s'"  % self.mysql_entry_s.table_lte_results.param_pcc_id
        GET_QUERY += (";")      
        
        if 1: 
            logger.debug(GET_QUERY)
        
        self.cursor.execute(GET_QUERY)
        result=self.cursor.fetchone()[0]
        
        logger.debug("Result for testrun_id %d, platform_id %d, param_id %d param_pcc_id %s has ID %d", self.mysql_entry_s.table_lte_results.testrun_id,
                                                                                                        self.mysql_entry_s.table_lte_results.platform_id, 
                                                                                                        self.mysql_entry_s.table_lte_results.param_id, 
                                                                                                        self.mysql_entry_s.table_lte_results.param_pcc_id, 
                                                                                                        result)
        return result    


    def _get_best_score(self, entry_s, branch, platform, carrier, varname):
        logger=logging.getLogger('_select_best_score')
        
        clnum          = None
        bestscore      = None
    
        # Build bestscore query
        EQUERY_BESTSCORE=re.sub('[ |\t|\n]+',' ', r"""SELECT clnum,MAX(%s) AS %s FROM %s
        INNER JOIN %s ON %s.platform_id=%s.platform_id 
        INNER JOIN %s ON %s.testrun_id=%s.testrun_id
        INNER JOIN %s ON %s.param_id=%s.param_id 
        INNER JOIN %s ON %s.testinfo_id=%s.testinfo_id""" % (varname, 
                                                             varname,
                                                             DatabaseMySqlPl1Testbench.TABLE_LTE_RESULTS,
                                                             DatabaseMySqlPl1Testbench.TABLE_PLATFORMS, DatabaseMySqlPl1Testbench.TABLE_LTE_RESULTS, DatabaseMySqlPl1Testbench.TABLE_PLATFORMS, 
                                                             DatabaseMySqlPl1Testbench.TABLE_TESTRUNS,  DatabaseMySqlPl1Testbench.TABLE_LTE_RESULTS, DatabaseMySqlPl1Testbench.TABLE_TESTRUNS,
                                                             DatabaseMySqlPl1Testbench.TABLE_LTE_PARAMS,DatabaseMySqlPl1Testbench.TABLE_LTE_RESULTS, DatabaseMySqlPl1Testbench.TABLE_LTE_PARAMS,
                                                             DatabaseMySqlPl1Testbench.TABLE_TESTINFOS, DatabaseMySqlPl1Testbench.TABLE_LTE_PARAMS,  DatabaseMySqlPl1Testbench.TABLE_TESTINFOS))
        EQUERY_BESTSCORE +=  (" WHERE  branch ='%s'" % branch if not branch is None else " WHERE branch is NULL")
        EQUERY_BESTSCORE +=  " AND  platform ='%s'" % platform
        EQUERY_BESTSCORE +=  " AND  valid ='1'"        
        EQUERY_BESTSCORE +=  " AND  carrier='%s'"   % carrier.upper()
        EQUERY_BESTSCORE +=  " AND  dmode='%s'"     % eval("entry_s.%s.dmode" % carrier.lower())
        EQUERY_BESTSCORE += (" AND  dlulconf='%s'"  % eval("entry_s.%s.dlulconf" % carrier.lower())) if not eval("entry_s.%s.dlulconf" % carrier.lower()) is None else " AND dlulconf is NULL"
        EQUERY_BESTSCORE += (" AND  ssconf='%s'"    % eval("entry_s.%s.ssconf" % carrier.lower()))   if not eval("entry_s.%s.ssconf"   % carrier.lower()) is None else " AND ssconf is NULL"
        EQUERY_BESTSCORE +=  " AND  bwmhz='%s'"     % eval("entry_s.%s.bwmhz" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  rfband='%s'"    % eval("entry_s.%s.rfband" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  earfcn='%s'"    % eval("entry_s.%s.earfcn" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  cp='%s'"        % eval("entry_s.%s.cp" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  tm='%s'"        % eval("entry_s.%s.tm" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  txants='%s'"    % eval("entry_s.%s.txants" % carrier.lower())
        EQUERY_BESTSCORE += (" AND  pmi='%s'"       % eval("entry_s.%s.pmi" % carrier.lower())) if not eval("entry_s.%s.pmi" % carrier.lower()) is None else " AND pmi is NULL"
        EQUERY_BESTSCORE +=  " AND  rsepre='%s'"    % eval("entry_s.%s.rsepre" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  pa='%s'"        % eval("entry_s.%s.pa" % carrier.lower())
        EQUERY_BESTSCORE +=  " AND  pb='%s'"        % eval("entry_s.%s.pb" % carrier.lower())
        
        EQUERY_BESTSCORE += (" AND  chtype='%s'"    % CmwLte.CMW_LTE_FADING_CHANNELS_TO_3GPP[eval("entry_s.%s.chtype" % carrier.lower())]) if not eval("entry_s.%s.chtype" % carrier.lower()) is None else " AND chtype is NULL"
        EQUERY_BESTSCORE += (" AND  snr='%s'"       % eval("entry_s.%s.snr" % carrier.lower())) if not eval("entry_s.%s.snr" % carrier.lower()) is None else " AND snr is NULL"
        EQUERY_BESTSCORE += (" AND  doppler='%s'"   % eval("entry_s.%s.doppler" % carrier.lower())) if not eval("entry_s.%s.doppler" % carrier.lower()) is None else " AND doppler is NULL"
        EQUERY_BESTSCORE +=  " AND  schedtype='%s'" % CMW_LTE_SCHEDTYPE_MAP[eval("entry_s.%s.schedtype" % carrier.lower())]
        EQUERY_BESTSCORE += (" AND  nhrtx='%s'"     % eval("entry_s.%s.nhrtx" % carrier.lower())) if not eval("entry_s.%s.nhrtx" % carrier.lower()) is None else " AND nhrtx is NULL"
        EQUERY_BESTSCORE += (" AND  riv='%s'"       % eval("entry_s.%s.riv" % carrier.lower())) if not eval("entry_s.%s.riv" % carrier.lower()) is None else " AND riv is NULL"
        EQUERY_BESTSCORE += (" AND  dlmcs='%s'"     % eval("entry_s.%s.dlmcs" % carrier.lower())) if not eval("entry_s.%s.dlmcs" % carrier.lower()) is None else " AND dlmcs is NULL"
        EQUERY_BESTSCORE += (" AND  dlnprb='%s'"    % eval("entry_s.%s.dlnprb" % carrier.lower())) if not eval("entry_s.%s.dlnprb" % carrier.lower()) is None else " AND dlnprb is NULL"
        EQUERY_BESTSCORE += (" AND  dlrbstart='%s'" % eval("entry_s.%s.dlrbstart" % carrier.lower())) if not eval("entry_s.%s.dlrbstart" % carrier.lower()) is None else " AND dlrbstart is NULL"
        EQUERY_BESTSCORE += (" AND  ulmcs='%s'"     % eval("entry_s.%s.ulmcs" % carrier.lower())) if not eval("entry_s.%s.ulmcs" % carrier.lower()) is None else " AND ulmcs is NULL"
        EQUERY_BESTSCORE += (" AND  ulnprb='%s'"    % eval("entry_s.%s.ulnprb" % carrier.lower())) if not eval("entry_s.%s.ulnprb" % carrier.lower()) is None else " AND ulnprb is NULL"
        EQUERY_BESTSCORE += (" AND  ulrbstart='%s'" % eval("entry_s.%s.ulrbstart" % carrier.lower())) if not eval("entry_s.%s.ulrbstart" % carrier.lower()) is None else " AND ulrbstart is NULL"
        EQUERY_BESTSCORE +=  ";" 
    
        logger.debug("EQUERY : %s" % EQUERY_BESTSCORE)

        # Access database        
        try:
            self.cursor.execute(EQUERY_BESTSCORE)
            if self.cursor:
                for result in self.cursor:
                    clnum      = result[0]
                    bestscore  = result[1]
            else:
                logger.debug("SELECT bestscore: no entry found")
        except TypeError:
            logger.error("FAILURE on SELECT bestscore")
        else:
            pass
            #logger.debug("SELECT bestscore: entry found")

        return (clnum, bestscore) 
   


    # *****************************************************************************#
    #                    LTE TABLES UPDATE FUNCTIONS                               #
    # *****************************************************************************#    
    def _write_database_config_entry(self):
        logger=logging.getLogger('_write_database_config_entry')
        
        try:             
            # Add platform
            self.platform_id=self.add_platform(self.mysql_entry_s.table_platforms.platform)
            logger.debug("SELECTED: platform_id:%s, platform:%s" % (self.platform_id, 
                                                                    self.mysql_entry_s.table_platforms.platform))
    
            # Add testinfo
            self.testinfo_id=self.add_testinfo(testid=self.mysql_entry_s.table_testinfos.testid,
                                               rat=self.mysql_entry_s.table_testinfos.rat, 
                                               testtype=self.mysql_entry_s.table_testinfos.testtype, 
                                               descr=self.mysql_entry_s.table_testinfos.descr)
            
            logger.debug("SELECTED: testinfo_id:%s, testid:%s, rat=%s, testtype:%s, descr:%s" % (self.testinfo_id, 
                                                                                                 self.mysql_entry_s.table_testinfos.testid, 
                                                                                                 self.mysql_entry_s.table_testinfos.rat,
                                                                                                 self.mysql_entry_s.table_testinfos.testtype, 
                                                                                                 self.mysql_entry_s.table_testinfos.descr))
            
            # Add test_run
            self.testrun_id=self.add_testrun(timestamp=self.mysql_entry_s.table_testruns.timestamp,
                                             branch=self.mysql_entry_s.table_testruns.branch, 
                                             clnum=self.mysql_entry_s.table_testruns.clnum, 
                                             mod_files=self.mysql_entry_s.table_testruns.mod_files, 
                                             p4webrev=self.mysql_entry_s.table_testruns.p4webrev, 
                                             testerinfo=self.mysql_entry_s.table_testruns.testerinfo,
                                             modeminfo=self.mysql_entry_s.table_testruns.modeminfo)        
            
            logger.debug("SELECTED: testrun_id:%s, timestamp=%s, branch:%s, clnum:%s, mod_files:%s, p4webrev:%s, testerinfo:%s, modeminfo=%s" % (self.testrun_id, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.timestamp, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.branch, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.clnum, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.mod_files, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.p4webrev, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.testerinfo, 
                                                                                                                                                 self.mysql_entry_s.table_testruns.modeminfo))

        except:
            logger.error("FAILURE: uploading test configuration into the database")
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            self.conn.commit()
            logger.debug("SUCCESS: test configuration uploaded")



    def _write_database_meas_entry(self):
        logger=logging.getLogger('_write_database_meas_entry')
    
        # Format entry values to be stored into the database 
        self._parse_meas_entry()
        try:        
            #Add LTE params set
            self.mysql_entry_s.table_lte_params.testinfo_id = self.testinfo_id            
            self.param_id=self._add_param_set_lte()
            
            # Add LTE results set
            # Copy the param_id into param_pcc_id  
            if self.mysql_entry_s.table_lte_params.carrier=='PCC':
                self.param_pcc_id = self.param_id    
            # Update secondary links to other tables 
            self.mysql_entry_s.table_lte_results.testrun_id   = self.testrun_id
            self.mysql_entry_s.table_lte_results.platform_id  = self.platform_id
            self.mysql_entry_s.table_lte_results.param_id     = self.param_id
            self.mysql_entry_s.table_lte_results.param_pcc_id = self.param_pcc_id
            # Add measurement results        
            self.result_id=self._add_result_set_lte()
                                        
        except:
            logger.error("FAILURE: uploading test measurement into the database")
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            #self.conn.commit()
            logger.debug("SUCCESS: test measurement uploaded")

        
    
    def _add_param_set_lte(self):
        logger=logging.getLogger('_add_param_set_lte')
        try:
            return self._get_param_id_lte() 
        except TypeError:
            logger.debug("Creating record for lte_param set %s", eval(self.lte_params_values_str))
            self.cursor.execute(("INSERT INTO lte_params(%s) VALUES (%s)" % (self.lte_params_args_str, self.lte_params_frmt_str)), eval(self.lte_params_values_str))
            return self._get_param_id_lte()


    def _add_result_set_lte(self):
        logger=logging.getLogger('_add_result_set_lte')
                
        try:
            return self._get_result_id_lte()
        except TypeError:
            logger.debug("Creating result record for testrun_id %s, platform_id %s, param_id %s, param_pcc_id %s", self.mysql_entry_s.table_lte_results.testrun_id, 
                                                                                                                   self.mysql_entry_s.table_lte_results.platform_id, 
                                                                                                                   self.mysql_entry_s.table_lte_results.param_id, 
                                                                                                                   self.mysql_entry_s.table_lte_results.param_pcc_id)
            
            self.cursor.execute(("INSERT INTO lte_results(%s) VALUES (%s)" % (self.lte_results_args_str, self.lte_results_frmt_str)), eval(self.lte_results_values_str))
            return self._get_result_id_lte()


    def _database_committ(self):
        logger=logging.getLogger('_write_database_committ')
        self.conn.commit()
        logger.debug("SUCCESS: test committed")
        
    # *****************************************************************************#
    #                    LTE TABLES UPDATE FUNCTIONS                               #
    # *****************************************************************************#    
    def _export_bler_results(self, filename):    
        logger=logging.getLogger('_export_bler_results')
        logger.debug("Export LTE database into file : %s" % filename)
        
        try: 
            # Clean data from any previous test
            if os.path.isfile(filename):
                os.remove(filename)
        
            # Create destination folder, if does not exists
            fpath=os.path.split(filename)[0]
            if not os.path.exists(fpath): 
                os.makedirs(fpath)
                logger.debug("Created destination folder: %s" % fpath)
                
            # Set query                                                        
            EQUERY_DATABASE=re.sub('[ |\t|\n]+',
                                   ' ', 
                                   r"""SELECT * FROM %s
                                         INNER JOIN %s ON %s.platform_id=%s.platform_id 
                                         INNER JOIN %s ON %s.testrun_id=%s.testrun_id
                                         INNER JOIN %s ON %s.param_id=%s.param_id 
                                         INNER JOIN %s ON %s.testinfo_id=%s.testinfo_id ORDER BY %s.testrun_id ;""" % (self.TABLE_LTE_RESULTS,
                                                                                               self.TABLE_PLATFORMS, self.TABLE_LTE_RESULTS, self.TABLE_PLATFORMS, 
                                                                                               self.TABLE_TESTRUNS,  self.TABLE_LTE_RESULTS, self.TABLE_TESTRUNS,
                                                                                               self.TABLE_LTE_PARAMS,self.TABLE_LTE_RESULTS, self.TABLE_LTE_PARAMS,
                                                                                               self.TABLE_TESTINFOS, self.TABLE_LTE_PARAMS,  self.TABLE_TESTINFOS,
                                                                                               self.TABLE_TESTRUNS))
            self.cursor.execute(EQUERY_DATABASE)
        
            # Extract header from cursor description
            query_header_l=[]
            if 0: print self.cursor.description
            for column in self.cursor.description:
                query_header_l.append(column[0])   
            logger.debug("QUERY HEADER : %s" % query_header_l)
            
            # Configure query line format 
            query_out_format='%s, '*(len(query_header_l)-1)+'%s\n'
            
            if self.cursor:
                with open(filename,'a') as fd:
                    fd.write(query_out_format % tuple(query_header_l))
                    for query_out in self.cursor:
                        fd.write(query_out_format % tuple(query_out))
                fd.close()
            else:
                logger.debug("export_to_csv(), no entry found in database %s" % filename)
    
        except TypeError:
            logger.error("SELECT failure")
            print sys.exc_info()
        except IOError:
            logger.error("ERROR: opening file %s" % filename)
            print sys.exc_info()
        except:
            logger.debug("Export LTE database failed")
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            logger.info("SUCCESS  LTE database exported into file: %s" % filename)
    
    
    # =============================================================================
    # PUBLIC METHODS
    # =============================================================================        
    def import_bler_results(self, configfile_txt, measfile_csv):
        self._import_ltebler_config_from_txt(configfile_txt)
        self._import_ltebler_meas_from_csv(measfile_csv)
    
    def export_bler_results(self, filename):    
        self._export_bler_results(filename)
        
    def select_best_score(self, entry_s, branch, platform, carrier, varname):
        (clnum, bestscore) = self._get_best_score(entry_s, branch, platform, carrier, varname)
        return (clnum, bestscore)
            
    def import_database(self, dbfile_csv):
        self._import_database_from_csv(dbfile_csv)
        
        

if __name__ == '__main__':

    from Struct import Struct
    
    # Configure logging
    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)
    
    t0=time.localtime()

    # Define folders hierarchy
    dir_root           =os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:])
    dir_export         =os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common', 'report', 'mysql', 'database', 'export'])
    dir_import         =os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common', 'report', 'mysql', 'database', 'import']) 
    
    if 1:
        # local database acces
        host    = 'localhost'
        dbname  = 'pl1testbench'
        uid     = 'root'
        pwd     = 'BZh91AY&SY!-o\xae\x00\x00\x01\x01\x80\x00\x00\x94\x00 \x000\xcc\x0c\xf5\x06qw$S\x85\t\x02\x12\xd6\xfa\xe0'
    
    if 1:     
        logger.debug("---------------------------------------") 
        logger.debug(">> Checking access permissions:")
        logger.debug("---------------------------------------") 
        mySqlCheckPermission(host, dbname, uid, pwd)
        mySqlGetVersion(host, dbname, uid, pwd)
    
    if 0:
        logger.debug("------------------------------------------") 
        logger.debug(">> Import from BLER measurements CVS file:")
        logger.debug("------------------------------------------")         
        
        cfgfile_2_import=os.path.join(dir_import,'LTE_FDD_CA_CMW500_TestConf_testID_10000.txt')
        csvfile_2_import=os.path.join(dir_import,'LTE_FDD_CA_CMW500_TestMeas_testID_10000.csv')

        if 1:
            db_h=DatabaseMySqlPl1TestbenchLte(host, dbname, uid, pwd)
            if 1:
                logger.debug("fields::table_platforms   : %s" % db_h.mysql_entry_s.table_platforms.get_fieldname_list())
                logger.debug("fields::table_testinfos   : %s" % db_h.mysql_entry_s.table_testinfos.get_fieldname_list())
                logger.debug("fields::table_testruns    : %s" % db_h.mysql_entry_s.table_testruns.get_fieldname_list())
                logger.debug("fields::table_lte_params  : %s" % db_h.mysql_entry_s.table_lte_params.get_fieldname_list())
                logger.debug("fields::table_lte_results : %s" % db_h.mysql_entry_s.table_lte_results.get_fieldname_list())
            db_h.import_bler_results(cfgfile_2_import, csvfile_2_import)       
            db_h.database_disconnect()
        else:
            mysqlImportBlerResults(host, dbname, uid, pwd, cfgfile_2_import, csvfile_2_import)
    
                
        
    t1=time.localtime()
    dt=time.mktime(t1)-time.mktime(t0)
    logger.info("Time duration %d[sec]" % dt)
           
   
    
        

    
