import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
#import ROOT
from coffea.nanoevents.methods import vector


def add_conept(EventProcess):
    #Cone-pt
    #https://github.com/CERN-PH-CMG/cmgtools-lite/blob/f8a34c64a4489d94ff9ac4c0d8b0b06dad46e521/TTHAnalysis/python/tools/conept.py#L74
    #Page 10 here https://indico.cern.ch/event/690741/contributions/2940170/attachments/1619880/2577898/ttHsync_180320_CMP_v2.pdf
    events = EventProcess.events
    muons = events.Muon
    electrons = events.Electron
    debug = EventProcess.debug
    if debug: print("Starting cone pt")

    muon_conept = ak.where(
        (abs(muons.pdgId) == 13) & (muons.mediumId) & (muons.mvaTTH > 0.50),
            muons.pt,
            0.9 * muons.pt * (1.0 + muons.jetRelIso)
    )

    electron_conept = ak.where(
        (abs(electrons.pdgId) == 11) & (electrons.mvaTTH > 0.30),
            electrons.pt,
            0.9 * electrons.pt * (1.0 + electrons.jetRelIso)
    )

    events.Muon = ak.with_field(events.Muon, muon_conept, "conept")
    events.Electron = ak.with_field(events.Electron, electron_conept, "conept")


def link_jets(EventProcess):
    #We want to create a link between the leptons and their ak4 jet, and the ak8 jets and their subjet
    #We also need to calculate the muon jetDeepJet values for muon btagging (slide 7 https://indico.cern.ch/event/812025/contributions/3475878/attachments/1867083/3070589/gp-fr-run2b.pdf)
    events = EventProcess.events
    muons = events.Muon
    electrons = events.Electron
    ak4_jets = ak.pad_none(events.Jet, 1)
    ak8_jets = events.FatJet
    ak8_subjets = ak.pad_none(events.SubJet, 2)
    jetDeepJet_WP_loose = EventProcess.jetDeepJet_WP[0]
    jetDeepJet_WP_medium = EventProcess.jetDeepJet_WP[1]
    jetDeepJet_WP_tight  = EventProcess.jetDeepJet_WP[2]
    debug = EventProcess.debug
    if debug: print("Starting link jets")

    events.Muon = ak.with_field(events.Muon, ak4_jets[muons.jetIdx].mask[(muons.jetIdx >= 0)], "ak4_jets")
    events.Electron = ak.with_field(events.Electron, ak4_jets[electrons.jetIdx].mask[(electrons.jetIdx >= 0)], "ak4_jets")
    events.FatJet = ak.with_field(events.FatJet, ak8_subjets[ak8_jets.subJetIdx1].mask[(ak8_jets.subJetIdx1 >= 0)], "subjet1")
    events.FatJet = ak.with_field(events.FatJet, ak8_subjets[ak8_jets.subJetIdx2].mask[(ak8_jets.subJetIdx2 >= 0)], "subjet2")

    jetDeepJet_min_pt = 20.0; jetDeepJet_max_pt = 45.0

    muons.jetDeepJet_Upper_x1 = ak.where(
        (muons.conept - jetDeepJet_min_pt) >= 0.0,
            muons.conept - jetDeepJet_min_pt,
            0.0
    )

    muons.jetDeepJet_Upper_x2 = ak.where(
        (muons.jetDeepJet_Upper_x1/(jetDeepJet_max_pt - jetDeepJet_min_pt)) <= 1.0,
            (muons.jetDeepJet_Upper_x1/(jetDeepJet_max_pt - jetDeepJet_min_pt)),
            1.0
    )

    events.Muon = ak.with_field(events.Muon, muons.jetDeepJet_Upper_x2 * jetDeepJet_WP_loose + (1 - muons.jetDeepJet_Upper_x2) * jetDeepJet_WP_medium, "jetDeepJet_Upper")


