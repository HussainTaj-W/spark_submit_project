#!/bin/bash

if [ -z "$SSP_PYTHON" ]
then
	PY_FOR_SSP=python
else
	PY_FOR_SSP=$SSP_PYTHON
fi

$PY_FOR_SSP .spark-submit-project/spark-submit-project.py $@
