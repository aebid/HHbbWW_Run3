import uproot
import numpy as np
import awkward as ak
from scipy.stats import rv_discrete, mode
import vector
import time
from sklearn.utils.extmath import weighted_mode
from scipy.stats import mode
#from coffea.nanoevents.methods import vector


### Awkward implementation of HME ###
### https://github.com/tahuang1991/HeavyMassEstimator/tree/master ###

start_time = time.time()


#####
#Define PDFs
onshellWmass_y = [784.0, 896.0, 861.0, 1050.0, 1036.0, 1099.0, 1127.0, 1246.0, 1491.0, 1547.0, 1806.0, 1729.0, 2170.0, 2177.0, 2576.0, 2982.0, 3038.0, 3773.0, 3976.0, 4522.0, 4725.0, 5705.0, 6027.0, 6405.0, 6622.0, 7077.0, 6958.0, 8134.0, 8302.0, 9492.0, 9842.0, 11312.0, 12957.0, 16044.0, 19208.0, 25683.0, 35189.0, 54467.0, 100597.0, 217462.0, 308560.0, 152964.0, 58289.0, 26145.0, 14161.0, 8498.0, 5341.0, 3801.0, 2156.0, 1547.0, 1015.0, 889.0, 651.0, 518.0, 343.0, 273.0, 147.0, 84.0, 91.0, 56.0]
onshellWmass_x = np.linspace(40,99,60)


recobjetrescalec1pdfPU40_y =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.0, 4.0, 6.0, 7.0, 4.0, 4.0, 4.0, 9.0, 6.0, 16.0, 8.0, 7.0, 8.0, 5.0, 6.0, 5.0, 4.0, 8.0, 14.0, 7.0, 21.0, 9.0, 7.0, 14.0, 15.0, 16.0, 9.0, 19.0, 17.0, 28.0, 24.0, 40.0, 51.0, 58.0, 73.0, 88.0, 126.0, 173.0, 269.0, 371.0, 474.0, 594.0, 695.0, 702.0, 777.0, 735.0, 742.0, 636.0, 593.0, 467.0, 458.0, 392.0, 383.0, 341.0, 319.0, 293.0, 270.0, 239.0, 204.0, 184.0, 154.0, 151.0, 153.0, 133.0, 127.0, 101.0, 104.0, 120.0, 77.0, 70.0, 61.0, 57.0, 74.0, 57.0, 73.0, 59.0, 56.0, 47.0, 30.0, 24.0, 38.0, 46.0, 33.0, 32.0, 21.0, 29.0, 30.0, 21.0, 18.0, 25.0, 20.0, 17.0, 19.0, 6.0, 11.0, 14.0, 14.0, 9.0, 12.0, 4.0, 10.0, 11.0, 7.0, 5.0, 7.0, 4.0, 5.0, 4.0, 8.0, 3.0, 2.0, 0.0, 2.0, 8.0, 6.0, 5.0, 0.0, 2.0, 2.0, 6.0, 2.0, 1.0, 1.0, 1.0, 0.0, 2.0, 4.0, 0.0, 1.0, 2.0, 0.0, 2.0, 1.0, 2.0, 3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
recobjetrescalec1pdfPU40_x = np.linspace(0, 6.0, 300)
#####

f1 = uproot.open("GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M300_Run3Sync.root")
f2 = uproot.open("GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M450_Run3Sync.root")
f3 = uproot.open("GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M700_Run3Sync.root")



HME_mass_lists = []
HME_mass_average_it_lists = []
HME_mass_average_sols_lists = []
nTimesHME = []

