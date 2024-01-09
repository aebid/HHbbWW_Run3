import ROOT

fname_ttbar = "/eos/user/d/daebi/2016_data_8Jan24_allData_ttBarSignalOnly/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/TTTo2L2Nu_allData_8Jan24.root"
fname_signal = "/eos/user/d/daebi/2016_data_8Jan24_allData_ttBarSignalOnly/GluGluToRadionToHHTo2B2VTo2L2Nu_M-400_narrow_13TeV-madgraph-v2/RunIISummer16NanoAODv7-PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8-v1/out_condor_job0.sh.root"

f_ttbar = ROOT.TFile(fname_ttbar)
t_ttbar = f_ttbar.Get("Double_Tree")

f_signal = ROOT.TFile(fname_signal)
t_signal = f_signal.Get("Double_Tree")


c1 = ROOT.TCanvas("", "", 800, 600)
eff = ROOT.TEfficiency("h","Percent of Events after individual Cuts",10,0,10)
htot = ROOT.TH1D("htot", "Total Events", 10, 0, 10)
htot.Sumw2()
hpass = ROOT.TH1D("hpass", "Passed Events", 10, 0, 10)
hpass.Sumw2()


eff_n1 = ROOT.TEfficiency("h_n1","Percent of Events after n-1 Cuts",10,0,10)
htot_n1 = ROOT.TH1D("htot_n1", "Total Events", 10, 0, 10)
htot_n1.Sumw2()
hpass_n1 = ROOT.TH1D("hpass_n1", "Passed Events", 10, 0, 10)
hpass_n1.Sumw2()


eff_signal = ROOT.TEfficiency("h_signal","Percent of Events after individual Cuts",10,0,10)
htot_signal = ROOT.TH1D("htot_signal", "Total Events", 10, 0, 10)
htot_signal.Sumw2()
hpass_signal = ROOT.TH1D("hpass_signal", "Passed Events", 10, 0, 10)
hpass_signal.Sumw2()


eff_n1_signal = ROOT.TEfficiency("h_n1_signal","Percent of Events after n-1 Cuts",10,0,10)
htot_n1_signal = ROOT.TH1D("htot_n1_signal", "Total Events", 10, 0, 10)
htot_n1_signal.Sumw2()
hpass_n1_signal = ROOT.TH1D("hpass_n1_signal", "Passed Events", 10, 0, 10)
hpass_n1_signal.Sumw2()




cuts_list = ["AtLeastTwoFakeableLeps", "PassesMETFilters", "LeadSubleadLeptonConePtCut", "ZMassAndInvarMassCut", "PassesHLTCuts", "AtMostTwoTightLeps", "EnoughJets"]
for i, cut in enumerate(cuts_list):
  print("At cut ", cut)
  htot.SetBinContent(i+1, t_ttbar.GetEntries())
  hpass.SetBinContent(i+1, t_ttbar.GetEntries(cut))

  htot.GetXaxis().SetBinLabel(i+1, cut)
  hpass.GetXaxis().SetBinLabel(i+1, cut)

  htot_signal.SetBinContent(i+1, t_signal.GetEntries())
  hpass_signal.SetBinContent(i+1, t_signal.GetEntries(cut))

  all_cuts = " && ".join(cuts_list)
  cuts_list_minus_one = cuts_list.copy()
  cuts_list_minus_one.remove(cut)
  n1_cuts = " && ".join(cuts_list_minus_one)

  htot_n1.SetBinContent(i+1, t_ttbar.GetEntries(n1_cuts))
  hpass_n1.SetBinContent(i+1, t_ttbar.GetEntries(all_cuts))

  htot_n1.GetXaxis().SetBinLabel(i+1, cut)
  hpass_n1.GetXaxis().SetBinLabel(i+1, cut)

  htot_n1_signal.SetBinContent(i+1, t_signal.GetEntries(n1_cuts))
  hpass_n1_signal.SetBinContent(i+1, t_signal.GetEntries(all_cuts))

eff.SetPassedHistogram(hpass, "F")
eff.SetTotalHistogram(htot, "F")

eff_n1.SetPassedHistogram(hpass_n1, "F")
eff_n1.SetTotalHistogram(htot_n1, "F")


eff_signal.SetPassedHistogram(hpass_signal, "F")
eff_signal.SetTotalHistogram(htot_signal, "F")

eff_n1_signal.SetPassedHistogram(hpass_n1_signal, "F")
eff_n1_signal.SetTotalHistogram(htot_n1_signal, "F")


c1.SetGrid()

eff.Draw()
eff_signal.SetLineColor(ROOT.kRed)
eff_signal.Draw("same")

legend = ROOT.TLegend()
legend.AddEntry(eff, "TTTo2L2Nu")
legend.AddEntry(eff_signal, "DL Radion M400")
legend.Draw("same")

ROOT.gPad.Update()
graph = eff.GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1.0)

c1.SaveAs("eff_eachcut.pdf")

eff_n1.Draw()
eff_n1_signal.SetLineColor(ROOT.kRed)
eff_n1_signal.Draw("same")

legend = ROOT.TLegend()
legend.AddEntry(eff_n1, "TTTo2L2Nu")
legend.AddEntry(eff_n1_signal, "DL Radion M400")
legend.Draw("same")

ROOT.gPad.Update()
graph = eff_n1.GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1.0)

c1.SaveAs("eff_nminus1.pdf")



nFakes_hist = ROOT.TH1D("nfakes", "nFakeable Leptons", 10, 0, 10)
nFakes_signal_hist = ROOT.TH1D("nfakes_signal", "nFakeable Leptons", 10, 0, 10)
t_ttbar.Project("nfakes", "n_fakeable_muons+n_fakeable_electrons")
t_signal.Project("nfakes_signal", "n_fakeable_muons+n_fakeable_electrons")

nFakes_hist.Scale(1.0/nFakes_hist.Integral())
nFakes_signal_hist.Scale(1.0/nFakes_signal_hist.Integral())

nFakes_hist.Draw()
nFakes_signal_hist.Draw("same")
nFakes_signal_hist.SetLineColor(ROOT.kRed)

legend = ROOT.TLegend()
legend.AddEntry(nFakes_hist, "TTTo2L2Nu")
legend.AddEntry(nFakes_signal_hist, "DL Radion M400")
legend.Draw("same")

nFakes_hist.SetMinimum(0)
nFakes_hist.SetMaximum(1.0)

c1.SaveAs("nFakeableLeps.pdf")
