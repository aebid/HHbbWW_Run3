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


iterations = 100

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


#Tao's getOnShellWMass function is very confusing, I'm just going to make a new one and sample the PDF directly
#First issue was to get the PDF and increase resolution (orignal was 1bin/GeV, but we want fine resolution so we interpolate and create 10x as many)
#We probably want to change this to use a function instead of interp
onshellWmass_x_new = np.linspace(40, 99.9, 600)
onshellWmass_y_new = [np.interp(x, onshellWmass_x, onshellWmass_y) for x in np.linspace(40.0, 99.9, 600)]
onshellWmass_weights = onshellWmass_y_new / np.sum(onshellWmass_y_new)

wmass_gen = np.random.choice(onshellWmass_x_new, p=onshellWmass_weights, size=random_size)


#Here tao starts the 4 solutions
#2 cases though, basically is Lep0 or Lep1 the onshell one?

nu_onshellW_pt_l0 = np.array((wmass_gen**2) / (2*lep0_p4.pt * (np.cosh(eta_gen - lep0_p4.eta) - np.cos(phi_gen - lep0_p4.phi))))


nu_onshellW_p4 = vector.MomentumNumpy4D(
    {
        "pt": ak.to_numpy(nu_onshellW_pt_l0),
        "eta": ak.to_numpy(eta_gen),
        "phi": ak.to_numpy(phi_gen),
        "mass": np.zeros_like(nu_onshellW_pt_l0),
    }
)


full_p4 = lep0_p4 + lep1_p4 + nu_onshellW_p4
nu2_px = met_p4.px - nu_onshellW_p4.px
nu2_py = met_p4.py - nu_onshellW_p4.py
nu2_pt = ((nu2_px**2) + (nu2_py**2))**(0.5)


full_p4_v2 = vector.MomentumNumpy4D(
    {
        "pt": (full_p4.pt**2 + full_p4.mass**2)**(0.5),
        "eta": np.zeros_like(full_p4.pt),
        "phi": full_p4.pz,
        "energy": full_p4.energy,
    }
)

coshdeta = (hmass_gen**2 + 2*(nu2_px * full_p4.px + nu2_py * full_p4.py - full_p4.mass**2)) / (2.0*full_p4_v2.pt * nu2_pt)
deta = np.arccosh(coshdeta)


nu2_p4 = vector.MomentumNumpy4D(
    {
        "px": nu2_px,
        "py": nu2_py,
        "pz": np.zeros_like(nu2_px),
        "mass": np.zeros_like(nu2_px),
    }
)

htoWW = full_p4 + nu2_p4


#nu_onshellW_pt_l1 = (events.wmass_gen**2) / (2*events.lep1_pt * (np.cosh(events.eta_gen - events.lep1_eta) - np.cos(events.phi_gen - events.lep1_phi)))




"""
nuP4FromOffshellW(met, lep1, lep2, nu1, nu2, case, hMass)
        tmp_p4 = lepton1_p4 + lepton2_p4 + nu1_p4
        tmp_nu_px = met.Px() - nu1_p4.Px()
        tmp_nu_py = met.Py() - nu1_p4.Py()
        nu_pxpy =  ROOT.TVector2(tmp_nu_px, tmp_nu_py)
        tmp_nu_pt = nu_pxpy.Mod()
        tmp_p4_v2 = ROOT.TLorentzVector(sqrt(pow(tmp_p4.Pt(), 2) + pow(tmp_p4.M(), 2)), 0, tmp_p4.Pz(), tmp_p4.Energy())
        chdeta = (pow(hMass, 2) + 2*(nu_pxpy.Px()*tmp_p4.Px() + nu_pxpy.Py()*tmp_p4.Py()) - pow(tmp_p4.M(), 2))/(2.0*tmp_p4_v2.Pt()*tmp_nu_pt)
        if chdeta < 1.0:
            #no solution if chdeta<1.0
            #print("no solution since chdeta<1.0, chdeta ",chdeta)
            nu2_p4.SetPtEtaPhiM(0.0, 0.0, 0.0, 0.0)
            return False
        tmp_nu_phi = nu_pxpy.Phi_mpi_pi(nu_pxpy.Phi())
        deta = acosh( chdeta )
        tmp_nu_eta = 0.0
        if case == 1:
            tmp_nu_eta = tmp_p4_v2.Eta() - deta
        else :
            tmp_nu_eta = tmp_p4_v2.Eta() + deta
        if (abs(tmp_nu_eta) > 7.0):
        #very unlikely solution
            print("tmp_nu_eta ",tmp_nu_eta, " very unlikely solution, pass")
            nu2_p4.SetPtEtaPhiM(0.0, 0.0, 0.0, 0.0)
            return False
        nu2_p4.SetPtEtaPhiM(tmp_nu_pt, tmp_nu_eta, tmp_nu_phi, 0.0)
        htoWW_tmp = tmp_p4 + nu2_p4
        if abs(htoWW_tmp.M() - hMass) > 1.0:
            print("Warning!!! gen hmass ", hMass, " HME htoWW mass ", htoWW_tmp.M())
        return True

"""
