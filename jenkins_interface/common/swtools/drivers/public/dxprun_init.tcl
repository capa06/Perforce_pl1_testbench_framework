#################################################################################################
#  Icera Inc
#  Copyright (c) 2006-2010
#  All rights reserved
#################################################################################################
#  $Id: //software/main.br/drivers/public/dxprun_init.tcl#176 $
#  $Revision: #176 $
#  $Date: 2014/02/26 $
#  $Author: aberdery $
#################################################################################################
#  dxp-run script to perform platform dependent initialisation.
#
#################################################################################################

# Platform dependency of the initialisation
# Non-default settings should be defined in drv_hwplat.tcl
# Platforms using only default settings may have empty drv_hwplat.tcl files or may not have one
# at all.
global _hwplat

global _nand_type
set _nand_type ""

if {![info exists _start_from_boot]} {
    set _start_from_boot 0
}

if {$_start_from_boot == 0} {
    if {[file exists $_platform_init_file] == 1} {
        puts "Sourcing $_platform_init_file..."
        source $_platform_init_file
    } else {
        puts "Error: $_platform_init_file missing"
        exit
    }
}

set platform_dependency_file $sw_root/drivers/private/hwplatform/$_hwplat/drv_hwplat.tcl
if {[file exists $platform_dependency_file] == 1} {
    source $platform_dependency_file
} else {
    if {$_start_from_boot == 0} {
        puts "Error: $platform_dependency_file missing"
        exit
    }
}

if {[info exists ::host_interface_shm]} {
  #If host interface is SHM, include SHM TCL
  puts "Including SHM TCL support"
  source $sw_root/drivers/public/drv_shm.tcl
}


proc SwitchOff32kHzExternalClock {} {

    puts "dxprun_init.tcl: Switch Off External 32kHz"
    set rtb_host_start $livanto_memmap::RTB_RTB_HOST_BASE
    set rtb_host_wakeup_ctrl [format 0x%x [expr $rtb_host_start + $livanto_memmap::RTB_HOST_WAKEUP_CTRL_OFFSET]]
    set clr_32kHz_mask ~0x2F0
    addrvalid -rw   $rtb_host_start  [format 0x%x [expr $rtb_host_start + $livanto_memmap::RTB_RTB_HOST_SIZE]]  RTB_HOST_REGS
    set value [peek 4 $rtb_host_wakeup_ctrl]
    set value [expr ($value & $clr_32kHz_mask)]
    poke 4 $rtb_host_wakeup_ctrl $value

}

proc CalcPllFreq {conf_item} {
    foreach register $conf_item {
        set register_name [lindex $register 0]
        set fields [lindex $register 1]
        if {$register_name == "PLL_CONFIG"} {
            foreach field $fields {
                set field_name [lindex $field 0]
                set field_value [lindex $field 1]
                if {$field_name == "PLL_F"} {
                    set pll_f [expr $field_value]
                } elseif {$field_name == "PLL_R"} {
                    set pll_r [expr $field_value]
                } elseif {$field_name == "PLL_CLKOD"} {
                    set pll_od [expr $field_value]
                }
            }
        }
    }
    set pll_freq [expr 26.0 * [incr pll_f] / [incr pll_r] / [incr pll_od]]
    return $pll_freq
}

proc GetFieldValue {conf_item req_reg_name req_reg_field} {
    set ret -1
    foreach register $conf_item {
        set register_name [lindex $register 0]
        set fields [lindex $register 1]
        if {$register_name == $req_reg_name} {
            foreach field $fields {
                set field_name [lindex $field 0]
                set field_value [lindex $field 1]
                if {$field_name == $req_reg_field} {
                    set ret $field_value
                }
            }
        }
    }
    return $ret
}

proc SetFieldValue {conf_item req_reg_name req_reg_field new_field_value} {
    set ret [list]
    foreach register $conf_item {
        set register_name [lindex $register 0]
        set fields [lindex $register 1]
        set new_fields [list]
        foreach field $fields {
            set field_name [lindex $field 0]
            set field_value [lindex $field 1]
            if {$register_name == $req_reg_name} {
              if {$field_name == $req_reg_field} {
                set field_value $new_field_value
              }
            }
            set new_field [list $field_name $field_value]
            lappend new_fields $new_field
        }
        set new_register [list $register_name $new_fields]
        lappend ret $new_register
    }
    return $ret
}


