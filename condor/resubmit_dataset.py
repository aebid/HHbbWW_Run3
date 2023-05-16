import os
import time
import subprocess

debug = False
cwd = os.getcwd()

resubmit_folder_list = [folder for folder in os.listdir(".") if os.path.isdir(folder)]

for folder1 in resubmit_folder_list:
    if not os.path.isdir(folder1): continue
    print("Looking at dataset ", folder1)
    os.chdir(folder1)
    failed_joblist = []
    finished_joblist = []
    #Find finished jobs and check if failed
    joblist = [f for f in os.listdir('.') if 'job' in f and '.py' not in f and '.root' not in f]
    for job in joblist:
        if debug: print("Job ", job)
        if not os.path.exists("./log/log."+job+".txt"):
            failed_joblist.append(job)
            finished_joblist.append(job)
            #For some reason, the job log is missing
            continue
        #Check if running first, then if failed
        with open("./log/log."+job+".txt") as f:
            freadlines = f.readlines()
            if any("terminated" in line for line in freadlines) or any("aborted" in line for line in freadlines):
                if debug: print("Finished, checking if failed")
                finished_joblist.append(job)
                if not os.path.exists("./out/out."+job+".txt"):
                    failed_joblist.append(job)
                    #For some reason, the job out is missing
                    if debug: print("No out file?")
                    continue
                with open("./out/out."+job+".txt") as f2:
                    if "Finished processing all files!\n" not in f2.readlines():
                        if debug: print("Failed!")
                        #print(job)
                        failed_joblist.append(job)
            else:
                print("Job still running ", job)

    if debug: print("Finished vs failed", len(finished_joblist), len(failed_joblist), len(joblist))

    if len(finished_joblist) == 0:
        print("No jobs are finished, try again later")
        os.chdir(cwd)
        continue

    if len(finished_joblist) != len(joblist):
        print("Some jobs still running, try again later")
        os.chdir(cwd)
        continue

    if len(failed_joblist) == 0:
        print("No failed jobs found for this folder!")
        os.chdir(cwd)
        continue

    condor_submit_file = open("condor.sub", "r")
    condor_resubmit_file = open("condor_resubmit.sub", "w")

    for line in condor_submit_file:
        if "queue filename" in line:
            string_to_write = "queue filename matching files"
            for jobname in failed_joblist:
                string_to_write = string_to_write + " " + jobname
                #print("Removing old log/err/out files")
                os.system("rm ./log/log."+jobname+".txt")
                os.system("rm ./err/err."+jobname+".txt")
                os.system("rm ./out/out."+jobname+".txt")
        else:
            string_to_write = line
        condor_resubmit_file.write(string_to_write)
    condor_submit_file.close()
    condor_resubmit_file.close()
    print("Going to resubmit with jobs ", failed_joblist)
    #Sleep for 5 seconds
    time.sleep(5)
    os.system("condor_submit condor_resubmit.sub")
    os.chdir(cwd)
