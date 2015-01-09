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
def databaseDestroy(dbname):
    logger=logging.getLogger('databaseDestroy')
    logger.debug("DatabaseDestroy()...")
    db_h=DatabasePl1Testbench(dbname)
    db_h.destroy()    
    del db_h
    
    
def databaseCheckPermission(dbname):
    logger=logging.getLogger('databaseCheckPermission')
    if sys.platform in ['cygwin', 'win32']:
        cmd="attrib -r %s" % dbname
    elif sys.platform in ['linux', 'linux2', 'linux3']:
        cmd="chmod +w %s" % dbname
    else:
        logger.error("OS not supported %s" % sys.platform)
        sys.exit(CfgError.ERRCODE_SYS_OS_ERROR)
    os.system(cmd)
    


# =============================================================================
# DATABASE STRUCTURE FOR PERFORMANCE MEASUREMENTS 
# =============================================================================
class DatabasePl1Testbench(object):
    TABLE_PLATFORMS   = 'platforms'
    TABLE_TESTINFOS   = 'testinfos'
    TABLE_TESTRUNS    = 'testruns'
    TABLE_LTE_PARAMS  = 'params'
    TABLE_LTE_RESULTS = 'results'
    TABLE_GSM_PARAMS  = 'gsm_params'
    TABLE_GSM_RESULTS = 'gsm_results'
    
    name=None
    conn=None
    cursor=None
    
    def __init__ (self, name):
            logger=logging.getLogger('DatabasePl1Testbench.__init__()') 
            # If database exists
            if os.path.exists(name):
                logger.debug("FOUND database           : %s" % name)
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
                        logger.debug("Creating destination folder: %s" % fpath)
                        os.makedirs(fpath)
        
                    self.name   = name                        
                    self.connect()
                    self.cursor = self.conn.cursor()
                    self.conn.execute("PRAGMA foreign_keys = ON;")
                    
                    logger.debug("INITIALIZING database    : %s" % self.name)
                    
                    self.conn.executescript("""
                        CREATE TABLE IF NOT EXISTS platforms (platform_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              platform        TEXT                NOT NULL);
        
                        CREATE TABLE IF NOT EXISTS testinfos (testinfo_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                                                              testid          UNSIGNED INT        NOT NULL,
                                                              testtype        TEXT                NOT NULL DEFAULT None,
                                                              descr           TEXT);                                      

                        CREATE TABLE IF NOT EXISTS lte_params (param_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                                                               testinfo_id     INTEGER             NOT NULL,
                                                               teststep        INTEGER             NOT NULL,
                                                               carrier         TEXT                NOT NULL DEFAULT PCC,
                                                               dmode           TEXT                NOT NULL DEFAULT FDD,
                                                               dlulconf        INTEGER             NOT NULL DEFAULT -1,
                                                               ssconf          INTEGER             NOT NULL DEFAULT -1,
                                                               bwmhz           REAL                NOT NULL,
                                                               rfband          INTEGER             NOT NULL,
                                                               earfcn          INTEGER             NOT NULL,
                                                               cp              TEXT                NOT NULL DEFAULT NORM,                                                              
                                                               tm              INTEGER UNSIGNED    NOT NULL,
                                                               txants          INTEGER UNSIGNED    NOT NULL,
                                                               pmi             UNSIGNED INT        NOT NULL,
                                                               rsepre          REAL                NOT NULL,
                                                               pa              INTEGER             NOT NULL,
                                                               pb              INTEGER             NOT NULL,
                                                               chtype          TEXT                NOT NULL,
                                                               snr             REAL                NOT NULL,
                                                               doppler         REAL                NOT NULL DEFAULT 0,
                                                               schedtype       TEXT                NOT NULL, /* AMC or FIXED */
                                                               dlmcs           INTEGER INSIGNED, 
                                                               dlnprb          INTEGER UNSIGNED,
                                                               dlrbstart       INTEGER UNSIGNED,
                                                               ulmcs           INTEGER UNSIGNED,
                                                               ulnprb          INTEGER UNSIGNED,
                                                               ulrbstart       INTEGER UNSIGNED,
                                                             FOREIGN KEY (testinfo_id) REFERENCES testinfos(testinfo_id));
       
                        CREATE INDEX IF NOT EXISTS param_lookup ON lte_params (bwmhz,
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
                                                              mod_files       INTEGER UNSIGNED    NOT NULL,
                                                              p4webrev        TEXT                NOT NULL DEFAULT None,                                                              
                                                              cmwinfo         TEXT                NOT NULL DEFAULT None,
                                                              modeminfo       TEXT                NOT NULL DEFAULT None);
        
                        CREATE TABLE IF NOT EXISTS lte_results ( result_id       INTEGER PRIMARY KEY AUTOINCREMENT,
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
                                                                 best_dlthr      REAL                NOT NULL DEFAULT 0,
                                                                 best_ulthr      REAL                NOT NULL DEFAULT 0,                                                               
                                                                 tolerance       TEXT                NOT NULL DEFAULT 0,
                                                                 verdict_dl      TEXT                NOT NULL DEFAULT FAIL,
                                                                 verdict_ul      TEXT                NOT NULL DEFAULT FAIL,
                                                                 current_mA      REAL                NOT NULL DEFAULT 0,
                                                                 pwr3p8V_mW      REAL                NOT NULL DEFAULT 0,                                                          
                                                              FOREIGN KEY (testrun_id) REFERENCES testruns(testrun_id),
                                                              FOREIGN KEY (param_id) REFERENCES lte_params(param_id),
                                                              FOREIGN KEY (platform_id) REFERENCES platforms(platform_id));
                                                                    
                        CREATE INDEX IF NOT EXISTS results_lookup ON lte_results(platform_id,param_id);""")
            
                    self.conn.commit()
                    #self.disconnect()
                except sqlite3.OperationalError:
                    logger.error("Error initialising database %s" % self.name)
                    print sys.exc_info()
                    sys.exit(CfgError.ERRCODE_SYS_DATABASE_ERROR)
                else:
                    logger.debug("INITIALIZED database     : %s" % self.name)
  
    def connect(self):
        logger=logging.getLogger('connect')
        if self.conn is None:
            self.conn = sqlite3.connect(self.name)
            logger.debug("CONNECT to database      : %s" % self.name)        

    def disconnect(self):
        logger=logging.getLogger('disconnect')
        if not self.conn is None:
            self.conn.close()
            logger.debug("DISCONNECT from database : %s" % self.name)

    def destroy(self):
        logger=logging.getLogger('destroy')
        if os.path.exists(self.name):
            #logger.debug("FOUND database : %s" % self.name)           
            if not self.conn is None:
                self.disconnect()
            os.remove(self.name)
            logger.debug("DESTROYED database       : %s" % self.name)
           
    # =============================================================================
    # TABLE SPECIFIC FUNCTIONS
    # =============================================================================
    def table_exists(self, tablename):
        logger=logging.getLogger('table_exists')
        try: 
            if self.conn==None: 
                self.connect()   
