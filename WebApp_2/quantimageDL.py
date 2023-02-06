# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.9 (default, Nov 25 2022, 14:10:45) 
# [GCC 8.4.0]
# Embedded file name: /home/matthieu-roux/MatthieuR/TritonClient/Git_Triton_Client/src/python/examples/image_client_quantimage.py
# Compiled at: 2022-12-28 09:26:10
# Initial code from https://github.com/triton-inference-server/client
# Adaptation by Matthieu Roux for 2023 bachelor's degree 

import argparse
from functools import partial
import os, sys
from PIL import Image
import numpy as np
from attrdict import AttrDict
import nibabel as nib
from scipy import ndimage
import tritonclient.grpc as grpcclient, tritonclient.grpc.model_config_pb2 as mc, tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException
from tritonclient.utils import triton_to_np_dtype
import json
import csv
import utils


FLAGS = {}

if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue


class UserData:
    def __init__(self):
        self._completed_requests = queue.Queue()


def completion_callback(user_data, result, error):
    user_data._completed_requests.put((result, error))


def parse_model(model_metadata, model_config):
    """
    Check the configuration of a model to make sure it meets the
    requirements for an image classification network (as expected by
    this client)
    """
    if len(model_metadata.inputs) != 1:
        raise Exception('expecting 1 input, got {}'.format(
            len(model_metadata.inputs)))
    if len(model_metadata.outputs) != 1:
        raise Exception('expecting 1 output, got {}'.format(
            len(model_metadata.outputs)))
            
    if len(model_config.input) != 1:
        raise Exception('expecting 1 input in model configuration, got {}'.format(
            len(model_config.input)))

    input_metadata = model_metadata.inputs[0]
    input_config = model_config.input[0]
    output_metadata = model_metadata.outputs[0]

    if output_metadata.datatype != 'FP32':
        raise Exception("expecting output datatype to be FP32, model '" + model_metadata.name + "' output type is " + output_metadata.datatype)
                
    output_batch_dim = model_config.max_batch_size > 0
    non_one_cnt = 0
    for dim in output_metadata.shape:
        if output_batch_dim:
            output_batch_dim = False
        else:
            if dim > 1:
                non_one_cnt += 1
                if non_one_cnt > 1:
                    raise Exception('expecting model output to be a vector')

    input_batch_dim = model_config.max_batch_size > 0
    expected_input_dims = 4 + (1 if input_batch_dim else 0)
    if len(input_metadata.shape) != expected_input_dims:
        raise Exception(
            "expecting input to have {} dimensions, model '{}' input has {}".
            format(expected_input_dims, model_metadata.name, 
                    len(input_metadata.shape)))

    return (model_config.max_batch_size, input_metadata.name,
        output_metadata.name, input_config.format,
        input_metadata.datatype)


def read_nifti_file(filepath):
    """Read and load volume
    Source : https://github.com/keras-team/keras-io/blob/master/examples/vision/3D_image_classification.py
    """
    scan = nib.load(filepath)
    scan = scan.get_fdata()
    
    return scan


def normalize(volume):
    """Normalize the volume
        Source : https://github.com/keras-team/keras-io/blob/master/examples/vision/3D_image_classification.py
    """
    min = -1000
    max = 400
    volume[volume < min] = min
    volume[volume > max] = max
    volume = (volume - min) / (max - min)
    volume = volume.astype('float32')
    
    return volume


def resize_volume(img):
    """Resize across z-axis
    Source : https://github.com/keras-team/keras-io/blob/master/examples/vision/3D_image_classification.py
    """
    desired_depth = 64
    desired_width = 128
    desired_height = 128
    current_depth = img.shape[-1]
    current_width = img.shape[0]
    current_height = img.shape[1]
    depth = current_depth / desired_depth
    width = current_width / desired_width
    height = current_height / desired_height
    depth_factor = 1 / depth
    width_factor = 1 / width
    height_factor = 1 / height
    img = ndimage.rotate(img, 90, reshape=False)
    img = ndimage.zoom(img, (width_factor, height_factor, depth_factor), order=1)
    
    return img


def preprocess(img, format, dtype):
    """Read and resize image volume to resolve model specification
    Source : https://github.com/keras-team/keras-io/blob/master/examples/vision/3D_image_classification.py
    """
    volume = read_nifti_file(img)
    volume = normalize(volume)
    volume = resize_volume(volume)
    
    return volume