##  Pinmux/padctrl platform configuration
if {$::_dxpCPUType == "ICE9040-A0"} {
    namespace eval syscfg {
        namespace eval chpc {
            set PLATFORM_PADCTRL { \
                {PADCTRL1 { \
                    {MCD0DRV         $::platform_padctrl1_MCD0DRV             } \
                    {MCD1DRV         $::platform_padctrl1_MCD1DRV             } \
                    {MCD2DRV         $::platform_padctrl1_MCD2DRV             } \
                    {MCD3DRV         $::platform_padctrl1_MCD3DRV             } \
                    {MCCTLDRV        $::platform_padctrl1_MCCTLDRV            } \
                    {MCDSCKDRV       $::platform_padctrl1_MCDSCKDRV           } \
                    {MPCTLDRV        $::platform_padctrl1_MPCTLDRV            } \
                    {MPCKDRV         $::platform_padctrl1_MPCKDRV             } \
                    {MPD0DRV         $::platform_padctrl1_MPD0DRV             } \
                    {MPD1DRV         $::platform_padctrl1_MPD1DRV             } \
                    } \
                } \
                {PADCTRL2 { \
                    {BBRFDLY         $::platform_padctrl2_BBRFDLY             } \
                    {BBRFDRV         $::platform_padctrl2_BBRFDRV             } \
                    {BBRFD1DRV       $::platform_padctrl2_BBRFD1DRV           } \
                    {CLK0DRV         $::platform_padctrl2_CLK0DRV             } \
                    {CLK1DRV         $::platform_padctrl2_CLK1DRV             } \
                    {PWMDRV          $::platform_padctrl2_PWMDRV              } \
                    {HSICDATADLY     $::platform_padctrl2_HSICDATADLY         } \
                    {MPCTL2DRV       $::platform_padctrl2_MPCTL2DRV           } \
                    } \
                } \
                {PADCTRL3 { \
                    {ULPIDRV         $::platform_padctrl3_ULPIDRV             } \
                    {ULPICLKDRV      $::platform_padctrl3_ULPICLKDRV          } \
                    {GENDRV          $::platform_padctrl3_GENDRV              } \
                    {SD_DRVA         $::platform_padctrl3_SD_DRVA             } \
                    {SD_DRVB         $::platform_padctrl3_SD_DRVB             } \
                    {SD_VSEL         $::platform_padctrl3_SD_VSEL             } \
                    {HSIM_VSEL       $::platform_padctrl3_HSIM_VSEL           } \
                    {HSICINPUTEN     $::platform_padctrl3_HSICINPUTEN         } \
                    }\
                } \
                {PADCTRL4 {\
                    {RF0PDEN         $::platform_padctrl4_RF0PDEN             } \
                    {RF1PDEN         $::platform_padctrl4_RF1PDEN             } \
                    {RF8PDEN         $::platform_padctrl4_RF8PDEN             } \
                    {RF9PDEN         $::platform_padctrl4_RF9PDEN             } \
                    {MCKIPDEN        $::platform_padctrl4_MCKIPDEN            } \
                    {NMSEIPDEN       $::platform_padctrl4_NMSEIPDEN           } \
                    {MCKOPDEN        $::platform_padctrl4_MCKOPDEN            } \
                    {MDO0PDEN        $::platform_padctrl4_MDO0PDEN            } \
                    {MDO1PDEN        $::platform_padctrl4_MDO1PDEN            } \
                    {NMSEOPDEN       $::platform_padctrl4_NMSEOPDEN           } \
                    {CLOCKREQPDEN    $::platform_padctrl4_CLOCKREQPDEN        } \
                    {SDCDPDEN        $::platform_padctrl4_SDCDPDEN            } \
                    {SDCDPUEN        $::platform_padctrl4_SDCDPUEN            } \
                    {SDPUEN          $::platform_padctrl4_SDPUEN              } \
                    {SD1PUEN         $::platform_padctrl4_SD1PUEN             } \
                    {SD3PUEN         $::platform_padctrl4_SD3PUEN             } \
                    {HS0DPUEN        $::platform_padctrl4_HS0DPUEN            } \
                    } \
                } \
                {PADCTRL5 { \
                    {SIP0DRV         $::platform_padctrl5_SIP0DRV             } \
                    {SIP1DRV         $::platform_padctrl5_SIP1DRV             } \
                    {SIP2DRV         $::platform_padctrl5_SIP2DRV             } \
                    {SIP3DRV         $::platform_padctrl5_SIP3DRV             } \
                    {SIP4DRV         $::platform_padctrl5_SIP4DRV             } \
                    {SIP5DRV         $::platform_padctrl5_SIP5DRV             } \
                    {SIP6DRV         $::platform_padctrl5_SIP6DRV             } \
                    {SIP7DRV         $::platform_padctrl5_SIP7DRV             } \
                    } \
                } \
                {PADCTRL6 { \
                    {SIP0_0PUEN      $::platform_padctrl6_SIP0_0PUEN          } \
                    {SIP0_1PUEN      $::platform_padctrl6_SIP0_1PUEN          } \
                    {SIP0_2PUEN      $::platform_padctrl6_SIP0_2PUEN          } \
                    {SIP0_3PUEN      $::platform_padctrl6_SIP0_3PUEN          } \
                    {SIP1_0PUEN      $::platform_padctrl6_SIP1_0PUEN          } \
                    {SIP1_1PUEN      $::platform_padctrl6_SIP1_1PUEN          } \
                    {SIP1_2PUEN      $::platform_padctrl6_SIP1_2PUEN          } \
                    {SIP1_3PUEN      $::platform_padctrl6_SIP1_3PUEN          } \
                    {SIP2_0PUEN      $::platform_padctrl6_SIP2_0PUEN          } \
                    {SIP2_1PUEN      $::platform_padctrl6_SIP2_1PUEN          } \
                    {SIP2_2PUEN      $::platform_padctrl6_SIP2_2PUEN          } \
                    {SIP2_3PUEN      $::platform_padctrl6_SIP2_3PUEN          } \
                    {SIP3_0PUEN      $::platform_padctrl6_SIP3_0PUEN          } \
                    {SIP3_1PUEN      $::platform_padctrl6_SIP3_1PUEN          } \
                    {SIP3_2PUEN      $::platform_padctrl6_SIP3_2PUEN          } \
                    {SIP3_3PUEN      $::platform_padctrl6_SIP3_3PUEN          } \
                    {SIP4_0PUEN      $::platform_padctrl6_SIP4_0PUEN          } \
                    {SIP4_1PUEN      $::platform_padctrl6_SIP4_1PUEN          } \
                    {SIP4_2PUEN      $::platform_padctrl6_SIP4_2PUEN          } \
                    {SIP4_3PUEN      $::platform_padctrl6_SIP4_3PUEN          } \
                    {SIP5_0PUEN      $::platform_padctrl6_SIP5_0PUEN          } \
                    {SIP5_1PUEN      $::platform_padctrl6_SIP5_1PUEN          } \
                    {SIP5_2PUEN      $::platform_padctrl6_SIP5_2PUEN          } \
                    {SIP5_3PUEN      $::platform_padctrl6_SIP5_3PUEN          } \
                    {SIP6_0PUEN      $::platform_padctrl6_SIP6_0PUEN          } \
                    {SIP6_1PUEN      $::platform_padctrl6_SIP6_1PUEN          } \
                    {SIP6_2PUEN      $::platform_padctrl6_SIP6_2PUEN          } \
                    {SIP6_3PUEN      $::platform_padctrl6_SIP6_3PUEN          } \
                    {SIP7_0PUEN      $::platform_padctrl6_SIP7_0PUEN          } \
                    {SIP7_1PUEN      $::platform_padctrl6_SIP7_1PUEN          } \
                    {SIP7_2PUEN      $::platform_padctrl6_SIP7_2PUEN          } \
                    {SIP7_3PUEN      $::platform_padctrl6_SIP7_3PUEN          } \
                    } \
                } \
                {PADCTRL7 { \
                    {SIP0_0PDEN      $::platform_padctrl7_SIP0_0PDEN          } \
                    {SIP0_1PDEN      $::platform_padctrl7_SIP0_1PDEN          } \
                    {SIP0_2PDEN      $::platform_padctrl7_SIP0_2PDEN          } \
                    {SIP0_3PDEN      $::platform_padctrl7_SIP0_3PDEN          } \
                    {SIP1_0PDEN      $::platform_padctrl7_SIP1_0PDEN          } \
                    {SIP1_1PDEN      $::platform_padctrl7_SIP1_1PDEN          } \
                    {SIP1_2PDEN      $::platform_padctrl7_SIP1_2PDEN          } \
                    {SIP1_3PDEN      $::platform_padctrl7_SIP1_3PDEN          } \
                    {SIP2_0PDEN      $::platform_padctrl7_SIP2_0PDEN          } \
                    {SIP2_1PDEN      $::platform_padctrl7_SIP2_1PDEN          } \
                    {SIP2_2PDEN      $::platform_padctrl7_SIP2_2PDEN          } \
                    {SIP2_3PDEN      $::platform_padctrl7_SIP2_3PDEN          } \
                    {SIP3_0PDEN      $::platform_padctrl7_SIP3_0PDEN          } \
                    {SIP3_1PDEN      $::platform_padctrl7_SIP3_1PDEN          } \
                    {SIP3_2PDEN      $::platform_padctrl7_SIP3_2PDEN          } \
                    {SIP3_3PDEN      $::platform_padctrl7_SIP3_3PDEN          } \
                    {SIP4_0PDEN      $::platform_padctrl7_SIP4_0PDEN          } \
                    {SIP4_1PDEN      $::platform_padctrl7_SIP4_1PDEN          } \
                    {SIP4_2PDEN      $::platform_padctrl7_SIP4_2PDEN          } \
                    {SIP4_3PDEN      $::platform_padctrl7_SIP4_3PDEN          } \
                    {SIP5_0PDEN      $::platform_padctrl7_SIP5_0PDEN          } \
                    {SIP5_1PDEN      $::platform_padctrl7_SIP5_1PDEN          } \
                    {SIP5_2PDEN      $::platform_padctrl7_SIP5_2PDEN          } \
                    {SIP5_3PDEN      $::platform_padctrl7_SIP5_3PDEN          } \
                    {SIP6_0PDEN      $::platform_padctrl7_SIP6_0PDEN          } \
                    {SIP6_1PDEN      $::platform_padctrl7_SIP6_1PDEN          } \
                    {SIP6_2PDEN      $::platform_padctrl7_SIP6_2PDEN          } \
                    {SIP6_3PDEN      $::platform_padctrl7_SIP6_3PDEN          } \
                    {SIP7_0PDEN      $::platform_padctrl7_SIP7_0PDEN          } \
                    {SIP7_1PDEN      $::platform_padctrl7_SIP7_1PDEN          } \
                    {SIP7_2PDEN      $::platform_padctrl7_SIP7_2PDEN          } \
                    {SIP7_3PDEN      $::platform_padctrl7_SIP7_3PDEN          } \
                    } \
                } \
                {PADCTRL8 { \
                    {SKEW_ILULS0     $::platform_padctrl8_SKEW_ILULS0         } \
                    {SKEW_ILULS1     $::platform_padctrl8_SKEW_ILULS1         } \
                    {SKEW_ILULD0     $::platform_padctrl8_SKEW_ILULD0         } \
                    {SKEW_ILULD1     $::platform_padctrl8_SKEW_ILULD1         } \
                    {SKEW_ILDLS0     $::platform_padctrl8_SKEW_ILDLS0         } \
                    {SKEW_ILDLS0     $::platform_padctrl8_SKEW_ILDLS0         } \
                    } \
                } \
                {PADCTRL9 { \
                    {SKEW_ILDLD0     $::platform_padctrl9_SKEW_ILDLD0         } \
                    {SKEW_ILDLD1     $::platform_padctrl9_SKEW_ILDLD1         } \
                    {SKEW_ILDLD2     $::platform_padctrl9_SKEW_ILDLD2         } \
                    {SKEW_ILDLD3     $::platform_padctrl9_SKEW_ILDLD3         } \
                    {SKEW_ILDLD4     $::platform_padctrl9_SKEW_ILDLD4         } \
                    {SKEW_ILDLD5     $::platform_padctrl9_SKEW_ILDLD5         } \
                    } \
                } \
            }
            set configArray(PLATFORM_PADCTRL) $PLATFORM_PADCTRL
        }
    }
} elseif {$::_dxpCPUType == "ICE9140-A0"} {
   namespace eval syscfg {
        namespace eval chpc {
            set PLATFORM_PADCTRL { \
                {PADCTRL1 { \
                    {MCD0DRV         $::platform_padctrl1_MCD0DRV             } \
                    {MCD1DRV         $::platform_padctrl1_MCD1DRV             } \
                    {MCD2DRV         $::platform_padctrl1_MCD2DRV             } \
                    {MCD3DRV         $::platform_padctrl1_MCD3DRV             } \
                    {MCCTLDRV        $::platform_padctrl1_MCCTLDRV            } \
                    {MCDSCKDRV       $::platform_padctrl1_MCDSCKDRV           } \
                    {MPCTLDRV        $::platform_padctrl1_MPCTLDRV            } \
                    {MPCKDRV         $::platform_padctrl1_MPCKDRV             } \
                    {MPD0DRV         $::platform_padctrl1_MPD0DRV             } \
                    {MPD1DRV         $::platform_padctrl1_MPD1DRV             } \
                    } \
                } \
                {PADCTRL2 { \
                    {BBRFDLY         $::platform_padctrl2_BBRFDLY             } \
                    {BBRFDRV         $::platform_padctrl2_BBRFDRV             } \
                    {BBRFD1DRV       $::platform_padctrl2_BBRFD1DRV           } \
                    {CLK0DRV         $::platform_padctrl2_CLK0DRV             } \
                    {CLK1DRV         $::platform_padctrl2_CLK1DRV             } \
                    {PWMDRV          $::platform_padctrl2_PWMDRV              } \
                    {MPCTL2DRV       $::platform_padctrl2_MPCTL2DRV           } \
                    } \
                } \
                {PADCTRL3 { \
                    {GENDRV          $::platform_padctrl3_GENDRV              } \
                    {HSIM_VSEL       $::platform_padctrl3_HSIM_VSEL           } \
                    {HSIM0_VALID     $::platform_padctrl3_HSIM0_VALID         } \
                    {HSIM1_VALID     $::platform_padctrl3_HSIM1_VALID         } \
                    {HSIM0_HW_CTRL_EN $::platform_padctrl3_HSIM0_HW_CTRL_EN   } \
                    {HSIM1_HW_CTRL_EN $::platform_padctrl3_HSIM1_HW_CTRL_EN   } \
                    }\
                } \
                {PADCTRL4 {\
                    {RF0PDEN         $::platform_padctrl4_RF0PDEN             } \
                    {RF1PDEN         $::platform_padctrl4_RF1PDEN             } \
                    {RF8PDEN         $::platform_padctrl4_RF8PDEN             } \
                    {RF9PDEN         $::platform_padctrl4_RF9PDEN             } \
                    {MCKIPDEN        $::platform_padctrl4_MCKIPDEN            } \
                    {NMSEIPDEN       $::platform_padctrl4_NMSEIPDEN           } \
                    {MCKOPDEN        $::platform_padctrl4_MCKOPDEN            } \
                    {MDO0PDEN        $::platform_padctrl4_MDO0PDEN            } \
                    {MDO1PDEN        $::platform_padctrl4_MDO1PDEN            } \
                    {NMSEOPDEN       $::platform_padctrl4_NMSEOPDEN           } \
                    {CLOCKREQPDEN    $::platform_padctrl4_CLOCKREQPDEN        } \
                    {SDCDPDEN        $::platform_padctrl4_SDCDPDEN            } \
                    {SDCDPUEN        $::platform_padctrl4_SDCDPUEN            } \
                    {SDPUEN          $::platform_padctrl4_SDPUEN              } \
                    {SD1PUEN         $::platform_padctrl4_SD1PUEN             } \
                    {SD3PUEN         $::platform_padctrl4_SD3PUEN             } \
                    {HS0DPUEN        $::platform_padctrl4_HS0DPUEN            } \
                    } \
                } \
                {PADCTRL5 { \
                    {SIP0DRV         $::platform_padctrl5_SIP0DRV             } \
                    {SIP1DRV         $::platform_padctrl5_SIP1DRV             } \
                    {SIP2DRV         $::platform_padctrl5_SIP2DRV             } \
                    {SIP3DRV         $::platform_padctrl5_SIP3DRV             } \
                    {SIP4DRV         $::platform_padctrl5_SIP4DRV             } \
                    {SIP5DRV         $::platform_padctrl5_SIP5DRV             } \
                    {SIP6DRV         $::platform_padctrl5_SIP6DRV             } \
                    {SIP7DRV         $::platform_padctrl5_SIP7DRV             } \
                    } \
                } \
                {PADCTRL6 { \
                    {SIP0_0PUEN      $::platform_padctrl6_SIP0_0PUEN          } \
                    {SIP0_1PUEN      $::platform_padctrl6_SIP0_1PUEN          } \
                    {SIP0_2PUEN      $::platform_padctrl6_SIP0_2PUEN          } \
                    {SIP0_3PUEN      $::platform_padctrl6_SIP0_3PUEN          } \
                    {SIP1_0PUEN      $::platform_padctrl6_SIP1_0PUEN          } \
                    {SIP1_1PUEN      $::platform_padctrl6_SIP1_1PUEN          } \
                    {SIP1_2PUEN      $::platform_padctrl6_SIP1_2PUEN          } \
                    {SIP1_3PUEN      $::platform_padctrl6_SIP1_3PUEN          } \
                    {SIP2_0PUEN      $::platform_padctrl6_SIP2_0PUEN          } \
                    {SIP2_1PUEN      $::platform_padctrl6_SIP2_1PUEN          } \
                    {SIP2_2PUEN      $::platform_padctrl6_SIP2_2PUEN          } \
                    {SIP2_3PUEN      $::platform_padctrl6_SIP2_3PUEN          } \
                    {SIP3_0PUEN      $::platform_padctrl6_SIP3_0PUEN          } \
                    {SIP3_1PUEN      $::platform_padctrl6_SIP3_1PUEN          } \
                    {SIP3_2PUEN      $::platform_padctrl6_SIP3_2PUEN          } \
                    {SIP3_3PUEN      $::platform_padctrl6_SIP3_3PUEN          } \
                    {SIP4_0PUEN      $::platform_padctrl6_SIP4_0PUEN          } \
                    {SIP4_1PUEN      $::platform_padctrl6_SIP4_1PUEN          } \
                    {SIP4_2PUEN      $::platform_padctrl6_SIP4_2PUEN          } \
                    {SIP4_3PUEN      $::platform_padctrl6_SIP4_3PUEN          } \
                    {SIP5_0PUEN      $::platform_padctrl6_SIP5_0PUEN          } \
                    {SIP5_1PUEN      $::platform_padctrl6_SIP5_1PUEN          } \
                    {SIP5_2PUEN      $::platform_padctrl6_SIP5_2PUEN          } \
                    {SIP5_3PUEN      $::platform_padctrl6_SIP5_3PUEN          } \
                    {SIP6_0PUEN      $::platform_padctrl6_SIP6_0PUEN          } \
                    {SIP6_1PUEN      $::platform_padctrl6_SIP6_1PUEN          } \
                    {SIP6_2PUEN      $::platform_padctrl6_SIP6_2PUEN          } \
                    {SIP6_3PUEN      $::platform_padctrl6_SIP6_3PUEN          } \
                    {SIP7_0PUEN      $::platform_padctrl6_SIP7_0PUEN          } \
                    {SIP7_1PUEN      $::platform_padctrl6_SIP7_1PUEN          } \
                    {SIP7_2PUEN      $::platform_padctrl6_SIP7_2PUEN          } \
                    {SIP7_3PUEN      $::platform_padctrl6_SIP7_3PUEN          } \
                    } \
                } \
                {PADCTRL7 { \
                    {SIP0_0PDEN      $::platform_padctrl7_SIP0_0PDEN          } \
                    {SIP0_1PDEN      $::platform_padctrl7_SIP0_1PDEN          } \
                    {SIP0_2PDEN      $::platform_padctrl7_SIP0_2PDEN          } \
                    {SIP0_3PDEN      $::platform_padctrl7_SIP0_3PDEN          } \
                    {SIP1_0PDEN      $::platform_padctrl7_SIP1_0PDEN          } \
                    {SIP1_1PDEN      $::platform_padctrl7_SIP1_1PDEN          } \
                    {SIP1_2PDEN      $::platform_padctrl7_SIP1_2PDEN          } \
                    {SIP1_3PDEN      $::platform_padctrl7_SIP1_3PDEN          } \
                    {SIP2_0PDEN      $::platform_padctrl7_SIP2_0PDEN          } \
                    {SIP2_1PDEN      $::platform_padctrl7_SIP2_1PDEN          } \
                    {SIP2_2PDEN      $::platform_padctrl7_SIP2_2PDEN          } \
                    {SIP2_3PDEN      $::platform_padctrl7_SIP2_3PDEN          } \
                    {SIP3_0PDEN      $::platform_padctrl7_SIP3_0PDEN          } \
                    {SIP3_1PDEN      $::platform_padctrl7_SIP3_1PDEN          } \
                    {SIP3_2PDEN      $::platform_padctrl7_SIP3_2PDEN          } \
                    {SIP3_3PDEN      $::platform_padctrl7_SIP3_3PDEN          } \
                    {SIP4_0PDEN      $::platform_padctrl7_SIP4_0PDEN          } \
                    {SIP4_1PDEN      $::platform_padctrl7_SIP4_1PDEN          } \
                    {SIP4_2PDEN      $::platform_padctrl7_SIP4_2PDEN          } \
                    {SIP4_3PDEN      $::platform_padctrl7_SIP4_3PDEN          } \
                    {SIP5_0PDEN      $::platform_padctrl7_SIP5_0PDEN          } \
                    {SIP5_1PDEN      $::platform_padctrl7_SIP5_1PDEN          } \
                    {SIP5_2PDEN      $::platform_padctrl7_SIP5_2PDEN          } \
                    {SIP5_3PDEN      $::platform_padctrl7_SIP5_3PDEN          } \
                    {SIP6_0PDEN      $::platform_padctrl7_SIP6_0PDEN          } \
                    {SIP6_1PDEN      $::platform_padctrl7_SIP6_1PDEN          } \
                    {SIP6_2PDEN      $::platform_padctrl7_SIP6_2PDEN          } \
                    {SIP6_3PDEN      $::platform_padctrl7_SIP6_3PDEN          } \
                    {SIP7_0PDEN      $::platform_padctrl7_SIP7_0PDEN          } \
                    {SIP7_1PDEN      $::platform_padctrl7_SIP7_1PDEN          } \
                    {SIP7_2PDEN      $::platform_padctrl7_SIP7_2PDEN          } \
                    {SIP7_3PDEN      $::platform_padctrl7_SIP7_3PDEN          } \
                    } \
                } \
                {PADCTRL8 { \
                    {SKEW_ILULS0     $::platform_padctrl8_SKEW_ILULS0         } \
                    {SKEW_ILULS1     $::platform_padctrl8_SKEW_ILULS1         } \
                    {SKEW_ILULD0     $::platform_padctrl8_SKEW_ILULD0         } \
                    {SKEW_ILULD1     $::platform_padctrl8_SKEW_ILULD1         } \
                    {SKEW_ILDLS0     $::platform_padctrl8_SKEW_ILDLS0         } \
                    {SKEW_ILDLS0     $::platform_padctrl8_SKEW_ILDLS0         } \
                    } \
                } \
                {PADCTRL9 { \
                    {SKEW_ILDLD0     $::platform_padctrl9_SKEW_ILDLD0         } \
                    {SKEW_ILDLD1     $::platform_padctrl9_SKEW_ILDLD1         } \
                    {SKEW_ILDLD2     $::platform_padctrl9_SKEW_ILDLD2         } \
                    {SKEW_ILDLD3     $::platform_padctrl9_SKEW_ILDLD3         } \
                    {SKEW_ILDLD4     $::platform_padctrl9_SKEW_ILDLD4         } \
                    {SKEW_ILDLD5     $::platform_padctrl9_SKEW_ILDLD5         } \
                    } \
                } \
            }
            set configArray(PLATFORM_PADCTRL) $PLATFORM_PADCTRL
        }
    }
}

