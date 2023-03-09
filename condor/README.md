# Condor Instructions

To run on condor, the main script is make_condor_jobs.py, while condor.sub, initialize_condor.sh, and job_template.sh do not require changes

After configuring make_condor_jobs.py with the correct work directory and data files, follow these steps

```
python3 make_condor_jobs.py
cd work_dir/
./initialize_condor.sh
condor_submit condor.sub
```

make_condor_jobs.py will create the work directory, copy the template files, and separate the files into jobs based on chosen options

initialize_condor.sh will check your grid proxy by doing voms-proxy-init, and copying the certificate to the current directory for condor to use

condor.sub will submit all the job*.sh files in the current area
