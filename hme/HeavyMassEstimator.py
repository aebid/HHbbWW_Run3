import uproot
import numpy as np
import awkward as ak


### Awkward implementation of HME ###
### https://github.com/tahuang1991/HeavyMassEstimator/tree/master ###


f = uproot.open("GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M450_Run3Sync.root")
t = f['Double_Tree']
events = t.arrays())


iterations = 100

events['eta_gen'] = np.random.uniform(-6,6)
