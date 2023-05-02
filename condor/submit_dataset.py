import os


for folder1 in os.listdir("."):
    if not os.path.isdir(folder1): continue
    os.system("cd "+folder1)
    os.system("condor_submit condor.sub")
    os.system("cd ..")
