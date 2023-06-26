# HHbbWW_Run3

Package for TAMU analysis of H -> hh -> bbWW

Instructions to use directly
```
cd python
python3 run_bbWW_processing.py -i Input_File -o Output_File -t DNN_Truth_Value(see run_bbWW_processing.py) -d debug
```
Or on lxplus, xrootd is supported to avoid downloading the inputFile. To initialize the grid access and source the needed python packages follow
```
voms-proxy-init --rfc --voms cms -valid 192:00
source /cvmfs/sft.cern.ch/lcg/views/LCG_103/x86_64-centos7-gcc11-opt/setup.sh
python3 run_bbWW_processing.py -i root://cmsxrootd.fnal.gov//path/to/dataset/file.root -o Output_File -t DNN_Truth_Value(see run_bbWW_processing.py) -d debug
```
To use through docker, first prepare the image named run3_bbww
```
docker build -t run3_bbww .
```

Then to run, prepare the input file (default input_files/run2022C_data_doublemuon_nanoaod.root), and then
```
./run_docker.sh
```
To use through condor, look at the README in the condor directory

To make data/MC plots:
- define variable to plot, binning, axis title etc at end of 'Plots_stack.py' file(which will be feeded to 'make_plot' function ) and run simply by 'python3 Plots_stack.py'


All major pieces of the analysis are handled by separate files, managed by the bbWWProcessor.py class

Steps are:
- Object Selection
- Event Selection
- Tree Creation
