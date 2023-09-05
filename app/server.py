from flask import Flask, render_template, request, jsonify
from typing import Callable
import numpy as np

app = Flask(__name__)

def init_sliders(model):

    # by default, sliders scale is set to log; this can be updated by the user front-end
    slider_scale = 'log'
    slider_dictionary = ''



    pass

model = None # to be a model object

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

# route for updating plots upon post request
@app.route('/update_plot', methods=['POST'])
def update_plot():

    # process request
    json = request.json
    parameter_value = float(json['paramterValue'])
    parameter_name = json['parameterName']

    # update parameters and evaluate
    model.set_free_parameters({parameter_name: parameter_value})
    output = model.evaluate()

    # return model output; plotting handled on the front-end
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)