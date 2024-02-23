import tensorflow as tf


import uproot

import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
import sklearn.metrics




print(tf.__version__)

tf.keras.backend.clear_session()


signal_sample = "GluGlutoRadion_2L_M450_PreEE.root"
signal_file = uproot.open(signal_sample)
signal_tree = signal_file['Double_Tree']
signal_events = signal_tree.arrays()
signal_resolved2b_events = signal_events[(signal_events.Double_Res_2b == 1) & (signal_events.Double_Signal == 1) & (signal_events.ZMassCut == 1) & (signal_events.InvarMassCut == 1)]
signal_events_filtered = signal_resolved2b_events


tt_sample = "TTto2L2Nu_PreEE.root"
tt_file = uproot.open(tt_sample)
tt_tree = tt_file['Double_Tree']
tt_events = tt_tree.arrays()
tt_resolved2b_events = tt_events[(tt_events.Double_Res_2b == 1) & (tt_events.Double_Signal == 1) & (tt_events.ZMassCut == 1) & (tt_events.InvarMassCut == 1)]
tt_events_filtered = tt_resolved2b_events


DY_sample = "DYto2L-2Jets_MLL-10to50_PreEE.root"
DY_file = uproot.open(DY_sample)
DY_tree = DY_file['Double_Tree']
DY_events = DY_tree.arrays()
DY_resolved2b_events = DY_events[(DY_events.Double_Res_2b == 1) & (DY_events.Double_Signal == 1) & (DY_events.ZMassCut == 1) & (DY_events.InvarMassCut == 1)]
DY_events_filtered = DY_resolved2b_events

ST_sample = "TbarWplusto2L2Nu_PreEE.root"
ST_file = uproot.open(ST_sample)
ST_tree = ST_file['Double_Tree']
ST_events = ST_tree.arrays()
ST_resolved2b_events = ST_events[(ST_events.Double_Res_2b == 1) & (ST_events.Double_Signal == 1) & (ST_events.ZMassCut == 1) & (ST_events.InvarMassCut == 1)]
ST_events_filtered = ST_resolved2b_events



print("After filtering for only Double_Res_2b, we have these events left")
print("Signal ", len(signal_events_filtered))
print("TT ", len(tt_events_filtered))
print("DY ", len(DY_events_filtered))
print("ST ", len(ST_events_filtered))
print("Starting the training and then will test")


#Lets try to use class weights? This allows us to have a weight per class to emphasize underrepresented data in the training
total_events = len(signal_events_filtered) + len(tt_events_filtered) + len(DY_events_filtered) + len(ST_events_filtered)
signal_classweight = 1.0/len(signal_events_filtered)
tt_classweight = 1.0/len(tt_events_filtered)
DY_classweight = 1.0/len(DY_events_filtered)
ST_classweight = 1.0/len(ST_events_filtered)
class_weight = {0: signal_classweight, 1: tt_classweight, 2: DY_classweight, 3: ST_classweight}
class_labels = ["Signal", "TT", "DY", "ST"]
print("Using classweights, weights are")
print(class_weight)
print(class_labels)
#Manuel has code fo better classweights, input plotting, and something else ask him he will send code

#Turn the labels into onehots, prepare the binarizer
label_binarizer = LabelBinarizer().fit([0,1,2,3])


#Put in a list of [ [px, py, pz, E, ...], [px, py, pz, E, ...], [px, py, pz, E, ...] ]
def create_nparray(events):
    array = np.array([
        events.lep0_px,
        events.lep0_py,
        events.lep0_pz,
        events.lep0_E,
        events.lep0_pdgId,
        events.lep0_charge,

        events.lep1_px,
        events.lep1_py,
        events.lep1_pz,
        events.lep1_E,
        events.lep1_pdgId,
        events.lep1_charge,

        events.ak4_jet0_px,
        events.ak4_jet0_py,
        events.ak4_jet0_pz,
        events.ak4_jet0_E,
        events.ak4_jet0_btagDeepFlavB,

        events.ak4_jet1_px,
        events.ak4_jet1_py,
        events.ak4_jet1_pz,
        events.ak4_jet1_E,
        events.ak4_jet1_btagDeepFlavB,

        events.ak4_jet2_px,
        events.ak4_jet2_py,
        events.ak4_jet2_pz,
        events.ak4_jet2_E,
        events.ak4_jet2_btagDeepFlavB,

        events.ak4_jet3_px,
        events.ak4_jet3_py,
        events.ak4_jet3_pz,
        events.ak4_jet3_E,
        events.ak4_jet3_btagDeepFlavB,

        events.met_px,
        events.met_py,
        events.met_pz,
        events.met_E,

        events.HT,

        events.ll_px,
        events.ll_py,
        events.ll_pz,
        events.ll_E,
        events.ll_mass,

        events.hWW_px,
        events.hWW_py,
        events.hWW_pz,
        events.hWW_E,
        events.hWW_mass,

        events.hbb_px,
        events.hbb_py,
        events.hbb_pz,
        events.hbb_E,
        events.hbb_mass,

        events.hh_px,
        events.hh_py,
        events.hh_pz,
        events.hh_E,
        events.hh_mass,

        events.n_fakeable_muons,
        events.n_fakeable_electrons,
        events.n_cleaned_ak4_jets,
        events.n_medium_btag_ak4_jets,

        #For now we must do dR by hand (not in tree)
        ((events.lep0_eta - events.lep1_eta)**2 + (events.lep0_phi - events.lep1_phi)**2)**(0.5),
        ((events.ak4_jet0_eta - events.ak4_jet1_eta)**2 + (events.ak4_jet0_phi - events.ak4_jet1_phi)**2)**(0.5)

    ])
    return array

