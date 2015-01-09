#//************************************************************************************************
#// Nvidia
#// Copyright (c) 2011
#// All rights reserved
#//************************************************************************************************
#// $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_profile_ids_macro_defs.h#1 $
#// $Revision: #1 $
#// $Date: 2014/11/13 $
#// $Author: joashr $
#//************************************************************************************************


#/** @addtogroup os_uist os_abs UIST */
#/** @{ */

#/**@file drv_usb_profile_ids_macro_defs.h USB profile IDs in an enum list.   */
#/**   This file is both in TCL and C language. The dash before the comments  */
#/**    should not be removed.                                                */
#/**   CAVEAT: It may be also used by Python scripts in:                      */
#/**           - the 'tools' folder present in this branch root directory     */
#/**           - the //swtools depot                                          */
#/**           Here is a non exhaustive list of python scripts.               */
#/**           In the 'tools' folder present in this branch root directory:   */
#/**           - tools/BoardConfig.py                                         */
#/**           In //swtools depot:                                            */
#/**           - macchiato/createMacchiatoPackage.py                          */
#/**           - macchiato/createReleaseToCustomer.py                         */
#/**           - ristretto/createArchive.py                                   */

#ifndef DRV_USB_PROFILE_IDS_MACRO_DEFS_H
#define DRV_USB_PROFILE_IDS_MACRO_DEFS_H

#//************************************************************************************************
#// Tcl Macros
#//************************************************************************************************
#if 0 /* Not used in C but in TCL only */

set usb_num_profiles 0

#proc USB_PROFILE_ID {lpar type tag msg rpar} {
proc USB_PROFILE_ID {lpar tag rpar} {
    global usb_num_profiles

    global usb_profile_name
    global usb_profile_dictionary

    # remove parenthesis and split parameters
#    set type  [string trim $type ",() "];
    set msg  [string trim $tag ",() "];
    set usb_profile_name($usb_num_profiles) "$tag"
    set usb_profile_dictionary($tag) $usb_num_profiles 

    incr usb_num_profiles;
}

proc USB_PROFILE_ID_BEGIN {} {}
proc USB_PROFILE_ID_END {} {}

proc LOAD_USB_PROFILE_IDS_TABLE {} {
    source $sw_root/drivers/public/drv_usb_profile_ids_list.h
}
#endif

#//************************************************************************************************
#// C Macros
#//************************************************************************************************

#///Define the start of the USB_PROFILE ID table
#///
#///@param _START_OFFSET_ ID offset. All previous IDs are reserved.
#define USB_PROFILE_ID_BEGIN                   typedef enum {

#///Define the end of the USB_PROFILE ID table
#///
#define USB_PROFILE_ID_END                     USB_NUM_PROFILES, USB_PROFILE_INVALID = USB_NUM_PROFILES} drv_UsbProfileId;

#///Boilerplate macro which defines a USB_PROFILE id.
#///
#///@param _TAG_    define referencing the USB_PROFILE
#///@param _MSG_    Message displayed in dxp-run at run time
#///define USB_PROFILE_ID(__TYPE__, _TAG_, _MSG_) _TAG_,
#define USB_PROFILE_ID(_TAG_) _TAG_,

#///
#/** @endcond */
#///
#///
#/** @} END OF FILE */
#///

#endif /* DRV_USB_PROFILE_IDS_MACRO_DEFS_H */

