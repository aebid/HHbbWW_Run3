#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

#python3 -i run_bbWW_processing.py -i GluGlutoRadiontoHHto2B2Vto2B2JLNu_M-1000_testfile.root -o test.root -ry 2022 -MC 1 -t 0 -d 0 -XS 1.0 -SF 0 -HLTCut 1

#python3 -i run_bbWW_processing.py -i GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-1400_testfile.root -o test.root -ry 2022 -MC 1 -t 0 -d 0 -XS 1.0 -SF 0 -HLTCut 1

python3 -i run_bbWW_processing.py -i GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_testfile.root -o test.root -ry 2022 -MC 1 -t 0 -d 0 -XS 1.0 -SF 0 -HLTCut 0
