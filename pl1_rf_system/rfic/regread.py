import os, platform


def get_reg_info_from_map (fieldname):

    foundshift = False
    foundmask = False

    platform_details = platform.uname()
    os_name = platform_details[0]

    if os_name == 'Linux':
        regmapname = '/../../../../../tools/rf_drivers/rfic_scripts/vesta/Docs/vesta_spec_sw.txt'
    else:
        regmapname = '\\..\\..\\..\\..\\..\\tools\\rf_drivers\\rfic_scripts\\vesta\\Docs\\vesta_spec_sw.txt'

    regmappath = os.environ['PL1_RF_SYSTEM_ROOT'] + regmapname
    f_regmap   = open(regmappath, 'r')
    for line in f_regmap:
        if fieldname + '_SHIFT' in line:
            shiftstring = line
            foundshift = True
            break
    for line in f_regmap:
        if fieldname + '_MASK' in line:
            maskstring = line
            foundmask = True
            break

    if foundshift and foundmask:
        #shift = shiftstring.split('(')[-1].split('x')[-1].split(')')[0]
        #mask = maskstring.split('(')[-1].split('x')[-1].split(')')[0]
        shift = shiftstring.split('(')[-1].split(')')[0]
        mask = maskstring.split('(')[-1].split(')')[0]
        return int(shift, 0), int(mask, 0)
    else:
        raise Exception("Can't find field " + fieldname + " in regmap")


def get_register_address (fieldname):

    platform_details = platform.uname()
    os_name = platform_details[0]

    if os_name == 'Linux':
        regmapname = '/../../../../../tools/rf_drivers/rfic_scripts/vesta/Docs/vesta_spec_sw.txt'
    else:
        regmapname = '\\..\\..\\..\\..\\..\\tools\\rf_drivers\\rfic_scripts\\vesta\\Docs\\vesta_spec_sw.txt'

    regmappath = os.environ['PL1_RF_SYSTEM_ROOT'] + regmapname

    f_regmap   = open(regmappath, 'r')

    registerlist = f_regmap.read().split('@')
    for item in registerlist:
        if fieldname in item:
            break

    f_regmap.close()

    return int(item.split()[0])


def verify_field_val (modemObj, fieldname, expectedfieldval):

    cmd_l = ['AT%IPRPR=SPI_RADIO,,1,' + str(get_register_address(fieldname))]
    msg = modemObj.sendCmdList(cmd_l, ret_msg_only=True)
    registerreadval = int(msg.splitlines()[2].split(' = ')[-1], 0)

    shift, mask = get_reg_info_from_map(fieldname)
    regval = registerreadval
    fieldval = (regval >> shift) & mask

    if (fieldval != expectedfieldval):
        print 'field name', fieldname, 'expected field val', expectedfieldval, 'actual field val', fieldval, 'test result', (fieldval == expectedfieldval)

    return (fieldval == expectedfieldval)



def verify_etm_field_val (modemObj, regaddress, shift, mask, expectedfieldval):

    cmd_l = ['AT%IPRPR=MRFFE0,5,0,' + str(regaddress)]
    msg = modemObj.sendCmdList(cmd_l, ret_msg_only=True)
    registerreadval = int(msg.splitlines()[2].split(' = ')[-1], 0)
    regval = registerreadval
    fieldval = (regval >> shift) & mask

    if (fieldval != expectedfieldval):
        print 'regaddress', regaddress, 'shift', shift, 'mask', mask, 'expected field val', expectedfieldval, 'actual field val', fieldval, 'test result', (fieldval == expectedfieldval)

    return (fieldval == expectedfieldval)
