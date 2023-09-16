#!/usr/bin/env python3

import os
import sys
import argparse
from model_playground.model import Model
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_url_path='/static', template_folder='./templates')
PLOT_DATA = {}
MODEL = None

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
@app.route('/')
def serve_static_content():
    global MODEL

    # read the model into memory
    MODEL = read_model(model_file)

    if not MODEL:
        print('ERROR: Model was not successfully read into memory. Ensure that you have constructed a Model object in your model file.')
        sys.exit()

    return render_template('index.html', model_name=MODEL.name)

# route for handling slider data requests
@app.route('/serve_slider_data', methods=['GET'])
def serve_slider_data():
    return jsonify(MODEL.slider_data)

# route for handling plot data requests
@app.route('/serve_plot_data', methods=['GET'])
def serve_plot_data():

    global PLOT_DATA

    x = MODEL.independent_variable_collection.get_value_arrays()
    x = x[0] if len(x) == 1 else x
    xlabel = MODEL.independent_variable_collection.get_names()
    xlabel = xlabel[0] if len(x) == 1 else xlabel

    # generate the layout for independent variables
    assert len(MODEL.independent_variable_collection.get_value_arrays()) < 3, 'LocalServerError: Only can plot functions with a maximum of two independent variables!'
    layout = {'title': MODEL.name}
    for index, name in enumerate(MODEL.independent_variable_collection.get_names()):
        axis = 'xaxis' if index == 0 else 'yaxis'
        layout[axis] = {'title': name, 'aspectratio': 1}

    # generate data for traces and layout for model prediction(s)
    traces = []
    for index, trace in enumerate(MODEL.evaluate()):

        trace_data = {'type': 'scatter', 'mode': 'lines','x': x, 'y': trace}
        name = MODEL.prediction_names[index] if len(MODEL.prediction_names) < index else None

        if name:
            trace_data['name'] = name
        
        traces.append(trace_data)

    PLOT_DATA['traces'] = traces
    axis = 'yaxis' if axis == 'xaxis' else 'zaxis'
    layout['axis'] = {'title': MODEL.name, 'aspectratio': 1}
    PLOT_DATA['layout'] = layout

    return jsonify(PLOT_DATA)

# route for handling update requests
@app.route('/update_plot_data', methods=['POST'])
def update_plot_data():

    data = request.json
    param_name = str(data['paramName'])
    param_value = float(data['paramValue'])
    MODEL.update_parameter(param_name, param_value)

    global PLOT_DATA
    for index, trace in enumerate(MODEL.evaluate()):
        PLOT_DATA['traces'][index]['y'] = trace

    return jsonify(PLOT_DATA)

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

    elif not os.path.exists(model_file):
        print('ERROR: Model file not found.')
        sys.exit()

    app.run()