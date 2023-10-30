import ROOT
import tdrStyle

ROOT.gROOT.SetBatch(1)
tdrStyle.setTDRStyle()

TT_binned = ROOT.TH1D("TT_binned", "TT_binned", 75, 0, 75)
TT_binned.SetFillColor(ROOT.kOrange+2)
DY_binned = ROOT.TH1D("DY_binned", "DY_binned", 75, 0, 75)
DY_binned.SetFillColor(ROOT.kAzure-7)
ST_binned = ROOT.TH1D("ST_binned", "ST_binned", 75, 0, 75)
ST_binned.SetFillColor(ROOT.kRed+2)
WJets_binned = ROOT.TH1D("WJets_binned", "WJets_binned", 75, 0, 75)
WJets_binned.SetFillColor(ROOT.kPink-5)
VVV_binned = ROOT.TH1D("VVV_binned", "VVV_binned", 75, 0, 75)
VVV_binned.SetFillColor(ROOT.kYellow-3)
SMH_binned = ROOT.TH1D("SMH_binned", "SMH_binned", 75, 0, 75)
SMH_binned.SetFillColor(ROOT.kTeal-5)
Rare_binned = ROOT.TH1D("Rare_binned", "Rare_binned", 75, 0, 75)
Rare_binned.SetFillColor(ROOT.kViolet-1)
Fakes_binned = ROOT.TH1D("Fakes_binned", "Fakes_binned", 75, 0, 75)
Fakes_binned.SetFillColor(ROOT.kRed+3)
data_binned = ROOT.TH1D("data", "data", 75, 0, 75)
signal_binned = ROOT.TH1D("signal", "signal", 75, 0, 75)
ratio_binned = ROOT.TH1D("ratio", "ratio", 75, 0, 75)


GGF_stack = ROOT.THStack("GGF_stack", "")
all_bkg = ROOT.TH1D("all_bkg", "all_bkg", 75, 0, 75)


resolved1b_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_resolved1b_GGF_2016.root")
resolved1b_card = 'tao_plots/2016/spin0/m400/HH_DL_400_resolved1b_GGF_2016.txt'
resolved2b_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_resolved2b_GGF_2016.root")
resolved2b_card = 'tao_plots/2016/spin0/m400/HH_DL_400_resolved2b_GGF_2016.txt'
boosted_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_boosted_GGF_2016.root")
boosted_card = 'tao_plots/2016/spin0/m400/HH_DL_400_boosted_GGF_2016.txt'


last_bin = 0

error_dict = {
    'signal_ggf_spin0_400_hbbhtt': 0.05556086752382469,
    'signal_ggf_spin0_400_hbbhww': 0.05729694581738197,
    'TT': 0.057160125962072594,
    'DY': 0.16900000000000004,
    'ST': 0.033166247903553964,
    'WJets': 0.011661903789690611,
    'VV': 0.053637673327615536,
    'VVV': 0.053646994324006624,
    'ggH_hmm': 0.05190375708944384,
    'ggH_htt': 0.05190375708944384,
    'ggH_hww': 0.054111828651414055,
    'ggH_hzz': 0.054111828651414055,
    'qqH_htt': 0.013304134695650041,
    'qqH_hww': 0.020275354497517474,
    'ttH_hbb': 0.0703829524814071,
    'ttH_hww': 0.0709513213407616,
    'ZH_hbb': 0.04453942074163064,
    'ZH_htt': 0.04277849927241486,
    'ZH_hww': 0.04543225726287437,
    'tHq_hww': 0.07722752100125958,
    'tHW_hww': 0.0819578550231763,
    'VH_hww': 0.04543225726287437,
    'ttZ': 0.10067770358922583,
    'ttW': 0.13106105447462263,
    'Other_bbWW': 0.011661903789690611,
    'Fakes': 0.0
    }