#            self.cursor.execute("""SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='%s';""" % tablename)
            self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;", (tablename,))
            result=(self.cursor.fetchone()[0] > 0)
        except sqlite3.OperationalError:
            logger.error("TABLE %s.table_exists()" % tablename)
            raise sqlite3.OperationalError
            print sys.exc_info()
            return False
        else:
            return result
                    
    def table_view(self, tablename):
        logger=logging.getLogger('table_view')
        try: 
            if self.table_exists(tablename):                
                # cursor_l = self.conn.execute("""SELECT * FROM %s ORDER BY rowid;""" % (tablename))
                cursor_l = self.conn.execute("""SELECT * FROM %s;""" % (tablename))
                if cursor_l:
                    for cursor in cursor_l: 
                        logger.debug("%s" % list(cursor))
                else:
                    logger.warning('TABLE "%s" EMPTY' % tablename)
            else:
                logger.warning("%s.table_view(): table %s not found" % tablename)        
        except sqlite3.OperationalError:
            logger.error("%s.table_view()" % tablename)
            print sys.exc_info()
            raise sqlite3.OperationalError
        else:
            pass

    # =============================================================================
    # TABLE ENTRY FUNCTIONS
    # =============================================================================
    def get_platform_id(self, platform):
        logger=logging.getLogger('get_platform_id')        
        self.cursor.execute("SELECT platform_id FROM platforms WHERE platform=?", (platform,))
        result=self.cursor.fetchone()[0]
        logger.debug("Platform %s has ID %d",(platform),result)
        return result

    def add_platform(self, platform):
        logger=logging.getLogger('add_platform')        
        try:
            return self.get_platform_id(platform)
        except TypeError:
            self.cursor.execute("INSERT INTO platforms(platform) VALUES (?)",(platform,))
            logger.debug("Created platform record for %s...",(platform))
            return self.get_platform_id(platform)
    
    def get_testinfo_id(self, testid):
        logger=logging.getLogger('get_testinfo_id')
        self.cursor.execute("SELECT testinfo_id FROM testinfos WHERE testid=?", (testid,))
        result=self.cursor.fetchone()[0]
        logger.debug("testid %s has ID %d", testid, result)
        return result

    def add_testinfo(self, testid, testtype, descr):
        logger=logging.getLogger('add_testinfo')
        try:
            return self.get_testinfo_id(testid)
        except TypeError:
            self.cursor.execute("INSERT INTO testinfos(testid, testtype, descr) VALUES (?,?,?)", (testid, testtype, descr))
            logger.debug("Created testinfo record for %s...",(testid, testtype, descr))
            return self.get_testinfo_id(testid)

    def get_testrun_id(self, timestamp, branch, clnum, mod_files, p4webrev):
        logger=logging.getLogger('get_testrun_id')
        self.cursor.execute("SELECT testrun_id FROM testruns WHERE timestamp=? AND branch=? AND clnum=? AND mod_files=? AND p4webrev=?", (timestamp, branch, clnum, mod_files, p4webrev))
        result=self.cursor.fetchone()[0]
        logger.debug("Test run %s has ID %d",(timestamp, branch, clnum, mod_files, p4webrev), result)
        return result

    def add_testrun(self, timestamp, branch, clnum, mod_files, p4webrev, cmwinfo, modeminfo):
        logger=logging.getLogger('add_testrun')
        try:
            return self.get_testrun_id(timestamp, branch, clnum, mod_files, p4webrev)
        except TypeError:
            logger.debug("Create testrun record for %s", (timestamp, branch, clnum, mod_files, p4webrev, cmwinfo, modeminfo))
            self.cursor.execute("INSERT INTO testruns(timestamp, branch, clnum, mod_files, p4webrev, cmwinfo, modeminfo) VALUES (?,?,?,?,?,?,?)",(timestamp, branch, clnum, mod_files, p4webrev, cmwinfo, modeminfo))
            return self.get_testrun_id(timestamp, branch, clnum, mod_files, p4webrev)

    def __str__(self):
        print "---------------------------------------" 
        print "  file_database                     : %s" % self.name
        print "  conn                        : %s" % self.conn
        print "  cursor                      : %s" % self.cursor
        return ""


