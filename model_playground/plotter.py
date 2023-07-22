import plotly.graph_objects as go
from ipywidgets import VBox, widgets

class Plotter:
    def __init__(self, model, sliders: list):
        self.model = model
        self.sliders = self._process_sliders(sliders)
        self.figure = self._initialize_figure2D()

    def _initialize_figure2D(self):

        # check to make sure independent variables are defined
        undefined_variables = []
        for independent_variable in self.model.independent_variable_names:
            value = self.model.argument_dictionary[independent_variable]
            if type(value) != np.ndarray:
                undefined_variables.append(independent_variable)
        if len(undefined_variables) > 0:
            print('model-playground: Undefined independent variables detected. Please define the independent variable space using the "define_independent_variables" method.')
            return

        # obtain figure data
        # TODO: add support for three dimensional plots
        dependent_variable = self.model.model(**self.model.argument_dictionary)
        data = [
            dict(
            type='scatter',
            x=self.model.argument_dictionary[self.model.independent_variable_names[0]],
            y=dependent_variable,
            name=self.model.dependent_variable_name
            )
        ]

        figure = go.FigureWidget(data=data)
        figure.layout.title = 'Model'
        figure.layout.xaxis.title = self.model.independent_variable_names[0]
        figure.layout.yaxis.title = self.model.dependent_variable_name
        return figure
        
    def _process_sliders(self, sliders):

        slider_list = []
        for slider_object in sliders:
            param_name = slider_object.name
            default_value = self.model.argument_dictionary[param_name]

            def slider_update(new_value):
                new_value = new_value['new']
                self.model._update_argument_dictionary(param_name, new_value['value'])
                dependent_variable = self.model.model(**self.model.argument_dictionary)
                self.figure.data[0].y = dependent_variable

            if type(slider_object) == LinearSlider:
                slider = widgets.FloatSlider(
                    value=default_value,
                    min=slider_object.min,
                    max=slider_object.max,
                    step=slider_object.stepsize,
                    continuous_update=True,
                    description=slider_object.name
                )
            elif type(slider_object) == LogSlider:
                slider = widgets.FloatLogSlider(
                    value=default_value,
                    min=slider_object.min,
                    max=slider_object.max,
                    step=slider_object.stepsize,
                    continuous_update=True,
                    description=slider_object.name
                )
            
            slider.observe(slider_update)
            slider_list.append(slider)
        return slider_list

    def plot(self):
        return VBox([self.figure] + self.sliders)

class LinearSlider:
    """
    Utility class for organizing linear slider data.

    name: str
        The name of the slider.
    min: float
        Minimum value for slider. 
    max: float
        Maximum value for slider. 
    stepsize: float
        Slider stepsize. 
    """

    def __init__(self, name: str, min: float, max: float, stepsize: float):
        self.name, self.min, self.max, self.stepsize = name, min, max, stepsize

class LogSlider(LinearSlider):
    """
    Utility class for organizing log slider data.

    Attributes
    ----------
    name: str
        The name of the slider.
    min: float
        Minimum value of the exponent.
    max: float
        Maximum value of the exponent.
    stepsize: float
        Exponent stepsize.
    base: float
        The base of the exponential.
    """
    def __init__(self, name: str, min: float, max: float, stepsize: float, base: float):
        super().__init__(name, min, max, stepsize)
        self.base = base
        