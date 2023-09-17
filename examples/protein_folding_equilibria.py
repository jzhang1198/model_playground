from model_playground.model import Model, IndependentVariableCollection, ParameterCollection
import numpy as np

# define the model
def fraction_folded(dG, T):
    """
    Model relating the fraction of folded protein to the 
    free energy of the folding equilibrium.
    """

    RT = 1.9872036e-3 * T
    pf = np.divide(1, 1 + np.exp(np.divide(dG, RT)))

    return pf

# define the independent variable collection
# NOTE: ensure that the variable names are consistent with the function signature
# NOTE: value_arrays will be converted to np.ndarrays upon construction
independent_variable_collection = IndependentVariableCollection(names=['dG'], value_arrays=[np.linspace(-5, 5, 1000)])

# define the free parameter variable collection
# NOTE: ensure that parameter names are consistent with the function signature
parameter_collection = ParameterCollection(names=['T'], initial_values=[298], lower_bounds=[0], upper_bounds=[1000])

# construct the model
model = Model(
    model=fraction_folded, 
    name='Protein Folding Equilibria',
    independent_variable_collection=independent_variable_collection, 
    parameter_collection=parameter_collection
    )