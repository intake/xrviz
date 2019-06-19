import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .utils import convert_widget


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
        self.set_data(data)
        self.x = pn.widgets.Select(name='x', width=200)
        self.y = pn.widgets.Select(name='y', width=200)
        self.agg_selectors = pn.Column()
        self.agg_opts = ['None', 'mean', 'max',
                         'min', 'median',
                         'std', 'count']

        self.agg_graph = pn.Row(pn.Spacer(name='Agg Graph'))

        self._register(self.x, 'x')
        self._register(self.y, 'y')

        self.connect('x', self.change_y)
        self.connect('y', self.change_dim_selectors)

        self.panel = pn.Row(pn.Column(self.x, self.y),
                            pn.Column(self.agg_selectors,
                                      pn.Spacer(name='agg_plot_button')),
                            name='Fields',)

        if not self.is_dataset:
            self.setup(data)

    def set_data(self, data):
        if isinstance(data, xr.Dataset):
            self.data = data
            self.is_dataset = True
        else:
            self.data = data
            self.is_dataset = False

    def setup(self, var):
        self.agg_selectors.clear()  # To empty previouly selected value from selector
        self.agg_graph[0] = pn.Spacer(name='Agg Graph')  # To clear Agg Graph upon selection of new variable

        if self.is_dataset:
            if isinstance(var, str):
                self.var = var
            else:
                self.var = var[0]
            self.var_dims = list(self.data[var].dims)
        else:
            self.var_dims = list(self.data.dims)
        #  dims_aggs: for ex {'dim1':'None','dim2':'None'}
        self.dims_aggs = dict(zip(self.var_dims, ['None']*len(self.var_dims)))

        x_opts = self.var_dims.copy()
        if len(x_opts) > 0:  # to check that data has dim (is not Empty)
            self.x.options = x_opts
            self.x.value = x_opts[0]
            y_opts = x_opts.copy()
            del y_opts[0]
            if y_opts is None:
                self.y.options = []
                self.remaining_dims = []
            else:
                self.y.options = y_opts
                self.remaining_dims = [opt for opt in y_opts if opt!=self.y.value]
        self.change_dim_selectors()

    def change_y(self, value):
        """
        Updates the options of y, by removing option selected in x (value),
        from all the variable dimensions available as options.
        """
        values = self.var_dims.copy()
        values.remove(self.x.value)
        self.y.options = values
        self.change_dim_selectors()

    def change_dim_selectors(self, *args):
        self.agg_selectors.clear()
        used_opts = [self.x.value, self.y.value]
        self.remaining_dims = [dim for dim in self.var_dims if dim not in used_opts]
        for dim in self.remaining_dims:
            agg_selector = pn.widgets.Select(name=dim,
                                             options=self.agg_opts,
                                             width=100,)
            self.agg_selectors.append(agg_selector)

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel[0]}
        selectors = {p.name: p.value for p in self.panel[1][0]}
        out.update(selectors)
        dims_to_agg = [dim for dim, agg in selectors.items() if agg is not 'None']
        out.update({'dims_to_agg': dims_to_agg})
        return out
