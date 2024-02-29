import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
#import ROOT
from coffea.nanoevents.methods import vector

def add_single_hlv(EventProcess):
    return 1

def add_double_hlv(EventProcess):
    events = EventProcess.events
    muons = events.Muon
    electrons = events.Electron
    taus = events.Tau
    ak4_jets = events.Jet
    ak8_jets = events.FatJet
    met = events.MET
    flag = events.Flag
    HLT = events.HLT
    Runyear = EventProcess.Runyear
    isMC = EventProcess.isMC
    debug = EventProcess.debug

    #Select the leptons to save
    muons["px"] = muons.px; muons["py"] = muons.py; muons["pz"] = muons.pz; muons["energy"] = muons.energy
    muons_pre = muons[(muons.preselected)]
    muons_fake = muons[(muons.fakeable)]
    muons_tight = muons[(muons.tight)]

    electrons["px"] = electrons.px; electrons["py"] = electrons.py; electrons["pz"] = electrons.pz; electrons["energy"] = electrons.energy
    electrons_pre = electrons[(electrons.preselected)]
    electrons_fake = electrons[(electrons.fakeable)]
    electrons_tight = electrons[(electrons.tight)]

    leptons_fakeable = ak.concatenate([electrons_fake, muons_fake], axis=1)
    leptons_fakeable = ak.pad_none(leptons_fakeable[ak.argsort(leptons_fakeable.conept, ascending=False)], 2)

    events["double_lep0"] = leptons_fakeable[:,0]
    events["double_lep1"] = leptons_fakeable[:,1]

    #Select the Ak4 Jets to save
    ak4_jets["px"] = ak4_jets.px; ak4_jets["py"] = ak4_jets.py; ak4_jets["pz"] = ak4_jets.pz; ak4_jets["energy"] = ak4_jets.energy
    ak4_jets_cleaned = ak.pad_none(ak4_jets[(ak4_jets.cleaned_double)], 4)

    #Take first 2 B tagged, then second 2 pT ordered (after removing bTags)
    ak4_jets_bsorted = ak4_jets_cleaned
    ak4_jets_bsorted_all_none = ak.all(ak.all(ak.is_none(ak4_jets_bsorted, axis=1), axis=1))
    if not ak4_jets_bsorted_all_none:
        ak4_jets_bsorted = ak4_jets_cleaned[ak.argsort(ak4_jets_cleaned.btagDeepFlavB, ascending=False)]

    events["double_ak4_jet0"] = ak4_jets_bsorted[:,0]
    events["double_ak4_jet1"] = ak4_jets_bsorted[:,1]


    ak4_jets_without_bjets = ak4_jets_bsorted[:,2:]
    ak4_jets_ptsorted = ak4_jets_without_bjets
    ak4_jets_ptsorted_all_none = ak.all(ak.all(ak.is_none(ak4_jets_ptsorted, axis=1), axis=1))
    if not ak4_jets_ptsorted_all_none:
        ak4_jets_ptsorted = ak4_jets_without_bjets[ak.argsort(ak4_jets_without_bjets.pt, ascending=False)]

    events["double_ak4_jet2"] = ak4_jets_ptsorted[:,0]
    events["double_ak4_jet3"] = ak4_jets_ptsorted[:,1]


    #Select the Ak8 Jet to save
    ak8_jets_cleaned = ak.pad_none(ak8_jets[(ak8_jets.cleaned_double)], 1)

    ak8_jets_cleaned_sorted = ak8_jets_cleaned
    ak8_jets_cleaned_all_none = ak.all(ak.all(ak.is_none(ak8_jets_cleaned_sorted, axis=1), axis=1))
    if not ak8_jets_cleaned_all_none:
        ak8_jets_cleaned_sorted = ak8_jets_cleaned[ak.argsort(ak8_jets_cleaned.pt, axis=1, ascending=False)]

    events["double_ak8_jet0"] = ak8_jets_cleaned_sorted[:,0]

    #Base objects are now
    #events.double_lep0
    #events.double_lep1
    #events.double_ak4_jet0
    #events.double_ak4_jet1
    #events.double_ak4_jet2
    #events.double_ak4_jet3
    #events.double_ak8_jet0
    #events.MET

    events["double_di_b_jet"] = (events.double_ak4_jet0 + events.double_ak4_jet1)
    events["double_di_jet"] = (events.double_ak4_jet2 + events.double_ak4_jet3)
    events["double_di_lepton"] = (events.double_lep0 + events.double_lep1)

    #Combined objects are now
    #events.di_b_jet    (ak4_jet0 + ak4_jet1)
    #events.di_jet      (ak4_jet2 + ak4_jet3)
    #events.di_lepton   (lep0 + lep1)



    ##### Now for the high level variables #####
    #dR between lep0 and lep1
    #dR between jet0 and jet1 (leading bjets)
    #dR between lep0+lep1 and jet2+jet3 (dilep vs dijet)
    #dR between lep0+lep1 and jet0+jet1 (dilep vs dibjet)
    #abs(dPhi) between lep0 and lep1
    #abs(dPhi) between jet0 and jet1 (leading bjets)
    #abs(dPhi) between MET and lep0+lep1 (MET vs dilep)
    #abs(dPhi) between MET and jet0+jet1 (MET vs dibjet)
    #minimum dR between lep0 and all ak4 jets (Does this mean preselected/cleaned???) go with cleaned
    #minimum dR between lep1 and all ak4 jets ^^^
    #minimum dR between jet0 and leading two leptons
    #minimum dR between jet1 and leading two leptons
    #minimum dR among all ak4 jets
    #minimum abs(dPhi) among all ak4 jets
    #di-b-jet invariant mass
    #di-b-jet invariant mass with b-jet energy regression applied
    #di-lepton invariant mass
    #invariant mass of 4-vector sum of MET and di-lepton
    #invariant mass of 4-vector sum of MET, di-lepton, and di-jets
    #invariant mass of 4-vector sum of MET, di-lepton, and di-jets with b-jet energy regression applied
    #MET-LD
    #HT
    #lep0 conept
    #lep1 conept
    #nBtaggedAk4Jets
    #boosted true/false
    #Mll_T transverse mass of missing pT and di-lepton
    ##### End of the list #####

    #dR between lep0 and lep1
    #dR between jet0 and jet1 (leading bjets)
    #dR between lep0+lep1 and jet2+jet3 (dilep vs dijet)
    #dR between lep0+lep1 and jet0+jet1 (dilep vs dibjet)
    def delta_r(obj1, obj2):
        dPhi = obj1.phi - obj2.phi
        dPhi = ak.where(
            dPhi < 3.14159265,
                dPhi,
                dPhi - 2*3.14159265
        )
        dEta = obj1.eta - obj2.eta
        dR = (dPhi**2 + dEta**2)**(0.5)
        return dR

    events["dR_dilep"] = delta_r(events.double_lep0, events.double_lep1)
    events["dR_dibjet"] = delta_r(events.double_ak4_jet0, events.double_ak4_jet1)
    events["dR_dilep_dijet"] = delta_r(events.double_lep0 + events.double_lep1, events.double_ak4_jet2 + events.double_ak4_jet3)
    events["dR_dilep_dibjet"] = delta_r(events.double_lep0 + events.double_lep1, events.double_ak4_jet0 + events.double_ak4_jet1)

    #abs(dPhi) between lep0 and lep1
    #abs(dPhi) between jet0 and jet1 (leading bjets)
    #abs(dPhi) between MET and lep0+lep1 (MET vs dilep)
    #abs(dPhi) between MET and jet0+jet1 (MET vs dibjet)
    #MET can't do delta_r since it does not have eta
    def delta_phi(obj1, obj2):
        dPhi = obj1.phi - obj2.phi
        dPhi = ak.where(
            dPhi < 3.14159265,
                dPhi,
                dPhi - 2*3.14159265
        )
        return dPhi

    events["dPhi_MET_dilep"] = delta_phi(events.MET, events.double_lep0 + events.double_lep1)
    events["dPhi_MET_dibjet"] = delta_phi(events.MET, events.double_ak4_jet0 + events.double_ak4_jet1)


    #minimum dR between lep0 and all ak4 jets (Does this mean preselected/cleaned???) go with cleaned
    #minimum dR between lep1 and all ak4 jets ^^^
    #minimum dR between jet0 and leading two leptons
    #minimum dR between jet1 and leading two leptons
    #minimum dR among all ak4 jets
    #minimum abs(dPhi) among all ak4 jets
