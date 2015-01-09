namespace eval usb_mac {
    variable num_dev_eps 0;
    variable dieptxf "DIEPTXF"; 
    variable has_sg 0; 
    variable has_gpwrdn 0;
    variable has_deachint 0;
    variable has_hsic 0;

}

switch  $_dxpCPUType {
    "ICE8040-A0" 
        { 
            set usb_mac::num_dev_eps 10;
            set usb_mac::dieptxf "DIEPTXF"; 
            set usb_mac::has_sg 0; 
            set usb_mac::has_gpwrdn 0;
            set usb_mac::has_deachint 0;
            set usb_mac::has_hsic 0;

        }
    "ICE8060-A0" 
        { 
            set usb_mac::num_dev_eps 14;
            set usb_mac::dieptxf "DIEPTXF";
            set usb_mac::has_sg 1;
            set usb_mac::has_gpwrdn 1;
            set usb_mac::has_deachint 1;
            set usb_mac::has_hsic 0;
        }
    default
        { 
            set usb_mac::num_dev_eps 16;
            set usb_mac::dieptxf "DIEPTXFN";
            set usb_mac::has_sg 1;
            set usb_mac::has_gpwrdn 1;
            set usb_mac::has_deachint 1;
            set usb_mac::has_hsic 1;
        }
} 

# Internal procedure to read a USB MAC register
proc i_usbr { addr } {
    set value 0
	set usb_addr [expr \$livanto_memmap::USB_BASE + \$livanto_memmap::USB_${addr}_OFFSET]
	set value [peek 4 $usb_addr]
    return $value
}

# Internal procedure to read a USB MAC register from an array
proc i_usbr_a { base index str_sz} {
    set value 0
	set usb_addr [expr \$livanto_memmap::USB_BASE + \$livanto_memmap::USB_${base}_OFFSET + ($index * $str_sz)]
	set value [peek 4 $usb_addr]
    return $value
}

# Internal procedure to write a USB MAC register
proc i_usbw { addr value } {
	set usb_addr [expr \$livanto_memmap::USB_BASE | \$livanto_memmap::USB_${addr}_OFFSET]
	poke 4 $usb_addr $value
}

# Internal procedure to write a USB MAC register
proc i_usbw_a { base index value str_sz} {
	set usb_addr [expr \$livanto_memmap::USB_BASE + \$livanto_memmap::USB_${base}_OFFSET + ($index * $str_sz)]
	poke 4 $usb_addr $value
}


proc get_usb_features {} {

    set reg [i_usbr GHWCFG2]
    set usb_mac::num_dev_eps [expr ( $reg >> 10) & 0xF ]
    puts [format "num_dev_eps = %d" $usb_mac::num_dev_eps ]
    set usb_mac::has_deachint [expr ( $reg >> 20) & 1 ]
    puts [format "has_deachint = %d" $usb_mac::has_deachint ]

    set reg [i_usbr GHWCFG3]
    set usb_mac::has_hsic [expr ( $reg >> 13) & 1 ]
    puts [format "has_hsic = %d" $usb_mac::has_hsic ]

    set reg [i_usbr GHWCFG4]
    set usb_mac::has_sg [expr ( $reg >> 30) & 1 ]
    puts [format "has_sg = %d" $usb_mac::has_sg ]

}

#
# Read USB register
#
help_text "usbr <register_name>" "Read USB register"
proc usbr {reg} {
    set wasQuiet [options -quiet]
    puts [format "USB_$reg = 0x%08X" [i_usbr $reg]]
    if {$wasQuiet == 0} {
      options -nquiet
    }
}

#
# Write USB register
#
help_text "usbw <register_name> <written_value>" "Write USB register"
proc usbw {reg val} {
    set wasQuiet [options -quiet]
    puts [format "USB_$reg = 0x%08X" $val]
    i_usbw $reg $val
    if {$wasQuiet == 0} {
      options -nquiet
    }
}

