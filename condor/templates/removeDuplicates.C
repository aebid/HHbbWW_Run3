#include <iostream>
#include <set>

void removeDuplicates() {

    TString filename = "SingleLepton_UL_2016.root";

    std::cout<<filename<<std::endl;

    TFile *oldfile = new TFile(filename);
    TTree *oldtree = (TTree*)oldfile->Get("Single_Tree");

    Long64_t nentries = oldtree->GetEntries();
    std::cout<<nentries<<" total entries."<<std::endl;
    UInt_t run, ls;
    ULong64_t event;
    oldtree->SetBranchAddress("run",&run);
    oldtree->SetBranchAddress("ls",&ls);
    oldtree->SetBranchAddress("event",&event);
    //Create a new file + a clone of old tree in new file
    TFile *newfile = new TFile("SingleLepton_UL_2016_NoDuplicates.root","recreate");
    TTree *newtree = oldtree->CloneTree(0);
    std::set<TString> runlumieventSet;
    int nremoved = 0;
    for (Long64_t i=0;i<nentries; i++) {
        if (i%10000==0) std::cout<<i<<"/"<<nentries<<std::endl;
        oldtree->GetEntry(i);

        TString s_Run  = std::to_string(run);
        TString s_Lumi = std::to_string(ls);
        TString s_Event = std::to_string(event);
        TString runlumievent = s_Run+":"+s_Lumi+":"+s_Event;
        
        if (runlumieventSet.find(runlumievent)==runlumieventSet.end()) {
            runlumieventSet.insert(runlumievent);
            newtree->Fill();
        } else {
            nremoved++;
        }
    }

    std::cout<<nremoved<<" duplicates."<<std::endl;
    newtree->Print();
    newtree->AutoSave();
    delete oldfile;
    delete newfile;



    filename = "DoubleLepton_UL_2016.root";

    std::cout<<filename<<std::endl;

    oldfile = new TFile(filename);
    oldtree = (TTree*)oldfile->Get("Double_Tree");

    nentries = oldtree->GetEntries();
    std::cout<<nentries<<" total entries."<<std::endl;
    oldtree->SetBranchAddress("run",&run);
    oldtree->SetBranchAddress("ls",&ls);
    oldtree->SetBranchAddress("event",&event);
    newfile = new TFile("DoubleLepton_UL_2016_NoDuplicates.root","recreate");
    newtree = oldtree->CloneTree(0);
    nremoved = 0;
    for (Long64_t i=0;i<nentries; i++) {
        if (i%10000==0) std::cout<<i<<"/"<<nentries<<std::endl;
        oldtree->GetEntry(i);

        TString s_Run  = std::to_string(run);
        TString s_Lumi = std::to_string(ls);
        TString s_Event = std::to_string(event);
        TString runlumievent = s_Run+":"+s_Lumi+":"+s_Event;

        if (runlumieventSet.find(runlumievent)==runlumieventSet.end()) {
            runlumieventSet.insert(runlumievent);
            newtree->Fill();
        } else {
            nremoved++;
        }
    }

    std::cout<<nremoved<<" duplicates."<<std::endl;
    newtree->Print();
    newtree->AutoSave();
    delete oldfile;
    delete newfile;
}

