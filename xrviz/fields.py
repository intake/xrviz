import panel as pn
import xarray as xr
from .sigslot import SigSlot


class Fields(SigSlot):
    """
    This section provides the user with a fields selection panel.
    Upon selection of a variable in `Display` panel, its dimensions
    are available as options in `x` and `y` Select widget.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
           datset is used to initialize.

    Attributes
    ----------
    x: `panel.widget.Select` for selection of dims along x-axis.
    y: `panel.widget.Select` for selection of dims along y-axis.
    kwargs: provides access to dims selected by `x` and `y`.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.x = pn.widgets.Select(name='x')
        self.y = pn.widgets.Select(name='y')

        self._register(self.x, 'x')

        self.connect('x', self.change_y)

        self.panel = pn.Row(pn.Column(self.x, self.y),
                            pn.Spacer(width=200),
                            name='Fields',)

        if isinstance(data, xr.DataArray):
            self.setup(data)

    def setup(self, var):
        #  For a variable Union of `dims` and `non_indexed_coords`
        #  will act as options in `x` Select, here called `sel_options`
        if isinstance(self.data, xr.Dataset):
            self.var = var[0]
            self.var_dims = list(self.data[var].dims)
            self.indexed_coords = set(self.var_dims) & set(self.data[var].coords)
            self.non_indexed_coords = list(set(self.data[var].coords) - self.indexed_coords)
            self.sel_options = self.var_dims + self.non_indexed_coords
        else:
            #  DataArray will only have dims in options
            self.sel_options = list(self.data.dims)
        x_opts = self.sel_options.copy()
        if len(x_opts) > 0:  # to check that data has dim (is not Empty)
            self.x.options = x_opts
            self.x.value = x_opts[0]
            y_opts = x_opts.copy()
            del y_opts[0]
            if y_opts is None:
                self.y.options = []
            else:
                self.y.options = y_opts

    def change_y(self, value):
        """
        Updates the options of y, by removing option selected in x (value),
        from all the variable dimensions available as options.
        """
        # if x belong to var_dims replace the y with remaining var_dims
        # else if x belong to non_indexed_coords, replace y with remaining
        # non_indexed_coords
        values = self.sel_options.copy()
        x_val = self.x.value
        values.remove(x_val)
        if x_val in self.var_dims:
            values = list(set(values) - set(self.non_indexed_coords))
        else:  # x_val belong to non_indexed_coords
            values = list(set(values) - set(self.var_dims))
        self.y.options = values

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel[0]}
        return out

    def set_coords(self, data, var):
        self.data = data
        if var:
            self.setup(var)
        print('Fields:', list(self.data.coords))