def muon_selection(EventProcess):
    events = EventProcess.events
    #Muons
    muons = events.Muon
    jetDeepJet_WP_medium = EventProcess.jetDeepJet_WP[1]
    isMC = EventProcess.isMC
    debug = EventProcess.debug
    if debug: print("Starting muon selection")

    muon_preselection_mask = (
        (abs(muons.eta) <= 2.4) & (muons.pt >= 5.0) & (abs(muons.dxy) <= 0.05) &
        (abs(muons.dz) <= 0.1) & (muons.miniPFRelIso_all <= 0.4) &
        (muons.sip3d <= 8) & (muons.looseId)
    )

    muon_fakeable_mask = (
        (muons.conept >= 10.0) &
        ak.where(
            ak.is_none(muons.ak4_jets, axis=1),
                (
                    (muons.mvaTTH > 0.50)
                    | #OR
                    (muons.jetRelIso < 0.80)
                ),
                (muons.ak4_jets.btagDeepFlavB <= jetDeepJet_WP_medium) &
                (
                    (muons.mvaTTH > 0.50)
                    | #OR
                    (muons.jetRelIso < 0.80) & (muons.ak4_jets.btagDeepFlavB <= muons.jetDeepJet_Upper)
                )
            )
    )

    muon_tight_mask = ((muons.mvaTTH >= 0.50) & (muons.mediumId))

    events.Muon = ak.with_field(events.Muon, muon_preselection_mask, "preselected")
    events.Muon = ak.with_field(events.Muon, muon_fakeable_mask & muon_preselection_mask, "fakeable")
    events.Muon = ak.with_field(events.Muon, muon_tight_mask & muon_fakeable_mask & muon_preselection_mask, "tight")


    events.Muon = ak.with_field(events.Muon, (getattr(muons, 'genPartFlav', False) == 1) | (getattr(muons, 'genPartFlav', False) == 15), "MC_Match")

    #NanoAOD -- 1 = prompt muon -- 15 = muon from prompt tau


def electron_selection(EventProcess):
    events = EventProcess.events
    #Electrons
    electrons = events.Electron
    muons = events.Muon
    jetDeepJet_WP_medium = EventProcess.jetDeepJet_WP[1]
    jetDeepJet_WP_tight = EventProcess.jetDeepJet_WP[2]
    isMC = EventProcess.isMC
    debug = EventProcess.debug
    if debug: print("Starting electron selection")

    #Need to check this! Run3 is mvaNoIso, Run2 is mvaFall17V2noIso
    #22Jan24 Run3 signal files look to not have mvaNoIso_WPL, trying mvaIso_WP90 for now
    mvaNoIso_WPL = getattr(electrons, 'mvaIso_WP90', False) | getattr(electrons, 'mvaNoIso_WPL', False) | getattr(electrons, 'mvaFall17V2noIso_WPL', False)
    mvaNoIso_WP90 = getattr(electrons, 'mvaIso_WP90', False) | getattr(electrons, 'mvaNoIso_WPL90', False) | getattr(electrons, 'mvaFall17V2noIso_WP90', False)

    electron_preselection_mask = (
        (abs(electrons.eta) <= 2.5) & (electrons.pt >= 7.0)& (abs(electrons.dxy) <= 0.05) &
        (abs(electrons.dz) <= 0.1) & (electrons.miniPFRelIso_all <= 0.4) &
        (electrons.sip3d <= 8) & (mvaNoIso_WPL) & (electrons.lostHits <= 1)
    )

    electron_fakeable_mask = (
        (electrons.conept >= 10.0) & (electrons.hoe <= 0.10) & (electrons.eInvMinusPInv >= -0.04) &
        (electrons.lostHits == 0) & (electrons.convVeto) &
        (
            (abs(electrons.eta + electrons.deltaEtaSC) > 1.479) & (electrons.sieie <= 0.030)
            | #OR
            (abs(electrons.eta + electrons.deltaEtaSC) <= 1.479) & (electrons.sieie <= 0.011)
        ) &
        ak.where(
            ak.is_none(electrons.ak4_jets, axis=1),
                True,
                ak.where(
                    electrons.mvaTTH < 0.3,
                        electrons.ak4_jets.btagDeepFlavB <= jetDeepJet_WP_tight,
                        electrons.ak4_jets.btagDeepFlavB <= jetDeepJet_WP_medium
                )
        ) &
        ak.where(
            electrons.mvaTTH < 0.30,
                (electrons.jetRelIso < 0.7) & (mvaNoIso_WP90),
                True
        )
    )

    electron_tight_mask = electrons.mvaTTH >= 0.30

    events.Electron = ak.with_field(events.Electron, electron_preselection_mask, "preselected")

    electrons = events.Electron
    mu_padded = ak.pad_none(muons, 1)
    #We pad muons with 1 None to allow all electrons to have a "pair" for cleaning

    ele_mu_pair_for_cleaning = ak.cartesian(
        [electrons.mask[electrons.preselected], mu_padded.mask[mu_padded.preselected]], nested=True
    )

    ele_for_cleaning, mu_for_cleaning = ak.unzip( ele_mu_pair_for_cleaning )

    electron_cleaning_dr = ak.where(
        (ak.is_none(mu_for_cleaning, axis=2) == 0) & (ak.is_none(ele_for_cleaning, axis=2) == 0),
            abs(ele_for_cleaning.delta_r(mu_for_cleaning)),
            electrons.preselected
    )

    electron_cleaning_mask = ak.min(electron_cleaning_dr, axis=2) > 0.30

    events.Electron = ak.with_field(events.Electron, electron_cleaning_mask & electrons.preselected, "cleaned")
    events.Electron = ak.with_field(events.Electron, electron_fakeable_mask & electron_cleaning_mask & electron_preselection_mask, "fakeable")
    events.Electron = ak.with_field(events.Electron, electron_tight_mask & electron_fakeable_mask & electron_cleaning_mask & electron_preselection_mask, "tight")

    events.Electron = ak.with_field(events.Electron, (getattr(electrons, 'genPartFlav', 0) == 1) | (getattr(electrons, 'genPartFlav', 0) == 15), "MC_Match")

    #NanoAOD -- 1 = prompt electron -- 15 = electron from prompt tau


