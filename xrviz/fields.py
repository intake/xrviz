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
        self.dims_selector = pn.widgets.MultiSelect(size=8, min_width=150,
                                                    height=110,
                                                    width_policy='min',
                                                    name='Aggregate along')
        self.agg_plot = pn.widgets.Button(name='Aggregate',
                                          width=150,
                                          disabled=True)

        self._register(self.x, 'x')
        self._register(self.dims_selector, 'agg_dims')
        self._register(self.agg_plot, 'agg_plot', 'clicks')

        self.connect('x', self.change_y)
        self.connect('agg_dims', self.setup_agg_button)
        self.connect('agg_plot', self.create_agg_plot)

        self.panel = pn.Row(pn.Column(self.x, self.y),
                            # pn.Spacer(width=200),
                            pn.Column(self.dims_selector,
                                      self.agg_plot,),
                            pn.Spacer(name='Graph'),
                            name='Fields',)

        if isinstance(data, xr.DataArray):
            self.setup(data)

    def setup(self, var):
        self.dims_selector.value = []  # To empty previouly selected value from selector
        self.dims_selected_for_agg = []
        self.agg_plot.disabled = True
        if isinstance(self.data, xr.Dataset):
            self.var = var[0]
            self.var_dims = list(self.data[var].dims)
        else:
            self.var_dims = list(self.data.dims)

        self.dims_selector.options = self.var_dims
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

    def setup_agg_button(self, selected_dims):
        self.dims_selected_for_agg = selected_dims
        self.agg_plot.disabled = True
        # We need atleast 1 and at max (dims-1) selections to aggregate
        # So this button would be enbled when this condition is satisfied.
        if len(selected_dims) == 1 or len(selected_dims) < len(self.dims_selector.options):
            self.agg_plot.disabled = False

    def change_y(self, value):
        """
        Updates the options of y, by removing option selected in x (value),
        from all the variable dimensions available as options.
        """
        values = self.var_dims.copy()
        values.remove(self.x.value)
        self.y.options = values

    def create_agg_plot(self, *args):
        remaining_dims = [dim for dim in self.var_dims if dim not in self.dims_selected_for_agg]
        assign_opts = {dim: self.data[dim] for dim in remaining_dims}
        sel = self.data[self.var].mean(self.dims_selected_for_agg)
        sel = sel.assign_coords(**assign_opts)

        # for 1d sel we have simple hvplot
        # for 2d or 3d we will have quadmesh
        if len(sel.shape) == 1:
            self.panel[-1] = sel.hvplot()
        else:
            self.panel[-1] = sel.hvplot.quadmesh()

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel[0]}
        return out
