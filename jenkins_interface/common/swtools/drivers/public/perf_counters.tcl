#################################################################################################
#  Icera Inc
#  Copyright (c) 2012
#  All rights reserved
#################################################################################################
#  $Id: //software/main.br/drivers/public/perf_counters.tcl#8 $
#  $Revision: #8 $
#  $Date: 2013/01/22 $
#  $Author: mhlond $
#################################################################################################

proc peek64 {addr} {
    set v [expr wide(0) + (wide([peek 4 $addr]) & 0x00000000ffffffff) + (wide([peek 4 [expr $addr + 4]]) << 32)]
    return $v
}

if {$::_dxpCPUType != "ICE8060-A0"} {

  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_CYC_RAW]) "CYC_RAW"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_CYC_NONIDLE]) "CYC_NONIDLE"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_BR_EXECUTED]) "BR_EXECUTED"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_BR_TAKEN]) "BR_TAKEN"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_BR_MISPREDICT]) "BR_MISPREDICT"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_INSTR_C_VALID]) "INSTR_C_VALID"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_INSTR_D_VALID]) "INSTR_D_VALID"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_INSTR_M_VALID]) "INSTR_M_VALID"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_QPM_1_DSIDES_EN]) "QPM_1_DSIDES_EN"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_QPM_GT1_DSIDES_EN]) "QPM_GT1_DSIDES_EN"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_DCACHE_MISS]) "DCACHE_MISS"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_DCACHE_LOAD]) "DCACHE_LOAD"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_DCACHE_STORE]) "DCACHE_STORE"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_DUNCACHE_LOAD]) "DUNCACHE_LOAD"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_DUNCACHE_STORE]) "DUNCACHE_STORE"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_ICACHE_MISS]) "ICACHE_MISS"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_ICACHE_FETCH]) "ICACHE_FETCH"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_ISYS_FETCH]) "ISYS_FETCH"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_IPORT_FETCH_STALL]) "IPORT_FETCH_STALL"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_ID_IPORT_PACKET_STALL]) "IPORT_PACKET_STALL"
  set ::pcb_names([expr $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK]) "FREEZEGAP"


  proc correct_iport_packet_stall {iport_packet_stall instr_c_valid instr_d_valid instr_m_valid br_taken} {

      # Number of C instruction executed from CCC packets is: 
      set c_instr_from_ccc [expr wide ($instr_c_valid) - $instr_d_valid + $instr_m_valid]

      # Number of branches taken from CCC packets (assuming the probability of a branch is the same for C instructions from CCC packets and CD packets):
      set br_taken_from_ccc [expr wide ($br_taken) * ($c_instr_from_ccc / $instr_c_valid)]

      # Assuming that a branch taken from a CCC packet is equally probable to be in one of the three possible locations, we can calculate the number of non-executed instructions in CCC packets presented to the CPU:
      #	0 for a packet that had branch taken from position 3 (total1 = 0 * br_taken_from_ccc / 3)
      #	1 for a packet that had branch taken from position 2 (total2 = 1 * br_taken_from_ccc / 3)
      #	2 for a packet that had branch taken from position 1 (total3 = 2 * br_taken_from_ccc / 3)
      # So the total is SUM(total1..3) = br_taken_from_ccc. Note that
      # the above calculation can also be presented as the branch
      # instruction being always in position 2, on average.
      # Non-executed instructions will also occur because the branches
      # can branch to any of the three instructions in the
      # packet. Assuming a simplification that branches from CCC always
      # go to CCC, we can also say that on average one instruction in
      # the target CCC packet is not executed (i.e. branching always to
      # position 2). So non-executed instructions are:
      set total3 2

      set ccc_nonexecuted_instr [expr $total3 * $br_taken_from_ccc]

      # The number of CCC packets presented to the CPU is then:
      set ccc_packets [expr (wide ($c_instr_from_ccc) + $ccc_nonexecuted_instr) / 3]

      # The number of CCC packets presented to the CPU and containing branches + branch target CCC packets is:
      set ccc_packets_with_branches [expr wide (2) * $br_taken_from_ccc]

      # The number of "pseudo-stall" cycles, i.e. cycles counted in iport_packet_stall, but spent on actually executing instructions from CCC packets that don?t contain branches is:
      set pseudo_stalls_no_branches [expr (wide ($ccc_packets) - $ccc_packets_with_branches) * 2 / 3]

      # The number of "pseudo-stall" cycles from CCC packets that contain branches is:
      set pseudo_stalls_branches [expr wide ($ccc_packets_with_branches) / 3]

      # The number of all "pseudo-stall" cycles is:
      set pseudo_stalls [expr wide ($pseudo_stalls_no_branches) + $pseudo_stalls_branches]

      # The number of real CPU stall cycles (i.e. iport_packet_stall corrected):
      set iport_packet_stall_corrected [expr wide ($iport_packet_stall) - $pseudo_stalls]

      return $iport_packet_stall_corrected
  }

  proc write_gnuplot_stat_old {filename freq} {

    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_pcb_periodic_count 0]

    set fp [open $filename w]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_pcb_counter_block]

      set periods [peek64 $addr_periods]
      for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
        set cntr($i) [peek64 $addr]
        incr addr 8
      }
      set periods_check [peek64 $addr_periods]

      if {$periods == $periods_check} {
          set rawcyc $cntr(0)
          set nonidle $cntr(1)
          set brexecuted $cntr(2)
          set brtaken $cntr(3)
          set brmispredict $cntr(4)
          set instrcvalid $cntr(5)
          set instrdvalid $cntr(6)
          set instrmvalid $cntr(7)
          set dcachemiss $cntr(10)
          set dcacheload $cntr(11)
          set dcachestore $cntr(12)
          set duncacheload $cntr(13)
          set duncachestore $cntr(14)
          set icachemiss $cntr(15)
          set icachefetch $cntr(16)
          set isysfetch $cntr(17)
          set iportfetchstall $cntr(18)
          set iportpacketstall $cntr(19)
          set freezegap $cntr(20)

          set iportpacketstall [correct_iport_packet_stall $iportpacketstall $instrcvalid $instrdvalid $instrmvalid $brtaken]

        if {$rawcyc > 0} {      

            set totalsampletimesecs [expr $rawcyc / ($freq * 1000000)] 

            set cpuusage [expr 100.0 * wide ($nonidle) / $rawcyc]
      
            puts $fp [format "CPU Usage : %8.2f" $cpuusage]
            puts [format "CPU Usage : %8.2f" $cpuusage]
      
            set mips [expr ((wide ($instrcvalid) + $instrmvalid) / (1000000 * $totalsampletimesecs))]
      
            puts $fp [format "MIPs : %ld" $mips]
            puts [format "MIPs : %ld" $mips]
      
            set percentagebrs [expr 1.0 * (($brtaken * wide (100)) / $brexecuted)]
      
            puts $fp [format "Percentage of branches taken : %8.2f" $percentagebrs]
            puts [format "Percentage of branches taken : %8.2f" $percentagebrs]

            set percentagebrsmispredict [expr 1.0 * (((wide ($brmispredict) - ($rawcyc - $nonidle)) * wide (100)) / $brexecuted)]
      
            puts $fp [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]
            puts [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]

            set dcachemisspersec [expr ((((wide ($rawcyc) + $freezegap) * $dcachemiss) / $rawcyc) / $totalsampletimesecs)]
          
            puts $fp [format "D-cache misses per second : %ld" $dcachemisspersec]
            puts [format "D-cache misses per second : %ld" $dcachemisspersec]

#             puts $fp [format "Total D-cache misses : %ld" $dcachemiss]
#             puts [format "Total D-cache misses : %ld" $dcachemiss]

            set icachemisspersec [expr ((((wide ($rawcyc) + $freezegap) * $icachemiss) / $rawcyc) / $totalsampletimesecs)]
          
            puts $fp [format "I-cache misses per second : %ld" $icachemisspersec]
            puts [format "I-cache misses per second : %ld" $icachemisspersec]

            set icachestallsperinstr [expr 1.0 * (wide ($iportfetchstall) / ($instrcvalid + $instrmvalid))]
            puts $fp [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]
            puts [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]

            set cpustallsperinstr [expr 1.0 * (wide ($iportpacketstall) / ($instrcvalid + $instrmvalid))]
            puts $fp [format "CPU  stalls per instruction : %8.2f" $cpustallsperinstr]
            puts [format "CPU stalls per instruction : %8.2f" $cpustallsperinstr]

            set utilization [expr 1.0 * ((wide ($instrcvalid) + $instrmvalid) * 100) / $nonidle]
            puts $fp [format "Utilization :  %8.2f" $utilization]
            puts [format "Utilization :  %8.2f" $utilization]

            set icachemisspenalty [expr 1.0 * (wide ($iportfetchstall) / $icachemiss)]
            puts $fp [format "I-cache miss penalty : %8.2f" $icachemisspenalty]
            puts [format "I-cache miss penalty : %8.2f" $icachemisspenalty]

            set dcachemisspenalty [expr 1.0 * (wide ($iportpacketstall) / ($dcachemiss + $duncacheload))]
            puts $fp [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]
            puts [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]

        }

      } else {
        puts $fp "Can't get consistent PCB stats"
      }
    } else {
      puts $fp "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }

    close $fp

#  puts $fp "set term x11 size 1500,900"
#  puts $fp "set datafile separator \',\'"
#  puts $fp "set key autotitle columnheader"
#  puts $fp "set multiplot layout 4, 4 title \'$1\' font \"Times-Roman,10\""
#  puts $fp "set tmargin 2"
#  puts $fp "set nokey"

  }

  proc write_gnuplot_stat {filename freq} {

      package require math::bignum 

    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_pcb_periodic_count 0]

    set fp [open $filename w]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_pcb_counter_block]

      set periods [peek64 $addr_periods]
      for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
        set cntr($i) [peek64 $addr]
        incr addr 8
      }
      set periods_check [peek64 $addr_periods]

      if {$periods == $periods_check} {
          set rawcyc $cntr(0)
          set nonidle $cntr(1)
          set brexecuted $cntr(2)
          set brtaken $cntr(3)
          set brmispredict $cntr(4)
          set instrcvalid $cntr(5)
          set instrdvalid $cntr(6)
          set instrmvalid $cntr(7)
          set dcachemiss $cntr(10)
          set dcacheload $cntr(11)
          set dcachestore $cntr(12)
          set duncacheload $cntr(13)
          set duncachestore $cntr(14)
          set icachemiss $cntr(15)
          set icachefetch $cntr(16)
          set isysfetch $cntr(17)
          set iportfetchstall $cntr(18)
          set iportpacketstall $cntr(19)
          set freezegap $cntr(20)

          set iportpacketstall [correct_iport_packet_stall $iportpacketstall $instrcvalid $instrdvalid $instrmvalid $brtaken]

        if {$rawcyc > 0} {      

            set totalsampletimesecs [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $rawcyc] [::math::bignum::mul [::math::bignum::fromstr $freq] [::math::bignum::fromstr 1000000]]]]

            puts $fp [format "Total sample time : %ld" $totalsampletimesecs]
            puts [format "Total sample time : %ld" $totalsampletimesecs]
            puts [format "Total sample time : %f" $totalsampletimesecs]


            set cpuusage [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::fromstr 100] [::math::bignum::fromstr $nonidle]] [::math::bignum::fromstr $rawcyc]]]
      
            puts $fp [format "CPU Usage : %8.2f" $cpuusage]
            puts [format "CPU Usage : %8.2f" $cpuusage]
      
            set mips [::math::bignum::tostr [::math::bignum::div [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]] [::math::bignum::mul [::math::bignum::fromstr 1000000]  [::math::bignum::fromstr $totalsampletimesecs]]]]
      
             puts $fp [format "MIPs : %ld" $mips]
             puts [format "MIPs : %ld" $mips]
      
            set percentagebrs [::math::bignum::tostr [::math::bignum::mul [::math::bignum::fromstr 1] [::math::bignum::div [::math::bignum::mul [::math::bignum::fromstr $brtaken] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $brexecuted]]]]
      
              puts $fp [format "Percentage of branches taken : %8.2f" $percentagebrs]
              puts [format "Percentage of branches taken : %8.2f" $percentagebrs]

            set percentagebrsmispredict [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::sub [::math::bignum::fromstr $brmispredict] [::math::bignum::sub [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $nonidle]]] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $brexecuted]]]
      
              puts $fp [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]
              puts [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]

            set dcachemisspersec [::math::bignum::tostr [::math::bignum::div [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $freezegap]] [::math::bignum::fromstr $dcachemiss]] [::math::bignum::fromstr $rawcyc]] [::math::bignum::fromstr $totalsampletimesecs]]]
          
              puts $fp [format "D-cache misses per second : %ld" $dcachemisspersec]
              puts [format "D-cache misses per second : %ld" $dcachemisspersec]

             set icachemisspersec [::math::bignum::tostr [::math::bignum::div [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $freezegap]] [::math::bignum::fromstr $icachemiss]] [::math::bignum::fromstr $rawcyc]] [::math::bignum::fromstr $totalsampletimesecs]]]
          
              puts $fp [format "I-cache misses per second : %ld" $icachemisspersec]
              puts [format "I-cache misses per second : %ld" $icachemisspersec]

             set icachestallsperinstr [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportfetchstall] [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]]]]


              puts $fp [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]
              puts [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]

             set cpustallsperinstr [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportpacketstall] [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]]]]

              puts $fp [format "CPU  stalls per instruction : %8.2f" $cpustallsperinstr]
              puts [format "CPU stalls per instruction : %8.2f" $cpustallsperinstr]

             set utilization [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $nonidle]]]

              puts $fp [format "Utilization :  %8.2f" $utilization]
              puts [format "Utilization :  %8.2f" $utilization]

            set icachemisspenalty [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportfetchstall] [::math::bignum::fromstr $icachemiss]]]

              puts $fp [format "I-cache miss penalty : %8.2f" $icachemisspenalty]
              puts [format "I-cache miss penalty : %8.2f" $icachemisspenalty]

            set dcachemisspenalty [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportpacketstall] [::math::bignum::add [::math::bignum::fromstr $dcachemiss] [::math::bignum::fromstr $duncacheload]]]]

              puts $fp [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]
              puts [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]

        }

      } else {
        puts $fp "Can't get consistent PCB stats"
      }
    } else {
      puts $fp "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }

    close $fp

#  puts $fp "set term x11 size 1500,900"
#  puts $fp "set datafile separator \',\'"
#  puts $fp "set key autotitle columnheader"
#  puts $fp "set multiplot layout 4, 4 title \'$1\' font \"Times-Roman,10\""
#  puts $fp "set tmargin 2"
#  puts $fp "set nokey"

  }

  proc write_gnuplot_stat_millisecs {filename freq} {

      package require math::bignum 

    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_pcb_periodic_count 0]

    set fp [open $filename w]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_pcb_counter_block]

      set periods [peek64 $addr_periods]
      for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
        set cntr($i) [peek64 $addr]
        incr addr 8
      }
      set periods_check [peek64 $addr_periods]

      if {$periods == $periods_check} {
          set rawcyc $cntr(0)
          set nonidle $cntr(1)
          set brexecuted $cntr(2)
          set brtaken $cntr(3)
          set brmispredict $cntr(4)
          set instrcvalid $cntr(5)
          set instrdvalid $cntr(6)
          set instrmvalid $cntr(7)
          set dcachemiss $cntr(10)
          set dcacheload $cntr(11)
          set dcachestore $cntr(12)
          set duncacheload $cntr(13)
          set duncachestore $cntr(14)
          set icachemiss $cntr(15)
          set icachefetch $cntr(16)
          set isysfetch $cntr(17)
          set iportfetchstall $cntr(18)
          set iportpacketstall $cntr(19)
          set freezegap $cntr(20)

          set iportpacketstall [correct_iport_packet_stall $iportpacketstall $instrcvalid $instrdvalid $instrmvalid $brtaken]

        if {$rawcyc > 0} {      

            set totalsampletimemillisecs [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $rawcyc] [::math::bignum::mul [::math::bignum::fromstr $freq] [::math::bignum::fromstr 1000]]]]

            set cpuusage [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::fromstr 100] [::math::bignum::fromstr $nonidle]] [::math::bignum::fromstr $rawcyc]]]
      
            puts $fp [format "CPU Usage : %8.2f" $cpuusage]
            puts [format "CPU Usage : %8.2f" $cpuusage]
      
            set mips [::math::bignum::tostr [::math::bignum::div [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]] [::math::bignum::mul [::math::bignum::fromstr 1000]  [::math::bignum::fromstr $totalsampletimemillisecs]]]]
      
             puts $fp [format "MIPms : %ld" $mips]
             puts [format "MIPms : %ld" $mips]
      
            set percentagebrs [::math::bignum::tostr [::math::bignum::mul [::math::bignum::fromstr 1] [::math::bignum::div [::math::bignum::mul [::math::bignum::fromstr $brtaken] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $brexecuted]]]]
      
              puts $fp [format "Percentage of branches taken : %8.2f" $percentagebrs]
              puts [format "Percentage of branches taken : %8.2f" $percentagebrs]

            set percentagebrsmispredict [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::sub [::math::bignum::fromstr $brmispredict] [::math::bignum::sub [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $nonidle]]] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $brexecuted]]]
      
              puts $fp [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]
              puts [format "Percentage of branches mis-predicated : %8.2f" $percentagebrsmispredict]

            set dcachemisspermillisec [::math::bignum::tostr [::math::bignum::div [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $freezegap]] [::math::bignum::fromstr $dcachemiss]] [::math::bignum::fromstr $rawcyc]] [::math::bignum::fromstr $totalsampletimemillisecs]]]
          
              puts $fp [format "D-cache misses per millisecond : %ld" $dcachemisspermillisec]
              puts [format "D-cache misses per millisecond : %ld" $dcachemisspermillisec]

             set icachemisspermillisec [::math::bignum::tostr [::math::bignum::div [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $rawcyc] [::math::bignum::fromstr $freezegap]] [::math::bignum::fromstr $icachemiss]] [::math::bignum::fromstr $rawcyc]] [::math::bignum::fromstr $totalsampletimemillisecs]]]
          
              puts $fp [format "I-cache misses per millisecond : %ld" $icachemisspermillisec]
              puts [format "I-cache misses per millisecond : %ld" $icachemisspermillisec]

             set icachestallsperinstr [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportfetchstall] [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]]]]


              puts $fp [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]
              puts [format "I-cache stalls per instruction : %8.2f" $icachestallsperinstr]

             set cpustallsperinstr [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportpacketstall] [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]]]]

              puts $fp [format "CPU  stalls per instruction : %8.2f" $cpustallsperinstr]
              puts [format "CPU stalls per instruction : %8.2f" $cpustallsperinstr]

             set utilization [::math::bignum::tostr [::math::bignum::div [::math::bignum::mul [::math::bignum::add [::math::bignum::fromstr $instrcvalid] [::math::bignum::fromstr $instrmvalid]] [::math::bignum::fromstr 100]] [::math::bignum::fromstr $nonidle]]]

              puts $fp [format "Utilization :  %8.2f" $utilization]
              puts [format "Utilization :  %8.2f" $utilization]

            set icachemisspenalty [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportfetchstall] [::math::bignum::fromstr $icachemiss]]]

              puts $fp [format "I-cache miss penalty : %8.2f" $icachemisspenalty]
              puts [format "I-cache miss penalty : %8.2f" $icachemisspenalty]

            set dcachemisspenalty [::math::bignum::tostr [::math::bignum::div [::math::bignum::fromstr $iportpacketstall] [::math::bignum::add [::math::bignum::fromstr $dcachemiss] [::math::bignum::fromstr $duncacheload]]]]

              puts $fp [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]
              puts [format "D-cache miss penalty : %8.2f" $dcachemisspenalty]

        }

      } else {
        puts $fp "Can't get consistent PCB stats"
      }
    } else {
      puts $fp "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }

    close $fp

#  puts $fp "set term x11 size 1500,900"
#  puts $fp "set datafile separator \',\'"
#  puts $fp "set key autotitle columnheader"
#  puts $fp "set multiplot layout 4, 4 title \'$1\' font \"Times-Roman,10\""
#  puts $fp "set tmargin 2"
#  puts $fp "set nokey"

  }

  proc write_pcb_stat {filename} {
    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_pcb_periodic_count 0]

    set fp [open $filename w]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_pcb_counter_block]

      set periods [peek64 $addr_periods]
      for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
        set cntr($i) [peek64 $addr]
        incr addr 8
      }
      set periods_check [peek64 $addr_periods]

      if {$periods == $periods_check} {
        puts $fp [format "PCB counter statistics (%d iterations):" $periods]
        set rawcyc $cntr(0)
        for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
          set val64 $cntr($i)
          set percentage 0.0
          if {$rawcyc != 0} {
            set percentage [expr 100.0 * $val64 / $rawcyc]
          }
#          puts $fp [format "  %20s : 0x%.16lx (%8.4f%%)" $::pcb_names($i) $val64 $percentage]
          puts $fp [format "  %20s : %.24ld (%8.4f%%)" $::pcb_names($i) $val64 $percentage]
        }
      } else {
        puts $fp "Can't get consistent PCB stats"
      }
    } else {
      puts $fp "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }

    close $fp

  }

  proc show_pcb_stat {} {
    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_pcb_periodic_count 0]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_pcb_counter_block]

      set periods [peek64 $addr_periods]
      for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
        set cntr($i) [peek64 $addr]
        incr addr 8
      }
      set periods_check [peek64 $addr_periods]

      if {$periods == $periods_check} {
        puts [format "PCB counter statistics (%d iterations):" $periods]
        set rawcyc $cntr(0)
        for {set i 0} {$i <= $::livanto_config::SPD_PCB_CNTR_REG_ALLOC_COUNTERS_PER_BLOCK} {incr i} {
          set val64 $cntr($i)
          set percentage 0.0
          if {$rawcyc != 0} {
            set percentage [expr 100.0 * $val64 / $rawcyc]
          }
          puts [format "  %20s : 0x%.16lx (%8.4f%%)" $::pcb_names($i) $val64 $percentage]
        }
      } else {
        puts "Can't get consistent PCB stats"
      }
    } else {
      puts "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }
  }

  proc enable_pcb_stat {{enable 1}} {
    set wasQuiet [options -quiet]

    set addr [symb2addr drv_pcb_enabled 0]

    if {$addr != 0xdeadbeef} {
      poke 4 $addr $enable
    } else {
      puts "No PCB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }
  }

}


