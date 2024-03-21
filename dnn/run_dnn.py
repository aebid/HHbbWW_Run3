from dnn import DNN_Model
import argparse

#Call example
#python3 run_dnn.py -i inputFile.root -o outputFile.root -m DNN_Model_Example/TT_ST_DY_signal -t 0 -p 1 -d 0

parser = argparse.ArgumentParser(description='HeavyMassEstimator for H->hh->bbWW')
parser.add_argument("-i", "--inputFile", dest="infile", type=str, default=[], help="input file name. [Default: [] ]")
parser.add_argument("-o", "--outputFile", dest="outfile", type=str, default="out.root", help="output file name. [Default: 'out.root']")
parser.add_argument("-m", "--model", dest="model", type=str, default="", help="model to use if loading [Default: '']")
parser.add_argument("-p", "--predict", dest="predict", type=int, default=1, help="do predict [Default: 1]")
parser.add_argument("-d", "--debug", dest="debug", type=int, default=0, help="debug [Default: 0]")
args, unknown = parser.parse_known_args()

fname = args.infile
outname = args.outfile
model = args.model
predict = args.predict
debug = args.debug

print("DNN on file: ", fname)
print("Will save as: ", outname)
print("Using model: ", model)
print("Args are = ", args)

print("Going to run DNN")

dnn = DNN_Model()

dnn.load_model(model)

dnn.predict(fname)

print("Finished HME!")
