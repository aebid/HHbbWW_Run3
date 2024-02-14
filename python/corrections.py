import awkward as ak
from coffea.lookup_tools import extractor, json_converters
from coffea.btag_tools import BTagScaleFactor
from coffea.jetmet_tools import FactorizedJetCorrector, JetCorrectionUncertainty, JECStack, CorrectedJetsFactory, JetResolution, JetResolutionScaleFactor, CorrectedMETFactory
import correctionlib
import numpy as np
import math

def jetmet_json(EventProcess):
    events = EventProcess.events
    corr_files = EventProcess.corr_files_Run3

    #Starting handling 2022 jec files, but they are in json.gz files
    #jerc_ak4_file = "correction_files/2022/jetmet/2022_Summer22EE/jet_jerc.json.gz"
    #jerc_ak8_file = "correction_files/2022/jetmet/2022_Summer22EE/fatJet_jerc.json.gz"

    #jerc_ak4_data_key = "Summer22EE_22Sep2023_RunE_V2_DATA_L1L2L3Res_AK4PFPuppi"
    #jerc_ak4_MC_key = "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK4PFPuppi"

    #jerc_ak8_data_key = "Summer22EE_22Sep2023_RunE_V2_DATA_L1L2L3Res_AK8PFPuppi"
    #jerc_ak8_MC_key = "Summer22EE_22Sep2023_V2_MC_L1L2L3Res_AK8PFPuppi"


    jerc_ak4_file = corr_files['ak4_file']
    jerc_ak8_file = corr_files['ak8_file']

    jerc_ak4_data_key = corr_files['ak4_data_key']
    jerc_ak8_data_key = corr_files['ak8_data_key']

    jerc_ak4_MC_key = corr_files['ak4_MC_key']
    jerc_ak8_MC_key = corr_files['ak8_MC_key']


    ak4_jerc_key = jerc_ak4_data_key
    ak8_jerc_key = jerc_ak8_data_key
    if EventProcess.isMC:
        ak4_jerc_key = jerc_ak4_MC_key
        ak8_jerc_key = jerc_ak8_MC_key


    jerc_ak4_set = correctionlib.CorrectionSet.from_file(jerc_ak4_file)
    jerc_ak8_set = correctionlib.CorrectionSet.from_file(jerc_ak8_file)

    #Example on how to use json and correctionlib
    #/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/examples/jercExample.py
    ak4_compound = jerc_ak4_set.compound
    ak8_compound = jerc_ak8_set.compound


    ak4_jec = ak4_compound[jerc_ak4_data_key]
    #Check what inputs the json wants
    #print([input.name for input in ak4_jec.inputs])
    #LUT to turn JSON names into object names
    lut = {'JetA': 'area', 'JetEta': 'eta', 'JetPt': 'pt', 'Rho': 'rho'}
    #print([lut[input.name] for input in ak4_jec.inputs])
    #Now get values from these real names
    #Cannot use jets.lut[input.name] or jets[lut[input.name]], must use getattr
    #For now, correctionlib doesn't take awkard arrays, so we take original shape, flatten variables, LUT, then reshape
    ak4_inputs = [ak.flatten(getattr(events.Jet, lut[input.name])) for input in ak4_jec.inputs]
    #print(ak4_inputs)
    #Now we try to feed it those inputs from the jet object
    ak4_counts = ak.num(events.Jet)
    ak4_correction_values = ak.unflatten(ak4_jec.evaluate(*ak4_inputs), ak4_counts)
    #Now we have the correction values, but we must apply them to the jets still
    events.Jet = ak.with_field(events.Jet, ak4_correction_values, "par_jet_rescale")
    events.Jet = ak.with_field(events.Jet, events.Jet.pt, "pt_raw")
    events.Jet = ak.with_field(events.Jet, events.Jet.pt*ak4_correction_values, "pt")
    events.Jet = ak.with_field(events.Jet, events.Jet.mass, "mass_raw")
    events.Jet = ak.with_field(events.Jet, events.Jet.mass*ak4_correction_values, "mass")


    #Now ak8 jets
    ak8_jec = ak8_compound[jerc_ak8_data_key]
    ak8_inputs = [ak.flatten(getattr(events.FatJet, lut[input.name])) for input in ak8_jec.inputs]
    ak8_counts = ak.num(events.FatJet)
    ak8_correction_values = ak.unflatten(ak8_jec.evaluate(*ak8_inputs), ak8_counts)
    events.FatJet = ak.with_field(events.FatJet, ak8_correction_values, "par_jet_rescale")
    events.FatJet = ak.with_field(events.FatJet, events.FatJet.pt, "pt_raw")
    events.FatJet = ak.with_field(events.FatJet, events.FatJet.pt*ak8_correction_values, "pt")
    events.FatJet = ak.with_field(events.FatJet, events.FatJet.mass, "mass_raw")
    events.FatJet = ak.with_field(events.FatJet, events.FatJet.mass*ak8_correction_values, "mass")



    #Also these JERC files have all four pieces (JES JUNC JER JERSF) Will add later


