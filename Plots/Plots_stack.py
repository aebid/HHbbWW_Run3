import ROOT, sys, os, string, re
from ROOT import *
from array import array
import math
from math import *

from tdrStyle import *
setTDRStyle()


from LoadData import *
LoadData()

def make_plot(channel, var, bin, low, high, xlabel, xunits, prelim, setLogX, setLogY):

    print('channel: ', channel)
    print('==========================================')
    print(var,low,'-',high,xunits)

    savevar = var    
    save = savevar+'_'+channel

    doratio = True
    #drawunc = False
    lumi2018 = 36.3
    save = save+'_2016'
    List = [
     #DY
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    'DYToLL_0J_13TeV-amcatnloFXFX-pythia8',
    'DYToLL_1J_13TeV-amcatnloFXFX-pythia8',
    'DYToLL_2J_13TeV-amcatnloFXFX-pythia8',
    #'DYToLL_2J_13TeV-amcatnloFXFX-pythia8', #extension sample
    #SM Higgs
     ##ggH
    'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8',
    #'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8', #extension sample
    'GluGluHToGG_M125_13TeV_amcatnloFXFX_pythia8',
    'GluGluHToMuMu_M-125_TuneCP5_PSweights_13TeV_powheg_pythia8',
    'GluGluHToTauTau_M125_13TeV_powheg_pythia8',
    'GluGluHToWWTo2L2Nu_M125_13TeV_powheg_JHUgen_pythia8',
    'GluGluHToWWToLNuQQ_M125_13TeV_powheg_JHUGenV628_pythia8',
    'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8',
    'HZJ_HToWW_M125_13TeV_powheg_pythia8',
     ##VBF
    'VBFHToBB_M-125_13TeV_powheg_pythia8_weightfix',
    #'VBFHToBB_M-125_13TeV_powheg_pythia8_weightfix', #extension sample
    'VBFHToGG_M125_13TeV_amcatnlo_pythia8',
    #'VBFHToGG_M125_13TeV_amcatnlo_pythia8', #extension sample
    'VBFHToMuMu_M-125_TuneCP5_PSweights_13TeV_powheg_pythia8',
    'VBFHToTauTau_M125_13TeV_powheg_pythia8',
    'VBFHToWWTo2L2Nu_M125_13TeV_powheg_JHUgenv628_pythia8',
    'VBFHToWWToLNuQQ_M125_13TeV_powheg_JHUGenV628_pythia8',
    'VBF_HToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8',
    ##VH
    'VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
    ##WH
    'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8',
    #'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', #extension sample
    'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8',
    #'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8', #extension sample
    ##ZH
    'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8',
    'ZHToTauTau_M125_13TeV_powheg_pythia8',
    ##ttH
    'ttHJetTobb_M125_13TeV_amcatnloFXFX_madspin_pythia8',
    'ttHJetToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8_mWCutfix',
    'THQ_ctcvcp_HIncl_M125_TuneCP5_13TeV-madgraph-pythia8',
    #Signal(m=500), Spin0
    ##ggH
    'GluGluToBulkGravitonToHHTo2B2Tau_M-500_narrow_13TeV-madgraph',
    'GluGluToBulkGravitonToHHTo2B2VTo2L2Nu_M-500_narrow_13TeV-madgraph-v2',
    'GluGluToBulkGravitonToHHTo2B2WToLNu2J_M-500_narrow_13TeV-madgraph',
    ##VBF
    #'VBFToBulkGravitonToHHTo2B2Tau_M-500_narrow_TuneCUETP8M1_PSWeights_13TeV-madgraph-pythia8',
    #Signal(m=500), Spin2
    ##ggH
    'GluGluToRadionToHHTo2B2Tau_M-500_narrow_13TeV-madgraph',
    'GluGluToRadionToHHTo2B2VTo2L2Nu_M-500_narrow_13TeV-madgraph-v2',
    'GluGluToRadionToHHTo2B2WToLNu2J_M-550_narrow_13TeV-madgraph', 
    ##VBF
    #'VBFToRadionToHHTo2B2Tau_M-500_narrow_TuneCUETP8M1_PSWeights_13TeV-madgraph-pythia8',
    #single Top 
    #'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
    'ST_s-channel_4f_leptonDecays_13TeV_PSweights-amcatnlo-pythia8',
    'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
    #'ST_t-channel_antitop_4f_inclusiveDecays_13TeV_PSweights-powhegV2-madspin',
    'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
    'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
    #'ST_tWll_5f_LO_13TeV-MadGraph-pythia8',
    'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',  
    'TGJets_leptonDecays_13TeV_amcatnlo_madspin_pythia8', #included in others
    #ttbar
    'TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8',
    'TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8',
    'TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8',
    #mulit
    'TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',#included in others
    #'TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',#included in others #extension sample
    'TTTT_TuneCUETP8M1_13TeV-amcatnlo-pythia8',#included in others
    'TTWH_TuneCUETP8M2T4_13TeV-madgraph-pythia8',#included in others
    #'TTZH_TuneCUETP8M2T4_13TeV-madgraph-pythia8', #included in others #extension sample
    'TTZToLL_M-1to10_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', #included in others
    ##ttw
    'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
    #'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8', #extension sample
    'TTWJetsToQQ_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
    ##ttZ
    'TTZToLL_M-1to10_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    #'TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8', #extension sample
    'TTZToQQ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
     #Tzq
    'tZq_ll_4f_13TeV-amcatnlo-pythia8', #included in others
    'tZq_ll_4f_PSweights_13TeV-amcatnlo-pythia8', #included in others
     #W(WW/WWW)
    'WGToLNuG_01J_5f_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', #included in others
    'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    #'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8', #extension sample
    #WW/WWW
    'WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8', #included in others
    'WWTo2L2Nu_13TeV-powheg',
    'WWTo2L2Nu_DoubleScattering_13TeV-pythia8',
    'WWToLNuQQ_13TeV-powheg',
    #'WWToLNuQQ_13TeV-powheg', #extension sample
    'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8  ',
     #WZ
    'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8', 
    'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
    'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
     #Z(ZZ/ZZZ)
    'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', #included in others
    'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
    'ZZTo4L_13TeV_powheg_pythia8',
    'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
     #Single lep data
     'SingleLepton_UL_2016_NoDuplicates.root',
     #double lep data
     'DoubleLepton_UL_2016_NoDuplicates.root',
        ]
    lumiplot2016 = '35.9 fb^{-1}'
    lumi2016 = 35900
    passedSelection = ""
    if "Double" in channel:
        passedSelection = "Double_Fake | Double_Signal"
    if "Single" in channel:
        passedSelection = "Single_Fake | Single_Signal"
    cut = passedSelection
 
    Variable = {}
    stack = THStack('stack', 'stack')
    added_bkg = TH1D('added_bkg','added_bkg',bin,low,high)
    diboson_triboson_bkg = TH1D('diboson_triboson_bkg', 'diboson_triboson_bkg',bin,low,high)
    singleT_bkg = TH1D('singleT_bkg', 'singleT_bkg',bin,low,high)
    sig_bbzz = TH1D('sig_bbzz', 'sig_bbzz',bin,low,high)
    sig_bbtt = TH1D('sig_bbtt', 'sig_bbtt',bin,low,high)
    sig_bbww = TH1D('sig_bbww', 'sig_bbww',bin,low,high)
    singleH_bkg = TH1D('singleH_bkg', 'singleH_bkg',bin,low,high)
    fake_bkg = TH1D('fake_bkg', 'fake_bkg',bin,low,high)
    wjets_bkg = TH1D('wjets_bkg', 'wjets_bkg',bin,low,high)
    ttbar_bkg = TH1D('ttbar_bkg', 'ttbar_bkg',bin,low,high)
    DY_bkg = TH1D('DY_bkg', 'DY_bkg',bin,low,high)
    others_bkg = TH1D('others_bkg', 'others_bkg',bin,low,high)
    data = TH1D('data', 'data',bin,low,high)
    added_bkg.Sumw2()
    diboson_triboson_bkg.Sumw2()
    singleT_bkg.Sumw2()
    sig_bbzz.Sumw2()
    sig_bbtt.Sumw2()
    sig_bbww.Sumw2()
    singleH_bkg.Sumw2()
    fake_bkg.Sumw2()
    wjets_bkg.Sumw2() 
    ttbar_bkg.Sumw2()
    DY_bkg.Sumw2()
    others_bkg.Sumw2()
    data.Sumw2()

    for Sample in List:
        print(Sample, 'channel: ', channel)
        if ( ('Single' in channel) and (not Sample in Single_Tree)): continue
        if ( ('Double' in channel) and (not Sample in Double_Tree)): continue 
        if (Sample.startswith('Double') or Sample.startswith('Single')):
            weight  = '(1.0)'
        else:
            weight = '('+str(xsection[Sample])+"*"+str(lumi2016)+'/'+str(nEvents[Sample])+')'
            #fix me: all others weigh per event (like PU weight, lepton SF) can mutplied on RH in numenator 
        histName = Sample
        Variable[histName] = TH1D(histName, histName, bin,low,high) 
        print('Sample: ', Sample, ' with Weight: ', weight)
        if ('Single' in channel):
            print('Total entries = ', Single_Tree[Sample].GetEntries())
            if ('Single' in Sample):
                Single_Tree[Sample].Draw(var + " >> " + histName, weight+"*("+ cut + ")", 'goff')
            else:
                Single_Tree[Sample].Draw(var + " >> " + histName, weight+"*("+ cut + ")", 'goff')
        if ('Double' in channel):
            print('Total entries = ', Double_Tree[Sample].GetEntries())
            if ('Double' in Sample):
                Double_Tree[Sample].Draw(var + " >> " + histName, weight+"*("+ cut + ")", 'goff')
            else:
                Double_Tree[Sample].Draw(var + " >> " + histName, weight+"*("+ cut + ")", 'goff')
        print(Sample,Variable[histName].Integral())
        if (Sample.startswith('Data') or Sample.startswith('Single') or Sample.startswith('Double')):
            data.Add(Variable[histName])
        elif (Sample.startswith('fake')): #fix me
            fake_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif (Sample.startswith('TT')):
            ttbar_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif ('GluGluToRadionToHHTo2B2Tau' in Sample ):
            sig_bbtt.Add(Variable[histName])
        elif ('GluGluToRadionToHHTo2B2V' in Sample ):
            sig_bbzz.Add(Variable[histName])
        elif ('GluGluToRadionToHHTo2B2W' in Sample ):
            sig_bbww.Add(Variable[histName])
        elif (Sample.startswith('ST_')):
            singleT_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif (('M125' in Sample ) or ('M-125' in Sample)):
            singleH_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif ('WJetsToLNu' in Sample):
            wjets_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif ('DY' in Sample):
            DY_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        elif (('WW' in Sample) or ('WZ' in Sample) or ('ZZ' in Sample)):
            diboson_triboson_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
        else:
            others_bkg.Add(Variable[histName])
            added_bkg.Add(Variable[histName])
    c1 = TCanvas("c1","c1", 800, 800)
    if (setLogX): c1.SetLogx()
    if (setLogY): c1.SetLogy()
    if (doratio): c1.SetBottomMargin(0.3)
    c1.SetRightMargin(0.03);

    ttbar_bkg.SetFillColor(kGray)
    ttbar_bkg.SetLineColor(kGray+1)
    ttbar_bkg.SetLineWidth(2)

    fake_bkg.SetFillColor(0)
    #fake_bkg.SetLineColor(kOrange+1)
    #fake_bkg.SetLineWidth(2)


    wjets_bkg.SetFillColor(kGreen+2)
    wjets_bkg.SetLineWidth(2)
    wjets_bkg.SetLineColor(kGreen+1)

    DY_bkg.SetFillColor(kMagenta+3)
    DY_bkg.SetLineWidth(2)
    DY_bkg.SetLineColor(kGreen+2)


    diboson_triboson_bkg.SetFillColor(kRed-7)
    diboson_triboson_bkg.SetLineWidth(2)
    diboson_triboson_bkg.SetLineColor(kBlue+0)
 
    singleT_bkg.SetFillColor(kSpring-4)
    singleT_bkg.SetLineWidth(2)
    singleT_bkg.SetLineColor(kSpring-5)

    singleH_bkg.SetFillColor(kCyan+1)
    singleH_bkg.SetLineWidth(2)
    singleH_bkg.SetLineColor(kCyan+2)

    sig_bbzz.SetFillColor(kRed+0)
    sig_bbzz.SetLineColor(kRed+1)
    sig_bbzz.SetLineWidth(2)

    sig_bbtt.SetFillColor(kYellow+0)
    sig_bbtt.SetLineColor(kYellow+1)
    sig_bbtt.SetLineWidth(2)

    sig_bbww.SetFillColor(kMagenta+0)
    sig_bbww.SetLineColor(kMagenta+1)
    sig_bbww.SetLineWidth(2)

    others_bkg.SetFillColor(kRed+3)
    others_bkg.SetLineColor(kRed+2)
    others_bkg.SetLineWidth(2)

    stack.Add(singleH_bkg)
    stack.Add(others_bkg)
    stack.Add(diboson_triboson_bkg)
    stack.Add(fake_bkg)
    stack.Add(DY_bkg)
    stack.Add(singleT_bkg)
    stack.Add(wjets_bkg)
    stack.Add(ttbar_bkg)
    stack.Draw("hist")


    stack.GetXaxis().SetMoreLogLabels(kTRUE)
    if (var=="mass4mu"): stack.GetXaxis().SetRangeUser(80,100.01)
    stack.GetXaxis().SetNoExponent(kTRUE)
    stack.SetMinimum(0.01)
    if (setLogY): stack.SetMaximum(5000*max(stack.GetMaximum(),data.GetMaximum()+1))
    else: 
        if (var=="mass4mu"): stack.SetMaximum(1.2*max(stack.GetMaximum(),data.GetMaximum()+1))
        elif (var=="massZ2" ): stack.SetMaximum(2.4*max(stack.GetMaximum(),data.GetMaximum()+1))
        elif (var=="massZ1" ): stack.SetMaximum(2.8*max(stack.GetMaximum(),data.GetMaximum()+1))
        elif (var=="mass4mu"): stack.SetMaximum(3.5*max(stack.GetMaximum(),data.GetMaximum()+1))
        elif (var=="etaL1"): stack.SetMaximum(2.5*max(stack.GetMaximum(),data.GetMaximum()+1))
        else: stack.SetMaximum(2.0*max(stack.GetMaximum(),data.GetMaximum()+1))
    if (xunits==''): stack.GetXaxis().SetTitle(xlabel)
    else: stack.GetXaxis().SetTitle(xlabel+' ['+xunits+']')
    stack.GetXaxis().SetTitleOffset(0.95)
    stack.GetYaxis().SetTitleOffset(0.95)
    if (doratio): stack.GetXaxis().SetTitleSize(0)
    if (doratio): stack.GetXaxis().SetLabelSize(0)
    binsize = str(round(float((high-low)/bin),2))
    if binsize.endswith('.0'): binsize=binsize.rstrip('.0')
    if (var=="mass4mu"):
        ylabel = 'Events / 0.5 GeV'
    else:
        ylabel = 'Events / bin'
    stack.GetYaxis().SetTitle(ylabel)           

    stack.GetXaxis().SetNdivisions(210);

    data.SetMarkerStyle(20)
    data.SetMarkerSize(0.9)
    data.SetBinErrorOption(TH1.kPoisson)
    data.Draw("ex0psame")
    sig_bbzz.Draw("lsame")
    sig_bbtt.Draw("lsame")
    sig_bbww.Draw("lsame")
    legend = TLegend(.55,.75,.96,.85)
    legend.SetNColumns(2);
    legend.AddEntry(data, 'Data', "ep")
    legend.AddEntry(wjets_bkg,'W + Jets', "f")
    legend.AddEntry(ttbar_bkg, 'ttbar + Jets', "f")
    legend.AddEntry(singleT_bkg, 'Single Top', "f")
    legend.AddEntry(singleH_bkg, 'Single H', "f")
    legend.AddEntry(DY_bkg, 'DY', "f")
    legend.AddEntry(fake_bkg, 'Fakes', "f")
    legend.AddEntry(diboson_triboson_bkg, 'VVV + VV', "f")
    legend.AddEntry(others_bkg, 'Others', "f")
    legend.AddEntry(sig_bbzz, 'Spin0_500_bbzz', "l")
    legend.AddEntry(sig_bbtt, 'Spin0_500_bbtt', "l")
    legend.AddEntry(sig_bbww, 'Spin0_500_bbww', "l")
    legend.SetShadowColor(0);
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.Draw("same")  



    latex2 = TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.6*c1.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right
    latex2.DrawLatex(0.92, 0.94,lumiplot2016+" (13 TeV)")
    latex2.SetTextSize(0.85*c1.GetTopMargin())
    latex2.SetTextFont(62)
    latex2.SetTextAlign(11) # align right
    latex2.DrawLatex(0.2, 0.84, "CMS")
    latex2.SetTextSize(0.7*c1.GetTopMargin())
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    #latex2.DrawLatex(0.28, 0.945, "Unpublished")    
    latex2.DrawLatex(0.2, 0.78, "Preliminary")

    lastbin=bin
    print('')
    print('W+Jets Bkg:',wjets_bkg.Integral(1,lastbin))
    print('ttbar Bkg:',ttbar_bkg.Integral(1,lastbin))
    print('Single Top Bkg:',singleT_bkg.Integral(1,lastbin))
    print('Single H Bkg:',singleH_bkg.Integral(1,lastbin))
    print('DY Bkg:',DY_bkg.Integral(1,lastbin))
    print('Diboson/Triboson Bkg:',diboson_triboson_bkg.Integral(1,lastbin))
    print('Fake Bkg:',fake_bkg.Integral(1,lastbin))
    print('Others Bkg:',others_bkg.Integral(1,lastbin))
    print('Signal bbzz:',sig_bbzz.Integral(1,lastbin))
    print('Signal bbtt:',sig_bbzz.Integral(1,lastbin))
    print('Signal bbww:',sig_bbzz.Integral(1,lastbin))
    print('added Bkg:',added_bkg.Integral(1,lastbin))
    print('Data:',data.Integral(1,lastbin))
    print("KS:",data.KolmogorovTest(added_bkg))
    print('')
    gPad.RedrawAxis()

    if (doratio):
        ratio = data.Clone('ratio')
        ratio.Divide(added_bkg)
        ratio.GetXaxis().SetMoreLogLabels(kTRUE)
        ratio.GetXaxis().SetNoExponent(kTRUE)

        pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 1.0);
        if (setLogX): pad.SetLogx()
        pad.SetTopMargin(0.7);
        pad.SetRightMargin(0.03);
        pad.SetFillColor(0);
        pad.SetGridy(1);
        pad.SetFillStyle(0);
        pad.Draw();        
        pad.cd(0);
        
        if (xunits==''):
            ratio.GetXaxis().SetTitle(xlabel)
        else:    
            ratio.GetXaxis().SetTitle(xlabel+' ['+xunits+']')
        ratio.GetXaxis().SetTitle
        ratio.GetYaxis().SetTitleSize(0.04);
        ratio.GetYaxis().SetTitleOffset(1.5);
        ratio.GetYaxis().SetTitle("Data/Bkg.");
        ratio.GetYaxis().CenterTitle();
        ratio.GetYaxis().SetLabelSize(0.03);
        ratio.SetMarkerStyle(20);
        ratio.SetMarkerSize(1.2);
        ratio.SetLineColor(1)
        ratio.SetMarkerColor(1)
        ratio.SetMinimum(-0.5);
        ratio.SetMaximum(3.0);
        ratio.Draw("ep");
        c1.Modified();
        c1.Update()
    c1.SaveAs('Histo_' + save + '.png')
    c1.SaveAs('Histo_' + save + '.pdf')
make_plot('Singlelepton','ak4_jet1_btagDeepFlavB', 25, 0, 1.0, 'B_{Tag}^{j1}', 'Score', True, False, True)
