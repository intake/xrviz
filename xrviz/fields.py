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
        self.agg_opts = ['Select', 'Animate', 'mean', 'max',
                         'min', 'median', 'std', 'count']

        self._register(self.x, 'x')
        self._register(self.y, 'y')

        self.connect('x', self.change_y)
        self.connect('y', self.change_dim_selectors)

        self.panel = pn.Row(pn.Column('### Plot Dimensions',
                                      self.x, self.y,
                                      background='rgb(175,175,175)'),
                            pn.Column('### Aggregations',
                                      self.agg_selectors,
                                      background='rgb(175,175,175)'),
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

        if self.is_dataset:
            if isinstance(var, str):
                self.var = var
            else:
                self.var = var[0]
            self.var_dims = list(self.data[var].dims)
            self.indexed_coords = set(self.var_dims) & set(self.data[var].coords)
            self.non_indexed_coords = list(set(self.data[var].coords) - self.indexed_coords)
            self.sel_options = self.var_dims + self.non_indexed_coords
        else:
            #  DataArray will only have dims in options
            self.sel_options = list(self.data.dims)

        # #  dims_aggs: for ex {'dim1':'Select','dim2':'Select'}
        # self.dims_aggs = dict(zip(self.var_dims, ['Select']*len(self.var_dims)))

        x_opts = self.sel_options.copy()
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
                self.change_y()
                # self.change_dim_selectors()

    def change_y(self, value=None):
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
        if isinstance(self.data, xr.Dataset):
            if x_val in self.var_dims:
                valid_values = list(set(values) - set(self.non_indexed_coords))
            else:  # x_val belong to non_indexed_coords
                values = list(set(values) - set(self.var_dims))
                #  Plot can be generated for 2 values only if ndims of both match
                valid_values = [val for val in values if self.ndim_matches(x_val, val)]
            self.y.options = valid_values
        else:
            self.y.options = values
        self.change_dim_selectors()

    def change_dim_selectors(self, *args):
        self.agg_selectors.clear()
        used_opts = [self.x.value, self.y.value]
        if self.is_dataset:
            if self.x.value in self.var_dims:
                self.remaining_dims = [dim for dim in self.var_dims if dim not in used_opts]
            else: # is a coord
                self.remaining_dims = []
        else:
            self.remaining_dims = [dim for dim in self.sel_options if dim not in used_opts]
        for dim in self.remaining_dims:
            agg_selector = pn.widgets.Select(name=dim,
                                             options=self.agg_opts,
                                             width=200,)
            self.agg_selectors.append(agg_selector)

    @property
    def kwargs(self):
        # Row(name='Fields')
        #     [0] Column(background='rgb(175,175,175)')
        #         [0] Markdown(str)     --> self.panel[0][0]
        #         [1] Select(name='x',) --> self.panel[0][1]
        #         [2] Select(name='y',) --> self.panel[0][2]
        #     [1] Column(background='rgb(175,175,175)')
        #         [0] Markdown(str)     --> self.panel[1][0]
        #         [1] Column            --> self.panel[1][1]
        #             [0] Select()
        #             [1] Select()
        out = {p.name: p.value for p in self.panel[0][1:]} #since panel[0][0] is Markdown
        selectors = {p.name: p.value for p in self.panel[1][1]}
        out.update(selectors)
        dims_to_agg = [dim for dim, agg in selectors.items() if agg not in ['Select', 'Animate']]
        out.update({'dims_to_agg': dims_to_agg})
        return out

    def set_coords(self, data, var):
        self.data = data
        if var:
            self.setup(var)

    def ndim_matches(self, var1, var2):
        return self.data[var1].ndim == self.data[var2].ndim
