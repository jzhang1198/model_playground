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