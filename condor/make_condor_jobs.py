import os
import math

project_folder = "TTBar"
file_list = ["/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/0db470d2-1dfb-471e-b8b0-60fe5cad9ddf.root", "/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/1e132652-55fb-4732-a077-2e1b013c6fc3.root", "/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/35c1c54d-4500-4542-9fb4-51baa6d04083.root"]

project_folder = "data"
file_list = ["/store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/aa5a4b71-fd45-45d9-bf26-ea4f2dc42882.root"]
nFilesPerJob = 2

nJobs = math.ceil(len(file_list)/nFilesPerJob)
remaining_files = file_list

os.mkdir(project_folder)
os.mkdir(project_folder+"/err")
os.mkdir(project_folder+"/log")
os.mkdir(project_folder+"/out")

os.system("cp initialize_condor.sh {}/".format(project_folder))

os.system("cp condor.sub {}/".format(project_folder))


for job_count in range(nJobs):
    job_template = open("job_template.sh", 'r')
    job_file = open(project_folder+"/job{}.sh".format(job_count), 'w')
    for line in job_template:
        if "list_of_files=" in line:
            files_for_this_job = remaining_files[:nFilesPerJob]
            remaining_files = remaining_files[nFilesPerJob:]
            string_to_write = 'list_of_files=("'
            for fname in files_for_this_job:
                string_to_write = string_to_write + 'root://cms-xrd-global.cern.ch//{} '.format(fname)
            string_to_write = string_to_write[:-1] + '")\n'
            job_file.write(string_to_write)
        elif "filename=" in line:
            filename = "job{}.sh".format(job_count)
            job_file.write('filename=("{}")\n'.format(filename))
        else:
            job_file.write(line)



    

