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


class DNN_Model():
    def __init__(self, quiet=0, debug=0):
        self.quiet = quiet
        self.debug = debug
        self.curr_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        self.model_folder = "DNN_Model_"+self.curr_time+"/"

        self.input_labels = [
            "Lep0 px", "Lep0 py", "Lep0 pz", "Lep0 E", "Lep0 pdgId", "Lep0 charge",
            "Lep1 px", "Lep1 py", "Lep1 pz", "Lep1 E", "Lep1 pdgId", "Lep1 charge",
            "Ak4 Jet0 px", "Ak4 Jet0 py", "Ak4 Jet0 pz", "Ak4 Jet0 E", "Ak4 Jet0 btagDeepFlavB",
            "Ak4 Jet1 px", "Ak4 Jet1 py", "Ak4 Jet1 pz", "Ak4 Jet1 E", "Ak4 Jet1 btagDeepFlavB",
            "Ak4 Jet2 px", "Ak4 Jet2 py", "Ak4 Jet2 pz", "Ak4 Jet2 E", "Ak4 Jet2 btagDeepFlavB",
            "Ak4 Jet3 px", "Ak4 Jet3 py", "Ak4 Jet3 pz", "Ak4 Jet3 E", "Ak4 Jet3 btagDeepFlavB",
            "AK8 Jet0 px", "Ak8 Jet0 py", "Ak8 Jet0 pz", "Ak8 Jet0 E",
            "Ak8 Jet0 Tau1", "Ak8 Jet0 Tau2", "Ak8 Jet0 Tau3", "Ak8 Jet0 Tau4",
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

        self.class_dict = {
            "0": {
                "classname": "Signal",
                "filelist": [],
                "paramlist": [],
                "eventslist": [],
                "classweight": 0.0,
                "arrays": [],
                "labels": [],
                "weights": [],
            },
            "1": {
                "classname": "TT",
                "filelist": [],
                "paramlist": [],
                "eventslist": [],
                "classweight": 0.0,
                "arrays": [],
                "labels": [],
                "weights": [],
            },
            "2": {
                "classname": "DY",
                "filelist": [],
                "paramlist": [],
                "eventslist": [],
                "classweight": 0.0,
                "arrays": [],
                "labels": [],
                "weights": [],
            },
            "3": {
                "classname": "ST",
                "filelist": [],
                "paramlist": [],
                "eventslist": [],
                "classweight": 0.0,
                "arrays": [],
                "labels": [],
                "weights": [],
            },
        }

        self.class_dict_finalized = False

        self.full_array = []
        self.full_label = []
        self.full_weight = []

        self.model = []

    def add_to_class_dict(self, classification, filename, param=[300,700]):
        classification = str(classification)
        self.class_dict[classification]['filelist'].append(filename)
        self.class_dict[classification]['paramlist'].append(param)

    def finalize_class_dict(self):
        array_list = []
        label_list = []
        weight_list = []
        for classification in self.class_dict.keys():
            nEvtsClass = 0.0
            for i, filename in enumerate(self.class_dict[classification]['filelist']):
                events = self.prepare_events(filename)#[:1000] #Experimental! Having a problem with overfitting
                array = (self.create_nparray(events, self.class_dict[classification]['paramlist'][i])).transpose()
                nEvtsClass += len(events)
                self.class_dict[classification]['eventslist'].append(events)
                self.class_dict[classification]['arrays'].append(array)
                self.class_dict[classification]['labels'].append(np.full(len(array), int(classification)))

                array_list.append(array)
                label_list.append(np.full(len(array), int(classification)))

            self.class_dict[classification]['classweight'] = 1.0/nEvtsClass
            for i in range(len(self.class_dict[classification]['filelist'])):
                self.class_dict[classification]['weights'].append(np.full(len(self.class_dict[classification]['arrays'][i]), self.class_dict[classification]['classweight']))

                weight_list.append(np.full(len(self.class_dict[classification]['arrays'][i]), self.class_dict[classification]['classweight']))

        self.full_array = np.concatenate(array_list)
        self.full_label = np.concatenate(label_list)
        self.full_weight = np.concatenate(weight_list)

        self.class_dict_finalized = True




    def create_nparray(self, events, param=[300,700]):
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

            events.ak8_jet0_px,
            events.ak8_jet0_py,
            events.ak8_jet0_pz,
            events.ak8_jet0_E,
            events.ak8_jet0_tau1,
            events.ak8_jet0_tau2,
            events.ak8_jet0_tau3,
            events.ak8_jet0_tau4,

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


    def prepare_events(self, filename):
        f = uproot.open(filename)
        t = f['Double_HME_Tree']
        events = t.arrays()
        #mask = (events.Double_Res_2b == 1) & (events.Double_Signal == 1) & (events.HME > 0)
        mask = (events.Double_Signal == 1) & (events.HME > 0)
        events_filtered = events[mask]
        return events_filtered

    def train_model(self):
        if not self.class_dict_finalized:
            print("YOU DID NOT FINALIZE THE CLASS DICT!")
            return

        print("Starting DNN training process")
        print("Current model will be saved in "+self.model_folder)
        print("Saving this file ", __file__, " into folder for future reference")
        os.makedirs(self.model_folder, exist_ok = True)
        os.system("cp {file} {folder}".format(file = __file__, folder = self.model_folder))


        if not self.quiet:
            print("Input comments about this training")
            comments_file = self.model_folder+"comments.txt"
            with open(comments_file, 'w', encoding='utf-8') as my_file:
                my_file.write(input('Comments: '))


        tf.keras.backend.clear_session()



        class_weight = {
            0: self.class_dict['0']['classweight'],
            1: self.class_dict['1']['classweight'],
            2: self.class_dict['2']['classweight'],
            3: self.class_dict['3']['classweight']
        }
        class_labels = ["Signal", "TT", "DY", "ST"]
        print("Using classweights, weights are")
        print(class_weight)
        print(class_labels)
        #Manuel has code for better classweights, input plotting, and something else ask him he will send code

        #Turn the labels into onehots, prepare the binarizer
        label_binarizer = LabelBinarizer().fit([0,1,2,3])

        #How many inputs?
        input_len = len(self.full_array[0])


        #Prepare train and test samples, as well as random states
        events = self.full_array
        labels = self.full_label
        sampleweights = self.full_weight

        events_train, events_test, labels_train, labels_test, sampleweights_train, sampleweights_test  = train_test_split(events, labels, sampleweights, test_size=0.33)
        labels_train = label_binarizer.transform(labels_train)
        labels_test = label_binarizer.transform(labels_test)


        #Create a layer to normalize the inputs
        #Inputs for DNN must be normalized, set normalization funcs on the train set
        norm_inputs = tf.keras.layers.Normalization(axis=-1)
        norm_inputs.adapt(events_train)


        events_train_norm = norm_inputs(events_train)
        events_test_norm = norm_inputs(events_test)

        #Was having problems with normalization, norm_inputs method was causing issues with predict
        events_train_norm = events_train
        events_test_norm = events_test

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

        l1_value = 0.00001
        l2_value = 0.0001
        dropout_value = 0.3

        def base_model():
            model = tf.keras.Sequential()

            #model.add(tf.keras.layers.BatchNormalization(input_dim=input_len))
            model.add(tf.keras.layers.Normalization(input_dim=input_len))

            #Manuel recommends having the nodes look like a cone and continue to decrease
            #Manuel says relu is dumb for our normalization, testing tanh on first layer
            model.add(tf.keras.layers.Dense(128, activation="tanh"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dense(256, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

            model.add(tf.keras.layers.Dense(128, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

            model.add(tf.keras.layers.Dense(64, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

            model.add(tf.keras.layers.Dense(32, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

            model.add(tf.keras.layers.Dense(16, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

            model.add(tf.keras.layers.Dense(8, activation="relu"))#, kernel_regularizer=tf.keras.regularizers.L1L2(l1=l1_value, l2=l2_value)))

            model.add(tf.keras.layers.Dropout(dropout_value))

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

        self.model = base_model()

        self.model.summary()


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
                                epochs=20,
                                #class_weight=class_weight,
                                batch_size=64,
                                # Callback: set of functions to be applied at given stages of the training procedure
                                callbacks=[
                                    #tf.keras.callbacks.ModelCheckpoint(model_NamePath, monitor='val_loss', verbose=False, save_best_only=True),
                                    tf.keras.callbacks.LearningRateScheduler(scheduler), # How this is different from 'conf.optimiz' ?
                                    tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=1E-7, patience=5) # Stop once you stop improving the val_loss
                                    ]
                                )
            return history




        def make_performance_plots(model, test_events, test_labels, plot_prefix=""):
            predict_set = model.predict(test_events)

            cm = sklearn.metrics.confusion_matrix(np.argmax(test_labels, axis=1), np.argmax(predict_set, axis=1), normalize='true')
            disp = sklearn.metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
            disp.plot(cmap=plt.cm.Blues)
            plt.savefig(self.model_folder+plot_prefix+"conf_matrix.pdf")
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
            g.savefig(self.model_folder+plot_prefix+"roc_curves.pdf")
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
            plt.savefig(self.model_folder+plot_prefix+"accuracy.pdf")
            plt.clf()
            plt.close()

            plt.plot(history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.grid(True)
            plt.yscale("log")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.legend(['train', 'test'], loc='upper left')
            plt.savefig(self.model_folder+plot_prefix+"loss.pdf")
            plt.clf()
            plt.close()

        def validate_dnn_output(plot_prefix=""):
            predict_list = []
            fname_list = []
            plotbins = 100
            plotrange = (0.0, 1.0)
            for classification in self.class_dict.keys():
                for fname in self.class_dict[classification]['filelist']:
                    print("Going to predict ", fname)
                    predict_list.append(self.predict(fname))
                    fname_list.append(fname)
            for i in range(len(predict_list)):
                plt.hist(predict_list[i][:,0], bins=plotbins, range=plotrange, density=True, histtype='step', label=fname_list[i].split('/')[-1], alpha=0.5)

            plt.legend(loc='upper right')
            plt.yscale('log')
            plt.savefig(self.model_folder+plot_prefix+"dnn_values.pdf")

            plt.clf()

            acceptance_list = []
            x = np.linspace(0.0, 1.0, 101)
            for i in range(len(predict_list)):
                tmp_list = []
                for cut in x:
                    tmp_list.append(np.sum(predict_list[i][:,0] > cut)/len(predict_list[i]))
                acceptance_list.append(tmp_list)
                plt.plot(x, acceptance_list[i], label=fname_list[i].split('/')[-1])

            plt.legend(loc='upper right')
            plt.yscale('log')
            plt.savefig(self.model_folder+plot_prefix+"dnn_acceptance.pdf")



        def do_feature_imp(sk_model):
            #Feature importance requires sklearn model
            import eli5
            from eli5.sklearn import PermutationImportance

            perm = PermutationImportance(sk_model, n_iter=10, random_state=1).fit(events_train_norm, labels_train)
            feat_import_dict = eli5.format_as_dict(eli5.explain_weights(perm, top=100))

            feat_import = feat_import_dict['feature_importances']['importances']
            print(eli5.format_as_text(eli5.explain_weights(perm, top=100, feature_names=input_labels)))
            return perm




        save_path = "./"+self.model_folder+"/TT_ST_DY_signal"
        history = fit_model(self.model, save_path)
        self.model.save(save_path)
        make_performance_plots(self.model, events_test_norm, labels_test)
        make_history_plots(history)
        validate_dnn_output()


        """
        save_path = "./"+model_folder+"/SK_TT_ST_DY_signalM450"
        sk_model = KerasRegressor(build_fn=base_model)
        sk_history = fit_model(sk_model, save_path)
        make_performance_plots(sk_model, events_test_norm, labels_test, "sk_")
        make_history_plots(sk_history, "sk_")
        perm = do_feature_imp(sk_model)
        """


    def load_model(self, modelname):
        self.model = tf.keras.models.load_model(modelname)
        print("Loaded model ", modelname)
        print(self.model.summary())

    def predict(self, filename):
        #Never give the param to predict, should always be full range [300,700]
        print("Going to predict events on file ", filename)
        events = self.prepare_events(filename)
        array = (self.create_nparray(events)).transpose()
        #norm_inputs = tf.keras.layers.Normalization(axis=-1)
        #norm_inputs.adapt(array)
        #array_norm = norm_inputs(array)
        pred = self.model.predict(array)
        return pred




train_example = False
predict_example = False

if train_example:
    dnn = DNN_Model()

    dnn.add_to_class_dict(0, "input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-300_PreEE.root", [300,300])
    dnn.add_to_class_dict(0, "input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_PreEE.root", [450,450])
    dnn.add_to_class_dict(0, "input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-700_PreEE.root", [700,700])

    dnn.add_to_class_dict(1, "input_files/with_hme/TTto2L2Nu/TTto2L2Nu_PreEE.root")

    dnn.add_to_class_dict(2, "input_files/with_hme/DYJetsToLL_M-50/DYJetsToLL_M-50_PreEE.root")
    dnn.add_to_class_dict(2, "input_files/with_hme/DYto2L-2Jets_MLL-10to50/DYto2L-2Jets_MLL-10to50_PreEE.root")

    dnn.add_to_class_dict(3, "input_files/with_hme/TbarWplusto2L2Nu/TbarWplusto2L2Nu_PreEE.root")
    dnn.add_to_class_dict(3, "input_files/with_hme/TWminusto2L2Nu/TWminusto2L2Nu_PreEE.root")

    dnn.finalize_class_dict()

    dnn.train_model()

if predict_example:
    dnn = DNN_Model()

    pred_file = "input_files/with_hme/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450/GluGlutoRadiontoHHto2B2Vto2B2L2Nu_M-450_PostEE.root"
    old_model = "DNN_Model_Example/TT_ST_DY_signal"
    dnn.load_model(old_model)
    print(dnn.predict(pred_file))
