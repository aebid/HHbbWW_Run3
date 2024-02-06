import ROOT, sys, os, string, re
from ROOT import *
from array import array
import math
from math import *

from tdrStyle import *
setTDRStyle()


import time
startTime = time.time()

from load_files import *
loaddata()
print('loaddata in seconds: ' + str((time.time() - startTime)))


def make_plot(channel, var, bin, low, high, xlabel, xunits, prelim, setLogX, setLogY, passedSelection="", plotdir = ""):
    if plotdir != "": os.makedirs(plotdir, exist_ok = True)


    print('channel: ', channel)
    print('==========================================')
    print(var,low,'-',high,xunits)

    savevar = var
    save = savevar+'_'+channel

    doratio = True
    #drawunc = False
    save = save+'_2022'

    List = []

    if 'Single' in channel: List = Single_Tree.keys()
    if 'Double' in channel: List = Double_Tree.keys()
    print("List is ", List)
    lumiplot2022 = '35.08 fb^{-1}'
    lumi2022 = 35080

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
            weight = '('+str(xsection[Sample])+"*"+str(lumi2022)+'/'+str(nEvents[Sample])+')'
            #fix me: all others weigh per event (like PU weight, lepton SF) can mutplied on RH in numenator
        histName = Sample
        Variable[histName] = TH1D(histName, histName, bin,low,high)
        print('Sample: ', Sample, ' with Weight: ', weight)
        print("Before fill we have")
        print(Sample,Variable[histName].Integral())
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
            if ('Single' in channel): #W+Jets only in the Single Category (Double will have it in 'Fakes'
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

    c1.SetGrid()

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
    if ('Single' in channel): #W+Jets only in the Single Category (Double will have it in 'Fakes'
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
    latex2.DrawLatex(0.92, 0.94,lumiplot2022+" (13 TeV)")
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

    print('Lets look at bin1 only')
    print('W+Jets Bkg:',wjets_bkg.Integral(1,2))
    print('ttbar Bkg:',ttbar_bkg.Integral(1,2))
    print('Single Top Bkg:',singleT_bkg.Integral(1,2))
    print('Single H Bkg:',singleH_bkg.Integral(1,2))
    print('DY Bkg:',DY_bkg.Integral(1,2))
    print('Diboson/Triboson Bkg:',diboson_triboson_bkg.Integral(1,2))
    print('Fake Bkg:',fake_bkg.Integral(1,2))
    print('Others Bkg:',others_bkg.Integral(1,2))
    print('Signal bbzz:',sig_bbzz.Integral(1,2))
    print('Signal bbtt:',sig_bbzz.Integral(1,2))
    print('Signal bbww:',sig_bbzz.Integral(1,2))
    print('added Bkg:',added_bkg.Integral(1,2))
    print('Data:',data.Integral(1,2))
    gPad.RedrawAxis()

    if (doratio):
        print("Starting doRatio, checking bin 5")
        ratio = data.Clone('ratio')
        print(ratio.GetBinContent(5))
        ratio.Add(added_bkg, -1)
        print(ratio.GetBinContent(5))
        ratio.Divide(added_bkg)
        print(ratio.GetBinContent(5))
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
        ratio.GetYaxis().SetTitleSize(0.03);
        ratio.GetYaxis().SetTitleOffset(1.5);
        ratio.GetYaxis().SetTitle("#frac{Data-Bkg}{Bkg}");
        ratio.GetYaxis().CenterTitle();
        ratio.GetYaxis().SetLabelSize(0.03);
        ratio.SetMarkerStyle(20);
        ratio.SetMarkerSize(1.2);
        ratio.SetLineColor(1)
        ratio.SetMarkerColor(1)
        ratio.SetMinimum(-0.5);
        ratio.SetMaximum(0.5);
        ratio.Draw("ep");
        c1.Modified();
        c1.Update()
    #c1.SaveAs('Histo_' + save + '_' + passedSelection + '.png')
    #c1.SaveAs('Histo_' + save + '_' + passedSelection + '.pdf')

    c1.SaveAs(plotdir+'Histo_' + save + '.pdf')
    print('Finished {var} {cut} plots at: '.format(var = var, cut = passedSelection) + str((time.time() - startTime)))
    del var
    del histName



print('Starting plots at: ' + str((time.time() - startTime)))

#Double Channel DNN Input Plots
base_dl_cut = "((Double_Signal) && (nBjets_pass) && (Zveto))"
plotdir = "feb5_run3"

