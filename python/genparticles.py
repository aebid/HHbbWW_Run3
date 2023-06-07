import awkward as ak
import numpy as np

from functools import reduce

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.nanoevents.methods import vector

def find_genpart(genpart, pdgid, ancestors):
    """
    Find gen level particles given pdgId (and ancestors ids) 

    Parameters:
    genpart (GenPart): NanoAOD GenPart collection.
    pdgid (list): pdgIds for the target particles.
    idmother (list): pdgIds for the ancestors of the target particles.

    Returns:
    NanoAOD GenPart collection
    """

    def check_id(p):
        return np.abs(genpart.pdgId) == p

    pid = reduce(np.logical_or, map(check_id, pdgid))

    if ancestors:
        ancs, ancs_idx = [], []
        for i, mother_id in enumerate(ancestors):
            if i == 0:
                mother_idx = genpart[pid].genPartIdxMother
            else:
                mother_idx = genpart[ancs_idx[i-1]].genPartIdxMother
            ancs.append(np.abs(genpart[mother_idx].pdgId) == mother_id)
            ancs_idx.append(mother_idx)

        decaymatch =  reduce(np.logical_and, ancs)
        return genpart[pid][decaymatch]

    return genpart[pid]

def single_lepton_genpart(EventProcess):
    events = EventProcess.events
    genparts = events.GenPart
    
    # b-quarks from Higgs decay
    bFromH = find_genpart(genparts, [5], [25])
    
    # H -> WW
    # light quarks W decay
    qFromW = find_genpart(genparts, [1, 2 ,3, 4], [24, 25])
    
    # leptons from W decay
    lepFromW = find_genpart(genparts, [11, 13, 15], [24, 25])
    nuFromW = find_genpart(genparts, [12, 14, 16], [24, 25])

    events = ak.with_field(events, bFromH.pt, "bFromH_pt")
    events = ak.with_field(events, bFromH.eta, "bFromH_eta")
    events = ak.with_field(events, bFromH.phi, "bFromH_phi")
    
    events = ak.with_field(events, qFromW.pt, "qFromW_pt")
    events = ak.with_field(events, qFromW.eta, "qFromW_eta")
    events = ak.with_field(events, qFromW.phi, "qFromW_phi")

    events = ak.with_field(events, lepFromW.pt, "lepFromW_pt")
    events = ak.with_field(events, lepFromW.eta, "lepFromW_eta")
    events = ak.with_field(events, lepFromW.phi, "lepFromW_phi")
    
    events = ak.with_field(events, nuFromW.pt, "nuFromW_pt")
    events = ak.with_field(events, nuFromW.eta, "nuFromW_eta")
    events = ak.with_field(events, nuFromW.phi, "nuFromW_phi")

def double_lepton_genpart(EventProcess):
    events = EventProcess.events
    genparts = events.GenPart
    
    # b-quarks from Higgs decay
    bFromH = find_genpart(genparts, [5], [25])
    
    # H -> WW
    # leptons from W decay
    lepFromW = find_genpart(genparts, [11, 13, 15], [24, 25])
    nuFromW = find_genpart(genparts, [12, 14, 16], [24, 25])

    events = ak.with_field(events, bFromH.pt, "bFromH_pt")
    events = ak.with_field(events, bFromH.eta, "bFromH_eta")
    events = ak.with_field(events, bFromH.phi, "bFromH_phi")
    
    events = ak.with_field(events, lepFromW.pt, "lepFromW_pt")
    events = ak.with_field(events, lepFromW.eta, "lepFromW_eta")
    events = ak.with_field(events, lepFromW.phi, "lepFromW_phi")
    
    events = ak.with_field(events, nuFromW.pt, "nuFromW_pt")
    events = ak.with_field(events, nuFromW.eta, "nuFromW_eta")
    events = ak.with_field(events, nuFromW.phi, "nuFromW_phi")
