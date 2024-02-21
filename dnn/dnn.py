import tensorflow as tf


import uproot

import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)


signal_sample = "GluGlutoRadion_2L_M450_PreEE.root"
signal_file = uproot.open(signal_sample)
signal_tree = signal_file['Double_Tree']
signal_events = signal_tree.arrays()
signal_resolved2b_events = signal_events[signal_events.Double_Res_2b == 1]
signal_events_filtered = signal_resolved2b_events


tt_sample = "TTto2L2Nu_PreEE.root"
tt_file = uproot.open(tt_sample)
tt_tree = tt_file['Double_Tree']
tt_events = tt_tree.arrays()
tt_resolved2b_events = tt_events[tt_events.Double_Res_2b == 1]
tt_events_filtered = tt_resolved2b_events


DY_sample = "DYto2L-2Jets_MLL-10to50_PreEE.root"
DY_file = uproot.open(DY_sample)
DY_tree = DY_file['Double_Tree']
DY_events = DY_tree.arrays()
DY_resolved2b_events = DY_events[DY_events.Double_Res_2b == 1]
DY_events_filtered = DY_resolved2b_events




print("After filtering for only Double_Res_2b, we have these events left")
print("Signal ", len(signal_events_filtered))
print("TT ", len(tt_events_filtered))
print("DY ", len(DY_events_filtered))
print("Starting the training and then will test")


#For now, we have too much TT events, lets only use 1000 events
#nEvtMax = 5000
#signal_events_filtered = signal_events_filtered[:min(nEvtMax, len(signal_events_filtered))]
#tt_events_filtered = tt_events_filtered[:min(nEvtMax, len(tt_events_filtered))]
#DY_events_filtered = DY_events_filtered[:min(nEvtMax, len(DY_events_filtered))]



#Lets try to use class weights? This allows us to have a weight per class to emphasize underrepresented data in the training
total_events = len(signal_events_filtered) + len(tt_events_filtered) + len(DY_events_filtered)
signal_classweight = 1.0
tt_classweight = len(signal_events_filtered)/len(tt_events_filtered)
DY_classweight = len(signal_events_filtered)/len(DY_events_filtered)
class_weight = {0: signal_classweight, 1: tt_classweight, 2: DY_classweight}
print("Using classweights, weights are")
print(class_weight)

#Turn the labels into onehots, prepare the binarizer
from sklearn.preprocessing import LabelBinarizer
label_binarizer = LabelBinarizer().fit([0,1,2])


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

        events.met_px,
        events.met_py,
        events.met_pz,
        events.met_E,

    ])
    return array

signal_array = create_nparray(signal_events_filtered)
signal_array = signal_array.transpose()
signal_label = np.full(len(signal_array), 0)

tt_array = create_nparray(tt_events_filtered)
tt_array = tt_array.transpose()
tt_label = np.full(len(tt_array), 1)

DY_array = create_nparray(DY_events_filtered)
DY_array = DY_array.transpose()
DY_label = np.full(len(DY_array), 2)




#Loaded all of the events, now we separate what we want to train on and what we want to test on
#Will use 90% of events for training, 10% for testing
PercOfTrain = 0.9
nSignalTrain = int(PercOfTrain*len(signal_events_filtered))
nttTrain = int(PercOfTrain*len(tt_events_filtered))
nDYTrain = int(PercOfTrain*len(DY_events_filtered))


train_signal_events = signal_array[:][:nSignalTrain]
train_signal_labels = signal_label[:][:nSignalTrain]

test_signal_events = signal_array[:][nSignalTrain:]
test_signal_labels = signal_label[:][nSignalTrain:]


train_tt_events = tt_array[:][:nttTrain]
train_tt_labels = tt_label[:][:nttTrain]

test_tt_events = tt_array[:][nttTrain:]
test_tt_labels = tt_label[:][nttTrain:]


train_DY_events = DY_array[:][:nDYTrain]
train_DY_labels = DY_label[:][:nDYTrain]

test_DY_events = DY_array[:][nDYTrain:]
test_DY_labels = DY_label[:][nDYTrain:]




train_set = np.concatenate((train_signal_events, train_tt_events, train_DY_events))
train_labels = np.concatenate((train_signal_labels, train_tt_labels, train_DY_labels))



#Shuffle the train set and labels in unison
shuffle_index = np.random.permutation(len(train_signal_events)+len(train_tt_events)+len(train_DY_events))

train_set = train_set[shuffle_index]
train_labels = train_labels[shuffle_index]
train_labels_onehot = label_binarizer.transform(train_labels)



test_set = np.concatenate((test_signal_events, test_tt_events, test_DY_events))
test_labels = np.concatenate((test_signal_labels, test_tt_labels, test_DY_labels))

#Shuffle the train set and labels in unison
shuffle_index = np.random.permutation(len(test_signal_events)+len(test_tt_events)+len(test_DY_events))

test_set = test_set[shuffle_index]
test_labels = test_labels[shuffle_index]
test_labels_onehot = label_binarizer.transform(test_labels)


#Create a layer to normalize the inputs
#Inputs for DNN must be normalized, set normalization funcs on the train set
norm_inputs = tf.keras.layers.Normalization(axis=-1)
norm_inputs.adapt(train_set)

train_set_norm = norm_inputs(train_set)
test_set_norm = norm_inputs(test_set)



model = tf.keras.Sequential()

#For resolved case, we start with Lep1/2 and Jet1/2 4 vectors, E,px,py,pz
#Since these will already be flattened (not 2D) we do not need a flatten layer

model.add(tf.keras.layers.Dense(26, activation="relu"))

model.add(tf.keras.layers.Dense(64, activation="relu"))

#model.add(tf.keras.layers.Dropout(0.5))

model.add(tf.keras.layers.Dense(64, activation="relu"))

model.add(tf.keras.layers.Dense(3, activation="softmax"))

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.CategoricalCrossentropy(),
    metrics=[
        #'accuracy',
        tf.keras.metrics.CategoricalAccuracy(),
    ]
)





#model.fit(train_set, train_labels, epochs=10, class_weight=class_weight)
model.fit(train_set_norm, train_labels_onehot, epochs=10, class_weight=class_weight)

prob_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])

prob_examples = prob_model.predict(test_set_norm)

#test_loss, test_acc = model.evaluate(test_set, test_labels, verbose=2)
test_loss, test_acc = model.evaluate(test_set_norm, test_labels_onehot, verbose=2)





import sklearn.metrics

cm = sklearn.metrics.confusion_matrix(np.argmax(test_labels_onehot, axis=1), np.argmax(prob_examples, axis=1), normalize='true')
disp = sklearn.metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Signal", "TT", "DY"])
disp.plot(cmap=plt.cm.Blues)
plt.show()
