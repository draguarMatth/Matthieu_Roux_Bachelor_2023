import os
from datetime import datetime
from time import strftime
import shutil
import csv
from zipfile import ZipFile


temp_csv_folder = "static/downloads/DL_results"
modalities = ["CT", "PT", "IRM"]
rois = ["GTV T", "GTV N", "GTV L"]
rois_extract = ["GTVT", "GTVN", "GTVL"]

def clean_folder (folder_path):
    """
    Verify if folder exist and create it if not
    Remove the folder (to clean it if it already exist) and make a new folder
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok = True)
    else:
        shutil.rmtree(folder_path, ignore_errors=True)
        os.makedirs(folder_path)


def extract_patient_modal_roi(filename):
    """
    Extract caractéristics (patientID, modality, roi) from dicom file path to populate result of inference
    Return an array, in order, [patientID, modality, roi]
    """
    result = []
    modality_found = False
    roi_found = False
        
    while modality_found == False and roi_found == False:
        for modality in modalities:
            if modality in filename:
                for_split = "_" + modality + "_"

                # Patient ID extraction
                file_name = os.path.basename(filename)
                patient_name = file_name.split(for_split)[0]

                if patient_name[-1] == "_":        
                    patient_name = patient_name[:-1]

                result.append(patient_name)
                result.append(modality)
                modality_found = True

                f = os.path.basename(filename)
                f = f.upper()
                f_n = f.split(for_split)[-1]
                roi_patient = f_n.strip("_")
                roi_patient = roi_patient.replace(" ", "")
                roi_p = roi_patient.split(for_split)[0]

                #ROI extraction
                for roi in rois_extract:
                    if roi in roi_p:
                        r = roi[:-1] + " " + roi[-1]
                        result.append(r)
                        roi_found = True

    return result


def save_csv (deep_features, albumID, destination_folder = temp_csv_folder):
    """
    Save results in csv files determined by the acquisition modality and regions of interest
    No header in csv files.
    each row of csv file is constructed according to : patientID;modality;roi
    All csv files obtained are put in one zip file in the "temp_csv_folder" directory
    Return zip file path
    """
    csvFile = ""
    csv_files_list = []
    writed = False
    date = datetime.now().strftime("%Y_%m_%d__%H:%M:%S")
    zipName = temp_csv_folder + "/" + albumID + "_" + date + ".zip"
    zipCSV = ZipFile(zipName, 'w')
  
    for modality in modalities :
        cpt = 0

        for roi in rois:
            r = []
            csvFile = "./" + albumID + "_" + modality+ "_" + roi + ".csv"
            for results in deep_features :
                for result in results:
                    if modality in result[1] and roi in result[2] :
                        r.append(result)
            cpt+=1

            if  len(r) != 0:
                with open(csvFile, 'w', newline='') as csv_f :
                    writer = csv.writer(csv_f, delimiter=';')

                    if (os.stat(csvFile).st_size != 0):
                        writed = True

                    for data in r :               
                        if (writed == False):
                            line_result= []
                            for i in range (3, len(data)):
                                cpt = 1
                                line_result=["PatientID", "Modality", "ROI"]  
                                line_result.append("Feat_" + str(cpt))
                                cpt += 1
                            line_result =[line_result]
                            writer.writerows(line_result)
                            writed = True
                        writer.writerows([data])
                    csv_f.close()
                    zipCSV.write(os.path.relpath(csvFile))
                    os.remove(csvFile)
    zipCSV.close()

    
    return zipName

