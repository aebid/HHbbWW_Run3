### in  nanoAOD_processing.py

from bbWWProcessor import EventProcess
import awkward as ak
import os

import time
startTime = time.time()

index = 0
fname_list = ["run2022C_data_doublemuon_nanoaod.root"]
fname = fname_list[index]

#Prepare for DNN training, give truth values
dnn_truth_value = 8
#value list example HH:0 TTbar:1 ST:2 DY:3 H:4 TTbarV(X):5 VV(V):6 Other:7 Data:8

outname = "out_"+fname
debug = 1

Runyear = 2022
isMC = False

print("Processing: ", fname)
print("Will save as: ", outname)

fname = "../input_files/"+fname
if not os.path.isdir("../output"):
    os.makedirs("../output")
outname = "../output/"+outname

eventProcess = EventProcess(fname, isMC, Runyear, dnn_truth_value, debug)


eventProcess.all_obj_selection()
print('Object Selection in seconds: ' + str((time.time() - startTime)))
if debug: eventProcess.print_object_selection()
eventProcess.single_lepton_category()
eventProcess.double_lepton_category()
print('Categories in seconds: ' + str((time.time() - startTime)))


eventProcess.create_df(outname)

print('Saved in seconds: ' + str((time.time() - startTime)))
print('Filename = ', outname)

"""
if isMC:
    eventProcess.ak4_jet_corrector()
    eventProcess.ak8_jet_corrector()
    #print("Sub jet will always use data-methods!")
    #eventProcess.sub_jet_corrector()
    eventProcess.met_corrector()
    #print('Jet Corrections in seconds: ' + str((time.time() - startTime)))


eventProcess.create_df(outname)

print('Saved in seconds: ' + str((time.time() - startTime)))
print('Filename = ', outname)
"""
