#!/bin/bash

export X509_USER_PROXY=$1

list_of_files=("test0.root" "test1.root")

cd python

for i in ${!list_of_files[@]}
do
    echo 'file is '
    echo ${list_of_files[$i]}
    xrdcp root://cms-xrd-global.cern.ch//${list_of_files[$i]} temp_file_${i}.root
    ls -lh
    python3 run_bbWW_processing.py -i temp_file_${i}.root -o ../condor_output_${i}.root -t 0 -d 0
    rm temp_file_${i}.root
done

cd ..
ls -lh
hadd condor_output.root *condor_output_*.root

echo 'Done!'
