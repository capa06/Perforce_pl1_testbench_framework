#!/bin/bash
#-------------------------------------------------------------------------------------------------
#
# pl1jenkins_linux.sh
#
#  Usage:
#    pl1jenkins_linux.sh <loglevel> <rat> <url> <jobtype> [<branch> <psu>]
# 
#  Description:
#    Script used for calling the pl1testbench Jenkins interface 
#
#  Input Parameters:                                                                                       
#     loglevel : { 'INFO', 'DEBUG' }
#          rat : { 'LTE_FDD', 'LTE_TDD', 'WCDMA'                        }
#          url : autobuild URL
#      jobtype : {'per_cl', 'nightly', 'weekly'                     }
#       branch : perforce branch (optional, not used)
#          psu : psu flag (optional, not used)
#
#  Examples:  	 
#    pl1jenkins_linux.sh INFO "[LTE,WCDMA,RF]" http://bs.nvidia.com/systems/datacard-builds/software/main.br/CL673206-i500-121-1725-ti-att--1e4a95ea per_cl
#
#-------------------------------------------------------------------------------------------------



#-------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------
path_here=`pwd`

# get the pl1 test framework root directory
cd ../../
TEST_FRAMEWORK_ROOT_DIR=`pwd`

cd ${path_here}


# get results directory for all the rats
#test_dir="$(dirname "$path_here")"
LTE_RESULTS_DIR="${TEST_FRAMEWORK_ROOT_DIR}/lte/results/latest"
WCDMA_RESULTS_DIR="${TEST_FRAMEWORK_ROOT_DIR}/wcdma/results/latest"
RF_RESULTS_DIR="${TEST_FRAMEWORK_ROOT_DIR}/pl1_rf_system/results/latest"
JENKINS_UPLOAD_DIR="${TEST_FRAMEWORK_ROOT_DIR}/jenkins_interface/linux/results/final"
ARCHIVE_PARENT_DIR="${TEST_FRAMEWORK_ROOT_DIR}/jenkins_interface/linux/results"


#-------------------------------------------------------------------------
# Global Functions
#-------------------------------------------------------------------------
function ShowHelp {
    echo "----------------------------------------------------------------------------------" 
    echo "Description:                                                                      "
  	echo "  Script used for calling the pl1testbench Jenkins interface                      "
  	echo "                                                                                  "
    echo "Usage:                                                                            "
    echo "    $0 <loglevel> <rat> <url> <jobtype> [<branch> <psu>]                          "
  	echo "                                                                                  "
    echo "Input Parameters:                                                                 "
    echo "    loglevel : { 'INFO', 'DEBUG'    }                                             "                                    
    echo "         rat : { 'LTE_FDD', 'LTE_TDD', 'WCDMA', 'RF'     }                        "                                    
    echo "         url : <autobuild URL>                                                    "                                   
    echo "     jobtype : { 'per_cl', 'nightly', 'weekly'}                                   "                                   
  	echo '                                                                                  '
    echo 'Examples:                                                                         '
    echo '    $0 -h                                                                         '
  	echo '   pl1jenkins_linux.sh INFO "[LTE_FDD,WCDMA,RF]"  http://bs.nvidia.com/systems/datacard-builds/software/main.br/CL673206-i500-121-1725-ti-att--1e4a95ea per_cl'
    echo 'END USAGE                                                                         '           
    echo '----------------------------------------------------------------------------------' 
}

# get a single empyty Jenkins status file from the 
# empty status files generated for each rat
# if any of the status files is inconclusive 
# then STATUS_UNSTABLE else if any is fail
# then STATUS_FAIL else if success then STATUS_SUCCESS
# the default is STATUS_UNSTABLE
function status_verdict_filename() 
{
	local my_verdict='STATUS_UNSTABLE.txt'
	local  __resultvar=$1

	local final_f=$JENKINS_UPLOAD_DIR
	local status_file_list=`ls $final_f | grep '.*STATUS'`
	echo "These are the current list of files in $JENKINS_UPLOAD_DIR"
	echo "$status_file_list"

	local m_regex_fail='.*FAIL'
	local m_regex_success='.*SUCCESS'
	local m_regex_incon='.*UNSTABLE'
    
	echo ${status_file_list} | grep -iq ${m_regex_incon}
	if [[ $? -eq 0 ]]; then
		my_verdict="STATUS_UNSTABLE.txt"
		echo "file match for inconclusive verdict"
		eval $__resultvar="'$my_verdict'"
		return
	fi

	echo ${status_file_list} | grep -iq ${m_regex_fail}
	if [[ $? -eq 0 ]]; then
		my_verdict="STATUS_FAIL.txt"
		echo "file match for fail verdict"
		eval $__resultvar="'$my_verdict'"
		return
	fi

	echo ${status_file_list} | grep -iq ${m_regex_success}
	if [[ $? -eq 0 ]]; then
		my_verdict="STATUS_SUCCESS.txt"
		echo "file match for success verdict"
		eval $__resultvar="'$my_verdict'"
		return
	fi

	# should not come to here
	echo "cannot determine verdict"
	eval $__resultvar="'$my_verdict'"
	return
}

function remove_status_files()
{
	local final_f=$JENKINS_UPLOAD_DIR
	local cmd

	local status_file_list=`ls $final_f | grep '.*STATUS'`
	echo "removing the following jenkins status files from folder $JENKINS_UPLOAD_DIR"
	echo "$status_file_list"
	for status_file in $status_file_list
		do
			cmd="rm ${final_f}/${status_file}"
			echo $cmd
			$cmd
		done
}

