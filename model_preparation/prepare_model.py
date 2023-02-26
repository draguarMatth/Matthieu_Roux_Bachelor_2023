import os
import zipfile
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from def_model_module import get_model
import process_NIFTI_input
from create_pbtxt_from_KerasH5 import convert_pb_to_pbtxt as to_pbtxt

"""
This module was used to transform model with less deep layers
and save it in .pb format to be compatible with Triton NVidia criterias acceptance
"""

path_scan = "/home/matthieu-roux/MatthieuR/vm/model_preparation/OKAPY_Nii/output/HN-CHUM-006__CT.nii.gz"
old_Model_weight = "/home/matthieu-roux/MatthieuR/vm/model_preparation/DL_Models/3dcnn.h5"
saved_new_Keras_Model_h5 = "/home/matthieu-roux/MatthieuR/vm/model_preparation/DL_Models/bachelor_DL_layers_DF_21Fev.h5"
path_Keras_modelSaved = "/home/matthieu-roux/MatthieuR/vm/model_preparation/DL_Models/3D_covid_1_Keras_pb"
saved_Model = "/home/matthieu-roux/MatthieuR/vm/model_preparation/DL_Models/bachelor_DL_layers_DF_21Fev/1/model"
#path_Keras_modelSaved = "/home/matthieu-roux/MatthieuR/vm/Model/Model_saved/QuantImg_Keras_PostTrain_save"

def save_Model (TheModel, path):
    """
    Save model in Keras format
    """
    return  TheModel.save(path)

def savedModel (TheModel,path):
    """
    Save model in TensorFlow .pb format
    """
    return tf.saved_model.save(TheModel,path)

#reconstruct model Keras with HDF5 weights
#reconstructed_model = get_model()
#reconstructed_model.load_weights(old_Model_weight)

#(easier way) reconstruct model Keras .pb (with folders : saved_model.pb && keras_metadata.pb)
reconstructed_model = keras.models.load_model(path_Keras_modelSaved)

#verifiy model architecture and analyse model deep layers
reconstructed_model.summary()

# Transforme DICOM to NIFTI
input = process_NIFTI_input.process_scan(path_scan)

# Test du model reconstruit :
""" np.testing.assert_allclose(
    reconstructed_model.predict(input)
) """

# verify and analyse layers (-4) of given model
feature_maps1 = reconstructed_model.predict(np.expand_dims(input, axis=0))
print(reconstructed_model.name,feature_maps1.shape)
print(reconstructed_model.layers[-4].name,feature_maps1.shape)
print(reconstructed_model.name,(np.expand_dims(input, axis=1)).shape)

# construct new model with deeper end layer and verify it
model = keras.Model(inputs=reconstructed_model.inputs, outputs=reconstructed_model.layers[-4].output, \
    name = "bachelor_DL_layers_DF_15Fev")
feature_maps2 = model.predict(np.expand_dims(input, axis=0)).squeeze()
print(reconstructed_model.layers[-4].name,feature_maps2.shape)
print(model.layers[-4].name,(np.expand_dims(input, axis=0)).shape)

# architecture new model verification
model.summary()

# saved new model in 2 formats
save_Model (model, saved_new_Keras_Model_h5)
savedModel (model,saved_Model)

# make config.pbtxt file for Triton server
to_pbtxt ()
