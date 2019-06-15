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
        if isinstance(self.data, xr.Dataset):
            self.var = var[0]
            self.var_dims = list(self.data[var].dims)
        else:
            self.var_dims = list(self.data.dims)
        x_opts = self.var_dims.copy()
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
        values = self.var_dims.copy()
        values.remove(self.x.value)
        self.y.options = values

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel[0]}
        return out
