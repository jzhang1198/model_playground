from model_playground import Model, IndependentVariableCollection, ParameterCollection
import numpy as np

def linear_model(x: np.ndarray, m, b):
    return (x * m) + b

independent_variable_collection = IndependentVariableCollection(names=['x'], value_arrays=[np.linspace(-10, 10, 100)])
parameter_collection = ParameterCollection(names=['m', 'b'], initial_values=[1, 0])

model = Model(
    model=linear_model, 
    model_name='Linear Model',
    independent_variable_collection=independent_variable_collection, 
    parameter_collection=parameter_collection
    )