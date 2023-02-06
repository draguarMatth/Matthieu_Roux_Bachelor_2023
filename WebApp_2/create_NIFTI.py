import os, shutil
import zipfile
import tempfile
from okapy.dicomconverter.converter import ExtractorConverter
import utils


temp_unzip= f"./static/downloads/unzip_dicom"
results_zip_folder = f"./static/downloads/DL_results"
params_path = f"./params_okapi.yml"

def unzip_dicom(zip_dicom, temp_unzip_folder):
    """ 
    Unzip zip file 
    """
    unzip_engine = zipfile.ZipFile(zip_dicom,'r')
    unzip_engine.extractall(temp_unzip_folder)
    unzip_engine.close()


def formatToNifti (zip_dicom_folder, output_directory):
    """ 
    Transform DICOM images serie to NIFTI images
    Clean temp_unzip
    Remove files (useless for us) that have "_RTSTRUCT_" in it
    """ 
    utils.clean_folder (output_directory)
    utils.clean_folder (temp_unzip)

    list_dicom = []

    for f in os.listdir(zip_dicom_folder):
        dicom_zp = f"{os.path.join(zip_dicom_folder, f)}"
        list_dicom.append(dicom_zp)

    for zip_dicom in list_dicom :
        unzip_dir = tempfile.mkdtemp(suffix=None, prefix=None, dir=temp_unzip)
        unzip_dicom(zip_dicom, unzip_dir)
        converter = ExtractorConverter.from_params(params_path)
        converter(unzip_dir, output_folder=output_directory, labels=None)
    
    utils.clean_folder (temp_unzip)
    
    for f in os.listdir(output_directory):
        File = f"{os.path.join(output_directory, f)}"
        if '_RTSTRUCT_' in f:
            os.remove(File)
           
            
def toNifti(dir_dicom_zip, nifti_folder):
    """ 
    Call formatToNifti
    Clean dicom zip folder
    Return NIFTI folder
    """ 
    utils.clean_folder(results_zip_folder)   
    formatToNifti (dir_dicom_zip, nifti_folder)
    utils.clean_folder(dir_dicom_zip)

    return nifti_folder