set ::firstReset 1

proc ApplyImageEntrypointToAllDxps {} {
  global _start_from_boot
  global _dxpInstance
  global _dxpNumDXPInstance
  global _elfEntrypoint
  if {$_start_from_boot == 0} {
    set wasQuiet [options -quiet]
    set old_dxp_instance $_dxpInstance

    #get entry point that has been set by loding the elf image: assume DXP0 $PC has been updated with it
    set _dxpInstance 0
    set elf_entrypoint [format "0x%.8x" [getreg -directcsr 0]]

    puts "Setting entrypoint $elf_entrypoint for all DXPs"

    #replicate this to DXP1/2
    set _dxpInstance 1
    setreg -pc $elf_entrypoint
    if {[info exists _dxpNumDXPInstance]} {
      if {$_dxpNumDXPInstance > 2} {
        set _dxpInstance 2
        setreg -pc $elf_entrypoint
      }
    }

    set _elfEntrypoint $elf_entrypoint
    set _dxpInstance $old_dxp_instance
    if {$wasQuiet == 0} {
      options -nquiet
    }
  }
}

proc Set9040ChipSiliconTypeFast {} {
    set addr [expr $livanto_memmap::CHPC_BASE + $livanto_memmap::CHPC_EFUSE_STATE_6_OFFSET]
    set val [peek 4 $addr]
    set new_val [expr ($val & ~(3 << 24)) | (1 << 24)]
    poke 4 $addr $new_val
    puts "Efuse reg for chipsilicontype set to FAST"
}

