import os

storage_dir = "/eos/user/d/daebi/2016_jobs_2filesper/"

datasetnames = os.listdir(".")
for datasetname in datasetnames:
    if not os.path.isdir(datasetname): continue
    os.makedirs(storage_dir+"/"+datasetname)
    subfoldernames = os.listdir(datasetname+"/.")
    for subfolder in subfoldernames:
        if not os.path.isdir(datasetname+"/"+subfolder): continue
        os.system("ls "+datasetname+"/"+subfolder+"/.")
        os.system("hadd "+datasetname+"/out_"+subfolder+".root "+datasetname+"/"+subfolder+"/out_condor_job*.sh.root")
        os.system("mv "+datasetname+"/out_"+subfolder+".root "+storage_dir+"/"+datasetname+"/.")
