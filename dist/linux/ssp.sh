#!/bin/bash

# Check if this was an init command
if [ $# = 1 ]
then 
	case $1 in
		([Ii][Nn][Ii][Tt]) 
		echo SSP: Running init..
		if [ -z "$SSP_HOME_DIR" ]
		then
			echo SSP_HOME_DIR environment variable not defined.
			exit 1
		else
			echo SSP: Copying files from $SSP_HOME_DIR
			cp -ri "$SSP_HOME_DIR/.spark-submit-project/" "./" 
			exit 0
		fi
		
		;;
	esac
fi

if [ -z "$SSP_PYTHON" ]
then
	PY_FOR_SSP=python
else
	PY_FOR_SSP=$SSP_PYTHON
fi

if [ -e ".spark-submit-project/spark-submit-project.py" ]
then
	$PY_FOR_SSP .spark-submit-project/spark-submit-project.py $@
else
	echo spark-submit-project/spark-submit-project.py Not Found.
	echo     Run 
	printf         "\tssp.sh init\n" 
	echo     to create these files in the current directory.
fi