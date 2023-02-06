import os
import zipfile
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from def_model_module import get_model
import process_NIFTI_input
import csv

"""
This module was used to transform model with less deep layers
and save it in .pb format to be compatible with Triton NVidia criterias acceptance
"""

path_scan = "MatthieuR/vm/OKAPY_Nii/output/HN-CHUM-006__GTVt__RTSTRUCT__CT.nii.gz"
save_newModel = "MatthieuR/vm/Model/Model_saved/QuantImage_DL_4L_44_Keras"
saved_Model = "MatthieuR/vm/Model/Model_saved/QuantImage_DL_4L_43"


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

#reconstruct model
reconstructed_model = tf.saved_model.load(saved_Model)

#verifiy model architecture and analyse model deep layers
reconstructed_model.summary()

# Transforme DICOM to NIFTI
input = process_NIFTI_input.process_scan(path_scan)


# verify and analyse layers (-4) of given model
feature_maps1 = reconstructed_model.predict(np.expand_dims(input, axis=0))
print(reconstructed_model.name,feature_maps1.shape)
print(model.layers[-4].name,feature_maps1.shape)
print(reconstructed_model.name,(np.expand_dims(input, axis=1)).shape)

# construct new model with deeper end layer and verify it
model = keras.Model(inputs=reconstructed_model.inputs, outputs=reconstructed_model.layers[-4].output, name = "QuantImage_DL_4L")
feature_maps2 = model.predict(np.expand_dims(input, axis=0)).squeeze()
print(reconstructed_model.layers[-4].name,feature_maps2.shape)
print(model.layers[-4].name,(np.expand_dims(output, axis=0)).shape)

# architecture new model verification
model.summary()

# saved new model in 2 formats
save_Model (model, saveKeras_newModel)
savedModel (model,saved_Model)