# get the name of the final 
function get_final_f_name()
{
	local date_format
	local time_format
	local yyyy_mm_dd
	local hh_mm_ss
	local folder_name

	date_format=$(date +%F)
	# remove hyphens from date format string
	yyyy_mm_dd=$(echo "$date_format" | sed 's\-\\g')

	time_format=$(date +%T) 
	# remove hyphens from date format string
	hh_mm_ss=$(echo "$time_format" | sed 's\:\\g')

	folder_name=${yyyy_mm_dd}_${hh_mm_ss}
	echo $folder_name
}

# ************************************************************************************************
#                                            MAIN
# ************************************************************************************************
# Redirect stdout and stderr to file 

# Input parameters set definition
NUM_PARMS=4

# Error codes definition
ERR_CODE_00="INVALID NUMBER OF PARAMETERS" 
ERR_CODE_01="INVALID INPUT PARAMETER VALUE" 
error_parms=0

# *********************************************
# Check parameters
# *********************************************
# Check if help is required 
if [[ $1 == "-h" ]]; then
  ShowHelp
  exit 0
fi


# Check the number of input parameters  
if [[ $# -lt $NUM_PARMS ]]; then
  echo "----------------------------------------------------------------------------------" 
  echo "ERROR:: $0 :: $ERR_CODE_00"         
  echo "----------------------------------------------------------------------------------" 
  ShowHelp
  exit 1
fi

# Assign NON OPTIONAL parameters
loglevel=$1
rat_list=$2
url=$3
jobtype=$4


# create directory from which Jenkins will extract the results
# if the directory does not exist
# clear old result files from this directory if it does exist
if [ -d "${JENKINS_UPLOAD_DIR}" ]
then
	echo "Jenkins upload directory already exists, no need to create"
	#rmDirContents="rm -rf ${JENKINS_UPLOAD_DIR}"
	rmDirContents="rm ${JENKINS_UPLOAD_DIR}/*"
	echo $rmDirContents
	$rmDirContents
else
	mkDirCmd="mkdir -p ${JENKINS_UPLOAD_DIR}"
	echo $mkDirCmd
	$mkDirCmd
	echo "Jenkins upload directory ${JENKINS_UPLOAD_DIR} successfully created"
fi

# remove brackets, replace comma by spaces
#echo $rat_list
format_rat_list=$(echo "$rat_list" | sed 's\[][]\\g' | sed -e 's\,\ \g' -e 's/"//g')
#echo $format_rat_list

for rat in $format_rat_list
	do

		if  [[ (${loglevel} != 'DEBUG') && (${loglevel} != 'INFO') ]] ; then
		  echo "----------------------------------------------------------------------------------" 
		  echo "ERROR:: $0:: loglevel=${loglevel} ${ERR_CODE_01}"
		  echo "----------------------------------------------------------------------------------" 
		  ShowHelp
		  exit 1
		fi
		
		if  [[ (${rat} != 'LTE_FDD') && (${rat} != 'LTE_TDD') && (${rat} != 'WCDMA') && (${rat} != 'RF') ]] ; then
		  echo "----------------------------------------------------------------------------------" 
		  echo "ERROR:: $0:: rat=${rat} ${ERR_CODE_01}"
		  echo "----------------------------------------------------------------------------------" 
		  ShowHelp
		  exit 1
		fi


		if [[ (${jobtype} != 'per_cl') && (${jobtype} != 'nightly') && (${jobtype} != 'weekly') ]]; then
		  echo "----------------------------------------------------------------------------------" 
		  echo "ERROR:: $0:: jobtype=${jobtype} ${ERR_CODE_01}"
		  echo "----------------------------------------------------------------------------------" 
		  ShowHelp
		  exit 1
		fi

		echo "Starting PL1 testbench for ${rat}"

		cmd_run="python pl1jenkins_linux.py -log=${loglevel} -r=${rat} -u=${url} -t=${jobtype}"
		echo $cmd_run
		${cmd_run}

		# copy results from the respective directories for each rat
		# to Jenkins upload directory
		if [ $(echo "$rat" | grep -Ei "lte*") ] ; then
			# copy source destination
			echo "copying results files for LTE regression tests"
			cmd_cp="cp -a ${LTE_RESULTS_DIR}/. ${JENKINS_UPLOAD_DIR}/"
			echo ${cmd_cp}
			${cmd_cp}

		# there is no need to copy results to ${JENKINS_UPLOAD_DIR} as this
		# this is handled by the unittest framwork for WCDMA

		elif [ $(echo "$rat" | grep -Ei "rf*") ] ; then
			# copy source destination
			echo "copying results files for RF factory tests"
			#cmd_cp="cp -avrf ${RF_RESULTS_DIR} ${JENKINS_UPLOAD_DIR}"
			cmd_cp="cp -a ${RF_RESULTS_DIR}/. ${JENKINS_UPLOAD_DIR}/"
			echo ${cmd_cp}
			${cmd_cp}
		fi
			
	done

# get a single consolidated status file
status_verdict_filename status_file_name


# remove the status files for each rat
remove_status_files

# create single consolidated status file and
# upload status file to jenkins upload directory
cmd_touch="touch ./${status_file_name}"
echo "Creating single status file $status_file_name"
echo $cmd_touch 
$cmd_touch
echo "moving $status_file_name to ${JENKINS_UPLOAD_DIR}"
cmd_mv="mv ./$status_file_name ${JENKINS_UPLOAD_DIR}"
echo $cmd_mv
$cmd_mv


# copy jenkins upload directory to archive
archive_folder=$(get_final_f_name)
echo "copying results to archive folder ${ARCHIVE_PARENT_DIR}/${archive_folder}"
cmd_cp="cp -a ${JENKINS_UPLOAD_DIR}/. ${ARCHIVE_PARENT_DIR}/${archive_folder}"
echo $cmd_cp
$cmd_cp

cd ${path_here}
