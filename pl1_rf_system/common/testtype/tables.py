et_atcmd_table = {
# atcmd                           params,          regfieldname,    regfieldvalue,      ... more pairs of field name + value ...
 'IETENABLE='     : [               'ON',             'TX_ETDACEN',             1,          'IL_TX_APTMODE',   0],
 'IETVCM='        : [                  3,         'TX_ETDACVCMSEL',             3],
 'IETLUTVIN='     : [ '205,710,899,1023',       'IL_TXET_SET0_PT1',           205,       'IL_TXET_SET0_PT2', 710,       'IL_TXET_SET0_PT3', 899,       'IL_TXET_SET0_PT4', 1023],
 'IETLUTVOUT='    : [      '100,200,300',    'IL_TXET_SET0_VALPT1',           100,    'IL_TXET_SET0_VALPT2', 200,    'IL_TXET_SET0_VALPT4', 300],
 'IETLUTSLOPE='   : [                 80,       'IL_TXET_SET0_SLP',            80],         
 'IETLUTGIN='     : [              -3000,                 'POSGN0',             0,                  'CRGN0',   6,                  'FNGN0',   72],
 'IETLUTGOUT='    : [                300,                 'POSGN1',             1,                  'CRGN1',   0,                  'FNGN1',   300],
 'IETLUTOPOS='    : [                999,          'IL_TXET_DCOFF',          1998],
 'IETLUTCURVEL='  : ['0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63', 'IL_TXET_SET0_LUTOD1_0',  1, 'IL_TXET_SET0_LUTOD1_31',  63, 'IL_TXET_SET0_LUTEV1_0', 0, 'IL_TXET_SET0_LUTEV1_31', 62],
 'IETLUTCURVEU='  : ['0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63', 'IL_TXET_SET0_LUTOD2_0',  1, 'IL_TXET_SET0_LUTOD2_31',  63, 'IL_TXET_SET0_LUTEV2_0', 0, 'IL_TXET_SET0_LUTEV2_31', 62],
 'IETDELAYS='     : [            '85000',        'IL_TX_DADJ4_BYP',             0,        'IL_TX_DADJ4_DEL',  10,   'IL_TXET_BYPFDELAY',  0,   'IL_TXET_MU',   74],
}

et_atcmd_etm_table = {
# atcmd                           params,     address,    shift,  mask,   value,
 'IETMAXVCC='     : [               0x2B,         0x1,      0x0,  0x7F,    0x2B],
 'IETBW='         : [            '20MHZ',         0x2,      0x4,   0x3,     0x3],
 'IETTXRX='       : [                0x2,         0x0,      0x0,   0x3,     0x2],
}
