import json
import os

config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/config_indice.json"

def read_config_file(config_file=config_file):
    with open(config_file) as json_data:
            data = json.load(json_data)
    return data