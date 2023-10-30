# Condor Instructions

To run on condor, the main script make_condor_jobs.py will create jobs based on your configurations and will pull template files from the templates folder

Base configurations are to use the pickle file dictionary, and will need a user input for what storage folder and subdirectory folder to save files in

```
python3 make_condor_jobs.py
cd work_dir/
```


After configuring make_condor_jobs.py with the correct work directory and data files, there are options to submit the entire year, individual datasets, or even individual jobs

## To run on all datasets

```
python3 initialize_condor_ALL.py
python3 submit_all.py
```

initialize_condor_ALL.py will check your grid proxy by doing voms-proxy-init, and then copying the certificate to the subdirectories for condor to access and send to the node (required for xrootd to load input files remotely)

condor_submit.py will submit all datasets

Condor nodes are not always working, and xrootd has its own efficiency, so resubmissions are required. You can automatically resubmit failed jobs in a loop with

```
python3 resubmit_all.py
```


This will look at the log/error/out files of the condor jobs and check which ones have failed. It will give a note whether the job failed to do xrootd timeout (most common) or a different error that should be checked by hand later. It will also create a simple histogram to check the performance of all jobs.

NOTE: resubmit_all.py will only create the plot with default configuration, to actually resubmit the jobs, you must change the 'resub = False' line to True.


## To run on single datasets

```
python3 initialize_condor_ALL.py
cd dataset/
python3 submit_dataset.py
```

This will submit only the specific dataset, and to resubmit failed jobs use

```
python3 resubmit_dataset.py
```


## To run on single files

```
cd dataset/
cd subfolder/
cd submit_by_hand/
chmod 755 job#.sh
voms-proxy-init --rfc --voms cms -valid 192:00
./job#.sh
```

After picking a dataset and a subfolder, you must go into the submit by hand folder and give execute permissions to the job you want to run. Then initialize your grid certificate and run the job directly.



As you add more information (genParts, SF) you may need more memory, you can edit a held job with

```
condor_qedit JOB.ID RequestMemory MemAmountInBytes
condor_release UserName
```

This would change the memory and release the job to run again