def btag_json(EventProcess):
    events = EventProcess.events
    corr_files = EventProcess.corr_files_Run3

    #btag_files = "correction_files/2022/btag_SF/2022_Summer22/btagging.json.gz"

    btag_file = corr_files['btag_SF_file']
    btag_key = corr_files['btag_SF_key']

    btag_cset = correctionlib.CorrectionSet.from_file(btag_file)
    btag_SF = btag_cset[btag_key]

    hadronFlavour = ak.flatten(abs(events.Jet.hadronFlavour))
    #For some reason, eta MUST be less than 2.5 or else binning crashes in correctionlib
    eta = abs(events.Jet.eta)
    eta = ak.where(
        eta >= 2.5,
            2.49,
            eta
    )
    abseta = ak.flatten(eta)
    pt = ak.flatten(events.Jet.pt)
    disc = ak.flatten(events.Jet.btagDeepFlavB)
    counts = ak.num(events.Jet)

    btag_SF_central = ak.unflatten(btag_SF.evaluate("central", hadronFlavour, abseta, pt, disc), counts)

    events.Jet = ak.with_field(events.Jet, btag_SF_central, "btag_SF")
    #Will do systematics later, just need main value for now
    #central, up, down


def pu_reweight_json(EventProcess):
    events = EventProcess.events
    corr_files = EventProcess.corr_files_Run3

    pu_reweight_file = corr_files['pu_reweight_file']
    pu_reweight_key = corr_files['pu_reweight_key']

    #pu_reweight_file = "correction_files/2022/pu_reweight/2022_Summer22/puWeights.json.gz"
    #pu_reweight_key = "Collisions2022_355100_357900_eraBCD_GoldenJson"

    pu_cset = correctionlib.CorrectionSet.from_file(pu_reweight_file)
    pu_reweight = pu_cset[pu_reweight_key]

    pu_reweight_values = pu_reweight.evaluate(events.Pileup.nTrueInt, "nominal")
    events["pu_reweight"] = pu_reweight_values
    #Will do systematis later, just need main value for now
    #nominal, up, down



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
    #Using BTagScaleFactor class from Coffea https://coffeateam.github.io/coffea/api/coffea.btag_tools.BTagScaleFactor.html
    #SF File obtained from https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
    events = EventProcess.events
    jets = events.Jet
    btag_SF_file =  EventProcess.btag_SF_file
    debug = EventProcess.debug
    if debug: print("Starting btag SF")

    if len(btag_SF_file) == 0:
        print("No btag SF files for Runyear ", EventProcess.Runyear)
        return

    btag_sf = BTagScaleFactor(btag_SF_file, "MEDIUM", methods="comb,comb,incl")
    events.Jet = ak.with_field(events.Jet, btag_sf.eval("central", jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB), "btag_SF")
    events.Jet = ak.with_field(events.Jet, btag_sf.eval("up", jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB), "btag_SF_up")
    events.Jet = ak.with_field(events.Jet, btag_sf.eval("down", jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB), "btag_SF_down")

def make_evaluator(EventProcess):
    dict_list = EventProcess.corrections_dict_list
    debug = EventProcess.debug

    ext = extractor()
    for dict in dict_list:
        for lep in ["electron", "muon"]:
            if lep not in dict.keys(): continue
            for process in dict[lep]:
                if process == "branch_name": continue
                for ext_string in dict[lep][process]["ext_list"]:
                    ext.add_weight_sets([ext_string])
    ext.finalize()
    EventProcess.corrections_Evaluator = ext.make_evaluator()
    if debug: print("Made evaluator! Keys are ", EventProcess.corrections_Evaluator.keys())

