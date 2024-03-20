import tensorflow as tf
import os
import uproot
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
import sklearn.metrics
from keras.wrappers.scikit_learn import KerasClassifier, KerasRegressor
import datetime




curr_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
model_folder = "DNN_Model_"+curr_time+"/"
os.makedirs(model_folder, exist_ok = True)

print("Starting DNN training process")
print("Current model will be saved in "+model_folder)
print("Saving this file ", __file__, " into folder for future reference")
os.system("cp {file} {folder}".format(file = __file__, folder = model_folder))


print("Input comments about this training")
comments_file = model_folder+"comments.txt"
with open(comments_file, 'w', encoding='utf-8') as my_file:
    my_file.write(input('Comments: '))

print(tf.__version__)

tf.keras.backend.clear_session()

signal300_sample = "input_files/GluGlutoRadion_2L_M300_PreEE.root"
signal300_file = uproot.open(signal300_sample)
signal300_tree = signal300_file['Double_Tree']
signal300_events = signal300_tree.arrays()
signal300_resolved2b_events = signal300_events[(signal300_events.Double_Res_2b == 1) & (signal300_events.Double_Signal == 1) & (signal300_events.ZMassCut == 1) & (signal300_events.InvarMassCut == 1)]
signal300_events_filtered = signal300_resolved2b_events

signal450_sample = "input_files/GluGlutoRadion_2L_M450_PreEE.root"
signal450_file = uproot.open(signal450_sample)
signal450_tree = signal450_file['Double_Tree']
signal450_events = signal450_tree.arrays()
signal450_resolved2b_events = signal450_events[(signal450_events.Double_Res_2b == 1) & (signal450_events.Double_Signal == 1) & (signal450_events.ZMassCut == 1) & (signal450_events.InvarMassCut == 1)]
signal450_events_filtered = signal450_resolved2b_events

signal700_sample = "input_files/GluGlutoRadion_2L_M450_PreEE.root"
signal700_file = uproot.open(signal700_sample)
signal700_tree = signal700_file['Double_Tree']
signal700_events = signal700_tree.arrays()
signal700_resolved2b_events = signal700_events[(signal700_events.Double_Res_2b == 1) & (signal700_events.Double_Signal == 1) & (signal700_events.ZMassCut == 1) & (signal700_events.InvarMassCut == 1)]
signal700_events_filtered = signal700_resolved2b_events

tt_sample = "input_files/TTto2L2Nu_PreEE.root"
tt_file = uproot.open(tt_sample)
tt_tree = tt_file['Double_Tree']
tt_events = tt_tree.arrays()
tt_resolved2b_events = tt_events[(tt_events.Double_Res_2b == 1) & (tt_events.Double_Signal == 1) & (tt_events.ZMassCut == 1) & (tt_events.InvarMassCut == 1)]
tt_events_filtered = tt_resolved2b_events


DY_sample = "input_files/DYto2L-2Jets_MLL-10to50_PreEE.root"
DY_file = uproot.open(DY_sample)
DY_tree = DY_file['Double_Tree']
DY_events = DY_tree.arrays()
DY_resolved2b_events = DY_events[(DY_events.Double_Res_2b == 1) & (DY_events.Double_Signal == 1) & (DY_events.ZMassCut == 1) & (DY_events.InvarMassCut == 1)]
DY_events_filtered = DY_resolved2b_events

ST_sample = "input_files/TbarWplusto2L2Nu_PreEE.root"
ST_file = uproot.open(ST_sample)
ST_tree = ST_file['Double_Tree']
ST_events = ST_tree.arrays()
ST_resolved2b_events = ST_events[(ST_events.Double_Res_2b == 1) & (ST_events.Double_Signal == 1) & (ST_events.ZMassCut == 1) & (ST_events.InvarMassCut == 1)]
ST_events_filtered = ST_resolved2b_events



print("After filtering for only Double_Res_2b, we have these events left")
print("Signal ", len(signal300_events_filtered) + len(signal450_events_filtered) + len(signal700_events_filtered))
print("TT ", len(tt_events_filtered))
print("DY ", len(DY_events_filtered))
print("ST ", len(ST_events_filtered))
print("Starting the training and then will test")


#Lets try to use class weights? This allows us to have a weight per class to emphasize underrepresented data in the training
total_events = len(signal300_events_filtered) + len(signal450_events_filtered) + len(signal700_events_filtered) + len(tt_events_filtered) + len(DY_events_filtered) + len(ST_events_filtered)
signal_classweight = 1.0/(len(signal300_events_filtered) + len(signal450_events_filtered) + len(signal700_events_filtered))
tt_classweight = 1.0/len(tt_events_filtered)
DY_classweight = 1.0/len(DY_events_filtered)
ST_classweight = 1.0/len(ST_events_filtered)
class_weight = {0: signal_classweight, 1: tt_classweight, 2: DY_classweight, 3: ST_classweight}

