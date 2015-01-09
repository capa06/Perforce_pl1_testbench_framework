#//************************************************************************************************
#// Icera Inc
#// Copyright (c) 2005-2007
#// All rights reserved
#//************************************************************************************************
#// $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_profile_ids.h#1 $
#// $Revision: #1 $
#// $Date: 2014/11/13 $
#// $Author: joashr $
#//************************************************************************************************


#/** @defgroup os_uist os_abs UIST */
#/** @{ */

#/**@file os_uist_ids.h os_abs interface for User Instrumented Software Trace. */
#/**   This file is both in TCL and C language. The dash before the comments   */
#/**    should not be removed.                                                 */
#/**   CAVEAT: It may be also used by Python scripts in:                       */
#/**           - the 'tools' folder present in this branch root directory      */
#/**           - the //swtools depot                                           */
#/**           Here is a non exhaustive list of python scripts.                */
#/**           In the 'tools' folder present in this branch root directory:    */
#/**           - tools/BoardConfig.py                                          */
#/**           In //swtools depot:                                             */
#/**           - macchiato/createMacchiatoPackage.py                           */
#/**           - macchiato/createReleaseToCustomer.py                          */
#/**           - ristretto/createArchive.py                                    */

#ifndef DRV_USB_PROFILE_IDS_H
#define DRV_USB_PROFILE_IDS_H

#//************************************************************************************************
#// Tcl Macros
#//************************************************************************************************
#if 0 /* Not used in C but in TCL only */

source $sw_root/drivers/public/drv_usb_profile_ids_macro_defs.h
source $sw_root/drivers/public/drv_usb_profile_ids_table.h

#endif

#//************************************************************************************************
#// C Macros
#//************************************************************************************************

#include "drv_usb_profile_ids_macro_defs.h"
#include "drv_usb_profile_ids_table.h"

#undef USB_PROFILE_ID_BEGIN
#undef USB_PROFILE_ID_END
#undef USB_PROFILE_ID

#///
#/** @endcond */
#///
#///
#/** @} END OF FILE */
#///

#endif /* DRV_USB_PROFILE_IDS_H */