#
# Dump fifo configuration
#
help_text "usbfifo" "Dump fifo configuration"
proc usbfifo {} {
    global dieptxf

    set wasQuiet [options -quiet]
    set reg [i_usbr GRXFSIZ]
    puts [format "FIFO RX = 0x%04X 32bits length" [expr $reg & 0xFFFF]]
    set reg [i_usbr GNPTXFSIZ]
    puts [format "FIFO TX EP0 = 0x%04X 32bits length (start in 0x%08X)" [expr $reg >> 16] [expr  $reg & 0xFFFF]]
    for {set idx 1} {$idx < 13} {incr idx 1} {
#        set reg [i_usbr [expr DIEPTXF0 | $idx * 4]]
        set reg [i_usbr $usb_mac::dieptxf$idx]
        puts [format "FIFO TX EP$idx = 0x%04X 32bits length (start in 0x%08X)" [expr $reg >> 16] [expr  $reg & 0xFFFF]]
    }
    if {$wasQuiet == 0} {
      options -nquiet
    }
}

proc waitulpidone {reg} {
    for {set idx 0} {$idx < 10000} {incr idx 1} {
        set value [i_usbr $reg]
        puts [format "waitulpidone: 0x%08X" $value]
        set done [expr  $value & 0x08000000]
        if {$done == 0x08000000} {
          set idx 10000
        }
    }
    if {$done == 0} {
        puts [format "ULPI timeout: 0x%08X" $value]
    }
}

#
# Write ULPI register
#
help_text "ulpiw <addr> <data>" "Write ULPI register"
proc ulpiw {addr data} {
    set wasQuiet [options -quiet]
    i_usbw GPVNDCTL [expr 0x02400000 | (($addr & 0x3F) << 16) | ($data & 0xFF)]
    waitulpidone GPVNDCTL
    set value [i_usbr GPVNDCTL]
    puts [format "Write PHY at 0x%02X: 0x%02X" $addr $data]
    if {$wasQuiet == 0} {
      options -nquiet
    }
}

#
# Read ULPI register
#
help_text "ulpir <addr>" "Read ULPI register"
proc ulpir {addr} {
    set wasQuiet [options -quiet]
    i_usbw GPVNDCTL [expr 0x02000000 | (($addr & 0x3F) << 16)]
    waitulpidone GPVNDCTL
    set value [i_usbr GPVNDCTL]
    puts [format "Read PHY at 0x%02X: 0x%02X" $addr [expr ($value & 0xFF)]]
    if {$wasQuiet == 0} {
      options -nquiet
    }
}

# Decode GINTSTS value
proc decode_gintsts { gintsts } {
    set str "("
    for { set i 1 } { $i <= 32 } { incr i } {
        set value [expr ($gintsts >> (32-$i)) & 0x1]
        if { $i < 32 } {
            set str [format "%s%d;" $str $value]
        } else {
            set str [format "%s%d)" $str $value]
        }
    }
    return $str
}

