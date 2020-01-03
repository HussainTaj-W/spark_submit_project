@echo off

IF DEFINED SSP_PYTHON (
	set PY_FOR_SSP=%SSP_PYTHON%
) ELSE (
	set PY_FOR_SSP=python
)

%PY_FOR_SSP% .spark-submit-project\spark-submit-project.py %*