"""
#Test simple inputs to see that resutls make sense (cannot classify)
def create_nparray(events):
    array = np.array([
        events.met_px,
        events.met_py,
        events.met_pz,
        events.met_E,
    ])
    return array
"""

signal_array = create_nparray(signal_events_filtered)
signal_array = signal_array.transpose()
signal_label = np.full(len(signal_array), 0)

tt_array = create_nparray(tt_events_filtered)
tt_array = tt_array.transpose()
tt_label = np.full(len(tt_array), 1)

DY_array = create_nparray(DY_events_filtered)
DY_array = DY_array.transpose()
DY_label = np.full(len(DY_array), 2)

ST_array = create_nparray(ST_events_filtered)
ST_array = ST_array.transpose()
ST_label = np.full(len(ST_array), 3)

#How many inputs?
input_len = len(signal_array[0])


#Prepare train and test samples, as well as random states
events = np.concatenate((signal_array, tt_array, DY_array, ST_array))
labels = np.concatenate((signal_label, tt_label, DY_label, ST_label))
events_train, events_test, labels_train, labels_test = train_test_split(events, labels, test_size=0.33, random_state=42)
labels_train = label_binarizer.transform(labels_train)
labels_test = label_binarizer.transform(labels_test)


#Create a layer to normalize the inputs
#Inputs for DNN must be normalized, set normalization funcs on the train set
norm_inputs = tf.keras.layers.Normalization(axis=-1)
norm_inputs.adapt(events_train)


events_train_norm = norm_inputs(events_train)
events_test_norm = norm_inputs(events_test)

print("Train before norm")
print(events_train)
print("Train after norm")
print(events_train_norm)



model = tf.keras.Sequential()

#Manuel recommends having the nodes look like a cone and continue to decrease
model.add(tf.keras.layers.Dense(128, input_dim=input_len))

model.add(tf.keras.layers.Dropout(0.3))

model.add(tf.keras.layers.Dense(64, activation="relu"))

model.add(tf.keras.layers.Dropout(0.3))

model.add(tf.keras.layers.Dense(32, activation="relu"))

model.add(tf.keras.layers.Dropout(0.3))

model.add(tf.keras.layers.Dense(16, activation="relu"))

model.add(tf.keras.layers.Dropout(0.3))

model.add(tf.keras.layers.Dense(8, activation="relu"))

model.add(tf.keras.layers.Dropout(0.3))

model.add(tf.keras.layers.Dense(4, activation="softmax"))

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.CategoricalCrossentropy(),
    metrics=[
        #'accuracy',
        tf.keras.metrics.CategoricalAccuracy(),
    ]
)





history = model.fit(events_train_norm, labels_train, validation_data=(events_test_norm, labels_test), epochs=200, class_weight=class_weight, batch_size=4096)

prob_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

prob_examples = prob_model.predict(events_test_norm)

#test_loss, test_acc = model.evaluate(test_set_norm, test_labels_onehot, verbose=2)




cm = sklearn.metrics.confusion_matrix(np.argmax(labels_test, axis=1), np.argmax(prob_examples, axis=1), normalize='true')
disp = sklearn.metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
disp.plot(cmap=plt.cm.Blues)
plt.savefig("conf_matrix.pdf")
plt.close()

#Lets look at training metrics, maybe just a plot of the history?
plt.plot(history.history['categorical_accuracy'])
plt.plot(history.history['val_categorical_accuracy'])
plt.grid(True)
plt.xlabel("Epoch")
plt.ylabel("Categorical Accuracy")
plt.ylim(0, 1.1)
plt.legend(['train', 'test'], loc='upper left')
plt.savefig("accuracy.pdf")
plt.close()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.grid(True)
plt.yscale("log")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend(['train', 'test'], loc='upper left')
plt.savefig("loss.pdf")
plt.close()



#Lets put the ROC curve for each class on a plot and calculate AUC
g, c_ax = plt.subplots(1,1, figsize = (12,8))
for (idx, c_label) in enumerate(class_labels):
    fpr, tpr, thresholds = sklearn.metrics.roc_curve(labels_test[:,idx].astype(int), prob_examples[:,idx])
    c_ax.plot(fpr, tpr, label = "{label} (AUC: {auc})".format(label = c_label, auc = sklearn.metrics.auc(fpr, tpr)))

c_ax.plot(fpr, fpr, "b-", label = "Random Guessing")

c_ax.legend()
c_ax.grid(True)
c_ax.set_xlabel("False Positive Rate")
c_ax.set_ylabel("True Positive Rate")
g.savefig("roc_curves.pdf")