def postprocess(input_name, results, output_name, batch_size, supports_batching):
    """
    Post-process results to show classifications.
    """
    results_list= []
    postprocess_results = []
    output_array = results.as_numpy(output_name)

    if supports_batching:
        if len(output_array) != batch_size:
            raise Exception('expected {} results, got {}'.format(
                batch_size, len(output_array)))
    
    for results in output_array:
        if not supports_batching:
            results = [results]
        
        patient = utils.extract_patient_modal_roi(input_name)
        postprocess_results.append(patient[0])
        postprocess_results.append(patient[1])
        postprocess_results.append(patient[2])

        for result in results:
            if output_array.dtype != 'float32':
                raise Exception('expected float32 type results, got {}'.format(output_array.dtype))
            else:
                prediction = result.squeeze()

            postprocess_results.append(str(prediction))             
                   
    return postprocess_results


def requestGenerator(batched_image_data, input_name, output_name, dtype, FLAGS):
    protocol = FLAGS['protocol'].lower()
    
    if protocol == 'grpc':
        client = grpcclient
    else:
        client = httpclient
    

    inputs = [
     client.InferInput(input_name, batched_image_data.shape, dtype)]
    inputs[0].set_data_from_numpy(batched_image_data)
     
    outputs = [
     client.InferRequestedOutput(output_name)
     ]

    yield inputs, outputs, FLAGS['model_name'], FLAGS['model_version']


def convert_http_metadata_config(_metadata, _config):
    _model_metadata = AttrDict(_metadata)
    _model_config = AttrDict(_config)
    
    return _model_metadata, _model_config


def triton_client_connection (FLAGS_url ='localhost:8000', FLAGS_protocol ='HTTP', 
                FLAGS_verbose = None, FLAGS_streaming = None, FLAGS_async_set = None):
    """
    Construct triton client connection
    """
    if FLAGS_streaming and FLAGS_protocol.lower() != 'grpc':
            raise Exception('Streaming is only allowed with gRPC protocol')
    try:
        if FLAGS_protocol.lower() == 'grpc':
            triton_client = grpcclient.InferenceServerClient(
                FLAGS_url, verbose=FLAGS_verbose)
        else:
            concurrency = 20 if FLAGS_async_set else 1
            triton_client = httpclient.InferenceServerClient(
                url=FLAGS_url, verbose=FLAGS_verbose, concurrency=concurrency)
    except Exception as e:
        print('client creation failed: ' + str(e))
        sys.exit(1)
    
    return triton_client


