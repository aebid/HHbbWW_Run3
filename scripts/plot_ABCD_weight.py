import ROOT
import os

def plot1Dhist(name, title, event, size, xlabel, ylabel, cut, plotdir, save, logy):
  if os.path.exists("plots/"+plotdir) == False:
    os.mkdir("plots/"+plotdir)
  c1 = ROOT.TCanvas("", "", 800, 600)
  hist = ROOT.TH1D(name, title, size[0], size[1], size[2])
  hist.GetXaxis().SetTitle(xlabel)
  hist.GetYaxis().SetTitle(ylabel)
  hist.Sumw2()
  event.Project(name, name, cut)
  hist.Draw("Hist")
  if logy:
    c1.SetLogy()
  if save:
    c1.SaveAs("plots/"+plotdir+"/"+title+".png")
  return hist


def plot2Dhist(name, title, event, size, xlabel, ylabel, cut, plotdir, save):
  if os.path.exists("plots/"+plotdir) == False:
    os.mkdir("plots/"+plotdir)
  c1 = ROOT.TCanvas("", "", 800, 800)
  hist = ROOT.TH2D(name, title, size[0], size[1], size[2], size[3], size[4], size[5])
  hist.GetXaxis().SetTitle(xlabel)
  hist.GetYaxis().SetTitle(ylabel)
  hist.Sumw2()
  event.Project(name, name, cut)
  hist.Draw("colz")
  if save:
    c1.SaveAs("plots/"+plotdir+"/"+title+".png")
  return hist


def plotDYEstComparison(name, weight, nJets, title, event, size, xlabel, ylabel, cut, plotdir, save, logy):
    if os.path.exists("plots/"+plotdir) == False:
        os.mkdir("plots/"+plotdir)
    c1 = ROOT.TCanvas("", "", 800, 600)
    hist_signal = ROOT.TH1D("signal", "signal", size[0], size[1], size[2])
    hist_est = ROOT.TH1D("est", "est", size[0], size[1], size[2])
    hist_signal.Sumw2()
    hist_est.Sumw2()

    hist_est.GetXaxis().SetTitle(xlabel)
    hist_est.GetYaxis().SetTitle(ylabel)

    base_cut = "(Double_Signal == 1) && (lep0_MC_Match == 1) && (lep1_MC_Match == 1)"
    #base_cut = "(Double_Signal == 1)"

    event.Project("signal", name, "({base_cut} && (n_medium_btag_ak4_jets == {nJets}) && (Zveto == 1))".format(base_cut = base_cut, nJets = nJets))
    event.Project("est", name, "({base_cut} && (n_medium_btag_ak4_jets == 0) && (Zveto == 1))*{weight}".format(base_cut = base_cut, weight = weight))
    #hist_signal.Draw("hist")
    #hist_est.Draw("same hist")
    hist_est.SetLineColor(ROOT.kRed)
    hist_est.SetMaximum(100.0*max(hist_signal.GetMaximum(), hist_est.GetMaximum()))
    hist_est.SetMinimum(0.001)
    hist_est.SetTitle("DY Estimation var "+name+" weight "+weight)
    if logy:
        c1.SetLogy()


    ratioplot = ROOT.TRatioPlot(hist_est, hist_signal)
    ratioplot.Draw()
    ratioplot.GetLowerRefYaxis().SetRangeUser(-0.5, 2.5)


    if save:
        c1.SaveAs("plots/"+plotdir+"/"+title+".png")
    return hist_signal, hist_est



#f = ROOT.TFile("abcd_plots/DY_withWeights.root")
f = ROOT.TFile("abcd_plots_MCMatchLeps/DY_withWeights.root")
event = f.Get("Double_Tree")

if os.path.exists("plots") == False:
    os.mkdir("plots/")


plot2Dhist("DY_Estimation_Weight1_HT:HT", "DY HT Weight1", event, [20, 0.0, 1000.0, 100, 0.0, 1.0], "HT", "DY HT Weight1", "", "weight", True)
plot2Dhist("DY_Estimation_Weight2_HT:HT", "DY HT Weight2", event, [20, 0.0, 1000.0, 100, 0.0, 1.0], "HT", "DY HT Weight2", "", "weight", True)

