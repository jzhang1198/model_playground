#!/usr/bin/env python3

import os
import sys
import argparse
from flask import Flask
from model_playground.routes import exec_serve_static_content, exec_serve_plot_data, exec_serve_slider_data, exec_update_plot_data

app = Flask(__name__, static_url_path='/static', template_folder='./templates')
MODEL_FILE, MODEL, PLOT_DATA = None, None, {}

# Set caching headers for all responses
@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# route for serving static content
@app.route('/')
def serve_static_content():
    global MODEL
    MODEL, response = exec_serve_static_content(MODEL_FILE) 
    return response

# route for handling slider data requests
@app.route('/serve_slider_data', methods=['GET'])
def serve_slider_data():
    response = exec_serve_slider_data(MODEL)
    return response

# route for handling plot data requests
@app.route('/serve_plot_data', methods=['GET'])
def serve_plot_data():
    global PLOT_DATA
    PLOT_DATA, response = exec_serve_plot_data(MODEL, PLOT_DATA)
    return response

# route for handling update requests
@app.route('/update_plot_data', methods=['POST'])
def update_plot_data():
    global MODEL, PLOT_DATA 
    MODEL, PLOT_DATA, response = exec_update_plot_data(MODEL, PLOT_DATA)
    return response

if __name__ == '__main__':

    # construct parser
    parser = argparse.ArgumentParser(description='Runs a modelPlayground local server.')
    parser.add_argument('--model-file', type=str, help='Path to model file.', required=True)

    # access arguments
    args = parser.parse_args()
    MODEL_FILE = args.model_file

    # ensure model file exists
    if not MODEL_FILE: 
        print('ERROR: A model file is required to run the local server.')
        sys.exit()

    elif not os.path.exists(MODEL_FILE):
        print('ERROR: Model file not found.')
        sys.exit()

    app.run()