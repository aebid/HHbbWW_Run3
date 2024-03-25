from dnn import DNN_Model
import argparse

#Call example
#python3 run_dnn.py -i inputFile.root -o outputFile.root -m DNN_Model_Example/TT_ST_DY_signal -p 1 -d 0

parser = argparse.ArgumentParser(description='HeavyMassEstimator for H->hh->bbWW')
parser.add_argument("-i", "--inputFile", dest="infile", type=str, default=[], help="input file name. [Default: [] ]")
parser.add_argument("-o", "--outputFile", dest="outfile", type=str, default="out.root", help="output file name. [Default: 'out.root']")
parser.add_argument("-m", "--model", dest="model", type=str, default="DNN_Model_Example/TT_ST_DY_signal", help="model to use if loading [Default: '']")
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

prediction = dnn.predict(fname)

print(prediction)

print("Finished DNN Prediction!")


validation_plots = True


if validation_plots:
    import matplotlib.pyplot as plt

    predict_signal300 = dnn.predict("input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300_PreEE.root")
    predict_signal450 = dnn.predict("input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_PreEE.root")
    predict_signal700 = dnn.predict("input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700_PreEE.root")

    predict_TT = dnn.predict("input_files/with_hme/TTto2L2Nu/TTto2L2Nu_PreEE.root")

    predict_DY_M50 = dnn.predict("input_files/with_hme/DYJetsToLL_M-50/DYJetsToLL_M-50_PreEE.root")
    predict_DY_M10to50 = dnn.predict("input_files/with_hme/DYto2L-2Jets_MLL-10to50/DYto2L-2Jets_MLL-10to50_PreEE.root")

    predict_TbarWplus = dnn.predict("input_files/with_hme/TbarWplusto2L2Nu/TbarWplusto2L2Nu_PreEE.root")
    predict_TWminus = dnn.predict("input_files/with_hme/TWminusto2L2Nu/TWminusto2L2Nu_PreEE.root")

    plotrange = (0.0, 1.0)
    plotbins = 100

    plt.hist(predict_signal300[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='/', label='Signal M300', alpha=0.5)
    plt.hist(predict_signal450[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='/', label='Signal M450', alpha=0.5)
    plt.hist(predict_signal700[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='/', label='Signal M700', alpha=0.5)

    plt.hist(predict_TT[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='|', label='TT', alpha=0.5)

    plt.hist(predict_DY_M50[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='+', label='DY M50', alpha=0.5)
    plt.hist(predict_DY_M10to50[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='+', label='DY M10to50', alpha=0.5)

    plt.hist(predict_TbarWplus[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='x', label='Tbar Wplus', alpha=0.5)
    plt.hist(predict_TWminus[:,0], bins=plotbins, range=plotrange, density=True, histtype='step', hatch='x', label='T Wminus', alpha=0.5)

    plt.legend(loc='upper right')

    plt.savefig("dnn_values.pdf")


    #plt.show()



    import numpy as np

    x = np.linspace(0.0, 1.0, 101)

    sig_m300_acc = []
    sig_m450_acc = []
    sig_m700_acc = []

    TT_acc = []

    DYm50_acc = []
    DYm10to50_acc = []

    TbarWplus_acc = []
    TWminus_acc = []

    for cut in x:
        sig_m300_acc.append(np.sum(predict_signal300[:,0] > cut)/len(predict_signal300))
        sig_m450_acc.append(np.sum(predict_signal450[:,0] > cut)/len(predict_signal450))
        sig_m700_acc.append(np.sum(predict_signal700[:,0] > cut)/len(predict_signal700))
        TT_acc.append(np.sum(predict_TT[:,0] > cut)/len(predict_TT))
        DYm50_acc.append(np.sum(predict_DY_M50[:,0] > cut)/len(predict_DY_M50))
        DYm10to50_acc.append(np.sum(predict_DY_M10to50[:,0] > cut)/len(predict_DY_M10to50))
        TbarWplus_acc.append(np.sum(predict_TbarWplus[:,0] > cut)/len(predict_TbarWplus))
        TWminus_acc.append(np.sum(predict_TWminus[:,0] > cut)/len(predict_TWminus))

        #print("Acceptances at SignalDNN cut ", cut)
        #print("Signal m300 ", np.sum(predict_signal300[:,0] > cut)/len(predict_signal300))
        #print("Signal m450 ", np.sum(predict_signal450[:,0] > cut)/len(predict_signal450))
        #print("Signal m700 ", np.sum(predict_signal700[:,0] > cut)/len(predict_signal700))
        #print("TT ", np.sum(predict_TT[:,0] > cut)/len(predict_TT))
        #print("DY M>50 ", np.sum(predict_DY_M50[:,0] > cut)/len(predict_DY_M50))
        #print("DY 10<M<50 ", np.sum(predict_DY_M10to50[:,0] > cut)/len(predict_DY_M10to50))
        #print("TbarWplus ", np.sum(predict_TbarWplus[:,0] > cut)/len(predict_TbarWplus))
        #print("TWminus ", np.sum(predict_TWminus[:,0] > cut)/len(predict_TWminus))


    plt.clf()

    plt.plot(x, sig_m300_acc, label='Signal m300 Acceptance')
    plt.plot(x, sig_m450_acc, label='Signal m450 Acceptance')
    plt.plot(x, sig_m700_acc, label='Signal m700 Acceptance')

    plt.plot(x, TT_acc, label='TT Acceptance')

    plt.plot(x, DYm50_acc, label='DY M>50 Acceptance')
    plt.plot(x, DYm10to50_acc, label='DY 10<M<50 Acceptance')

    plt.plot(x, TbarWplus_acc, label='TbarWplus Acceptance')
    plt.plot(x, TWminus_acc, label='TWminus Acceptance')

    plt.legend(loc='upper right')

    plt.savefig("dnn_acceptance.pdf")


    #plt.show()
