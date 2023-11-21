#!/bin/bash

list_of_files=("test0.root" "test1.root")
filename=("filename.sh")
runyear=("2022")
isMC=("1")
XS=("1.0")
DNN=("-1")
SF=("0")
HLTCut=("1")
PYTHON_FOLDER=("/afs/cern.ch/work/d/daebi/diHiggs/HHbbWW_Run3/python/")

source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh

ls -lh
python3 ${PYTHON_FOLDER}/run_bbWW_processing.py -i ${list_of_files} -o out_by_hand_${filename}.root -d 0 -ry ${runyear} -MC ${isMC} -XS ${XS} -t ${DNN} -SF ${SF} -HLTCut ${HLTCut}

ls -lh

echo 'Done!'
