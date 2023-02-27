# HHbbWW_Run3

Package for TAMU analysis of H -> hh -> bbWW

Instructions to use directly
```
cd python
python3 run_bbWW_processing.py -i Input_File -o Output_File
```
To use through docker, prepare the image named run3_bbww and then
```
./run_docker.sh
```

All major pieces of the analysis are handled by separate files, managed by the bbWWProcessor.py class

Steps are:
- Object Selection
- Event Selection
- Tree Creation
