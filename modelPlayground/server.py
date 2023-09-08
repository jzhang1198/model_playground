from flask import Flask, render_template, request, jsonify
import numpy as np

import inspect
from typing import Callable

class IndependentVariableCollection:
    def __init__(self, names: list, value_arrays: list, units:list=[]):

        assert len(names) == len(value_arrays), 'ERROR: The length of names and values lists must be identical.'

        self.names = names
        self.value_arrays = value_arrays
        self.units = units if len(units) > 0 else [None] * len(names)
    
    def get_names(self):
        return self.names
    
    def get_value_arrays(self):
        return self.value_arrays
    
    def get_units(self):
        return self.units

class ParameterColllection:
    def __init__(self, names: list, initial_values: list, lower_bounds:list=[], upper_bounds:list=[], units:list=[]):

        assert len(names) == len(initial_values), 'ERROR: The length of names, values, upper_bounds, and lower_bounds lists must be identical.' 

        self.names = names
        self.initial_values = initial_values
        self.lower_bounds = lower_bounds if len(lower_bounds) > 0 else [None] * len(names)
        self.upper_bounds = upper_bounds if len(upper_bounds) > 0 else [None] * len(upper_bounds)
        self.units = units if len(units) > 0 else [None] * len(names)

    def get_names(self):
        return self.names
    
    def get_initial_values(self):
        return self.initial_values
    
    def get_lower_bounds(self):
        return self.lower_bounds

    def get_upper_bounds(self):
        return self.upper_bounds
    
    def get_units(self):
        return self.units

class Model:
    def __init__(
            self, 
            model: Callable,
            model_name: str,
            independent_variable_collection: IndependentVariableCollection,
            parameter_collection: ParameterColllection,
            model_units:str = None
            ):
        
        # parse function signature of the model to ensure consistency with collections
        signature = inspect.signature(model)
        arguments = list(signature.parameters.keys())
        assert len(arguments) == len(independent_variable_collection.get_names()) + len(parameter_collection.get_names())
        assert set(arguments) == set(independent_variable_collection.get_names()).union(set(parameter_collection.get_names()))
        
        self.model = model
        self.model_name = model_name
        self.model_units = model_units
        self.independent_variable_collection = independent_variable_collection
        self.parameter_collection = parameter_collection

        # private dictionaries to map parameter names to values or value arrays
        self._independent_variable_dictionary = dict([(argname, value_range) for argname, value_range in zip(self.independent_variable_collection.get_names(), self.independent_variable_collection.get_value_arrays())])
        self._parameter_dictionary = dict([(argname, argvalue) for argname, argvalue in zip(self.parameter_collection.get_names(), self.parameter_collection.get_initial_values())])
        self._argument_dictionary = dict(
            **self._independent_variable_dictionary, 
            **self._parameter_dictionary)

    def evaluate(self):
        """ 
        Evaluates the model with set independent variables and parameters.
        """
        return self.model(**self._argument_dictionary)
    
    def update_parameter(self, param_name: str, new_value: float):
        self._parameter_dictionary[param_name] = new_value
        self._argument_dictionary = dict(**self._independent_variable_dictionary, **self._parameter_dictionary)

def generate_slider_data(model):
    
    slider_datas = []
    NO_STEPS = 50
    MIN = 0
    MAX = 100
    SCALE = 'linear'

    for name, initial_value, lower_bound, upper_bound in zip(
        model.parameter_collection.get_names(), 
        model.parameter_collection.get_initial_values(), 
        model.parameter_collection.get_lower_bounds(), 
        model.parameter_collection.get_upper_bounds()):

        lower_bound = lower_bound if lower_bound else MIN 
        upper_bound = upper_bound if upper_bound else MAX
        stepsize = (upper_bound - lower_bound) / (NO_STEPS - 1)

        slider_datas.append(
            {'name': name, 
                'scale': SCALE,
                'min': lower_bound, 
                'max': upper_bound, 
                'initial_value': initial_value, 
                'stepsize': stepsize}
                )

    return slider_datas

app = Flask(__name__, static_url_path='/static')

independent_variable_collection = IndependentVariableCollection(names=['x'], value_arrays=[np.linspace(-10, 10, 100)])
parameter_collection = ParameterColllection(names=['m', 'b'], initial_values=[1, 0])

def linear_model(x: np.ndarray, m, b):
    return (x * m) + b

model = Model(model=linear_model, model_name='Linear Model',independent_variable_collection=independent_variable_collection, parameter_collection=parameter_collection)
slider_datas = generate_slider_data(model)

# route for serving content
@app.route('/')
def serve():
    
    # send a response containing dynamically generated HTML with plot data
    # return render_template(
    #     'index.html', 
    #     model_name=model.get_name(),
    #     model_units=model.get_units(include_parentheses=True),
    #     independent_variable_names=model.independent_variable_collection.get_names(),
    #     independent_variable_units=model.independent_variable_collection.get_units(include_parentheses=True),
    #     x_data=model.independent_variable_collection.get_values(),
    #     y_data=model.evaluate(),

    #     )
    return render_template(
        'index.html', 
        model_name='Model!',
        )

# route for handling slider data requests
@app.route('/send_slider_data', methods=['GET'])
def serve_slider_data():
    return jsonify(slider_datas)

# route for handling initial plot data requests
@app.route('/send_initial_data', methods=['GET'])
def serve_initial_data():

    x = model.independent_variable_collection.get_value_arrays()
    y = model.evaluate()

    return jsonify({'x': x.tolist(), 'y': y.tolist()})

# route for handling data requests
@app.route('/send_data', methods=['GET'])
def update_plot_data():

    # process request
    json = request.json
    parameter_value = float(json['paramterValue'])
    parameter_name = json['parameterName']

    # update parameters and evaluate
    model.update(parameter_name, parameter_value)
    output = model.evaluate().tolist()

    response = jsonify({'data': output})
    response.headers['Content-Type'] = 'application/json'

    # return model output; plotting handled on the front-end
    return response

if __name__ == '__main__':
    app.run(debug=True)