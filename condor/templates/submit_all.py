import os
import re
import subprocess

cwd = os.getcwd()
for folder1 in os.listdir("."):
    if not os.path.isdir(folder1): continue
    print("Submitting dataset ", folder1)
    os.chdir(folder1)
    os.system("python3 submit_dataset.py")
    os.chdir(cwd)
