from jinja2 import Environment, FileSystemLoader
import panel as pn
import os
import sys
import xarray as xr
from .sigslot import SigSlot


class Describe(SigSlot):
    """
    Displays the properties of the variable selected in the Display section.

    This section has two tables as output. The first table shows
    `Variable attributes` and the second table shows `Global Attributes`.
    Upon selection of a new variable in the Display widget, the first table
    updates itself with properties of the new selection,
    while the second table stays same.

    Parameters
    ----------

    data: xarray.DataSet

    Attributes
    ----------

    panel:
        A ``panel.pane.HTML`` instance which displays the tables arranged
        next to each other.

    """
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.panel = pn.pane.HTML(
            style={'font-size': '12pt'}, min_width=800, height=100) 
        self.panel.object = "Description Section"
        self._template_load_path = os.path.join(os.path.dirname(__file__),
                                                "templates")
        self._template_env = Environment(loader=FileSystemLoader(self._template_load_path))
        self._variable_template = self._template_env.get_template('variable.html')

    def setup(self, var):
        self.panel.object = self.variable_pane_for_dataset(var)

    def variable_pane_for_dataset(self, var):
        """
        Returns HTML template describing variable and global attributes.
        """
        if var is not None:
            var = var if isinstance(var, str) else var[0]
            var_attrs = [(k, v) for k, v in self.data[var].attrs.items()]
            var_coords = [coord for coord in self.data[var].coords]
            var_dims = self.data[var].dims
            var_dtype = str(self.data[var].dtype)
            var_name = self.data[var].name
            var_nbytes = self.data[var].nbytes
            var_shape = self.data[var].shape
            var_size = self.data[var].size
            var_dim_shape = [(dim, shape) for dim, shape in zip(var_dims, var_shape)]
            data_attrs = [(k, v) for k, v in self.data.attrs.items()]
            data_coords = [coord for coord in self.data.coords.keys()]
            data_dims = [(k, v) for k, v in self.data.dims.items()]

            return self._variable_template.render(data_attrs=data_attrs,
                                                  data_coords=data_coords,
                                                  data_dims=data_dims,
                                                  var=var,
                                                  var_attrs=var_attrs,
                                                  var_coords=var_coords,
                                                  var_dim_shape=var_dim_shape,
                                                  var_dtype=var_dtype,
                                                  var_name=var_name,
                                                  var_nbytes=var_nbytes,
                                                  var_size=var_size,
                                                  )
        else:
            return self._variable_template.render(var=None)

    def set_coords(self, data, var):
        self.data = data
        if var is not None:
            self.setup(var=[var])
