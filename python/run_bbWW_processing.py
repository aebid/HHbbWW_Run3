### in  nanoAOD_processing.py

from bbWWProcessor import EventProcess
import awkward as ak
import os
import uproot
import psutil
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema


import time
startTime = time.time()

import argparse

parser = argparse.ArgumentParser(description='Run3 analysis for H->hh->bbWW')
parser.add_argument("-i", "--inputFileList", dest="infile_list", type=str, nargs='+', default=[], help="input file name. [Default: [] ]")
parser.add_argument("-o", "--outputFile", dest="outfile", type=str, default="out.root", help="output file name. [Default: 'out.root']")
parser.add_argument("-ry", "--runyear", dest="Runyear", type=int, default=2022, help="Runyear of the file. [Default: 2022]")
parser.add_argument("-re", "--runera", dest="runera", type=str, default="A", help="RunA, B, C, etc. For Run3 2022 jetmet corrections. [Default: 'A']")
parser.add_argument("-MC", dest="isMC", type=int, default=0, help="Is the file MC. [Default: 0]")
parser.add_argument("-t", "--truth", dest="dnn_truth_value", type=int, default="8", help="DNN Truth value, HH:0 TTbar:1 ST:2 DY:3 H:4 TTbarV(X):5 VV(V):6 Other:7 Data:8. [Default: 8 (Data)]")
parser.add_argument("-d", "--debug", dest="debug", type=int, default="0", help="Debug. [Default: 0 (False)]")
parser.add_argument("-XS", dest="XS", type=float, default=1.0, help="Cross Section. [Default: 1.0]")
parser.add_argument("-SF", dest="SF", type=int, default=0, help="Add Scale Factors. [Default: 0 (False)]")
parser.add_argument("-HLTCut", dest="HLTCut", type=int, default=1, help="Filter out MC events that do not pass HLT. [Default: 1 (True)]")
parser.add_argument("-nEvts", dest="nEventsLoopSize", type=int, default=500000, help="Number of events to loop over to save RAM. [Default: 500,000]")
args, unknown = parser.parse_known_args()

flist = args.infile_list
outname = args.outfile
outfile = uproot.recreate(outname)

args = parser.parse_args()

if len(flist) == 0:
    raise Exception("No input files, use python3 run_bbWW_processing.py -i InputFileList -o OutputFile")

#index = 0
#fname_list = ["run2022C_data_doublemuon_nanoaod.root"]
#fname = fname_list[index]

#Prepare for DNN training, give truth values
#dnn_truth_value = 8
dnn_truth_value = args.dnn_truth_value
#value list example HH:0 TTbar:1 ST:2 DY:3 H:4 TTbarV(X):5 VV(V):6 Other:7 Data:8

debug = args.debug

Runyear = args.Runyear
runera = args.runera
isMC = args.isMC
XS = args.XS
doSF = args.SF
HLT_Cuts = args.HLTCut
nEventsLoopSize = args.nEventsLoopSize

print("Processing: ", flist)
print("Will save as: ", outname)
print("Args are = ", args)
print("Memory usage in MB is ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))


for fname in flist:
    print("Starting file: ", fname)
    #nEventsLoopSize = 250000
    #Check how many events are in the file
    uproot_file = uproot.open(fname)
    events = NanoEventsFactory.from_root(uproot_file, schemaclass=NanoAODSchema.v7).events()
    nEvents = len(events)
    if nEvents == 0:
        print("Zero events! This will fail ):")
        continue
    print("There are ", nEvents, " total events")
    #Now lets loop only over the loop size (Save RAM!)
    for nLoopIter in range(int(nEvents/nEventsLoopSize)+1):
        print("At loop iter ", nLoopIter)
        entryStart = nEventsLoopSize*(nLoopIter)
        entryStop = nEventsLoopSize*(nLoopIter+1)

        #Only load the events in range
        eventProcess = EventProcess(fname, entryStart, entryStop, isMC, doSF, Runyear, runera, dnn_truth_value, XS, debug, HLT_Cuts)
        if eventProcess.skip_file: continue
        eventProcess.make_evaluator()

        #For now we hardcode 2022 jetmet corrections
        if Runyear == 2022:
            print("Doing 2022 jetmet corrections!!! Maybe turn this off")
            eventProcess.jetmet_json_corrector()
            if isMC:
                #Scale Factors are only for MC
                print("Doing 2022 btag SF!!!")
                eventProcess.btag_json_SF()
                print("Doing 2022 pu reweight!!!")
                eventProcess.pu_reweight_json()
            if dnn_truth_value == 1:
                #TTBar sample, do TTBar reweights
                print("Doing 2022 top pt reweight!!!")
                eventProcess.top_pt_reweight()

        if doSF:
            #Jet Corrections are for both MC and Data
            eventProcess.jet_met_corrector()
            print("JetMET Corrector in seconds: " + str((time.time() - startTime)))
            #Scale Factors are only for MC
            if isMC:
                eventProcess.add_scale_factors()
                print("Scale Factors in seconds: " + str((time.time() - startTime)))
                print("Memory usage in MB after SF ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))
            #Lepton Fakerates are only for Data ? Maybe?
            eventProcess.do_lepton_fakerate()
            print("Fake Rate addition in seconds: " + str((time.time() - startTime)))
            print("Memory usage in MB after FR ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))

            if dnn_truth_value == 1:
                #TTBar sample, do TTBar reweights
                eventProcess.top_pt_reweight()
                print("TTBar reweight done")

        if isMC:
            eventProcess.match_genparts()
            print('GenParts in seconds: ' + str((time.time() - startTime)))
            print("Memory usage in MB after GenMatch ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))


        eventProcess.all_obj_selection()
        print('Object Selection in seconds: ' + str((time.time() - startTime)))
        print("Memory usage in MB after Object ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))

        if debug: eventProcess.print_object_selection()

        eventProcess.single_lepton_category()
        eventProcess.double_lepton_category()
        print('Categories in seconds: ' + str((time.time() - startTime)))
        print("Memory usage in MB after Event ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))

        if isMC and doSF:
            eventProcess.add_event_weight()
            print('Added weights in seconds: ' + str((time.time() - startTime)))
            print("Memory usage in MB after Event ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))

        if debug: eventProcess.print_event_selection()

        eventProcess.add_high_level_variables()

        eventProcess.update_outfile(outfile)

        print('Updated in seconds: ' + str((time.time() - startTime)))
        print("Memory usage in MB after Tree ", psutil.Process(os.getpid()).memory_info()[0] / float(2 ** 20))
        print('Filename = ', outname)

    print("Finished processing all events!")

print("Finished processing all files!")
