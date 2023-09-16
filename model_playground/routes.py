from flask import Flask, render_template, request, jsonify
from .model import Model
import sys

app = Flask(__name__)

# utility function for reading in a model
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
def serve_static_content(model_file):
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
