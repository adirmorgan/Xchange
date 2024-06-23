from flask import Flask
import json
import requests
import time 

import logging
import os
import cloudstorage as gcs
import webapp2

from google.appengine.api import app_identity

app = Flask(__name__)

@app.route("/")
def check():
    return 'Hi!'

@app.get("/rates_data")
def load():
    filename = 'current_rates.json'  
    with open(filename, 'r') as f:
        data = json.load(f)
    if isStale(data):
        update_success = update()
        if update_success:
            with open('current_rates.json','r') as f:
                data = json.load(f)

    return data


def get_bucket_name():
    bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
    return bucket_name

def create_file(filename, data):
  write_retry_params = gcs.RetryParams(backoff_factor=1.1)
  gcs_file = gcs.open(filename,
                      'w',
                      content_type='application/json',
                      retry_params=write_retry_params)
  gcs_file.write('abcde\n')
  gcs_file.close()


def update():
    latest_rates_api_endpoint = r'http://api.exchangeratesapi.io/v1/latest'
    filename = 'access_key.txt'
    with open(filename,'r') as f:
        access_key = f.read()
    
    respone = requests.get(f'{latest_rates_api_endpoint}?access_key={access_key}')
    if respone.status_code == 200:
        data = respone.json()
        with open('current_rates.json', 'w') as f:
            json.dump(data, f)
        return True

    return False

def isStale(data, update_th='day'):
    file_timestamp = data['timestamp']
    cur_timestamp = time.time()
    if update_th == 'day':
        return cur_timestamp - file_timestamp > 86400   # 60*60*24
    
    return False



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)