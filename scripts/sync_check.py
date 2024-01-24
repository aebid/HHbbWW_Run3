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



nEvents_RecoEleGt2 = ak.sum(events.n_electrons >= 2)
nEvents_PreselEleGt2 = ak.sum(events.n_presel_electrons >= 2)
nEvents_FakeEleGt2 = ak.sum(events.n_fakeable_electrons >= 2)
nEvents_TightEleGt2 = ak.sum(events.n_tight_electrons >= 2)

nEvents_RecoMuonGt2 = ak.sum(events.n_muons >= 2)
nEvents_PreselMuonGt2 = ak.sum(events.n_presel_muons >= 2)
nEvents_FakeMuonGt2 = ak.sum(events.n_fakeable_muons >= 2)
nEvents_TightMuonGt2 = ak.sum(events.n_tight_muons >= 2)

nEvents_Ak4JetsGt1 = ak.sum(events.n_ak4_jets >= 1)
nEvents_PreselAk4JetsGt1 = ak.sum(events.n_presel_ak4_jets >= 1)
nEvents_CleanedAk4JetsGt1 = ak.sum(events.n_cleaned_ak4_jets >= 1)
nEvents_MediumBAk4JetsGt1 = ak.sum(events.n_medium_btag_ak4_jets >= 1)

nEvents_Ak8JetsGt1 = ak.sum(events.n_ak8_jets >= 1)
nEvents_PreselAk8JetsGt1 = ak.sum(events.n_presel_ak8_jets >= 1)
nEvents_CleanedAk8JetsGt1 = ak.sum(events.n_cleaned_ak8_jets >= 1)
nEvents_MediumBAk8JetsGt1 = ak.sum(events.n_btag_ak8_jets >= 1)



print("nEvents with nReco Electrons >= 2         = ", nEvents_RecoEleGt2)
print("nEvents with nPreselected Electrons >= 2  = ", nEvents_PreselEleGt2)
print("nEvents with nFakeable Electrons >= 2     = ", nEvents_FakeEleGt2)
print("nEvents with nTight Electrons >= 2        = ", nEvents_TightEleGt2)

print("nEvents with nReco Muons >= 2             = ", nEvents_RecoMuonGt2)
print("nEvents with nPreselected Muons >= 2      = ", nEvents_PreselMuonGt2)
print("nEvents with nFakeable Muons >= 2         = ", nEvents_FakeMuonGt2)
print("nEvents with nTight Muons >= 2            = ", nEvents_TightMuonGt2)

print("nEvents with nReco Ak4 Jets >= 1          = ", nEvents_Ak4JetsGt1)
print("nEvents with nPreselected Ak4 Jets >= 1   = ", nEvents_PreselAk4JetsGt1)
print("nEvents with nCleaned Ak4 Jets >= 1       = ", nEvents_CleanedAk4JetsGt1)
print("nEvents with nMediumB Ak4 Jets >= 1       = ", nEvents_MediumBAk4JetsGt1)

print("nEvents with nReco Ak8 Jets >= 1          = ", nEvents_Ak8JetsGt1)
print("nEvents with nPreselected Ak8 Jets >= 1   = ", nEvents_PreselAk8JetsGt1)
print("nEvents with nCleaned Ak8 Jets >= 1       = ", nEvents_CleanedAk8JetsGt1)
print("nEvents with nMediumB Ak8 Jets >= 1       = ", nEvents_MediumBAk8JetsGt1)

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



nEvents_RecoEleGt1 = ak.sum(events.n_electrons >= 1)
nEvents_PreselEleGt1 = ak.sum(events.n_presel_electrons >= 1)
nEvents_FakeEleGt1 = ak.sum(events.n_fakeable_electrons >= 1)
nEvents_TightEleGt1 = ak.sum(events.n_tight_electrons >= 1)

nEvents_RecoMuonGt1 = ak.sum(events.n_muons >= 1)
nEvents_PreselMuonGt1 = ak.sum(events.n_presel_muons >= 1)
nEvents_FakeMuonGt1 = ak.sum(events.n_fakeable_muons >= 1)
nEvents_TightMuonGt1 = ak.sum(events.n_tight_muons >= 1)

nEvents_Ak4JetsGt1 = ak.sum(events.n_ak4_jets >= 1)
nEvents_PreselAk4JetsGt1 = ak.sum(events.n_presel_ak4_jets >= 1)
nEvents_CleanedAk4JetsGt1 = ak.sum(events.n_cleaned_ak4_jets >= 1)
nEvents_MediumBAk4JetsGt1 = ak.sum(events.n_medium_btag_ak4_jets >= 1)

nEvents_Ak8JetsGt1 = ak.sum(events.n_ak8_jets >= 1)
nEvents_PreselAk8JetsGt1 = ak.sum(events.n_presel_ak8_jets >= 1)
nEvents_CleanedAk8JetsGt1 = ak.sum(events.n_cleaned_ak8_jets >= 1)
nEvents_MediumBAk8JetsGt1 = ak.sum(events.n_btag_ak8_jets >= 1)



print("nEvents with nReco Electrons >= 1         = ", nEvents_RecoEleGt1)
print("nEvents with nPreselected Electrons >= 1  = ", nEvents_PreselEleGt1)
print("nEvents with nFakeable Electrons >= 1     = ", nEvents_FakeEleGt1)
print("nEvents with nTight Electrons >= 1        = ", nEvents_TightEleGt1)

print("nEvents with nReco Muons >= 1             = ", nEvents_RecoMuonGt1)
print("nEvents with nPreselected Muons >= 1      = ", nEvents_PreselMuonGt1)
print("nEvents with nFakeable Muons >= 1         = ", nEvents_FakeMuonGt1)
print("nEvents with nTight Muons >= 1            = ", nEvents_TightMuonGt1)

print("nEvents with nReco Ak4 Jets >= 1          = ", nEvents_Ak4JetsGt1)
print("nEvents with nPreselected Ak4 Jets >= 1   = ", nEvents_PreselAk4JetsGt1)
print("nEvents with nCleaned Ak4 Jets >= 1       = ", nEvents_CleanedAk4JetsGt1)
print("nEvents with nMediumB Ak4 Jets >= 1       = ", nEvents_MediumBAk4JetsGt1)

print("nEvents with nReco Ak8 Jets >= 1          = ", nEvents_Ak8JetsGt1)
print("nEvents with nPreselected Ak8 Jets >= 1   = ", nEvents_PreselAk8JetsGt1)
print("nEvents with nCleaned Ak8 Jets >= 1       = ", nEvents_CleanedAk8JetsGt1)
print("nEvents with nMediumB Ak8 Jets >= 1       = ", nEvents_MediumBAk8JetsGt1)

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
