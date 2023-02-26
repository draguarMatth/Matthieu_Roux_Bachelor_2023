import os, sys
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
import numpy as np
from google.protobuf import text_format
from tensorflow.python.platform import gfile
from tensorflow.python.util import compat

"""
Use to create pbtxt config file from Keras (.h5) model 
"""

INPUT_SAVED_MODEL_DIR = './DL_Models/bachelor_DL_layers_DF_21Fev.h5'
OUTPUT_SAVED_MODEL_DIR = "./DL_Models/bachelor_DL_layers_DF_21Fev/1"
 
def prepare_model(input_model, dir_save_elmt) :
    model = keras.models.load_model(INPUT_SAVED_MODEL_DIR)
    # model = # Your model# Convert Keras model to ConcreteFunction

    full_model = tf.function(lambda x: model(x))
    full_model = full_model.get_concrete_function(
        tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))# Get frozen ConcreteFunction
    frozen_func = convert_variables_to_constants_v2(full_model)
    return frozen_func

def convert_pbtxt_to_pb (input_model = INPUT_SAVED_MODEL_DIR, dir_save_elmt = OUTPUT_SAVED_MODEL_DIR) :
    #path of the directory where you want to save your model
    frozen_out_path = dir_save_elmt
    # name of the .pb file
    frozen_graph_filename = "config"
    
    frozen_func = prepare_model(input_model, dir_save_elmt)
    frozen_func.graph.as_graph_def()
    
    # pbtxt >> pb
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                    logdir=frozen_out_path,
                    name=f"{frozen_graph_filename}.pb",
                    as_text=False)
   
def convert_pb_to_pbtxt (input_model = INPUT_SAVED_MODEL_DIR, dir_save_elmt = OUTPUT_SAVED_MODEL_DIR) :
    #path of the directory where you want to save your model
    frozen_out_path = dir_save_elmt
    # name of the .pb file
    frozen_graph_filename = "config"
    
    frozen_func = prepare_model(input_model, dir_save_elmt)
    frozen_func.graph.as_graph_def()
    
    # pb >> pbtxt
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                    logdir=frozen_out_path,
                    name= f"{frozen_graph_filename}.pbtxt",
                    as_text=True)


