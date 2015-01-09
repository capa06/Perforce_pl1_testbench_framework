'''
Created on 28 Nov 2013

@author: jlucas, fsaracino
'''

import os
import sys
import logging
import time
#import re
import bz2
import MySQLdb as mydb


# =============================================================================
# DEFINE LOCAL PATHS 
# =============================================================================
try: 
    os.environ['PL1TESTBENCH_ROOT_FOLDER']
except KeyError:
    os.environ['PL1TESTBENCH_ROOT_FOLDER'] = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-4])
    print ">> os.environ['PL1TESTBENCH_ROOT_FOLDER']=%s" % os.environ['PL1TESTBENCH_ROOT_FOLDER']
else:
    pass

sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'report', 'csv']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'config']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'utils']))
sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'icera']))


 
# =============================================================================
# IMPORT USER DEFINED LIBRARY 
# =============================================================================
from CfgError import CfgError
from icera_utils import parseModemInfo, getBranch, getPlatform, getVariant

# =============================================================================
# GLOBAL VARIABLES 
# =============================================================================



# =============================================================================
# DATABASE API FUNCTIONS 
# =============================================================================
def mySqlCheckPermission(host, dbname, uid, pwd):
    logger=logging.getLogger('mySqlCheckPermission')
    logger.debug("db_params: name %s, uid %s, host %s" % (dbname, uid, host))
    
    try: 
        # Get database connection object instance
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        
        # Open database connection                                                
        db_h.database_connect()
        
        db_h.cursor.execute("SHOW GRANTS for current_user;")
        result=db_h.cursor.fetchall()
        
        grant_all_db = "ALL PRIVILEGES ON `%s`" %dbname
        grant_all_all = "ALL PRIVILEGES ON *.*"
        grant_select_db = "SELECT ON `%s`" %dbname
        grant_select_all = "SELECT ON *.*"
        grant = ""
        for res in result:
            grant = "%s %s" %(grant,res)
        
        if ( (grant_select_db in grant) or (grant_select_all in grant)):
            res = "READ_ONLY"
        elif ( (grant_all_db in grant) or (grant_all_all in grant)):
            res = "READ_WRITE"
        else:
            res = None
        
        logger.debug("Available access to DB: %s@%s for User: %s is %s." %(dbname, host, uid, res))    
        
        db_h.database_disconnect()    
        return res  
    
    except :
        logger.warning("ACCESS to Database is not available.")
        return None


def mySqlGetVersion(host, dbname, uid, pwd):
    logger=logging.getLogger('mySqlGetVersion')
    logger.debug("db_params: name %s, uid %s, host %s" % (dbname, uid, host))
    db_h = None
    ver  = None
    try: 
        # Get database connection object instance
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        db_h.database_connect()
        db_h.cursor = db_h.conn.cursor()
        db_h.cursor.execute("SELECT VERSION()")
        ver=db_h.cursor.fetchone()
        logger.info("Database version : %s " % ver)
    except mydb.Error, e:
        logger.error("Error %d: %s" % (e.args[0],e.args[1]))
        sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
    finally:
        if (not db_h is None):
            db_h.database_disconnect()
    return ver
    

