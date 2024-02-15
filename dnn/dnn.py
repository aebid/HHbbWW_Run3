import tensorflow as tf


import uproot

import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)


model = tf.keras.Sequential()

#For resolved case, we start with Lep1/2 and Jet1/2 4 vectors, E,px,py,pz
#Since these will already be flattened (not 2D) we do not need a flatten layer


model.add(tf.keras.layers.Dense(2, activation="relu"))

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)


signal_sample = "GluGlutoRadion_2L_M450_PreEE.root"
background_sample = "TTto2L2Nu_PreEE.root"

signal_file = uproot.open(signal_sample)
background_file = uproot.open(background_sample)

signal_tree = signal_file['Double_Tree']
background_tree = background_file['Double_Tree']

signal_events = signal_tree.arrays()
background_events = background_tree.arrays()

signal_resolved2b_events = signal_events[signal_events.Double_Res_2b == 1]
background_resolved2b_events = background_events[background_events.Double_Res_2b == 1]


signal_events_filtered = signal_resolved2b_events
background_events_filtered = background_resolved2b_events

print("After filtering for only Double_Res_2b, we have these events left")
print("Signal ", len(signal_events_filtered))
print("Background ", len(background_events_filtered))
print("Starting the training and then will test")


#Put in a list of [ [px, py, pz, E, ...], [px, py, pz, E, ...], [px, py, pz, E, ...] ]
signal_array = np.array([
    signal_events_filtered.lep0_px,
    signal_events_filtered.lep0_py,
    signal_events_filtered.lep0_pz,
    signal_events_filtered.lep0_E,

    signal_events_filtered.lep1_px,
    signal_events_filtered.lep1_py,
    signal_events_filtered.lep1_pz,
    signal_events_filtered.lep1_E,

    signal_events_filtered.ak4_jet0_px,
    signal_events_filtered.ak4_jet0_py,
    signal_events_filtered.ak4_jet0_pz,
    signal_events_filtered.ak4_jet0_E,

    signal_events_filtered.ak4_jet1_px,
    signal_events_filtered.ak4_jet1_py,
    signal_events_filtered.ak4_jet1_pz,
    signal_events_filtered.ak4_jet1_E
])
signal_array = signal_array.transpose()
signal_label = np.full(len(signal_array), 0)


background_array = np.array([
    background_events_filtered.lep0_px,
    background_events_filtered.lep0_py,
    background_events_filtered.lep0_pz,
    background_events_filtered.lep0_E,

    background_events_filtered.lep1_px,
    background_events_filtered.lep1_py,
    background_events_filtered.lep1_pz,
    background_events_filtered.lep1_E,

    background_events_filtered.ak4_jet0_px,
    background_events_filtered.ak4_jet0_py,
    background_events_filtered.ak4_jet0_pz,
    background_events_filtered.ak4_jet0_E,

    background_events_filtered.ak4_jet1_px,
    background_events_filtered.ak4_jet1_py,
    background_events_filtered.ak4_jet1_pz,
    background_events_filtered.ak4_jet1_E,

])
background_array = background_array.transpose()
background_label = np.full(len(background_array), 1)


#Loaded all of the events, now we separate what we want to train on and what we want to test on
#Will use 90% of events for training, 10% for testing
PercOfTrain = 0.9
nSignalTrain = int(PercOfTrain*len(signal_events_filtered))
nBackgroundTrain = int(PercOfTrain*len(background_events_filtered))

train_signal_events = signal_array[:][:nSignalTrain]
train_signal_labels = signal_label[:][:nSignalTrain]

train_background_events = background_array[:][:nBackgroundTrain]
train_background_labels = background_label[:][:nBackgroundTrain]


test_signal_events = signal_array[:][nSignalTrain:]
test_signal_labels = signal_label[:][nSignalTrain:]

test_background_events = background_array[:][nBackgroundTrain:]
test_background_labels = background_label[:][nBackgroundTrain:]



train_set = np.concatenate((train_signal_events, train_background_events))
train_labels = np.concatenate((train_signal_labels, train_background_labels))

#Shuffle the train set and labels in unison
shuffle_index = np.random.permutation(len(train_signal_events)+len(train_background_events))

train_set = train_set[shuffle_index]
train_labels = train_labels[shuffle_index]



test_set = np.concatenate((test_signal_events, test_background_events))
test_labels = np.concatenate((test_signal_labels, test_background_labels))

#Shuffle the train set and labels in unison
shuffle_index = np.random.permutation(len(test_signal_events)+len(test_background_events))

test_set = test_set[shuffle_index]
test_labels = test_labels[shuffle_index]


model.fit(train_set, train_labels, epochs=10)


test_loss, test_acc = model.evaluate(test_set, test_labels, verbose=2)
