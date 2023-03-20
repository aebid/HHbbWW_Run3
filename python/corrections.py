import awkward as ak
from coffea.lookup_tools import extractor
from coffea.btag_tools import BTagScaleFactor
from coffea.jetmet_tools import FactorizedJetCorrector, JetCorrectionUncertainty, JECStack, CorrectedJetsFactory, JetResolution, JetResolutionScaleFactor, CorrectedMETFactory
import numpy as np

def jet_corrector(EventProcess):
    events = EventProcess.events
    events_pretrigger = EventProcess.events_pretrigger
    ak4_jets = events_pretrigger.Jet
    ak8_jets = events_pretrigger.FatJet
    jetmet_files = EventProcess.jetmet_files
    isMC = EventProcess.isMC
    debug = EventProcess.debug

    if len(jetmet_files) == 0:
        print("No jetmet files for Runyear ", EventProcess.Runyear)
        return

    ak4_jec_files = jetmet_files["ak4_jec_files"]
    ak4_junc_file = jetmet_files["ak4_junc_file"]
    ak4_jer_file = jetmet_files["ak4_jer_file"]
    ak4_jersf_file = jetmet_files["ak4_jersf_file"]

    ak8_jec_files = jetmet_files["ak8_jec_files"]
    ak8_junc_file = jetmet_files["ak8_junc_file"]
    ak8_jer_file = jetmet_files["ak8_jer_file"]
    ak8_jersf_file = jetmet_files["ak8_jersf_file"]

    ak4_extractor_list = []
    ak4_stack_names = []

    for stack_file in (ak4_jec_files+ak4_junc_file+ak4_jer_file+ak4_jersf_file):
        ak4_extractor_list.append("* * " + stack_file)
        ak4_stack_names.append((stack_file.split('/')[-1]).split('.')[0])
        #Stack name needs to take just the file names first portion, so
        #correction_files/jetmet/Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt
        #Goes to
        #Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi

    ak8_extractor_list = []
    ak8_stack_names = []

    for stack_file in (ak8_jec_files+ak8_junc_file+ak8_jer_file+ak8_jersf_file):
        ak8_extractor_list.append("* * " + stack_file)
        ak8_stack_names.append((stack_file.split('/')[-1]).split('.')[0])
        #Stack name needs to take just the file names first portion, so
        #correction_files/jetmet/Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt
        #Goes to
        #Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi


    ak4_ext = extractor()
    ak4_ext.add_weight_sets(ak4_extractor_list)
    ak4_ext.finalize()
    ak4_evaluator = ak4_ext.make_evaluator()
    ak4_jec_stack = JECStack({name: ak4_evaluator[name] for name in ak4_stack_names})

    ak8_ext = extractor()
    ak8_ext.add_weight_sets(ak8_extractor_list)
    ak8_ext.finalize()
    ak8_evaluator = ak8_ext.make_evaluator()
    ak8_jec_stack = JECStack({name: ak8_evaluator[name] for name in ak8_stack_names})

    ak4_name_map = ak4_jec_stack.blank_name_map
    ak4_name_map['JetPt'] = 'pt'
    ak4_name_map['JetMass'] = 'mass'
    ak4_name_map['JetEta'] = 'eta'
    ak4_name_map['JetA'] = 'area'

    ak8_name_map = ak8_jec_stack.blank_name_map
    ak8_name_map['JetPt'] = 'pt'
    ak8_name_map['JetMass'] = 'mass'
    ak8_name_map['JetEta'] = 'eta'
    ak8_name_map['JetA'] = 'area'

    ak4_jets['pt_raw'] = (1 - ak4_jets['rawFactor']) * ak4_jets['pt']
    ak4_jets['mass_raw'] = (1 - ak4_jets['rawFactor']) * ak4_jets['mass']

    ak8_jets['pt_raw'] = (1 - ak8_jets['rawFactor']) * ak8_jets['pt']
    ak8_jets['mass_raw'] = (1 - ak8_jets['rawFactor']) * ak8_jets['mass']

    if isMC: #Hard fix for jetmet_tools bug? https://github.com/CoffeaTeam/coffea/blob/b4589704dc72da509927ea7a15b1996e15ae7702/coffea/jetmet_tools/CorrectedJetsFactory.py#L135-L139
        ak4_jets['pt_gen'] = ak.values_astype(ak.fill_none(ak4_jets.matched_gen.pt, 0), np.float32)
        ak4_name_map['ptGenJet'] = 'pt_gen'

        ak8_jets['pt_gen'] = ak.values_astype(ak.fill_none(ak8_jets.matched_gen.pt, 0), np.float32)
        ak8_name_map['ptGenJet'] = 'pt_gen'

    rho_list = []
    if "Rho" in events_pretrigger.fields:
        rho_list = events_pretrigger.Rho.fixedGridRhoFastjetAll
    else:
        rho_list = events_pretrigger.fixedGridRhoFastjetAll

    ak4_jets['rho'] = ak.broadcast_arrays(rho_list, ak4_jets.pt)[0]
    ak8_jets['rho'] = ak.broadcast_arrays(rho_list, ak8_jets.pt)[0]

    ak4_name_map['ptRaw'] = 'pt_raw'
    ak4_name_map['massRaw'] = 'mass_raw'
    ak4_name_map['Rho'] = 'rho'

    ak8_name_map['ptRaw'] = 'pt_raw'
    ak8_name_map['massRaw'] = 'mass_raw'
    ak8_name_map['Rho'] = 'rho'

    events_pretrigger_cache = events_pretrigger.caches[0]

    if ak4_jec_files == True:
        ak4_fjc_dict = {}
        for stack_file in ak4_jec_files:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak4_fjc_dict[filename] = ak4_evaluator[filename]
        ak4_fjc = FactorizedJetCorrector(
            **ak4_fjc_dict
        )

    if ak4_junc_file == True:
        ak4_jcu_dict = {}
        for stack_file in ak4_junc_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak4_jcu_dict[filename] = ak4_evaluator[filename]
        ak4_jcu = JetCorrectionUncertainty(
            **ak4_jcu_dict
        )

    if ak4_jer_file == True:
        ak4_jer_dict = {}
        for stack_file in ak4_jer_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak4_jer_dict[filename] = ak4_evaluator[filename]
        ak4_jr = JetResolution(
            **ak4_jer_dict
        )


    if ak4_jersf_file == True:
        ak4_jersf_dict = {}
        for stack_file in ak4_jersf_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak4_jersf_dict[filename] = ak4_evaluator[filename]
        ak4_jersf = JetResolutionScaleFactor(
            **ak4_jersf_dict
        )

    ak4_jet_factory = CorrectedJetsFactory(ak4_name_map, ak4_jec_stack)


    if ak8_jec_files == True:
        ak8_fjc_dict = {}
        for stack_file in ak8_jec_files:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak8_fjc_dict[filename] = ak8_evaluator[filename]
        ak8_fjc = FactorizedJetCorrector(
            **ak8_fjc_dict
        )

    if ak8_junc_file == True:
        ak8_jcu_dict = {}
        for stack_file in ak8_junc_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak4_jcu_dict[filename] = ak8_evaluator[filename]
        ak8_jcu = JetCorrectionUncertainty(
            **ak8_jcu_dict
        )

    if ak8_jer_file == True:
        ak8_jer_dict = {}
        for stack_file in ak8_jer_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak8_jer_dict[filename] = ak8_evaluator[filename]
        ak8_jr = JetResolution(
            **ak8_jer_dict
        )


    if ak8_jersf_file == True:
        ak8_jersf_dict = {}
        for stack_file in ak8_jersf_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            ak8_jersf_dict[filename] = ak8_evaluator[filename]
        ak8_jersf = JetResolutionScaleFactor(
            **ak8_jersf_dict
        )

    ak8_jet_factory = CorrectedJetsFactory(ak8_name_map, ak8_jec_stack)


    if not isMC: #Hard fix for jetmet_tools bug? https://github.com/CoffeaTeam/coffea/blob/b4589704dc72da509927ea7a15b1996e15ae7702/coffea/jetmet_tools/CorrectedJetsFactory.py#L135-L139
        ak4_jet_factory.name_map["ptGenJet"] = ak4_jet_factory.name_map["JetPt"]
        ak8_jet_factory.name_map["ptGenJet"] = ak8_jet_factory.name_map["JetPt"]

    events_pretrigger.Jet = ak.pad_none(ak4_jet_factory.build(ak4_jets, lazy_cache=events_pretrigger_cache), 4)

    events_pretrigger.Jet["par_jet_rescale"] = events_pretrigger.Jet.pt_orig/events_pretrigger.Jet.pt
    events_pretrigger.Jet["par_JER_up"] = events_pretrigger.Jet.JER.up.pt/events_pretrigger.Jet.pt
    events_pretrigger.Jet["par_JER_down"] = events_pretrigger.Jet.JER.down.pt/events_pretrigger.Jet.pt
    events_pretrigger.Jet["par_JES_up"] = events_pretrigger.Jet.JES_jes.up.pt/events_pretrigger.Jet.pt
    events_pretrigger.Jet["par_JES_down"] = events_pretrigger.Jet.JES_jes.down.pt/events_pretrigger.Jet.pt


    events_pretrigger.FatJet = ak.pad_none(ak8_jet_factory.build(ak8_jets, lazy_cache=events_pretrigger_cache), 4)

    events_pretrigger.FatJet["par_jet_rescale"] = events_pretrigger.FatJet.pt_orig/events_pretrigger.FatJet.pt
    events_pretrigger.FatJet["par_JER_up"] = events_pretrigger.FatJet.JER.up.pt/events_pretrigger.FatJet.pt
    events_pretrigger.FatJet["par_JER_down"] = events_pretrigger.FatJet.JER.down.pt/events_pretrigger.FatJet.pt
    events_pretrigger.FatJet["par_JES_up"] = events_pretrigger.FatJet.JES_jes.up.pt/events_pretrigger.FatJet.pt
    events_pretrigger.FatJet["par_JES_down"] = events_pretrigger.FatJet.JES_jes.down.pt/events_pretrigger.FatJet.pt

    events.Jet = events_pretrigger.Jet[EventProcess.any_HLT_mask]
    events.FatJet = events_pretrigger.FatJet[EventProcess.any_HLT_mask]