def get_SF_from_dict(dict, leptons, eval, LUTx_var, LUTy_var):
    tmp_value = 1.0
    for cut_num, pt_cut in enumerate(dict["pt_bins"]):
        tmp_value = ak.where(
            leptons.pt > pt_cut,
                eval[dict["ext_strings"][cut_num]](LUTx_var, LUTy_var),
                tmp_value
        )
    return tmp_value

def lepton_ID_SF(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.lepton_ID_SF_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.eta, lep_list.pt)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For POG + loose ttH, we multiple all SF together, where up = nom+up and down = nom-down
            nom_value = nom_value * process_nom_value
            up_value = up_value * (process_nom_value + process_up_value)
            down_value = down_value * (process_nom_value - process_down_value)
            if debug: print("Did process ", process, " on ", lep)



        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def lepton_tight_TTH_SF(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.lepton_tight_TTH_SF_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            #process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval) #No nominal for this SF
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.eta, lep_list.pt)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For tight ttH, we only have error up and error down, nom = 1.0
            #nom_value = process_nom_value
            up_value = process_up_value
            down_value = process_down_value
            if debug: print("Did process ", process, " on ", lep)


        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def lepton_relaxed_TTH_SF(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.lepton_relaxed_TTH_SF_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.eta, lep_list.pt)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For relaxed ttH, we do nom, nom+up, nom-down
            nom_value = process_nom_value
            up_value = process_nom_value + process_up_value
            down_value = process_nom_value - process_down_value
            if debug: print("Did process ", process, " on ", lep)


        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def single_lepton_trigger_SF(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.single_lepton_trigger_SF_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.eta, lep_list.pt)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.eta, lep_list.pt)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For relaxed ttH, we do nom, nom+up, nom-down
            nom_value = process_nom_value
            up_value = process_nom_value + process_up_value
            down_value = process_nom_value - process_down_value
            if debug: print("Did process ", process, " on ", lep)


        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def single_lepton_fakerate(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.single_lepton_fakerate_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval, lep_list.pt, lep_list.eta)
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.pt, lep_list.eta)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.pt, lep_list.eta)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For relaxed ttH, we do nom, nom+up, nom-down
            nom_value = process_nom_value
            up_value = process_nom_value + process_up_value
            down_value = process_nom_value - process_down_value
            if debug: print("Did process ", process, " on ", lep)


        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def double_lepton_fakerate(EventProcess):
    eval = EventProcess.corrections_Evaluator
    events = EventProcess.events
    electrons = events.Electron
    muons = events.Muon
    dict = EventProcess.double_lepton_fakerate_dict
    debug = EventProcess.debug

    for lep_pair in [("electron", electrons), ("muon", muons)]:
        lep = lep_pair[0]
        lep_list = lep_pair[1]
        branch_name = dict["branch_name"]
        nom_value = 1.0
        up_value = 1.0
        down_value = 1.0
        for process in dict[lep]:
            process_nom_value = get_SF_from_dict(dict[lep][process]["nominal"], lep_list, eval, lep_list.pt, lep_list.eta)
            process_up_value = get_SF_from_dict(dict[lep][process]["up"], lep_list, eval, lep_list.pt, lep_list.eta)
            process_down_value = get_SF_from_dict(dict[lep][process]["down"], lep_list, eval, lep_list.pt, lep_list.eta)

            #THIS IS WHERE YOU MUST WRITE YOUR OWN CODE
            #Here you decide what values will go into the nom/up/down branches
            #THIS COULD BE DIFFERENT FOR EVERY PROCESS
            #For relaxed ttH, we do nom, nom+up, nom-down
            nom_value = process_nom_value
            up_value = process_nom_value + process_up_value
            down_value = process_nom_value - process_down_value
            if debug: print("Did process ", process, " on ", lep)


        if lep == "electron":
            events.Electron = ak.with_field(events.Electron, nom_value, branch_name)
            events.Electron = ak.with_field(events.Electron, up_value, branch_name+"_up")
            events.Electron = ak.with_field(events.Electron, down_value, branch_name+"_down")

        if lep == "muon":
            events.Muon = ak.with_field(events.Muon, nom_value, branch_name)
            events.Muon = ak.with_field(events.Muon, up_value, branch_name+"_up")
            events.Muon = ak.with_field(events.Muon, down_value, branch_name+"_down")

