#!/bin/bash

list_of_files=("test0.root" "test1.root")

cd python
export X509_USER_PROXY=../$1

for i in ${!list_of_files[@]}
do
    echo 'file is '
    echo ${list_of_files[$i]}
    ls -lh
    python3 run_bbWW_processing.py -i root://cms-xrd-global.cern.ch//${list_of_files[$i]} -o ../condor_output_${i}.root -t 0 -d 0
done

cd ..
ls -lh

echo 'Done!'
