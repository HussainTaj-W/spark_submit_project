@echo off

:: count args
SET argC=0
FOR %%x IN (%*) DO SET/A argC+=1

IF %argC% == 1 (

	GOTO CheckForCommands
) ELSE (

	GOTO RunSparkSubmit
)

:CheckForCommands

IF /I %1 == init (
	GOTO InitializeSSP
) ELSE (
	GOTO RunSparkSubmit
)

:InitializeSSP

echo SSP: Running init...

IF DEFINED SSP_HOME_DIR (
	echo SSP: Copying files from %SSP_HOME_DIR% to %cd%
	xcopy /s "%SSP_HOME_DIR%\.spark-submit-project" ".\.spark-submit-project\"
	GOTO end
) ELSE (
	echo SSP_HOME_DIR environment variable not defined.
	exit 1
)

:RunSparkSubmit


IF DEFINED SSP_PYTHON (
	set PY_FOR_SSP=%SSP_PYTHON%
) ELSE (
	set PY_FOR_SSP=python
)

IF EXIST .spark-submit-project\spark-submit-project.py (
	%PY_FOR_SSP% .spark-submit-project\spark-submit-project.py %*
) ELSE (
	ECHO spark-submit-project\spark-submit-project.py Not Found.
	ECHO     Run 
	ECHO         "ssp.bat init" 
	ECHO     to create these files in the current directory.
)

:end