#
# Dump USB Core Global registers
#
help_text "usbcore" "Dump USB Core Global registers"
proc usbcore {} {

    set wasQuiet [options -quiet]
    
    set gotgctl   [i_usbr GOTGCTL]
    set gotgint   [i_usbr GOTGINT]
    set gahbcfg   [i_usbr GAHBCFG]
    set gusbcfg   [i_usbr GUSBCFG]
    set grstctl   [i_usbr GRSTCTL]
    set gintsts   [i_usbr GINTSTS]
    set gintmsk   [i_usbr GINTMSK]
    set grxstsr   [i_usbr GRXSTSR]
    set grxstsp   [i_usbr GRXSTSP]
    set grxfsiz   [i_usbr GRXFSIZ]
    set gnptxfsiz [i_usbr GNPTXFSIZ]
    set gnptxsts  [i_usbr GNPTXSTS]
#    set gi2cctl   [i_usbr GI2CCTL]
    set gpvndctl  [i_usbr GPVNDCTL]
#    set ggpio     [i_usbr GGPIO]
#    set guid      [i_usbr GUID]
    set gsnpsid   [i_usbr GSNPSID]
    set ghwcfg1   [i_usbr GHWCFG1]
    set ghwcfg2   [i_usbr GHWCFG2]
    set ghwcfg3   [i_usbr GHWCFG3]
    set ghwcfg4   [i_usbr GHWCFG4]
    if { $usb_mac::has_gpwrdn == 1 } {
        set gpwrdn      [i_usbr GPWRDN]
        set gdfifocfg   [i_usbr GDFIFOCFG]
        set gphytest    [i_usbr GDFIFOCFG]
        set ghwsyncmsk  [i_usbr GDFIFOCFG]
        set giceramtest [i_usbr GDFIFOCFG]
    }
    set hptxfsiz  [i_usbr HPTXFSIZ]

    set dieptxfn {0}
    for { set i 1 } { $i < $usb_mac::num_dev_eps } { incr i } {
        lappend dieptxfn [i_usbr $usb_mac::dieptxf$i]
    }

    puts [format "GOTGCTL   0x%.8x = 0x%.8x" $livanto_memmap::USB_GOTGCTL_OFFSET $gotgctl]
    puts [format "GOTGINT   0x%.8x = 0x%.8x" $livanto_memmap::USB_GOTGINT_OFFSET $gotgint]
    puts [format "GAHBCFG   0x%.8x = 0x%.8x" $livanto_memmap::USB_GAHBCFG_OFFSET $gahbcfg]
    puts [format "GUSBCFG   0x%.8x = 0x%.8x" $livanto_memmap::USB_GUSBCFG_OFFSET $gusbcfg]
    puts [format "GRSTCTL   0x%.8x = 0x%.8x" $livanto_memmap::USB_GRSTCTL_OFFSET $grstctl]
    puts [format "GINTSTS   0x%.8x = 0x%.8x %s" $livanto_memmap::USB_GINTSTS_OFFSET $gintsts [decode_gintsts $gintsts]]
    puts [format "GINTMSK   0x%.8x = 0x%.8x" $livanto_memmap::USB_GINTMSK_OFFSET $gintmsk]
    puts [format "GRXSTSR   0x%.8x = 0x%.8x" $livanto_memmap::USB_GRXSTSR_OFFSET $grxstsr]
    puts [format "GRXSTSP   0x%.8x = 0x%.8x" $livanto_memmap::USB_GRXSTSP_OFFSET $grxstsp]
    puts [format "GRXFSIZ   0x%.8x = 0x%.8x" $livanto_memmap::USB_GRXFSIZ_OFFSET $grxfsiz]
    puts [format "GNPTXFSIZ 0x%.8x = 0x%.8x" $livanto_memmap::USB_GNPTXFSIZ_OFFSET $gnptxfsiz]
    puts [format "GNPTXSTS  0x%.8x = 0x%.8x" $livanto_memmap::USB_GNPTXSTS_OFFSET $gnptxsts]
#    puts [format "GI2CCTL   0x%.8x = 0x%.8x" $livanto_memmap::USB_GI2CCTL_OFFSET $gi2cctl]
    puts [format "GPVNDCTL  0x%.8x = 0x%.8x" $livanto_memmap::USB_GPVNDCTL_OFFSET $gpvndctl]
#    puts [format "GGPIO     0x%.8x = 0x%.8x" $livanto_memmap::USB_GGPIO_OFFSET $ggpio]
#    puts [format "GUID      0x%.8x = 0x%.8x" $livanto_memmap::USB_GUID_OFFSET $guid]
    puts [format "GSNPSID   0x%.8x = 0x%.8x" $livanto_memmap::USB_GSNPSID_OFFSET $gsnpsid]
    puts [format "GHWCFG1   0x%.8x = 0x%.8x" $livanto_memmap::USB_GHWCFG1_OFFSET $ghwcfg1]
    puts [format "GHWCFG2   0x%.8x = 0x%.8x" $livanto_memmap::USB_GHWCFG2_OFFSET $ghwcfg2]
    puts [format "GHWCFG3   0x%.8x = 0x%.8x" $livanto_memmap::USB_GHWCFG3_OFFSET $ghwcfg3]
    puts [format "GHWCFG4   0x%.8x = 0x%.8x" $livanto_memmap::USB_GHWCFG4_OFFSET $ghwcfg4]

    if { $usb_mac::has_gpwrdn == 1 } {
        puts [format "GPWRDN   0x%.8x = 0x%.8x" $livanto_memmap::USB_GPWRDN_OFFSET $gpwrdn]
    }
    puts [format "HPTXFSIZ  0x%.8x = 0x%.8x" $livanto_memmap::USB_HPTXFSIZ_OFFSET $hptxfsiz]

    for { set i 1 } { $i < $usb_mac::num_dev_eps } { incr i } {
        puts [format "DIEPTXF%d  0x%.8x = 0x%.8x" $i [expr \$livanto_memmap::USB_${usb_mac::dieptxf}${i}_OFFSET] [lindex $dieptxfn $i]]
    }

    if {$wasQuiet == 0} {
        options -nquiet
    }
}