flist = [f1, f2, f3]
#flist = [f2]
for f in flist:
    print("Starting")
    t = f['Double_Tree']
    events = t.arrays()

    events = events[(events.Double_Signal == 1) & ((events.Double_Res_2b == 1) | (events.Double_Res_1b == 1))]
    #Will fail if missing an object, just check that they all have some pT
    events = events[(events.lep0_pt >= 0) & (events.lep1_pt >= 0) & (events.ak4_jet1_pt >= 0) & (events.ak4_jet2_pt >= 0)]


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

    #Since we are correctiong bjets, this will be slightly different for each iteration too
    #Bjet corrections
    recobjetrescalec1pdfPU40_weights = recobjetrescalec1pdfPU40_y / np.sum(recobjetrescalec1pdfPU40_y)

    print("Starting bjet corrections")
    bjet_rescale_c1 = np.random.choice(recobjetrescalec1pdfPU40_x, p=recobjetrescalec1pdfPU40_weights, size=[len(events), iterations])

    x1 = (bjet1_p4.mass)**2
    x2 = 2*bjet_rescale_c1*(bjet0_p4.dot(bjet1_p4))
    x3 = (bjet_rescale_c1**2)*((bjet0_p4.mass)**2) - 125.0*125.0

    bjet_rescale_c2 = (-x2 + ((x2**2 - 4*x1*x3)**(0.5)))/(2*x1)

    retry_counter = 0
    while np.any(x2<0 | (x2*x2 - 4*x1*x3 < 0) | (x1 == 0) | (bjet_rescale_c2 < .0)):
        if retry_counter >= 10:
            print("Hit max number of retries, HME failed for some events")
            break
        print("Trying bjet corr again!")

        print("Change bool = ")
        print(x2<0 | (x2*x2 - 4*x1*x3 < 0) | (x1 == 0) | (bjet_rescale_c2 < .0))
        print("Old rescale c1 = ")
        print(bjet_rescale_c1)
        print("old masked = ", bjet_rescale_c1[x2<0 | (x2*x2 - 4*x1*x3 < 0) | (x1 == 0) | (bjet_rescale_c2 < .0)])
        bjet_rescale_c1 = np.where(
            x2<0 | (x2*x2 - 4*x1*x3 < 0) | (x1 == 0) | (bjet_rescale_c2 < .0),
                np.random.choice(recobjetrescalec1pdfPU40_x, p=recobjetrescalec1pdfPU40_weights),
                bjet_rescale_c1
        )
        print("New rescale = ")
        print(bjet_rescale_c1)
        #bjet_rescale_c1 = np.repeat(np.expand_dims(np.random.choice(recobjetrescalec1pdfPU40_x, p=recobjetrescalec1pdfPU40_weights, size=len(events)), 1), iterations, axis=1)

        x1 = (bjet1_p4.mass)**2
        x2 = 2*bjet_rescale_c1*(bjet0_p4.dot(bjet1_p4))
        x3 = (bjet_rescale_c1**2)*((bjet0_p4.mass)**2) - 125.0*125.0

        bjet_rescale_c2 = (-x2 + ((x2**2 - 4*x1*x3)**(0.5)))/(2*x1)

        retry_counter += 1

    htoBB = bjet0_p4 * bjet_rescale_c1 + bjet1_p4 * bjet_rescale_c2



    #But the b corrections also affect the MET!!!
    dmet_bcorr = vector.MomentumNumpy4D(
        {
            "px": bjet0_p4.px * (1 - bjet_rescale_c1) + bjet1_p4.px * (1 - bjet_rescale_c2),
            "py": bjet0_p4.py * (1 - bjet_rescale_c1) + bjet1_p4.py * (1 - bjet_rescale_c2),
            "pz": ak.to_numpy(np.repeat(np.expand_dims(events.met_pz, 1), iterations, axis=1)),
            "energy": ak.to_numpy(np.repeat(np.expand_dims(events.met_E, 1), iterations, axis=1)),
        }
    )

    met_sigma = 25.2
    met_smear = vector.MomentumNumpy4D(
        {
            "px": np.random.normal(0.0, met_sigma, random_size),
            "py": np.random.normal(0.0, met_sigma, random_size),
            "pz": ak.to_numpy(np.repeat(np.expand_dims(events.met_pz, 1), iterations, axis=1)),
            "energy": ak.to_numpy(np.repeat(np.expand_dims(events.met_E, 1), iterations, axis=1)),
        }
    )

    #Eventually I will use the cov CovMatrix
    """
    met_px = met_p4.px
    met_py = met_p4.py
    met_covXX = events.met_covXX
    met_covYY = events.met_covYY
    met_covXY = events.met_covXY

    met_pxpy = (np.array([met_px, met_py])).T
    met_cov_matrix = (np.array([[met_covXX, met_covXY], [met_covXY, met_covYY]])).T

    met_smear = vector.MomentumNumpy3D(
        {
            "px": bjet0_p4.px * (1 - bjet_rescale_c1) + bjet1_p4.px * (1 - bjet_rescale_c2),
            "py": bjet0_p4.py * (1 - bjet_rescale_c1) + bjet1_p4.py * (1 - bjet_rescale_c2),
            "pz": ak.to_numpy(np.repeat(np.expand_dims(events.met_pz, 1), iterations, axis=1)),
            "energy": ak.to_numpy(np.repeat(np.expand_dims(events.met_E, 1), iterations, axis=1)),
        }
    )
    """

    met_corr_p4 = met_p4 + dmet_bcorr + met_smear




    print("Starting htoWW")

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
            "px": met_corr_p4.px - nu_onshellW_l0_p4.px,
            "py": met_corr_p4.py - nu_onshellW_l0_p4.py,
        }
    )

    full_l0_p4 = lep0_p4 + lep1_p4 + nu_onshellW_l0_p4

    full_l0_p4_v2 = vector.MomentumNumpy4D(
        {
            "px": (full_l0_p4.pt**2 + full_l0_p4.mass**2)**(0.5),
            "py": np.zeros_like(full_l0_p4.pt),
            "pz": full_l0_p4.pz,
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
            "px": met_corr_p4.px - nu_onshellW_l1_p4.px,
            "py": met_corr_p4.py - nu_onshellW_l1_p4.py,
        }
    )


    full_l1_p4 = lep0_p4 + lep1_p4 + nu_onshellW_l1_p4



    full_l1_p4_v2 = vector.MomentumNumpy4D(
        {
            "px": (full_l1_p4.pt**2 + full_l1_p4.mass**2)**(0.5),
            "py": np.zeros_like(full_l1_p4.pt),
            "pz": full_l1_p4.pz,
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


    print("Checking final objects")

    #htoWW check
    l0_min_mass = np.expand_dims((htoWW_l0_min).mass, axis=2)
    l0_plus_mass = np.expand_dims((htoWW_l0_plus).mass, axis=2)
    l1_min_mass = np.expand_dims((htoWW_l1_min).mass, axis=2)
    l1_plus_mass = np.expand_dims((htoWW_l1_plus).mass, axis=2)
    htoWW_masses = np.concatenate((l0_min_mass, l0_plus_mass, l1_min_mass, l1_plus_mass), axis=2)
    #Now we want to use mean of the 4 cases
    average_htoWW_masses = np.nanmean(htoWW_masses, axis=2)


    #htoBB check
    l0_min_mass = np.expand_dims((htoBB).mass, axis=2)
    l0_plus_mass = np.expand_dims((htoBB).mass, axis=2)
    l1_min_mass = np.expand_dims((htoBB).mass, axis=2)
    l1_plus_mass = np.expand_dims((htoBB).mass, axis=2)
    htoBB_masses = np.concatenate((l0_min_mass, l0_plus_mass, l1_min_mass, l1_plus_mass), axis=2)
    #Now we want to use mean of the 4 cases
    average_htoBB_masses = np.nanmean(htoBB_masses, axis=2)


    #hh check
    l0_min_mass = np.expand_dims((htoWW_l0_min+htoBB).mass, axis=2)
    l0_plus_mass = np.expand_dims((htoWW_l0_plus+htoBB).mass, axis=2)
    l1_min_mass = np.expand_dims((htoWW_l1_min+htoBB).mass, axis=2)
    l1_plus_mass = np.expand_dims((htoWW_l1_plus+htoBB).mass, axis=2)
    hh_masses = np.concatenate((l0_min_mass, l0_plus_mass, l1_min_mass, l1_plus_mass), axis=2)
    #Now we want to use mean of the 4 cases
    average_hh_masses = np.nanmean(hh_masses, axis=2)
    #No we don't! What we want is a hist of all cases but weighted to nSolutions per case!
    #Count the number of solutions per iteration
    nSol = np.count_nonzero(np.isnan(hh_masses) == False, axis=2)
    weights = np.where(
        nSol >= 1,
            1/nSol,
            0.0
    )
    weights = np.repeat(np.expand_dims(weights, 2), 4, axis=2)
    #Simple way to 'weight' would be to repeat values by weights*4

    hh_flat = ak.flatten(hh_masses, axis=2)
    weights_flat = ak.flatten(weights, axis=2)
    valid_flag = hh_flat >= 0.0
    hh_flat = hh_flat[valid_flag]
    weights_flat = weights_flat[valid_flag]

    #HME_mass = ak.mean(hh_flat, weight=weights_flat, axis=1)

    print("Starting to find the mode of each event (most common bin)")
    HME_mass = []

    #Average all over whole it
    HME_mass_average_it = ak.to_list(ak.fill_none(ak.nan_to_num(ak.mean(hh_flat, weight=weights_flat, axis=1)), 0.0))
    #Average over all sols, but mode of that over it
    tmp_avgsols = ak.mean(hh_masses, weight=weights, axis=2)
    HME_mass_average_sols = ak.to_list(ak.nan_to_num(mode(ak.values_astype(ak.mask(tmp_avgsols, tmp_avgsols > 0), "int64"), axis=1)[0]))

    for i in range(len(hh_flat)):
        if len(hh_flat[i]) == 0:
            print("HME Failed at event ", i)
            HME_mass.append(0.0)
            #HME_mass_average_it.append(0.0)
            #HME_mass_average_sols.append(0.0)
            continue
        HME_mass.append(weighted_mode(ak.values_astype(hh_flat[i], "int64"), weights_flat[i])[0][0])




    file_time = time.time()
    print("File runtime was ", file_time - start_time)
    HME_mass_lists.append(HME_mass)
    HME_mass_average_it_lists.append(HME_mass_average_it)
    HME_mass_average_sols_lists.append(HME_mass_average_sols)
    print("Had ", np.count_nonzero(HME_mass)/len(HME_mass), " successrate")
    #nTimesHME.append(mode(ak.values_astype(awk_hh_masses, "int64"))[1])

end_time = time.time()
print("Total runtime was ", end_time - start_time)



import matplotlib.pyplot as plt

for i in range(len(flist)):
    plt.hist(HME_mass_lists[i], bins=80, range=(200,1000), density=True)

plt.show()


def debug_hme(gh, gw, geta, gphi, tmp_lep0_p4, tmp_lep1_p4, tmp_met_p4):
    nu0_p4 = vector.MomentumObject4D(
        pt=(gw**2) / (2*tmp_lep0_p4.pt * (np.cosh(geta - tmp_lep0_p4.eta) - np.cos(gphi - tmp_lep0_p4.phi))),
        eta=geta,
        phi=gphi,
        mass=0,
    )
    print("nu0 = ", nu0_p4)

    met_min_nu0 = vector.MomentumObject2D(
        px=(tmp_met_p4.px - nu0_p4.px),
        py=(tmp_met_p4.py - nu0_p4.py),
    )
    print("met minus nu0 = ", met_min_nu0)


    leps_plus_nu0 = tmp_lep0_p4 + tmp_lep1_p4 + nu0_p4
    print("leps plus nu0 = ", leps_plus_nu0)


    tmp_4D = vector.MomentumObject4D(
        px=(leps_plus_nu0.pt**2 + leps_plus_nu0.mass**2)**(0.5),
        py=0,
        pz=leps_plus_nu0.pz,
        energy=leps_plus_nu0.energy,
    )
    print("temporary vec = ", tmp_4D)

    ##chdeta = (pow(hMass, 2) + 2*(nu_pxpy.Px()*tmp_p4.Px() + nu_pxpy.Py()*tmp_p4.Py()) - pow(tmp_p4.M(), 2))/(2.0*tmp_p4_v2.Pt()*tmp_nu_pt)

    #print("Showing the chdeta calc")
    #print(gh)
    #print(met_min_nu0.px)
    #print(leps_plus_nu0.px)
    #print(met_min_nu0.py)
    #print(leps_plus_nu0.py)
    #print(leps_plus_nu0.mass)
    #print(tmp_4D.pt)
    #print(met_min_nu0.pt)

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