class_labels = ["Signal", "TT", "DY", "ST"]
print("Using classweights, weights are")
print(class_weight)
print(class_labels)
#Manuel has code for better classweights, input plotting, and something else ask him he will send code

#Turn the labels into onehots, prepare the binarizer
label_binarizer = LabelBinarizer().fit([0,1,2,3])


input_labels = [
    "Lep0 px", "Lep0 py", "Lep0 pz", "Lep0 E", "Lep0 pdgId", "Lep0 charge",
    "Lep1 px", "Lep1 py", "Lep1 pz", "Lep1 E", "Lep1 pdgId", "Lep1 charge",
    "Ak4 Jet0 px", "Ak4 Jet0 py", "Ak4 Jet0 pz", "Ak4 Jet0 E", "Ak4 Jet0 btagDeepFlavB",
    "Ak4 Jet1 px", "Ak4 Jet1 py", "Ak4 Jet1 pz", "Ak4 Jet1 E", "Ak4 Jet1 btagDeepFlavB",
    "Ak4 Jet2 px", "Ak4 Jet2 py", "Ak4 Jet2 pz", "Ak4 Jet2 E", "Ak4 Jet2 btagDeepFlavB",
    "Ak4 Jet3 px", "Ak4 Jet3 py", "Ak4 Jet3 pz", "Ak4 Jet3 E", "Ak4 Jet3 btagDeepFlavB",
    "MET px", "MET py", "MET pz", "MET E",
    "HT",
    "ll px", "ll py", "ll pz", "ll E", "ll mass",
    "hWW px", "hWW py", "hWW pz", "hWW E", "hWW mass",
    "hbb px", "hbb py", "hbb pz", "hbb E", "hbb mass",
    "hh px", "hh py", "hh pz", "hh E", "hh mass",
    "n Fakeable Muons",
    "n Fakeable Electrons",
    "n Cleaned Ak4 Jets",
    "n Medium B Ak4 Jets",
    "Lep0 Lep1 dR",
    "Jet0 Jet1 dR",
    "HME",
    "param"
]

def create_nparray(events, param=[300,700]):
    #param input is the parametric DNN hh mass
    #for signal, we give true mass, for background we give random
    #we will train for mass 300, 450, and 700 initially, so for now we give random [300, 700]
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
        ((events.ak4_jet0_eta - events.ak4_jet1_eta)**2 + (events.ak4_jet0_phi - events.ak4_jet1_phi)**2)**(0.5),

        events.HME,

        np.random.uniform(param[0], param[1], len(events))

    ])
    return array



signal300_array = create_nparray(signal300_events_filtered, [300, 300])
signal300_array = signal300_array.transpose()
signal300_label = np.full(len(signal300_array), 0)
signal300_sampleweights = np.full(len(signal300_array), signal_classweight)

signal450_array = create_nparray(signal450_events_filtered, [450, 450])
signal450_array = signal450_array.transpose()
signal450_label = np.full(len(signal450_array), 0)
signal450_sampleweights = np.full(len(signal450_array), signal_classweight)

signal700_array = create_nparray(signal300_events_filtered, [700, 700])
signal700_array = signal700_array.transpose()
signal700_label = np.full(len(signal700_array), 0)
signal700_sampleweights = np.full(len(signal700_array), signal_classweight)

tt_array = create_nparray(tt_events_filtered, [300, 700])
tt_array = tt_array.transpose()
tt_label = np.full(len(tt_array), 1)
tt_sampleweights = np.full(len(tt_array), tt_classweight)

DY_array = create_nparray(DY_events_filtered, [300, 700])
DY_array = DY_array.transpose()
DY_label = np.full(len(DY_array), 2)
DY_sampleweights = np.full(len(DY_array), DY_classweight)

ST_array = create_nparray(ST_events_filtered, [300, 700])
ST_array = ST_array.transpose()
ST_label = np.full(len(ST_array), 3)
ST_sampleweights = np.full(len(ST_array), ST_classweight)

#How many inputs?
input_len = len(signal300_array[0])


#Prepare train and test samples, as well as random states
events = np.concatenate((signal300_array, signal450_array, signal700_array, tt_array, DY_array, ST_array))
labels = np.concatenate((signal300_label, signal450_label, signal700_label, tt_label, DY_label, ST_label))
sampleweights = np.concatenate((signal300_sampleweights, signal450_sampleweights, signal700_sampleweights, tt_sampleweights, DY_sampleweights, ST_sampleweights))

events_train, events_test, labels_train, labels_test, sampleweights_train, sampleweights_test  = train_test_split(events, labels, sampleweights, test_size=0.33, random_state=42)
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

# This function keeps the initial learning rate for the first ten epochs
# and decreases it exponentially after that.
def scheduler(epoch, lr):
  if epoch < 10:
    return lr
  else:
    return lr * tf.math.exp(-0.1)



