import awkward as ak
from coffea.lookup_tools import extractor
from coffea.btag_tools import BTagScaleFactor
from coffea.jetmet_tools import FactorizedJetCorrector, JetCorrectionUncertainty, JECStack, CorrectedJetsFactory, JetResolution, JetResolutionScaleFactor, CorrectedMETFactory
import numpy as np

def ak4_jet_corrector(EventProcess):
    events = EventProcess.events
    jets = events.Jet
    jetmet_files = EventProcess.jetmet_files
    isMC = EventProcess.isMC
    debug = EventProcess.debug

    jec_files = jetmet_files["ak4_jec_files"]
    junc_file = jetmet_files["ak4_junc_file"]
    jer_file = jetmet_files["ak4_jer_file"]
    jersf_file = jetmet_files["ak4_jersf_file"]

    extractor_list = []
    stack_names = []

    for stack_file in (jec_files+junc_file+jer_file+jersf_file):
        extractor_list.append("* * " + stack_file)
        stack_names.append((stack_file.split('/')[-1]).split('.')[0])
        #Stack name needs to take just the file names first portion, so
        #correction_files/jetmet/Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi.jec.txt
        #Goes to
        #Summer19UL16_V7_MC_L1FastJet_AK4PFPuppi

    ext = extractor()
    ext.add_weight_sets(extractor_list)
    ext.finalize()
    evaluator = ext.make_evaluator()
    jec_stack = JECStack({name: evaluator[name] for name in stack_names})

    name_map = jec_stack.blank_name_map
    name_map['JetPt'] = 'pt'
    name_map['JetMass'] = 'mass'
    name_map['JetEta'] = 'eta'
    name_map['JetA'] = 'area'

    jets['pt_raw'] = (1 - jets['rawFactor']) * jets['pt']
    jets['mass_raw'] = (1 - jets['rawFactor']) * jets['mass']
    if isMC: #Hard fix for jetmet_tools bug? https://github.com/CoffeaTeam/coffea/blob/b4589704dc72da509927ea7a15b1996e15ae7702/coffea/jetmet_tools/CorrectedJetsFactory.py#L135-L139
        jets['pt_gen'] = ak.values_astype(ak.fill_none(jets.matched_gen.pt, 0), np.float32)
        name_map['ptGenJet'] = 'pt_gen'
    #jets['rho'] = ak.broadcast_arrays(EventProcess.events.fixedGridRhoFastjetAll, jets.pt)[0]
    jets['rho'] = ak.broadcast_arrays(EventProcess.events.Rho.fixedGridRhoFastjetAll, jets.pt)[0]
    name_map['ptRaw'] = 'pt_raw'
    name_map['massRaw'] = 'mass_raw'
    name_map['Rho'] = 'rho'

    events_cache = EventProcess.events.caches[0]

    if jec_files == True:
        fjc_dict = {}
        for stack_file in jec_files:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            fjc_dict[filename] = evaluator[filename]
        fjc = FactorizedJetCorrector(
            **fjc_dict
        )

    if junc_file == True:
        jcu_dict = {}
        for stack_file in junc_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            jcu_dict[filename] = evaluator[filename]
        jcu = JetCorrectionUncertainty(
            **jcu_dict
        )

    if jer_file == True:
        jer_dict = {}
        for stack_file in jer_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            jer_dict[filename] = evaluator[filename]
        jr = JetResolution(
            **jer_dict
        )


    if jersf_file == True:
        jersf_dict = {}
        for stack_file in jersf_file:
            filename = (stack_file.split('/')[-1]).split('.')[0]
            jersf_dict[filename] = evaluator[filename]
        jersf = JetResolutionScaleFactor(
            **jersf_dict
        )

    jet_factory = CorrectedJetsFactory(name_map, jec_stack)
    if not isMC: #Hard fix for jetmet_tools bug? https://github.com/CoffeaTeam/coffea/blob/b4589704dc72da509927ea7a15b1996e15ae7702/coffea/jetmet_tools/CorrectedJetsFactory.py#L135-L139
        jet_factory.name_map["ptGenJet"] = jet_factory.name_map["JetPt"]
    events.Jet = ak.pad_none(jet_factory.build(jets, lazy_cache=events_cache), 4)

    events.Jet["par_jet_rescale"] = events.Jet.pt_orig/events.Jet.pt
    events.Jet["par_JER_up"] = events.Jet.JER.up.pt/events.Jet.pt
    events.Jet["par_JER_down"] = events.Jet.JER.down.pt/events.Jet.pt
    events.Jet["par_JES_up"] = events.Jet.JES_jes.up.pt/events.Jet.pt
    events.Jet["par_JES_down"] = events.Jet.JES_jes.down.pt/events.Jet.pt


def btag_SF(EventProcess):
    events = EventProcess.events
    jets = events.Jet
    do_systematics = EventProcess.do_systematics
    btag_SF_file =  EventProcess.btag_SF_file
    debug = EventProcess.debug
    if debug: print("Starting btag SF")

    btag_sf = BTagScaleFactor(btag_SF_file, "reshape", methods="iterativefit,iterativefit,iterativefit")
    events.Jet = ak.with_field(events.Jet, btag_sf.eval("central", jets.hadronFlavour, abs(jets.eta), jets.pt, discr=jets.btagDeepFlavB), "btag_SF_central")
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
