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

## To run on entire datasets from a pkl file

make_condor_jobs.py will create the subdirectory and individual folders for each dataset

You can utilize initialize_condor_ALL.py, submit_all.py, and resubmit_all.py to manage multiple datasets at once

```
python3 make_condor_jobs.py
cd work_dir/
python3 initialize_condor_ALL.py
python3 submit_all.py
```

And to resubmit failed jobs

```
python3 resubmit_all.py
```

Or to submit individual datasets, you can use submit_dataset.py and resubmit_dataset.py

```
python3 make_condor_jobs.py
cd work_dir/
python3 initialize_condor_ALL.py
cd dataset/
python3 submit_dataset.py
```

And to resubmit failed jobs

```
python3 resubmit_dataset.py
```



