#!/bin/bash

echo "ls -l $PWD"
ls -l $PWD
export X509_USER_PROXY=$1

cd python/
python3 run_bbWW_processing.py -i root://cmsxrootd.fnal.gov//store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/aa5a4b71-fd45-45d9-bf26-ea4f2dc42882.root -o condor_output.root -t 0 -d 1