def ak4_jet_selection(EventProcess):
    events = EventProcess.events
    #AK4 Jets
    ak4_jets = events.Jet
    muons = events.Muon
    electrons = events.Electron
    jetDeepJet_WP_loose = EventProcess.jetDeepJet_WP[0]
    jetDeepJet_WP_medium = EventProcess.jetDeepJet_WP[1]
    PFJetID = EventProcess.PFJetID
    isMC = EventProcess.isMC
    debug = EventProcess.debug
    if debug: print("Starting ak4 selection")

    #NanoAODv11 ak4_jets uses Puppi instead of CHS, so no more puId cut
    #Keep jets with central pt under 25 but JEC_up above 25???
    #https://gitlab.cern.ch/cms-hh-bbww/cms-hh-to-bbww/-/blob/master/Legacy/objects.md#22-ak4-jets
    ak4_jet_preselection_mask = (
        (ak4_jets.pt >= 25.0) & (abs(ak4_jets.eta) <= 2.4) &
        ((ak4_jets.jetId & PFJetID) > 0)
    )

    ak4_jets_loose_btag_mask = ak4_jets.btagDeepFlavB > jetDeepJet_WP_loose

    ak4_jets_medium_btag_mask = ak4_jets.btagDeepFlavB > jetDeepJet_WP_medium

    events.Jet = ak.with_field(events.Jet, ak4_jet_preselection_mask, "preselected")
    ak4_jets = events.Jet

    leptons_fakeable = ak.concatenate([electrons.mask[electrons.fakeable], muons.mask[muons.fakeable]], axis=1)
    #argsort fails if all values are none, fix by a all none check
    #Check if variables are none, then if all in the nested list are none, then if all in the unnested list are none
    if not ak.all(ak.all(ak.is_none(leptons_fakeable, axis=1), axis=1)):
        leptons_fakeable = leptons_fakeable[ak.argsort(leptons_fakeable.conept, ascending=False)]
    leptons_fakeable = ak.pad_none(leptons_fakeable, 1)

    ak4_jet_lep_pair_for_cleaning = ak.cartesian([ak4_jets.mask[ak4_jets.preselected], leptons_fakeable], nested=True)
    ak4_jet_for_cleaning, lep_for_cleaning = ak.unzip( ak4_jet_lep_pair_for_cleaning )

    ak4_jet_cleaning_dr_all = ak.fill_none(abs(ak4_jet_for_cleaning.delta_r(lep_for_cleaning)), True)
    ak4_jet_cleaning_mask_all = ak.min(ak4_jet_cleaning_dr_all, axis=2) > 0.40

    ak4_jet_cleaning_dr_single = ak.fill_none(abs(ak4_jet_for_cleaning.delta_r(lep_for_cleaning)), True)[:,:,0:1]
    ak4_jet_cleaning_mask_single = ak.min(ak4_jet_cleaning_dr_single, axis=2) > 0.40

    ak4_jet_cleaning_dr_double = ak.fill_none(abs(ak4_jet_for_cleaning.delta_r(lep_for_cleaning)), True)[:,:,0:2]
    ak4_jet_cleaning_mask_double = ak.min(ak4_jet_cleaning_dr_double, axis=2) > 0.40

    events.Jet = ak.with_field(events.Jet, ak4_jet_cleaning_mask_all & ak4_jets.preselected, "cleaned_all")
    events.Jet = ak.with_field(events.Jet, ak4_jet_cleaning_mask_single & ak4_jets.preselected, "cleaned_single")
    events.Jet = ak.with_field(events.Jet, ak4_jet_cleaning_mask_double & ak4_jets.preselected, "cleaned_double")

    ak4_jets = events.Jet

    events.Jet = ak.with_field(events.Jet, ak4_jets_loose_btag_mask & ak4_jets.cleaned_all, "loose_btag_all")
    events.Jet = ak.with_field(events.Jet, ak4_jets_loose_btag_mask & ak4_jets.cleaned_single, "loose_btag_single")
    events.Jet = ak.with_field(events.Jet, ak4_jets_loose_btag_mask & ak4_jets.cleaned_double, "loose_btag_double")

    events.Jet = ak.with_field(events.Jet, ak4_jets_medium_btag_mask & ak4_jets.cleaned_all, "medium_btag_all")
    events.Jet = ak.with_field(events.Jet, ak4_jets_medium_btag_mask & ak4_jets.cleaned_single, "medium_btag_single")
    events.Jet = ak.with_field(events.Jet, ak4_jets_medium_btag_mask & ak4_jets.cleaned_double, "medium_btag_double")


