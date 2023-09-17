from flask import Flask, Blueprint, render_template, request, jsonify, current_app
from .model import Model
import sys

template = Blueprint('template', __name__)

# Set caching headers for all responses
@template.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

def load_model(model_file: str):
    """
    Reads a model into memory.

    Parameters:
        model_file (str): Path to the input model.
    """

    # execute the model file and get variables
    variables = {}
    with open(model_file, 'r') as file:
        exec(file.read(), variables)

    # identify variable containing the model
    for value in variables.values():
        if type(value) == Model:
            return value
    
    print('ERROR: Model was not successfully read into memory. Ensure that you have constructed a Model object in your model file.')
    sys.exit()

# route for serving static content
@template.route('/')
def serve_static_content():

    if not current_app.config['model']:
        # read the model into memory
        current_app.config['model'] = load_model(current_app.config['model_file'])

    return render_template('index.html', model_name=current_app.config['model'].name)

# route for handling slider data requests
@template.route('/serve_slider_data', methods=['GET'])
def serve_slider_data():
    return jsonify(current_app.config['model'].slider_data)

# route for handling plot data requests
@template.route('/serve_plot_data', methods=['GET'])
def serve_plot_data():

    x = current_app.config['model'].independent_variable_collection.get_value_arrays()
    x = x[0] if len(x) == 1 else x
    xlabel = current_app.config['model'].independent_variable_collection.get_names()
    xlabel = xlabel[0] if len(x) == 1 else xlabel

    # generate the layout for independent variables
    assert len(current_app.config['model'].independent_variable_collection.get_value_arrays()) < 3, 'LocalServerError: Only can plot functions with a maximum of two independent variables!'
    layout = {'title': current_app.config['model'].name}
    for index, name in enumerate(current_app.config['model'].independent_variable_collection.get_names()):
        axis = 'xaxis' if index == 0 else 'yaxis'
        layout[axis] = {'title': name, 'aspectratio': 1}

    # generate data for traces and layout for model prediction(s)
    traces = []
    for index, trace in enumerate(current_app.config['model'].evaluate()):

        trace_data = {'type': 'scatter', 'mode': 'lines','x': x, 'y': trace}
        name = None if len(current_app.config['model'].prediction_names) <= index else current_app.config['model'].prediction_names[index]

        if name:
            trace_data['name'] = name
        
        traces.append(trace_data)

    current_app.config['plot_data']['traces'] = traces
    axis = 'yaxis' if axis == 'xaxis' else 'zaxis'
    layout['axis'] = {'title': current_app.config['model'].name, 'aspectratio': 1}
    current_app.config['plot_data']['layout'] = layout

    return jsonify(current_app.config['plot_data'])

# route for handling update requests
@template.route('/update_plot_data', methods=['POST'])
def update_plot_data():

    data = request.json
    param_name = str(data['paramName'])
    param_value = float(data['paramValue'])
    current_app.config['model'].update_parameter(param_name, param_value)

    for index, trace in enumerate(current_app.config['model'].evaluate()):
        current_app.config['plot_data']['traces'][index]['y'] = trace

    return jsonify(current_app.config['plot_data'])

def launch_interactive(model: Model):

    app = Flask(__name__, static_url_path='/static', template_folder='./templates')
    app.config['model_file'], app.config['model'], app.config['plot_data'] = None, model, {}

    # register route handling functions
    app.register_blueprint(template)
    app.run()