def base_model():
    model = tf.keras.Sequential()

    #Manuel recommends having the nodes look like a cone and continue to decrease
    #Manuel says relu is dumb for our normalization, testing tanh on first layer
    model.add(tf.keras.layers.Dense(128, activation="tanh", input_dim=input_len))

    model.add(tf.keras.layers.Dense(256, activation="relu"))

    model.add(tf.keras.layers.Dropout(0.3))

    model.add(tf.keras.layers.Dense(128, activation="relu"))

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

    #Testing Softmax layer here
    model.add(tf.keras.layers.Softmax())

    model.compile(
        ### Adam optimizer, with initial lr = 0.001
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        #loss=tf.keras.losses.CategoricalHinge(),
        loss=tf.keras.losses.CategoricalCrossentropy(),
        weighted_metrics=[
            #'accuracy',
            tf.keras.metrics.CategoricalAccuracy(),
            tf.keras.metrics.CategoricalCrossentropy(),
            tf.keras.metrics.CategoricalHinge(),
        ]
    )
    return model

model = base_model()

model.summary()


def fit_model(model, model_NamePath):
    history = model.fit(
                        events_train_norm,
                        labels_train,
                        sample_weight = sampleweights_train,
                        validation_data=(
                            events_test_norm,
                            labels_test,
                            sampleweights_test
                            ),
                        epochs=100,
                        #class_weight=class_weight,
                        batch_size=2048,
                        # Callback: set of functions to be applied at given stages of the training procedure
                        callbacks=[
                            #tf.keras.callbacks.ModelCheckpoint(model_NamePath, monitor='val_loss', verbose=False, save_best_only=True),
                            tf.keras.callbacks.LearningRateScheduler(scheduler), # How this is different from 'conf.optimiz' ?
                            tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=10) # Stop once you stop improving the val_loss
                            ]
                        )
    return history




def make_performance_plots(model, test_events, test_labels, plot_prefix=""):
    predict_set = model.predict(test_events)

    cm = sklearn.metrics.confusion_matrix(np.argmax(test_labels, axis=1), np.argmax(predict_set, axis=1), normalize='true')
    disp = sklearn.metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
    disp.plot(cmap=plt.cm.Blues)
    plt.savefig(model_folder+plot_prefix+"conf_matrix.pdf")
    plt.close()

    #Lets put the ROC curve for each class on a plot and calculate AUC
    g, c_ax = plt.subplots(1,1, figsize = (8,6))
    for (idx, c_label) in enumerate(class_labels):
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(test_labels[:,idx].astype(int), predict_set[:,idx])
        c_ax.plot(fpr, tpr, label = "{label} (AUC: {auc})".format(label = c_label, auc = sklearn.metrics.auc(fpr, tpr)))

    c_ax.plot(fpr, fpr, "b-", label = "Random Guessing")

    c_ax.legend()
    c_ax.grid(True)
    c_ax.set_xlabel("False Positive Rate")
    c_ax.set_ylabel("True Positive Rate")
    g.savefig(model_folder+plot_prefix+"roc_curves.pdf")
    g.clf()
    plt.close()
    #g.close()


def make_history_plots(history, plot_prefix=""):
    #Lets look at training metrics, maybe just a plot of the history?
    plt.plot(history.history['categorical_accuracy'])
    plt.plot(history.history['val_categorical_accuracy'])
    plt.grid(True)
    plt.xlabel("Epoch")
    plt.ylabel("Categorical Accuracy")
    plt.ylim(0, 1.1)
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(model_folder+plot_prefix+"accuracy.pdf")
    plt.clf()
    plt.close()

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.grid(True)
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(model_folder+plot_prefix+"loss.pdf")
    plt.clf()
    plt.close()




def do_feature_imp(sk_model):
    #Feature importance requires sklearn model
    import eli5
    from eli5.sklearn import PermutationImportance

    perm = PermutationImportance(sk_model, n_iter=10, random_state=1).fit(events_train_norm, labels_train)
    feat_import_dict = eli5.format_as_dict(eli5.explain_weights(perm, top=100))

    feat_import = feat_import_dict['feature_importances']['importances']
    print(eli5.format_as_text(eli5.explain_weights(perm, top=100, feature_names=input_labels)))
    return perm




save_path = "./"+model_folder+"/TT_ST_DY_signalM450"
history = fit_model(model, save_path)
model.save(save_path)
make_performance_plots(model, events_test_norm, labels_test)
make_history_plots(history)


"""
save_path = "./"+model_folder+"/SK_TT_ST_DY_signalM450"
sk_model = KerasRegressor(build_fn=base_model)
sk_history = fit_model(sk_model, save_path)
make_performance_plots(sk_model, events_test_norm, labels_test, "sk_")
make_history_plots(sk_history, "sk_")
perm = do_feature_imp(sk_model)
"""
