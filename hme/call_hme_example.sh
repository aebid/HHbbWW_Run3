#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc13-opt/setup.sh

python3 -i run_hme.py -i input.root -o output.root -it 100 -SL 0 -DL 1 -d 0
