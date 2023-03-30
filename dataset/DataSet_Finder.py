#!/usr/bin/python
import sys, os, pwd, commands
import optparse, shlex, re
import time
from time import gmtime, strftime
import math
#define function for parsing options
def parseOptions():
    global observalbesTags, modelTags, runAllSteps

    usage = ('usage: %prog [options]\n'
             + '%prog -h for help')
    parser = optparse.OptionParser(usage)

    # input options
    parser.add_option('-d', '--datasets', dest='DATASETS', type='string', default='DatasetRun2_legacy.txt', help='txt file with datasets to run over')
    parser.add_option('-s', '--substring', dest='SUBSTRING', type='string', default='', help='only submit datasets with this string in the name')

    # store options and arguments as global variables
    global opt, args
    (opt, args) = parser.parse_args()
# define function for processing the external os commands
def processCmd(cmd, quite = 0):
    #    print cmd
    status, output = commands.getstatusoutput(cmd)
    if (status !=0 and not quite):
        print 'Error in processing command:\n   ['+cmd+']'
        print 'Output:\n   ['+output+'] \n'
        return "ERROR!!! "+output
    else:
        return output

def datasetParser():

    # parse the arguments and options
    global opt, args
    parseOptions()
    # get the datasets
    print '[Gathering Dataset Information]'
    datasets = []
    cross_section = {}
    nfiles = {}
    nevents = {}
    datasetfiles = {}

    with open(opt.DATASETS, "r") as datasetfile:
        for line in datasetfile:

            if (line.startswith('#')): continue

            if ( not (opt.SUBSTRING=="")):
                if (not (opt.SUBSTRING in line)): continue

            dataset = line.split()[0]
            dataset = dataset.rstrip()
            dataset = dataset.lstrip()

            datasets.append(dataset)
            cross_section[dataset] = float(line.split()[1])
            
            cmd = '/cvmfs/cms.cern.ch/common/dasgoclient --query="file dataset='+dataset+'" --limit=10 | grep ".root"'
            output = processCmd(cmd)
            while ('error' in output):
                time.sleep(1.0);
                output = processCmd(cmd)
            datasetfiles[dataset] =  output.split()
            nfiles[dataset] = len(datasetfiles[dataset])
 
            cmd = '/cvmfs/cms.cern.ch/common/dasgoclient --query="dataset dataset='+dataset+' | grep dataset.nevents" --limit=0'
            print cmd
            output = processCmd(cmd)
            while ('error' in output):
                time.sleep(1.0);
                output = processCmd(cmd)
            nevents[dataset] = (output.rstrip()).lstrip()
            print dataset,'xs:',cross_section[dataset],'nfiles:',nfiles[dataset],'nevents:',nevents[dataset]
            print 'files: ',datasetfiles[dataset]
datasetParser() 
