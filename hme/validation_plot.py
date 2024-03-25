import uproot
import matplotlib.pyplot as plt

fname_m300 = "/Users/devin/Desktop/HHbbWW_Run3.nosync/dnn/input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300_PreEE.root"
fname_m450 = "/Users/devin/Desktop/HHbbWW_Run3.nosync/dnn/input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_PreEE.root"
fname_m700 = "/Users/devin/Desktop/HHbbWW_Run3.nosync/dnn/input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700_PreEE.root"


fname_list = [fname_m300, fname_m450, fname_m700]

for fname in fname_list:
    events = uproot.open(fname)['Double_HME_Tree'].arrays()

    mask_res1b = (events.Double_Signal == 1) & (events.Double_Res_1b == 1)
    mask_res2b = (events.Double_Signal == 1) & (events.Double_Res_2b == 1)
    mask_boost = (events.Double_Signal == 1) & (events.Double_HbbFat == 1)

    events_res1b = events[mask_res1b]
    events_res2b = events[mask_res2b]
    events_boost = events[mask_boost]

    plotrange = (0.0, 1000.0)
    plotbins = 100

    mass = 0.0
    if "300" in fname: mass = 300
    if "450" in fname: mass = 450
    if "700" in fname: mass = 700


    plt.hist(events_res1b.HME, bins=plotbins, range=plotrange, histtype='step', label='Signal M{m} Res1b'.format(m = mass), alpha=0.5)
    plt.hist(events_res2b.HME, bins=plotbins, range=plotrange, histtype='step', label='Signal M{m} Res2b'.format(m = mass), alpha=0.5)
    plt.hist(events_boost.HME, bins=plotbins, range=plotrange, histtype='step', label='Signal M{m} Boost'.format(m = mass), alpha=0.5)

    plt.legend(loc='upper right')

    plt.savefig("hme_m{m}.pdf".format(m = mass))

    plt.clf()
