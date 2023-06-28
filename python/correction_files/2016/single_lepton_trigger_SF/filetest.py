import ROOT
import array

el_file = ROOT.TFile("Electron_Run2016_legacy_Ele25.root")
mu_file = ROOT.TFile("Muon_Run2016_legacy_IsoMu22.root")


def find_binning(input_file):
  eta_binlist = []
  pt_binlist = []
  for key in input_file.GetListOfKeys():
    name = key.GetName()
    print(name)
    if "etaBinsH" in name: continue
    if "MC" in name: continue

    if "Lt" in name: #Less than
      name_list = name.split("Lt")[1]
      high_lim_list = (name_list.split("_")[0]).split("p")
      high_lim = int(high_lim_list[0])+int(high_lim_list[1])*0.1**(len(high_lim_list[1]))

      eta_binlist.append(0)

    elif "Gt" in name: #Greater than
      name_list = name.split("Gt")[1]
      low_lim_list = (name_list.split("_")[0]).split("p")
      low_lim = int(low_lim_list[0])+int(low_lim_list[1])*0.1**(len(low_lim_list[1]))

      eta_binlist.append(low_lim)

    elif "to" in name: # low < x < high
      name_list = name.split("to")
      low_lim_list = (name_list[0].split("Eta")[1]).split("p")
      low_lim = int(low_lim_list[0])+int(low_lim_list[1])*0.1**(len(low_lim_list[1]))

      high_lim_list = (name_list[1].split("_")[0]).split("p")
      high_lim = int(high_lim_list[0])+int(high_lim_list[1])*0.1**(len(high_lim_list[1]))

      eta_binlist.append(low_lim)

    if "Lt" in name:
      t = key.ReadObj()
      #print("entries = ", t.GetN())
      nEntries = t.GetN()
      for i in range(nEntries):
        #print("x = ", t.GetX()[i])
        #print("y = ", t.GetY()[i])
        #print("error = ", t.GetErrorX(i))
        pt_binlist.append(t.GetX()[i]-t.GetErrorX(i))
      pt_binlist.append(t.GetX()[nEntries-1]+t.GetErrorX(nEntries-1))


  eta_binlist.append(2.5) #Upper limit
  print("eta_binlist = ", eta_binlist)
  print("pt_binlist = ", pt_binlist)

  return eta_binlist, pt_binlist


