import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
import ROOT
from coffea.nanoevents.methods import vector


import object_selection
import event_selection
#import tree_manager
#import jet_corrections

class EventProcess():
    def __init__(self, inputFile, isMC, Runyear, dnn_truth_value, debug=0):
        self.fname = inputFile
        self.sampleName = sampleName
        self.isMC  = isMC
        self.Runyear = Runyear
        self.dnn_truth_value = dnn_truth_value
        self.debug  = debug
        print("Starting NanoAOD processing")
        print("Debug set to ", self.debug)

        events = NanoEventsFactory.from_root(self.fname, schemaclass=NanoAODSchema.v7).events()

        #Load all events, then we will cut on HLT early to slim the array
        self.events_pretrigger = events

        #Dicts of variables by year, 2022 is made up for now while we study
        jetDeepJet_WP_dict = {
            "2022": [0.0494, 0.2770, 0.7264],
        }

        ak8_btagDeepB_WP_dict = {
            "2022": [0.1241, 0.4184, 0.7527],
        }

        PFJetID_dict = {
            "2022": 2,
        }

        #Currently we include all trigger paths -- In the future we may remove some
        electron_trigger_cuts_dict = {
            "2022": (
                getattr(self.events_pretrigger.HLT, "Ele15_WPLoose_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele20_WPLoose_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele27_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele28_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele30_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele32_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele35_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele38_WPTight_Gsf", False) |
                getattr(self.events_pretrigger.HLT, "Ele40_WPTight_Gsf", False)
            ),
        }
        muon_trigger_cuts_dict = {
            "2022": (
                getattr(self.events_pretrigger.HLT, "Mu17", False) |
                getattr(self.events_pretrigger.HLT, "Mu17_TrkIsoVVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu19", False) |
                getattr(self.events_pretrigger.HLT, "Mu19_TrkIsoVVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu20", False) |
                getattr(self.events_pretrigger.HLT, "Mu27", False) |
                getattr(self.events_pretrigger.HLT, "IsoMu20", False) |
                getattr(self.events_pretrigger.HLT, "IsoMu24", False) |
                getattr(self.events_pretrigger.HLT, "IsoMu24_eta2p1", False) |
                getattr(self.events_pretrigger.HLT, "IsoMu27", False)
            )
        }
        double_electron_trigger_cuts_dict = {
            "2022": (
                getattr(self.events_pretrigger.HLT, "Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", False)
            )
        }
        double_muon_trigger_cuts_dict = {
            "2022": (
                getattr(self.events_pretrigger.HLT, "Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", False)
            )
        }
        muon_electron_trigger_cuts_dict = {
            "2022": (
                getattr(self.events_pretrigger.HLT, "Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", False) |
                getattr(self.events_pretrigger.HLT, "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", False)
            )
        }

        self.jetDeepJet_WP = jetDeepJet_WP_dict[str(self.Runyear)]
        self.ak8_btagDeepB_WP = ak8_btagDeepB_WP_dict[str(self.Runyear)]
        self.PFJetID = PFJetID_dict[str(self.Runyear)]

        self.electron_trigger_cuts = electron_trigger_cuts_dict[str(self.Runyear)]
        self.muon_trigger_cuts = muon_trigger_cuts_dict[str(self.Runyear)]
        self.double_electron_trigger_cuts = double_electron_trigger_cuts_dict[str(self.Runyear)]
        self.double_muon_trigger_cuts = double_muon_trigger_cuts_dict[str(self.Runyear)]
        self.muon_electron_trigger_cuts = muon_electron_trigger_cuts_dict[str(self.Runyear)]

        #Here we define the used events array passing any of the lepton triggers
        any_HLT_mask = self.electron_trigger_cuts | self.muon_trigger_cuts | self.double_electron_trigger_cuts | self.double_muon_trigger_cuts | self.muon_electron_trigger_cuts
        self.events = self.events_pretrigger[any_HLT_mask]
        self.electron_trigger_cuts = self.electron_trigger_cuts[any_HLT_mask]
        self.muon_trigger_cuts = self.muon_trigger_cuts[any_HLT_mask]
        self.double_electron_trigger_cuts = self.double_electron_trigger_cuts[any_HLT_mask]
        self.double_muon_trigger_cuts = self.double_muon_trigger_cuts[any_HLT_mask]
        self.muon_electron_trigger_cuts = self.muon_electron_trigger_cuts[any_HLT_mask]
        #We also have to cut the cuts arrays because they must be the same shape as the events

        self.jetmet_corr_dir = "jetmet_corrections/"
        self.ak4_jec_files  =   []
        self.ak4_junc_file  =   []
        self.ak4_jer_file   =   []
        self.ak4_jersf_file =   []
        self.ak8_jec_files  =   []
        self.ak8_junc_file  =   []
        self.ak8_jer_file   =   []
        self.ak8_jersf_file =   []

        if self.Runyear == 2016:
            self.ak4_jec_files  =   ["Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt", "Summer19UL16_V7_MC_L2Relative_AK4PFPuppi.jec.txt", "Summer19UL16_V7_MC_L3Absolute_AK4PFPuppi.jec.txt"]
            self.ak4_junc_file  =   ["Summer19UL16_V7_MC_Uncertainty_AK4PFPuppi.junc.txt"]
            self.ak4_jer_file   =   ["Summer20UL16_JRV3_MC_PtResolution_AK4PFPuppi.jr.txt"]
            self.ak4_jersf_file =   ["Summer20UL16_JRV3_MC_SF_AK4PFPuppi.jersf.txt"]
            self.ak8_jec_files  =   ["Summer19UL16_V7_MC_L1FastJet_AK8PFPuppi.jec.txt", "Summer19UL16_V7_MC_L2Relative_AK8PFPuppi.jec.txt", "Summer19UL16_V7_MC_L3Absolute_AK8PFPuppi.jec.txt"]
            self.ak8_junc_file  =   ["Summer19UL16_V7_MC_Uncertainty_AK8PFPuppi.junc.txt"]
            self.ak8_jer_file   =   ["Summer20UL16_JRV3_MC_PtResolution_AK8PFPuppi.jr.txt"]
            self.ak8_jersf_file =   ["Summer20UL16_JRV3_MC_SF_AK8PFPuppi.jersf.txt"]



        if self.debug > 0:
            print("Muons: ",       self.events.Muon)
            print("Electrons: ",   self.events.Electron)
            print("Taus: ",        self.events.Tau)
            print("AK4 Jets: ",    self.events.Jet)
            print("AK8 Jets: ",    self.events.FatJet)
            print("AK8 SubJets: ", self.events.SubJet)
            print("HLT: ",         self.events.HLT)
        #from object_selection import object_selection
        #from event_selection import SL_selection,DL_selection

        events["dnn_truth_value"] = dnn_truth_value


    def add_conept(self):
        return object_selection.add_conept(self)
    def link_jets(self):
        return object_selection.link_jets(self)
    def muon_selection(self):
        return object_selection.muon_selection(self)
    def electron_selection(self):
        return object_selection.electron_selection(self)
    def ak4_jet_selection(self):
        return object_selection.ak4_jet_selection(self)
    def ak8_jet_selection(self):
        return object_selection.ak8_jet_selection(self)
    def clean_events(self):
        return object_selection.clean_events(self)

    def all_obj_selection(self):
        return object_selection.all_obj_selection(self)
    def single_lepton_category(self):
        return event_selection.single_lepton_category(self)
    def double_lepton_category(self):
        return event_selection.double_lepton_category(self)

    #def ak4_jet_corrector(self):
    #    return jet_corrections.ak4_jet_corrector(self)
    #def ak8_jet_corrector(self):
    #    return jet_corrections.ak8_jet_corrector(self)
    #def sub_jet_corrector(self):
    #    return jet_corrections.sub_jet_corrector(self)
    #def met_corrector(self):
    #    return jet_corrections.met_corrector(self)

    def print_object_selection(self):

        print("Muons preselected: ", ak.sum(ak.any(self.events.Muon.preselected, axis=1)))
        print("Muons fakeable: ", ak.sum(ak.any(self.events.Muon.fakeable, axis=1)))
        print("Muons tight: ", ak.sum(ak.any(self.events.Muon.tight, axis=1)))


        print("Electrons preselected: ", ak.sum(ak.any(self.events.Electron.preselected, axis=1)))
        print("Electrons cleaned: ", ak.sum(ak.any(self.events.Electron.cleaned, axis=1)))
        print("Electrons fakeable: ", ak.sum(ak.any(self.events.Electron.fakeable, axis=1)))
        print("Electrons tight: ", ak.sum(ak.any(self.events.Electron.tight, axis=1)))


        print("AK4 Jets preselected: ", ak.sum(ak.any(self.events.Jet.preselected, axis=1)))
        print("AK4 Jets cleaned: ", ak.sum(ak.any(self.events.Jet.cleaned_all, axis=1)))
        print("AK4 Jets loose Btag: ", ak.sum(ak.any(self.events.Jet.loose_btag_all, axis=1)))
        print("AK4 Jets medium Btag: ", ak.sum(ak.any(self.events.Jet.medium_btag_all, axis=1)))

        print("AK8 Jets preselected: ", ak.sum(ak.any(self.events.FatJet.preselected, axis=1)))
        print("AK8 Jets cleaned: ", ak.sum(ak.any(self.events.FatJet.cleaned_all, axis=1)))
        print("AK8 Jets Btag: ", ak.sum(ak.any(self.events.FatJet.btag_all, axis=1)))

    def print_event_selection(self):
        print("N events: ", len(self.events))
        print("N single events: ", ak.sum(self.events.single_lepton))

        print("N Single_HbbFat_WjjRes_AllReco: ", ak.sum(self.events.Single_HbbFat_WjjRes_AllReco))
        print("N Single_HbbFat_WjjRes_MissJet: ", ak.sum(self.events.Single_HbbFat_WjjRes_MissJet))
        print("N Single_Res_allReco_2b:        ", ak.sum(self.events.Single_Res_allReco_2b))
        print("N Single_Res_allReco_1b:        ", ak.sum(self.events.Single_Res_allReco_1b))
        print("N Single_Res_MissWJet_2b:       ", ak.sum(self.events.Single_Res_MissWJet_2b))
        print("N Single_Res_MissWJet_1b:       ", ak.sum(self.events.Single_Res_MissWJet_1b))
        print("N Signal:                       ", ak.sum(self.events.Single_Signal))
        print("N Fake:                         ", ak.sum(self.events.Single_Fake))
        print("Single Category Cutflow:        ", self.events.single_cutflow)


        print("N events: ", len(self.events))
        print("N double events: ", ak.sum(self.events.double_lepton))



        print("N Double HbbFat:         ", ak.sum(self.events.Double_HbbFat))
        print("N Double Res_1b:         ", ak.sum(self.events.Double_Res_1b))
        print("N Double Res_2b:         ", ak.sum(self.events.Double_Res_2b))
        print("N Double Signal:         ", ak.sum(self.events.Double_Signal))
        print("N Double Fake:           ", ak.sum(self.events.Double_Fake))
        print("Double Category Cutflow: ", self.events.double_cutflow)

    #def create_df(self, outname):
    #    return tree_manager.create_df(self, outname)
