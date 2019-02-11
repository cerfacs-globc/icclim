import json
import os

config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/config_indice.json"

def read_config_file(config_file_path=config_file_path):
    with open(config_file_path) as json_data:
            data = json.load(json_data)
    return data

config_file = read_config_file()

def get_icclim_indice_config(config_file=config_file):
        #Loading config from icclim for the dispel4py wps workflow
        return config_file["icclim"]["indice"].keys()

def get_icclim_slice_mode(config_file=config_file):
        #Loading config from icclim for the dispel4py wps workflow
        return config_file["icclim"]["slice_mode"] 

def get_disp4py_config(config_file=config_file):
        #Loading config from icclim for the dispel4py wps workflow
        conf_filename = config_file["C4I"]["dispel4py_wps"]["configFileName"]
        json_structure = config_file["C4I"]["dispel4py_wps"]["jsonStructure"]
        return conf_filename, json_structure