#!/usr/bin/env python3

import os
import sys
import argparse
# from modelPlayground import Model
# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__, static_url_path='/static', template_folder='')

def read_model(model_file: str):
    """
    Reads a variables within an input model file into memory.
    """

    # execute the model file and get variables
    model = None
    variables = {}
    with open(model_file, 'r') as file:
        exec(file.read(), variables)

    # identify variable containing the model
    for value in variables.values():
        if type(value) == Model:
            model = value
    return model

# route for serving static content
# @app.route('/')
# def serve_static_content():
#     pass

# # route for handling slider data requests
# @app.route('/send_slider_data', methods=['GET'])
# def serve_slider_data():
#     pass

# # route for handling plot data requests
# @app.route('/send_initial_data', methods=['GET'])
# def serve_plot_data():
#     pass

# # route for handling update requests
# @app.route('/send_data', methods=['GET'])
# def update_plot_data():
#     return

if __name__ == '__main__':

    # construct parser
    parser = argparse.ArgumentParser(description='Runs a modelPlayground local server.')
    parser.add_argument('--model-file', type=str, help='Path to model file.', required=True)

    # access arguments
    args = parser.parse_args()
    model_file = args.model_file

    if not model_file: 
        print('ERROR: A model file is required to run the local server.')
        sys.exit()

    if not os.path.exists(model_file):
        print('ERROR: Model file not found.')
        sys.exit()

    # read the model into memory
    model = read_model(model_file)

    if not model:
        print('ERROR: Model was not successfully read into memory. Ensure that you have constructed a Model object in your model file.')

    # app.run()