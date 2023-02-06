import os
from flask import Flask, render_template, request
import tritonclient.grpc as grpcclient, tritonclient.grpc.model_config_pb2 as mc, tritonclient.http as httpclient
import quantimageDL
from create_NIFTI import toNifti
import json
import csv
import requests
import utils


app = Flask(__name__)

base_temp_path = "./static/downloads"
dicom_test = f"./DICOM_TEST"
temp_nifti= f"{base_temp_path}/temp_nifti"
temp_dicoms = f"{base_temp_path}/temp_dicoms"
temp_csv_results = f"{base_temp_path}/DL_results"

# url and protocol for Triton client
url = "localhost:8000"
p = "HTTP"

global triton_client    
    
@app.route("/")
def home():
    
    return render_template('connect_kheops.html')


@app.route('/studies', methods = ['GET','POST'])
def studies():
    """
    Call "connect_kheops.html" in each way
    """
    # downloaad patient DICOM medical images and transform them to NIFTI 
    if request.method == 'POST':
        utils.clean_folder(temp_dicoms)

        auth = request.headers['Authorization']
        data = request.get_json() 
        albumID = str(data['albumID'])
        
        try:
            studies = data['studies']
            albumID = str(data['albumID'])
            album = albumID

            for study in studies :
                requestURL = "https://kheops.ehealth.hevs.ch/api/studies/" + str(study['study_id']) + "?accept=application/zip&albumID=" + albumID
                r = requests.get(requestURL, headers={'Authorization': auth}, stream=True)
                with open("./static/downloads/temp_dicoms/" + study['patient_id'] + "-" + study['study_id'] + ".zip", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)

        except Exception as e:
            temp_dicom = dicom_test
            albumID = "Un problème est survenu, vous pouvez continuer avec des données tests."
            print("Somethings is wrong : " + str(e))

        toNifti(temp_dicoms, temp_nifti)
        
        return render_template("connect_kheops.html", album = albumID)                

    else:
        return render_template("connect_kheops.html")                


@app.route("/models", methods = ['POST'])
def get_models():
    """ 
    Construct Triton client and download models list to display it in "models.html"
    """
    triton_client = quantimageDL.triton_client_connection (url, p)
    list_models = triton_client.get_model_repository_index()

    albumID = request.form['album']
   
    return render_template("models.html", list_models = list_models, album = albumID)
        

def select_used_parameters(param_list_json):
    """ 
    Prepare Kwargs
    """
    Kwark = param_list_json.copy()
    
    for js in param_list_json:
        if (param_list_json[js] == ""):
            del Kwark[js]

    return Kwark

        
@app.route("/resultats",methods = ['POST'])
def result():
    """ 
    Call inference with quantImageDL and transfer the results to "results.html"
    """
    if request.method == 'POST':
        model = eval(request.form.get('model_name'))

        m = model['name']

        try :
            x = model['version']
        except Exception :
            x=1

        albumID = request.form['album']

        data = {"model_name": str(m), "model_version": str(x), "images_path": str(temp_nifti), "album_id": albumID }
        Kwargs=select_used_parameters(data)

        results = []
        results =  quantimageDL.run_annalysis(**Kwargs)

        for i in results[1]:
            print(" Flie : " + str(i) )

    return render_template('results.html', album = albumID, model_name = m, model_version = x, results = results[0], csv = results[1])


if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)