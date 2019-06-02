from jinja2 import Environment, FileSystemLoader
import panel as pn
import os
import sys
import xarray as xr
from .sigslot import SigSlot


class Describe(SigSlot):
    """
    This section describes the property selected in the Display section.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
        datset is used to initialize the DataSelector

    Attributes
    ----------
    panel: Displays the generated template

    """
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.panel = pn.pane.HTML(style={'font-size': '12pt'}, width=400,
                                  height=100)
        self.panel.object = "Description Area"
        self._template_load_path = os.path.join(os.path.dirname(__file__),
                                                "templates")
        self._template_env = Environment(loader=FileSystemLoader(self._template_load_path))
        self._variable_template = self._template_env.get_template('variable.html')
        self._coordinate_template = self._template_env.get_template('coordinate.html')
        self._dimension_template = self._template_env.get_template('dimension.html')
        self._attribute_template = self._template_env.get_template('attribute.html')

    def variable_pane(self, var):
        if var is not None:
            variable_attributes = [(k, v)
                                   for k, v in self.data[var].attrs.items()]
            return self._variable_template.render(variable_attributes=variable_attributes,
                                                  var=var)
        else:
            return self._variable_template.render(var=None)

    def attribute_pane(self):
        attrs = [(k, v) for k, v in self.data.attrs.items()]
        return self._attribute_template.render(attrs=attrs)

    def coordinate_pane(self):
        coords = [coord for coord in self.data.coords.keys()]
        return self._coordinate_template.render(coords=coords)

    def dimension_pane(self):
        dims = [(k, v) for k, v in self.data.dims.items()]
        return self._dimension_template.render(dims=dims)

    def setup(self, selected_property, sub_property):
        if selected_property == 'Attributes':
            self.panel.object = self.attribute_pane()
        elif selected_property == 'Coordinates':
            self.panel.object = self.coordinate_pane()
        elif selected_property == 'Dimensions':
            self.panel.object = self.dimension_pane()               
        elif selected_property == 'Variables':
            self.panel.object = self.variable_pane(sub_property)
        else:
            self.panel.object = str(selected_property) + " : " + str(sub_property)
