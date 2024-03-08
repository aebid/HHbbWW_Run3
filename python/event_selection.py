import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
#import ROOT
from coffea.nanoevents.methods import vector

def increment_cutflow(events, cut, cutflow_name):
    events[cutflow_name] = ak.where(
        cut,
            (events[cutflow_name] + 1),
            events[cutflow_name]
    )

def single_lepton_category(EventProcess):
    #Pass MET filters
    #At least 1 fakeable lepton
    #If the leading cone-pT lepton is e (mu), pass single e (mu) trigger
    #cone-pt > 32 (25) for e (mu)
    #Invariant mass of each pair of preselected leptons (electrons NOT cleaned) must be greater than 12 GeV
    #Not more than 1 tight lepton - tight should be same as highest cone pT fakeable
    #Tau veto: no tau passing pt > 20, abs(eta) < 2.3, abs(dxy) <= 1000, abs(dz) <= 0.2, decay modes = {0, 1, 2, 10, 11}, and byMediumDeepTau2017v2VSjet, byVLooseDeepTau2017v2VSmu, byVVVLooseDeepTau2017v2VSe. Taus overlapping with fakeable electrons or fakeable muons within dR < 0.3 are not considered for the tau veto
    #No pair of same-flavor, opposite sign preselected leptons within 10 GeV of the Z mass
    #At least 1 medium btag (that can be on a AK8 jet): (#selJetsAK8_b >= 1 || #b-medium >= 1)
    #Minimal number of jets to construct an Hbb and admit an hadronic W with a missing jet: (#selJetsAK8_b == 0 && #selJetsAK4 >= 3) || (#selJetsAK8_b >= 1 && nJet_that_not_bb >= 1)
    events = EventProcess.events
    muons = events.Muon
    electrons = events.Electron
    taus = events.Tau
    ak4_jets = events.Jet
    ak8_jets = events.FatJet
    flag = events.Flag
    HLT = events.HLT
    Runyear = EventProcess.Runyear
    isMC = EventProcess.isMC
    debug = EventProcess.debug

    #Prepare leptons
    leptons_preselected = ak.concatenate([electrons.mask[electrons.preselected], muons.mask[muons.preselected]], axis=1)
    leptons_fakeable = ak.concatenate([electrons.mask[electrons.fakeable], muons.mask[muons.fakeable]], axis=1)
    leptons_tight = ak.concatenate([electrons.mask[electrons.tight], muons.mask[muons.tight]], axis=1)

    if ak.any(leptons_preselected): #Required in case no leptons available, can happen with data
        leptons_preselected = leptons_preselected[ak.argsort(leptons_preselected.conept, axis=1, ascending=False)]
    if ak.any(leptons_fakeable):
        leptons_fakeable = leptons_fakeable[ak.argsort(leptons_fakeable.conept, axis=1, ascending=False)]
    if ak.any(leptons_tight):
        leptons_tight = leptons_tight[ak.argsort(leptons_tight.conept, axis=1, ascending=False)]


    leading_leptons = ak.pad_none(leptons_fakeable, 1)[:,0]


    #We break the cuts into separate steps for the cutflow
    #Step 1 -- Require at least 1 fakeable (or tight) lepton
    #Step 2 -- Require MET filters
    #Step 3 -- Leading lepton cone-pT for El (Mu) >= 32.0 (25.0)
    #Step 4 -- Z mass and invariant mass cuts
    #Step 5 -- HLT Cuts
    #   If El, pass El trigger
    #   If Mu, pass Mu trigger
    #Step 6 -- MC match for leading lepton
    #Step 7 -- Require no more than 1 tight lepton (must be leading)
    #Step 8 -- Tau veto
    #Step 9 -- 1 or more btagged ak8_jets or 1 or more btagged ak4_jets
    #Step 10 -- Categories

    if debug: print("N triggered events: " , len(events))

    events["single_cutflow"] = np.zeros_like(events.run)

    events["is_e"] = (abs(leading_leptons.pdgId) == 11)
    events["is_m"] = (abs(leading_leptons.pdgId) == 13)

    #Require at least 1 fakeable (or tight) lepton
    one_fakeable_lepton = ak.fill_none(ak.sum(leptons_fakeable.fakeable, axis=1) >= 1, False)
    events["AtLeastOneFakeableLepSingle"] = one_fakeable_lepton
    #single_step1_mask = ak.fill_none(one_fakeable_lepton, False)

    #Require MET filters
    #These filters are recommended from the JetMET POG (Currently use 2018, JetMET says Run2 filters are good to use) https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#UL_data
    MET_filters = ak.fill_none((flag.goodVertices) & (flag.globalSuperTightHalo2016Filter) & (flag.HBHENoiseFilter) & (flag.HBHENoiseIsoFilter) & (flag.EcalDeadCellTriggerPrimitiveFilter) & (flag.BadPFMuonFilter) & (flag.ecalBadCalibFilter) & (flag.eeBadScFilter), False)
    events["PassesMETFiltersSingle"] = MET_filters

    #Leading lepton cone-pT for El (Mu) >= 32.0 (25.0)
    cone_pt_cuts = ak.fill_none(ak.where(
        abs(leading_leptons.pdgId) == 11,
            leading_leptons.conept >= 32.0,
            ak.where(
                abs(leading_leptons.pdgId) == 13,
                    leading_leptons.conept >= 25.0,
                    False
            )
    ), False)
    events["LeadLeptonConePtCutSingle"] = cone_pt_cuts

    #Z mass and invariant mass cuts
    #No pair of same-flavor, opposite-sign preselcted leptons within 10 GeV of the Z mass (91.1876)
    #Invariant mass of each pair of preselected leptons (electrons not cleaned) must be greater than 12 GeV
    lep_pairs_for_Zmass_and_Invarmass = ak.combinations(leptons_preselected, 2)
    first_leps, second_leps = ak.unzip(lep_pairs_for_Zmass_and_Invarmass)

    lep1_lorentz_vec = ak.zip(
        {
            "pt": ak.fill_none(first_leps.pt, 0.0),
            "eta": ak.fill_none(first_leps.eta, 0.0),
            "phi": ak.fill_none(first_leps.phi, 0.0),
            "mass": ak.fill_none(first_leps.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    lep2_lorentz_vec = ak.zip(
        {
            "pt": ak.fill_none(second_leps.pt, 0.0),
            "eta": ak.fill_none(second_leps.eta, 0.0),
            "phi": ak.fill_none(second_leps.phi, 0.0),
            "mass": ak.fill_none(second_leps.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )


    Invariant_mass_cut = ak.fill_none(ak.all(
        (
            ((lep1_lorentz_vec + lep2_lorentz_vec).mass > 12.0) |
            ak.is_none(first_leps, axis = 1) |
            ak.is_none(second_leps, axis = 1)
        ), axis = 1
    ), False)

    events["InvarMassCutSingle"] = Invariant_mass_cut


    Zmass_cut = ak.fill_none(ak.any(
        (
            (abs(ak.fill_none(first_leps.pdgId, 0)) == abs(ak.fill_none(second_leps.pdgId, 0))) &
            (ak.fill_none(first_leps.charge, 0) != ak.fill_none(second_leps.charge, 0)) &
            (abs((lep1_lorentz_vec + lep2_lorentz_vec).mass - 91.1876) < 10.0)
        ), axis = 1
    ) == 0, False)

    events["ZMassCutSingle"] = Zmass_cut

    #HLT Cuts
    #   If Mu, pass Mu trigger
    #   If El, pass El trigger
    HLT_cut = ak.fill_none(((events.is_m & EventProcess.muon_trigger_cuts) | (events.is_e & EventProcess.electron_trigger_cuts)), False)

    events["PassesHLTCutsSingle"] = HLT_cut



    #MC match for leading and subleading leptons
    leading_MC_match = leading_leptons.MC_Match | (isMC == False)

    single_step6_mask = ak.fill_none(leading_MC_match, False)


    #No more than 1 tight leptons AND should be the same as leading lepton
    n_tight_leptons = ak.sum(leptons_tight.tight, axis=1)

    tight_lep_cut = ak.fill_none(((n_tight_leptons == 0) | ((n_tight_leptons == 1) & (leading_leptons.tight))), False)

    events["AtMostOneTightLepSingle"] = tight_lep_cut


    #Tau veto: no tau passing pt>20, abs(eta) < 2.3, abs(dxy) <= 1000, abs(dz) <= 0.2, "decayModeFindingNewDMs", decay modes = {0, 1, 2, 10, 11}, and "byMediumDeepTau2017v2VSjet", "byVLooseDeepTau2017v2VSmu", "byVVVLooseDeepTau2017v2VSe". Taus overlapping with fakeable electrons or fakeable muons within dR < 0.3 are not considered for the tau veto
    #False -> Gets Removed : True -> Passes veto
    tau_veto_pairs = ak.cartesian([taus, leptons_fakeable], nested=True)
    taus_for_veto, leps_for_veto = ak.unzip(tau_veto_pairs)

    tau_veto_cleaning = ak.min(abs(taus_for_veto.delta_r(leps_for_veto)), axis=2) >= 0.3

    tau_veto_selection = (
    (taus.pt > 20) & (abs(taus.eta) < 2.3) & (abs(taus.dxy) <= 1000.0) & (abs(taus.dz) <= 0.2) & (getattr(taus, 'idDecayModeNewDMs', False) | getattr(taus, 'idDecayModeOldDMs', False)) &
    (
        (taus.decayMode == 0) | (taus.decayMode == 1) | (taus.decayMode == 2) | (taus.decayMode == 10) | (taus.decayMode == 11)
    ) &
    (taus.idDeepTau2017v2p1VSjet >= 16) & (taus.idDeepTau2017v2p1VSmu >= 1) & (taus.idDeepTau2017v2p1VSe >= 1)
    )

    tau_veto = ak.fill_none(ak.any(tau_veto_cleaning & tau_veto_selection, axis=1) == 0, False)

    events["TauVetoSingle"] = tau_veto


    #Jet cuts
    #1 or more btagged ak8_jets or 1 or more btagged ak4_jets
    one_btagged_jet = ak.fill_none((ak.sum(ak4_jets.medium_btag_single, axis=1) >= 1) | (ak.sum(ak8_jets.btag_single, axis=1) >= 1), False)

    events["AtLeastOneBJetSingle"] = one_btagged_jet

    #Count ak4 jets that are dR 1.2 away from btagged ak8 jets
    #Require either:
    #   0 ak8 btagged jets and 3 or more cleaned ak4 jets
    #   or
    #   1 or more ak8 btagged jets and 1 or more cleaned ak4 jets 1.2dR away from an ak8 bjet
    #ak8_jets_btag_single = ak8_jets.mask[ak8_jets.btag_single]
    ak8_jets_btag_single = ak8_jets[ak8_jets.btag_single]

    ak8_jets_btag_single_sorted = ak8_jets_btag_single
    if ak.any(ak8_jets_btag_single): #Required in case no ak8 jets available, can happen with data
        ak8_jets_btag_single_sorted = ak8_jets_btag_single[ak.argsort(ak8_jets_btag_single.pt, axis=1, ascending=False)]

    ak8_jets_btag_single_sorted_padded = ak.pad_none(ak8_jets_btag_single_sorted, 1)

    ak4_jets_padded = ak.pad_none(ak4_jets, 1)

    clean_ak4_jets_btagged_ak8_jets = ak.cartesian([ak4_jets_padded.mask[ak4_jets_padded.cleaned_single], ak8_jets_btag_single_sorted_padded], nested=True)

    clean_ak4_for_veto, btag_ak8_for_veto = ak.unzip(clean_ak4_jets_btagged_ak8_jets)

    ak4_jets.jets_that_not_bb = ak.any(abs(clean_ak4_for_veto.delta_r(btag_ak8_for_veto)) > 1.2, axis=2)
    n_jets_that_not_bb = ak.sum(ak4_jets.jets_that_not_bb, axis=1)


    jet_btag_veto = ak.fill_none((
        ( (n_jets_that_not_bb >= 1) & (ak.sum(ak8_jets.btag_single, axis=1) >= 1) )
        |
        ( (ak.sum(ak8_jets.btag_single, axis=1) == 0) & (ak.sum(ak4_jets.cleaned_single, axis=1) >= 3) )
    ), False)

    events["EnoughNonBJetsSingle"] = jet_btag_veto


    events["single_lepton"] = one_fakeable_lepton
    if debug: print("N single events step1: ", ak.sum(events.single_lepton), " Require at least 1 fakeable (or tight) lepton")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = MET_filters & events.single_lepton
    if debug: print("N single events step2: ", ak.sum(events.single_lepton), " Require MET filters")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = cone_pt_cuts & events.single_lepton
    if debug: print("N single events step3: ", ak.sum(events.single_lepton), " Leading lepton cone-pT for El (Mu) >= 32.0 (25.0)")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = Invariant_mass_cut & Zmass_cut & events.single_lepton
    if debug: print("N single events step4: ", ak.sum(events.single_lepton), " Z mass and invariant mass cuts")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = HLT_cut & events.single_lepton
    if debug: print("N single events step5: ", ak.sum(events.single_lepton), " HLT Cuts")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    #Asking for the MC Match was a bad idea, we want to keep both cases and just have a lepton bool for match or not
    #events["single_lepton"] = single_step6_mask & events.single_lepton
    #if debug: print("N single events step6: ", ak.sum(events.single_lepton), " MC match for leading lepton")
    #increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = tight_lep_cut & events.single_lepton
    if debug: print("N single events step7: ", ak.sum(events.single_lepton), " Require no more than 1 tight lepton")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = tau_veto & events.single_lepton
    if debug: print("N single events step8: ", ak.sum(events.single_lepton), " Tau veto")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = one_btagged_jet & events.single_lepton
    if debug: print("N single events step9: ", ak.sum(events.single_lepton), " 1 or more btagged ak8_jets or 1 or more btagged ak4_jets")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["single_lepton"] = jet_btag_veto & events.single_lepton
    if debug: print("N single events step10: ", ak.sum(events.single_lepton), " Categories")
    increment_cutflow(events, events.single_lepton, "single_cutflow")

    events["Single_HbbFat_WjjRes_AllReco"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) >= 1) & (n_jets_that_not_bb >= 2), False)

    events["Single_HbbFat_WjjRes_MissJet"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) >= 1) & (n_jets_that_not_bb < 2), False)

    events["Single_Res_allReco_2b"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) == 0) & (ak.sum(ak4_jets.cleaned_single, axis=1) >= 4) & (ak.sum(ak4_jets.medium_btag_single, axis=1) > 1), False)

    events["Single_Res_allReco_1b"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) == 0) & (ak.sum(ak4_jets.cleaned_single, axis=1) >= 4) & (ak.sum(ak4_jets.medium_btag_single, axis=1) == 1), False)

    events["Single_Res_MissWJet_2b"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) == 0) & (ak.sum(ak4_jets.cleaned_single, axis=1) < 4) & (ak.sum(ak4_jets.medium_btag_single, axis=1) > 1), False)

    events["Single_Res_MissWJet_1b"] = ak.fill_none((events.single_lepton) & (ak.sum(ak8_jets.btag_single, axis=1) == 0) & (ak.sum(ak4_jets.cleaned_single, axis=1) < 4) & (ak.sum(ak4_jets.medium_btag_single, axis=1) == 1), False)

    events["Single_Signal"] = ak.fill_none((events.single_lepton) & ((ak.sum(leptons_tight.tight, axis=1) == 1) & (leading_leptons.tight)), False)

    events["Single_Fake"] = ak.fill_none((events.single_lepton) & ((leading_leptons.tight) == 0), False)


    if debug:
        print("Single HbbFat_WjjRes_AllReco: ", events.Single_HbbFat_WjjRes_AllReco, ak.sum(events.Single_HbbFat_WjjRes_AllReco))
        print("Single HbbFat_WjjRes_MissJet: ", events.Single_HbbFat_WjjRes_MissJet, ak.sum(events.Single_HbbFat_WjjRes_MissJet))
        print("Single Res_allReco_2b: ", events.Single_Res_allReco_2b, ak.sum(events.Single_Res_allReco_2b))
        print("Single Res_allReco_1b: ", events.Single_Res_allReco_1b, ak.sum(events.Single_Res_allReco_1b))
        print("Single Res_MissWJet_2b: ", events.Single_Res_MissWJet_2b, ak.sum(events.Single_Res_MissWJet_2b))
        print("Single Res_MissWJet_1b: ", events.Single_Res_MissWJet_1b, ak.sum(events.Single_Res_MissWJet_1b))
        print("Single Signal: ", events.Single_Signal, ak.sum(events.Single_Signal))
        print("Single Fake: ", events.Single_Fake, ak.sum(events.Single_Fake))






