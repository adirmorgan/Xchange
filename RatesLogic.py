import requests
import json
import time
import os, sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_no_server():
    filename = 'current_rates.json'
    filename = resource_path(filename)
        
    with open(filename, 'r') as f:
        data = json.load(f)

    return data['base'], data['rates']

def load_from_server(api_url):
    try:
        response = requests.get(api_url)
        data = response.json()
        return data['base'], data['rates']
    except:
        print('server down, using local data')
        return load_no_server()
   
def convValue(val, currency, base_currency, rates_dict, convert_to):
    if currency != base_currency:
        val /= rates_dict[currency]
    
    return {curr: val*rates_dict[curr] for curr in convert_to}

if __name__ == "__main__":
    base_currency, rates_dict = load_from_server()
    convert_to = ["USD", "ILS"]
    print(convValue(10, base_currency, base_currency, rates_dict, convert_to))