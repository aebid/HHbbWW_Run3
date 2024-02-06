from ROOT import *
from array import array
import sys, os, pwd, subprocess
import optparse, shlex, re
import time
from time import gmtime, strftime
import math
import pickle

filesdir = '/eos/user/d/daebi/2022_data_5Feb24/'

datafilelist = []
MCfilelist = []

for dataset in os.listdir(filesdir):
  fulldataset = filesdir+dataset+"/"
  if os.path.isdir(fulldataset):
    #At this level is DATA, but MC is still one more folder down
    if dataset == "data":
      for datafile in os.listdir(fulldataset):
        fulldatafile = fulldataset+datafile
        if os.path.isfile(fulldatafile) and ("NoDuplicates" in fulldatafile):
          datafilelist.append(fulldatafile)
    elif dataset not in ["SingleElectron", "SingleMuon", "DoubleEG", "DoubleMuon", "MuonEG", "Muon", "EGamma"]:
      for subdir in os.listdir(fulldataset):
        fullsubdir = fulldataset+subdir+"/"
        if os.path.isdir(fullsubdir):
          for mcfile in os.listdir(fullsubdir):
            fullmcfile = fullsubdir+mcfile
            if os.path.isfile(fullmcfile):
              MCfilelist.append(fullmcfile)

RootFile = {}
Single_Tree = {}
Double_Tree = {}
nEvents = {}
xsection = {}

datasetInfo = pickle.load(open("../dataset/dataset_names/2022/2022_Datasets.pkl", "rb"))
def loaddata():
  for mcfile in MCfilelist:
    datasetname = mcfile.split('/')[-3]
    datasetsubname = mcfile.split('/')[-2]
    LUT_key = "/"+datasetname+"/"+datasetsubname+"/NANOAODSIM"


    if datasetname in nEvents:
      print("Already found dataset ", datasetname, " extending!!!")

      #Commenting out for now to handle extensions better
      #nEvents[datasetname] = int(datasetInfo['nevents'][LUT_key])
      #print("Dataset already exists, lets find the value inside the nEvents tree")
      f_tmp = TFile(mcfile)
      t_tmp = f_tmp.Get("nEvents")
      nEvtTot = 0
      for event in t_tmp:
          nEvtTot += event.nEvents
      #print("nEvents in file is ", nEvtTot)
      #print("But pkl said ", int(datasetInfo['nevents'][LUT_key]))
      nEvents[datasetname] += nEvtTot
      if xsection[datasetname] != datasetInfo['xs'][LUT_key]:
        print("BAD XSEC FOR THIS SAMPLE, EXTENSION DOESN'T MATCH!")
    else:
      print("New dataset ", datasetname)
      Single_Tree[datasetname] = TChain("Single_Tree")
      Double_Tree[datasetname] = TChain("Double_Tree")

      #Commenting out for now to handle extensions better
      #nEvents[datasetname] = int(datasetInfo['nevents'][LUT_key])

      f_tmp = TFile(mcfile)
      t_tmp = f_tmp.Get("nEvents")
      nEvtTot = 0
      for event in t_tmp:
          nEvtTot += event.nEvents
      #print("nEvents in file is ", nEvtTot)
      #print("But pkl said ", int(datasetInfo['nevents'][LUT_key]))
      nEvents[datasetname] = nEvtTot

      xsection[datasetname] = datasetInfo['xs'][LUT_key]

    Single_Tree[datasetname].Add(mcfile)
    Double_Tree[datasetname].Add(mcfile)

    if (not Single_Tree[datasetname]): print(datasetname+' has no Single tree')
    #else: print(datasetname,"nevents",nEvents[datasetname],"xsection",xsection[datasetname])
    if (not Double_Tree[datasetname]): print(datasetname+' has no Double tree')
    #else: print(datasetname,"nevents",nEvents[datasetname],"xsection",xsection[datasetname])



  for datafile in datafilelist:
    datafilename = datafile.split("/")[-1]

    RootFile[datafilename] = TFile(datafile, "READ")
    if ('Single' in datafilename):
      Single_Tree[datafilename] = RootFile[datafilename].Get("Single_Tree")
      if (not Single_Tree[datafilename]): print(datafilename+' has no Single tree')
    if ('Double' in datafilename):
      Double_Tree[datafilename] = RootFile[datafilename].Get("Double_Tree")
      if (not Double_Tree[datafilename]): print(datafilename+' has no Double tree')
