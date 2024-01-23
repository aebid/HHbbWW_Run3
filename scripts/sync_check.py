import ROOT
import uproot
import awkward as ak

fname = "../python/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M450_Run3Sync.root"

uproot_file = uproot.open(fname)



print("Double Category Sync Info")


tree = uproot_file['Double_Tree']

events = tree.arrays()

nRecoElectrons = ak.sum(events.n_electrons)
nPreselElectrons = ak.sum(events.n_presel_electrons)
nFakeableElectrons = ak.sum(events.n_fakeable_electrons)
nTightElectrons = ak.sum(events.n_tight_electrons)


nRecoMuons = ak.sum(events.n_muons)
nPreselMuons = ak.sum(events.n_presel_muons)
nFakeableMuons = ak.sum(events.n_fakeable_muons)
nTightMuons = ak.sum(events.n_tight_muons)

nAk4Jets = ak.sum(events.n_ak4_jets)
nPreselAk4Jets = ak.sum(events.n_presel_ak4_jets)
nCleanedAk4Jets = ak.sum(events.n_cleaned_ak4_jets)
nMediumBAk4Jets = ak.sum(events.n_medium_btag_ak4_jets)

nAk8Jets = ak.sum(events.n_ak8_jets)
nPreselAk8Jets = ak.sum(events.n_presel_ak8_jets)
nCleanedAk8Jets = ak.sum(events.n_cleaned_ak8_jets)
nMediumBAk8Jets = ak.sum(events.n_btag_ak8_jets)



print("nReco Electrons        = ", nRecoElectrons)
print("nPreselected Electrons = ", nPreselElectrons)
print("nFakeable Electrons    = ", nFakeableElectrons)
print("nTight Electrons       = ", nTightElectrons)


print("nReco Muons            = ", nRecoMuons)
print("nPreselected Muons     = ", nPreselMuons)
print("nFakeable Muons        = ", nFakeableMuons)
print("nTight Muons           = ", nTightMuons)


print("nReco Ak4 Jets         = ", nAk4Jets)
print("nPreselected Ak4 Jets  = ", nPreselAk4Jets)
print("nCleaned Ak4 Jets      = ", nCleanedAk4Jets)
print("nMediumB Ak4 Jets      = ", nMediumBAk4Jets)

print("nReco Ak8 Jets         = ", nAk8Jets)
print("nPreselected Ak8 Jets  = ", nPreselAk8Jets)
print("nCleaned Ak8 Jets      = ", nCleanedAk8Jets)
print("nMediumB Ak8 Jets      = ", nMediumBAk8Jets)

nFakeableLeptons = (events.n_fakeable_electrons + events.n_fakeable_muons)

nFakeGt1 = (nFakeableLeptons >= 1)
nFakeGt2 = (nFakeableLeptons >= 2)

nEventsMoreThan1Fake = ak.sum(nFakeGt1)
nEventsMoreThan2Fake = ak.sum(nFakeGt2)


print("nEvents with 1 or more Fakeable Lepton = ", nEventsMoreThan1Fake)
print("nEvents with 2 or more Fakeable Lepton = ", nEventsMoreThan2Fake)

print("#########################################")


#Double Category Info

nEvents_2FakeableLeps = ak.sum(events.AtLeastTwoFakeableLeps)
nEvents_ee = ak.sum(events.double_is_ee)
nEvents_mm = ak.sum(events.double_is_mm)
nEvents_em = ak.sum(events.double_is_em)
nEvents_me = ak.sum(events.double_is_me)
nEvents_LeptonChargeCut = ak.sum(events.LeadSubleadChargeCut)
nEvents_LeptonConePtCut = ak.sum(events.LeadSubleadLeptonConePtCut)
nEvents_InvarMassCut = ak.sum(events.InvarMassCut)
nEvents_ZMassCut = ak.sum(events.ZMassCut)
nEvents_2TightLeps = ak.sum(events.AtMostTwoTightLeps)
nEvents_EnoughJets = ak.sum(events.EnoughJets)
nEvents_Signal = ak.sum(events.Double_Signal)
nEvents_Fake = ak.sum(events.Double_Fake)
nEvents_HLT = ak.sum(events.PassesHLTCuts)


print("nEvents with at least 2 fakeable leps = ", nEvents_2FakeableLeps)
print("nEvents EE                            = ", nEvents_ee)
print("nEvents MM                            = ", nEvents_mm)
print("nEvents EM                            = ", nEvents_em)
print("nEvents ME                            = ", nEvents_me)
print("nEvents lepton charge cut             = ", nEvents_LeptonChargeCut)
print("nEvents lepton conept cut             = ", nEvents_LeptonConePtCut)
print("nEvents InvarMassCut                  = ", nEvents_InvarMassCut)
print("nEvents ZMassCut                      = ", nEvents_ZMassCut)
print("nEvents at most 2 tight leps          = ", nEvents_2TightLeps)
print("nEvents Enough Jets                   = ", nEvents_EnoughJets)
print("nEvents Signal                        = ", nEvents_Signal)
print("nEvents Fake                          = ", nEvents_Fake)
print("nEvents HLT                           = ", nEvents_HLT)










