# HHbbWW_Run3

Package for TAMU analysis of H -> hh -> bbWW

Instructions to use
```
cd python
python3 run_bbWW_processing.py
```
Any changes for input files must be done inside the run_bbWW_processing.py file

All major pieces of the analysis are handled by separate files, managed by the bbWWProcessor.py class

Steps are:
- Object Selection
- Event Selection
- Tree Creation
