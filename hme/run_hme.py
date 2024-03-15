from HeavyMassEstimator import HeavyMassEstimator
import argparse

parser = argparse.ArgumentParser(description='HeavyMassEstimator for H->hh->bbWW')
parser.add_argument("-i", "--inputFile", dest="infile", type=str, default=[], help="input file name. [Default: [] ]")
parser.add_argument("-o", "--outputFile", dest="outfile", type=str, default="out.root", help="output file name. [Default: 'out.root']")
parser.add_argument("-it", "--iterations", dest="iterations", type=int, default=10000, help="number of iterations [Default: 10000]")
parser.add_argument("-SL", "--singlelepton", dest="doSL", type=bool, default=1, help="do single lepton HME [Default: 1]")
parser.add_argument("-DL", "--doublelepton", dest="doDL", type=bool, default=1, help="do double lepton HME [Default: 1]")
parser.add_argument("-d", "--debug", dest="debug", type=bool, default=0, help="debug [Default: 0]")
args, unknown = parser.parse_known_args()

fname = args.infile
outname = args.outfile
iterations = args.iterations
doSL = args.doSL
doDL = args.doDL
debug = args.debug


print("HME on file: ", fname)
print("Will save as: ", outname)
print("Args are = ", args)

hme = HeavyMassEstimator(fname, outname, iterations, doSL, doDL, debug)

hme.run_HME()

print("Finished HME!")
