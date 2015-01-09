#
# Set which USB Profile is being used
# 
set usb_profile_max [expr  $usb_num_profiles - 1]
#help_text "set_usb_profile <0.."+[expr $usb_num_profiles - 1]+">" "Override USB profile"
help_text "set_usb_profile <0..$usb_profile_max>" "Override USB profile"
proc set_usb_profile { {profile $usb_num_profiles} } {
    global usb_num_profiles
    global usb_profile_max
    global usb_profile_name
    global usb_profile_dictionary

    if { [ string is integer -strict $profile ] } {
        if { $profile < 0 && $profile >= $usb_num_profiles } {
            set profile ""
        }
    } else {
        if { [catch { set profile $usb_profile_dictionary($profile) } status ] } {
            set profile ""
        }
    }

    if { $profile != "" } {
        set profile_addr [symb2addr dxp_run_usb_profile]
        if { $profile_addr == 0xdeadbeef } {
            puts "Error: In order to use set_usb_profile, you need to compile your code using USB_STACK_USBWARE"
        } else {
            puts "setting profile to $usb_profile_name($profile)"
            mw $profile_addr $profile 1
        }
    } else {
        puts "set_usb_profile <0..$usb_profile_max>"
        for { set i 0 } { $i < $usb_num_profiles } { incr i } {
            puts "$i $usb_profile_name($i)"
        }
    }
}

#
# Modify USB PID
# 
#help_text "set_usb_pid <pid>" "set the USB product id"
proc set_usb_pid {value} {
    set addr [symb2addr dxp_run_usb_pid]
    if { $addr == 0xdeadbeef } {
        puts "Error: In order to use set_usb_pid, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $addr $value
    }
}

#
# Modify USB VID
# 
#help_text "set_usb_vid <vid>" "set the USB vendor id"
proc set_usb_vid {value} {
    set addr [symb2addr dxp_run_usb_vid]
    if { $addr == 0xdeadbeef } {
        puts "Error: In order to use set_usb_vid, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $addr $value
    }
}

#
# Enable or not USB Remote Wakeup
# 
help_text "set_usb_remote_wakeup <0,1>" "Enable or not Remote Wakeup: 0/1"
proc set_usb_remote_wakeup {value} {
    set remote_wakeup_address [symb2addr dxp_usb_common_remote_wakeup]
    if { $remote_wakeup_address == 0xdeadbeef } {
        puts "Error: In order to use set_usb_remote_wakeup, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $remote_wakeup_address $value
    }
}

#
# Modify max_power (to allow testing with USB 1.1 that does not support 500 mA 
# 
#help_text "set_usb_max_power <0,250>" "max power in units of 2 mA"
proc set_usb_max_power {value} {
    set max_power_address [symb2addr dxp_usb_common_max_power]
    if { $max_power_address == 0xdeadbeef } {
        puts "Error: In order to use set_usb_max_power, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $max_power_address $value
    }
}

#
# Set Self Powered or Bus Powered
# 
help_text "set_usb_self_powered <0,1>" "Set Self Powered or Bus Powered: 1/0"
proc set_usb_self_powered {value} {
    set self_powered_address [symb2addr dxp_usb_common_self_powered]
    if { $self_powered_address == 0xdeadbeef } {
        puts "Error: In order to use set_usb_self_powered, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $self_powered_address $value
    }
}

help_text "set_usb_no_diag_port" "Force to have no diag port"
proc set_usb_no_diag_port {} {
    set log_enabled_address [symb2addr dxp_usb_common_gsc_log_enabled]
    if { $log_enabled_address == 0xdeadbeef } {
        puts "Error: In order to use log_enabled_address, you need to compile your code using USB_STACK_USBWARE"
    } else {
        mw $log_enabled_address 0
    }
}

help_text "uw_dump_mallocs" "Shows all USB allocated memory blocks"
proc uw_dump_mallocs {} {
    global _dxpInstance 
    global exe_prefix

    set _dxpInstance 1
    set enable [scan [exec dxp-icera-elf-objdump -t $exe_prefix.exe | grep uw_enable_dump_mallocs] %x]
    mw $enable 1
    set dump [scan [exec dxp-icera-elf-objdump -t $exe_prefix.exe | grep uw_dump_mallocs] %x]
    puts $dump
    setreg -pc $dump
    cont
}

help_text "set_pcap_eth snaplen" "Enable NCM/ECM pcap"
proc set_pcap_eth {snaplen} {
    global exe_prefix

    set addr [scan [exec dxp-icera-elf-objdump -t $exe_prefix.exe | grep drv_pcap_netif_snaplen] %x]
    mw $addr $snaplen
}


help_text "set_pcap_ip snaplen" "Enable IP pcap"
proc set_pcap_ip {snaplen} {
    global exe_prefix

    set addr [scan [exec dxp-icera-elf-objdump -t $exe_prefix.exe | grep drv_pcap_ip_snaplen] %x]
    mw $addr $snaplen
}

proc ncm {} {
    set_usb_profile "USB_PROFILE_IAD_2ANMO"
    set_usb_pid 0x410
    set_usb_vid 0x1983
}

#
# Enable mass storage method
#
help_text "enable_mass_modem" "Enable mass storage in modem app"
proc enable_mass_modem { {choice ""}} {
    global _start_from_boot

    set usb_mass_modem_mode_enabled_address [symb2addr usb_mass_modem_mode_enabled]

    if { $usb_mass_modem_mode_enabled_address == 0xdeadbeef } {
        puts "Error: In order to use enable_mass_modem, you need to compile your code using USB_STACK_USBWARE"
    } else {
        switch $choice {
           yes      {
               puts "Modem forced to mass storage mode"
               mw  $usb_mass_modem_mode_enabled_address 1
           }
           no       {
               puts "Modem forced to bypass mass sotrage emulation"
               mw  $usb_mass_modem_mode_enabled_address 0
           }
           default  {
               if {[info exists _start_from_boot]} {
                 if {$_start_from_boot == 0} {
                     puts "Runnig from RAM: Modem to bypass mass storage emulation"
                     mw  $usb_mass_modem_mode_enabled_address 0
                 }
              }
           }
        }
    }
}

#
# 
#help_text "set_usb_tx_frames <frames>" 
proc set_usb_tx_frames {value} {
    set config [symb2addr dxp_run_class_config_tx_xfer_frames]
    if { $config == 0xdeadbeef } {
        puts "Error: In order to use set_usb_tx_frames, you need to compile your code using USB_STACK_BSD"
    } else {
        mw $config $value
    }
}
#
# 
#help_text "set_usb_rx_frames <frames>" 
proc set_usb_rx_frames {value} {
    set config [symb2addr dxp_run_class_config_rx_xfer_frames]
    if { $config == 0xdeadbeef } {
        puts "Error: In order to use set_usb_rx_frames, you need to compile your code using USB_STACK_BSD"
    } else {
        mw $config $value
    }
}
#
# 
#help_text "set_usb_ntb_out <size>" 
proc set_usb_ntb_out {value} {
    set config [symb2addr dxp_run_ncm_out_ntb]
    if { $config == 0xdeadbeef } {
        puts "Error: In order to use set_usb_ntb_out, you need to compile your code using USB_STACK_BSD"
    } else {
        mw $config $value
    }
}
#
# 
#help_text "set_usb_ntb_in <size>" 
proc set_usb_ntb_in {value} {
    set config [symb2addr dxp_run_ncm_in_ntb]
    if { $config == 0xdeadbeef } {
        puts "Error: In order to use set_usb_ntb_in, you need to compile your code using USB_STACK_BSD"
    } else {
        mw $config $value
    }
}