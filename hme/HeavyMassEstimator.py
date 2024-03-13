import uproot
import numpy as np
import awkward as ak
from scipy.stats import rv_discrete
import vector
#from coffea.nanoevents.methods import vector


### Awkward implementation of HME ###
### https://github.com/tahuang1991/HeavyMassEstimator/tree/master ###



#####
#Define PDFs
onshellWmass_y = [784.0, 896.0, 861.0, 1050.0, 1036.0, 1099.0, 1127.0, 1246.0, 1491.0, 1547.0, 1806.0, 1729.0, 2170.0, 2177.0, 2576.0, 2982.0, 3038.0, 3773.0, 3976.0, 4522.0, 4725.0, 5705.0, 6027.0, 6405.0, 6622.0, 7077.0, 6958.0, 8134.0, 8302.0, 9492.0, 9842.0, 11312.0, 12957.0, 16044.0, 19208.0, 25683.0, 35189.0, 54467.0, 100597.0, 217462.0, 308560.0, 152964.0, 58289.0, 26145.0, 14161.0, 8498.0, 5341.0, 3801.0, 2156.0, 1547.0, 1015.0, 889.0, 651.0, 518.0, 343.0, 273.0, 147.0, 84.0, 91.0, 56.0]
onshellWmass_x = np.linspace(40,99,60)
#####

f = uproot.open("GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M450_Run3Sync.root")
t = f['Double_Tree']
events = t.arrays()

events = events[events.Double_Signal == 1]


iterations = 1000

random_size = [len(events), iterations]

eta_gen = np.random.uniform(-6,6, random_size)
phi_gen = np.random.uniform(-3.1415926, 3.1415926, random_size)
hmass_gen = np.random.normal(125.03, 0.004, random_size)

lep0_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(np.repeat(np.expand_dims(events.lep0_pt, 1), iterations, axis=1)),
        "eta": ak.to_numpy(np.repeat(np.expand_dims(events.lep0_eta, 1), iterations, axis=1)),
        "phi": ak.to_numpy(np.repeat(np.expand_dims(events.lep0_phi, 1), iterations, axis=1)),
        "energy": ak.to_numpy(np.repeat(np.expand_dims(events.lep0_E, 1), iterations, axis=1)),
    }
)

lep1_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(np.repeat(np.expand_dims(events.lep1_pt, 1), iterations, axis=1)),
        "eta": ak.to_numpy(np.repeat(np.expand_dims(events.lep1_eta, 1), iterations, axis=1)),
        "phi": ak.to_numpy(np.repeat(np.expand_dims(events.lep1_phi, 1), iterations, axis=1)),
        "energy": ak.to_numpy(np.repeat(np.expand_dims(events.lep1_E, 1), iterations, axis=1)),
    }
)

met_p4 = vector.MomentumNumpy4D(
    {
        "px": ak.to_numpy(np.repeat(np.expand_dims(events.met_px, 1), iterations, axis=1)),
        "py": ak.to_numpy(np.repeat(np.expand_dims(events.met_py, 1), iterations, axis=1)),
        "pz": ak.to_numpy(np.repeat(np.expand_dims(events.met_pz, 1), iterations, axis=1)),
        "energy": ak.to_numpy(np.repeat(np.expand_dims(events.met_E, 1), iterations, axis=1)),
    }
)

bjet0_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet0_pt, 1), iterations, axis=1)),
        "eta": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet0_eta, 1), iterations, axis=1)),
        "phi": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet0_phi, 1), iterations, axis=1)),
        "energy": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet0_E, 1), iterations, axis=1)),
    }
)

bjet1_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet1_pt, 1), iterations, axis=1)),
        "eta": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet1_eta, 1), iterations, axis=1)),
        "phi": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet1_phi, 1), iterations, axis=1)),
        "energy": ak.to_numpy(np.repeat(np.expand_dims(events.ak4_jet1_E, 1), iterations, axis=1)),
    }
)