proc Set9x40EfuseStates {} {
    # Indicate internal boot mode:
    # EFUSE 19, bit 0 or 1 to 1.
    set efuse19 [syscfg::chpc::ReadEFUSE 19]
    set efuse19 [expr $efuse19 | 0x1 ]
    syscfg::chpc::WriteEFUSE 19 $efuse19

    if {$::_dxpCPUType == "ICE9040-A0"} {
        # Indicate authentication enable:
        # EFUSE 19, bit 2 or 3 to 1
        set efuse19 [syscfg::chpc::ReadEFUSE 19]
        set efuse19 [expr $efuse19 | 0x4 ]
        syscfg::chpc::WriteEFUSE 19 $efuse19
    }
}

proc SetupPlatformConfiguration9040 {} {
    global _flash_size
    global _hwplat
    global mckosocdiv
    global mcki_mhz
    global aux_link_mode
    global aux_link_requested_freq
    global aux_drive_strength
    global _sdram_size

    set wasQuiet [options -quiet]

    if {![info exists _flash_size]} {
        set _flash_size  [expr 64*1024*1024]
    }
    if {![info exists _sdram_size]} {
        set _sdram_size  [expr 64*1024*1024]
    }

    ## Log some enviroment variable for debug
    global env
    foreach idx [array names env] {
        if {$idx=="ADA" || $idx=="VARIANT" || $idx=="MAKEFLAGS" || $idx=="USB_PROFILE" } {
            puts "$idx=$env($idx)"
        }
    }

    if {$::firstReset} {
        set ::firstReset 0

        ###
        ### ICE9040 configurations
        ###
        set aux_compress 1

        #some parameters can be overriden in platform-specific drv_hwplat.tcl
        if {[info exists aux_link_requested_freq]} {
            puts "!!!!! WARNING: ignoring aux_link_requested_freq: not supported for 9040 !!!!!"
        }
        if {![info exists mckosocdiv]} {
            set mckosocdiv 4
        }
        if {![info exists aux_link_mode]} {
            set aux_link_mode "p2e2"
        }
        if {![info exists aux_drive_strength]} {
            set aux_drive_strength 6
        }
        if {![info exists mcki_mhz]} {
            set mcki_mhz 110
        }

        puts [format "AUX link: %s, AUX compress: %d, MCKO div: %d, MCKI MHz: %d, drive strength: %d" $aux_link_mode $aux_compress $mckosocdiv $mcki_mhz $aux_drive_strength]

        # UMCD microcode selection
        if { $::platform_umcd_32bit != 0 } {
          if { $::platform_umcd_freq == 133 } {
            set mem_config DDR_MOB_512_BRC_x32_133MHz
          } else {
            set mem_config DDR_MOB_512_BRC_x32_200MHz
          }
        } else {
          set mem_config DDR_MOB_512_BRC_x16_200MHz
        }

        puts [format "UMCD Config: %s" $mem_config]

        #process UMCD configuration with possibly some modifications
        set umcd_conf_item $::syscfg::umcd::configArray($mem_config)

        #modify drive strength in DDR EMR if told to do so
        if { $::platform_umcd_ds_full != 0 } {
          puts "!!!!! FULL DDR DRIVE STRENGTH NOT SUPPORTED FOR 9040 !!!!!"
          exit 211
        }

        set soc_src $::livanto_regdefs::CRPC_REGS_SOC_CLK_CTRL_SRC_DIVA
        if { $::platform_clkb_prediv != 0 } {
          set soc_src $::livanto_regdefs::CRPC_REGS_SOC_CLK_CTRL_SRC_DIVB
        }

        set BT2_CLOCKS \
        [list \
          [list MAIN_PLL_CONFIG \
            [list \
              [list PLL_R $::platform_pll_r] \
              [list PLL_F $::platform_pll_f] \
              [list PLL_CLKOD $::platform_pll_od] \
            ] \
          ] \
          [list APP_PLL_CONFIG \
            [list \
              [list PLL_R $::platform_pll_r] \
              [list PLL_F $::platform_pll_f] \
              [list PLL_CLKOD $::platform_pll_od] \
            ] \
          ] \
          [list DXP_DIV_CTRL \
            [list \
              [list DIV $::platform_dxp_clk_div] \
              [list SEL $::livanto_regdefs::CRPC_REGS_DXP_DIV_CTRL_SEL_APP] \
            ] \
          ] \
          [list CLKA_DIV_CTRL \
            [list \
              [list DIV $::platform_clka_prediv] \
            ] \
          ] \
          [list CLKB_DIV_CTRL \
            [list \
              [list DIV $::platform_clkb_prediv] \
            ] \
          ] \
          [list SOC_CLK_CTRL \
            [list \
              [list DIV $::platform_soc_clk_div] \
              [list SRC $soc_src] \
            ] \
          ] \
          [list DDR_2X_CLK_CTRL \
            [list \
              [list DIV $::platform_umcd_clk_div] \
            ] \
          ] \
        ]
        set ::syscfg::crpc::configArray(BT2_CLOCKS) $BT2_CLOCKS

        # For now no UMCO (Flash) configuration
        set umcoConfig "NONE"

        #set up MCLK for the platform
        puts [format "Setting MCLK to %d" $::platform_mclk]
        ::syscfg::crpc::SetXTALInFreq $::platform_mclk

        SetupEVBConfiguration_ICE9040_DDR BT2_CLOCKS $mem_config PLATFORM_PADCTRL $umcoConfig $aux_link_mode $aux_drive_strength $mckosocdiv $mcki_mhz $aux_compress

        # Set desired PADCTRL settings
        syscfg::chpc::ActivateConfig PLATFORM_PADCTRL

        ::syscfg::PrintClkFreq
    }

    if {$wasQuiet == 0} {
        options -nquiet
    }
}