def met_corrector(EventProcess):
    events = EventProcess.events
    events_pretrigger = EventProcess.events_pretrigger
    MET = events_pretrigger.MET
    ak4_jets = events_pretrigger.Jet

    name_map = {}
    name_map['JetPt'] = 'pt'
    name_map['JetPhi'] = 'phi'

    name_map['ptRaw'] = 'pt_raw'

    name_map['METpt'] = 'pt'
    name_map['METphi'] = 'phi'
    name_map['UnClusteredEnergyDeltaX'] = 'MetUnclustEnUpDeltaX'
    name_map['UnClusteredEnergyDeltaY'] = 'MetUnclustEnUpDeltaY'
    met_factory = CorrectedMETFactory(name_map)
    events_pretrigger_cache = events_pretrigger.caches[0]
    events_pretrigger.MET = met_factory.build(events_pretrigger.MET, events_pretrigger.Jet, lazy_cache=events_pretrigger_cache)

    events_pretrigger.MET["par_jet_rescale"] = events_pretrigger.MET.pt_orig/events_pretrigger.MET.pt
    events_pretrigger.MET["par_JER_up"] = events_pretrigger.MET.JER.up.pt/events_pretrigger.MET.pt
    events_pretrigger.MET["par_JER_down"] = events_pretrigger.MET.JER.down.pt/events_pretrigger.MET.pt
    events_pretrigger.MET["par_JES_up"] = events_pretrigger.MET.JES_jes.up.pt/events_pretrigger.MET.pt
    events_pretrigger.MET["par_JES_down"] = events_pretrigger.MET.JES_jes.down.pt/events_pretrigger.MET.pt

    events.MET = events_pretrigger.MET[EventProcess.any_HLT_mask]