#Tao's getOnShellWMass function is very confusing, I'm just going to make a new one and sample the PDF directly
#First issue was to get the PDF and increase resolution (orignal was 1bin/GeV, but we want fine resolution so we interpolate and create 10x as many)
#We probably want to change this to use a function instead of interp
onshellWmass_x_new = np.linspace(40, 99.9, 600)
onshellWmass_y_new = [np.interp(x, onshellWmass_x, onshellWmass_y) for x in np.linspace(40.0, 99.9, 600)]
onshellWmass_weights = onshellWmass_y_new / np.sum(onshellWmass_y_new)

wmass_gen = np.random.choice(onshellWmass_x_new, p=onshellWmass_weights, size=random_size)


#Here tao starts the 4 solutions
#4 cases
#Lep0 is onshell
    #Nutrino + eta
    #Nutrino - eta
#Lep1 is onshell
    #Nutrino + eta
    #Nutrino - eta


#L0 is onshell
nu_onshellW_pt_l0 = np.array((wmass_gen**2) / (2*lep0_p4.pt * (np.cosh(eta_gen - lep0_p4.eta) - np.cos(phi_gen - lep0_p4.phi))))

nu_onshellW_l0_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(nu_onshellW_pt_l0),
        "eta": ak.to_numpy(eta_gen),
        "phi": ak.to_numpy(phi_gen),
        "mass": np.zeros_like(nu_onshellW_pt_l0),
    }
)

nu2_l0_p2 = vector.MomentumNumpy2D(
    {
        "px": met_p4.px - nu_onshellW_l0_p4.px,
        "py": met_p4.py - nu_onshellW_l0_p4.py,
    }
)

full_l0_p4 = lep0_p4 + lep1_p4 + nu_onshellW_l0_p4

full_l0_p4_v2 = vector.MomentumNumpy4D(
    {
        "pt": (full_l0_p4.pt**2 + full_l0_p4.mass**2)**(0.5),
        "eta": np.zeros_like(full_l0_p4.pt),
        "phi": full_l0_p4.pz,
        "energy": full_l0_p4.energy,
    }
)

coshdeta_l0 = (hmass_gen**2 + 2*(nu2_l0_p2.px * full_l0_p4.px + nu2_l0_p2.py * full_l0_p4.py) - full_l0_p4.mass**2) / (2.0*full_l0_p4_v2.pt * nu2_l0_p2.pt)
deta_l0 = np.arccosh(coshdeta_l0)

valid_mask_l0 = coshdeta_l0 >= 1.0

#Minus eta case
nu2_l0_min_p4 = vector.MomentumNumpy4D(
    {
        "pt": nu2_l0_p2.pt,
        "eta": full_l0_p4_v2.eta - deta_l0,
        "phi": nu2_l0_p2.phi,
        "mass": np.zeros_like(nu2_l0_p2.pt),
    }
)

htoWW_l0_min = full_l0_p4 + nu2_l0_min_p4

#Plus eta case
nu2_l0_plus_p4 = vector.MomentumNumpy4D(
    {
        "pt": nu2_l0_p2.pt,
        "eta": full_l0_p4_v2.eta + deta_l0,
        "phi": nu2_l0_p2.phi,
        "mass": np.zeros_like(nu2_l0_p2.pt),
    }
)

htoWW_l0_plus = full_l0_p4 + nu2_l0_plus_p4

#L1 is onshell

nu_onshellW_pt_l1 = np.array((wmass_gen**2) / (2*lep1_p4.pt * (np.cosh(eta_gen - lep1_p4.eta) - np.cos(phi_gen - lep1_p4.phi))))



nu_onshellW_l1_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(nu_onshellW_pt_l1),
        "eta": ak.to_numpy(eta_gen),
        "phi": ak.to_numpy(phi_gen),
        "mass": np.zeros_like(nu_onshellW_pt_l1),
    }
)

nu2_l1_p2 = vector.MomentumNumpy2D(
    {
        "px": met_p4.px - nu_onshellW_l1_p4.px,
        "py": met_p4.py - nu_onshellW_l1_p4.py,
    }
)


full_l1_p4 = lep0_p4 + lep1_p4 + nu_onshellW_l1_p4