if __name__ == '__main__':

    from Struct import Struct
    from cfg_multilogging import cfg_multilogging
    cfg_multilogging('DEBUG', 'DatabasePl1Testbench.LOG')
    logger=logging.getLogger('DatabasePl1Testbench')
    
    t0=time.localtime()
    
    # Define folders hierarchy
    dir_root           =os.sep.join(os.environ['PL1TESTBENCH_ROOT_FOLDER'].split(os.sep)[:])
    dir_database       =os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database'])
    dir_export         =os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database', 'export'])
    dir_import         =os.sep.join(dir_root.split(os.sep)[:]+['lte', 'common','report','sqllite', 'database', 'import']) 
    #file_database      =os.sep.join(dir_database.split(os.sep)[:]+['perf_bestscore_20140909_Win8.db'])
    file_database      =os.sep.join(dir_database.split(os.sep)[:]+['pl1testbench_lte_20140909_Linux.db'])
        

    #logger=cfg_logger_root('DEBUG', log_file)    
    logger.info("FOLDER HIERARCHY  :")
    logger.info("------------------------------------")
    logger.info("dir_root          : %s" % dir_root)
    logger.info("dir_database      : %s" % dir_database)
    logger.info("dir_export        : %s" % dir_export)                              
    logger.info("FILES         :")
    logger.info("------------------------------------")
    logger.info("file_database            : %s"  % file_database)
    
              
    if 1:  
        logger.debug(">> Check table existence")
        logger.debug("---------------------------------------") 
        db_h=DatabasePl1Testbench(file_database)
        logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_PLATFORMS, db_h.table_exists(db_h.TABLE_PLATFORMS)))
        logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_TESTINFOS, db_h.table_exists(db_h.TABLE_TESTINFOS)))
        logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_TESTRUNS, db_h.table_exists(db_h.TABLE_TESTRUNS)))
        logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_LTE_PARAMS, db_h.table_exists(db_h.TABLE_LTE_PARAMS)))
        logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_LTE_RESULTS, db_h.table_exists(db_h.TABLE_LTE_RESULTS)))
        #logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_GSM_PARAMS, db_h.table_exists(db_h.TABLE_GSM_PARAMS)))
        #logger.debug('TABLE "%s" exists? %s' % (db_h.TABLE_GSM_RESULTS, db_h.table_exists(db_h.TABLE_GSM_RESULTS)))        
        db_h.disconnect()
        del db_h
    
    if 1:
        logger.debug(">> Check table view")
        logger.debug("---------------------------------------") 
        db_h=DatabasePl1Testbench(file_database)
        db_h.table_view(db_h.TABLE_PLATFORMS)
        db_h.table_view(db_h.TABLE_TESTINFOS)
        db_h.table_view(db_h.TABLE_LTE_PARAMS)
        db_h.table_view(db_h.TABLE_TESTRUNS)
        db_h.table_view(db_h.TABLE_LTE_RESULTS)
        #db_h.table_view(db_h.TABLE_GSM_PARAMS)
        #db_h.table_view(db_h.TABLE_GSM_RESULTS)
        db_h.disconnect()
        del db_h

            
    t1=time.localtime()
    dt=time.mktime(t1)-time.mktime(t0)                             
    logger.info("Time duration %d[sec]" % dt)
           
   
    
        

    