#Boosted Plots
var = 'n_ak8_jets'
varname = 'n fatjets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")



var = 'n_cleaned_ak8_jets'
varname = 'n cleaned fatjets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")


var = 'n_btag_ak8_jets'
varname = 'n btagged fatjets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")



var = 'ak8_jet0_pt'
varname = 'fatjet 0 pT'
varunit = 'GeV'
nBins = 100
binlow = 200.0
binhigh = 800.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")





var = 'ak8_jet0_eta'
varname = 'fatjet 0 eta'
varunit = 'GeV'
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")







var = 'ak8_jet0_subjet1_pt'
varname = 'fatjet 0 subjet1 pT'
varunit = 'GeV'
nBins = 50
binlow = 0.0
binhigh = 500.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")


var = 'ak8_jet0_subjet2_pt'
varname = 'fatjet 0 subjet2 pT'
varunit = 'GeV'
nBins = 50
binlow = 0.0
binhigh = 500.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")






var = 'll_mass'
varname = 'll invar mass'
varunit = 'GeV'
nBins = 60
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")









var = 'lep0_pt'
varname = 'lep0 pt'
varunit = 'GeV'
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")




var = 'lep1_pt'
varname = 'lep1 pt'
varunit = 'GeV'
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")




var = 'lep0_eta'
varname = 'lep0 eta'
varunit = 'GeV'
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")





var = 'lep1_eta'
varname = 'lep1 eta'
varunit = 'GeV'
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_ee/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_mm/")

cut = base_dl_cut+" && (Double_HbbFat) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/boosted_em/")














#Resolved 1B Plots
base_dl_cut = "((Double_Signal) && (nBjets_pass) && (Zveto))"
plotdir = "feb5_run3"

var = 'n_ak4_jets'
varname = 'n jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")



var = 'n_cleaned_ak4_jets'
varname = 'n cleaned jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")



var = 'n_medium_btag_ak4_jets'
varname = 'n medium btagged jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")




var = 'ak4_jet0_pt'
varname = 'ak4 jet0 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 500.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")


var = 'ak4_jet1_pt'
varname = 'ak4 jet1 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 500.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")





var = 'ak4_jet0_eta'
varname = 'ak4 jet0 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")


var = 'ak4_jet1_eta'
varname = 'ak4 jet1 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")










var = 'lep0_pt'
varname = 'lep0 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")


var = 'lep1_pt'
varname = 'lep1 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")


var = 'lep0_eta'
varname = 'lep0 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")


var = 'lep1_eta'
varname = 'lep1 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")



var = 'll_mass'
varname = 'll invar mass'
varunit = 'GeV'
nBins = 60
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_ee/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_mm/")

cut = base_dl_cut+" && (Double_Res_1b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res1b_em/")














#Resolved 2B Plots
base_dl_cut = "((Double_Signal) && (nBjets_pass) && (Zveto))"
plotdir = "feb5_run3"

var = 'n_ak4_jets'
varname = 'n jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")



var = 'n_cleaned_ak4_jets'
varname = 'n cleaned jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")



var = 'n_medium_btag_ak4_jets'
varname = 'n medium btagged jets'
varunit = ''
nBins = 10
binlow = -0.5
binhigh = 9.5

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")




var = 'ak4_jet0_pt'
varname = 'ak4 jet0 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 500.0
cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")


var = 'ak4_jet1_pt'
varname = 'ak4 jet1 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 500.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")





var = 'ak4_jet0_eta'
varname = 'ak4 jet0 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")


var = 'ak4_jet1_eta'
varname = 'ak4 jet1 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")






var = 'lep0_pt'
varname = 'lep0 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")


var = 'lep1_pt'
varname = 'lep1 pt'
varunit = ''
nBins = 100
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")


var = 'lep0_eta'
varname = 'lep0 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")


var = 'lep1_eta'
varname = 'lep1 eta'
varunit = ''
nBins = 30
binlow = -3.0
binhigh = 3.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")



var = 'll_mass'
varname = 'll invar mass'
varunit = 'GeV'
nBins = 60
binlow = 0.0
binhigh = 300.0

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_ee)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_ee/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_mm)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_mm/")

cut = base_dl_cut+" && (Double_Res_2b) && (double_is_em || double_is_me)"
make_plot('Doublelepton',var, nBins, binlow, binhigh, varname, varunit, True, False, True, cut, plotdir+"/res2b_em/")