print("Single Category Sync Info")


tree = uproot_file['Single_Tree']

events = tree.arrays()

nRecoElectrons = ak.sum(events.n_electrons)
nPreselElectrons = ak.sum(events.n_presel_electrons)
nFakeableElectrons = ak.sum(events.n_fakeable_electrons)
nTightElectrons = ak.sum(events.n_tight_electrons)


nRecoMuons = ak.sum(events.n_muons)
nPreselMuons = ak.sum(events.n_presel_muons)
nFakeableMuons = ak.sum(events.n_fakeable_muons)
nTightMuons = ak.sum(events.n_tight_muons)

nAk4Jets = ak.sum(events.n_ak4_jets)
nPreselAk4Jets = ak.sum(events.n_presel_ak4_jets)
nCleanedAk4Jets = ak.sum(events.n_cleaned_ak4_jets)
nMediumBAk4Jets = ak.sum(events.n_medium_btag_ak4_jets)

nAk8Jets = ak.sum(events.n_ak8_jets)
nPreselAk8Jets = ak.sum(events.n_presel_ak8_jets)
nCleanedAk8Jets = ak.sum(events.n_cleaned_ak8_jets)
nMediumBAk8Jets = ak.sum(events.n_btag_ak8_jets)



print("nReco Electrons        = ", nRecoElectrons)
print("nPreselected Electrons = ", nPreselElectrons)
print("nFakeable Electrons    = ", nFakeableElectrons)
print("nTight Electrons       = ", nTightElectrons)


print("nReco Muons            = ", nRecoMuons)
print("nPreselected Muons     = ", nPreselMuons)
print("nFakeable Muons        = ", nFakeableMuons)
print("nTight Muons           = ", nTightMuons)


print("nReco Ak4 Jets         = ", nAk4Jets)
print("nPreselected Ak4 Jets  = ", nPreselAk4Jets)
print("nCleaned Ak4 Jets      = ", nCleanedAk4Jets)
print("nMediumB Ak4 Jets      = ", nMediumBAk4Jets)

print("nReco Ak8 Jets         = ", nAk8Jets)
print("nPreselected Ak8 Jets  = ", nPreselAk8Jets)
print("nCleaned Ak8 Jets      = ", nCleanedAk8Jets)
print("nMediumB Ak8 Jets      = ", nMediumBAk8Jets)

nFakeableLeptons = (events.n_fakeable_electrons + events.n_fakeable_muons)

nFakeGt1 = (nFakeableLeptons >= 1)
nFakeGt2 = (nFakeableLeptons >= 2)

nEventsMoreThan1Fake = ak.sum(nFakeGt1)
nEventsMoreThan2Fake = ak.sum(nFakeGt2)


print("nEvents with 1 or more Fakeable Lepton = ", nEventsMoreThan1Fake)
print("nEvents with 2 or more Fakeable Lepton = ", nEventsMoreThan2Fake)

print("#########################################")



#Single Category Info

nEvents_1FakeableLeps = ak.sum(events.AtLeastOneFakeableLep)
nEvents_e = ak.sum(events.single_is_e)
nEvents_m = ak.sum(events.single_is_m)
nEvents_LeptonConePtCut = ak.sum(events.LeadLeptonConePtCut)
nEvents_InvarMassCut = ak.sum(events.InvarMassCut)
nEvents_ZMassCut = ak.sum(events.ZMassCut)
nEvents_1TightLeps = ak.sum(events.AtMostOneTightLep)
nEvents_AtLeastOneBJet = ak.sum(events.AtLeastOneBJet)
nEvents_EnoughNonBJets = ak.sum(events.EnoughNonBJets)
nEvents_Signal = ak.sum(events.Single_Signal)
nEvents_Fake = ak.sum(events.Single_Fake)
nEvents_HLT = ak.sum(events.PassesHLTCuts)


print("nEvents with at least 1 fakeable lep = ", nEvents_1FakeableLeps)
print("nEvents E                            = ", nEvents_e)
print("nEvents M                            = ", nEvents_m)
print("nEvents lepton conept cut            = ", nEvents_LeptonConePtCut)
print("nEvents InvarMassCut                 = ", nEvents_InvarMassCut)
print("nEvents ZMassCut                     = ", nEvents_ZMassCut)
print("nEvents at most 1 tight leps         = ", nEvents_1TightLeps)
print("nEvents at least 1 b jet             = ", nEvents_AtLeastOneBJet)
print("nEvents Enough NonB Jets             = ", nEvents_EnoughNonBJets)
print("nEvents Signal                       = ", nEvents_Signal)
print("nEvents Fake                         = ", nEvents_Fake)
print("nEvents HLT                          = ", nEvents_HLT)
