#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

python3 -i run_hme.py -i GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_testfile.root -o GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M450_HME.root -it 100 -doSL 0 -doDL 1 -debug 0
