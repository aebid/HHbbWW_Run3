import os
import time
import subprocess

cwd = os.getcwd()

for folder1 in os.listdir("."):
    if not os.path.isdir(folder1): continue

    os.chdir(folder1)

    os.system("condor_submit condor.sub")

    os.chdir(cwd)
