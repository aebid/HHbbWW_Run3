import awkward as ak
import numpy as np
import uproot
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
from scipy.stats import norm


fname_list = ['out_condor_GluGluToRadionToHHTo2B2VTo2L2Nu_M-260_narrow_13TeV-madgraph-v2.root', 'out_condor_GluGluToRadionToHHTo2B2Tau_M-260_narrow_13TeV-madgraph.root', 'out_condor_GluGluToRadionToHHTo2B2WToLNu2J_M-260_narrow_13TeV-madgraph.root']
s_events_list = []
d_events_list = []
nTotalEvents_list = []
for fname in fname_list:
    uproot_file = uproot.open(fname)
    single_tree = uproot_file['Single_Tree']
    double_tree = uproot_file['Double_Tree']
    nEvents_tree = uproot_file['nEvents']
    s_events = single_tree.arrays()
    d_events = double_tree.arrays()
    n_events = nEvents_tree.arrays()

    nSingleSignal = ak.num(s_events[s_events.Single_Signal == 1], axis=0)
    nDoubleSignal = ak.num(d_events[(d_events.Double_Signal == 1) & (d_events.Zveto == 1) & (d_events.nBjets_pass == 1)], axis=0)
    nTotalEvents = ak.sum(n_events.nEvents)

    print("For file ", fname, " we have acceptances ")
    print("Single = ", nSingleSignal/nTotalEvents)
    print("Double = ", nDoubleSignal/nTotalEvents)
    print("Total events in sample ", nTotalEvents)

    s_events_list.append(ak.num(s_events[s_events.Single_Signal == 1], axis=0))
    d_events_list.append(ak.num(d_events[(d_events.Double_Signal == 1) & (d_events.Zveto == 1) & (d_events.nBjets_pass == 1)], axis=0))
    nTotalEvents_list.append(ak.sum(n_events.nEvents))



print("For files ", fname_list, " we have acceptances ")
print("Single = ", ak.sum(s_events_list)/ak.sum(nTotalEvents_list))
print("Double = ", ak.sum(d_events_list)/ak.sum(nTotalEvents_list))
print("Total events in sample ", ak.sum(nTotalEvents_list))