# Decode DIEPCTL/DOEPCTL value
proc decode_dioepctl { dioepctl index } {
    # EP0 has a different formula for MPS since it is always a CTRL EP
    if { $index == 0 } {
        set mps [expr (0x8 << (~($dioepctl & 0x3) & 0x3))] 
    } else {
        set mps [expr $dioepctl & 0x7FF]
    }
    set next_ep [expr ( $dioepctl >> 11 ) & 0xF]
    set active [expr ( $dioepctl >> 15 ) & 0x1]
    set pid [expr ( $dioepctl >> 16 ) & 0x1]
    set nak [expr ( $dioepctl >> 17 ) & 0x1]
    set ep_type [expr ( $dioepctl >> 18 ) & 0x3]
    set ep_type_str "????"
    if { $ep_type == 0 } {
        set ep_type_str "CTRL"
    }
    if { $ep_type == 1 } {
        set ep_type_str "ISOC"
    }
    if { $ep_type == 2 } {
        set ep_type_str "BULK"
    }
    if { $ep_type == 3 } {
        set ep_type_str "INTR"
    }
    set stall [expr ( $dioepctl >> 21 ) & 0x1]
    set tx_fifo [expr ( $dioepctl >> 22 ) & 0xF]
    set enable [expr ( $dioepctl >> 31 ) & 0x1]
    return [format "(%d;%d;%s;%d;%d;%d;0x%.3x;%2d;%2d)" $active $enable $ep_type_str $pid $nak $stall $mps $tx_fifo $next_ep]
}

