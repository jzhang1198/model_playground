from flask import render_template, request, jsonify
from .model import Model
import sys

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

def exec_serve_static_content(model_file: str):

    # read the model into memory
    model = read_model(model_file)

    if not model:
        print('ERROR: Model was not successfully read into memory. Ensure that you have constructed a Model object in your model file.')
        sys.exit()

    return model, render_template('index.html', model_name=model.name)

def exec_serve_slider_data(model):
    return jsonify(model.slider_data)

def exec_serve_plot_data(model: Model, plot_data: dict):

    x = model.independent_variable_collection.get_value_arrays()
    x = x[0] if len(x) == 1 else x
    xlabel = model.independent_variable_collection.get_names()
    xlabel = xlabel[0] if len(x) == 1 else xlabel

    # generate the layout for independent variables
    assert len(model.independent_variable_collection.get_value_arrays()) < 3, 'LocalServerError: Only can plot functions with a maximum of two independent variables!'
    layout = {'title': model.name}
    for index, name in enumerate(model.independent_variable_collection.get_names()):
        axis = 'xaxis' if index == 0 else 'yaxis'
        layout[axis] = {'title': name, 'aspectratio': 1}

    # generate data for traces and layout for model prediction(s)
    traces = []
    for index, trace in enumerate(model.evaluate()):

        trace_data = {'type': 'scatter', 'mode': 'lines','x': x, 'y': trace}
        name = model.prediction_names[index] if len(model.prediction_names) < index else None

        if name:
            trace_data['name'] = name
        
        traces.append(trace_data)

    plot_data['traces'] = traces
    axis = 'yaxis' if axis == 'xaxis' else 'zaxis'
    layout['axis'] = {'title': model.name, 'aspectratio': 1}
    plot_data['layout'] = layout

    return plot_data, jsonify(plot_data)

def exec_update_plot_data(model: Model, plot_data: dict):

    data = request.json
    param_name = str(data['paramName'])
    param_value = float(data['paramValue'])
    model.update_parameter(param_name, param_value)

    for index, trace in enumerate(model.evaluate()):
        plot_data['traces'][index]['y'] = trace

    return model, plot_data, jsonify(plot_data)
