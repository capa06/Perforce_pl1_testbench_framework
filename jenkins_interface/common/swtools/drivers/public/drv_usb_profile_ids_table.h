#//************************************************************************************************
#// Nvidia
#// Copyright (c) 2011
#// All rights reserved
#//************************************************************************************************
#// $Id: //software/teams/phy/pl1_dev.br/modem/l123/phy/test/pl1_testbench_framework/jenkins_interface/common/swtools/drivers/public/drv_usb_profile_ids_table.h#1 $
#// $Revision: #1 $
#// $Date: 2014/11/13 $
#// $Author: joashr $
#//************************************************************************************************


#/** @addtogroup os_uist os_abs UIST */
#/** @{ */

#/**@file drv_usb_profile_ids_table.h List of USB profile IDs. */
#/**   This file is both in TCL and C language. The dash before the comments   */
#/**    should not be removed.                                                 */
#/**   There is voluntarily no include guard in this file.                     */
#/**   This file shall be included in a file defining BEFORE above macros:     */
#/**   USB_PROFILE_ID_BEGIN, USB_PROFILE_ID and USB_PROFILE_ID_END             */
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

#//************************************************************************************************
#// File System
#//************************************************************************************************
USB_PROFILE_ID_BEGIN

#// BE CAREFUL: do not modify the first values below (CPO is assuming specific values) 
USB_PROFILE_ID ( USB_PROFILE_DEFAULT )
USB_PROFILE_ID ( USB_PROFILE_WHCM_4A )
USB_PROFILE_ID ( USB_PROFILE_A )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2A )
USB_PROFILE_ID ( USB_PROFILE_ARCADYAN )
#// BE CAREFUL: do not modify the PIDs below, add new PID at the end of this list. 
USB_PROFILE_ID ( USB_PROFILE_WHCM_2A )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_AO )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_A3O )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_A3OEM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2AO )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2AEM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2AEMO )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_3AM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_4AM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_O )
USB_PROFILE_ID ( USB_PROFILE_IAD_AO )
USB_PROFILE_ID ( USB_PROFILE_IAD_A2OE )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AE )
USB_PROFILE_ID ( USB_PROFILE_IAD_2A2O )
USB_PROFILE_ID ( USB_PROFILE_IAD_A3O )
USB_PROFILE_ID ( USB_PROFILE_IAD_A3OEM )
USB_PROFILE_ID ( USB_PROFILE_IAD_A5O )
USB_PROFILE_ID ( USB_PROFILE_IAD_2A )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AO )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AOEM )
USB_PROFILE_ID ( USB_PROFILE_IAD_3A )
USB_PROFILE_ID ( USB_PROFILE_IAD_4A )
USB_PROFILE_ID ( USB_PROFILE_IAD_E )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AE )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AEMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AEM )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AEO )
USB_PROFILE_ID ( USB_PROFILE_MASS_STORAGE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_A3OEM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AOEM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_4AM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AEM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AEMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AEO )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_A )
USB_PROFILE_ID ( USB_PROFILE_3A )
USB_PROFILE_ID ( USB_PROFILE_3AM )
USB_PROFILE_ID ( USB_PROFILE_O )
USB_PROFILE_ID ( USB_PROFILE_TEST )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3A )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_4A )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_3A )
USB_PROFILE_ID ( USB_PROFILE_WHCM_A )
USB_PROFILE_ID ( USB_PROFILE_IAD_A )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AOEMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AOEMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AEOM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AEOM )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_AEA )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_AEAM )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_AE2A )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_AE2AM )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AM )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AMA )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AMA )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2AM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2AMA )
USB_PROFILE_ID ( USB_PROFILE_VENDOR02_A2O )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_4AM )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_2M )
USB_PROFILE_ID ( USB_PROFILE_COMPOSITE_3M )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AN )
USB_PROFILE_ID ( USB_PROFILE_IAD_2ANM )
USB_PROFILE_ID ( USB_PROFILE_IAD_2ANMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_AO2E )
USB_PROFILE_ID ( USB_PROFILE_IAD_AO2EM )
USB_PROFILE_ID ( USB_PROFILE_IAD_AO2EMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_AO2EM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_AO2EMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_2AMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_2AMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AEM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AEM )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AEMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AEMO )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AN )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AN )
USB_PROFILE_ID ( USB_PROFILE_IAD_5AN )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AEO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3AEO )
USB_PROFILE_ID ( USB_PROFILE_IAD_3A2E )
USB_PROFILE_ID ( USB_PROFILE_IAD_4A2E )
USB_PROFILE_ID ( USB_PROFILE_WHCM_3A2E )
USB_PROFILE_ID ( USB_PROFILE_WHCM_4A2E )
USB_PROFILE_ID ( USB_PROFILE_IAD_4AE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_4AE )
USB_PROFILE_ID ( USB_PROFILE_IAD_5AE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_5AE )
USB_PROFILE_ID ( USB_PROFILE_WHCM_B )
USB_PROFILE_ID ( USB_PROFILE_B )
USB_PROFILE_ID ( USB_PROFILE_IAD_B )
USB_PROFILE_ID ( USB_PROFILE_IAD_3AB )
USB_PROFILE_ID ( USB_PROFILE_VENDOR01_4AEM )
USB_PROFILE_ID ( USB_PROFILE_WIRELESS_R )
USB_PROFILE_ID ( USB_PROFILE_IAD_R )
USB_PROFILE_ID ( USB_PROFILE_WHCM_R )
USB_PROFILE_ID ( USB_PROFILE_R )
USB_PROFILE_ID ( USB_PROFILE_IAD_R2AM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_R2AM )
USB_PROFILE_ID ( USB_PROFILE_IAD_R2AMO )
USB_PROFILE_ID ( USB_PROFILE_WHCM_R2AMO )
USB_PROFILE_ID ( USB_PROFILE_WIRELESS_R2AMO )
USB_PROFILE_ID ( USB_PROFILE_WIRELESS_RM )
USB_PROFILE_ID ( USB_PROFILE_IAD_RM )
USB_PROFILE_ID ( USB_PROFILE_WHCM_RM )
USB_PROFILE_ID ( USB_PROFILE_IAD_B2A )
USB_PROFILE_ID ( USB_PROFILE_IAD_B3A )
USB_PROFILE_ID ( USB_PROFILE_WHCM_B2A )
USB_PROFILE_ID ( USB_PROFILE_IAD_MB )
USB_PROFILE_ID ( USB_PROFILE_IAD_MB2A )
USB_PROFILE_ID ( USB_PROFILE_IAD_MB3A )
USB_PROFILE_ID ( USB_PROFILE_GENERIC_ANDROID )
USB_PROFILE_ID ( USB_PROFILE_IAD_R3A )
USB_PROFILE_ID ( USB_PROFILE_IAD_RB )
USB_PROFILE_ID ( USB_PROFILE_IAD_RB3A )
USB_PROFILE_ID ( USB_PROFILE_IAD_4AON )
USB_PROFILE_ID_END

#///
#/** @endcond */
#///
#///
#/** @} END OF FILE */
#///
