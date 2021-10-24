#!/bin/bash

set -e
set -x
default_pythonpath=$PYTHONPATH:.
export PYTHONPATH=${default_pythonpath:-.}
for f in `ls tests/*.py`; do
	python $f
	if [ $? -gt 0 ]; then
		exit 1
	fi
done
set +x
set +e