for dataset_pair in [[resolved1b_file, resolved1b_card], [resolved2b_file, resolved2b_card], [boosted_file, boosted_card]]:
    dataset = dataset_pair[0]
    datacard = dataset_pair[1]


    error_dict = {}
    key_list = []

    with open(datacard) as f:
        lines = f.readlines()
        for line in lines:
            splitline = line.split()
            if (splitline[0] == 'process') and (splitline[1] == 'signal_ggf_spin0_400_hbbhtt'):
                print(splitline)
                for process_name in splitline[1:]:
                    key_list.append(process_name)
                    error_dict[process_name] = 0

            if (len(splitline) > 1) and (splitline[1] == 'lnN'):
                for index, error_value in enumerate(splitline[2:]):
                    if error_value == '-': continue
                    if '/' in error_value:
                        error_split = error_value.split('/')
                        error_dict[key_list[index]] += (1-float(error_split[1]))**2
                    else:
                        error_dict[key_list[index]] += (1-float(error_value))**2

    for key in error_dict:
        error_dict[key] = error_dict[key]**(0.5)




    TT = dataset.Get("TT")
    DY = dataset.Get("DY")
    ST = dataset.Get("ST")
    WJets = dataset.Get("WJets")
    VV = dataset.Get("VV")
    VVV = dataset.Get("VVV")
    ggH_hbb = dataset.Get("ggH_hbb")
    ggH_hgg = dataset.Get("ggH_hgg")
    ggH_hmm = dataset.Get("ggH_hmm")
    ggH_htt = dataset.Get("ggH_htt")
    ggH_hww = dataset.Get("ggH_hww")
    ggH_hzz = dataset.Get("ggH_hzz")
    qqH_hbb = dataset.Get("qqH_hbb")
    qqH_hgg = dataset.Get("qqH_hgg")
    qqH_hmm = dataset.Get("qqH_hmm")
    qqH_htt = dataset.Get("qqH_htt")
    qqH_hww = dataset.Get("qqH_hww")
    qqH_hzz = dataset.Get("qqH_hzz")
    ttH_hbb = dataset.Get("ttH_hbb")
    ttH_hww = dataset.Get("ttH_hww")
    WH_hbb = dataset.Get("WH_hbb")
    ZH_hbb = dataset.Get("ZH_hbb")
    ZH_htt = dataset.Get("ZH_htt")
    ZH_hww = dataset.Get("ZH_hww")
    tHq_hww = dataset.Get("tHq_hww")
    tHW_hww = dataset.Get("tHW_hww")
    VH_hww = dataset.Get("VH_hww")
    ttZ = dataset.Get("ttZ")
    ttW = dataset.Get("ttW")
    Other_bbWW = dataset.Get("Other_bbWW")
    Fakes = dataset.Get("Fakes")
    data_obs = dataset.Get("data_obs")

    signal_ggf_spin0_400_hbbhww = resolved1b_file.Get("signal_ggf_spin0_400_hbbhww")
    signal_ggf_spin0_400_hbbhtt = resolved1b_file.Get("signal_ggf_spin0_400_hbbhtt")

    for binnum in range(1, TT.GetNbinsX()+1):
        if "TT" in error_dict.keys(): TT.SetBinError(binnum, ((((TT.GetBinError(binnum)/TT.GetBinContent(binnum))**2) + ((error_dict['TT'])**2))**0.5)*TT.GetBinContent(binnum))
        if "DY" in error_dict.keys(): DY.SetBinError(binnum, ((((DY.GetBinError(binnum)/DY.GetBinContent(binnum))**2) + ((error_dict['DY'])**2))**0.5)*DY.GetBinContent(binnum))
        if "ST" in error_dict.keys(): ST.SetBinError(binnum, ((((ST.GetBinError(binnum)/ST.GetBinContent(binnum))**2) + ((error_dict['ST'])**2))**0.5)*DY.GetBinContent(binnum))
        if "WJets" in error_dict.keys(): WJets.SetBinError(binnum, ((((WJets.GetBinError(binnum)/WJets.GetBinContent(binnum))**2) + ((error_dict['WJets'])**2))**0.5)*DY.GetBinContent(binnum))
        if "VV" in error_dict.keys(): VV.SetBinError(binnum, ((((VV.GetBinError(binnum)/VV.GetBinContent(binnum))**2) + ((error_dict['VV'])**2))**0.5)*VV.GetBinContent(binnum))
        if "VVV" in error_dict.keys(): VVV.SetBinError(binnum, ((((VVV.GetBinError(binnum)/VVV.GetBinContent(binnum))**2) + ((error_dict['VVV'])**2))**0.5)*VVV.GetBinContent(binnum))

        if "ggH_hbb" in error_dict.keys(): ggH_hbb.SetBinError(binnum, ((((ggH_hbb.GetBinError(binnum)/ggH_hbb.GetBinContent(binnum))**2) + ((error_dict['ggH_hbb'])**2))**0.5)*ggH_hbb.GetBinContent(binnum))
        if "ggH_hgg" in error_dict.keys(): ggH_hgg.SetBinError(binnum, ((((ggH_hgg.GetBinError(binnum)/ggH_hgg.GetBinContent(binnum))**2) + ((error_dict['ggH_hgg'])**2))**0.5)*ggH_hgg.GetBinContent(binnum))
        if "ggH_hmm" in error_dict.keys(): ggH_hmm.SetBinError(binnum, ((((ggH_hmm.GetBinError(binnum)/ggH_hmm.GetBinContent(binnum))**2) + ((error_dict['ggH_hmm'])**2))**0.5)*ggH_hmm.GetBinContent(binnum))
        if "ggH_htt" in error_dict.keys(): ggH_htt.SetBinError(binnum, ((((ggH_htt.GetBinError(binnum)/ggH_htt.GetBinContent(binnum))**2) + ((error_dict['ggH_htt'])**2))**0.5)*ggH_htt.GetBinContent(binnum))
        if "ggH_hww" in error_dict.keys(): ggH_hww.SetBinError(binnum, ((((ggH_hww.GetBinError(binnum)/ggH_hww.GetBinContent(binnum))**2) + ((error_dict['ggH_hww'])**2))**0.5)*ggH_hww.GetBinContent(binnum))
        if "ggH_hzz" in error_dict.keys(): ggH_hzz.SetBinError(binnum, ((((ggH_hzz.GetBinError(binnum)/ggH_hzz.GetBinContent(binnum))**2) + ((error_dict['ggH_hzz'])**2))**0.5)*ggH_hzz.GetBinContent(binnum))
        if "qqH_hbb" in error_dict.keys(): qqH_hbb.SetBinError(binnum, ((((qqH_hbb.GetBinError(binnum)/qqH_hbb.GetBinContent(binnum))**2) + ((error_dict['qqH_hbb'])**2))**0.5)*qqH_hbb.GetBinContent(binnum))
        if "qqH_hgg" in error_dict.keys(): qqH_hgg.SetBinError(binnum, ((((qqH_hgg.GetBinError(binnum)/qqH_hgg.GetBinContent(binnum))**2) + ((error_dict['qqH_hgg'])**2))**0.5)*qqH_hgg.GetBinContent(binnum))
        if "qqH_hmm" in error_dict.keys(): qqH_hmm.SetBinError(binnum, ((((qqH_hmm.GetBinError(binnum)/qqH_hmm.GetBinContent(binnum))**2) + ((error_dict['qqH_hmm'])**2))**0.5)*qqH_hmm.GetBinContent(binnum))
        if "qqH_htt" in error_dict.keys(): qqH_htt.SetBinError(binnum, ((((qqH_htt.GetBinError(binnum)/qqH_htt.GetBinContent(binnum))**2) + ((error_dict['qqH_htt'])**2))**0.5)*qqH_htt.GetBinContent(binnum))
        if "qqH_hww" in error_dict.keys(): qqH_hww.SetBinError(binnum, ((((qqH_hww.GetBinError(binnum)/qqH_hww.GetBinContent(binnum))**2) + ((error_dict['qqH_hww'])**2))**0.5)*qqH_hww.GetBinContent(binnum))
        if "qqH_hzz" in error_dict.keys(): qqH_hzz.SetBinError(binnum, ((((qqH_hzz.GetBinError(binnum)/qqH_hzz.GetBinContent(binnum))**2) + ((error_dict['qqH_hzz'])**2))**0.5)*qqH_hzz.GetBinContent(binnum))

        if "qqH_hzz" in error_dict.keys(): qqH_hzz.SetBinError(binnum, ((((qqH_hzz.GetBinError(binnum)/qqH_hzz.GetBinContent(binnum))**2) + ((error_dict['qqH_hzz'])**2))**0.5)*qqH_hzz.GetBinContent(binnum))
        if "ttH_hbb" in error_dict.keys(): ttH_hbb.SetBinError(binnum, ((((ttH_hbb.GetBinError(binnum)/ttH_hbb.GetBinContent(binnum))**2) + ((error_dict['ttH_hbb'])**2))**0.5)*ttH_hbb.GetBinContent(binnum))
        if "ttH_hww" in error_dict.keys(): ttH_hww.SetBinError(binnum, ((((ttH_hww.GetBinError(binnum)/ttH_hww.GetBinContent(binnum))**2) + ((error_dict['ttH_hww'])**2))**0.5)*ttH_hww.GetBinContent(binnum))
        if "WH_hbb" in error_dict.keys(): WH_hbb.SetBinError(binnum, ((((WH_hbb.GetBinError(binnum)/WH_hbb.GetBinContent(binnum))**2) + ((error_dict['WH_hbb'])**2))**0.5)*WH_hbb.GetBinContent(binnum))
        if "ZH_hbb" in error_dict.keys(): ZH_hbb.SetBinError(binnum, ((((ZH_hbb.GetBinError(binnum)/ZH_hbb.GetBinContent(binnum))**2) + ((error_dict['ZH_hbb'])**2))**0.5)*ZH_hbb.GetBinContent(binnum))
        if "ZH_htt" in error_dict.keys(): ZH_htt.SetBinError(binnum, ((((ZH_htt.GetBinError(binnum)/ZH_htt.GetBinContent(binnum))**2) + ((error_dict['ZH_htt'])**2))**0.5)*ZH_htt.GetBinContent(binnum))
        if "ZH_hww" in error_dict.keys(): ZH_hww.SetBinError(binnum, ((((ZH_hww.GetBinError(binnum)/ZH_hww.GetBinContent(binnum))**2) + ((error_dict['ZH_hww'])**2))**0.5)*ZH_hww.GetBinContent(binnum))

        if "tHq_hww" in error_dict.keys(): tHq_hww.SetBinError(binnum, ((((tHq_hww.GetBinError(binnum)/tHq_hww.GetBinContent(binnum))**2) + ((error_dict['tHq_hww'])**2))**0.5)*tHq_hww.GetBinContent(binnum))
        if "tHW_hww" in error_dict.keys(): tHW_hww.SetBinError(binnum, ((((tHW_hww.GetBinError(binnum)/tHW_hww.GetBinContent(binnum))**2) + ((error_dict['tHW_hww'])**2))**0.5)*tHW_hww.GetBinContent(binnum))
        if "VH_hww" in error_dict.keys(): VH_hww.SetBinError(binnum, ((((VH_hww.GetBinError(binnum)/VH_hww.GetBinContent(binnum))**2) + ((error_dict['VH_hww'])**2))**0.5)*VH_hww.GetBinContent(binnum))
        if "ttZ" in error_dict.keys(): ttZ.SetBinError(binnum, ((((ttZ.GetBinError(binnum)/ttZ.GetBinContent(binnum))**2) + ((error_dict['ttZ'])**2))**0.5)*ttZ.GetBinContent(binnum))
        if "ttW" in error_dict.keys(): ttW.SetBinError(binnum, ((((ttW.GetBinError(binnum)/ttW.GetBinContent(binnum))**2) + ((error_dict['ttW'])**2))**0.5)*ttW.GetBinContent(binnum))
        if "Other_bbWW" in error_dict.keys(): Other_bbWW.SetBinError(binnum, ((((Other_bbWW.GetBinError(binnum)/Other_bbWW.GetBinContent(binnum))**2) + ((error_dict['Other_bbWW'])**2))**0.5)*Other_bbWW.GetBinContent(binnum))
        if "Fakes" in error_dict.keys(): Fakes.SetBinError(binnum, ((((Fakes.GetBinError(binnum)/Fakes.GetBinContent(binnum))**2) + ((error_dict['Fakes'])**2))**0.5)*Fakes.GetBinContent(binnum))





    VVV_stack = VV
    VVV_stack.Add(VVV)

    SMH = ggH_hbb
    SMH.Add(ggH_hgg)
    SMH.Add(ggH_hmm)
    SMH.Add(ggH_htt)
    SMH.Add(ggH_htt)
    SMH.Add(ggH_hww)
    SMH.Add(ggH_hzz)
    SMH.Add(ggH_hzz)
    SMH.Add(qqH_hbb)
    SMH.Add(qqH_hgg)
    SMH.Add(qqH_hmm)
    SMH.Add(qqH_htt)
    SMH.Add(qqH_hww)
    SMH.Add(qqH_hzz)

    Rare = ttH_hbb
    Rare.Add(ttH_hww)
    Rare.Add(WH_hbb)
    Rare.Add(ZH_hbb)
    Rare.Add(ZH_htt)
    Rare.Add(ZH_hww)
    Rare.Add(tHq_hww)
    Rare.Add(tHW_hww)
    Rare.Add(VH_hww)
    Rare.Add(ttZ)
    Rare.Add(ttW)
    Rare.Add(Other_bbWW)

    signal = signal_ggf_spin0_400_hbbhww
    signal.Add(signal_ggf_spin0_400_hbbhtt)



    for binnum in range(1, TT.GetNbinsX()+1):
        binned_binnum = binnum + last_bin
        TT_binned.SetBinContent(binned_binnum, TT.GetBinContent(binnum))
        TT_binned.SetBinError(binned_binnum, TT.GetBinError(binnum))
        print("TT Error at bin ", binned_binnum, " value ", TT_binned.GetBinContent(binned_binnum), " error ", TT_binned.GetBinError(binned_binnum))

        DY_binned.SetBinContent(binned_binnum, DY.GetBinContent(binnum))
        DY_binned.SetBinError(binned_binnum, DY.GetBinError(binnum))

        ST_binned.SetBinContent(binned_binnum, ST.GetBinContent(binnum))
        ST_binned.SetBinError(binned_binnum, ST.GetBinError(binnum))

        WJets_binned.SetBinContent(binned_binnum, WJets.GetBinContent(binnum))
        WJets_binned.SetBinError(binned_binnum, WJets.GetBinError(binnum))

        VVV_binned.SetBinContent(binned_binnum, VVV_stack.GetBinContent(binnum))
        VVV_binned.SetBinError(binned_binnum, VVV_stack.GetBinError(binnum))

        SMH_binned.SetBinContent(binned_binnum, SMH.GetBinContent(binnum))
        SMH_binned.SetBinError(binned_binnum, SMH.GetBinError(binnum))

        Rare_binned.SetBinContent(binned_binnum, Rare.GetBinContent(binnum))
        Rare_binned.SetBinError(binned_binnum, Rare.GetBinError(binnum))

        Fakes_binned.SetBinContent(binned_binnum, Fakes.GetBinContent(binnum))
        Fakes_binned.SetBinError(binned_binnum, Fakes.GetBinError(binnum))

        data_binned.SetBinContent(binned_binnum, data_obs.GetBinContent(binnum))
        data_binned.SetBinError(binned_binnum, data_obs.GetBinError(binnum))

        signal_binned.SetBinContent(binned_binnum, signal.GetBinContent(binnum))
        signal_binned.SetBinError(binned_binnum, signal.GetBinError(binnum))

        total_bkg = TT.GetBinContent(binnum) + DY.GetBinContent(binnum) + ST.GetBinContent(binnum) + WJets.GetBinContent(binnum) + VVV_stack.GetBinContent(binnum) + SMH.GetBinContent(binnum) + Rare.GetBinContent(binnum) + Fakes.GetBinContent(binnum)
        total_bkg_err = (TT.GetBinError(binnum)**2 + DY.GetBinError(binnum)**2 + ST.GetBinError(binnum)**2 + WJets.GetBinError(binnum)**2 + VVV_stack.GetBinError(binnum)**2 + SMH.GetBinError(binnum)**2 + Rare.GetBinError(binnum)**2 + Fakes.GetBinError(binnum)**2)**(0.5)

        print("Total bkg is ", total_bkg)
        print("Total err is ", total_bkg_err)


        ratio_binned.SetBinContent(binned_binnum, (data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)
        ratio_binned.SetBinError(binned_binnum, ((data_obs.GetBinError(binnum)/(data_obs.GetBinContent(binnum)))**2) + (total_bkg_err**2))
        ratio_binned.SetBinError(binned_binnum, ((data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)*((((data_obs.GetBinError(binnum)/(data_obs.GetBinContent(binnum)))**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))

        print("Ratio value ", (data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)
        print("Ratio errPer ", (((data_obs.GetBinError(binnum)**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))
        print("Data Error ", data_obs.GetBinError(binnum))
        print("Total err ", total_bkg_err)
        print("Ratio error ", ((data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)*(((data_obs.GetBinError(binnum)**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))

    last_bin += 30


#Must add by smallest to largest in order by hand
GGF_stack.Add(WJets_binned)
GGF_stack.Add(SMH_binned)
GGF_stack.Add(VVV_binned)
GGF_stack.Add(Rare_binned)
GGF_stack.Add(Fakes_binned)
GGF_stack.Add(ST_binned)
GGF_stack.Add(DY_binned)
GGF_stack.Add(TT_binned)

#For error bars we must add to a histogram
all_bkg.Add(WJets_binned)
all_bkg.Add(SMH_binned)
all_bkg.Add(VVV_binned)
all_bkg.Add(Rare_binned)
all_bkg.Add(Fakes_binned)
all_bkg.Add(ST_binned)
all_bkg.Add(DY_binned)
all_bkg.Add(TT_binned)

legend1 = ROOT.TLegend(0.5, 0.7, 0.9, 0.85)
legend1.SetNColumns(2)
legend1.AddEntry(TT_binned, "ttbar")
legend1.AddEntry(DY_binned, "Drell-Yan")
legend1.AddEntry(ST_binned, "Single Top")
legend1.AddEntry(Fakes_binned, "Fakes")
legend1.AddEntry(Rare_binned, "Rares")
legend1.AddEntry(VVV_binned, "VV(V)")
legend1.AddEntry(SMH_binned, "SM H")
legend1.AddEntry(WJets_binned, "W+jets")
legend1.SetTextSize(0.)
legend1.SetBorderSize(0)



H_ref = 800
W_ref = 800
W = W_ref
H = H_ref

T = 0.12*H_ref
B = 0.16*H_ref
L = 0.16*W_ref
R = 0.08*W_ref

canvas = ROOT.TCanvas("c1", "c1", 100, 100, W, H)
canvas.SetFillColor(0)
canvas.SetBorderMode(0)
canvas.SetFrameFillStyle(0)
canvas.SetFrameBorderMode(0)
canvas.SetLeftMargin( L/W )
canvas.SetRightMargin( R/W )
canvas.SetTopMargin( T/H )
canvas.SetBottomMargin( B/H )

pad1 = ROOT.TPad("pad1", "pad1", 0, 0.4, 1, 1.0)
pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.4)
pad1.SetBottomMargin(0.05)
pad2.SetTopMargin(0.05)
pad1.Draw()
pad2.Draw()
pad1.cd()

pad1.SetLogy()
GGF_stack.SetMaximum(10**7)
GGF_stack.SetMinimum(10**(-2))
GGF_stack.Draw("hist")
GGF_stack.GetYaxis().SetTitle("Events / bin")
data_binned.Draw("same EP")
data_binned.SetMarkerStyle(8)
data_binned.SetMarkerSize(1)
all_bkg.Draw("same E2")
#all_bkg.SetFillColor(ROOT.kOrange-9)
all_bkg.SetFillStyle(3001)
all_bkg.SetFillColorAlpha(ROOT.kOrange-9, 0.7)
signal_binned.Draw("same hist")
signal_binned.SetLineColor(ROOT.kRed-3)
signal_binned.SetFillColor(ROOT.kRed-3)
signal_binned.SetFillStyle(3353)
legend1.Draw()



legend2 = ROOT.TLegend(0.15, 0.7, 0.4, 0.85)
legend2.SetNColumns(1)
legend2.AddEntry(data_binned, "Data")
legend2.AddEntry(signal_binned, "X (spin-0 400 GeV), 1 pb")
legend2.AddEntry(all_bkg, "Uncertainty")
legend2.SetTextSize(0.)
legend2.SetBorderSize(0)
legend2.Draw("same")



latex = ROOT.TLatex()
latex.SetNDC()
latex.SetTextAngle(0)
latex.SetTextColor(ROOT.kBlack)

latex.SetTextFont(42)
latex.SetTextSize(0.3*canvas.GetTopMargin())
latex.SetTextAlign(31)
latex.DrawLatex(1-1*pad1.GetRightMargin(), 1-0.9*pad1.GetTopMargin(), "36.3 fb^{-1} (13 TeV)")

latex.SetTextAlign(11)
latex.SetTextSize(0.45*canvas.GetTopMargin())
latex.SetTextFont(61)
latex.DrawLatex(0+1*pad1.GetLeftMargin(), 1-0.9*pad1.GetTopMargin(), "CMS")

latex.SetTextFont(61)
latex.SetTextAlign(11)
latex.SetTextSize(0.4*canvas.GetTopMargin())
latex.DrawLatex(0+1.25*pad1.GetLeftMargin(), 1-2*pad1.GetTopMargin(), "GGF categories (400 GeV), prefit")

latex.SetTextFont(42)
latex.SetTextSize(0.25*canvas.GetTopMargin())
latex.SetTextAlign(11)
latex.DrawLatex(0+1.25*pad1.GetLeftMargin(), 1-5.5*pad1.GetTopMargin(), "Resolved 1b, GGF")
latex.DrawLatex(0+4.00*pad1.GetLeftMargin(), 1-5.5*pad1.GetTopMargin(), "Resolved 2b, GGF")
latex.DrawLatex(0+6.75*pad1.GetLeftMargin(), 1-5.5*pad1.GetTopMargin(), "Boosted, GGF")

canvas.Update()

pad2.cd()
ratio_binned.SetMaximum(2)
ratio_binned.SetMinimum(-2)
ratio_binned.Draw("EP")
ratio_binned.SetMarkerStyle(8)
ratio_binned.SetMarkerSize(1)
ratio_binned.GetYaxis().SetTitle("Data - Expectation / Expectation")
ratio_binned.GetXaxis().SetTitle("DNN Score x HME mass bin (A.U.)")



canvas.Update()








canvas.SaveAs('Histo_test.pdf')







"""




"""