proc ClearTbApMailbox {} {
    set addr_start [expr $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE + 0x1000]
    set addr_end   [expr $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE + 0x3000]
    for {set addr $addr_start} {$addr < $addr_end} {set addr [expr $addr + 4]} {
      poke 4 $addr 0
    }
}

proc SetupPlatformConfiguration9140 {} {
    global _flash_size
    global _hwplat
    global mckosocdiv
    global aux_link_mode
    global aux_link_requested_freq
    global aux_drive_strength
    global _sdram_size

    set wasQuiet [options -quiet]

    if {![info exists _flash_size]} {
        set _flash_size  [expr 64*1024*1024]
    }
    if {![info exists _sdram_size]} {
        set _sdram_size  [expr 64*1024*1024]
    }
    ## Log some enviroment variable for debug
    global env
    foreach idx [array names env] {
        if {$idx=="ADA" || $idx=="VARIANT" || $idx=="MAKEFLAGS" || $idx=="USB_PROFILE" } {
            puts "$idx=$env($idx)"
        }
    }

    if {$::firstReset} {
        set ::firstReset 0

        ###
        ### ICE9140 configurations
        ###

        #Enable accessing the IPC region from TCL
        addrvalid -rw $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE [expr $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_BASE + $::livanto_memmap::SEG_EXTUNCACHED_IPC_MEM_SIZE - 1] IPC

        #some parameters can be overriden in platform-specific drv_hwplat.tcl
        if {[info exists aux_link_requested_freq]} {
            puts "!!!!! WARNING: ignoring aux_link_requested_freq: not supported for 9140 !!!!!"
        }
        if {![info exists mckosocdiv]} {
            set mckosocdiv 3
        }
        if {![info exists aux_link_mode]} {
            set aux_link_mode "p2e2"
        }
        if {![info exists aux_drive_strength]} {
            set aux_drive_strength 5
        }

        #MCKI is fixed for now
        set mcki_mhz 110
        set aux_compress 1

        puts [format "AUX link: %s, AUX compress: %d, MCKO div: %d, MCKI MHz: %d, drive strength: %d" $aux_link_mode $aux_compress $mckosocdiv $mcki_mhz $aux_drive_strength]

        set soc_src $::livanto_regdefs::CRPC_REGS_SOC_CLK_CTRL_SRC_DIVA
        if { $::platform_clkb_prediv != 0 } {
          set soc_src $::livanto_regdefs::CRPC_REGS_SOC_CLK_CTRL_SRC_DIVB
        }

        set BT2_CLOCKS \
        [list \
          [list MAIN_PLL_CONFIG \
            [list \
              [list PLL_R $::platform_pll_r] \
              [list PLL_F $::platform_pll_f] \
              [list PLL_CLKOD $::platform_pll_od] \
            ] \
          ] \
          [list APP_PLL_CONFIG \
            [list \
              [list PLL_R $::platform_pll_r] \
              [list PLL_F $::platform_pll_f] \
              [list PLL_CLKOD $::platform_pll_od] \
            ] \
          ] \
          [list DXP_DIV_CTRL \
            [list \
              [list DIV $::platform_dxp_clk_div] \
              [list SEL $::livanto_regdefs::CRPC_REGS_DXP_DIV_CTRL_SEL_APP] \
            ] \
          ] \
          [list CLKA_DIV_CTRL \
            [list \
              [list DIV $::platform_clka_prediv] \
            ] \
          ] \
          [list CLKB_DIV_CTRL \
            [list \
              [list DIV $::platform_clkb_prediv] \
            ] \
          ] \
          [list SOC_CLK_CTRL \
            [list \
              [list DIV $::platform_soc_clk_div] \
              [list SRC $soc_src] \
            ] \
          ] \
          [list DDR_2X_CLK_CTRL \
            [list \
              [list DIV $::platform_umcd_clk_div] \
            ] \
          ] \
        ]
        if { $::platform_use_pllp != 0 } {
            puts "Using external PLL"
            #remove main PLL config if PLLP is in use
            set lix [lsearch -regexp $BT2_CLOCKS MAIN_PLL_CONFIG]
            set BT2_CLOCKS [lreplace $BT2_CLOCKS $lix $lix]
            unset lix
            #switch DXP to PLLP
            set addr [expr $::livanto_memmap::CRPC_BASE + $::livanto_memmap::CRPC_REGS_MAIN_CLK_SOURCE_OFFSET]
            poke 4 $addr 1

        }
        set ::syscfg::crpc::configArray(BT2_CLOCKS) $BT2_CLOCKS

        #set up MCLK for the platform
        puts [format "Setting MCLK to %d" $::platform_mclk]
        ::syscfg::crpc::SetXTALInFreq $::platform_mclk

        SetupEVBConfiguration_ICE9140 BT2_CLOCKS $aux_link_mode $aux_drive_strength $mckosocdiv $mcki_mhz $aux_compress

        #set PADCTRLs (TODO: remove when SetupEVBConfiguration_ICE9140 does it: see MISCTOOL/3062)
        ::syscfg::chpc::ActivateConfig PLATFORM_PADCTRL

        # unfreeze pins
        ::syscfg::UnfreezeIOPins

        ::syscfg::PrintClkFreq

        #may want to do some handshaking with the AP if the SHM host interface is used
        #Do IPC handshaking unconditionally, controlled only by an env var
        #if { $::host_interface_shm != 0 } {}
        if { $::_dxpTarget == "NXV_DXP_TARGET_TYPE_DEBUG_ADAPTOR" } {
            if { [info exists ::env(ENABLE_RUNI_BROM_IPC_HANDSHAKING)] } {
                IPCprepareDebugRun
                set platcfg [IPCgetPlatCfgFromBootBuffer]
                if { $platcfg != ""} {
                    set ::boot_buffer_platcfg $platcfg
                }
            }
        }

        if { $::tb_ap_mailbox != 0 } {
            #Clearing the TB AP mailbox status, required for running standalone testbench variants
            puts "Clearing TB AP mailbox"
            ClearTbApMailbox
        }
    }

    if {$wasQuiet == 0} {
        options -nquiet
    }
}

