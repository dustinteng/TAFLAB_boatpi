import json
import os

def load_config():
    config_address = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_address, 'r') as file:
        return json.load(file)
