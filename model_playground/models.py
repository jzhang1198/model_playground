import inspect

class Model:
    def __init__(self, model: function, dependent_variable_name: str):
        independent_variable_names, free_parameter_names, free_parameter_values = Model._process_model_params(model)

        self.model = model
        self.argument_dictionary = {**dict([(argname, None) for argname in independent_variable_names]), **dict([(argname, argvalue) for argname, argvalue in zip(free_parameter_names, free_parameter_values)])}
        self.independent_variable_names = independent_variable_names
        self.free_parameter_names = free_parameter_names
        self.dependent_variable_name = dependent_variable_name

    @staticmethod
    def _process_model_params(model):
        independent_variable_names, free_parameter_names, free_parameter_values = [], [], []
        
        # Extract parameter information
        signature = inspect.signature(model)
        for argname, arg in signature.parameters.items():
            if arg.default is inspect.Parameter.empty:
                independent_variable_names.append(argname)
            else:
                # Parameter has a default value
                free_parameter_names.append(argname)
                free_parameter_values.append(arg.default)
        return independent_variable_names, free_parameter_names, free_parameter_values

    def define_independent_variables(self, variable_name: str, variable_range: np.ndarray):
        if variable_name not in self.independent_variable_names:
            print('model-playground: Provided variable name is not an independent variable.')
            return 
        self.argument_dictionary[variable_name] = variable_range

    def _update_argument_dictionary(self, param_name: str, new_value: float):
        self.argument_dictionary[param_name] = new_value