#proc DPRAM_init {} {
    #XMC_SMC_CS2_CONFIG_OFFSET
    #SMC_SMBIDCYR2_OFFSET
    #SMC_SMBWSTRDR2_OFFSET
    #SMC_SMBWSTWRR2_OFFSET
    #
    #    set smc_base_dpram $livanto_memmap::RTB_RTB_HOST_BASE
    #    set smc_base_sem $livanto_memmap::RTB_RTB_HOST_BASE
    #    set rtb_host_wakeup_ctrl [format 0x%x [expr $rtb_host_start + $livanto_memmap::RTB_HOST_WAKEUP_CTRL_OFFSET]]
    #    set clr_32kHz_mask ~0x2F0
    #    addrvalid -rw   $rtb_host_start  [format 0x%x [expr $rtb_host_start + $livanto_memmap::RTB_RTB_HOST_SIZE]]  RTB_HOST_REGS
    #
#}


#
# Set platform configuration: to be used if BT2 not ran,
#  on a single flash platform, to indicate content of
#  platform config file and store it for modem application
#
proc set_plat_config {{plat_config ""}} {
    set wasQuiet [options -quiet]

    # Get addr of buffer used by the provided binary to store debug platform config:
    set plat_config_addr [symb2addr dxp_run_platform_config]

    if {$plat_config_addr != 0xdeadbeef} {
        # Copy string bytes per bytes in memory as integers...:
        for {set id 0} {$id < [string length $plat_config]} {incr id 1} {
            set str [scan [string index $plat_config $id] %c]
            poke 1 [expr $plat_config_addr + $id] $str
        }
        puts "Platform config for runi set @$plat_config_addr: $plat_config"
    } else {
        puts "ERROR: can't set platform config for runi : $plat_config"
    }

    if {$wasQuiet == 0} {
        options -nquiet
    }
}