if {$::_dxpCPUType != "ICE8060-A0"} {

  proc show_amb_stat {} {
    set wasQuiet [options -quiet]

    set addr_periods [symb2addr drv_ambextmem_periodic_count 0]

    if {$addr_periods != 0xdeadbeef} {
      set addr [symb2addr drv_ambextmem_match_count]

      set periods [peek64 $addr_periods]
      set match_count_ch0 [peek64 $addr]
      incr addr 8
      set match_count_ch1 [peek64 $addr]
      set periods_check [peek64 $addr_periods]


      if {$periods == $periods_check} {
        set addr [symb2addr drv_ambextmem_period_us]
        set period_sec [expr 1e-6 * [peek 4 $addr]]
        puts [format "Extmem AMB match count statistics (%d iterations)" $periods]
        set bytes_per_second 0.0
        if {$periods != 0} {
          set bytes_per_second [expr 1.0 * $match_count_ch0 / $periods * 4.0 / $period_sec]
        }
        puts [format "  Channel 0: %9.4f MB/s  raw: 0x%.16lx (%ld)" [expr $bytes_per_second / (1024.0 * 1024.0)] $match_count_ch0 $match_count_ch0]
        if {$periods != 0} {
          set bytes_per_second [expr 1.0 * $match_count_ch1 / $periods * 4.0 / $period_sec]
        }
        puts [format "  Channel 1: %9.4f MB/s  raw: 0x%.16lx (%ld)" [expr $bytes_per_second / (1024.0 * 1024.0)] $match_count_ch1 $match_count_ch1]
      } else {
        puts "Can't get consistent AMB stats"
      }
    } else {
      puts "No AMB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }
  }

  proc enable_amb_stat {{enable 1}} {
    set wasQuiet [options -quiet]

    set addr [symb2addr drv_ambextmem_enabled 0]

    if {$addr != 0xdeadbeef} {
      poke 4 $addr $enable
    } else {
      puts "No AMB stat in this build"
    }

    if {$wasQuiet == 0} {
      options -nquiet
    }
  }

}