#plot1Dhist("DY_Estimation_Weight1_lep0_pt", "DY lep0 pT Weight1", event, [200, 0, 3], "lep0 p_T", "DY lep0 pT Weight1", "", "weight", True, False)
#plot1Dhist("DY_Estimation_Weight2_lep0_pt", "DY lep0 pT Weight2", event, [200, 0, 3], "lep0 p_T", "DY lep0 pT Weight2", "", "weight", True, False)

plotDYEstComparison("HT", "DY_Estimation_Weight1_HT", "1", "DYComparisonHTWeight1Plot", event, [20, 0, 1000], "HT", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("HT", "DY_Estimation_Weight2_HT", "2", "DYComparisonHTWeight2Plot", event, [20, 0, 1000], "HT", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("lep0_pt", "DY_Estimation_Weight1_lep0_pt", "1", "DYComparisonLep0PtWeight1Plot", event, [20, 0, 1000], "lep0_pt", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("lep0_pt", "DY_Estimation_Weight2_lep0_pt", "2", "DYComparisonLep0PtWeight2Plot", event, [20, 0, 1000], "lep0_pt", "Entries", "", "DY_Est_Comp", True, True)




varlist = []
varlist.append({"varname": "HT", "bins": 20, "binlow": 0.0, "binhigh": 1000.0})
varlist.append({"varname": "lep0_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0})
varlist.append({"varname": "lep0_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0})
varlist.append({"varname": "lep1_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0})
varlist.append({"varname": "lep1_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0})
varlist.append({"varname": "ak4_jet0_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0})
varlist.append({"varname": "ak4_jet0_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0})
varlist.append({"varname": "ak4_jet1_pt", "bins": 20, "binlow": 0.0, "binhigh": 500.0})
varlist.append({"varname": "ak4_jet1_eta", "bins": 20, "binlow": -3.0, "binhigh": 3.0})


for vardict in varlist:
    varname = vardict["varname"]
    bins = vardict["bins"]
    binlow = vardict["binlow"]
    binhigh = vardict["binhigh"]

    plot2Dhist("DY_Estimation_Weight1_"+varname+":"+varname, "DY "+varname+" Weight1", event, [bins, binlow, binhigh, 100, 0.0, 1.0], varname, "DY "+varname+" Weight1", "", "weight", True)
    plot2Dhist("DY_Estimation_Weight2_"+varname+":"+varname, "DY "+varname+" Weight2", event, [bins, binlow, binhigh, 100, 0.0, 1.0], varname, "DY "+varname+" Weight2", "", "weight", True)

    plotDYEstComparison(varname, "DY_Estimation_Weight1_"+varname, "1", "DYComparison"+varname+"Weight1Plot", event, [bins, binlow, binhigh], varname, "Entries", "", "DY_Est_Comp", True, True)
    plotDYEstComparison(varname, "DY_Estimation_Weight2_"+varname, "2", "DYComparison"+varname+"Weight2Plot", event, [bins, binlow, binhigh], varname, "Entries", "", "DY_Est_Comp", True, True)


"""
 DY_Estimation_Weight1_HT = 0.133214
 DY_Estimation_Weight2_HT = 0.0197224
 DY_Estimation_Weight1_lep0_pt = 0.135841
 DY_Estimation_Weight2_lep0_pt = 0.0218758
 DY_Estimation_Weight1_lep0_eta = 0.13099
 DY_Estimation_Weight2_lep0_eta = 0.020972
 DY_Estimation_Weight1_lep1_pt = 0.134839
 DY_Estimation_Weight2_lep1_pt = 0.0229862
 DY_Estimation_Weight1_lep1_eta = 0.120843
 DY_Estimation_Weight2_lep1_eta = 0.0179368
 DY_Estimation_Weight1_ak4_jet0_pt = 0.13853
 DY_Estimation_Weight2_ak4_jet0_pt = 0.0239998
 DY_Estimation_Weight1_ak4_jet0_eta = 0.166733
 DY_Estimation_Weight2_ak4_jet0_eta = 0.0300481
 DY_Estimation_Weight1_ak4_jet1_pt = 0.127757
 DY_Estimation_Weight2_ak4_jet1_pt = 0.0227427
 DY_Estimation_Weight1_ak4_jet1_eta = 0.127678
 DY_Estimation_Weight2_ak4_jet1_eta = 0.0230655
"""