#
# Set platform configuration: to be used if BT2 not ran,
#  on a single flash platform, to indicate content of
#  platform config file and store it for modem application
#
proc set_ver_compat {ver_compat} {

    # Get addr of buffer used by the provided binary to store debug version compatibility:
    set ver_compat_addr [symb2addr dxp_run_serial_version_compatibility]
    if {$ver_compat_addr != 0xdeadbeef} {
        # Copy given value in dxp_run_serial_version_compatibility integer
        mw $ver_compat_addr $ver_compat
    }
}

# define a procedure to handle setup following reset
# - if the target is not a software model, we need to configure it
#

#
# Set boot configuration
#
proc set_boot_config {{boot_config ""}} {
    global _nand_type

    set _nand_type $boot_config
    set config_word 0

    if {$boot_config eq ""} {
        puts ""
        puts "set_boot_config <boot_config>"
        puts "Select boot configuration:"
        puts "- nor (default)"
        puts "- nandx8"
        puts "- nandx16"
        puts "- smallnandx8"
        puts "- 4bitnandx16"
        puts "- uart0_115200"
        puts "- uart1_115200"
        puts "- uart2_115200"
        puts "- uart2_921600"
        # boot from UART2 at 921600 with flow control enabled:
        puts "- uart2_921600_fc"
        puts "- uart2_3686300"
        # boot from UART2 at 3686300 with flow control enabled:
        puts "- uart2_3686300_fc"
        # boot from HSI, channel 0, width 2 bits, framed, break enabled
        puts "- hsi0_w2b_f_b"
        # boot from HSI, channel 0, width 3 bits, framed, break enabled
        puts "- hsi0_w3b_f_b"
        # boot from USI UART at 3.32M with flow control enabled:
        puts "- usi_uart_3P32M_fc"
        # boot from USI UART at 115.2K without flow control:
        puts "- usi_uart_115200"
    } else {
        puts "set_boot_config $boot_config"
    }

    # set the shadow fuse registers to look like the fuses are saying boot from <boot_config>
    # this is for config 0 which is default for debugger attached
    if {$boot_config eq "nandx8"} {
        set config_word 0x7200
    } elseif {$boot_config eq "nandx16"} {
        set config_word 0x7A00
    } elseif {$boot_config eq "smallnandx8"} {
        set config_word 0x4200
    } elseif {$boot_config eq "4bitnandx16"} {
        if {$::_dxpCPUType == "ICE9040-A0"} {
            set config_word 0x4b0010
        }
    } elseif {$boot_config eq "uart0_115200"} {
        set config_word 0x2000
    } elseif {$boot_config eq "uart1_115200"} {
        set config_word 0x2800
    } elseif {$boot_config eq "uart2_115200"} {
        set config_word 0x3000
    } elseif {$boot_config eq "uart2_921600"} {
        set config_word 0x9011
    } elseif {$boot_config eq "uart2_921600_fc"} {
        set config_word 0x19011
    } elseif {$boot_config eq "uart2_3686300"} {
        set config_word 0xD019
    } elseif {$boot_config eq "uart2_3686300_fc"} {
        set config_word 0x1D019
    } elseif {$boot_config eq "nor"} {
        set config_word 0x4980
    } elseif {$boot_config eq "hsi0_w2b_f_b"} {
        set config_word 0x8300
    } elseif {$boot_config eq "hsi0_w3b_f_b"} {
        set config_word 0xC300
    } elseif {$boot_config eq "usi_uart_3P32M_fc"} {
        set config_word 0x1e60000
    } elseif {$boot_config eq "usi_uart_115200"} {
        set config_word 0x36060000
    } else {
        puts "Invalid boot configuration"
    }

    if {$config_word != 0} {
        # Now, write the config word into config_word_0
        # which is the config_word selected when debugger is plugged
        if {$::_dxpCPUType == "ICE9040-A0"} {
            # chpc_efuse_7
            syscfg::chpc::WriteReg EFUSE_STATE_7 $config_word
        }
    }
}

