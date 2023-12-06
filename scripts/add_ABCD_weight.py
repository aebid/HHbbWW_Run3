import awkward as ak
import numpy as np
import uproot
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
from scipy.stats import norm
import ROOT
import array


fnamelist = ["../input_files/2016_files/DY_File1.root", "../input_files/2016_files/DY_File2.root"]


base_cut = "(Double_Signal == 1)"
ZVeto = "(Zveto == 1)"
ZPeak = "(Zveto == 0)"
nBJet0 = "(n_medium_btag_ak4_jets == 0)"
nBJet1 = "(n_medium_btag_ak4_jets == 1)"
nBJet2 = "(n_medium_btag_ak4_jets == 2)"


varname = "HT"
bins = 20
binlow = 0.0
binhigh = 1000.0


#Initialize all histograms

#A is ZPeak and nBJet0
hA_name = "ZPeakZeroB"
hA_cut = ZPeak + " && " + nBJet0 + " && " + base_cut
hA = ROOT.TH1D(hA_name, hA_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hA_name, hA_cut, "goff")
#B1 is ZPeak and nBJet1
hB1_name = "ZPeakOneB"
hB1_cut = ZPeak + " && " + nBJet1 + " && " + base_cut
hB1 = ROOT.TH1D(hB1_name, hB1_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hB1_name, hB1_cut, "goff")
#B2 is ZPeak and nBJet2
hB2_name = "ZPeakTwoB"
hB2_cut = ZPeak + " && " + nBJet2 + " && " + base_cut
hB2 = ROOT.TH1D(hB2_name, hB2_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hB2_name, hB2_cut, "goff")
#C is ZVeto and nBJet0
hC_name = "ZVetoZeroB"
hC_cut = ZVeto + " && " + nBJet0 + " && " + base_cut
hC = ROOT.TH1D(hC_name, hC_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hC_name, hC_cut, "goff")
#D1 is ZVeto and nBJet1
hD1_name = "ZVetoOneB"
hD1_cut = ZVeto + " && " + nBJet1 + " && " + base_cut
hD1 = ROOT.TH1D(hD1_name, hD1_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hD1_name, hD1_cut, "goff")
#D2 is ZVeto and nBJet2
hD2_name = "ZVetoTwoB"
hD2_cut = ZVeto + " && " + nBJet2 + " && " + base_cut
hD2 = ROOT.TH1D(hD2_name, hD2_name, bins, binlow, binhigh)
#events.Draw(varname+" >> "+hD2_name, hD2_cut, "goff")



#Fill the histograms
files_dict = {} #Events must be saved as a dict or else the data is thrown away
trees_dict = {}
for fname in fnamelist:
    print("Looking at ", fname)
    files_dict[fname] = ROOT.TFile(fname)
    trees_dict[fname] = files_dict[fname].Get("Double_Tree")

    h_tmp = ROOT.TH1D("h_tmp", "h_tmp", bins, binlow, binhigh)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hA_cut, "goff")
    hA.Add(h_tmp)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hB1_cut, "goff")
    hB1.Add(h_tmp)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hB2_cut, "goff")
    hB2.Add(h_tmp)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hC_cut, "goff")
    hC.Add(h_tmp)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hD1_cut, "goff")
    hD1.Add(h_tmp)
    trees_dict[fname].Draw(varname+" >> "+"h_tmp", hD2_cut, "goff")
    hD2.Add(h_tmp)




hWeight1 = hB1.Clone()
hWeight1.SetName("OneBWeight")
hWeight1.Divide(hA)

hWeight2 = hB2.Clone()
hWeight2.SetName("TwoBWeight")
hWeight2.Divide(hA)

hD1_Estimation = hWeight1*hC
hD1_Estimation.SetName("OneBEstimation")

hD2_Estimation = hWeight2*hC
hD2_Estimation.SetName("TwoBEstimation")


for hist in [hA, hB1, hB2, hC, hD1, hD2, hWeight1, hWeight2, hD1_Estimation, hD2_Estimation]:
    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    hist.Draw("hist")
    c1.SaveAs(hist.GetName()+".pdf")

c1 = ROOT.TCanvas("c1", "c1", 800, 800)
hD1.Draw("hist")
hD1_Estimation.Draw("hist same")
hD1_Estimation.SetLineColor(ROOT.kRed)
c1.SaveAs("oneB_compare.pdf")

c1 = ROOT.TCanvas("c1", "c1", 800, 800)
hD2.Draw("hist")
hD2_Estimation.Draw("hist same")
hD2_Estimation.SetLineColor(ROOT.kRed)
c1.SaveAs("twoB_compare.pdf")


#Must get new event weights, using the variable and Weights hist as a LUT
for fname in fnamelist:
    new_filename = fname[:-5]+"_wightWeight.root"
    print("Creating new file ", new_filename)
    events = trees_dict[fname]
    newfile = ROOT.TFile(new_filename, "recreate")
    new_tree = events.CloneTree(0)
    ABCD_Weight_val = array.array('d', [0])
    new_tree.Branch('DY_Estimation_Weights_'+varname, ABCD_Weight_val, 'DY_Estimation_Weights_'+varname+'/D')
    for evt in events:
        HT = evt.HT
        weight1_bin = hWeight1.FindBin(HT)
        ABCD_Weight_val[0] = hWeight1.GetBinContent(weight1_bin)
        #print("HT is ", HT, " Bin is ", weight1_bin, " Val is ", ABCD_Weight_val[0])
        new_tree.Fill()
