import os
import re
import subprocess

os.system("./initialize_condor.sh")
voms_proxy_file = [str(name) for name in re.split(r' |\\n|/', [str(name) for name in subprocess.Popen('voms-proxy-info', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate() if (name != None and "x509" in str(name))][0]) if "x509" in str(name)][0]

for folder1 in os.listdir("."):
    if not os.path.isdir(folder1): continue
    for folder2 in os.listdir("./"+folder1):
        if not os.path.isdir(folder1+"/"+folder2): continue
        os.system("cp "+voms_proxy_file+" "+folder1+"/"+folder2)
