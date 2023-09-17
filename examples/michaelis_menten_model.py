from model_playground.model import Model, IndependentVariableCollection, ParameterCollection
from scipy.integrate import odeint
import numpy as np

def MM_model(
        time: np.ndarray, 
        E: float, 
        S: float, 
        kon: float, 
        koff: float, 
        kcat: float
        ):
    
    # initial concentrations of E, P, ES, and S species
    initial_concentrations = np.array([E, 0, 0, S])

    # construct mass action matrices
    A = np.array([
        [1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 0, 1, 0]    ])
    N = np.array([
        [-1, 0, 1, -1],
        [1, 0, -1, 1],
        [1, 1, -1, 0]
    ])
    K = np.diag(np.array([kon, koff, kcat]))

    # define system of ODEs describing system
    def ODEs(concentrations: np.ndarray, time: np.ndarray):
        return np.dot(N.T, np.dot(K, np.prod(np.power(concentrations, A), axis=1)))
    
    # integrate the ODEs to get progress curves for E, P, ES, and S
    progress_curves = odeint(ODEs, initial_concentrations, time).T

    return progress_curves

# define the independent variable collection
# NOTE: ensure that the variable names are consistent with the function signature
# NOTE: value_arrays will be converted to np.ndarrays upon construction
independent_variable_collection = IndependentVariableCollection(names=['time'], value_arrays=[np.linspace(0, 1000, 1000)])

# define the free parameter variable collection
# NOTE: ensure that parameter names are consistent with the function signature
parameter_collection = ParameterCollection(
    names=['E', 'S', 'kon', 'koff', 'kcat'], 
    initial_values=[1e-1, 1e3, 100, 1, 1], 
    lower_bounds=[0, 0, 0, 0, 0], 
    upper_bounds=[1e1, 1e4, 1e10, 1e10, 1000])

# construct the model
model = Model(
    model=MM_model, 
    name='Michaelis Menten Model of Enzyme Kinetics',
    independent_variable_collection=independent_variable_collection, 
    parameter_collection=parameter_collection
    )