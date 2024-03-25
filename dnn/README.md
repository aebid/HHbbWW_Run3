# Tensorflow Keras DNN Model

Class used to train and apply a sequential DNN

To train, edit ```train_dnn.py``` to include the classes and files you want to use, then
```
python3 train_dnn.py
```

This will create a model and some validation plots

To use an existing model to predict outputs
```
python3 run_dnn.py -i inputFile.root -o outputFile.root -m DNN_Model_Example/TT_ST_DY_signal -p 1 -d 0
```
