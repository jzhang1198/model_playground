from model_playground.model import Model, IndependentVariableCollection, ParameterCollection
import numpy as np

def mwc(F, Kr, Kt, L):
    """
    Monod-Wyman-Changeux model of allostery

    F: the concentration of ligand
    Kr: the dissociation constant describing the affinity of F for the R state.
    Kt: the dissociation constant describing the affinity of F for the T state.
    L: the equilbrium constant for the R <-> T conformational change.
    """
    n = 2 # the number of sites accessible to the ligand

    alpha = np.divide(F, Kr)
    c = Kr / Kt

    term1 = np.power(alpha + 1, n)
    term2 = np.power(c * alpha + 1, n)
    pR = np.divide(term1, term1 + L * term2)

    return pR 

independent_variable_collection = IndependentVariableCollection(names=['F'], value_arrays=[np.linspace(0, 10, 100)], units=['µM'])
parameter_collection = ParameterCollection(names=['Kr', 'Kt', 'L'], initial_values=[1, 0], units=['µM', 'µM', None])

model = Model(
    model=mwc, 
    model_name='Monod-Wyman-Changuaex Model of Allostery',
    independent_variable_collection=independent_variable_collection, 
    parameter_collection=parameter_collection
    )