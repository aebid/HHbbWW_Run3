import os
import ROOT
import array
import glob

plotdir = "abcd_plots_MCMatchLeps/"
if not os.path.exists(plotdir):
    os.mkdir(plotdir)

#filesdir = "/eos/user/d/daebi/2016_data_28Nov23_usexroot0/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8_ext2-v1/"
#fnamelist = [filesdir+fname for fname in os.listdir(filesdir) if "root" in fname]

filesdir = "/eos/user/d/daebi/2016_data_28Nov23_usexroot0/DY*/*/*"
fnamelist = [fname for fname in glob.glob(filesdir) if fname[-4:] == "root"]
print(fnamelist)

fnamelist = ["/eos/user/d/daebi/Full_DY/DY_Full.root"]
#fnamelist = ["../input_files/2016_files/DY_File1.root", "../input_files/2016_files/DY_File2.root"]

files_dict = {} #Events must be saved as a dict or else the data is thrown away
trees_dict = {}
for fname in fnamelist:
    files_dict[fname] = ROOT.TFile(fname)
    trees_dict[fname] = files_dict[fname].Get("Double_Tree")

base_cut = "(Double_Signal == 1) && (lep0_MC_Match == 1) && (lep1_MC_Match == 1)"
#base_cut = "(Double_Signal == 1)"
ZVeto = "(Zveto == 1)"
ZPeak = "(Zveto == 0)"
nBJet0 = "(n_medium_btag_ak4_jets == 0)"
nBJet1 = "(n_medium_btag_ak4_jets == 1)"
nBJet2 = "(n_medium_btag_ak4_jets == 2)"



varlist = []
varlist.append({"varname": "HT", "bins": 20, "binlow": 0.0, "binhigh": 1000.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "lep0_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "lep0_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "lep1_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "lep1_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "ak4_jet0_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "ak4_jet0_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "ak4_jet1_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})
varlist.append({"varname": "ak4_jet1_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0, "weight1": ROOT.TH1D(), "weight2": ROOT.TH1D()})

hA = [ROOT.TH1D()]
hB1 = [ROOT.TH1D()]
hB2 = [ROOT.TH1D()]
hC = [ROOT.TH1D()]
hD1 = [ROOT.TH1D()]
hD2 = [ROOT.TH1D()]

hWeight1 = [ROOT.TH1D()]
hWeight2 = [ROOT.TH1D()]

for vardict in varlist:
    varname = vardict["varname"]
    bins = vardict["bins"]
    binlow = vardict["binlow"]
    binhigh = vardict["binhigh"]

    print("Looking at var "+varname)

    #Initialize all histograms

    #A is ZPeak and nBJet0
    hA_name = "ZPeakZeroB_"+varname
    hA_cut = ZPeak + " && " + nBJet0 + " && " + base_cut
    hA[0] = ROOT.TH1D(hA_name, hA_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hA_name, hA_cut, "goff")
    #B1 is ZPeak and nBJet1
    hB1_name = "ZPeakOneB_"+varname
    hB1_cut = ZPeak + " && " + nBJet1 + " && " + base_cut
    hB1[0] = ROOT.TH1D(hB1_name, hB1_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hB1_name, hB1_cut, "goff")
    #B2 is ZPeak and nBJet2
    hB2_name = "ZPeakTwoB_"+varname
    hB2_cut = ZPeak + " && " + nBJet2 + " && " + base_cut
    hB2[0] = ROOT.TH1D(hB2_name, hB2_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hB2_name, hB2_cut, "goff")
    #C is ZVeto and nBJet0
    hC_name = "ZVetoZeroB_"+varname
    hC_cut = ZVeto + " && " + nBJet0 + " && " + base_cut
    hC[0] = ROOT.TH1D(hC_name, hC_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hC_name, hC_cut, "goff")
    #D1 is ZVeto and nBJet1
    hD1_name = "ZVetoOneB_"+varname
    hD1_cut = ZVeto + " && " + nBJet1 + " && " + base_cut
    hD1[0] = ROOT.TH1D(hD1_name, hD1_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hD1_name, hD1_cut, "goff")
    #D2 is ZVeto and nBJet2
    hD2_name = "ZVetoTwoB_"+varname
    hD2_cut = ZVeto + " && " + nBJet2 + " && " + base_cut
    hD2[0] = ROOT.TH1D(hD2_name, hD2_name, bins, binlow, binhigh)
    #events.Draw(varname+" >> "+hD2_name, hD2_cut, "goff")


    for fname in fnamelist:
        print("Looking at ", fname)
        #files_dict[fname] = ROOT.TFile(fname)
        #trees_dict[fname] = files_dict[fname].Get("Double_Tree")

        h_tmp = ROOT.TH1D("h_tmp", "h_tmp", bins, binlow, binhigh)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hA_cut, "goff")
        hA[0].Add(h_tmp)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hB1_cut, "goff")
        hB1[0].Add(h_tmp)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hB2_cut, "goff")
        hB2[0].Add(h_tmp)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hC_cut, "goff")
        hC[0].Add(h_tmp)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hD1_cut, "goff")
        hD1[0].Add(h_tmp)
        trees_dict[fname].Draw(varname+" >> "+"h_tmp", hD2_cut, "goff")
        hD2[0].Add(h_tmp)




    vardict["weight1"] = hB1[0].Clone()
    vardict["weight1"].SetName("OneBWeight_"+varname)
    vardict["weight1"].Divide(hA[0])

    vardict["weight2"] = hB2[0].Clone()
    vardict["weight2"].SetName("TwoBWeight_"+varname)
    vardict["weight2"].Divide(hA[0])

    hD1_Estimation = vardict["weight1"]*hC[0]
    hD1_Estimation.SetName("OneBEstimation_"+varname)

    hD2_Estimation = vardict["weight2"]*hC[0]
    hD2_Estimation.SetName("TwoBEstimation_"+varname)


    print("Finished all files for var "+varname+", simple getEntries")
    print("A = ", hA[0].GetEntries())
    print("B1 = ", hB1[0].GetEntries())
    print("B2 = ", hB2[0].GetEntries())
    print("C = ", hC[0].GetEntries())
    print("D1 = ", hD1[0].GetEntries())
    print("D2 = ", hD2[0].GetEntries())


    for hist in [hA[0], hB1[0], hB2[0], hC[0], hD1[0], hD2[0], vardict["weight1"], vardict["weight2"], hD1_Estimation, hD2_Estimation]:
        c1 = ROOT.TCanvas("c1", "c1", 800, 800)
        c1.SetLogy()
        hist.Draw("hist")
        c1.SaveAs(plotdir+hist.GetName()+".pdf")

    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLogy()
    hD1[0].Draw("hist")
    hD1_Estimation.Draw("hist same")
    hD1_Estimation.SetLineColor(ROOT.kRed)
    c1.SaveAs(plotdir+"oneB_compare_"+varname+".pdf")

    c1 = ROOT.TCanvas("c1", "c1", 800, 800)
    c1.SetLogy()
    hD2[0].Draw("hist")
    hD2_Estimation.Draw("hist same")
    hD2_Estimation.SetLineColor(ROOT.kRed)
    c1.SaveAs(plotdir+"twoB_compare_"+varname+".pdf")




