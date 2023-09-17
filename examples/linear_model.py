from model_playground.model import Model, IndependentVariableCollection, ParameterCollection
import numpy as np

# define the model
def linear_model(x: np.ndarray, m, b):
    return (x * m) + b

# define the independent variable collection
# NOTE: ensure that the variable names are consistent with the function signature
# NOTE: value_arrays will be converted to np.ndarrays upon construction
independent_variable_collection = IndependentVariableCollection(names=['x'], value_arrays=[np.linspace(-10, 10, 100)])

# define the free parameter variable collection
# NOTE: ensure that parameter names are consistent with the function signature
parameter_collection = ParameterCollection(names=['m', 'b'], initial_values=[1, 0], lower_bounds=[-10, -10], upper_bounds=[10, 10])

# construct the model
model = Model(
    model=linear_model, 
    name='Linear Model',
    independent_variable_collection=independent_variable_collection, 
    parameter_collection=parameter_collection
    )