#################################################################################################
#  Icera Inc
#  Copyright (c) 2013
#  All rights reserved
#################################################################################################
#  $Id: //software/main.br/drivers/public/drv_shm.tcl#4 $
#  $Revision: #4 $
#  $Date: 2013/12/20 $
#  $Author: fdelorme $
#################################################################################################
#  dxp-run script implementing IPC SHM mailbox access
#
#################################################################################################

source $env(ICERA_ROOT)/x86-linux/bin/livanto_memmap.tcl
source $env(ICERA_ROOT)/x86-linux/bin/livanto_config.tcl

if {[info exists ::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE]} {

    #
    # 'Pure' IPC status codes
    #
    set DRV_IPC_PURE_UNKNOWN               0
    set DRV_IPC_PURE_BOOT_COLD_BOOT_IND    1
    set DRV_IPC_PURE_BOOT_FW_REQ           2
    set DRV_IPC_PURE_BOOT_RESTART_FW_REQ   3
    set DRV_IPC_PURE_BOOT_FW_CONF          4
    set DRV_IPC_PURE_READY                 5

    #
    # IPC status code names
    #
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_UNKNOWN) "*UNKNOWN*"
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_BOOT_COLD_BOOT_IND) "BOOT_COLD_BOOT_IND"
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_BOOT_FW_REQ) "BOOT_FW_REQ"
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_BOOT_RESTART_FW_REQ) "BOOT_RESTART_FW_REQ"
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_BOOT_FW_CONF) "BOOT_FW_CONF"
    set DRV_IPC_STATUS_NAMES($DRV_IPC_PURE_READY) "READY"

    #
    # IPC status mailbox address
    #
    set DRV_IPC_MAILBOX_ADDR $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE

    ######################################################################################
    # Functions
    ######################################################################################

    #
    #  Convert 'pure' IPC status value to actual ('full') value to be used in the mailbox
    #
    proc IPCpure2full {pure} {
        return [expr (~$pure << 16) | $pure]
    }

    #
    #  Convert 'full' IPC status value to 'pure' value
    #
    proc IPCfull2pure {full} {
        set ret $::DRV_IPC_PURE_UNKNOWN
        set pure [expr $full & 0x0000ffff]
        set pure_check [expr ~($full >> 16) & 0x0000ffff]
        if {$pure == $pure_check} {
          set ret $pure
        }
        return $pure
    }

    #
    #  Generate BB->AP interrupt
    #
    proc IPCsendSignal {} {
        set addr [expr $::livanto_memmap::IPC_BASE + $::livanto_memmap::IPC_BBC_INT_SET_OFFSET]
        #set value [peek 4 $addr]
        poke 4 $addr 0x1
    }

    #
    #  Read IPC mailbox
    #
    proc IPCreadMailbox {} {
        # Perform dummy read to another memory atom address
        # to invalidate the BBMCI read buffer...
        peek 4 [expr $::DRV_IPC_MAILBOX_ADDR + 0x20]
        set value [format 0x%.8x [peek 4 $::DRV_IPC_MAILBOX_ADDR]]
        return $value
    }

    #
    #  Write IPC mailbox
    #
    proc IPCwriteMailbox {value} {
        poke 4 $::DRV_IPC_MAILBOX_ADDR $value
    }

    #
    #  Show IPC mailbox value
    #
    proc IPCshowMailbox {} {
        set val [IPCreadMailbox]
        puts [format "  IPC Mailbox         : 0x%.8x" $val]
    }

    #
    #  Write mailbox and interrupt AP
    #
    proc IPCactMailbox {value} {
        IPCwriteMailbox [IPCpure2full $value]
        IPCsendSignal
    }

    #
    #  Read mailbox and convert to 'pure' value
    #
    proc IPCreadpureMailbox {} {
        return [IPCfull2pure [IPCreadMailbox]]
    }

    #
    #  Get name for a 'pure' mailbox value
    #
    proc IPCnameMailbox {pureval} {
        return $::DRV_IPC_STATUS_NAMES($pureval)
    }

    #
    #  Show 'pure' mailbox value
    #
    proc IPCshowpureMailbox {} {
        set val [IPCreadpureMailbox]
        puts [format "  IPC Mailbox (pure)  : %d (%s)" $val [IPCnameMailbox $val]]
    }

    #
    #  Unregister BB
    #
    proc IPCunregisterBB {} {
        IPCactMailbox $::DRV_IPC_PURE_BOOT_FW_REQ
    }

    #
    #  Prepare dxp-run runi, doing BROM-like handshaking
    #
    proc IPCprepareDebugRun {} {
        set wasQuiet [options -quiet]
        set after_time 1000
        set iter_limit [expr 30000 / $after_time]
        set timeout_seen 0

        #If not cold boot status, set cold boot status
        set ipc_status [IPCreadpureMailbox]
        puts [format "IPC -> Preparing IPC for dxp-run started BBC sw (status: %s)" [IPCnameMailbox $ipc_status]]
        if {$ipc_status != $::DRV_IPC_PURE_BOOT_COLD_BOOT_IND} {
          puts "IPC -> Setting cold boot into mailbox"
          IPCactMailbox $::DRV_IPC_PURE_BOOT_COLD_BOOT_IND
        }

        #wait for cold boot status (shouldn't be needed, should never happen)
        set ipc_status [IPCreadpureMailbox]
        set i 0
        while {$ipc_status != $::DRV_IPC_PURE_BOOT_COLD_BOOT_IND} {
          if {$i >= $iter_limit} {
            set timeout_seen 1
            break
          }
          incr i
          puts [format "IPC -> Waiting cold boot (status %s, iter %d)" [IPCnameMailbox $ipc_status] $i]
          after $after_time
          set ipc_status [IPCreadpureMailbox]
        }

        #Request firmware
        set ipc_status [IPCreadpureMailbox]
        if {$ipc_status == $::DRV_IPC_PURE_BOOT_COLD_BOOT_IND} {
          puts "IPC -> Requesting firmware load on cold boot"
          IPCactMailbox $::DRV_IPC_PURE_BOOT_FW_REQ
        }

        #wait for firmware ready
        set ipc_status [IPCreadpureMailbox]
        set i 0
        while {$ipc_status != $::DRV_IPC_PURE_BOOT_FW_CONF} {
          if {$i >= $iter_limit} {
            set timeout_seen 2
            break
          }
          incr i
          puts [format "IPC -> Waiting for firmware ready (status: %s. iter %d)" [IPCnameMailbox $ipc_status] $i]
          after $after_time
          set ipc_status [IPCreadpureMailbox]
        }

        if {$timeout_seen} {
          puts [format "IPC -> FAILED: IPC timed out (%d)" $timeout_seen]
        } else {
          puts [format "IPC -> Success: IPC prepared for dxp-run sw start (status: %s)" [IPCnameMailbox [IPCreadpureMailbox]]]
        }

        if {$wasQuiet == 0} {
          options -nquiet
        }
    }

    #
    #  Dump IPC region to a file
    #
    proc IPCdump {ipc_file} {
        set ipc_window_base $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE
        # Get IPC size at 12bytes offset from IPC_WINDOW_BASE
        set ipc_size [peek 4 [expr $ipc_window_base + 12]]
        puts [format "  IPC Base: 0x%x" $ipc_window_base]
        puts [format "  IPC Size: 0x%x" $ipc_size]
        if {$ipc_size > $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_SIZE} {
            puts "ERROR: $ipc_size invalid IPC size value"
        } else {
            # Dump IPC window
            rawmemdump $ipc_file $ipc_window_base $ipc_size
        }
    }

    #
    # Gets platform config info from the boot buffer,
    #  where it is placed by the AP
    #
    proc IPCgetPlatCfgFromBootBuffer {{verbose 1}} {
        set wasQuiet [options -quiet]

        set str ""

        #this is start of BT2 header
        set addr [expr $::livanto_memmap::SEG_EXTUNCACHED_EXT_SDRAM_BASE + 0x1020]
        set bt2_hdr_len [peek 4 [expr $addr + 4]]
        set bt2_len [peek 4 [expr $addr + 8]]
        #this is the start of the boot buffer (12 is the size of boot config)
        set boot_buf_len [peek 4 [expr $addr + $bt2_hdr_len + $bt2_len + 8]]
        set boot_buf_addr [expr $addr + $bt2_hdr_len + $bt2_len + 12]
        set boot_buf_end [expr $boot_buf_addr + $boot_buf_len]

        #look for the plat cfg record
        set addr $boot_buf_addr
        while { 1 } {
            set buf_id [peek 4 [expr $addr + 0]]
            set len [peek 4 [expr $addr + 4]]
            #Buf ID == 1 is platform config
            if { $buf_id == 1 } {
                set platcfg_addr [expr $addr + 8]
                for {set i 0} {$i < $len} {incr i} {
                    set byte [peek 1 [expr $platcfg_addr + $i]]
                    if { $byte != 0} {
                        set str [format "%s%c" $str $byte]
                    }
                }
                if { $verbose } {
                    puts [format "Boot buffer: found platform config @0x%.8x (len: %d): %s" $platcfg_addr $len $str]
                }
                break
            }
            #8 is buffer header
            set addr [expr $addr + 8 + $len]
            if { $addr >= $boot_buf_end} {
                break
            }
        }

        if {$wasQuiet == 0} {
            options -nquiet
        }

        return $str
    }
}
