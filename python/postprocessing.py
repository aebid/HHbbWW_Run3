import ROOT
import uproot
from array import array

fname = 'sync_test.root'

f = ROOT.TFile.Open(fname)
events = f.Get("Single_Tree")


outfile = ROOT.TFile.Open("out_postproc.root", "RECREATE")
new_tree = events.CloneTree()
mHbb = array('f', [0])
mHbbBranch = new_tree.Branch('mHbb', mHbb, 'mHbb/F')
HT = array('f', [0])
HTBranch = new_tree.Branch('HT', HT, 'HT/F')
mTw = array('f', [0])
mTwBranch = new_tree.Branch('mTw', mTw, 'mTw/F')
hbb_pt = array('f', [0])
hbb_ptBranch = new_tree.Branch('hbb_pt', hbb_pt, 'hbb_pt/F')
hh_pt = array('f', [0])
hh_ptBranch = new_tree.Branch('hh_pt', hh_pt, 'hh_pt/F')



print("There are ", events.GetEntries(), " events")
for evtcount, event in enumerate(events):
  if ((evtcount/events.GetEntries())*100)%1 == 0: print("At event ", evtcount)

  #Min dR between leading lepton and all ak4 jets
  dR0 = ( (event.lep0_eta - event.ak4_jet0_eta)**2 + (event.lep0_phi - event.ak4_jet0_phi)**2 )**(0.5) if event.ak4_jet0_pt != 0 else 999.9
  dR1 = ( (event.lep0_eta - event.ak4_jet1_eta)**2 + (event.lep0_phi - event.ak4_jet1_phi)**2 )**(0.5) if event.ak4_jet1_pt != 0 else 999.9
  dR2 = ( (event.lep0_eta - event.ak4_jet2_eta)**2 + (event.lep0_phi - event.ak4_jet2_phi)**2 )**(0.5) if event.ak4_jet2_pt != 0 else 999.9
  dR3 = ( (event.lep0_eta - event.ak4_jet3_eta)**2 + (event.lep0_phi - event.ak4_jet3_phi)**2 )**(0.5) if event.ak4_jet3_pt != 0 else 999.9
  min_dR = min(dR0, dR1, dR2, dR3)
  #print("Min dR of ", dR0, dR1, dR2, dR3, " is ", min_dR)

  dR_bjet = dR0

  lep0_lorentz = ROOT.TLorentzVector()
  lep0_lorentz.SetPxPyPzE(event.lep0_px, event.lep0_py, event.lep0_pz, event.lep0_E)

  lep1_lorentz = ROOT.TLorentzVector()
  lep1_lorentz.SetPxPyPzE(event.lep1_px, event.lep1_py, event.lep1_pz, event.lep1_E)

  ak40_lorentz = ROOT.TLorentzVector()
  ak40_lorentz.SetPxPyPzE(event.ak4_jet0_px, event.ak4_jet0_py, event.ak4_jet0_pz, event.ak4_jet0_E)

  ak41_lorentz = ROOT.TLorentzVector()
  ak41_lorentz.SetPxPyPzE(event.ak4_jet1_px, event.ak4_jet1_py, event.ak4_jet1_pz, event.ak4_jet1_E)

  ak42_lorentz = ROOT.TLorentzVector()
  ak42_lorentz.SetPxPyPzE(event.ak4_jet2_px, event.ak4_jet2_py, event.ak4_jet2_pz, event.ak4_jet2_E)

  ak43_lorentz = ROOT.TLorentzVector()
  ak43_lorentz.SetPxPyPzE(event.ak4_jet3_px, event.ak4_jet3_py, event.ak4_jet3_pz, event.ak4_jet3_E)

  ak80_lorentz = ROOT.TLorentzVector()
  ak80_lorentz.SetPxPyPzE(event.ak8_jet0_px, event.ak8_jet0_py, event.ak8_jet0_pz, event.ak8_jet0_E)

  met_lorentz = ROOT.TLorentzVector()
  met_lorentz.SetPxPyPzE(event.met_px, event.met_py, event.met_pz, event.met_E)

  w_lepmet_system = ROOT.TLorentzVector()
  w_jets_system = ROOT.TLorentzVector()
  h_bb_system = ROOT.TLorentzVector()
  h_ww_system = ROOT.TLorentzVector()
  hh_system = ROOT.TLorentzVector()

  w_lepmet_system = lep0_lorentz + met_lorentz
  w_jets_system = ak42_lorentz + ak43_lorentz

  if event.Single_Res_allReco_2b or event.Single_Res_allReco_1b or event.Single_Res_MissWJet_2b or event.Single_Res_MissWJet_1b:
    h_bb_system = ak40_lorentz + ak41_lorentz
  if event.Single_HbbFat_WjjRes_AllReco or event.Single_HbbFat_WjjRes_MissJet:
    h_bb_system = ak80_lorentz

  h_ww_system = w_lepmet_system + w_jets_system

  hh_system = h_bb_system + h_ww_system

  #print("Category is ", event.Single_Res_allReco_2b, event.Single_Res_allReco_1b, event.Single_Res_MissWJet_2b, event.Single_Res_MissWJet_1b, event.Single_HbbFat_WjjRes_AllReco, event.Single_HbbFat_WjjRes_MissJet)
  #print("w_lepmet_system pT M", w_lepmet_system.Pt(), w_lepmet_system.Mt())
  #print("w_jets_system   pT M", w_jets_system.Pt(), w_jets_system.Mt())
  #print("h_bb_system     pT M", h_bb_system.Pt(), h_bb_system.Mt())
  #print("h_ww_system     pT M", h_ww_system.Pt(), h_ww_system.Mt())
  #print("hh_system       pT M", hh_system.Pt(), hh_system.Mt())


  HT_tmp = 0.0
  if abs(event.ak4_jet0_pt) > 50: HT_tmp += abs(event.ak4_jet0_pt)
  if abs(event.ak4_jet1_pt) > 50: HT_tmp += abs(event.ak4_jet1_pt)
  if abs(event.ak4_jet2_pt) > 50: HT_tmp += abs(event.ak4_jet2_pt)
  if abs(event.ak4_jet3_pt) > 50: HT_tmp += abs(event.ak4_jet3_pt)

  mHbb[0] = h_bb_system.M()
  mHbbBranch.Fill()
  HT[0] = HT_tmp
  HTBranch.Fill()
  mTw[0] = w_lepmet_system.Mt()
  mTwBranch.Fill()
  hbb_pt[0] = h_bb_system.Pt()
  hbb_ptBranch.Fill()
  hh_pt[0] = hh_system.Pt()
  hh_ptBranch.Fill()

  HTBranch.Fill()

outfile.Write()