full_l1_p4_v2 = vector.MomentumNumpy4D(
    {
        "pt": (full_l1_p4.pt**2 + full_l1_p4.mass**2)**(0.5),
        "eta": np.zeros_like(full_l1_p4.pt),
        "phi": full_l1_p4.pz,
        "energy": full_l1_p4.energy,
    }
)

coshdeta_l1 = (hmass_gen**2 + 2*(nu2_l1_p2.px * full_l1_p4.px + nu2_l1_p2.py * full_l1_p4.py) - full_l1_p4.mass**2) / (2.0*full_l1_p4_v2.pt * nu2_l1_p2.pt)
deta_l1 = np.arccosh(coshdeta_l1)

valid_mask_l1 = coshdeta_l1 >= 1.0

#Minus eta case
nu2_l1_min_p4 = vector.MomentumNumpy4D(
    {
        "pt": nu2_l1_p2.pt,
        "eta": full_l1_p4_v2.eta - deta_l1,
        "phi": nu2_l1_p2.phi,
        "mass": np.zeros_like(nu2_l1_p2.pt),
    }
)

htoWW_l1_min = full_l1_p4 + nu2_l1_min_p4

#Plus eta case
nu2_l1_plus_p4 = vector.MomentumNumpy4D(
    {
        "pt": nu2_l1_p2.pt,
        "eta": full_l1_p4_v2.eta + deta_l1,
        "phi": nu2_l1_p2.phi,
        "mass": np.zeros_like(nu2_l1_p2.pt),
    }
)

htoWW_l1_plus = full_l1_p4 + nu2_l1_plus_p4



#Successful iteration bool
valid_hme = valid_mask_l0 | valid_mask_l1



hh = bjet0_p4 + bjet1_p4 + htoWW_l0_min






def debug_hme(gh, gw, geta, gphi, tmp_lep0_p4, tmp_lep1_p4, tmp_met_p4):
    nu0_p4 = vector.MomentumObject4D(
        pt=(gw**2) / (2*tmp_lep0_p4.pt * (np.cosh(geta - tmp_lep0_p4.eta) - np.cos(gphi - tmp_lep0_p4.phi))),
        eta=geta,
        phi=gphi,
        mass=0,
    )
    print("nu0 = ", nu0_p4)

    print(tmp_met_p4.px)
    print(nu0_p4.px)
    print(tmp_met_p4.py)
    print(nu0_p4.py)

    met_min_nu0 = vector.MomentumObject2D(
        px=(tmp_met_p4.px - nu0_p4.px),
        py=(tmp_met_p4.py - nu0_p4.py),
    )
    print("met minus nu0 = ", met_min_nu0)


    leps_plus_nu0 = tmp_lep0_p4 + tmp_lep1_p4 + nu0_p4
    print("leps plus nu0 = ", leps_plus_nu0)


    tmp_4D = vector.MomentumObject4D(
        pt=(leps_plus_nu0.pt**2 + leps_plus_nu0.mass**2)**(0.5),
        eta=0,
        phi=leps_plus_nu0.pz,
        energy=leps_plus_nu0.energy,
    )
    print("temporary vec = ", tmp_4D)

    chdeta = (pow(hMass, 2) + 2*(nu_pxpy.Px()*tmp_p4.Px() + nu_pxpy.Py()*tmp_p4.Py()) - pow(tmp_p4.M(), 2))/(2.0*tmp_p4_v2.Pt()*tmp_nu_pt)


    coshdeta = (gh**2 + 2*(met_min_nu0.px * leps_plus_nu0.px + met_min_nu0.py * leps_plus_nu0.py) - leps_plus_nu0.mass**2) / (2.0*tmp_4D.pt * met_min_nu0.pt)
    deta = np.arccosh(coshdeta)
    print("coshdeta and deta = ", coshdeta, " ", deta)

    nu1_p4 = vector.MomentumObject4D(
        pt=met_min_nu0.pt,
        eta=tmp_4D.eta - deta,
        phi=met_min_nu0.phi,
        mass=0,
    )
    print("nu1 p4 = ", nu1_p4)


    htoWW = leps_plus_nu0 + nu1_p4
    print("htoWW = ", htoWW)
    print("h mass = ", htoWW.mass)
