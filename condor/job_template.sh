#!/bin/bash

list_of_files=("test0.root" "test1.root")
filename=("filename.sh")
runyear=("2022")

cd python
export X509_USER_PROXY=../$1


ls -lh
python3 run_bbWW_processing.py -i ${list_of_files} -o ../out_condor_${filename}.root -t 0 -d 0 -ry ${runyear}

cd ..
ls -lh

echo 'Done!'