# =============================================================================
# DATABASE STRUCTURE FOR PERFORMANCE MEASUREMENTS 
# =============================================================================
class DatabaseMySqlPl1Testbench(object):
    DATABASE_NAME       = 'pl1testbench'
    TABLE_PLATFORMS     = 'platforms'
    TABLE_TESTINFOS     = 'testinfos'
    TABLE_TESTRUNS      = 'testruns'
    TABLE_LTE_PARAMS    = 'lte_params'
    TABLE_LTE_RESULTS   = 'lte_results'
    TABLE_WCDMA_PARAMS  = 'wcdma_params'
    TABLE_WCDMA_RESULTS = 'wcdma_results'
    TABLE_GSM_PARAMS    = 'gsm_params'
    TABLE_GSM_RESULTS   = 'gsm_results'
    
    
    name   = None
    conn   = None
    cursor = None
    host   = None
    uid    = None
    pwd    = None
    
    def __init__ (self, host, dbname, uid, pwd):   
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.__init__') 

        self.host   = host
        self.name   = dbname
        self.uid    = uid
        self.pwd    = pwd                        
        
        # Note: database MUST be created 
        try:
            logger.debug("Checking MySQL database : (host=%s, dbname=%s, uid=%s)" % (host, dbname, uid))
            self.database_connect()
            self.cursor = self.conn.cursor()            
        except :
            logger.error("Error database not found: %s" % self.name)
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            pass
        
        
    # =============================================================================
    # DATABASE ADMIN FUNCTIONS
    # =============================================================================
    def database_destroy(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_destroy')
        try: 
            # Get database connection object instance
            self.cursor.execute("DROP DATABASE %s;" % self.name)
            logger.info("Database deleted : %s " % self.name)
        except mydb.Error, e:
            logger.error("Error %d: %s" % (e.args[0],e.args[1]))
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        finally:
            pass


    def database_tables_init(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_tables_init')
        if 0: self.database_tables_drop() 
        self.database_tables_insert()    
        logger.debug("initialised database : %s" % self.name)


    def database_tables_insert(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_tables_insert')
        try:
            if not self.table_exists(self.name, self.TABLE_PLATFORMS):
                
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (platform_id     INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      platform        TEXT                NOT NULL,
                                                                      aux_info        TEXT                NULL);""" % self.TABLE_PLATFORMS)
                logger.debug("created table : %s" % self.TABLE_PLATFORMS)
                
            if not self.table_exists(self.name, self.TABLE_TESTINFOS):
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (testinfo_id     INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      testid          INTEGER UNSIGNED            NOT NULL,
                                                                      rat             ENUM('LTE_FDD', 'LTE_FDD_CA', 'LTE_TDD', 'LTE_TDD_CA', 'WCDMA', 'GSM') NOT NULL,
                                                                      testtype        TEXT                        NOT NULL,
                                                                      descr           TEXT);""" % self.TABLE_TESTINFOS)                                      
                logger.debug("created table : %s" % self.TABLE_TESTINFOS)

            if not self.table_exists(self.name, self.TABLE_TESTRUNS):
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s ( testrun_id      INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                       timestamp       TIMESTAMP           NOT NULL,
                                                                       branch          TEXT                    NULL,
                                                                       clnum           INTEGER UNSIGNED        NULL,
                                                                       mod_files       INTEGER UNSIGNED        NULL,
                                                                       p4webrev        TEXT                    NULL,                                                              
                                                                       testerinfo      TEXT                    NULL,
                                                                       modeminfo       TEXT                    NULL);""" % self.TABLE_TESTRUNS)
                logger.debug("created table : %s" % self.TABLE_TESTRUNS)
            
            if not self.table_exists(self.name, self.TABLE_LTE_PARAMS):     
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (param_id        INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      testinfo_id     INTEGER             NOT NULL,
                                                                      carrier         TEXT                NOT NULL,
                                                                      dmode           TEXT                NOT NULL,
                                                                      dlulconf        INTEGER                 NULL,
                                                                      ssconf          INTEGER                 NULL,
                                                                      bwmhz           REAL                NOT NULL,
                                                                      rfband          INTEGER             NOT NULL,
                                                                      earfcn          INTEGER             NOT NULL,
                                                                      cp              TEXT                NOT NULL,                                                              
                                                                      tm              INTEGER UNSIGNED    NOT NULL,
                                                                      txants          INTEGER UNSIGNED    NOT NULL,
                                                                      pmi             INTEGER UNSIGNED        NULL,
                                                                      rsepre          REAL                NOT NULL,
                                                                      pa              INTEGER             NOT NULL,
                                                                      pb              INTEGER             NOT NULL,
                                                                      chtype          TEXT                    NULL,
                                                                      snr             REAL                    NULL,
                                                                      doppler         REAL                    NULL,
                                                                      schedtype       TEXT                NOT NULL,
                                                                      nhrtx           INTEGER UNSIGNED        NULL,
                                                                      riv             TEXT                    NULL,                                                                      
                                                                      dlmcs           INTEGER UNSIGNED        NULL, 
                                                                      dlnprb          INTEGER UNSIGNED        NULL,
                                                                      dlrbstart       INTEGER UNSIGNED        NULL,
                                                                      ulmcs           INTEGER UNSIGNED        NULL,
                                                                      ulnprb          INTEGER UNSIGNED        NULL,
                                                                      ulrbstart       INTEGER UNSIGNED        NULL,
                                                                      FOREIGN KEY (testinfo_id) REFERENCES %s(testinfo_id));""" % (self.TABLE_LTE_PARAMS, self.TABLE_TESTINFOS))
                
                logger.debug("created table LTE: %s" % self.TABLE_LTE_PARAMS)
                
            if not self.table_exists(self.name, self.TABLE_LTE_RESULTS):
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (result_id       INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      testrun_id      INTEGER             NOT NULL,
                                                                      platform_id     INTEGER             NOT NULL,
                                                                      param_id        INTEGER             NOT NULL,
                                                                      param_pcc_id    INTEGER             NOT NULL,                                                                      
                                                                      valid           BOOL                NOT NULL,
                                                                      dlrely          INTEGER,
                                                                      dlthr_Mbps      REAL,
                                                                      dlthr_min_Mbps  REAL,
                                                                      dlthr_max_Mbps  REAL,                                                                      
                                                                      dlbler          REAL,
                                                                      cqi             INTEGER UNSIGNED,
                                                                      ack             INTEGER UNSIGNED,
                                                                      nack            INTEGER UNSIGNED,
                                                                      dtx             INTEGER UNSIGNED,
                                                                      sf_total        INTEGER UNSIGNED,
                                                                      sf_scheduled    INTEGER UNSIGNED,
                                                                      ulrely          INTEGER UNSIGNED        NULL,            
                                                                      ulthr_Mbps      REAL                    NULL,
                                                                      ulbler          REAL                    NULL,
                                                                      crc_pass        INTEGER UNSIGNED        NULL,
                                                                      crc_fail        INTEGER UNSIGNED        NULL,
                                                                      best_dlthr_Mbps REAL                    NULL,
                                                                      best_ulthr_Mbps REAL                    NULL,                                                               
                                                                      tolerance       TEXT                    NULL,
                                                                      verdict_dl      TEXT                    NULL,
                                                                      verdict_ul      TEXT                    NULL,
                                                                      voltage_V       REAL                    NULL,
                                                                      current_mA      REAL                    NULL,
                                                                      power_mW        REAL                    NULL,
                                                                      rank            TEXT                    NULL,
                                                                      dlthr_cw1       TEXT                    NULL,
                                                                      dlthr_cw2       TEXT                    NULL,
                                                                      cqi_cw1         TEXT                    NULL,
                                                                      cqi_cw2         TEXT                    NULL,
                                                                      pmi_ri1         TEXT                    NULL,
                                                                      pmi_ri2         TEXT                    NULL,
                                                                      harq_cw1        TEXT                    NULL,
                                                                      harq_cw2        TEXT                    NULL,                                                                      
                                                                      FOREIGN KEY (testrun_id) REFERENCES %s(testrun_id),
                                                                      FOREIGN KEY (param_id) REFERENCES %s(param_id),
                                                                      FOREIGN KEY (platform_id) REFERENCES %s(platform_id));""" % (self.TABLE_LTE_RESULTS, self.TABLE_TESTRUNS, self.TABLE_LTE_PARAMS, self.TABLE_PLATFORMS))                                      
                logger.debug("created table : %s" % self.TABLE_LTE_RESULTS)    

            if not self.table_exists(self.name, self.TABLE_WCDMA_PARAMS):
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (param_id             INTEGER     PRIMARY KEY AUTO_INCREMENT, 
                                                                      testinfo_id          INTEGER          NOT NULL,
                                                                      rfband               INTEGER          NOT NULL,
                                                                      uarfcn               INTEGER          NOT NULL,
                                                                      chtype               TEXT             NOT NULL,    
                                                                      datarate             TEXT             NOT NULL,
                                                                      snr                  REAL             NOT NULL,
                                                                      power                REAL             NOT NULL,
                                                                      txant                INTEGER UNSIGNED NOT NULL,
                                                                      sched_type           TEXT,
                                                                      modulation           TEXT,
                                                                      ki                   INTEGER                   DEFAULT 0,
                                                                      num_hsdsch_codes     INTEGER                   DEFAULT 0,
                                                                      cpich_power          REAL                      DEFAULT 0.0,
                                                                      hspdsch_power        REAL                      DEFAULT 0.0,
                                                                      snr_2                REAL                      DEFAULT 0.0,
                                                                      power_2              REAL                      DEFAULT 0.0,
                                                                      modulation_2         TEXT,
                                                                      ki_2                 INTEGER                   DEFAULT 0,
                                                                      num_hsdsch_codes_2   INTEGER                   DEFAULT 0,
                                                                      FOREIGN KEY (testinfo_id) REFERENCES %s(testinfo_id));""" % (self.TABLE_WCDMA_PARAMS, self.TABLE_TESTINFOS))                
                logger.debug("created table : %s" % self.TABLE_WCDMA_PARAMS)    

            if not self.table_exists(self.name, self.TABLE_WCDMA_RESULTS):                                                                         
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (result_id         INTEGER    PRIMARY KEY AUTO_INCREMENT,
                                                                      testrun_id          INTEGER    NOT NULL,
                                                                      platform_id         INTEGER    NOT NULL,
                                                                      param_id          INTEGER    NOT NULL,
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
                                                                      dl_verdict          TEXT       ,
                                                                      i_min               REAL       DEFAULT 0.0,
                                                                      i_avg               REAL       DEFAULT 0.0,
                                                                      i_max               REAL       DEFAULT 0.0,
                                                                      i_deviation         TINYTEXT, 
                                                                      pwr_min             REAL       DEFAULT 0.0,
                                                                      pwr_avg             REAL       DEFAULT 0.0,
                                                                      pwr_max             REAL       DEFAULT 0.0,    
                                                                      FOREIGN KEY (testrun_id) REFERENCES %s(testrun_id),
                                                                      FOREIGN KEY (param_id) REFERENCES %s(param_id),
                                                                      FOREIGN KEY (platform_id) REFERENCES %s(platform_id));""" % (self.TABLE_WCDMA_RESULTS, self.TABLE_TESTRUNS, self.TABLE_WCDMA_PARAMS, self.TABLE_PLATFORMS))
                logger.debug("created table : %s" % self.TABLE_WCDMA_RESULTS)    


            if not self.table_exists(self.name, self.TABLE_GSM_PARAMS):
                
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (param_id        INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      testinfo_id     INTEGER             NOT NULL,
                                                                      rfband          INTEGER             NOT NULL,
                                                                      bch_arfcn       INTEGER             NOT NULL,
                                                                      bch_pwr_dl      REAL                NOT NULL,
                                                                      bch_pcl         REAL                NOT NULL,                                                             
                                                                      tch_arfcn       INTEGER             NOT NULL,
                                                                      tch_pwr_dl      REAL                NOT NULL,
                                                                      tbfl            TEXT                NOT NULL,
                                                                      chtype          TEXT                NOT NULL,
                                                                      snr             REAL                    NULL,                                                             
                                                                      dlmcs           TEXT                    NULL,
                                                                      ulmcs           TEXT                    NULL,
                                                                      FOREIGN KEY (testinfo_id) REFERENCES %s(testinfo_id));""" % (self.TABLE_GSM_PARAMS, self.TABLE_TESTINFOS))
                logger.debug("created table : %s" % self.TABLE_GSM_PARAMS)    

            if not self.table_exists(self.name, self.TABLE_GSM_RESULTS):
                self.cursor.execute("""CREATE TABLE IF NOT EXISTS %s (result_id       INTEGER PRIMARY KEY AUTO_INCREMENT,
                                                                      testrun_id      INTEGER             NOT NULL,
                                                                      platform_id     INTEGER             NOT NULL,
                                                                      param_id        INTEGER             NOT NULL,
                                                                      valid           BOOL                NOT NULL,
                                                                      dlrely          INTEGER             NOT NULL,
                                                                      dlbler          REAL                NOT NULL,
                                                                      rlc_blocks      INTEGER UNSIGNED    NOT NULL,
                                                                      tot_datarate    REAL                NOT NULL,
                                                                      thr_ovrall      REAL                NOT NULL,
                                                                      thr_per_slot    REAL                NOT NULL,
                                                                      noise_sysbw     REAL                NOT NULL,
                                                                      noise_totbw     REAL                NOT NULL,
                                                                      s_plus_n_totbw  REAL                NOT NULL,
                                                                      dlthr_ref       REAL                NOT NULL,
                                                                      tolerance       REAL                NOT NULL,
                                                                      verdict_dl      TEXT                NOT NULL,
                                                                      curr            REAL                    NULL,
                                                                      volt            REAL                    NULL,
                                                                      pwr             REAL                    NULL,                                                              
                                                                      FOREIGN KEY (testrun_id) REFERENCES %s(testrun_id),
                                                                      FOREIGN KEY (param_id) REFERENCES %s(param_id),
                                                                      FOREIGN KEY (platform_id) REFERENCES %s(platform_id));""" % (self.TABLE_GSM_RESULTS, self.TABLE_TESTRUNS, self.TABLE_GSM_PARAMS, self.TABLE_PLATFORMS))
                logger.debug("created table : %s" % self.TABLE_GSM_RESULTS)
                 
        except:
            logger.error("table insertion failure")
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            self.conn.commit()         
                                                              
    
    def database_tables_drop(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_tables_drop')
        try:
            if self.table_exists(self.name, self.TABLE_LTE_RESULTS):
                self.cursor.execute("""DROP TABLE %s;""" % self.TABLE_LTE_RESULTS)
                logger.debug("dropped table : %s" % self.TABLE_LTE_RESULTS)

            if self.table_exists(self.name, self.TABLE_LTE_PARAMS):
                self.cursor.execute("""DROP TABLE %s;""" % self.TABLE_LTE_PARAMS)
                logger.debug("dropped table : %s" % self.TABLE_LTE_PARAMS)

            if self.table_exists(self.name, self.TABLE_PLATFORMS):
                self.cursor.execute("""DROP TABLE %s;""" % self.TABLE_PLATFORMS)
                logger.debug("dropped table : %s" % self.TABLE_PLATFORMS)

            if self.table_exists(self.name, self.TABLE_TESTINFOS):
                self.cursor.execute("""DROP TABLE %s;""" % self.TABLE_TESTINFOS)
                logger.debug("dropped table : %s" % self.TABLE_TESTINFOS)

            if self.table_exists(self.name, self.TABLE_TESTRUNS):
                self.cursor.execute("""DROP TABLE %s;""" % self.TABLE_TESTRUNS)
                logger.debug("dropped table : %s" % self.TABLE_TESTRUNS)
                    
        except:
            logger.error("table drop failure")
            print sys.exc_info()
            sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
        else:
            self.conn.commit()
    
    
    # =============================================================================
    # DATABASE USER FUNCTIONS
    # =============================================================================
    def database_connect(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_connect')
        if self.conn is None:
            self.conn = mydb.connect(self.host, self.uid, bz2.decompress(self.pwd), self.name)
            logger.debug("Connected to database : %s" % self.name)
        else:
            logger.debug("Self.con is not None")    


    def database_disconnect(self):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.database_disconnect')
        if not self.conn is None:
            self.conn.close()
            logger.debug("Disconnected from database : %s" % self.name)


    # =============================================================================
    # TABLE SPECIFIC FUNCTIONS
    # =============================================================================
    def table_exists(self, dbname, tablename):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.table_exists')
        try: 
            if self.conn==None: 
                self.database_connect()   
            self.cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = %s ;", (dbname, tablename))
            result=(self.cursor.fetchone()[0] > 0)
            if result:
                logger.debug("table=%s found in database=%s" % (tablename, dbname))
            else:
                logger.debug("table=%s not found in database=%s" % (tablename, dbname))
        except mydb.OperationalError:
            logger.error("TABLE %s.table_exists()" % tablename)
            raise mydb.OperationalError
            print sys.exc_info()
            return False
        else:  
            return result
                                       
    def table_view(self, dbname, tablename):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.table_view')
        try: 
            if self.table_exists(dbname, tablename):
                cursor_len=self.cursor.execute("SELECT * FROM %s;""" % (tablename))
                idx=0
                while (idx<cursor_len):
                    data = self.cursor.fetchone()
                    logger.info("%s[%s] : %s" % (tablename, idx, data))
                    idx += 1
                if not idx:
                    logger.warning('empty table :  %s' % tablename)
            #else:
            #    logger.warning("table %s not found" % tablename)        
        except mydb.OperationalError:
            logger.error("error on table : %s" % tablename)
            print sys.exc_info()
            raise mydb.OperationalError
        else:
            pass


    def table_describe(self, dbname, tablename):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.table_describe')
        try: 
            if self.table_exists(dbname, tablename):
                cursor_len=self.cursor.execute("DESCRIBE %s;""" % (tablename))
                idx=0
                while (idx<cursor_len):
                    data = self.cursor.fetchone()
                    logger.info("%s[%s] : %s" % (tablename, idx, data))
                    idx += 1
                if not idx:
                    logger.warning('empty table :  %s' % tablename)
            #else:
            #    logger.warning("table %s not found" % tablename)        
        except mydb.OperationalError:
            logger.error("error on table : %s" % tablename)
            print sys.exc_info()
            raise mydb.OperationalError
        else:
            pass


    # =============================================================================
    # TABLE ENTRY FUNCTIONS
    # =============================================================================
    def get_platform_id(self, platform):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.get_platform_id')        
        self.cursor.execute("SELECT platform_id FROM platforms WHERE platform=%s", (platform,))
        result=self.cursor.fetchone()[0]
        logger.debug("Platform %s has ID %d",(platform),result)
        return result


    def add_platform(self, platform):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.add_platform')        
        try:
            return self.get_platform_id(platform)
        except TypeError:
            self.cursor.execute("INSERT INTO platforms(platform) VALUES (%s)",(platform,))
            logger.debug("Created platform record for %s...",(platform))
            return self.get_platform_id(platform)

    
    def get_testinfo_id(self, testid):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.get_testinfo_id')
        self.cursor.execute("SELECT testinfo_id FROM testinfos WHERE testid=%s", (testid,))
        result=self.cursor.fetchone()[0]
        logger.debug("testid %s has ID %d", testid, result)
        return result


    def add_testinfo(self, testid, rat, testtype, descr):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.add_testinfo')
        try:
            return self.get_testinfo_id(testid)
        except TypeError:
            self.cursor.execute("INSERT INTO testinfos(testid, rat, testtype, descr) VALUES (%s,%s,%s,%s)", (testid, rat, testtype, descr))
            logger.debug("Created testinfo record for %s...",(testid, rat, testtype, descr))
            return self.get_testinfo_id(testid)


    def get_testrun_id(self, timestamp, branch, clnum, mod_files, p4webrev):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.get_testrun_id')
        GET_QUERY  = "SELECT testrun_id FROM testruns WHERE timestamp='%s'" % timestamp
        GET_QUERY += (" AND  branch='%s'"    % branch)    if not branch    is None else " AND branch is NULL" 
        GET_QUERY += (" AND  clnum='%s'"     % clnum)     if not clnum     is None else " AND clnum is NULL" 
        GET_QUERY += (" AND  mod_files='%s'" % mod_files) if not mod_files is None else " AND mod_files is NULL" 
        GET_QUERY += (" AND  p4webrev='%s'"  % p4webrev)  if not p4webrev  is None else " AND p4webrev is NULL"
        GET_QUERY += (";")      
        if 1: logger.debug(GET_QUERY)
        #self.cursor.execute("SELECT testrun_id FROM testruns WHERE timestamp=%s AND branch=%s AND clnum=%s AND mod_files=%s AND p4webrev=%s", (timestamp, branch, clnum, mod_files, p4webrev))
        self.cursor.execute(GET_QUERY)
        result=self.cursor.fetchone()[0]
        logger.debug("Test run %s has ID %d",(timestamp, branch, clnum, mod_files, p4webrev), result)
        return result


    def add_testrun(self, timestamp, branch, clnum, mod_files, p4webrev, testerinfo, modeminfo):
        logger=logging.getLogger('DatabaseMySqlPl1Testbench.add_testrun')
        try:
            return self.get_testrun_id(timestamp, branch, clnum, mod_files, p4webrev)
        except TypeError:
            logger.debug("Create testrun record for %s", (timestamp, branch, clnum, mod_files, p4webrev, testerinfo, modeminfo))
            self.cursor.execute("INSERT INTO testruns(timestamp, branch, clnum, mod_files, p4webrev, testerinfo, modeminfo) VALUES (%s,%s,%s,%s,%s,%s,%s)",(timestamp, branch, clnum, mod_files, p4webrev, testerinfo, modeminfo))
            return self.get_testrun_id(timestamp, branch, clnum, mod_files, p4webrev)


    def __str__(self):
        print "---------------------------------------" 
        print "  file_database               : %s" % self.name
        print "  conn                        : %s" % self.conn
        print "  cursor                      : %s" % self.cursor
        return ""


if __name__ == '__main__':

    from cfg_multilogging import cfg_multilogging
    loglevel = 'DEBUG'
    logname  = logname= os.path.splitext(os.path.basename(__file__))[0]
    logfile  = logname  + '.LOG'
    cfg_multilogging(loglevel, logfile)
    logger=logging.getLogger(logname)

    sys.path.append(os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:]+['common', 'struct']))
    from Struct import Struct
    
    t0=time.localtime()

    # Define folders hierarchy
    dir_root           =os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:])
    dir_export         =os.sep.join(dir_root.split(os.sep)[:]+['common','report','mysql', 'database', 'export'])
    dir_import         =os.sep.join(dir_root.split(os.sep)[:]+['common','report','mysql', 'database', 'import']) 

    logger.info("------------------------------------")
    logger.info("dir_root          : %s" % dir_root)
    logger.info("dir_export        : %s" % dir_import)                              
    logger.info("dir_export        : %s" % dir_export)                              
    logger.info("------------------------------------")
    
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


    if 1:     
        logger.debug("---------------------------------------") 
        logger.debug(">> Init database tables:")
        logger.debug("---------------------------------------") 
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        db_h.database_tables_init()
        db_h.database_disconnect()
        del db_h
              
        
    if 1:
        logger.debug("---------------------------------------") 
        logger.debug(">> Checking table existence:")
        logger.debug("---------------------------------------") 
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        db_h.table_exists(dbname, db_h.TABLE_PLATFORMS)
        db_h.table_exists(dbname, db_h.TABLE_TESTINFOS)
        db_h.table_exists(dbname, db_h.TABLE_TESTRUNS)
        db_h.table_exists(dbname, db_h.TABLE_LTE_PARAMS)
        db_h.table_exists(dbname, db_h.TABLE_LTE_RESULTS)
        #db_h.table_exists(dbname, db_h.TABLE_GSM_PARAMS)
        #db_h.table_exists(dbname, db_h.TABLE_GSM_RESULTS)
        db_h.database_disconnect()
        del db_h

    if 1:
        logger.debug("---------------------------------------") 
        logger.debug(">> Checking table view:")
        logger.debug("---------------------------------------") 
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        db_h.table_view(dbname, db_h.TABLE_PLATFORMS)
        db_h.table_view(dbname, db_h.TABLE_TESTINFOS)
        db_h.table_view(dbname, db_h.TABLE_TESTRUNS)
        db_h.table_view(dbname, db_h.TABLE_LTE_PARAMS)
        db_h.table_view(dbname, db_h.TABLE_LTE_RESULTS)
        #db_h.table_view(dbname, db_h.TABLE_GSM_PARAMS)
        #db_h.table_view(dbname, db_h.TABLE_GSM_RESULTS)
        db_h.database_disconnect()
        del db_h

    if 1:
        logger.debug("---------------------------------------") 
        logger.debug(">> Retrieve table description:")
        logger.debug("---------------------------------------") 
        db_h=DatabaseMySqlPl1Testbench(host, dbname, uid, pwd)
        db_h.table_describe(dbname, db_h.TABLE_PLATFORMS)
        db_h.table_describe(dbname, db_h.TABLE_TESTINFOS)
        db_h.table_describe(dbname, db_h.TABLE_TESTRUNS)
        db_h.table_describe(dbname, db_h.TABLE_LTE_PARAMS)
        db_h.table_describe(dbname, db_h.TABLE_LTE_RESULTS)
        del db_h

                    
    t1=time.localtime()
    dt=time.mktime(t1)-time.mktime(t0)                             
    logger.info("Time duration %d[sec]" % dt)
    
    
