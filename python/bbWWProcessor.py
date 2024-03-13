import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import numpy as np
import uproot
import os
from coffea.nanoevents.methods import vector


import object_selection
import event_selection
import tree_manager
import corrections
import genparticles
import weights
import high_level_variables
#import jet_corrections

class EventProcess():
    def __init__(self, inputFile, entryStart, entryStop, isMC, doSF, Runyear, runera, dnn_truth_value, XS, debug=0, HLT_Cuts=0):
        self.fname = inputFile
        self.isMC  = isMC
        self.doSF = doSF
        self.Runyear = Runyear
        self.runera = runera
        self.dnn_truth_value = dnn_truth_value
        self.XS = XS
        self.debug  = debug
        self.HLT_Cuts = HLT_Cuts
        print("Starting NanoAOD processing")
        print("Debug set to ", self.debug)
        self.skip_file = False #Bool to look at if a file is broken

        uproot_file = uproot.open(self.fname)
        events = NanoEventsFactory.from_root(uproot_file, entry_start = entryStart, entry_stop = entryStop, schemaclass=NanoAODSchema.v7).events()
        self.nEvents = len(events)

        #Need sumGenWeight, but data doesn't have a genWeight, so we must set to 1.0 ourselves
        if not self.isMC:
            self.sumGenWeight = self.nEvents
        else:
            self.sumGenWeight = ak.sum(events.genWeight)

        if self.nEvents == 0:
            print("Zero events! This will fail ):")
            self.skip_file = True
            return

        #events = NanoEventsFactory.from_root(self.fname, schemaclass=NanoAODSchema.v7).events()

        #Load all events, then we will cut on HLT early to slim the array
        self.events_pretrigger = events

        #Dicts of variables by year, 2022 is made up for now while we study
        jetDeepJet_WP_dict = {
            "2016": [0.0613, 0.3093, 0.7221],
            "2022": [0.0494, 0.2770, 0.7264],
        }

        ak8_btagDeepB_WP_dict = {
            "2016": [0.2217, 0.6321, 0.8953],
            "2022": [0.1241, 0.4184, 0.7527],
        }

        PFJetID_dict = {
            "2016": 1, #The UL version of 2016 has the PUID set to even intead of odd https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD#Jets
            "2022": 2,
        }
        if not self.isMC:
            PFJetID_dict["2016"] = 2

        #Currently we include all trigger paths -- In the future we may remove some
        electron_trigger_cuts_dict = {
            "2016": (
                getattr(self.events_pretrigger.HLT, 'Ele27_WPTight_Gsf', False) |
                getattr(self.events_pretrigger.HLT, 'Ele25_eta2p1_WPTight_Gsf', False) |
                getattr(self.events_pretrigger.HLT, 'Ele27_eta2p1_WPLoose_Gsf', False)
            ),
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
            "2016": (
                getattr(self.events_pretrigger.HLT, 'IsoMu22', False) |
                getattr(self.events_pretrigger.HLT, 'IsoTkMu22', False) |
                getattr(self.events_pretrigger.HLT, 'IsoMu22_eta2p1', False) |
                getattr(self.events_pretrigger.HLT, 'IsoTkMu22_eta2p1', False) |
                getattr(self.events_pretrigger.HLT, 'IsoMu24', False) |
                getattr(self.events_pretrigger.HLT, 'IsoTkMu24', False)
                ),
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
            ),
        }
        double_electron_trigger_cuts_dict = {
            "2016": (
                getattr(self.events_pretrigger.HLT, 'Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', False)
            ),
            "2022": (
                getattr(self.events_pretrigger.HLT, "Ele23_Ele12_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", False)
            ),
        }
        double_muon_trigger_cuts_dict = {
            "2016": (
                getattr(self.events_pretrigger.HLT, 'Mu17_TrkIsoVVL_Mu8_TrkIsoVVL', False) |
                getattr(self.events_pretrigger.HLT, 'Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', False) |
                getattr(self.events_pretrigger.HLT, 'Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL', False) |
                getattr(self.events_pretrigger.HLT, 'Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ', False)
            ),
            "2022": (
                getattr(self.events_pretrigger.HLT, "Mu17_TrkIsoVVL_Mu8_TrkIsoVVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ", False)
            ),
        }
        muon_electron_trigger_cuts_dict = {
            "2016": (
                getattr(self.events_pretrigger.HLT, 'Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL', False) |
                getattr(self.events_pretrigger.HLT, 'Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', False) |
                getattr(self.events_pretrigger.HLT, 'Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', False) |
                getattr(self.events_pretrigger.HLT, 'Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ', False)
            ),
            "2022": (
                getattr(self.events_pretrigger.HLT, "Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ", False) |
                getattr(self.events_pretrigger.HLT, "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL", False) |
                getattr(self.events_pretrigger.HLT, "Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ", False)
            ),
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
        #We cannot slim these lists until AFTER we do the JetMet corrections!!!
        self.any_HLT_mask = self.electron_trigger_cuts | self.muon_trigger_cuts | self.double_electron_trigger_cuts | self.double_muon_trigger_cuts | self.muon_electron_trigger_cuts
        if not self.HLT_Cuts and self.isMC: self.any_HLT_mask = ak.ones_like(self.any_HLT_mask)

        self.events = self.events_pretrigger
        #if self.HLT_Cuts:
        print("nEvents before HLT Cuts was ", len(self.events))
        self.events = self.events_pretrigger[self.any_HLT_mask]
        self.electron_trigger_cuts = self.electron_trigger_cuts[self.any_HLT_mask]
        self.muon_trigger_cuts = self.muon_trigger_cuts[self.any_HLT_mask]
        self.double_electron_trigger_cuts = self.double_electron_trigger_cuts[self.any_HLT_mask]
        self.double_muon_trigger_cuts = self.double_muon_trigger_cuts[self.any_HLT_mask]
        self.muon_electron_trigger_cuts = self.muon_electron_trigger_cuts[self.any_HLT_mask]
        print("nEvents after HLT Cuts was ", len(self.events))
        #We also have to cut the cuts arrays because they must be the same shape as the events
        self.events["dnn_truth_value"] = dnn_truth_value

        #Re check for zero events after HLT
        if len(self.events) == 0:
            print("Zero events after HLT! This will fail ):")
            self.skip_file = True
            return


        #Start of the corrections files -- When 2022 files are available we must update these
        python_folder_base = "/".join((os.path.realpath(__file__)).split('/')[:-1])
        corrections_dir = python_folder_base+"/correction_files/2016/"
        jetmet_dir = corrections_dir+"jetmet/"
        btag_dir = corrections_dir+"btag_SF/"
        lepton_ID_SF_dir = corrections_dir+"lepton_ID_SF/"
        lepton_tight_TTH_SF_dir = corrections_dir+"tight_tth_SF/"
        lepton_relaxed_TTH_SF_dir = corrections_dir+"relaxed_tth_SF/"
        single_lepton_trigger_SF_dir = corrections_dir+"single_lepton_trigger_SF/"
        single_lepton_fakerate_dir = corrections_dir+"fakerate/SL/"
        double_lepton_fakerate_dir = corrections_dir+"fakerate/DL/"
        pu_reweight_SF_dir = corrections_dir+"pu_reweight/"

        jetmet_files_dict = {
            "2016": {
                "ak4_jec_files": [jetmet_dir+"Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L2Relative_AK4PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L3Absolute_AK4PFPuppi.jec.txt"],
                "ak4_junc_file": [jetmet_dir+"Summer19UL16_V7_MC_Uncertainty_AK4PFPuppi.junc.txt"],
                "ak4_jer_file": [jetmet_dir+"Summer20UL16_JRV3_MC_PtResolution_AK4PFPuppi.jr.txt"],
                "ak4_jersf_file": [jetmet_dir+"Summer20UL16_JRV3_MC_SF_AK4PFPuppi.jersf.txt"],
                "ak8_jec_files": [jetmet_dir+"Summer19UL16_V7_MC_L1FastJet_AK8PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L2Relative_AK8PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L3Absolute_AK8PFPuppi.jec.txt"],
                "ak8_junc_file": [jetmet_dir+"Summer19UL16_V7_MC_Uncertainty_AK8PFPuppi.junc.txt"],
                "ak8_jer_file": [jetmet_dir+"Summer20UL16_JRV3_MC_PtResolution_AK8PFPuppi.jr.txt"],
                "ak8_jersf_file": [jetmet_dir+"Summer20UL16_JRV3_MC_SF_AK8PFPuppi.jersf.txt"],
            },
            "2022": {
                "ak4_jec_files": [jetmet_dir+"Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L2Relative_AK4PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L3Absolute_AK4PFPuppi.jec.txt"],
                "ak4_junc_file": [jetmet_dir+"Summer19UL16_V7_MC_Uncertainty_AK4PFPuppi.junc.txt"],
                "ak4_jer_file": [jetmet_dir+"Summer20UL16_JRV3_MC_PtResolution_AK4PFPuppi.jr.txt"],
                "ak4_jersf_file": [jetmet_dir+"Summer20UL16_JRV3_MC_SF_AK4PFPuppi.jersf.txt"],
                "ak8_jec_files": [jetmet_dir+"Summer19UL16_V7_MC_L1FastJet_AK8PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L2Relative_AK8PFPuppi.jec.txt", jetmet_dir+"Summer19UL16_V7_MC_L3Absolute_AK8PFPuppi.jec.txt"],
                "ak8_junc_file": [jetmet_dir+"Summer19UL16_V7_MC_Uncertainty_AK8PFPuppi.junc.txt"],
                "ak8_jer_file": [jetmet_dir+"Summer20UL16_JRV3_MC_PtResolution_AK8PFPuppi.jr.txt"],
                "ak8_jersf_file": [jetmet_dir+"Summer20UL16_JRV3_MC_SF_AK8PFPuppi.jersf.txt"],
            },
        }


        corrections_dir_run3 = python_folder_base+"/correction_files/2022/"
        corr_files_dict_run3 = {
            "2022": {
                "A": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_355100_357900_eraBCD_GoldenJson",
                },
                "B": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_355100_357900_eraBCD_GoldenJson",
                },
                "C": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_355100_357900_eraBCD_GoldenJson",
                },
                "D": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22_22Sep2023_RunCD_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_355100_357900_eraBCD_GoldenJson",
                },
                "E": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22EE/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22EE/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22EE_22Sep2023_RunE_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22EE_22Sep2023_RunE_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22EE/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_359022_362760_eraEFG_GoldenJson",
                },
                "F": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22EE/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22EE/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22EE_22Sep2023_RunF_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22EE_22Sep2023_RunF_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22EE/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_359022_362760_eraEFG_GoldenJson",
                },
                "G": {
                    "ak4_file": corrections_dir_run3+"jetmet/2022_Summer22EE/jet_jerc.json.gz",
                    "ak8_file": corrections_dir_run3+"jetmet/2022_Summer22EE/fatJet_jerc.json.gz",
                    "ak4_data_key": "Summer22EE_22Sep2023_RunG_V2_DATA_L1L2L3Res_AK4PFPuppi",
                    "ak8_data_key": "Summer22EE_22Sep2023_RunG_V2_DATA_L1L2L3Res_AK8PFPuppi",
                    "ak4_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi",
                    "ak8_MC_key": "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi",

                    "btag_SF_file": corrections_dir_run3+"btag_SF/2022_Summer22/btagging.json.gz",
                    "btag_SF_key": "deepJet_shape",

                    "pu_reweight_file": corrections_dir_run3+"pu_reweight/2022_Summer22EE/puWeights.json.gz",
                    "pu_reweight_key": "Collisions2022_359022_362760_eraEFG_GoldenJson",
                },
            },
            "2023": {

            },
        }


        btag_SF_file_dict = {
            "2016": btag_dir+"DeepJet_2016LegacySF_V1.csv",
            "2022": btag_dir+"DeepJet_2016LegacySF_V1.csv",
        }



        """
        #Example of SF Dict format, supports multiple files split in pT bins
        dict_example = {
            "year": {
                "branch_name": "",
                "electron": {
                    "source_1": {
                        "ext_list": [
                            "local_name RootObjectName "+directory_prefix+"FileName.root",
                            "local_name_error RootObjectName_error "+directory_prefix+"FileName.root",
                        ],
                        "nominal": {
                            "ext_strings": ["local_name"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["local_name_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["local_name_error"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    ...
                },
            },
        }
        """

        lepton_tight_TTH_SF_dict = {
            "2016": {
                "branch_name": "lepton_tight_TTH_SF",
                "electron": {
                    "tight_TTH": {
                        "ext_list": [
                            "ele_tight_ttH_error_min histo_eff_data_min "+lepton_tight_TTH_SF_dir+"lepMVAEffSF_e_error_2016.root",
                            "ele_tight_ttH_error_max histo_eff_data_max "+lepton_tight_TTH_SF_dir+"lepMVAEffSF_e_error_2016.root"
                        ],
                        "nominal": {
                            "ext_strings": [],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_tight_ttH_error_max"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_tight_ttH_error_min"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "tight_TTH": {
                        "ext_list": [
                            "mu_tight_ttH_error_min histo_eff_data_min "+lepton_tight_TTH_SF_dir+"lepMVAEffSF_m_error_2016.root",
                            "mu_tight_ttH_error_max histo_eff_data_max "+lepton_tight_TTH_SF_dir+"lepMVAEffSF_m_error_2016.root"
                        ],
                        "nominal": {
                            "ext_strings": [],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["mu_tight_ttH_error_max"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["mu_tight_ttH_error_min"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022": {
            },
        }


        lepton_ID_SF_dict = {
            "2016": {
                "branch_name": "lepton_ID_SF",
                "electron": {
                    "POG_SF": {
                        "ext_list": [
                            "ele_Lt20 EGamma_SF2D "+lepton_ID_SF_dir+"el_scaleFactors_gsf_ptLt20.root",
                            "ele_Lt20_error EGamma_SF2D_error "+lepton_ID_SF_dir+"el_scaleFactors_gsf_ptLt20.root",
                            "ele_Gt20 EGamma_SF2D "+lepton_ID_SF_dir+"el_scaleFactors_gsf_ptGt20.root",
                            "ele_Gt20_error EGamma_SF2D_error "+lepton_ID_SF_dir+"el_scaleFactors_gsf_ptGt20.root"
                        ],
                        "nominal": {
                            "ext_strings": ["ele_Lt20", "ele_Gt20"],
                            "pt_bins": [0, 20],
                        },
                        "up": {
                            "ext_strings": ["ele_Lt20_error", "ele_Gt20_error"],
                            "pt_bins": [0, 20],
                        },
                        "down": {
                            "ext_strings": ["ele_Lt20_error", "ele_Gt20_error"],
                            "pt_bins": [0, 20],
                        },
                    },
                    "TnP_loose": {
                        "ext_list": [
                            "ele_loose EGamma_SF2D "+lepton_ID_SF_dir+"TnP_loose_ele_2016.root",
                            "ele_loose_error EGamma_SF2D_error "+lepton_ID_SF_dir+"TnP_loose_ele_2016.root"
                        ],
                        "nominal": {
                            "ext_strings": ["ele_loose"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_loose_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_loose_error"],
                            "pt_bins": [0],
                        },
                    },
                    "TnP_looseTTH": {
                        "ext_list": [
                            "ele_loosettH EGamma_SF2D "+lepton_ID_SF_dir+"TnP_loosettH_ele_2016.root",
                            "ele_loosettH_error EGamma_SF2D_error "+lepton_ID_SF_dir+"TnP_loosettH_ele_2016.root"
                        ],
                        "nominal": {
                            "ext_strings": ["ele_loosettH"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_loosettH_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_loosettH_error"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "TnP_looseTTH": {
                        "ext_list": [
                            "mu_loosettH EGamma_SF2D "+lepton_ID_SF_dir+"TnP_loose_muon_2016.root",
                            "mu_loosettH_error EGamma_SF2D_error "+lepton_ID_SF_dir+"TnP_loose_muon_2016.root",
                        ],
                        "nominal": {
                            "ext_strings": ["mu_loosettH"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["mu_loosettH_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["mu_loosettH_error"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022": {

            },
        }


        lepton_relaxed_TTH_SF_dict = {
            "2016": {
                "branch_name": "lepton_relaxed_TTH_SF",
                "electron": {
                    "tight_TTH": {
                        "ext_list": [
                            "ele_relaxed_ttH EGamma_SF2D "+lepton_relaxed_TTH_SF_dir+"lepMVAEffSF_e_2016_recomp.root",
                            "ele_relaxed_ttH_error EGamma_SF2D_error "+lepton_relaxed_TTH_SF_dir+"lepMVAEffSF_e_2016_recomp.root",
                        ],
                        "nominal": {
                            "ext_strings": ["ele_relaxed_ttH"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_relaxed_ttH_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_relaxed_ttH_error"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "tight_TTH": {
                        "ext_list": [
                            "mu_relaxed_ttH EGamma_SF2D "+lepton_relaxed_TTH_SF_dir+"lepMVAEffSF_m_2016_recomp.root",
                            "mu_relaxed_ttH_error EGamma_SF2D_error "+lepton_relaxed_TTH_SF_dir+"lepMVAEffSF_m_2016_recomp.root",
                        ],
                        "nominal": {
                            "ext_strings": ["mu_relaxed_ttH"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["mu_relaxed_ttH_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["mu_relaxed_ttH_error"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022": {
            },
        }


        single_lepton_trigger_SF_dict_OLD = {
            "2016": {
                "branch_name": "single_lepton_trigger_SF",
                "electron": {
                    "single_lepton_trigger": {
                        "ext_list": [
                            "ele_single_trigger etaBinsH "+single_lepton_trigger_SF_dir+"Electron_Run2016_legacy_Ele25.root",
                            "ele_single_trigger_error etaBinsH_error "+single_lepton_trigger_SF_dir+"Electron_Run2016_legacy_Ele25.root",
                        ],
                        "nominal": {
                            "ext_strings": ["ele_single_trigger"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_single_trigger_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_single_trigger_error"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "single_lepton_trigger": {
                        "ext_list": [
                            "mu_single_trigger etaBinsH "+single_lepton_trigger_SF_dir+"Muon_Run2016_legacy_IsoMu22.root",
                            "mu_single_trigger_error etaBinsH_error "+single_lepton_trigger_SF_dir+"Muon_Run2016_legacy_IsoMu22.root",
                        ],
                        "nominal": {
                            "ext_strings": ["mu_single_trigger"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["mu_single_trigger_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["mu_single_trigger_error"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022":{

            },
        }


        single_lepton_trigger_SF_dict = {
            "2016": {
                "branch_name": "single_lepton_trigger_SF",
                "electron": {
                    "single_lepton_trigger": {
                        "ext_list": [
                            "ele_single_trigger ele_SF "+single_lepton_trigger_SF_dir+"ele_and_mu_SF_2016.root",
                            "ele_single_trigger_error ele_SF_error "+single_lepton_trigger_SF_dir+"ele_and_mu_SF_2016.root",
                        ],
                        "nominal": {
                            "ext_strings": ["ele_single_trigger"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["ele_single_trigger_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["ele_single_trigger_error"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "single_lepton_trigger": {
                        "ext_list": [
                            "mu_single_trigger mu_SF "+single_lepton_trigger_SF_dir+"ele_and_mu_SF_2016.root",
                            "mu_single_trigger_error mu_SF_error "+single_lepton_trigger_SF_dir+"ele_and_mu_SF_2016.root",
                        ],
                        "nominal": {
                            "ext_strings": ["mu_single_trigger"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["mu_single_trigger_error"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["mu_single_trigger_error"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022":{

            },
        }





        single_lepton_fakerate_dict = {
            "2016": {
                "branch_name": "single_lepton_fakerate",
                "electron": {
                    "single_lepton_fakerate": {
                        "ext_list": [
                            "single_ele_FR FR_mva030_el_data_comb "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                            "single_ele_FR_up FR_mva030_el_data_comb_up "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                            "single_ele_FR_down FR_mva030_el_data_comb_down "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                        ],
                        "nominal": {
                            "ext_strings": ["single_ele_FR"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["single_ele_FR_up"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["single_ele_FR_down"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "single_lepton_fakerate": {
                        "ext_list": [
                            "single_mu_FR FR_mva050_mu_data_comb "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                            "single_mu_FR_up FR_mva050_mu_data_comb_up "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                            "single_mu_FR_down FR_mva050_mu_data_comb_down "+single_lepton_fakerate_dir+"FR_lep_mva_hh_bbWW_wFullSyst_2016_KBFI_2021Feb3_wCERNUncs2_FRErrTheshold_0p01.root",
                        ],
                        "nominal": {
                            "ext_strings": ["single_mu_FR"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["single_mu_FR_up"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["single_mu_FR_down"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022":{

            },
        }




        double_lepton_fakerate_dict = {
            "2016": {
                "branch_name": "double_lepton_fakerate",
                "electron": {
                    "double_lepton_fakerate": {
                        "ext_list": [
                            "double_ele_FR FR_mva030_el_data_comb "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                            "double_ele_FR_up FR_mva030_el_data_comb_up "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                            "double_ele_FR_down FR_mva030_el_data_comb_down "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                        ],
                        "nominal": {
                            "ext_strings": ["double_ele_FR"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["double_ele_FR_up"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["double_ele_FR_down"],
                            "pt_bins": [0],
                        },
                    },
                },
                "muon": {
                    "double_lepton_fakerate": {
                        "ext_list": [
                            "double_mu_FR FR_mva050_mu_data_comb "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                            "double_mu_FR_up FR_mva050_mu_data_comb_up "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                            "double_mu_FR_down FR_mva050_mu_data_comb_down "+double_lepton_fakerate_dir+"FR_lep_mva_hh_multilepton_wFullSyst_2016_KBFI_2020Dec21_wCERNUncs2_FRErrTheshold_0p01.root",
                        ],
                        "nominal": {
                            "ext_strings": ["double_mu_FR"],
                            "pt_bins": [0],
                        },
                        "up": {
                            "ext_strings": ["double_mu_FR_up"],
                            "pt_bins": [0],
                        },
                        "down": {
                            "ext_strings": ["double_mu_FR_down"],
                            "pt_bins": [0],
                        },
                    },
                },
            },
            "2022":{

            },
        }


        pu_reweight_dict = {
            "2016": {
                "branch_name": "pu_reweight",
                "json_file": pu_reweight_SF_dir+"puWeights_preVPF.json",
                "json_corrname": "Collisions16_UltraLegacy_goldenJSON",
            },
            "2022": {

            },
        }



        self.lepton_ID_SF_dict = lepton_ID_SF_dict[str(self.Runyear)]
        self.lepton_tight_TTH_SF_dict = lepton_tight_TTH_SF_dict[str(self.Runyear)]
        self.lepton_relaxed_TTH_SF_dict = lepton_relaxed_TTH_SF_dict[str(self.Runyear)]
        self.single_lepton_trigger_SF_dict = single_lepton_trigger_SF_dict[str(self.Runyear)]
        self.single_lepton_fakerate_dict = single_lepton_fakerate_dict[str(self.Runyear)]
        self.double_lepton_fakerate_dict = double_lepton_fakerate_dict[str(self.Runyear)]
        self.corrections_dict_list = [self.lepton_ID_SF_dict, self.lepton_tight_TTH_SF_dict, self.lepton_relaxed_TTH_SF_dict, self.single_lepton_trigger_SF_dict, self.single_lepton_fakerate_dict, self.double_lepton_fakerate_dict]

        self.jetmet_files = jetmet_files_dict[str(self.Runyear)]
        self.btag_SF_file = btag_SF_file_dict[str(self.Runyear)]
        self.pu_reweight_dict = pu_reweight_dict[str(self.Runyear)]

        #Run3 jetmet files are in a different format
        if self.Runyear >= 2022: self.corr_files_Run3 = corr_files_dict_run3[str(self.Runyear)][str(self.runera)]

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

    #Prepare Objects
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
    def add_HT(self):
        return object_selection.add_HT(self)
    def clean_events(self):
        return object_selection.clean_events(self)
    def all_obj_selection(self):
        return object_selection.all_obj_selection(self)

    #Event Topology
    def single_lepton_category(self):
        return event_selection.single_lepton_category(self)
    def double_lepton_category(self):
        return event_selection.double_lepton_category(self)

    #Jet Energy Corrections
    def jet_corrector(self):
        return corrections.jet_corrector(self)

    def jetmet_json_corrector(self):
        return corrections.jetmet_json(self)
    def btag_json_SF(self):
        return corrections.btag_json(self)
    def pu_reweight_json(self):
        return corrections.pu_reweight_json(self)


    def met_corrector(self):
        return corrections.met_corrector(self)
    def jet_met_corrector(self):
        return corrections.jet_met_corrector(self)

    #Scale Factors and Corrections
    def lepton_ID_SF(self):
        return corrections.lepton_ID_SF(self)
    def lepton_tight_TTH_SF(self):
        return corrections.lepton_tight_TTH_SF(self)
    def lepton_relaxed_TTH_SF(self):
        return corrections.lepton_relaxed_TTH_SF(self)
    def btag_SF(self):
        return corrections.btag_SF(self)
    def make_evaluator(self):
        return corrections.make_evaluator(self)
    def add_scale_factors(self):
        return corrections.add_scale_factors(self)
    def do_lepton_fakerate(self):
        return corrections.do_lepton_fakerate(self)
    def single_lepton_trigger_SF(self):
        return corrections.single_lepton_trigger_SF(self)
    def top_pt_reweight(self):
        return corrections.top_pt_reweight(self)
    def pu_reweight(self):
        return corrections.pu_reweight(self)

    #Gen Particle Matchers
    def single_lepton_genpart(self):
        self.genpart_sgl = genparticles.single_lepton_genpart(self)
    def double_lepton_genpart(self):
        self.genpart_dbl = genparticles.double_lepton_genpart(self)
    def recoJet_to_genJet(self):
        return genparticles.recoJet_to_genJet(self)
    def recoLep_to_genLep(self):
        return genparticles.recoLep_to_genLep(self)
    def recoMET_to_genMET(self):
        return genparticles.recoMET_to_genMET(self)
    def match_genparts(self):
        return genparticles.match_genparts(self)

    def add_event_weight(self):
        return weights.add_event_weight(self)

    def add_high_level_variables(self):
        return high_level_variables.add_high_level_variables(self)

    #Output tree
    def update_outfile(self, outfile):
        return tree_manager.update_outfile(self, outfile)


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
