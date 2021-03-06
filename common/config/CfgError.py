'''
Created on 5 Aug 2013

@author: fsaracino
'''

# ********************************************************************************************
# Error table definition
# ********************************************************************************************
class CfgError(object):
    #Test errors
    ERRCODE_TEST_PASS                 = 0
    ERRCODE_TEST_FAILURE              = 1
    ERRCODE_TEST_TIMEOUT              = 2
    ERRCODE_TEST_PARAM_INVALID        = 3

    ERRCODE_TEST_FAILURE_REFTHR       = 4
    ERRCODE_TEST_FAILURE_ATTACH       = 5
    ERRCODE_TEST_FAILURE_CEST         = 6
    ERRCODE_TEST_FAILURE_INTRAHO      = 7
    ERRCODE_TEST_FAILURE_PARAMCONFIG  = 8
    ERRCODE_TEST_FAILURE_INCONCLUSIVE = 9

    ERRCODE_TEST_UNKNOWN_JOBTYPE      = 10
    ERRCODE_TEST_RF_FAILURE           = 11
    ERRCODE_TEST_RF_INCONCLUSIVE      = 12

	# WCDMA	errors
    ERRCODE_TEST_FAILURE_GENERAL      = 20
    ERRCODE_TEST_FAILURE_BLER         = 21
    ERRCODE_TEST_FAILURE_TESTCONFIG   = 22
    ERRCODE_TEST_FAILURE_INTERBANDHO  = 23
    ERRCODE_TEST_FAILURE_BAND_ENABLE  = 24

    # System errors
    ERRCODE_SYS_CMW_CONN                 = 30
    ERRCODE_SYS_CMW_INVMEAS              = 31
    ERRCODE_SYS_CMW_TIMEOUT              = 32
    ERRCODE_SYS_CMW_CONNECTION_LOST      = 33
    ERRCODE_SYS_CMW_INCORRECT_SW_VERSION = 34
    ERRCODE_SYS_CMW_SCPI_FAILURE         = 35
    ERRCODE_SYS_CMW_PARAM_CHECK          = 36
    ERRCODE_SYS_SERIAL_CONN              = 37
    ERRCODE_SYS_SOCKET_CONN              = 38
    ERRCODE_SYS_FILE_IO                  = 39
    ERRCODE_SYS_DUT_TIMEOUT              = 40
    ERRCODE_SYS_ICAL_FAILURE             = 41
    ERRCODE_SYS_ICAL_PARAMCONFIG         = 42
    ERRCODE_SYS_PSU_CONNECTION_FAILURE   = 43
    ERRCODE_SYS_PSU_FAILURE              = 44
    ERRCODE_SYS_COM_FAILURE              = 45
    ERRCODE_SYS_OS_ERROR                 = 46
    ERRCODE_SYS_DATABASE_ERROR           = 47
    ERRCODE_SYS_DATABASE_CONN_FAILURE    = 48
    ERRCODE_SYS_DATABASE_RD_FAILURE      = 49
    ERRCODE_SYS_DATABASE_WR_FAILURE      = 50
    ERRCODE_SYS_PARAM_INVALID            = 51
    ERRCODE_SYS_ADB_COM_FAILURE          = 52
    ERRCODE_SYS_ADB_CMD_ERROR            = 53
    ERRCODE_SYS_CMW_NO_MEAS              = 54
    ERRCODE_SYS_LOG_FAIL                 = 55
    ERRCODE_SYS_CMW_CELL_ON              = 56
    ERRCODE_SYS_CMW_CONFIG               = 57
    ERRCODE_SYS_MODEM_NO_COM             = 58
    ERRCODE_SYS_CMW_INCORRECT_SW_VERSION = 59



    ERRCODE_SYS_DEBUG_EXIT               = 100
    ERRCODE_SYS_BREAKPOINT               = ERRCODE_SYS_DEBUG_EXIT # for WCDMA
    ERRCODE_TEST_DEBUG                   = ERRCODE_SYS_DEBUG_EXIT # for WCDMA
    ERRCODE_UNHANDLED_EXECEPTION         = 101

    MSG={
        ERRCODE_TEST_PASS                    : 'PASS',
        ERRCODE_TEST_FAILURE                 : 'FAILURE',
        ERRCODE_TEST_TIMEOUT                 : 'TIMEOUT',
        ERRCODE_TEST_PARAM_INVALID           : 'TEST_PARAM_INVALID',
        ERRCODE_TEST_FAILURE_REFTHR          : 'REFERENCE_THROUGHPUT_FAILURE',
        ERRCODE_TEST_FAILURE_ATTACH          : 'ATTACH_FAILURE',
        ERRCODE_TEST_FAILURE_CEST            : 'CONNECTION_ESTABLISHMENT_FAILURE',
        ERRCODE_TEST_FAILURE_INTRAHO         : 'CONNECTION_FAILURE_AFTER_INTRA_CELL_HO',
        ERRCODE_TEST_FAILURE_PARAMCONFIG     : 'TEST_PARAMETER_CONFIGURATION_ERROR',
        ERRCODE_TEST_FAILURE_INCONCLUSIVE    : 'INCONCLUSIVE_TEST_VERDICT',
        ERRCODE_TEST_UNKNOWN_JOBTYPE         : 'ERRCODE_TEST_UNKNOWN_JOBTYPE',
        ERRCODE_TEST_RF_FAILURE              : 'ERRCODE_TEST_RF_FAILURE',
        ERRCODE_TEST_RF_INCONCLUSIVE         : 'ERRCODE_TEST_RF_INCONCLUSIVE',

        ERRCODE_TEST_FAILURE_GENERAL         : 'MULTIPLE_FAILURES',
        ERRCODE_TEST_FAILURE_BLER            : 'BLER_FAILURE',
        ERRCODE_TEST_FAILURE_TESTCONFIG      : 'DL_CHANNELISATION_CODE_CONFLICT',
        ERRCODE_TEST_FAILURE_INTERBANDHO     : 'CONNECTION_FAILURE_AFTER_INTERBAND_CELL_HO',
        ERRCODE_TEST_FAILURE_BAND_ENABLE     : 'AT_BAND_ENABLE_FAILURE',

        ERRCODE_SYS_CMW_CONN                 : 'CMW500_CONNECTION_FAILURE',
        ERRCODE_SYS_CMW_INVMEAS              : 'CMW500_INVALID_MEASUREMENTS',
        ERRCODE_SYS_CMW_TIMEOUT              : 'CMW500_INVALID_TIMEOUT',
        ERRCODE_SYS_CMW_CONNECTION_LOST      : 'UE_CONNECTION_LOST_DURING_MEASUREMENT_PERIOD',
        ERRCODE_SYS_CMW_INCORRECT_SW_VERSION : 'CMW500_INVALID_SW_VERSION_DETECTED',
        ERRCODE_SYS_CMW_SCPI_FAILURE         : 'ERRCODE_SYS_CMW_SCPI_FAILURE',
        ERRCODE_SYS_CMW_PARAM_CHECK          : 'ERRCODE_SYS_CMW_PARAM_CHECK',
        ERRCODE_SYS_SERIAL_CONN              : 'SERIAL_CONNECTION_COMMUNICATION_ERROR',
        ERRCODE_SYS_SOCKET_CONN              : 'SOCKET_CONNECTION_COMMUNICATION_ERROR',
        ERRCODE_SYS_FILE_IO                  : 'FILE_IO_OPERATION_ERROR',

        ERRCODE_SYS_DUT_TIMEOUT              : 'ERRCODE_SYS_DUT_TIMEOUT',
        ERRCODE_SYS_ICAL_FAILURE             : 'ERRCODE_SYS_ICAL_FAILURE',
        ERRCODE_SYS_ICAL_PARAMCONFIG         : 'ERRCODE_SYS_ICAL_PARAMCONFIG',
        ERRCODE_SYS_PSU_CONNECTION_FAILURE   : 'ERRCODE_SYS_PSU_CONNECTION_FAILURE',
        ERRCODE_SYS_PSU_FAILURE              : 'ERRCODE_SYS_PSU_FAILURE',
        ERRCODE_SYS_COM_FAILURE              : 'ERRCODE_SYS_COM_FAILURE',
        ERRCODE_SYS_OS_ERROR                 : 'ERRCODE_SYS_OS_ERROR',
        ERRCODE_SYS_DATABASE_ERROR           : 'ERRCODE_SYS_DATABASE_ERROR',
        ERRCODE_SYS_DATABASE_CONN_FAILURE    : 'ERRCODE_SYS_DATABASE_CONN_FAILURE',
        ERRCODE_SYS_DATABASE_RD_FAILURE      : 'ERRCODE_SYS_DATABASE_RD_FAILURE',
        ERRCODE_SYS_DATABASE_WR_FAILURE      : 'ERRCODE_SYS_DATABASE_WR_FAILURE',
        ERRCODE_SYS_PARAM_INVALID            : 'PARAM_INVALID',
        ERRCODE_SYS_DEBUG_EXIT               : 'ERRCODE_SYS_DEBUG_EXIT',
        ERRCODE_SYS_ADB_COM_FAILURE          : 'ERRCODE_SYS_ADB_COM_FAILURE',
        ERRCODE_SYS_ADB_CMD_ERROR            : 'ERRCODE_SYS_ADB_CMD_ERROR',
        ERRCODE_SYS_CMW_NO_MEAS              : 'CMW500_NO_MEASUREMENTS',
        ERRCODE_SYS_CMW_CELL_ON              : 'CMW_CELL_SWITCH_ON_ERROR',
        ERRCODE_SYS_CMW_CONFIG               : 'CMW_CONFIGURATION_ERROR',
        ERRCODE_SYS_MODEM_NO_COM             : 'MODEM_PORT_DETECT_FAILURE',
        ERRCODE_SYS_CMW_INCORRECT_SW_VERSION : 'CMW500_INVALID_SW_VERSION_DETECTED',
        ERRCODE_UNHANDLED_EXECEPTION         : 'UNHANDLED_EXCEPTION'
    }


    def __init__(self):
        pass

if __name__ == '__main__':

    code = CfgError()

    for (k, v) in code.MSG.items():
        print ">> errorcode=%s, description=%s" % (k, v)