def fill_profile(input_file, hist):
  print("Starting to fill hist")
  SF = 0.0 #Will fill later
  error = 0.0 #Will fill later
  for key in input_file.GetListOfKeys():
    name_MC = key.GetName()
    if "MC" not in name_MC: continue
    eta = 0.0 #Initial eta to fill, will find real value

    name_Data = name_MC[:-2]+"Data"
    for key2 in input_file.GetListOfKeys():
      if key2.GetName() == name_Data:
        print("Found Match")
        print(name_MC, name_Data)

        if "Lt" in name_MC:
          eta_bin_finder = name_MC.split("Lt")[1]
          eta_bin_finder_high = (eta_bin_finder.split("_")[0]).split("p")
          eta_bin_finder_value_high = int(eta_bin_finder_high[0])+int(eta_bin_finder_high[1])*0.1**(len(eta_bin_finder_high[1]))
          eta_bin_finder_value_low = 0
          print("Eta bin values are ", eta_bin_finder_value_low, eta_bin_finder_value_high)

        elif "Gt" in name_MC:
          eta_bin_finder = name_MC.split("Gt")[1]
          eta_bin_finder_low = (eta_bin_finder.split("_")[0]).split("p")
          eta_bin_finder_value_low = int(eta_bin_finder_low[0])+int(eta_bin_finder_low[1])*0.1**(len(eta_bin_finder_low[1]))
          eta_bin_finder_value_high = 2.5
          print("Eta bin values are ", eta_bin_finder_value_low, eta_bin_finder_value_high)

        elif "to" in name_MC:
          eta_bin_finder = name_MC.split("to")
          eta_bin_finder_low = (eta_bin_finder[0].split("Eta")[1]).split("p")
          eta_bin_finder_value_low = int(eta_bin_finder_low[0])+int(eta_bin_finder_low[1])*0.1**(len(eta_bin_finder_low[1]))

          eta_bin_finder_high = (eta_bin_finder[1].split("_")[0]).split("p")
          eta_bin_finder_value_high = int(eta_bin_finder_high[0])+int(eta_bin_finder_high[1])*0.1**(len(eta_bin_finder_high[1]))

          print("Eta bin values are ", eta_bin_finder_value_low, eta_bin_finder_value_high)


        eta = (eta_bin_finder_value_low + eta_bin_finder_value_high)/2.0
        print("Eta chosen = ", eta)
        pT = 0.0 #Initial pT to fill, will find real value
        t_MC = key.ReadObj()
        t_Data = key2.ReadObj()
        nEntries_MC = t_MC.GetN()
        nEntries_Data = t_Data.GetN()
        for i in range(nEntries_MC):
          pT = t_MC.GetX()[i]
          print("pT chosen = ", pT)
          MC_efficiency = t_MC.Eval(pT)			#CMSSW 10 does not include GetPointY(i)
          Data_efficiency = t_Data.Eval(pT)		#Must use Eval(pT) instead
          #MC_efficiency = t_MC.GetPointY(i)
          #Data_efficiency = t_Data.GetPointY(i)
          MC_error = t_MC.GetErrorY(i)
          Data_error = t_Data.GetErrorY(i)
          print("MC   eff:err", MC_efficiency, MC_error)
          print("Data eff:err", Data_efficiency, Data_error)

          if MC_efficiency != 0: 
            SF = Data_efficiency/MC_efficiency
            if Data_efficiency == 0:
              error = 0 #???
            else:
              error = ((Data_error/Data_efficiency)**2 + (MC_error/MC_efficiency)**2)**(0.5)*SF
          if MC_efficiency == 0 and Data_efficiency == 0: 
            SF = 1
            error = 0 #???
            #error = ((Data_error/Data_efficiency)**2 + (MC_error/MC_efficiency)**2)**(0.5)*SF
          if "El" in input_file and eta > 2.1: 
            SF = 1
            error = 0 #???
            #error = ((Data_error/Data_efficiency)**2 + (MC_error/MC_efficiency)**2)**(0.5)*SF




          #Finally putting the info into the hist
          xBin = hist.GetXaxis().FindBin(eta)
          yBin = hist.GetYaxis().FindBin(pT)
          print("eta, pT = ", eta, pT)
          print("Filling ", xBin, yBin, " with ", SF, " and error ", error)
          hist.SetBinContent(xBin, yBin, SF)
          hist.SetBinError(xBin, yBin, error)


f_new = ROOT.TFile("ele_and_mu_SF_2016.root", "recreate")
c1 = ROOT.TCanvas("", "", 1280, 800)
print("Electron file")
ele_bins = find_binning(el_file)
eta_bins = len(ele_bins[0])-1
eta_array = array.array('d', ele_bins[0])
pT_bins = len(ele_bins[1])-1
pT_array = array.array('d', ele_bins[1])
SF_ele = ROOT.TH2F("ele_SF", "ele_SF", eta_bins, eta_array, pT_bins, pT_array) #x = eta, y = pT
fill_profile(el_file, SF_ele)
SF_ele.SetStats(0)
SF_ele.Draw("colz text")
c1.SaveAs("Ele_SF.png")

print("Muon file")
mu_bins = find_binning(mu_file)
eta_bins = len(mu_bins[0])-1
eta_array = array.array('d', mu_bins[0])
pT_bins = len(mu_bins[1])-1
pT_array = array.array('d', mu_bins[1])
SF_mu = ROOT.TH2F("mu_SF", "mu_SF", eta_bins, eta_array, pT_bins, pT_array) #x = eta, y = pT
fill_profile(mu_file, SF_mu)
SF_mu.SetStats(0)
SF_mu.Draw("colz text")
c1.SaveAs("Mu_SF.png")


f_new.Write()
