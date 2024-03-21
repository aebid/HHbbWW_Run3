from dnn import DNN_Model

quiet = 1
debug = 0


for i in range(10):
    dnn = DNN_Model(quiet, debug)
    
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
