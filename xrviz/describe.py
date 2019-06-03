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

        if isinstance(self.data, xr.DataArray):
            self.panel.object = self.panel.object = self.variable_pane_for_dataarray()

    def variable_pane_for_dataset(self, var):
        if var is not None:
            var_attrs = [(k, v) for k, v in self.data[var].attrs.items()]
            var_coords = [coord for coord in self.data[var].coords]
            var_dims = self.data[var].dims
            var_dtype = str(self.data[var].dtype)
            var_name = self.data[var].name
            var_nbytes = self.data[var].nbytes
            var_shape = self.data[var].shape
            var_size = self.data[var].size

            return self._variable_template.render(var=var,
                                                  var_attrs=var_attrs,
                                                  var_coords=var_coords,
                                                  var_dims=var_dims,
                                                  var_dtype=var_dtype,
                                                  var_name=var_name,
                                                  var_nbytes=var_nbytes,
                                                  var_shape=var_shape,
                                                  var_size=var_size,
                                                  )
        else:
            return self._variable_template.render(var=None)

    def variable_pane_for_dataarray(self):
        var_attrs = [(k, v) for k, v in self.data.attrs.items()]
        var_coords = [coord for coord in self.data.coords]
        var_dims = self.data.dims
        var_dtype = str(self.data.dtype)
        var_name = self.data.name
        var_nbytes = self.data.nbytes
        var_shape = self.data.shape
        var_size = self.data.size

        return self._variable_template.render(var='var',  # to check condition in template
                                              var_attrs=var_attrs,
                                              var_coords=var_coords,
                                              var_dims=var_dims,
                                              var_dtype=var_dtype,
                                              var_name=var_name,
                                              var_nbytes=var_nbytes,
                                              var_shape=var_shape,
                                              var_size=var_size,
                                              )

    def attribute_pane(self):
        attrs = [(k, v) for k, v in self.data.attrs.items()]
        return self._attribute_template.render(attrs=attrs)

    def coordinate_pane(self, coord):
        if coord is not None:
            coord_info = self.data.coords.get(coord)
            coord_attrs = [(k, v) for k, v in coord_info.attrs.items()]
            coord_dtype = str(coord_info.encoding.get('dtype'))
            coord_name = coord_info.name
            coord_nbytes = coord_info.nbytes
            coord_shape = coord_info.shape
            coord_size = coord_info.size
            coord_units = coord_info.encoding.get('units')

            return self._coordinate_template.render(coord=coord,
                                                    coord_attrs=coord_attrs,
                                                    coord_dtype=coord_dtype,
                                                    coord_info=coord_info,
                                                    coord_name=coord_name,
                                                    coord_nbytes=coord_nbytes,
                                                    coord_shape=coord_shape,
                                                    coord_size=coord_size,
                                                    coord_units=coord_units,
                                                    )
        else:
            return self._coordinate_template.render(coord=None)

    def dimension_pane(self):
        dims = [(k, v) for k, v in self.data.dims.items()]
        return self._dimension_template.render(dims=dims)

    def setup(self, selected_property, sub_property):
        if selected_property == 'Attributes':
            self.panel.object = self.attribute_pane()
        elif selected_property == 'Coordinates':
            self.panel.object = self.coordinate_pane(sub_property)
        elif selected_property == 'Dimensions':
            self.panel.object = self.dimension_pane()
        elif selected_property == 'Variables':
            if isinstance(self.data, xr.Dataset):
                self.panel.object = self.variable_pane_for_dataset(sub_property)
        else:
            self.panel.object = str(selected_property)
