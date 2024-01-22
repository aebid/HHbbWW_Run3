import awkward as ak
from coffea.lookup_tools import extractor
from coffea.btag_tools import BTagScaleFactor
from coffea.jetmet_tools import FactorizedJetCorrector, JetCorrectionUncertainty, JECStack, CorrectedJetsFactory, JetResolution, JetResolutionScaleFactor, CorrectedMETFactory
import numpy as np
import math


def add_event_weight(EventProcess):
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

    #First lets find the selected leptons the same as in the event selection process
    leptons_fakeable = ak.concatenate([electrons.mask[electrons.fakeable], muons.mask[muons.fakeable]], axis=1)

    if not ak.all(ak.all(ak.is_none(leptons_fakeable, axis=1), axis=1)):
        leptons_fakeable = leptons_fakeable[ak.argsort(leptons_fakeable.conept, axis=1, ascending=False)]

    leading_leptons = ak.pad_none(leptons_fakeable, 2)[:,0]
    subleading_leptons = ak.pad_none(leptons_fakeable, 2)[:,1]

    #Prepare the event weight variables
    single_event_weight = ak.ones_like(events.run)
    double_event_weight = ak.ones_like(events.run)

    #Add lepton ID SF
    single_event_weight = single_event_weight * leading_leptons.lepton_ID_SF
    double_event_weight = double_event_weight * leading_leptons.lepton_ID_SF
    double_event_weight = double_event_weight * subleading_leptons.lepton_ID_SF

    #Add lepton ttH relaxed
    single_event_weight = single_event_weight * leading_leptons.lepton_relaxed_TTH_SF
    double_event_weight = double_event_weight * leading_leptons.lepton_relaxed_TTH_SF
    double_event_weight = double_event_weight * subleading_leptons.lepton_relaxed_TTH_SF

    #Add lepton ttH tight (value is one, tight is only used for up/down, for consistency will still put it here)
    single_event_weight = single_event_weight * leading_leptons.lepton_tight_TTH_SF
    double_event_weight = double_event_weight * leading_leptons.lepton_tight_TTH_SF
    double_event_weight = double_event_weight * subleading_leptons.lepton_tight_TTH_SF

    #Add single lepton trigger
    single_event_weight = single_event_weight * leading_leptons.single_lepton_trigger_SF

    #Must calculate double lepton trigger SF here since it is every based not lepton based
    double_lepton_trigger_SF = ak.ones_like(events)
    double_lepton_trigger_SF = ak.where(
        events.is_mm,
            0.99,
            ak.where(
                events.is_ee,
                    ak.where(
                        subleading_leptons.pt > 25,
                            1.00,
                            0.98
                    ),
                    ak.where(
                        events.is_em,
                            1.00,
                            1.00
                    )
            )
    )
    double_event_weight = double_event_weight * double_lepton_trigger_SF

    if EventProcess.dnn_truth_value == 1:
        #Add ttbar reweighting
        single_event_weight = single_event_weight * events.tt_reweight
        double_event_weight = double_event_weight * events.tt_reweight

    #PU Reweight
    #PU Weights are wrong, LUTs are for UltraLegacy but we are not using UL datasets
    #single_event_weight = single_event_weight * events.pu_reweight
    #double_event_weight = double_event_weight * events.pu_reweight



    events["single_event_weight"] = single_event_weight
    events["double_event_weight"] = double_event_weight