#
# Dump USB Device Mode registers
#
help_text "usbdevice" "Dump USB Device Mode registers"
proc usbdevice {} {

    set wasQuiet [options -quiet]
    
    set dcfg [i_usbr DCFG]
    set dctl [i_usbr DCTL]
    set dsts [i_usbr DSTS]
    set diepmsk [i_usbr DIEPMSK]
    set doepmsk [i_usbr DOEPMSK]
    set daint [i_usbr DAINT]
    set daintmsk [i_usbr DAINTMSK]
    if { $usb_mac::has_deachint == 1 } {
        set deachint [i_usbr DEACHINT]
        set deachintmsk [i_usbr DEACHINTMSK]
    }
    set dvbusdis [i_usbr DVBUSDIS]
    set dvbuspulse [i_usbr DVBUSPULSE]
    set dthrctl [i_usbr DTHRCTL]
    set diepempmsk [i_usbr DIEPEMPMSK]

    set diepctln {}
    set diepintn {}
    set dieptsizn {}
    set diepdman {}
    set dtxfstsn {}
    set diepdmabn {}
    set doepctln {}
    set doepintn {}
    set doeptsizn {}
    set doepdman {}
    set doepdmabn {}
    set diepeachmsk {}
    set doepeachmsk {}

    for {set i 0} {$i < $usb_mac::num_dev_eps} {incr i 1} {
        lappend diepeachmskn  [i_usbr_a DIEPEACHMSKN $i 0x4]
        lappend doepeachmskn  [i_usbr_a DOEPEACHMSKN $i 0x4]
        lappend diepctln  [i_usbr_a DIEPCTL0 $i 0x20]
        lappend diepintn  [i_usbr_a DIEPINTN $i 0x20]
        lappend dieptsizn [i_usbr_a DIEPTSIZ0 $i 0x20]
        lappend diepdman  [i_usbr_a DIEPDMAN $i 0x20]
        lappend dtxfstsn  [i_usbr_a DTXFSTSN $i 0x20]
        if { $usb_mac::has_sg == 1 } {
            lappend diepdmabn [i_usbr_a DIEPDMABN $i 0x20]
        }
        lappend doepctln  [i_usbr_a DOEPCTL0 $i 0x20]
        lappend doepintn  [i_usbr_a DOEPINTN $i 0x20]
        lappend doeptsizn [i_usbr_a DOEPTSIZ0 $i 0x20]
        lappend doepdman  [i_usbr_a DOEPDMAN $i 0x20]
        if { $usb_mac::has_sg == 1 } {
            lappend doepdmabn [i_usbr_a DOEPDMABN $i 0x20]
        }
    }

    puts [format "DCFG       0x%.8x = 0x%.8x" $livanto_memmap::USB_DCFG_OFFSET $dcfg]
    puts [format "DCTL       0x%.8x = 0x%.8x" $livanto_memmap::USB_DCTL_OFFSET $dctl]
    puts [format "DSTS       0x%.8x = 0x%.8x" $livanto_memmap::USB_DSTS_OFFSET $dsts]
    puts [format "DIEPMSK    0x%.8x = 0x%.8x" $livanto_memmap::USB_DIEPMSK_OFFSET $diepmsk]
    puts [format "DOEPMSK    0x%.8x = 0x%.8x" $livanto_memmap::USB_DOEPMSK_OFFSET $doepmsk]
    puts [format "DAINT      0x%.8x = 0x%.8x" $livanto_memmap::USB_DAINT_OFFSET $daint]
    puts [format "DAINTMSK   0x%.8x = 0x%.8x" $livanto_memmap::USB_DAINTMSK_OFFSET $daintmsk]
    puts [format "DVBUSDIS   0x%.8x = 0x%.8x" $livanto_memmap::USB_DVBUSDIS_OFFSET $dvbusdis]
    puts [format "DVBUSPULSE 0x%.8x = 0x%.8x" $livanto_memmap::USB_DVBUSPULSE_OFFSET $dvbuspulse]
    puts [format "DTHRCTL    0x%.8x = 0x%.8x" $livanto_memmap::USB_DTHRCTL_OFFSET $dthrctl]
    puts [format "DIEPEMPMSK 0x%.8x = 0x%.8x" $livanto_memmap::USB_DIEPEMPMSK_OFFSET $diepempmsk]
    if { $usb_mac::has_deachint == 1 } {
        puts [format "DEACHINTMSK   0x%.8x = 0x%.8x" $livanto_memmap::USB_DEACHINTMSK_OFFSET $deachintmsk]
        puts [format "DEACHINT   0x%.8x = 0x%.8x" $livanto_memmap::USB_DEACHINT_OFFSET $deachint]
        for {set i 0} {$i < $usb_mac::num_dev_eps} {incr i 1} {
            puts [format "DIEPEACHMSK  EP%.2d    0x%08X 0x%08X" $i [expr $livanto_memmap::USB_DIEPEACHMSKN_OFFSET + (4 * $i)] [lindex $diepeachmskn $i]  ]
            puts [format "DOEPEACHMSK  EP%.2d    0x%08X 0x%08X"  $i [expr $livanto_memmap::USB_DOEPEACHMSKN_OFFSET + (4 * $i)] [lindex $doepeachmskn $i]  ]
        }
    puts ""
    puts "                                                                                          active"
    puts "                                                                                          | enable"
    puts "                                                                                          | | ep_type"
    puts "                                                                                          | | |    pid"
    puts "                                                                                          | | |    | nak"
    puts "                                                                                          | | |    | | stall"
    puts "                                                                                          | | |    | | | mps"
    puts "                                                                                          | | |    | | | |      tx_fifo"
    puts "                       DIEPCTLn   DIEPINTn   DIEPTSIZn  DIEPDMAn   DTXFSTSn  DIEPDMABn    | | |    | | | |      |  next_ep"
    puts "                       +00        +08        +10        +14        +18       +1C          | | |    | | | |      |  |"
    puts [format "IN  EP00    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X %s" [expr $livanto_memmap::USB_DIEPCTL0_OFFSET] [lindex $diepctln 0]  [lindex $diepintn 0]  [lindex $dieptsizn 0] [lindex $diepdman 0] [lindex $dtxfstsn 0] [lindex $diepdmabn 0] [decode_dioepctl [lindex $diepctln 0] 0]]
    for {set i 1} {$i < $usb_mac::num_dev_eps} {incr i 1} {
    puts [format "IN  EP%.2d    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X %s" $i [expr $livanto_memmap::USB_DIEPCTLN_OFFSET + (32 * ($i - 1))] [lindex $diepctln $i]  [lindex $diepintn $i]  [lindex $dieptsizn $i] [lindex $diepdman $i] [lindex $dtxfstsn $i] [lindex $diepdmabn $i] [decode_dioepctl [lindex $diepctln $i] $i]]
    }
    puts "                                                                                          | | |    | | | |      |  |"
    puts "                       DOEPCTLn   DOEPINTn   DOEPTSIZn  DOEPDMAn  DOEPDMABn               | | |    | | | |      |  |"
    puts "                       +00        +08        +10        +14       +1C                     | | |    | | | |      |  |"
    puts [format "OUT EP00    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X           %s" [expr $livanto_memmap::USB_DOEPCTL0_OFFSET] [lindex $doepctln 0]  [lindex $doepintn 0]  [lindex $doeptsizn 0] [lindex $doepdman 0]  [lindex $doepdmabn 0] [decode_dioepctl [lindex $doepctln 0] 0]]
    for {set i 1} {$i < $usb_mac::num_dev_eps} {incr i 1} {
    puts [format "OUT EP%.2d    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X          %s" $i [expr $livanto_memmap::USB_DOEPCTLN_OFFSET + (32 * ($i - 1))] [lindex $doepctln $i]  [lindex $doepintn $i]  [lindex $doeptsizn $i] [lindex $doepdman $i] [lindex $doepdmabn $i] [decode_dioepctl [lindex $doepctln $i] $i]]
    } 
    } else {
    puts ""
    puts "                                                                               active"
    puts "                                                                               | enable"
    puts "                                                                               | | ep_type"
    puts "                                                                               | | |    pid"
    puts "                                                                               | | |    | nak"
    puts "                                                                               | | |    | | stall"
    puts "                                                                               | | |    | | | mps"
    puts "                                                                               | | |    | | | |      tx_fifo"
    puts "                       DIEPCTLn   DIEPINTn   DIEPTSIZn  DIEPDMAn   DTXFSTSn    | | |    | | | |      |  next_ep"
    puts "                       +00        +08        +10        +14        +18         | | |    | | | |      |  |"
    puts [format "IN  EP00    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X %s" [expr $livanto_memmap::USB_DIEPCTL0_OFFSET] [lindex $diepctln 0]  [lindex $diepintn 0]  [lindex $dieptsizn 0] [lindex $diepdman 0] [lindex $dtxfstsn 0] [decode_dioepctl [lindex $diepctln 0] 0]]
    for {set i 1} {$i < $usb_mac::num_dev_eps} {incr i 1} {
    puts [format "IN  EP%.2d    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X 0x%08X %s" $i [expr $livanto_memmap::USB_DIEPCTLN_OFFSET + (32 * ($i - 1))] [lindex $diepctln $i]  [lindex $diepintn $i]  [lindex $dieptsizn $i] [lindex $diepdman $i] [lindex $dtxfstsn $i] [decode_dioepctl [lindex $diepctln $i] $i]]
    }
    puts "                                                                               | | |    | | | |      |  |"
    puts "                       DOEPCTLn   DOEPINTn   DOEPTSIZn  DOEPDMAn               | | |    | | | |      |  |"
    puts "                       +00        +08        +10        +14                    | | |    | | | |      |  |"
    puts [format "OUT EP00    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X            %s" [expr $livanto_memmap::USB_DOEPCTL0_OFFSET] [lindex $doepctln 0]  [lindex $doepintn 0]  [lindex $doeptsizn 0] [lindex $doepdman 0] [decode_dioepctl [lindex $doepctln 0] 0]]
    for {set i 1} {$i < $usb_mac::num_dev_eps} {incr i 1} {
    puts [format "OUT EP%.2d    0x%08X 0x%08X 0x%08X 0x%08X 0x%08X            %s" $i [expr $livanto_memmap::USB_DOEPCTLN_OFFSET + (32 * ($i - 1))] [lindex $doepctln $i]  [lindex $doepintn $i]  [lindex $doeptsizn $i] [lindex $doepdman $i] [decode_dioepctl [lindex $doepctln $i] $i]]
    } 
    }
    if {$wasQuiet == 0} {
        options -nquiet
    }
}

#
# Dump USB Device Mode registers
#
help_text "usbpower" "Dump USB Device Mode registers"
proc usbpower {} {
    set wasQuiet [options -quiet]
    
    puts [format "PCGCCTL    0x%.8x 0x%.8x" $livanto_memmap::USB_PCGCCTL_OFFSET [i_usbr PCGCCTL]]
    
    if {$wasQuiet == 0} {
        options -nquiet
    }
}

#
# Dump ULPI register
#
help_text "ulpireg" "Dump ULPI register"
proc ulpireg {} {
    set wasQuiet [options -quiet]
    set reg [i_usbr GPVNDCTL]
    for {set idx 0} {$idx < 0x40} {incr idx 1} {
        i_usbw GPVNDCTL [expr 0x02000000 | (($idx & 0x3F) << 16)]
        waitulpidone GPVNDCTL
        set value [i_usbr GPVNDCTL]
        puts [format "0x%02X = 0x%08X" [expr ($idx & 0x3F)] [expr ($value & 0xFF)]]
    }
    if {$wasQuiet == 0} {
      options -nquiet
    }
}