def jet_met_corrector(EventProcess):
    jet_corrector(EventProcess)
    if EventProcess.debug: print("Jet Corrector Done")
    met_corrector(EventProcess)
    if EventProcess.debug: print("MET Corrector Done")

def add_scale_factors(EventProcess):
    lepton_ID_SF(EventProcess)
    if EventProcess.debug: print("Lepton ID SF Done")
    lepton_tight_TTH_SF(EventProcess)
    if EventProcess.debug: print("Lepton tight TTH SF Done")
    lepton_relaxed_TTH_SF(EventProcess)
    if EventProcess.debug: print("Lepton relaxed TTH SF Done")
    single_lepton_trigger_SF(EventProcess)
    if EventProcess.debug: print("Single Lepton Trigger SF Done")
    btag_SF(EventProcess)
    if EventProcess.debug: print("Btag SF Done")
    pu_reweight(EventProcess)
    if EventProcess.debug: print("PU SF Done")

def do_lepton_fakerate(EventProcess):
    single_lepton_fakerate(EventProcess)
    double_lepton_fakerate(EventProcess)

def top_pt_reweight(EventProcess):
    events = EventProcess.events
    genParts = events.GenPart
    genTops = genParts[abs(genParts.pdgId) == 6]

    genTop1 = genTops[:,0]
    genTop2 = genTops[:,1]

    top1_weight = math.exp(1)**(0.088 - (0.00087*genTop1.pt) + 0.000000927*(genTop1.pt**2))
    top2_weight = math.exp(1)**(0.088 - (0.00087*genTop2.pt) + 0.000000927*(genTop2.pt**2))
    top_reweight = (top1_weight * top2_weight)**(0.5)

    events["tt_reweight"] = top_reweight

def pu_reweight(EventProcess):
    events = EventProcess.events

    pu_reweight_dict = EventProcess.pu_reweight_dict
    pu_reweight_filename = pu_reweight_dict["json_file"]
    pu_reweight_corrname = pu_reweight_dict["json_corrname"]
    branch_name = pu_reweight_dict["branch_name"]

    #python_folder_base = "/".join((os.path.realpath(__file__)).split('/')[:-1])
    #corrections_dir = python_folder_base+"/correction_files/2016/"
    #pu_reweight_SF_dir = corrections_dir+"pu_reweight/"
    #pu_reweight_filename = pu_reweight_SF_dir + "puWeights.json"
    #pu_reweight_corrname = "Collisions16_UltraLegacy_goldenJSON"


    pu_reweight_corrlib = correctionlib.CorrectionSet.from_file(pu_reweight_filename)[pu_reweight_corrname]

    """ #Lxplus won't let me use evaluate on a list for some reason? Maybe this will work in the future
    pu_reweight_values = pu_reweight_corrlib.evaluate(events.Pileup.nTrueInt, "nominal")
    pu_reweight_values_up = pu_reweight_corrlib.evaluate(events.Pileup.nTrueInt, "up")
    pu_reweight_values_down = pu_reweight_corrlib.evaluate(events.Pileup.nTrueInt, "down")
    """

    """
    pu_reweight_values = []
    pu_reweight_values_up = []
    pu_reweight_values_down = []
    for val in events.Pileup.nTrueInt:
        pu_reweight_values.append(pu_reweight_corrlib.evaluate(val, "nominal"))
        pu_reweight_values_up.append(pu_reweight_corrlib.evaluate(val, "up"))
        pu_reweight_values_down.append(pu_reweight_corrlib.evaluate(val, "down"))
    """
    #Actually all of these are wrong, the json files are for UltraLegacy and we are not using UL datasets ):
    pu_reweight_values = pu_reweight_corrlib.evaluate(np.array(events.Pileup.nTrueInt), "nominal")
    pu_reweight_values_up = pu_reweight_corrlib.evaluate(np.array(events.Pileup.nTrueInt), "up")
    pu_reweight_values_down = pu_reweight_corrlib.evaluate(np.array(events.Pileup.nTrueInt), "down")


    events[branch_name] = pu_reweight_values
    events[branch_name+"_up"] = pu_reweight_values_up
    events[branch_name+"_down"] = pu_reweight_values_down
