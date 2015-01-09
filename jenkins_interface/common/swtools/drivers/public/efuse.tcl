proc decode_efuse {} {
    set wasQuiet [options -quiet]

    set addr [expr $::livanto_memmap::CHPC_BASE + $::livanto_memmap::CHPC_EFUSE_STATE_0_OFFSET]

    puts [format "Decoding eFuses: (0x%.8x)" $addr]

    if { $::_dxpCPUType == "ICE8060-A0" } {
        #eFuse 0
        set val [expr [peek 4 [expr $addr + 0]] & 0xffffffff]
        set efuse0 $val
        set efuse_debug1     [expr ($efuse0 >> 0) & 0x01]
        set efuse_bs1        [expr ($efuse0 >> 1) & 0x01]
        set efuse_sparelock  [expr ($efuse0 >> 2) & 0x01]
        set efuse_debuglog1  [expr ($efuse0 >> 3) & 0x01]
        set efuse_avsrev     [expr ($efuse0 >> 10) & 0x3FF]
        set efuse_sispeed    [expr ($efuse0 >> 20) & 0x0F]
        set efuse_hkadccal   [expr ($efuse0 >> 24) & 0x3F]
        set efuse_hwidscheme [expr ($efuse0 >> 30) & 0x03]

        #eFuse 1
        set val [expr [peek 4 [expr $addr + 4]] & 0xffffffff]
        set efuse1 $val
        set efuse_numdie      [expr ($efuse1 >> 0) & 0x07]
        set efuse_die1ver     [expr ($efuse1 >> 3) & 0x0F]
        set efuse_die2id      [expr ($efuse1 >> 7) & 0x0F]
        set efuse_die2ver     [expr ($efuse1 >> 11) & 0x0F]
        set efuse_die3id      [expr ($efuse1 >> 15) & 0x0F]
        set efuse_die3ver     [expr ($efuse1 >> 19) & 0x0F]
        set efuse_ws2ftmarker [expr ($efuse1 >> 23) & 0x01]
        set efuse_chipcap     [expr ($efuse1 >> 24) & 0xFF]

        #eFuse 2
        set val [expr [peek 4 [expr $addr + 8]] & 0xffffffff]
        set efuse2 $val
        set efuse_debuglog0   [expr ($efuse2 >> 14) & 0x01]
        set efuse_bs0         [expr ($efuse2 >> 15) & 0x01]
        set efuse_debug0      [expr ($efuse2 >> 16) & 0x01]
        set efuse_idlock      [expr ($efuse2 >> 17) & 0x01]
        set efuse_chipid_2    [expr ($efuse2 >> 18) & 0x03FFF]

        #eFuse 3
        set val [expr [peek 4 [expr $addr + 12]] & 0xffffffff]
        set efuse3 $val
        set efuse_chipid_3    [expr $efuse3]

        #eFuse 4
        set val [expr [peek 4 [expr $addr + 16]] & 0xffffffff]
        set efuse4 $val
        set efuse_chipid_4    [expr ($efuse4 >> 0) & 0x1F]
        set efuse_ramctrl     [expr ($efuse4 >> 5) & 0x03FF]
        set efuse_ramlock     [expr ($efuse4 >> 15) & 0x01]

        #eFuse 5
        set val [expr [peek 4 [expr $addr + 20]] & 0xffffffff]
        set efuse5 $val
        set efuse_cfgword0    [expr ($efuse5 >> 0) & 0x0FFFFF]
        set efuse_cfgword1_5  [expr ($efuse5 >> 20) & 0x0FFF]

        #eFuse 6
        set val [expr [peek 4 [expr $addr + 24]] & 0xffffffff]
        set efuse6 $val
        set efuse_cfgword1_6  [expr ($efuse6 >> 0) & 0x0FF]
        set efuse_cfgword2    [expr ($efuse6 >> 8) & 0x0FFFFF]
        set efuse_cfgword3_6  [expr ($efuse6 >> 28) & 0x0F]

        #eFuse 7
        set val [expr [peek 4 [expr $addr + 28]] & 0xffffffff]
        set efuse7 $val
        set efuse_cfgword3_7  [expr ($efuse7 >> 0) & 0x0FFFF]
        set efuse_cfgword4_7  [expr ($efuse7 >> 16) & 0x0FFFF]

        #eFuse 8
        set val [expr [peek 4 [expr $addr + 32]] & 0xffffffff]
        set efuse8 $val
        set efuse_cfgword4_8  [expr ($efuse8 >> 0) & 0x0F]
        set efuse_cfgword5    [expr ($efuse8 >> 4) & 0x0FFFFF]
        set efuse_cfgword6_8  [expr ($efuse8 >> 24) & 0x0FF]

        #eFuse 9
        set val [expr [peek 4 [expr $addr + 36]] & 0xffffffff]
        set efuse9 $val
        set efuse_cfgword6_9  [expr ($efuse9 >> 0) & 0x0FFF]
        set efuse_cfgword7    [expr ($efuse9 >> 12) & 0x0FFFFF]

        #eFuse 10
        set val [expr [peek 4 [expr $addr + 40]] & 0xffffffff]
        set efuse10 $val
        set efuse_cfgword8    [expr ($efuse10 >> 0) & 0x0FFFFF]
        set efuse_cfgword9_10 [expr ($efuse10 >> 20) & 0x0FFF]

        #eFuse 11
        set val [expr [peek 4 [expr $addr + 44]] & 0xffffffff]
        set efuse11 $val
        set efuse_cfgword9_11  [expr ($efuse11 >> 0) & 0x0FF]
        set efuse_cfgword10    [expr ($efuse11 >> 8) & 0x0FFFFF]
        set efuse_cfgword11_11 [expr ($efuse11 >> 28) & 0x00F]

        #eFuse 12
        set val [expr [peek 4 [expr $addr + 48]] & 0xffffffff]
        set efuse12 $val
        set efuse_cfgword11_12 [expr ($efuse11 >> 0) & 0x0FFFF]

        #eFuse 13
        set val [expr [peek 4 [expr $addr + 52]] & 0xffffffff]
        set efuse13 $val
        set efuse_xipdis      [expr ($efuse13 >> 0) & 0x03]
        set efuse_authen      [expr ($efuse13 >> 2) & 0x03]
        set efuse_rsakeydis   [expr ($efuse13 >> 4) & 0x03F]
        set efuse_bypasspll   [expr ($efuse13 >> 11) & 0x01]
        set efuse_disablecksq [expr ($efuse13 >> 12) & 0x01]
        set efuse_disableckout0 [expr ($efuse13 >> 13) & 0x01]
        set efuse_hsiflushmux [expr ($efuse13 >> 14) & 0x01]

        #eFuse 14
        set val [expr [peek 4 [expr $addr + 56]] & 0xffffffff]
        set efuse14 $val
        set efuse_crc16_a     [expr ($efuse14 >> 0) & 0x0FFFF]
        set efuse_crc16_b     [expr ($efuse14 >> 16) & 0x0FFFF]

        #eFuse 15
        set val [expr [peek 4 [expr $addr + 60]] & 0xffffffff]
        set efuse15 $val
        set efuse_crc16_c     [expr ($efuse15 >> 0) & 0x0FFFF]
        set efuse_crc16_d     [expr ($efuse15 >> 16) & 0x0FFFF]

        #eFuse 53
        set val [expr [peek 4 [expr $addr + 212]] & 0xffffffff]
        set efuse_ext_chipid_1 $val

        #eFuse 54
        set val [expr [peek 4 [expr $addr + 216]] & 0xffffffff]
        set efuse_ext_chipid_2 $val

        #eFuse 55
        set val [expr [peek 4 [expr $addr + 220]] & 0xffffffff]
        set efuse_ext_chipid_3 [expr ($val >> 16) & 0x1fff]

        # Construct multi-line values:
        set efuse_chipid_ls [expr ($efuse_chipid_2 | ($efuse_chipid_3 << 14)) & 0xFFFFFFFF]
        set efuse_chipid_ms [expr (($efuse_chipid_3 & 0xFFFC0000) >> 0x18) | ($efuse_chipid_4 << 14)]
        set efuse_cfgword1  [expr $efuse_cfgword1_5   | ($efuse_cfgword1_6 << 12)]
        set efuse_cfgword3  [expr $efuse_cfgword3_6   | ($efuse_cfgword4_7 << 4)]
        set efuse_cfgword4  [expr $efuse_cfgword4_7   | ($efuse_cfgword4_8 << 16)]
        set efuse_cfgword6  [expr $efuse_cfgword6_8   | ($efuse_cfgword6_9 << 8)]
        set efuse_cfgword9  [expr $efuse_cfgword9_10  | ($efuse_cfgword9_11 << 12)]
        set efuse_cfgword11 [expr $efuse_cfgword11_11 | ($efuse_cfgword11_12 << 4)]

        if { [expr ($efuse0  == 0) && ($efuse1  == 0) && ($efuse2  == 0) && ($efuse3  == 0) && \
                   ($efuse4  == 0) && ($efuse5  == 0) && ($efuse6  == 0) && ($efuse7  == 0) && \
                   ($efuse8  == 0) && ($efuse9  == 0) && ($efuse10 == 0) && ($efuse11 == 0) && \
                   ($efuse12 == 0) && ($efuse13 == 0) && ($efuse14 == 0) && ($efuse15 == 0)] } {
            puts "  WARNING: eFuses are not programmed."
        } else {
            # Display eFuses
            puts ""
            puts "BootROM eFuses:"
            puts [format "  Config Word (00) 0x%.8x" $efuse_cfgword0]
            puts [format "  Config Word (01) 0x%.8x" $efuse_cfgword1]
            puts [format "  Config Word (02) 0x%.8x" $efuse_cfgword2]
            puts [format "  Config Word (03) 0x%.8x" $efuse_cfgword3]
            puts [format "  Config Word (04) 0x%.8x" $efuse_cfgword4]
            puts [format "  Config Word (05) 0x%.8x" $efuse_cfgword5]
            puts [format "  Config Word (06) 0x%.8x" $efuse_cfgword6]
            puts [format "  Config Word (07) 0x%.8x" $efuse_cfgword7]
            puts [format "  Config Word (08) 0x%.8x" $efuse_cfgword8]
            puts [format "  Config Word (09) 0x%.8x" $efuse_cfgword9]
            puts [format "  Config Word (10) 0x%.8x" $efuse_cfgword10]
            puts [format "  Config Word (11) 0x%.8x" $efuse_cfgword11]
            puts [format "  RAM Lock         %d" $efuse_ramlock]
            puts [format "  XIP Disable      0x%x" $efuse_xipdis]
            puts [format "  Auth Enable      0x%x" $efuse_authen]
            puts [format "  RSA Key Disable  0x%.2x" $efuse_rsakeydis]
            puts [format "  Bypass PLL Init  %d" $efuse_bypasspll]
            puts [format "  Disable Clk Sq   %d" $efuse_disablecksq]
            puts [format "  Disable ClkOut0  %d" $efuse_disableckout0]

            puts ""
            puts "Silicon Settings:"
            puts [format "  Debug            (0) %d, (1) %d" $efuse_debug0 $efuse_debug1]
            puts [format "  Debug Log        (0) %d, (1) %d" $efuse_debuglog0 $efuse_debuglog1]
            puts [format "  Boundary Scan    (0) %d, (1) %d" $efuse_bs0 $efuse_bs1]
            puts [format "  Spare Lock       %d" $efuse_sparelock]
            puts [format "  ID Lock          %d" $efuse_idlock]
            puts [format "  Chip ID          0x%.8x%.8x" $efuse_chipid_ms $efuse_chipid_ls]
            puts [format "  Extended Chip ID 0x%.8x%.8x%.8x" $efuse_ext_chipid_3 $efuse_ext_chipid_2 $efuse_ext_chipid_1]
            puts [format "  RAM Control      0x%.3x" $efuse_ramctrl]
            puts [format "  HSI Flush Mux    %d" $efuse_hsiflushmux]

            puts ""
            puts "HW Revision information:"
            puts [format "  Scheme        %d" $efuse_hwidscheme]
            if { $efuse_hwidscheme == 1 } {
                puts [format "  Num Die       %d" $efuse_numdie]
                puts [format "  Die 1 Version 0x%x" $efuse_die1ver]
                puts [format "  Die 2 ID      0x%x" $efuse_die2id]
                puts [format "  Die 2 Version 0x%x" $efuse_die2ver]
                puts [format "  Die 3 ID      0x%x" $efuse_die3id]
                puts [format "  Die 3 Version 0x%x" $efuse_die3ver]
            }

            puts ""
            puts "Other information:"
            puts [format "  AVS Revision        0x%.3x" $efuse_avsrev]
            puts [format "  Si Speed            0x%.1x" $efuse_sispeed]
            puts [format "  HK ADC Cal          0x%.2x" $efuse_hkadccal]
            puts [format "  Chip Capabilities   0x%.2x" $efuse_chipcap]

            puts ""
            puts "CRCs:"
            puts [format "  CRC16 A    0x%.4x" $efuse_crc16_a]
            puts [format "  CRC16 B    0x%.4x" $efuse_crc16_b]
            puts [format "  CRC16 C    0x%.4x" $efuse_crc16_c]
            puts [format "  CRC16 D    0x%.4x" $efuse_crc16_d]

#        puts "Checking CRCs..."
#TODO: Check CRCs.
        }
    } 
    if {$wasQuiet == 0} {
      options -nquiet
    }
}
