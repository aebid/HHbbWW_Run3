import ROOT
import math
import tdrStyle

ROOT.gROOT.SetBatch(1)
tdrStyle.setTDRStyle()

year = 2016
spin = 0
mass = 400

yearlumi = {"2016": 36.3,
            "2017": 41.5,
            "2018": 59.7,
            "Run2": 138
        }

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



def makeStackPlots(spin, mass, era, datasetlist, isSignalNode, plotname):
  lumi = yearlumi[era] ## era is str: 2016, 2017, 2018, Run2
  nodestr = "GGF" 
  catnames = ["Resolved 1b, GGF", "Resolved 2b, GGF", "Boosted, GGF"]
  if not isSignalNode:
      nodestr = "Background" 
      catnames = ["Inclusive, DY+VV(V)", "Resolved, Top+Other", "Boosted, Top+Other"]
  Nbins = 0
  Nbins_list = []
  for dataset_pair in datasetlist:
      dataset = dataset_pair[0]
      TT = dataset.Get("TT")
      Nbins_list.append(TT.GetNbinsX())
      Nbins += TT.GetNbinsX()
  

  print("datasetlist ", datasetlist, "nbins ", Nbins_list, " total ", Nbins)
  GGF_stack = ROOT.THStack("GGF_stack", "")
  all_bkg = ROOT.TH1D("all_bkg", "all_bkg", Nbins, 0, Nbins)
  TT_binned = ROOT.TH1D("TT_binned", "TT_binned", Nbins, 0, Nbins)
  TT_binned.SetFillColor(ROOT.kOrange+2)
  TT_binned.SetLineWidth(0)
  DY_binned = ROOT.TH1D("DY_binned", "DY_binned", Nbins, 0, Nbins)
  DY_binned.SetFillColor(ROOT.kAzure-7)
  DY_binned.SetLineWidth(0)
  ST_binned = ROOT.TH1D("ST_binned", "ST_binned", Nbins, 0, Nbins)
  ST_binned.SetFillColor(ROOT.kRed+2)
  ST_binned.SetLineWidth(0)
  WJets_binned = ROOT.TH1D("WJets_binned", "WJets_binned", Nbins, 0, Nbins)
  WJets_binned.SetFillColor(ROOT.kPink-5)
  WJets_binned.SetLineWidth(0)
  VVV_binned = ROOT.TH1D("VVV_binned",       "VVV_binned", Nbins, 0, Nbins)
  VVV_binned.SetFillColor(ROOT.kYellow-3)
  VVV_binned.SetLineWidth(0)
  SMH_binned = ROOT.TH1D("SMH_binned",       "SMH_binned", Nbins, 0, Nbins)
  SMH_binned.SetFillColor(ROOT.kTeal-5)
  SMH_binned.SetLineWidth(0)
  Rare_binned = ROOT.TH1D("Rare_binned",    "Rare_binned", Nbins, 0, Nbins)
  Rare_binned.SetFillColor(ROOT.kViolet-1)
  Rare_binned.SetLineWidth(0)
  Fakes_binned = ROOT.TH1D("Fakes_binned", "Fakes_binned", Nbins, 0, Nbins)
  Fakes_binned.SetFillColor(ROOT.kRed+3)
  Fakes_binned.SetLineWidth(0)
  data_binned = ROOT.TH1D("data",                  "data", Nbins, 0, Nbins)
  signal_binned = ROOT.TH1D("signal",            "signal", Nbins, 0, Nbins)
  ratio_binned = ROOT.TH1D("ratio",               "ratio", Nbins, 0, Nbins)
  errband_binned = ROOT.TH1D("errband",         "errband", Nbins, 0, Nbins)
  
  
  
  
  last_bin = 0
  datasetindex  = 0
  #for dataset_pair in [[resolved1b_file, resolved1b_card], [resolved2b_file, resolved2b_card], [boosted_file, boosted_card]]:
  for dataset_pair in datasetlist:
      dataset = dataset_pair[0]
      datacard = dataset_pair[1]
  
  
      error_dict = {}
      key_list = []
  
      with open(datacard) as f:
          lines = f.readlines()
          for line in lines:
              splitline = line.split()
              if (splitline[0] == 'process') and (splitline[1] == 'signal_ggf_spin%d_%d_hbbhtt'%(spin, mass)):
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
  
      signal_ggf_hbbhww = dataset.Get("signal_ggf_spin%d_%d_hbbhww"%(spin, mass))
      signal_ggf_hbbhtt = dataset.Get("signal_ggf_spin%d_%d_hbbhtt"%(spin, mass))
  
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
  
      signal = signal_ggf_hbbhww
      signal.Add(signal_ggf_hbbhtt)
  
  
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
          #######ratio bin error  only depends on data statistic 
          ratio_binned.SetBinError(binned_binnum, data_obs.GetBinError(binnum)/total_bkg)
          errband_binned.SetBinContent(binned_binnum, 0.0)
          errband_binned.SetBinError(binned_binnum, total_bkg_err/total_bkg)
          
          #ratio_binned.SetBinError(binned_binnum, ((data_obs.GetBinError(binnum)/(data_obs.GetBinContent(binnum)))**2) + (total_bkg_err**2))
          #ratio_binned.SetBinError(binned_binnum, ((data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)*((((data_obs.GetBinError(binnum)/(data_obs.GetBinContent(binnum)))**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))
  
          print("Ratio value ", (data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)
          print("Ratio errPer ", (((data_obs.GetBinError(binnum)**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))
          print("Data Error ", data_obs.GetBinError(binnum))
          print("Total err ", total_bkg_err)
          print("Ratio error ", ((data_obs.GetBinContent(binnum) - total_bkg)/total_bkg)*(((data_obs.GetBinError(binnum)**2) + (total_bkg_err**2))/(total_bkg_err**2)**0.5))
  
      last_bin += Nbins_list[datasetindex]
      datasetindex += 1
  
  
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
  
  legend1 = ROOT.TLegend(0.56, 0.7, 0.93, 0.85)
  legend1.SetNColumns(2)
  legend1.AddEntry(TT_binned, "ttbar","f")
  legend1.AddEntry(DY_binned, "Drell-Yan","f")
  legend1.AddEntry(ST_binned, "Single Top","f")
  legend1.AddEntry(Fakes_binned, "Fakes","f")
  legend1.AddEntry(Rare_binned, "Rares","f")
  legend1.AddEntry(VVV_binned, "VV(V)","f")
  legend1.AddEntry(SMH_binned, "SM H","f")
  legend1.AddEntry(WJets_binned, "W+jets","f")
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
  
  pad1 = ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
  pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.3)


  pad1.SetBottomMargin(0.01)
  pad2.SetTopMargin(0.02)
  pad2.SetBottomMargin(0.25)
  pad1.Draw()
  pad2.Draw()
  pad1.cd()
  
  pad1.SetLogy()

  ymin = 0.005
  dataMax = data_binned.GetMaximum()
  magnitude_data = math.floor(math.log(2*dataMax, 10))+2
  yratio = 1.35
  line1 = ROOT.TLine(Nbins_list[0], ymin, Nbins_list[0], dataMax*2.0)
  line2 = ROOT.TLine(Nbins_list[1]+Nbins_list[0], ymin, Nbins_list[1]+Nbins_list[0], dataMax*2.0)

  GGF_stack.SetMaximum(10**(magnitude_data*yratio))
  GGF_stack.SetMinimum(ymin)
  print("GGG-stack min", GGF_stack.GetMinimum())

  GGF_stack.Draw("hist")
  GGF_stack.GetYaxis().SetTitle("Events / bin")
  GGF_stack.GetYaxis().SetRangeUser(ymin, 10**(magnitude_data*yratio))
  for i in range(1, GGF_stack.GetHistogram().GetNbinsX()):
      GGF_stack.GetHistogram().GetXaxis().SetBinLabel(i+1, "")
  GGF_stack.Draw("hist")
  #GGF_stack.GetYaxis().SetRangeUser(0.01, dataMax*dataMax*100.0)
  data_binned.Draw("same EP")
  data_binned.SetMarkerStyle(8)
  data_binned.SetMarkerSize(1)
  all_bkg.Draw("same E2")
  #all_bkg.SetFillColor(ROOT.kOrange-9)
  all_bkg.SetFillStyle(3001)
  all_bkg.SetFillColorAlpha(ROOT.kOrange-9, 0.7)
  all_bkg.SetLineWidth(0)
  errband_binned.SetFillStyle(3001)
  errband_binned.SetFillColorAlpha(ROOT.kOrange-9, 0.7)
  signal_binned.Draw("same hist")
  signal_binned.SetLineColor(ROOT.kRed-3)
  signal_binned.SetFillColor(ROOT.kRed-3)
  signal_binned.SetFillStyle(3353)

  line1.Draw("same")
  line2.Draw("same")
  legend1.Draw()
  
  
  
  legend2 = ROOT.TLegend(0.15, 0.7, 0.5, 0.85)
  legend2.SetNColumns(1)
  legend2.AddEntry(data_binned, "Data")
  legend2.AddEntry(signal_binned, "pp#rightarrow X(spin-%d,%d GeV)#rightarrow HH, 1 pb"%(spin, mass),"f")
  legend2.AddEntry(all_bkg, "Uncertainty","f")
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
  latex.DrawLatex(1-1*pad1.GetRightMargin(), 1-0.9*pad1.GetTopMargin(), "%.1f fb^{-1} (13 TeV)"%lumi)
  
  latex.SetTextAlign(11)
  latex.SetTextSize(0.45*canvas.GetTopMargin())
  latex.SetTextFont(61)
  latex.DrawLatex(0+1*pad1.GetLeftMargin(), 1-0.9*pad1.GetTopMargin(), "CMS")
  
  latex.SetTextFont(61)
  latex.SetTextAlign(11)
  latex.SetTextSize(0.4*canvas.GetTopMargin())
  latex.DrawLatex(0+1.25*pad1.GetLeftMargin(), 1-2*pad1.GetTopMargin(), "%s categories (%d GeV), prefit"%(nodestr, mass))
  
  latex.SetTextFont(42)
  latex.SetTextSize(0.25*canvas.GetTopMargin())
  latex.SetTextAlign(11)
  Nbins_ratio0 = Nbins_list[0]*1.05*(W-L-R)/(Nbins*W)
  Nbins_ratio1 = (Nbins_list[0]+Nbins_list[1])*1.05*(W-L-R)/(Nbins*W)
  cat0_x = pad1.GetLeftMargin()+0.03
  cat1_x = pad1.GetLeftMargin()+0.03 + Nbins_ratio0
  cat2_x = pad1.GetLeftMargin()+0.03 + Nbins_ratio1
  cat_y = pad1.GetBottomMargin() + 1/yratio*(1.0-T/H-B/H) + 0.07
  #(math.floor(math.log(2*dataMax, 10))+2.5)*1.1*(1.0-T/H-B/H)/(math.floor(math.log(dataMax*dataMax, 10))+2.5)
  print("test x ", 0+1.25*pad1.GetLeftMargin()," ",0+4.00*pad1.GetLeftMargin()," ",0+6.45*pad1.GetLeftMargin()," ",pad1.GetLeftMargin())
  print("New x ", cat0_x," ",cat1_x,"  ",cat2_x, " y ", cat_y, " previous y ", 1-5.5*pad1.GetTopMargin())
  latex.DrawLatex(cat0_x, cat_y, catnames[0])#"Resolved 1b, GGF")
  latex.DrawLatex(cat1_x, cat_y, catnames[1])#"Resolved 2b, GGF")
  latex.DrawLatex(cat2_x, cat_y, catnames[2])#"Boosted, GGF")
  
  canvas.Update()
  
  pad2.cd()
  ratio_binned.SetMaximum(1.)
  ratio_binned.SetMinimum(-1.)
  ratio_binned.SetMarkerStyle(8)
  ratio_binned.SetMarkerSize(1)
  ratio_binned.GetXaxis().SetTitle("DNN Score x HME mass bin (A.U.)")
  ratio_binned.GetYaxis().SetTitle("#frac{Data - Expectation}{Expectation}")
  ratio_binned.GetXaxis().SetTitleSize(.1)
  ratio_binned.GetXaxis().SetTitleFont(42)
  #ratio_binned.GetXaxis().SetTitleOffset(3.0)
  ratio_binned.GetXaxis().SetLabelSize(.1)
  ratio_binned.GetXaxis().SetLabelFont(42)
  ratio_binned.GetYaxis().SetNdivisions(505)
  ratio_binned.GetYaxis().SetTitleSize(.08)
  ratio_binned.GetYaxis().SetTitleFont(42)
  ratio_binned.GetYaxis().SetTitleOffset(.7)
  ratio_binned.GetYaxis().SetLabelSize(.1)
  ratio_binned.GetYaxis().SetLabelFont(42)
  ratio_binned.GetYaxis().CenterTitle()
  if not isSignalNode:
    ratio_binned.GetXaxis().SetTitle("DNN Score (A.U.)")
  
  ratio_binned.Draw("EP")
  errband_binned.Draw("e2same")
  canvas.Update()
  
  
  canvas.SaveAs('Run2bbWW_DL_spin%d_mass%d_%s.pdf'%(spin, mass, plotname))
  canvas.SaveAs('Run2bbWW_DL_spin%d_mass%d_%s.C'%(spin, mass, plotname))


def getSignalAcceptance(spin, mass, era):
  folder = "/Users/taohuang/Documents/CMSANDN/AN-20-119/datacards/resonant/dl/Run2/spin%d/%d/"%(spin, mass)
  resolved1b_file = ROOT.TFile(folder+"HH_DL_%d_resolved1b_GGF_%d.root"%(mass, year))
  resolved2b_file = ROOT.TFile(folder+"HH_DL_%d_resolved2b_GGF_%d.root"%(mass, year))
  boosted_file      = ROOT.TFile(folder+"HH_DL_%d_boosted_GGF_%d.root"%(mass, year))
  DY_file            = ROOT.TFile(folder+"HH_DL_%d_inclusive_DY_VVV_%d.root"%(mass, year))
  resolvedOther_file = ROOT.TFile(folder+"HH_DL_%d_resolved_other_%d.root"%(mass, year))
  boostOther_file    = ROOT.TFile(folder+"HH_DL_%d_boosted_other_%d.root"%(mass, year))
  datasetlist = [resolved1b_file, resolved2b_file, boosted_file, DY_file, resolvedOther_file, boostOther_file]

  lumi = yearlumi["%d"%era]
  Nexpect = lumi*1000.0*0.0268
  index = 0
  totalSig = 0.0
  for dataset in datasetlist:
      signal_ggf_hbbhww = dataset.Get("signal_ggf_spin%d_%d_hbbhww"%(spin, mass))
      #signal_ggf_hbbhtt = dataset.Get("signal_ggf_spin%d_%d_hbbhtt"%(spin, mass))
      #signal_ggf_hbbhww.Add(signal_ggf_hbbhtt)
      signal_ggf_hbbhww.Rebin(signal_ggf_hbbhww.GetNbinsX())
      #print("mass ",mass ,index," bin 1 ",signal_ggf_hbbhww.GetBinContent(1)," err ", signal_ggf_hbbhww.GetBinError(1)," integral ", signal_ggf_hbbhww.Integral())
      totalSig += signal_ggf_hbbhww.GetBinContent(1) ## only 1 bin now
      index += 1
  return totalSig/Nexpect


def getAllSignalAcceptance(masslist):
  for mass in masslist:
      spin0_2016 =  getSignalAcceptance(0, mass, 2016)
      spin0_2017 =  getSignalAcceptance(0, mass, 2017)
      spin0_2018 =  getSignalAcceptance(0, mass, 2018)
      spin2_2016 =  getSignalAcceptance(2, mass, 2016)
      spin2_2017 =  getSignalAcceptance(2, mass, 2017)
      spin2_2018 =  getSignalAcceptance(2, mass, 2018)
      print("%d \t& %.3f \t& %.3f \t& %.3f \t& %.3f \t& %.3f \t& %.3f \\\\ [0.5ex]"\
              %(mass, spin0_2016, spin0_2017, spin0_2018, spin2_2016, spin2_2017, spin2_2018))

def getYieldTable(spin, mass, year):
  folder = "/Users/taohuang/Documents/CMSANDN/AN-20-119/datacards/resonant/dl/Run2/spin%d/%d/"%(spin, mass)
  resolved1b_file = ROOT.TFile(folder+"HH_DL_%d_resolved1b_GGF_%d.root"%(mass, year))
  resolved2b_file = ROOT.TFile(folder+"HH_DL_%d_resolved2b_GGF_%d.root"%(mass, year))
  boosted_file      = ROOT.TFile(folder+"HH_DL_%d_boosted_GGF_%d.root"%(mass, year))
  DY_file            = ROOT.TFile(folder+"HH_DL_%d_inclusive_DY_VVV_%d.root"%(mass, year))
  resolvedOther_file = ROOT.TFile(folder+"HH_DL_%d_resolved_other_%d.root"%(mass, year))
  boostOther_file    = ROOT.TFile(folder+"HH_DL_%d_boosted_other_%d.root"%(mass, year))
  datasetlist = [resolved1b_file, resolved2b_file, boosted_file, DY_file, resolvedOther_file, boostOther_file]
  
  datasets_dict = {
          "Resolved 1b GGF" : resolved1b_file,
          "Resolved 2b GGF" : resolved2b_file,
          "Boosted GGF" : boosted_file, 
          "Inclusive DY+VV(V)" : DY_file,
          "Resolved Other": resolvedOther_file,
          "Boosted Other": boostOther_file
          }

  sortedKeys= ["Resolved 1b GGF", "Resolved 2b GGF", "Boosted GGF", "Inclusive DY+VV(V)", "Resolved Other", "Boosted Other"]
  yields_dict = {}
  lumi = yearlumi["%d"%year]
  TT_incl = None; DY_incl = None; ST_incl = None; SMH_incl = None; Fakes_incl = None; 
  Rare_incl = None; WJets_incl = None; VVV_stack = None; signal_incl = None; data_incl = None; total_bkg = None
  sigprocess = "Spin-%d, %dGeV"%(spin,mass)
  for key in sortedKeys:
      dataset = datasets_dict[key]
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
  
      signal_ggf_hbbhww = dataset.Get("signal_ggf_spin%d_%d_hbbhww"%(spin, mass))
      signal_ggf_hbbhtt = dataset.Get("signal_ggf_spin%d_%d_hbbhtt"%(spin, mass))

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
  
      signal = signal_ggf_hbbhww
      NbinsX = TT.GetNbinsX()
      TT.Rebin(NbinsX)
      DY.Rebin(NbinsX)
      ST.Rebin(NbinsX)
      Rare.Rebin(NbinsX)
      Fakes.Rebin(NbinsX)
      VVV_stack.Rebin(NbinsX)
      SMH.Rebin(NbinsX)
      WJets.Rebin(NbinsX)
      if WJets.GetBinContent(1) < 0.0:
          WJets.SetBinContent(1, 0.0)
          WJets.SetBinError(1, 0.0)
      signal.Rebin(NbinsX)
      data_obs.Rebin(NbinsX)

      tot_bkg = ROOT.TH1D("tot_bkg","tot_bkg", 1, 0, 1)
      tot_bkg.Add(TT)
      tot_bkg.Add(DY)
      tot_bkg.Add(ST)
      tot_bkg.Add(Rare)
      tot_bkg.Add(Fakes)
      tot_bkg.Add(VVV_stack)
      tot_bkg.Add(SMH)
      tot_bkg.Add(WJets)
      yields_dict[key] = {}
      yields_dict[key]["ttbar"]      = "$%.2f\pm%.2f$"%(TT.GetBinContent(1), TT.GetBinError(1))
      yields_dict[key]["Drell-Yan"]  = "$%.2f\pm%.2f$"%(DY.GetBinContent(1), DY.GetBinError(1))
      yields_dict[key]["Single Top"] = "$%.2f\pm%.2f$"%(ST.GetBinContent(1), ST.GetBinError(1))
      yields_dict[key]["Rares"]      = "$%.2f\pm%.2f$"%(Rare.GetBinContent(1), Rare.GetBinError(1))
      yields_dict[key]["Fakes"]      = "$%.2f\pm%.2f$"%(Fakes.GetBinContent(1), Fakes.GetBinError(1))
      yields_dict[key]["VV(V)"]      = "$%.2f\pm%.2f$"%(VVV_stack.GetBinContent(1), VVV_stack.GetBinError(1))
      yields_dict[key]["SM H"]       = "$%.2f\pm%.2f$"%(SMH.GetBinContent(1), SMH.GetBinError(1))
      yields_dict[key]["W+jets"]     = "$%.2f\pm%.2f$"%(WJets.GetBinContent(1), WJets.GetBinError(1))
      yields_dict[key]["Total BKG"]  = "$%.2f\pm%.2f$"%(tot_bkg.GetBinContent(1), tot_bkg.GetBinError(1))
      yields_dict[key]["Data"]       = "$%.2f\pm%.2f$"%(data_obs.GetBinContent(1),data_obs.GetBinError(1))
      yields_dict[key][sigprocess]  = "$%.2f\pm%.2f$"%(signal.GetBinContent(1), signal.GetBinError(1))
      if TT_incl ==  None:
        TT_incl   = TT; DY_incl      = DY;      ST_incl = ST; SMH_incl = SMH; Fakes_incl = Fakes; total_bkg = tot_bkg
        Rare_incl = Rare; WJets_incl = WJets; VVV_stack_incl = VVV_stack; signal_incl = signal; data_incl = data_obs
      else:
        TT_incl.Add(TT); DY_incl.Add(DY);      ST_incl.Add(ST); SMH_incl.Add(SMH); Fakes_incl.Add(Fakes); total_bkg.Add(tot_bkg)
        Rare_incl.Add(Rare); WJets_incl.Add(WJets); VVV_stack_incl.Add(VVV_stack); signal_incl.Add(signal); data_incl.Add(data_obs)
  yields_dict["Inclusive"] = {}
  yields_dict["Inclusive"]["ttbar"]      = "$%.2f\pm%.2f$"%(TT_incl.GetBinContent(1), TT_incl.GetBinError(1))
  yields_dict["Inclusive"]["Drell-Yan"]  = "$%.2f\pm%.2f$"%(DY_incl.GetBinContent(1), DY_incl.GetBinError(1))
  yields_dict["Inclusive"]["Single Top"] = "$%.2f\pm%.2f$"%(ST_incl.GetBinContent(1), ST_incl.GetBinError(1))
  yields_dict["Inclusive"]["Rares"]      = "$%.2f\pm%.2f$"%(Rare_incl.GetBinContent(1), Rare_incl.GetBinError(1))
  yields_dict["Inclusive"]["Fakes"]      = "$%.2f\pm%.2f$"%(Fakes_incl.GetBinContent(1), Fakes_incl.GetBinError(1))
  yields_dict["Inclusive"]["VV(V)"]      = "$%.2f\pm%.2f$"%(VVV_stack_incl.GetBinContent(1), VVV_stack_incl.GetBinError(1))
  yields_dict["Inclusive"]["SM H"]       = "$%.2f\pm%.2f$"%(SMH_incl.GetBinContent(1), SMH_incl.GetBinError(1))
  yields_dict["Inclusive"]["W+jets"]     = "$%.2f\pm%.2f$"%(WJets_incl.GetBinContent(1), WJets_incl.GetBinError(1))
  yields_dict["Inclusive"]["Total BKG"]  = "$%.2f\pm%.2f$"%(total_bkg.GetBinContent(1), total_bkg.GetBinError(1))
  yields_dict["Inclusive"]["Data"]       = "$%.2f\pm%.2f$"%(data_incl.GetBinContent(1),data_incl.GetBinError(1))
  yields_dict["Inclusive"][sigprocess]  = "$%.2f\pm%.2f$"%(signal_incl.GetBinContent(1), signal_incl.GetBinError(1))
      
  sortedProcess = ["ttbar", "Drell-Yan", "Single Top", "Rares", "Fakes", "VV(V)", "SM H", "W+jets", "Total BKG", sigprocess, "Data"]
  print("  \multicolumn{8}{|c|}{Event yields for the %d data-taking year, integrated luminosity of the dataset %.1f \\fb} \\\\ [1ex] \hline"%(year, lumi))
  print("Process\t & Resolved 1b GGF\t & Resolved 2b GGF\t & Boosted GGF\t & Inclusive DY+VV(V)\t & Resolved Other\t & Boosted Other\t & Inclusive \\\\[0.8ex]\hline ")
  
  for p in sortedProcess:
      if p == "Total BKG": print("\hline")
      pstr = p+"\t & "
      if "Spin" in p:
          pstr = p+"(1 pb) & "
      for cat in sortedKeys:
          pstr += yields_dict[cat][p] + "\t & "
      pstr += yields_dict["Inclusive"][p] +"\\\\ [0.8ex]"
      print(pstr)
  print("\hline \hline")
  return yields_dict["Inclusive"]


def getPlots(spin, mass, year):
  folder = "/Users/taohuang/Documents/CMSANDN/AN-20-119/datacards/resonant/dl/Run2/spin%d/%d/"%(spin, mass)
  resolved1b_file = ROOT.TFile(folder+"HH_DL_%d_resolved1b_GGF_%d.root"%(mass, year))
  resolved2b_file = ROOT.TFile(folder+"HH_DL_%d_resolved2b_GGF_%d.root"%(mass, year))
  boosted_file      = ROOT.TFile(folder+"HH_DL_%d_boosted_GGF_%d.root"%(mass, year))
  resolved1b_card = folder+"HH_DL_%d_resolved1b_GGF_%d.txt"%(mass, year)
  resolved2b_card = folder+"HH_DL_%d_resolved2b_GGF_%d.txt"%(mass, year)
  boosted_card      = folder+"HH_DL_%d_boosted_GGF_%d.txt"%(mass, year)
  DY_file            = ROOT.TFile(folder+"HH_DL_%d_inclusive_DY_VVV_%d.root"%(mass, year))
  resolvedOther_file = ROOT.TFile(folder+"HH_DL_%d_resolved_other_%d.root"%(mass, year))
  boostOther_file    = ROOT.TFile(folder+"HH_DL_%d_boosted_other_%d.root"%(mass, year))
  DY_card            = folder+"HH_DL_%d_inclusive_DY_VVV_%d.txt"%(mass, year)
  resolvedOther_card = folder+"HH_DL_%d_resolved_other_%d.txt"%(mass, year)
  boostOther_card    = folder+"HH_DL_%d_boosted_other_%d.txt"%(mass, year)
  #resolved1b_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_resolved1b_GGF_2016.root")
  #resolved1b_card = 'tao_plots/2016/spin0/m400/HH_DL_400_resolved1b_GGF_2016.txt'
  #resolved2b_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_resolved2b_GGF_2016.root")
  #resolved2b_card = 'tao_plots/2016/spin0/m400/HH_DL_400_resolved2b_GGF_2016.txt'
  #boosted_file = ROOT.TFile("tao_plots/2016/spin0/m400/HH_DL_400_boosted_GGF_2016.root")
  #boosted_card = 'tao_plots/2016/spin0/m400/HH_DL_400_boosted_GGF_2016.txt'
  
  era = "%d"%year
  datapairlist_ggf = [[resolved1b_file, resolved1b_card], [resolved2b_file, resolved2b_card], [boosted_file, boosted_card]] 
  datapairlist_bkg = [[DY_file, DY_card],[resolvedOther_file, resolvedOther_card], [boostOther_file, boostOther_card]]
  makeStackPlots(spin, mass, era, datapairlist_ggf, 1, "GGF_resonant_%d"%year)
  makeStackPlots(spin, mass, era, datapairlist_bkg, 0, "BKG_resonant_%d"%year)


#getPlots(0, 400, 2016)
#getPlots(0, 800, 2016)
#getPlots(0, 400, 2017)
#getPlots(0, 800, 2017)
#getPlots(0, 400, 2018)
#getPlots(0, 800, 2018)
#getPlots(2, 400, 2016)
#getPlots(2, 800, 2016)

masslist = [250, 260, 270, 300, 320, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 900]
#getAllSignalAcceptance(masslist)

def inclusiveYield():
  inclusive_spin2_400_2016 = getYieldTable(2, 400, 2016)
  inclusive_spin2_400_2017 = getYieldTable(2, 400, 2017)
  inclusive_spin2_400_2018 = getYieldTable(2, 400, 2018)
  inclusive_spin2_800_2016 = getYieldTable(2, 800, 2016)
  inclusive_spin2_800_2017 = getYieldTable(2, 800, 2017)
  inclusive_spin2_800_2018 = getYieldTable(2, 800, 2018)
  inclusive_spin0_400_2016 = getYieldTable(0, 400, 2016)
  inclusive_spin0_400_2017 = getYieldTable(0, 400, 2017)
  inclusive_spin0_400_2018 = getYieldTable(0, 400, 2018)
  inclusive_spin0_800_2016 = getYieldTable(0, 800, 2016)
  inclusive_spin0_800_2017 = getYieldTable(0, 800, 2017)
  inclusive_spin0_800_2018 = getYieldTable(0, 800, 2018)
  
  inclusive_dict = {
          2016 : inclusive_spin0_400_2016,
          2017 : inclusive_spin0_400_2017,
          2018 : inclusive_spin0_400_2018
          }
  inclusive_spin0_800_dict = {
          2016 : inclusive_spin0_800_2016,
          2017 : inclusive_spin0_800_2017,
          2018 : inclusive_spin0_800_2018
          }
  inclusive_spin2_400_dict = {
          2016 : inclusive_spin2_400_2016,
          2017 : inclusive_spin2_400_2017,
          2018 : inclusive_spin2_400_2018
          }
  inclusive_spin2_800_dict = {
          2016 : inclusive_spin2_800_2016,
          2017 : inclusive_spin2_800_2017,
          2018 : inclusive_spin2_800_2018
          }
  
  
  def sigYield(thisdict, signame):
    pstr = signame+"(1 pb) & "
    for year in [2016, 2017, 2018]:
        pstr += thisdict[year][signame] + "\t "
        if year != 2018: pstr += "& "
    pstr += "\\\\ [0.5ex]"
    return pstr
  sigprocess = "Spin-%d, %dGeV"%(0, 400)
  sortedProcess = ["ttbar", "Drell-Yan", "Single Top", "Rares", "Fakes", "VV(V)", "SM H", "W+jets", "Total BKG", sigprocess, "Data"]
  print("Process\t & 2016 \t & 2017 \t & 2018 \\\\ \hline ")
  for p in sortedProcess:
      if p == "Total BKG": print("\hline")
      pstr = p+"\t & "
      if "Spin" in p:
          pstr = p+"(1 pb) & "
      for year in [2016, 2017, 2018]:
          pstr += inclusive_dict[year][p] + "\t "
          if year != 2018: pstr += "& "
      pstr += "\\\\ [0.5ex]"
      print(pstr)
      if "Spin" in p:
          sig_spin0_M800 = "Spin-%d, %dGeV"%(0, 800) 
          sig_spin2_M400 = "Spin-%d, %dGeV"%(2, 400) 
          sig_spin2_M800 = "Spin-%d, %dGeV"%(2, 800) 
          print(sigYield(inclusive_spin0_800_dict, sig_spin0_M800))
          print(sigYield(inclusive_spin2_400_dict, sig_spin2_M400))
          print(sigYield(inclusive_spin2_800_dict, sig_spin2_M800))
  print("\hline")

#inclusiveYield()