#Must get new event weights, using the variable and Weights hist as a LUT
for fname in fnamelist:
    new_filename = plotdir+"DY_withWeights.root"
    print("Creating new file ", new_filename)
    events = trees_dict[fname]
    newfile = ROOT.TFile(new_filename, "recreate")
    new_tree = events.CloneTree(0)
    ABCD_Weight1_dict = {}
    ABCD_Weight2_dict = {}
    for vardict in varlist:
        varname = vardict["varname"]
        ABCD_Weight1_dict[varname] = array.array('d', [0])
        ABCD_Weight2_dict[varname] = array.array('d', [0])
        new_tree.Branch('DY_Estimation_Weight1_'+varname, ABCD_Weight1_dict[varname], 'DY_Estimation_Weight1_'+varname+'/D')
        new_tree.Branch('DY_Estimation_Weight2_'+varname, ABCD_Weight2_dict[varname], 'DY_Estimation_Weight2_'+varname+'/D')

    #ABCD_Weight_val = array.array('d', [0])
    #new_tree.Branch('DY_Estimation_Weights_'+varname, ABCD_Weight_val, 'DY_Estimation_Weights_'+varname+'/D')
    for evt in events:
        for vardict in varlist:
            varname = vardict["varname"]
            hWeight1 = vardict["weight1"]
            hWeight2 = vardict["weight2"]
            ABCD_Weight1_val = ABCD_Weight1_dict[varname]
            ABCD_Weight2_val = ABCD_Weight2_dict[varname]
            val = getattr(evt, varname)
            weight1_bin = hWeight1.FindBin(val)
            weight2_bin = hWeight2.FindBin(val)
            ABCD_Weight1_val[0] = hWeight1.GetBinContent(weight1_bin)
            ABCD_Weight2_val[0] = hWeight2.GetBinContent(weight2_bin)



        #HT = evt.HT
        #weight1_bin = hWeight1.FindBin(HT)
        #ABCD_Weight_val[0] = hWeight1.GetBinContent(weight1_bin)
        #print("HT is ", HT, " Bin is ", weight1_bin, " Val is ", ABCD_Weight_val[0])
        new_tree.Fill()
    print("New file has entries ", new_tree.GetEntries())
    new_tree.AutoSave()
