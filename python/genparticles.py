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
        return np.abs(genpart.GenPart_pdgId) == p

    pid = reduce(np.logical_or, map(check_id, pdgid))

    if ancestors:
        ancs, ancs_idx = [], []
        for i, mother_id in enumerate(ancestors):
            if i == 0:
                mother_idx = genpart[pid].GenPart_genPartIdxMother
            else:
                mother_idx = genpart[ancs_idx[i-1]].GenPart_genPartIdxMother
            ancs.append(np.abs(genpart[mother_idx].GenPart_pdgId) == anc_id)
            anc_idx.append(mother_idx)

        decaymatch =  reduce(np.logical_and, ancs)
        return genpart[pid][decaymatch]

    return genpart[pid]

def genpart_single_lepton(EventProcessor):
    pass

def genpart_double_lepton(EventProcessor):
    pass
