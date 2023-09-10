import inspect
import numpy as np
from numbers import Number
from typing import Callable, Union

class IndependentVariableCollection:
    def __init__(self, names: Union[list, np.ndarray], value_arrays: Union[list, np.ndarray], units: Union[list, np.ndarray]=[]):
        """
        A utility class for organizing data associated with model independent variables.
        """

        IndependentVariableCollection._parse_inputs(names, value_arrays, units)
        self.names = IndependentVariableCollection._to_list(names)
        self.value_arrays = IndependentVariableCollection._to_list(value_arrays)
        units = units if len(units) > 0 else [None] * len(names)
        self.units = IndependentVariableCollection._to_list(units)
    
    @staticmethod
    def _parse_inputs(names, value_arrays, units):
        """ 
        Private static method for ensuring input parameters satisfy assumptions of the program.
        """

        inputs = (names, value_arrays, units)

        # ensure consistent length and datatype of input arrays
        input_length_set = set([len(input) for input in inputs])
        input_length_set.discard(0)
        assert len(input_length_set) == 1, 'IndependentVariableCollection Error: The length of input lists must be identical.'
        assert set([type(input) for input in inputs]).issubset(set([np.ndarray, list])), 'IndependentVariableCollection Error: Inputs must be lists or np.ndarrays.'

        # ensure value_arrays contains elements of the correct datatype
        for value_array in value_arrays:
            assert type(value_array) == list or type(value_array) == np.ndarray, "IndependentVariableCollection Error: Elements within value_arrays must be lists or np.ndarrays."
            assert set([isinstance(value, Number) for value in value_array]) == set([True]), "IndependentVariableCollection Error: Numeric data is required for value_arrays."

    @staticmethod
    def _to_list(array: Union[list, np.ndarray]):
        """ 
        Function for converting array inputs to lists.
        """

        if type(array) == np.ndarray:
            array = array.tolist()
        elif type(array) == list:
            array = [i.tolist() if type(i) == np.ndarray else i for i in array]

        return array

    def get_names(self):
        return self.names
    
    def get_value_arrays(self):
        return self.value_arrays
    
    def get_units(self):
        return self.units

class ParameterCollection:
    def __init__(
            self, 
            names: 
            Union[list, np.ndarray], 
            initial_values: Union[list, np.ndarray], 
            lower_bounds: Union[list, np.ndarray], 
            upper_bounds: Union[list, np.ndarray], 
            units: Union[list, np.ndarray]=[]):
        """
        A utility class for organizing data associated with model parameters.
        """

        ParameterCollection._parse_inputs(names, initial_values, lower_bounds, upper_bounds, units)
        self.names = ParameterCollection._to_list(names)
        self.initial_values = ParameterCollection._to_list(initial_values)
        self.lower_bounds = ParameterCollection._to_list(lower_bounds)
        self.upper_bounds = ParameterCollection._to_list(upper_bounds)
        units = units if len(units) > 0 else [None] * len(names)
        self.units = ParameterCollection._to_list(units)

    @staticmethod
    def _parse_inputs(names, initial_values, lower_bounds, upper_bounds, units):
        """ 
        Private static method for ensuring input parameters satisfy assumptions of the program.
        """

        inputs = (names, initial_values, lower_bounds, upper_bounds, units)

        # ensure consistent length and datatype of input arrays
        input_length_set = set([len(input) for input in inputs])
        input_length_set.discard(0)
        assert len(input_length_set) == 1, 'ParameterCollection Error: The length of input lists must be identical.'
        assert set([type(input) for input in inputs]).issubset(set([np.ndarray, list])), 'ParameterCollection Error: Inputs must be lists or np.ndarrays.'

        assert set([isinstance(value, Number) for value in initial_values]) == set([True]), "ParameterCollection Error: Numeric data is required for initial_values."
        assert set([isinstance(value, Number) for value in lower_bounds]) == set([True]), "ParameterCollection Error: Numeric data is required for lower_bounds."
        assert set([isinstance(value, Number) for value in upper_bounds]) == set([True]), "ParameterCollection Error: Numeric data is required for upper_bounds."

    @staticmethod
    def _to_list(array: Union[list, np.ndarray]):
        """ 
        Function for converting array inputs to lists.
        """

        if type(array) == np.ndarray:
            array = array.tolist()
        return array

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
            parameter_collection: ParameterCollection,
            model_units:str = None
            ):
        
        Model._parse_inputs(model, independent_variable_collection, parameter_collection)
        
        self.model = model
        self.model_name = model_name
        self.model_units = model_units
        self.independent_variable_collection = independent_variable_collection
        self.parameter_collection = parameter_collection
        self.slider_data = self._generate_slider_data()

        # private dictionaries to map parameter names to values or value arrays
        self._independent_variable_dictionary = dict([(argname, value_range) for argname, value_range in zip(self.independent_variable_collection.get_names(), self.independent_variable_collection.get_value_arrays())])
        self._parameter_dictionary = dict([(argname, argvalue) for argname, argvalue in zip(self.parameter_collection.get_names(), self.parameter_collection.get_initial_values())])
        self._argument_dictionary = dict(
            **self._independent_variable_dictionary, 
            **self._parameter_dictionary)
        
    def _parse_inputs(model, independent_variable_collection, parameter_collection):

        # parse function signature of the model to ensure consistency with collections
        signature = inspect.signature(model)
        arguments = list(signature.parameters.keys())
        assert len(arguments) == len(independent_variable_collection.get_names()) + len(parameter_collection.get_names()), 'Model Error: '
        assert set(arguments) == set(independent_variable_collection.get_names()).union(set(parameter_collection.get_names())), 'Model Error: '

        assert type(independent_variable_collection) == IndependentVariableCollection, 'Model Error: independent_variable_collection must be an instance of the IndependentVariableCollection class.'
        assert type(parameter_collection) == ParameterCollection, 'Model Error: parameter_collection must be an instance of the ParameterCollection class.'

    def _generate_slider_data(self):

        NO_STEPS = 100 # default number of steps
        SCALE = 'linear' # default slider scale

        slider_datas = []
        for name, initial_value, lower_bound, upper_bound, unit in zip(
            self.parameter_collection.get_names(),
            self.parameter_collection.get_initial_values(),
            self.parameter_collection.get_lower_bounds(),
            self.parameter_collection.get_upper_bounds(),
            self.parameter_collection.get_units()
        ):
            stepsize = (upper_bound - lower_bound) / (NO_STEPS - 1)
            slider_datas.append(
                {
                    'name': name,
                    'initial_value': initial_value,
                    'min': lower_bound,
                    'max': upper_bound,
                    'scale': SCALE,
                    'stepsize': stepsize
                }
            )

        return slider_datas
        
    def evaluate(self):
        """ 
        Evaluates the model with set independent variables and parameters.
        """
        return self.model(**self._argument_dictionary)
    
    def update_parameter(self, param_name: str, new_value: float):
        self._parameter_dictionary[param_name] = new_value
        self._argument_dictionary = dict(**self._independent_variable_dictionary, **self._parameter_dictionary)