def btag_SF(EventProcess):
    events = EventProcess.events
    events_pretrigger = EventProcess.events_pretrigger
    jets = events_pretrigger.Jet
    do_systematics = EventProcess.do_systematics
    btag_SF_file =  EventProcess.btag_SF_file
    debug = EventProcess.debug
    if debug: print("Starting btag SF")

    if len(btag_SF_file) == 0:
        print("No btag SF files for Runyear ", EventProcess.Runyear)
        return

    btag_sf = BTagScaleFactor(btag_SF_file, "reshape", methods="iterativefit,iterativefit,iterativefit")
    events_pretrigger.Jet = ak.with_field(events_pretrigger.Jet, btag_sf.eval("central", jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB), "btag_SF_central")
    btag_systematics = ["jes", "lf", "hf", "hfstats1", "hfstats2", "lfstats1", "lfstats2", "cferr1", "cferr2"]


    if do_systematics:
        for syst in btag_systematics:
            if debug: print("Doing BTag sys " + syst)
            if "cferr" in syst:
                jets["btag_SF_up_"+syst] = ak.where(
                    jets.hadronFlavour == 4,
                        btag_sf.eval("up_"+syst, jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB, ignore_missing=True),
                        jets.btag_SF_central
                )
                jets["btag_SF_down_"+syst] = ak.where(
                    jets.hadronFlavour == 4,
                        btag_sf.eval("down_"+syst, jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB, ignore_missing=True),
                        jets.btag_SF_central
                )
            else:
                jets["btag_SF_up_"+syst] = ak.where(
                    jets.hadronFlavour == 4,
                        jets.btag_SF_central,
                        btag_sf.eval("up_"+syst, jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB, ignore_missing=True)
                )
                jets["btag_SF_down_"+syst] = ak.where(
                    jets.hadronFlavour == 4,
                        jets.btag_SF_central,
                        btag_sf.eval("down_"+syst, jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB, ignore_missing=True)
                )

    events.Jet = jets[EventProcess.any_HLT_mask]


def lepton_ID_SF(EventProcess):
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    lepton_ID_SF_files = EventProcess.lepton_ID_SF_files

    electron_file_dict = lepton_ID_SF_files["electron"]
    muon_file_dict = lepton_ID_SF_files["muon"]

    electron_ext = extractor()
    for ele_ext_str in electron_file_dict["ext_list"]:
        electron_ext.add_weight_sets([ele_ext_str])
    electron_ext.finalize()

    electron_evaluator = electron_ext.make_evaluator()
    print(electron_evaluator.keys())


    muon_ext = extractor()
    for mu_ext_str in muon_file_dict["ext_list"]:
        muon_ext.add_weight_sets([mu_ext_str])
    muon_ext.finalize()

    muon_evaluator = muon_ext.make_evaluator()
    print(muon_evaluator.keys())


    #eleSF = electron_evaluator[""](electrons.eta, electrons.pt)
