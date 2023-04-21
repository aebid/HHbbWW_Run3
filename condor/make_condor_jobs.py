import os
import math
import subprocess
import re
import pickle


def main():

    use_dict = True
    pickle_file = "../dataset/dataset_names/2016/2016_Datasets.pkl"


    project_folder = "TTBar"
    file_list = ["/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/0db470d2-1dfb-471e-b8b0-60fe5cad9ddf.root", "/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/1e132652-55fb-4732-a077-2e1b013c6fc3.root", "/store/mc/Run3Winter22NanoAOD/TTTo2L2Nu_CP5_13p6TeV_powheg-pythia8/NANOAODSIM/122X_mcRun3_2021_realistic_v9-v1/40000/35c1c54d-4500-4542-9fb4-51baa6d04083.root"]

    project_folder = "data3"
    file_list = ["/store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/03dbce72-4887-4164-b63a-7b2eea25abbb.root", "/store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/734b806e-ff93-4d99-b784-0e3164f2dd4e.root", "/store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/aa5a4b71-fd45-45d9-bf26-ea4f2dc42882.root", "/store/data/Run2022C/DoubleMuon/NANOAOD/PromptNanoAODv10_v1-v1/50000/e3a97f0b-715d-40d3-9763-7a3070a5fe5c.root"]

    nFilesPerJob = 5
    subdir = "2016_jobs/"

    if use_dict:
        dataset_dict = pickle.load(open(pickle_file, 'rb'))
        nDataSets = len(dataset_dict.keys())
        print("Going over {} datasets".format(nDataSets))
        for i,dataset_name in enumerate(dataset_dict.keys()):
            if i%(int(nDataSets/10)) == 0:
                print("At dataset {}".format(i))
            project_folder = dataset_name.split('/')[1]
            file_list = dataset_dict[dataset_name]
            make_jobs(subdir, project_folder, file_list, nFilesPerJob)
    else:
        make_jobs(subdir, project_folder, file_list, nFilesPerJob)


def make_jobs(subdir, project_folder, file_list, nFilesPerJob):
    print("Making "+subdir+project_folder)
    print("There are ", len(file_list), "total files")

    nJobs = math.ceil(len(file_list)/nFilesPerJob)
    remaining_files = file_list

    if not os.path.exists(subdir):
        os.mkdir(subdir)
    project_folder = subdir+project_folder
    if not os.path.exists(project_folder):
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

    voms_proxy_file = [str(name) for name in re.split(r' |\\n|/', [str(name) for name in subprocess.Popen('voms-proxy-info', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate() if (name != None and "x509" in str(name))][0]) if "x509" in str(name)][0]

    condor_sub_template = open("condor.sub", 'r')
    condor_sub_file = open(project_folder+"/condor.sub", 'w')
    for line in condor_sub_template:
        if "Proxy_filename          =" in line:
            string_to_write = "Proxy_filename          = {}\n".format(voms_proxy_file)
        elif "transfer_input_files    =" in line:
            cwd = os.getcwd()
            pwd_to_python = cwd[:-6] + "python"
            string_to_write = "transfer_input_files    = $(Proxy_path), {}\n".format(pwd_to_python)
        else:
            string_to_write = line
        condor_sub_file.write(string_to_write)

if __name__ == '__main__':
    main()
