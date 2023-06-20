import os
import re
import subprocess
import time
import ROOT

def check_jobs():
    subfolder_pass_rate_hist = ROOT.TH1F("subfolder_pass_rate", "subfolder_pass_rate", 11, 0, 1.1)
    cwd = os.getcwd()

    dataset_list = [folder for folder in os.listdir(".") if os.path.isdir(folder)]
    finished_dataset_list = []

    for dataset in dataset_list:
        if not os.path.isdir(dataset): continue
        os.chdir(dataset)

        subfolder_list = [folder for folder in os.listdir(".") if os.path.isdir(folder)]
        finished_subfolder_list = []

        for subfolder in subfolder_list:
            os.chdir(subfolder)

            joblist = [job for job in os.listdir(".") if 'job' in job and '.py' not in job and '.root' not in job]
            finished_joblist = []
            if len(joblist) == 0:
                print("Bad dataset! No jobs!!!", dataset, subfolder)
                continue

            for job in joblist:
                if not os.path.exists("./out/out."+job+".txt"): continue
                with open("./out/out."+job+".txt") as f:
                    if "Finished processing all files!\n" in f.readlines():
                        finished_joblist.append(job)


            job_pass_rate = len(finished_joblist)/len(joblist)
            print("Dataset " + dataset + " Subfolder " + subfolder + " had success rate ", job_pass_rate, len(finished_joblist), len(joblist))
            subfolder_pass_rate_hist.Fill(job_pass_rate)
            if job_pass_rate == 1:
                finished_subfolder_list.append(dataset)

            os.chdir("..")

        subfolder_pass_rate = len(finished_subfolder_list)/len(subfolder_list)
        #print("Dataset " + dataset + " had success rate ", subfolder_pass_rate)
        if subfolder_pass_rate == 1:
            finished_dataset_list.append(dataset)

        os.chdir(cwd)

    dataset_pass_rate = len(finished_dataset_list)/len(dataset_list)
    print("Percentage of datasets finished ", dataset_pass_rate, len(finished_dataset_list), len(dataset_list))


    H_ref = 800
    W_ref = 800
    W = W_ref*2
    H = H_ref*2

    T = 0.12*H_ref
    B = 0.16*H_ref
    L = 0.16*W_ref
    R = 0.08*W_ref

    canvas1 = ROOT.TCanvas("c1", "c1", 100, 100, W, H)
    canvas1.SetFillColor(0)
    canvas1.SetBorderMode(0)
    canvas1.SetFrameFillStyle(0)
    canvas1.SetFrameBorderMode(0)
    canvas1.SetLeftMargin( L/W )
    canvas1.SetRightMargin( R/W )
    canvas1.SetTopMargin( T/H )
    canvas1.SetBottomMargin( B/H )
    canvas1.SetTickx(0)
    canvas1.SetTicky(0)

    h1 = subfolder_pass_rate_hist
    h1.Draw()
    xaxis = h1.GetXaxis()
    yaxis = h1.GetYaxis()
    xaxis.SetTitle("Job Pass Rate")
    yaxis.SetTitle("Entries")
    h1.SetStats(0)

    canvas1.SaveAs("condor_job_analysis.pdf")


    return dataset_pass_rate


cwd = os.getcwd()

resub = True

while resub:
    for folder1 in os.listdir("."):
        if not os.path.isdir(folder1): continue
        print("Submitting dataset ", folder1)
        time.sleep(2)
        os.chdir(folder1)
        os.system("python3 resubmit_dataset.py")
        os.chdir(cwd)

    job_status = check_jobs()
    print("Job status has dataset pass rate ", job_status)
    if job_status >= 1.0: resub = False
    time.sleep(5)



