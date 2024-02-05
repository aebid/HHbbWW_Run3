#!/bin/bash

hadd -O DoubleLepton_UL_2016.root ../{DoubleMuon,SingleMuon,Muon,EGamma,MuonEG}/*/*.root
#hadd -O DoubleLepton_UL_2016.root ../{DoubleMuon,DoubleEG,SingleMuon,SingleElectron,EGamma,MuonEG}/*/*.root #2022 Data doesn't have these
hadd -O SingleLepton_UL_2016.root ../{SingleMuon,Muon,EGamma}/*/*.root