def double_lepton_category(EventProcess):
    #Pass MET filters
    #At least 2 fakeable leptons (choose the leading 2 in cone pT in the following)
    #if both fakeable leptons are electrons, the event needs to pass either the single electron or the double electron trigger; if both fakeable leptons are muons, the event needs to pass either the single muon or the double muon trigger; if one fakeable lepton is an electron and the other fakeable lepton is a muon, the event needs to pass either the single electron or the single muon or the muon+electron trigger
    #cone pT > 25 for the leading fakeable lepton and cone pT > 15 GeV for the subleading fakeable lepton
    #The 2 fakeable leptons must have opposite charge
    #No pair of same-flavor, opposite-sign preselected leptons within 10 GeV of the Z mass
    #The event needs to pass the selection in either the boosted or the resolved category:
    #In order for the event to pass the selection in the boosted category, it needs to contain at least one b-tagged Ak8 jet (see object definition)
    #In order for the event to pass the selection in the resolved category, it needs to contain at least 2 AK4 jets, of which at least one passes the medium working-point of the DeepJet b-tagging algorithm
    #The two categories are mutually exclusive. The higher priority is given to the boosted category, i.e. events satisfying the criteria for the boosted category are not considered for the resolved category.
    #The leading and subleading fakeable lepton both pass the tight lepton selection criteria
    #In MC, require MC matching of the leading and subleading fakeable lepton
    #Either the leading fakeable lepton, the subleading fakeable lepton or both fail the tight lepton selection criteria
    #In MC, require MC matching of the leading and subleading fakeable lepton
    events = EventProcess.events
    muons = events.Muon
    electrons = events.Electron
    taus = events.Tau
    ak4_jets = events.Jet
    ak8_jets = events.FatJet
    flag = events.Flag
    HLT = events.HLT
    Runyear = EventProcess.Runyear
    isMC = EventProcess.isMC
    debug = EventProcess.debug

    leptons_preselected = ak.concatenate([electrons.mask[electrons.preselected], muons.mask[muons.preselected]], axis=1)
    leptons_fakeable = ak.concatenate([electrons.mask[electrons.fakeable], muons.mask[muons.fakeable]], axis=1)
    leptons_tight = ak.concatenate([electrons.mask[electrons.tight], muons.mask[muons.tight]], axis=1)


    if not ak.all(ak.all(ak.is_none(leptons_preselected, axis=1), axis=1)):
        leptons_preselected = leptons_preselected[ak.argsort(leptons_preselected.conept, axis=1, ascending=False)]
    if not ak.all(ak.all(ak.is_none(leptons_fakeable, axis=1), axis=1)):
        leptons_fakeable = leptons_fakeable[ak.argsort(leptons_fakeable.conept, axis=1, ascending=False)]
    if not ak.all(ak.all(ak.is_none(leptons_tight, axis=1), axis=1)):
        leptons_tight = leptons_tight[ak.argsort(leptons_tight.conept, axis=1, ascending=False)]

    leading_leptons = ak.pad_none(leptons_fakeable, 2)[:,0]
    subleading_leptons = ak.pad_none(leptons_fakeable, 2)[:,1]

    #We break the cuts into separate steps for the cutflow
    #Step 1 -- Require at least 2 fakeable (or tight) leptons
    #Step 2 -- Require MET filters
    #Step 3 -- Leading lepton cone-pT > 25.0, subleading lepton cone-pT > 15.0, leading lepton charge != subleading lepton charge
    #Step 4 -- Z mass and invariant mass cuts
    #   No pair of same-flavor, opposite-sign preselcted leptons within 10 GeV of the Z mass (91.1876)
    #   Invariant mass of each pair of preselected leptons (electrons not cleaned) must be greater than 12 GeV
    #Step 5 -- HLT Cuts
    #   If MuMu, pass MuMu or Mu trigger
    #   If ElEl, pass ElEl or El trigger
    #   If MuEl, pass MuEl or El or Mu trigger
    #Step 6 -- MC match for leading and subleading leptons
    #Step 7 -- No more than 2 tight leptons
    #Step 8 -- Put into category
    #   HbbFat -- n_ak8 cleaned >= 1 & leading_ak8.btag
    #   res_1b -- n_ak4 cleaned >= 2 & n_ak4.medium_btag == 1
    #   res_2b -- n_ak4 cleaned >= 2 & n_ak4.medium_btag == 2
    #   Since boosted/resolved isn't exclusive, priority is given as -- HbbFat > res_1b > res_2b

    if debug: print("N triggered events: " , len(events))

    events["double_cutflow"] = np.zeros_like(events.run)

    events["is_ee"] = (abs(leading_leptons.pdgId) == 11) & (abs(subleading_leptons.pdgId) == 11)
    events["is_mm"] = (abs(leading_leptons.pdgId) == 13) & (abs(subleading_leptons.pdgId) == 13)
    events["is_em"] = (abs(leading_leptons.pdgId) == 11) & (abs(subleading_leptons.pdgId) == 13)
    events["is_me"] = (abs(leading_leptons.pdgId) == 13) & (abs(subleading_leptons.pdgId) == 11)

    #Require at least 2 fakeable (or tight) leptons
    two_fakeable_lepton = ak.fill_none(ak.sum(leptons_fakeable.fakeable, axis=1) >= 2, False)

    events["AtLeastTwoFakeableLepsDouble"] = two_fakeable_lepton


    #Require MET filters
    #These filters are recommended from the JetMET POG (Currently use 2018, JetMET says Run2 filters are good to use) https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2#UL_data
    MET_filters = ak.fill_none((flag.goodVertices) & (flag.globalSuperTightHalo2016Filter) & (flag.HBHENoiseFilter) & (flag.HBHENoiseIsoFilter) & (flag.EcalDeadCellTriggerPrimitiveFilter) & (flag.BadPFMuonFilter) & (flag.ecalBadCalibFilter) & (flag.eeBadScFilter), False)

    events["PassesMETFiltersDouble"] = MET_filters


    #Leading lepton cone-pT > 25.0, subleading lepton cone-pT > 15.0, leading lepton charge != subleading lepton charge
    cone_pt_cuts = ak.fill_none((leading_leptons.conept > 25.0) & (subleading_leptons.conept > 15.0), False)
    charge_cuts = ak.fill_none((leading_leptons.charge != subleading_leptons.charge), False)

    events["LeadSubleadLeptonConePtCutDouble"] = cone_pt_cuts
    events["LeadSubleadChargeCutDouble"] = charge_cuts


    #Z mass and invariant mass cuts
    #No pair of same-flavor, opposite-sign preselcted leptons within 10 GeV of the Z mass (91.1876)
    #Invariant mass of each pair of preselected leptons (electrons not cleaned) must be greater than 12 GeV
    lep_pairs_for_Zmass_and_Invarmass = ak.combinations(leptons_preselected, 2)
    first_leps, second_leps = ak.unzip(lep_pairs_for_Zmass_and_Invarmass)

    lep1_lorentz_vec = ak.zip(
        {
            "pt": ak.fill_none(first_leps.pt, 0.0),
            "eta": ak.fill_none(first_leps.eta, 0.0),
            "phi": ak.fill_none(first_leps.phi, 0.0),
            "mass": ak.fill_none(first_leps.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    lep2_lorentz_vec = ak.zip(
        {
            "pt": ak.fill_none(second_leps.pt, 0.0),
            "eta": ak.fill_none(second_leps.eta, 0.0),
            "phi": ak.fill_none(second_leps.phi, 0.0),
            "mass": ak.fill_none(second_leps.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )


    Invariant_mass_cut = ak.fill_none(ak.all(
        (
            ((lep1_lorentz_vec + lep2_lorentz_vec).mass > 12.0) |
            ak.is_none(first_leps, axis = 1) |
            ak.is_none(second_leps, axis = 1)
        ), axis = 1
    ), False)
    Zmass_cut = ak.fill_none(ak.any(
        (
            (abs(ak.fill_none(first_leps.pdgId, 0)) == abs(ak.fill_none(second_leps.pdgId, 0))) &
            (ak.fill_none(first_leps.charge, 0) != ak.fill_none(second_leps.charge, 0)) &
            (abs((lep1_lorentz_vec + lep2_lorentz_vec).mass - 91.1876) < 10.0)
        ), axis = 1
    ) == 0, False)


    lep_pairs_for_Zmass_fakeable = ak.combinations(leptons_fakeable, 2)
    first_leps_fakeable, second_leps_fakeable = ak.unzip(lep_pairs_for_Zmass_fakeable)

    lep1_lorentz_vec_fakeable = ak.zip(
        {
            "pt": ak.fill_none(first_leps_fakeable.pt, 0.0),
            "eta": ak.fill_none(first_leps_fakeable.eta, 0.0),
            "phi": ak.fill_none(first_leps_fakeable.phi, 0.0),
            "mass": ak.fill_none(first_leps_fakeable.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    lep2_lorentz_vec_fakeable = ak.zip(
        {
            "pt": ak.fill_none(second_leps_fakeable.pt, 0.0),
            "eta": ak.fill_none(second_leps_fakeable.eta, 0.0),
            "phi": ak.fill_none(second_leps_fakeable.phi, 0.0),
            "mass": ak.fill_none(second_leps_fakeable.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    Zmass_fakeable_cut = ak.any(
        (
            (abs(ak.fill_none(first_leps_fakeable.pdgId, 0)) == abs(ak.fill_none(second_leps_fakeable.pdgId, 0))) &
            (ak.fill_none(first_leps_fakeable.charge, 0) != ak.fill_none(second_leps_fakeable.charge, 0)) &
            (abs((lep1_lorentz_vec_fakeable + lep2_lorentz_vec_fakeable).mass - 91.1876) < 10.0)
        ), axis = 1
    ) == 0


    lep_pairs_for_Zmass_tight = ak.combinations(leptons_tight, 2)
    first_leps_tight, second_leps_tight = ak.unzip(lep_pairs_for_Zmass_tight)

    lep1_lorentz_vec_tight = ak.zip(
        {
            "pt": ak.fill_none(first_leps_tight.pt, 0.0),
            "eta": ak.fill_none(first_leps_tight.eta, 0.0),
            "phi": ak.fill_none(first_leps_tight.phi, 0.0),
            "mass": ak.fill_none(first_leps_tight.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    lep2_lorentz_vec_tight = ak.zip(
        {
            "pt": ak.fill_none(second_leps_tight.pt, 0.0),
            "eta": ak.fill_none(second_leps_tight.eta, 0.0),
            "phi": ak.fill_none(second_leps_tight.phi, 0.0),
            "mass": ak.fill_none(second_leps_tight.mass, 0.0),
        },
        with_name="PtEtaPhiMLorentzVector",
        behavior=vector.behavior,
    )

    Zmass_tight_cut = ak.any(
        (
            (abs(ak.fill_none(first_leps_tight.pdgId, 0)) == abs(ak.fill_none(second_leps_tight.pdgId, 0))) &
            (ak.fill_none(first_leps_tight.charge, 0) != ak.fill_none(second_leps_tight.charge, 0)) &
            (abs((lep1_lorentz_vec_tight + lep2_lorentz_vec_tight).mass - 91.1876) < 10.0)
        ), axis = 1
    ) == 0


    events["ZMassCutDouble"] = Zmass_cut
    events["InvarMassCutDouble"] = Invariant_mass_cut



    #double_step4_mask = ak.fill_none(Invariant_mass_cut & Zmass_cut, False)
    events["Zveto"] = ak.fill_none(Zmass_cut, False) #Required extra event level bool in case of DY Estimation
    events["Zveto_fakeable"] = ak.fill_none(Zmass_fakeable_cut, False) #Alexei thinks maybe we are too loose doing Zmass cut with preselected, upped to fakeable
    events["Zveto_tight"] = ak.fill_none(Zmass_tight_cut, False) #Alexei thinks maybe we are too loose doing Zmass cut with preselected, upped to tight
    #For DY Estimation we need to turn off Zmass cut and the nBJets cut (ABCD method over M_{ll} and nBJets), so we separate them


    #HLT Cuts
    #If MuMu, pass MuMu or Mu trigger
    #If ElEl, pass ElEl or El trigger
    #If MuEl, pass MuEl or El or Mu trigger
    HLT_cut = ak.fill_none(ak.where(
        events.is_mm,
            EventProcess.double_muon_trigger_cuts | EventProcess.muon_trigger_cuts,
            ak.where(
                events.is_ee,
                    EventProcess.double_electron_trigger_cuts | EventProcess.electron_trigger_cuts,
                    ak.where(
                        (events.is_em | events.is_me),
                            EventProcess.muon_electron_trigger_cuts | EventProcess.electron_trigger_cuts | EventProcess.muon_trigger_cuts,
                            False
                    )
            )
    ), False)

    events["PassesHLTCutsDouble"] = HLT_cut



    #MC match for leading and subleading leptons
    leading_MC_match = leading_leptons.MC_Match | (isMC == False)
    subleading_MC_match = subleading_leptons.MC_Match | (isMC == False)

    double_step6_mask = ak.fill_none(leading_MC_match & subleading_MC_match, False)



    #No more than 2 tight leptons
    n_tight_leptons = ak.sum(leptons_tight.tight, axis=1)
    two_tight_leptons = ak.fill_none(n_tight_leptons <= 2, False)

    events["AtMostTwoTightLepsDouble"] = two_tight_leptons


    #Put into category
    #HbbFat -- n_ak8 cleaned >= 1 & leading_ak8.btag
    #res_1b -- n_ak4 cleaned >= 2 & n_ak4.medium_btag == 1
    #res_2b -- n_ak4 cleaned >= 2 & n_ak4.medium_btag == 2
    #Since boosted/resolved isn't exclusive, priority is given as -- HbbFat > res_1b > res_2b
    cleaned_ak8_jets = ak8_jets.mask[ak8_jets.cleaned_double]
    cleaned_ak8_jets_sorted = cleaned_ak8_jets
    if ak.any(cleaned_ak8_jets_sorted): #Required in case no ak8 jets available, can happen with data
        cleaned_ak8_jets_sorted = cleaned_ak8_jets[ak.argsort(cleaned_ak8_jets.pt, axis=1, ascending=False)]
    leading_ak8_jet_cleaned = ak.pad_none(cleaned_ak8_jets_sorted, 1)[:,0]

    double_hbbfat_cut = ak.fill_none((ak.sum(ak8_jets.cleaned_double, axis=1) >= 1) & (leading_ak8_jet_cleaned.btag_double), False)
    double_res_0b_cut = ak.fill_none((ak.sum(ak4_jets.cleaned_double, axis=1) >= 2) & (ak.sum(ak4_jets.medium_btag_double, axis=1) == 0), False)
    double_res_1b_cut = ak.fill_none((ak.sum(ak4_jets.cleaned_double, axis=1) >= 2) & (ak.sum(ak4_jets.medium_btag_double, axis=1) == 1), False)
    double_res_2b_cut = ak.fill_none((ak.sum(ak4_jets.cleaned_double, axis=1) >= 2) & (ak.sum(ak4_jets.medium_btag_double, axis=1) >= 2), False)

    enough_jets = ak.fill_none((double_hbbfat_cut) | (double_res_1b_cut) | (double_res_2b_cut), False)
    events["EnoughJetsDouble"] = enough_jets

    #For DY Estimation we need to turn off Zmass cut and the nBJets cut (ABCD method over M_{ll} and nBJets)
    #We still want to require the base jets (1 ak8 or 2 ak4)
    events["nBjets_passDouble"] = ak.fill_none((double_hbbfat_cut) | (double_res_1b_cut) | (double_res_2b_cut), False)
    #Required extra event level bool in case of DY Estimation


    events["double_lepton"] = two_fakeable_lepton
    if debug: print("N double events step1: ", ak.sum(events.double_lepton), " Require at least 2 fakeable (or tight) leptons")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["double_lepton"] = MET_filters & events.double_lepton
    if debug: print("N double events step2: ", ak.sum(events.double_lepton), " Require MET filters")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["double_lepton"] = cone_pt_cuts & charge_cuts & events.double_lepton
    if debug: print("N double events step3: ", ak.sum(events.double_lepton), " Leading and Subleading lep cuts")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    #events["double_lepton"] = Zmass_cut & Invariant_mass_cut & events.double_lepton
    events["double_lepton"] = Zmass_cut & Invariant_mass_cut & events.double_lepton
    if debug: print("N double events step4: ", ak.sum(events.double_lepton), " Z mass and Invariant mass cuts")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["double_lepton"] = HLT_cut & events.double_lepton
    if debug: print("N double events step5: ", ak.sum(events.double_lepton), " HLT Cuts")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    #Asking for the MC Match was a bad idea, we want to keep both cases and just have a lepton bool for match or not
    #events["double_lepton"] = double_step6_mask & events.double_lepton
    #if debug: print("N double events step6: ", ak.sum(events.double_lepton), " MC match for leading and subleading leptons")
    #increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["double_lepton"] = two_tight_leptons & events.double_lepton
    if debug: print("N double events step7: ", ak.sum(events.double_lepton), " No more than 2 tight leptons")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["double_lepton"] = enough_jets & events.double_lepton
    if debug: print("N double events step8: ", ak.sum(events.double_lepton), " Categories")
    increment_cutflow(events, events.double_lepton, "double_cutflow")

    events["Double_HbbFat"] = ak.fill_none((events.double_lepton) & (double_hbbfat_cut), False)

    events["Double_Res_0b"] = ak.fill_none((events.double_lepton) & (events.Double_HbbFat == 0) & (double_res_0b_cut), False)

    events["Double_Res_1b"] = ak.fill_none((events.double_lepton) & (events.Double_HbbFat == 0) & (double_res_1b_cut), False)

    events["Double_Res_2b"] = ak.fill_none((events.double_lepton) & (events.Double_Res_1b == 0) & (events.Double_HbbFat == 0) & (double_res_2b_cut), False)


    events["Double_Signal"] = ak.fill_none((events.double_lepton) & ((leading_leptons.tight) & (subleading_leptons.tight)), False)

    events["Double_Fake"] = ak.fill_none((events.double_lepton) & (((leading_leptons.tight) == 0) | ((subleading_leptons.tight) == 0)), False)

    #Create full selection without the Zmass or nBJets cuts
    events["DY_Est_ZPeak_nB0"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & (Zmass_cut == 0) & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_0b_cut
    events["DY_Est_ZPeak_nB1"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & (Zmass_cut == 0) & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_1b_cut
    events["DY_Est_ZPeak_nB2"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & (Zmass_cut == 0) & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_2b_cut
    events["DY_Est_ZVeto_nB0"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & Zmass_cut & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_0b_cut
    events["DY_Est_ZVeto_nB1"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & Zmass_cut & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_1b_cut
    events["DY_Est_ZVeto_nB2"] = two_fakeable_lepton & MET_filters & cone_pt_cuts & charge_cuts & Zmass_cut & Invariant_mass_cut & HLT_cut & two_tight_leptons & double_res_2b_cut
    events["DY_Est_Evt"] = events.DY_Est_ZPeak_nB0 | events.DY_Est_ZPeak_nB1 | events.DY_Est_ZPeak_nB2 | events.DY_Est_ZVeto_nB0 | events.DY_Est_ZVeto_nB1 | events.DY_Est_ZVeto_nB2

    if debug:
        print("Double HbbFat: ", events.Double_HbbFat, ak.sum(events.Double_HbbFat))
        print("Double Res_1b: ", events.Double_Res_1b, ak.sum(events.Double_Res_1b))
        print("Double Res_2b: ", events.Double_Res_2b, ak.sum(events.Double_Res_2b))
        print("Double Signal: ", events.Double_Signal, ak.sum(events.Double_Signal))
        print("Double Fake: ", events.Double_Fake, ak.sum(events.Double_Fake))
