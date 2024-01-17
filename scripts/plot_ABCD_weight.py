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


def plotDYEstComparison(name, weight, nJets, title, event, size, xlabel, ylabel, cut, plotdir, save, logy):
    if os.path.exists("plots/"+plotdir) == False:
        os.mkdir("plots/"+plotdir)
    c1 = ROOT.TCanvas("", "", 800, 600)
    hist_signal = ROOT.TH1D("signal", "signal", size[0], size[1], size[2])
    hist_est = ROOT.TH1D("est", "est", size[0], size[1], size[2])
    hist_signal.Sumw2()
    hist_est.Sumw2()

    event.Project("signal", name, "(Double_Signal && (n_medium_btag_ak4_jets == {nJets}) && (Zveto == 1))".format(nJets = nJets))
    event.Project("est", name, "(Double_Signal && (n_medium_btag_ak4_jets == 0) && (Zveto == 0))*{weight}".format(weight = weight))
    hist_signal.Draw("hist")
    hist_est.Draw("same hist")
    hist_est.SetLineColor(ROOT.kRed)
    hist_signal.SetMaximum(2*max(hist_signal.GetMaximum(), hist_est.GetMaximum()))
    hist_signal.SetTitle("DY Estimation var "+name+" weight "+weight)
    if logy:
        c1.SetLogy()
    if save:
        c1.SaveAs("plots/"+plotdir+"/"+title+"1.png")
    return hist_signal, hist_est



f = ROOT.TFile("abcd_plots/DY_withWeights.root")
event = f.Get("Double_Tree")

if os.path.exists("plots") == False:
    os.mkdir("plots/")

plot1Dhist("DY_Estimation_Weight1_HT", "DY HT Weight1", event, [200, 0, 3], "HT", "DY HT Weight1", "", "weight", True, False)
plot1Dhist("DY_Estimation_Weight2_HT", "DY HT Weight2", event, [200, 0, 3], "HT", "DY HT Weight2", "", "weight", True, False)

plot1Dhist("DY_Estimation_Weight1_lep0_pt", "DY lep0 pT Weight1", event, [200, 0, 3], "lep0 p_T", "DY lep0 pT Weight1", "", "weight", True, False)
plot1Dhist("DY_Estimation_Weight2_lep0_pt", "DY lep0 pT Weight2", event, [200, 0, 3], "lep0 p_T", "DY lep0 pT Weight2", "", "weight", True, False)

plotDYEstComparison("HT", "DY_Estimation_Weight1_HT", "1", "DYComparisonHTWeight1Plot", event, [20, 0, 1000], "HT", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("HT", "DY_Estimation_Weight2_HT", "2", "DYComparisonHTWeight2Plot", event, [20, 0, 1000], "HT", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("lep0_pt", "DY_Estimation_Weight1_lep0_pt", "1", "DYComparisonLep0PtWeight1Plot", event, [20, 0, 1000], "lep0_pt", "Entries", "", "DY_Est_Comp", True, True)
plotDYEstComparison("lep0_pt", "DY_Estimation_Weight2_lep0_pt", "2", "DYComparisonLep0PtWeight2Plot", event, [20, 0, 1000], "lep0_pt", "Entries", "", "DY_Est_Comp", True, True)


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
