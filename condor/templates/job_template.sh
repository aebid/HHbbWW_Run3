#!/bin/bash

list_of_files=("test0.root" "test1.root")
filename=("filename.sh")
runyear=("2022")
runera=("A")
isMC=("1")
XS=("1.0")
DNN=("-1")
SF=("0")
HLTCut=("1")
useXrootD=("1")


cd python
export X509_USER_PROXY=../$1
export XRD_NETWORKSTACK=IPv4
export XRD_REQUESTTIMEOUT=1800

source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

ls -lh

if [ $useXrootD -eq "1" ]
then
  python3 run_bbWW_processing.py -i ${list_of_files} -o ../out_condor_${filename}.root -d 0 -ry ${runyear} -re ${runera} -MC ${isMC} -XS ${XS} -t ${DNN} -SF ${SF} -HLTCut ${HLTCut} -nEvts 100000
else
  filecount=0
  list_of_tmp_files=("")
  for in_filename in $list_of_files
  do
    xrdcp $in_filename tmp_file${filecount}.root
    list_of_tmp_files+=" tmp_file"${filecount}.root
    filecount=$((filecount+1))
  done
  python3 run_bbWW_processing.py -i ${list_of_tmp_files} -o ../out_condor_${filename}.root -d 0 -ry ${runyear} -re ${runera} -MC ${isMC} -XS ${XS} -t ${DNN} -SF ${SF} -HLTCut ${HLTCut} -nEvts 100000
  rm tmp_file*
fi

cd ..
ls -lh

echo 'Done!'
