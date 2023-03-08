import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
import uproot
#import ROOT
from coffea.nanoevents.methods import vector


def create_df(EventProcess, outname):
    isMC = EventProcess.isMC
    debug = EventProcess.debug
    print("Creating save dicts")
    underflow_value = -999999.0
    underflow_value = 0.0

    events = EventProcess.events
    #Muons and Electrons are same for single/double
    muons = events.Muon
    muons["px"] = muons.px; muons["py"] = muons.py; muons["pz"] = muons.pz; muons["energy"] = muons.energy
    muons_pre = muons.mask[(muons.preselected)]
    muons_fake = muons.mask[(muons.preselected)]
    muons_tight = muons.mask[(muons.tight)]

    electrons = events.Electron
    electrons["px"] = electrons.px; electrons["py"] = electrons.py; electrons["pz"] = electrons.pz; electrons["energy"] = electrons.energy
    electrons_pre = electrons.mask[(electrons.preselected)]
    electrons_cleaned = electrons.mask[(electrons.cleaned)]
    electrons_fake = electrons.mask[(electrons.preselected)]
    electrons_tight = electrons.mask[(electrons.tight)]

    ak4_jets = ak.pad_none(events.Jet, 4)
    ak4_jets["px"] = ak4_jets.px; ak4_jets["py"] = ak4_jets.py; ak4_jets["pz"] = ak4_jets.pz; ak4_jets["energy"] = ak4_jets.energy
    ak4_jets_cleaned_single = ak4_jets.mask[(ak4_jets.cleaned_single)]
    ak4_jets_cleaned_double = ak4_jets.mask[(ak4_jets.cleaned_double)]

    ak8_jets = ak.pad_none(events.FatJet, 1)
    ak8_subjets = events.SubJet
    #ak8_jets["subjet1"] = ak8_subjets[ak8_jets.subJetIdx1]
    #ak8_jets["subjet2"] = ak8_subjets[ak8_jets.subJetIdx2]
    ak8_jets_cleaned_single = ak8_jets.mask[(ak8_jets.cleaned_single)]
    ak8_jets_cleaned_double = ak8_jets.mask[(ak8_jets.cleaned_double)]
    ak8_jets_cleaned_single_sorted = ak8_jets_cleaned_single[ak.argsort(ak8_jets_cleaned_single.pt, axis=1, ascending=False)]
    ak8_jets_cleaned_double_sorted = ak8_jets_cleaned_double[ak.argsort(ak8_jets_cleaned_double.pt, axis=1, ascending=False)]


    ls = events.luminosityBlock
    run = events.run
    met = events.MET

    leptons_fakeable = ak.concatenate([electrons_fake, muons_fake], axis=1)
    leptons_fakeable = ak.pad_none(leptons_fakeable[ak.argsort(leptons_fakeable.conept, ascending=False)], 2)
    lep0 = leptons_fakeable[:,0]
    lep1 = leptons_fakeable[:,1]


    #Take first 2 B tagged, then second 2 pT ordered (after removing bTags)
    ak4_jets_bsorted_double = ak4_jets_cleaned_double[ak.argsort(ak4_jets_cleaned_double.btagDeepFlavB, ascending=False)]
    ak4_jet0 = ak4_jets_bsorted_double[:,0]
    ak4_jet1 = ak4_jets_bsorted_double[:,1]
    tmp_ak4_slice_without_bjets = ak4_jets_bsorted_double[:,2:]
    ak4_jets_ptsorted_double = tmp_ak4_slice_without_bjets[ak.argsort(tmp_ak4_slice_without_bjets.pt, ascending=False)]
    ak4_jet2 = ak4_jets_ptsorted_double[:,0]
    ak4_jet3 = ak4_jets_ptsorted_double[:,1]


    ak8_jet0 = ak8_jets_cleaned_double_sorted[:,0]



    def make_lep_dict(lep, name):
        dict = {
            name+'_pdgId': np.array(ak.fill_none(lep.pdgId, underflow_value), dtype=np.int32),
            name+'_charge': np.array(ak.fill_none(lep.charge, underflow_value), dtype=np.int32),
            name+'_pt': np.array(ak.fill_none(lep.pt, underflow_value), dtype=np.float32),
            name+'_conept': np.array(ak.fill_none(lep.conept, underflow_value), dtype=np.float32),
            name+'_eta': np.array(ak.fill_none(lep.eta, underflow_value), dtype=np.float32),
            name+'_phi': np.array(ak.fill_none(lep.phi, underflow_value), dtype=np.float32),
            name+'_E': np.array(ak.fill_none(lep.energy, underflow_value), dtype=np.float32),
            name+'_px': np.array(ak.fill_none(lep.px, underflow_value), dtype=np.float32),
            name+'_py': np.array(ak.fill_none(lep.py, underflow_value), dtype=np.float32),
            name+'_pz': np.array(ak.fill_none(lep.pz, underflow_value), dtype=np.float32),
        }
        return dict

    def make_ak4_jet_dict(jet, name):
        dict = {
            name+'_pt': np.array(ak.fill_none(jet.pt, underflow_value), dtype=np.float32),
            name+'_eta': np.array(ak.fill_none(jet.eta, underflow_value), dtype=np.float32),
            name+'_phi': np.array(ak.fill_none(jet.phi, underflow_value), dtype=np.float32),
            name+'_E': np.array(ak.fill_none(jet.energy, underflow_value), dtype=np.float32),
            name+'_px': np.array(ak.fill_none(jet.px, underflow_value), dtype=np.float32),
            name+'_py': np.array(ak.fill_none(jet.py, underflow_value), dtype=np.float32),
            name+'_pz': np.array(ak.fill_none(jet.pz, underflow_value), dtype=np.float32),
            name+'_btagDeepFlavB': np.array(ak.fill_none(jet.btagDeepFlavB, underflow_value), dtype=np.float32),
        }
        if isMC:
            MC_dict = {
                name+"_jet_rescale_par": np.array(ak.fill_none(jet.par_jet_rescale, underflow_value), dtype=np.float32),
                name+"_JER_up_par": np.array(ak.fill_none(jet.par_JER_up, underflow_value), dtype=np.float32),
                name+"_JER_down_par": np.array(ak.fill_none(jet.par_JER_down, underflow_value), dtype=np.float32),
                name+"_JES_up_par": np.array(ak.fill_none(jet.par_JES_up, underflow_value), dtype=np.float32),
                name+"_JES_down_par": np.array(ak.fill_none(jet.par_JES_down, underflow_value), dtype=np.float32),
            }
            dict.update(MC_dict)
        return dict

    def make_ak8_jet_dict(jet, name):
        dict = {
            name+'_pt': np.array(ak.fill_none(jet.pt, underflow_value), dtype=np.float32),
            name+'_eta': np.array(ak.fill_none(jet.eta, underflow_value), dtype=np.float32),
            name+'_phi': np.array(ak.fill_none(jet.phi, underflow_value), dtype=np.float32),
            name+'_E': np.array(ak.fill_none(jet.energy, underflow_value), dtype=np.float32),
            name+'_px': np.array(ak.fill_none(jet.px, underflow_value), dtype=np.float32),
            name+'_py': np.array(ak.fill_none(jet.py, underflow_value), dtype=np.float32),
            name+'_pz': np.array(ak.fill_none(jet.pz, underflow_value), dtype=np.float32),
            name+'_tau1': np.array(ak.fill_none(jet.tau1, underflow_value), dtype=np.float32),
            name+'_tau2': np.array(ak.fill_none(jet.tau2, underflow_value), dtype=np.float32),
            name+'_tau3': np.array(ak.fill_none(jet.tau3, underflow_value), dtype=np.float32),
            name+'_tau4': np.array(ak.fill_none(jet.tau4, underflow_value), dtype=np.float32),
            name+'_msoftdrop': np.array(ak.fill_none(jet.msoftdrop, underflow_value), dtype=np.float32),

            name+'_subjet1_E': np.array(ak.fill_none(jet.subjet1.energy, underflow_value), dtype=np.float32),
            name+'_subjet1_px': np.array(ak.fill_none(jet.subjet1.px, underflow_value), dtype=np.float32),
            name+'_subjet1_py': np.array(ak.fill_none(jet.subjet1.py, underflow_value), dtype=np.float32),
            name+'_subjet1_pz': np.array(ak.fill_none(jet.subjet1.pz, underflow_value), dtype=np.float32),
            name+'_subjet1_pt': np.array(ak.fill_none(jet.subjet1.pt, underflow_value), dtype=np.float32),

            name+'_subjet2_E': np.array(ak.fill_none(jet.subjet2.energy, underflow_value), dtype=np.float32),
            name+'_subjet2_px': np.array(ak.fill_none(jet.subjet2.px, underflow_value), dtype=np.float32),
            name+'_subjet2_py': np.array(ak.fill_none(jet.subjet2.py, underflow_value), dtype=np.float32),
            name+'_subjet2_pz': np.array(ak.fill_none(jet.subjet2.pz, underflow_value), dtype=np.float32),
            name+'_subjet2_pt': np.array(ak.fill_none(jet.subjet2.pt, underflow_value), dtype=np.float32),
        }
        if isMC:
            MC_dict = {
                name+"_jet_rescale_par": np.array(ak.fill_none(jet.par_jet_rescale, underflow_value), dtype=np.float32),
                name+"_JER_up_par": np.array(ak.fill_none(jet.par_JER_up, underflow_value), dtype=np.float32),
                name+"_JER_down_par": np.array(ak.fill_none(jet.par_JER_down, underflow_value), dtype=np.float32),
                name+"_JES_up_par": np.array(ak.fill_none(jet.par_JES_up, underflow_value), dtype=np.float32),
                name+"_JES_down_par": np.array(ak.fill_none(jet.par_JES_down, underflow_value), dtype=np.float32),
            }
            dict.update(MC_dict)
        return dict

    def make_met_dict(met, name):
        dict = {
            name+'_E': np.array(ak.fill_none(met.px*0.0, underflow_value), dtype=np.float32), #Set to 0, but I want to keep the 'none' values
            name+'_px': np.array(ak.fill_none(met.px, underflow_value), dtype=np.float32),
            name+'_py': np.array(ak.fill_none(met.py, underflow_value), dtype=np.float32),
            name+'_pz': np.array(ak.fill_none(met.px*0.0, underflow_value), dtype=np.float32), #Set to 0, but I want to keep the 'none' values
            name+'_unclust_energy_up_x': np.array(ak.fill_none(met.MetUnclustEnUpDeltaX, underflow_value), dtype=np.float32),
            name+'_unclust_energy_up_y': np.array(ak.fill_none(met.MetUnclustEnUpDeltaY, underflow_value), dtype=np.float32),
            name+'_covXX': np.array(ak.fill_none(met.covXX, underflow_value), dtype=np.float32),
            name+'_covXY': np.array(ak.fill_none(met.covXY, underflow_value), dtype=np.float32),
            name+'_covYY': np.array(ak.fill_none(met.covYY, underflow_value), dtype=np.float32),
        }
        return dict

    event_dict_single = {
        #Event level information
        'event': np.array(events.event),
        'ls': np.array(ls),
        'run': np.array(run),
        'n_presel_muons': np.array(ak.sum(muons.preselected, axis=1), dtype=np.int32),
        'n_fakeable_muons': np.array(ak.sum(muons.fakeable, axis=1), dtype=np.int32),
        'n_tight_muons': np.array(ak.sum(muons.tight, axis=1), dtype=np.int32),

        'n_presel_electrons': np.array(ak.sum(electrons.preselected, axis=1), dtype=np.int32),
        'n_fakeable_electrons': np.array(ak.sum(electrons.fakeable, axis=1), dtype=np.int32),
        'n_tight_electrons': np.array(ak.sum(electrons.tight, axis=1), dtype=np.int32),

        'n_presel_ak4_jets': np.array(ak.sum(ak4_jets.preselected, axis=1), dtype=np.int32),
        'n_cleaned_ak4_jets': np.array(ak.sum(ak4_jets.cleaned_single, axis=1), dtype=np.int32),
        'n_loose_btag_ak4_jets': np.array(ak.sum(ak4_jets.loose_btag_single, axis=1), dtype=np.int32),
        'n_medium_btag_ak4_jets': np.array(ak.sum(ak4_jets.medium_btag_single, axis=1), dtype=np.int32),

        'n_presel_ak8_jets': np.array(ak.sum(ak8_jets.preselected, axis=1), dtype=np.int32),
        'n_cleaned_ak8_jets': np.array(ak.sum(ak8_jets.cleaned_single, axis=1), dtype=np.int32),
        'n_btag_ak8_jets': np.array(ak.sum(ak8_jets.btag_single, axis=1), dtype=np.int32),

        'Single_HbbFat_WjjRes_AllReco': np.array(events.Single_HbbFat_WjjRes_AllReco, dtype=np.int32),
        'Single_HbbFat_WjjRes_MissJet': np.array(events.Single_HbbFat_WjjRes_MissJet, dtype=np.int32),
        'Single_Res_allReco_2b': np.array(events.Single_Res_allReco_2b, dtype=np.int32),
        'Single_Res_allReco_1b': np.array(events.Single_Res_allReco_1b, dtype=np.int32),
        'Single_Res_MissWJet_2b': np.array(events.Single_Res_MissWJet_2b, dtype=np.int32),
        'Single_Res_MissWJet_1b': np.array(events.Single_Res_MissWJet_1b, dtype=np.int32),
        'Single_Signal': np.array(events.Single_Signal, dtype=np.int32),
        'Single_Fake': np.array(events.Single_Fake, dtype=np.int32),
        'single_category_cutflow': np.array(events.single_cutflow, dtype=np.int32),
        'single_is_e': np.array(ak.fill_none(events.is_e, False), dtype=np.int32),
        'single_is_m': np.array(ak.fill_none(events.is_m, False), dtype=np.int32),

        'dnn_truth_value': np.array(events.dnn_truth_value, dtype=np.int32),
    }

    event_dict_double = {
        #Event level information
        'event': np.array(events.event),
        'ls': np.array(ls),
        'run': np.array(run),
        'n_presel_muons': np.array(ak.sum(muons.preselected, axis=1), dtype=np.int32),
        'n_fakeable_muons': np.array(ak.sum(muons.fakeable, axis=1), dtype=np.int32),
        'n_tight_muons': np.array(ak.sum(muons.tight, axis=1), dtype=np.int32),

        'n_presel_electrons': np.array(ak.sum(electrons.preselected, axis=1), dtype=np.int32),
        'n_fakeable_electrons': np.array(ak.sum(electrons.fakeable, axis=1), dtype=np.int32),
        'n_tight_electrons': np.array(ak.sum(electrons.tight, axis=1), dtype=np.int32),

        'n_presel_ak4_jets': np.array(ak.sum(ak4_jets.preselected, axis=1), dtype=np.int32),
        'n_cleaned_ak4_jets': np.array(ak.sum(ak4_jets.cleaned_double, axis=1), dtype=np.int32),
        'n_loose_btag_ak4_jets': np.array(ak.sum(ak4_jets.loose_btag_double, axis=1), dtype=np.int32),
        'n_medium_btag_ak4_jets': np.array(ak.sum(ak4_jets.medium_btag_double, axis=1), dtype=np.int32),

        'n_presel_ak8_jets': np.array(ak.sum(ak8_jets.preselected, axis=1), dtype=np.int32),
        'n_cleaned_ak8_jets': np.array(ak.sum(ak8_jets.cleaned_double, axis=1), dtype=np.int32),
        'n_btag_ak8_jets': np.array(ak.sum(ak8_jets.btag_double, axis=1), dtype=np.int32),

        'Double_HbbFat': np.array(events.Double_HbbFat, dtype=np.int32),
        'Double_Res_1b': np.array(events.Double_Res_1b, dtype=np.int32),
        'Double_Res_2b': np.array(events.Double_Res_2b, dtype=np.int32),
        'Double_Signal': np.array(events.Double_Signal, dtype=np.int32),
        'Double_Fake': np.array(events.Double_Fake, dtype=np.int32),
        'double_category_cutflow': np.array(events.double_cutflow, dtype=np.int32),
        'double_is_ee': np.array(ak.fill_none(events.is_ee, False), dtype=np.int32),
        'double_is_mm': np.array(ak.fill_none(events.is_mm, False), dtype=np.int32),
        'double_is_em': np.array(ak.fill_none(events.is_em, False), dtype=np.int32),

        'dnn_truth_value': np.array(events.dnn_truth_value, dtype=np.int32),
    }


    lep0_dict = make_lep_dict(lep0, 'lep0')
    lep1_dict = make_lep_dict(lep1, 'lep1')

    lep_dict_double = lep0_dict | lep1_dict

    ak4_jet0_dict = make_ak4_jet_dict(ak4_jet0, 'ak4_jet0')
    ak4_jet1_dict = make_ak4_jet_dict(ak4_jet1, 'ak4_jet1')
    ak4_jet2_dict = make_ak4_jet_dict(ak4_jet2, 'ak4_jet2')
    ak4_jet3_dict = make_ak4_jet_dict(ak4_jet3, 'ak4_jet3')

    ak4_jet_dict_double = ak4_jet0_dict | ak4_jet1_dict | ak4_jet2_dict | ak4_jet3_dict

    ak8_jet0_dict = make_ak8_jet_dict(ak8_jet0, 'ak8_jet0')

    ak8_jet_dict_double = ak8_jet0_dict

    met_dict = make_met_dict(met, 'met')

    single_dicts = event_dict_single
    double_dicts = event_dict_double | lep_dict_double | ak4_jet_dict_double | ak8_jet_dict_double | met_dict


    if debug: import time
    if debug: print("Save the tree in uproot")
    if debug: startTime = time.time()
    outfile = uproot.recreate(outname)
    outfile["Single_Tree"] = single_dicts
    outfile["Double_Tree"] = double_dicts
    if debug: print("Took ", time.time() - startTime, " seconds")

    """
    print("Save the tree in ROOT")
    startTime = time.time()


    df_single = ROOT.RDF.MakeNumpyDataFrame(event_dict_single)
    df_double = ROOT.RDF.MakeNumpyDataFrame(double_dicts)

    opts = ROOT.RDF.RSnapshotOptions()
    opts.fMode = "UPDATE"

    #print(opts)
    #print(opts.fMode)

    df_single.Snapshot('Single_Tree', outname)
    df_double.Snapshot('Double_Tree', outname, "", opts)

    print("Took ", time.time() - startTime, " seconds")
    """