#if defined ICERA_FEATURE_INTERNAL
#
# Enable/disable ice-ice dev keys
#
proc enable_dev_keys { enable } {

    set efuse19 [syscfg::chpc::ReadReg EFUSE_STATE_19]
    if {$enable == 1} {
        set efuse19 [expr ($efuse19 & ~0x00000030)]
    } else {
        set efuse19 [expr ($efuse19 | 0x00000030)]
    }
    syscfg::chpc::WriteReg EFUSE_STATE_19 $efuse19
}

proc set_fuse_id { fuse_id } {

    syscfg::chpc::WriteReg EFUSE_STATE_18 $fuse_id
}

proc get_fuse_id { } {

    set fuse_id [syscfg::chpc::ReadReg EFUSE_STATE_18]
    puts [format "Fuse id: 0x%x" $fuse_id]
}

proc is_fuse_id { } {

    set fuse_id [syscfg::chpc::ReadReg EFUSE_STATE_18]
    if {$fuse_id==0} {
        puts "Fuse id is not programmed"
    } else {
        puts "Fuse id is programmed"
    }
}


proc is_dev_device {} {

    set efuse13 [syscfg::chpc::ReadReg EFUSE_STATE_13]
    set efuse13_sh [peek 4 [expr $livanto_memmap::CHPC_BASE + $livanto_memmap::CHPC_EFUSE_STATE_13_OFFSET]]
    set efuse13_sh [expr ($efuse13_sh & 0x00000030)]

    if {$efuse13_sh==0x00000030} {
        puts "It's a production device"
    } else {
        puts "It's a development device"
    }
}
# Set HW product ID
proc set_hw_product_id {value} {
    #code below is 8060 code
    #set efuse4 [syscfg::chpc::ReadReg EFUSE_STATE_4]
    #set value [expr ($value << 16)]
    #set efuse4 [expr ($efuse4 | $value) ]
    #syscfg::chpc::WriteReg EFUSE_STATE_4 $efuse4
    puts "ERROR: No code for 9xxx"
}
#endif

set first_rst 1
proc PlatformResetCB {} {
    global _dxpTarget
    global _start_from_boot
    global _flash_size
    global first_rst
    global _hwplat
    global _nand_type
    global mckosocdiv

    if {$::_dxpCPUType != "ICE9040-A0" && $::_dxpCPUType != "ICE9140-A0"} {
        puts "!!!!! UNSUPPORTED PLATFORM: $::_dxpCPUType !!!!!"
        exit 43
    }

    if {$::_dxpCPUType == "ICE9040-A0" || $::_dxpCPUType == "ICE9140-A0"} {
        Set9x40EfuseStates
    }

    if {$_dxpTarget != "NXV_DXP_TARGET_TYPE_SOFTWARE_MODEL" || $::_dxpCPUType == "ICE9040-A0" || $::_dxpCPUType == "ICE9140-A0"} {
        if {$_start_from_boot == 0} {
            set wasQuiet [options -quiet]
            puts "Getting Ready..."
            if {$::_dxpCPUType == "ICE9040-A0"} {
                puts "Calling SetupPlatform for 9040"
                SetupPlatformConfiguration9040
            }
            if {$::_dxpCPUType == "ICE9140-A0"} {
                puts "Calling SetupPlatform for 9140"
                SetupPlatformConfiguration9140
            }
            if {$wasQuiet == 0} {
                options -nquiet
            }
        } else {
            if {$_nand_type != ""} {
                set_boot_config $_nand_type
            }
            if {$first_rst == 1} {
                set _dxpInstance 0
                setreg -pc $livanto_memmap::EXT_STATIC_BROM_BASE
                set _dxpInstance 1
                setreg -pc $livanto_memmap::EXT_STATIC_BROM_BASE
                set _dxpInstance 0
                set first_rst 0
            }
        }
    }
}

# setup the TCL variable which is invoked following reset -ext operations
# Overwrites the
#
set _dxpResetCB PlatformResetCB

proc Set9x40EfuseStates {} {
    # Indicate internal boot mode:
    # EFUSE 19, bit 0 or 1 to 1.
    set efuse19 [syscfg::chpc::ReadEFUSE 19]
    set efuse19 [expr $efuse19 | 0x1 ]
    syscfg::chpc::WriteEFUSE 19 $efuse19

    if {$::_dxpCPUType == "ICE9040-A0"} {
        # Indicate authentication enable:
        # EFUSE 19, bit 2 or 3 to 1
        set efuse19 [syscfg::chpc::ReadEFUSE 19]
        set efuse19 [expr $efuse19 | 0x4 ]
        syscfg::chpc::WriteEFUSE 19 $efuse19
    }
}

proc set_fuse_hwprodid { value } {
    set efuse21 [syscfg::chpc::ReadEFUSE 21]
    set hwprodid [expr $value & 0xffff]
    set efuse21 [expr $efuse21 | $hwprodid ]
    syscfg::chpc::WriteReg EFUSE_STATE_21 $efuse21
}
