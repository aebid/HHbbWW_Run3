#!/bin/bash

list_of_files=("test0.root" "test1.root")
filename=("filename.sh")
runyear=("2022")
isMC=("1")
XS=("1.0")
DNN=("-1")
SF=("0")
HLTCut=("1")
useXrootD=("1")
PYTHON_FOLDER=("/afs/cern.ch/work/d/daebi/diHiggs/HHbbWW_Run3/python/")

HME_FOLDER=("/afs/cern.ch/work/d/daebi/diHiggs/HHbbWW_Run3/hme")
iterations=("1000")
singleHME=("0")
doubleHME=("0")

source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

ls -lh

if [ $useXrootD -eq "1" ]
then
  python3 ${PYTHON_FOLDER}/run_bbWW_processing.py -i ${list_of_files} -o out_by_hand_${filename}.root -d 0 -ry ${runyear} -MC ${isMC} -XS ${XS} -t ${DNN} -SF ${SF} -HLTCut ${HLTCut}
else
  filecount=0
  list_of_tmp_files=("")
  for in_filename in $list_of_files
  do
    xrdcp $in_filename tmp_file${filecount}.root
    list_of_tmp_files+=" tmp_file"${filecount}.root
    filecount=$((filecount+1))
  done
  python3 ${PYTHON_FOLDER}/run_bbWW_processing.py -i ${list_of_tmp_files} -o out_by_hand_${filename}.root -d 0 -ry ${runyear} -MC ${isMC} -XS ${XS} -t ${DNN} -SF ${SF} -HLTCut ${HLTCut}
  rm tmp_file*
fi

ls -lh

echo 'Starting HME'

python3 ${HME_FOLDER}/run_hme.py -i out_by_hand_${filename}.root -o out_by_hand_HME_${filename}.root -d 0 -it ${iterations} -SL ${singleHME} -DL ${doubleHME}

ls -lh

echo 'Done!'
