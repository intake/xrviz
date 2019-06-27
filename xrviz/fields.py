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
        self.data = data
        self.x = pn.widgets.Select(name='x', width=200)
        self.y = pn.widgets.Select(name='y', width=200)
        self.agg_selectors = pn.Column()
        self.agg_opts = ['select', 'animate', 'mean', 'max',
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
                            name='Axes',)

    def setup(self, var):
        self.agg_selectors.clear()  # To empty previouly selected value from selector
        self.var = var if isinstance(var, str) else var[0]
        self.var_dims = list(self.data[var].dims)
        self.indexed_coords = set(self.var_dims).intersection(set(self.data[var].coords))
        self.non_indexed_coords = set(self.data[var].coords) - self.indexed_coords
        self.sel_options = sorted(self.var_dims + list(self.non_indexed_coords))

        x_opts = self.sel_options.copy()
        if len(x_opts):  # to check that data has dim (is not Empty)
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

        if x_val in self.var_dims:
            valid_values = set(values) - self.non_indexed_coords
        else:  # x_val belong to non_indexed_coords
            values = set(values) - set(self.var_dims)
            #  Plot can be generated for 2 values only if ndims of both match
            valid_values = [val for val in values if self.ndim_matches(x_val, val)]
        self.y.options = sorted(list(valid_values))

        self.change_dim_selectors()

    def change_dim_selectors(self, *args):
        self.agg_selectors.clear()
        used_opts = [self.x.value, self.y.value]

        if self.x.value in self.var_dims:
            self.remaining_dims = [dim for dim in self.var_dims if dim not in used_opts]
        else:  # is a coord
            #  We can't aggregate along dims which are present in x and y.
            dims_not_to_agg = set(self.data[self.x.value].dims).union(set(self.data[self.y.value].dims)).union(set(used_opts))
            self.remaining_dims = [dim for dim in self.var_dims if dim not in dims_not_to_agg]

        for dim in sorted(self.remaining_dims):
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
        out = {p.name: p.value for p in self.panel[0][1:]}  # since panel[0][0] is Markdown
        selectors = {p.name: p.value for p in self.panel[1][1]}
        out.update(selectors)
        dims_to_select_animate = [dim for dim, agg in selectors.items() if agg in ['select', 'animate']]
        dims_to_agg = [dim for dim in selectors if dim not in dims_to_select_animate]
        out.update({'dims_to_agg': dims_to_agg})
        out.update({'dims_to_select_animate': sorted(dims_to_select_animate)})
        return out

    def set_coords(self, data, var):
        self.data = data
        if var:
            self.setup(var)

    def ndim_matches(self, var1, var2):
        return self.data[var1].ndim == self.data[var2].ndim