def run_annalysis(**Kwargs):
    """
    Main module to request inference and manage results
    Return an array that includes [ [table of all results], path of the zip results backup] 
    """
    THE_LIST = []

    # Not optional
    FLAGS['model_name'] = str(Kwargs.get('model_name', None))
    FLAGS['model_version'] = str(Kwargs.get('model_version', "1"))
    FLAGS['image_filename'] = str(Kwargs.get('images_path', None))
    FLAGS['album'] = str(Kwargs.get('album_id', None))

    # Optional
    FLAGS['modality'] = str(Kwargs.get('modality', None))

    FLAGS['verbose'] = Kwargs.get('verbose', None)
    FLAGS['async_set'] = Kwargs.get('asynchrone', None)
    FLAGS['streaming'] = Kwargs.get('streaming', None)
    FLAGS['batch_size'] = int(Kwargs.get('batch_size', 1))
    FLAGS['url'] = str(Kwargs.get('url', "localhost:8000"))
    FLAGS['protocol'] = str(Kwargs.get('protocol', "HTTP"))
    triton_client = Kwargs.get('triton_client', None)

    if ( triton_client == None):
        triton_client = triton_client_connection (FLAGS['url'], FLAGS['protocol'], 
            FLAGS['verbose'], FLAGS['streaming'], FLAGS['async_set'] )

    try:
        model_metadata = triton_client.get_model_metadata(
            model_name=FLAGS['model_name'], model_version=FLAGS['model_version'])
    except InferenceServerException as e:
        print('failed to retrieve the metadata: ' + str(e))
        sys.exit(1)

    try:
        model_config = triton_client.get_model_config(
            model_name=FLAGS['model_name'], model_version=FLAGS['model_version'])
    except InferenceServerException as e:
        print('failed to retrieve the config: ' + str(e))
        sys.exit(1)

    if FLAGS['protocol'].lower() == 'grpc':
        model_config = model_config.config
    else:
        model_metadata, model_config = convert_http_metadata_config(
                model_metadata, model_config)

    max_batch_size, input_name, output_name, format, dtype = parse_model(
        model_metadata, model_config)

    supports_batching = max_batch_size > 0
    if not supports_batching and FLAGS['batch_size'] != 1:
        print("ERROR: This model doesn't support batching.")
        sys.exit(1)
    
    filenames = []
    if os.path.isdir(FLAGS['image_filename']):
        filenames = [
            os.path.join(FLAGS['image_filename'], f) 
            for f in os.listdir(FLAGS['image_filename']) 
            if os.path.isfile(os.path.join(FLAGS['image_filename'], f))
        ]
    else:
        filenames = [
            FLAGS['image_filename']
        ]

    filenames.sort()

    image_data = []
    for filename in filenames:
        img = filename
        image_data.append(
            preprocess(img, format, dtype))

    requests = []
    responses = []
    result_filenames = []
    request_ids = []
    image_idx = 0
    last_request = False
    user_data = UserData()
    async_requests = []
    sent_count = 0

    if FLAGS['streaming']:
        triton_client.start_stream(partial(completion_callback, user_data))
    
    while not last_request:
        input_filenames = []
        repeated_image_data = []

        for idx in range(FLAGS['batch_size']):
            input_filenames.append(filenames[image_idx])
            repeated_image_data.append(np.expand_dims(image_data[image_idx], axis=-1))
            image_idx = (image_idx + 1) % len(image_data)
            if image_idx == 0:
                last_request = True

        if supports_batching:
            batched_image_data = np.stack(repeated_image_data, axis=0)
        else:
            batched_image_data = repeated_image_data[0]
        
        try:
            for inputs, outputs, model_name, model_version in requestGenerator(
                batched_image_data, input_name, output_name, dtype, FLAGS):
                sent_count += 1
                if FLAGS['streaming']:
                    triton_client.async_stream_infer(FLAGS['model_name'],
                        inputs,
                        request_id=str(sent_count),
                        model_version=FLAGS['model_version'],
                        outputs=outputs)
                elif FLAGS['async_set']:                   
                    if FLAGS['protocol'].lower() == 'grpc':
                        triton_client.async_infer(FLAGS['model_name'],
                            inputs,
                            partial(completion_callback, user_data),
                            request_id=str(sent_count),
                            model_version=FLAGS['model_version'],
                            outputs=outputs)
                    else:
                        async_requests.append(triton_client.async_infer(FLAGS['model_name'],
                            inputs,
                            request_id=str(sent_count),
                            model_version=FLAGS['model_version'],
                            outputs=outputs))
                else:
                    responses.append(
                        triton_client.infer(FLAGS['model_name'], inputs,
                            request_id=str(sent_count),
                            model_version=FLAGS['model_version'],
                            outputs=outputs))

        except InferenceServerException as e:
            print('inference failed 369: ' + str(e))
            if FLAGS['streaming']:
                triton_client.stop_stream()
            sys.exit(1)

    if FLAGS['streaming']:
        triton_client.stop_stream()

    if FLAGS['protocol'].lower() == 'grpc':
        if FLAGS['streaming'] or FLAGS['async_set']:
            processed_count = 0
            while processed_count < sent_count:
                results, error = user_data._completed_requests.get()
                processed_count += 1
                if error is not None:
                    print('inference failed 385: ' + str(error))
                    sys.exit(1)
                responses.append(results)

    else:
        if FLAGS['async_set']:
            for async_request in async_requests:
                responses.append(async_request.get_result())

    result_extracted = []
    cpt = 0

    for response in responses:
        if FLAGS['protocol'].lower() == 'grpc':
            this_id = response.get_response().id
        else:
            this_id = response.get_response()['id']
        
        row2 = postprocess(filenames[cpt], response, output_name, FLAGS['batch_size'], supports_batching)
        result_extracted.append(row2)
        cpt +=1
    
    THE_LIST.append(result_extracted)

    list_result = []

    zip_csv = utils.save_csv (THE_LIST, FLAGS['album']) 
    list_result.append(THE_LIST)
    list_result.append(zip_csv)

    return list_result