def ak8_jet_selection(EventProcess):
    events = EventProcess.events
    #AK8 Jets
    ak8_jets = events.FatJet
    muons = events.Muon
    electrons = events.Electron
    ak8_btagDeepB_WP_medium = EventProcess.ak8_btagDeepB_WP[1]
    PFJetID = EventProcess.PFJetID
    isMC = EventProcess.isMC
    debug = EventProcess.debug
    if debug: print("Starting ak8 selection")


    ak8_jets.tau2overtau1 = ak.where(
        (ak.is_none(ak8_jets, axis=1) == 0) & (ak.is_none(ak8_jets.tau2, axis=1) == 0) & (ak.is_none(ak8_jets.tau1, axis=1) == 0),
            ak8_jets.tau2 / ak8_jets.tau1,
            10.0
    )

    ak8_jet_preselection_mask = (
        (ak.is_none(ak8_jets.subjet1) == 0) & (ak.is_none(ak8_jets.subjet2) == 0) &
        (ak8_jets.subjet1.pt >= 20) & (abs(ak8_jets.subjet1.eta) <= 2.4) &
        (ak8_jets.subjet2.pt >= 20) & (abs(ak8_jets.subjet2.eta) <= 2.4) &
        ( (ak8_jets.jetId & PFJetID) > 0) & (ak8_jets.pt >= 200) &
        (abs(ak8_jets.eta) <= 2.4) & (ak8_jets.msoftdrop >= 30) & (ak8_jets.msoftdrop <= 210) &
        (ak8_jets.tau2 / ak8_jets.tau1 <= 0.75)
    )

    ak8_jet_btag_mask = (
        (ak8_jets.subjet1.btagDeepB > ak8_btagDeepB_WP_medium) & (ak8_jets.subjet1.pt >= 30)
        | #OR
        (ak8_jets.subjet2.btagDeepB > ak8_btagDeepB_WP_medium) & (ak8_jets.subjet2.pt >= 30)
    )

    events.FatJet = ak.with_field(events.FatJet, ak8_jet_preselection_mask, "preselected")
    ak8_jets = events.FatJet

    leptons_fakeable = ak.concatenate([electrons.mask[electrons.fakeable], muons.mask[muons.fakeable]], axis=1)
    #argsort fails if all values are none, fix by a all none check
    #Check if variables are none, then if all in the nested list are none, then if all in the unnested list are none
    if not ak.all(ak.all(ak.is_none(leptons_fakeable, axis=1), axis=1)):
        leptons_fakeable = leptons_fakeable[ak.argsort(leptons_fakeable.conept, ascending=False)]
    leptons_fakeable = ak.pad_none(leptons_fakeable, 1)

    ak8_jet_lep_pair_for_cleaning = ak.cartesian([ak8_jets.mask[ak8_jets.preselected], leptons_fakeable], nested=True)
    ak8_jet_for_cleaning, lep_for_cleaning = ak.unzip( ak8_jet_lep_pair_for_cleaning )

    ak8_jet_cleaning_dr_all = ak.fill_none(abs(ak8_jet_for_cleaning.delta_r(lep_for_cleaning)), True)
    ak8_jet_cleaning_mask_all = ak.min(ak8_jet_cleaning_dr_all, axis=2) > 0.80

    ak8_jet_cleaning_dr_single = ak8_jet_cleaning_dr_all[:,:,0:1]
    ak8_jet_cleaning_mask_single = ak.min(ak8_jet_cleaning_dr_single, axis=2) > 0.80

    ak8_jet_cleaning_dr_double = ak8_jet_cleaning_dr_all[:,:,0:2]
    ak8_jet_cleaning_mask_double = ak.min(ak8_jet_cleaning_dr_double, axis=2) > 0.80

    events.FatJet = ak.with_field(events.FatJet, ak8_jet_cleaning_mask_all & ak8_jets.preselected, "cleaned_all")
    events.FatJet = ak.with_field(events.FatJet, ak8_jet_cleaning_mask_single & ak8_jets.preselected, "cleaned_single")
    events.FatJet = ak.with_field(events.FatJet, ak8_jet_cleaning_mask_double & ak8_jets.preselected, "cleaned_double")
    ak8_jets = events.FatJet

    events.FatJet = ak.with_field(events.FatJet, ak8_jet_btag_mask & ak8_jets.cleaned_all, "btag_all")
    events.FatJet = ak.with_field(events.FatJet, ak8_jet_btag_mask & ak8_jets.cleaned_single, "btag_single")
    events.FatJet = ak.with_field(events.FatJet, ak8_jet_btag_mask & ak8_jets.cleaned_double, "btag_double")


def add_HT(EventProcess):
    events = EventProcess.events
    ak4_jets = events.Jet
    ak4_jets_pre = ak4_jets.mask[ak4_jets.preselected]

    ak4_jets_ptGt50 = ak4_jets_pre.mask[ak4_jets_pre.pt > 50]

    events["HT"] = ak.sum(ak4_jets_ptGt50.pt, axis=1)


def all_obj_selection(EventProcess):
    add_conept(EventProcess)
    link_jets(EventProcess)
    muon_selection(EventProcess)
    electron_selection(EventProcess)
    ak4_jet_selection(EventProcess)
    ak8_jet_selection(EventProcess)
    add_HT(EventProcess)
