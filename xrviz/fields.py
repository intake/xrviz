import panel as pn
import xarray as xr
import warnings
from .sigslot import SigSlot
from .utils import convert_widget
from .compatibility import mpcalc


class Fields(SigSlot):
    """
    This pane controls which array dimensions should be mapped,
    how additional dimensions should be handled, and which dimension
    series plots should be extracted along.

    Parameters
    ----------
    data: ``xarray.DataSet`` or ``xarray.DataArray``

    Attributes
    ----------
    `x`:
        To select which of the available dimensions/coordinates in the data is assigned to the plot’s x (horizontal) axis.
    `y`:
        To select which of the available dimensions/coordinates in the data is assigned to the plot’s y (vertical) axis.

    `Remaining Dims`:
        Any one of the following aggregations can be applied on each of remaining dimensions:
            1. ``select``: This is the default option. It creates a widget to select the value of dimension, for which the graph would be displayed.
            2. ``animate``: It creates a `player`_ widget which helps to quickly iterate over all the values for a dimension.
            3. ``mean``: To create plot for mean of the values.
            4. ``max``: To create plot for maximum of the values.
            5. ``min``: To create plot for minimum of the values.
            6. ``median``: To create plot for median of the values.
            7. ``std``: To create plot for standard deviation of the values.
            8. ``count``: To create plot for non-nan of the values.

        Note that for both ``select`` and ``animate``, the plot will update according
        to the value selected in the generated widget. Also, if a dimension has been
        aggregated, its select widget would not be available.

    `Extract Along`:
        Series extraction can be done along the remaining dims, which are available
        as options in this select widget.
    
    .. _player: https://panel.pyviz.org/reference/widgets/DiscretePlayer.html
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.x = pn.widgets.Select(name='x', width=200)
        self.y = pn.widgets.Select(name='y', width=200)
        self.agg_selectors = pn.Column()
        self.agg_opts = ['select', 'animate', 'mean', 'max',
                         'min', 'median', 'std', 'count']
        self.series_col = pn.Column()
        self.are_var_coords = False

        self._register(self.x, 'x')
        self._register(self.y, 'y')

        self.connect('x', self.change_y)
        self.connect('y', self.change_dim_selectors)

        self.panel = pn.Column(pn.Row(pn.Column('### Plot Dimensions',
                                                self.x, self.y,
                                                background='rgb(175,175,175)'),
                                      pn.Spacer(),
                                      pn.Column('### Aggregations',
                                                self.agg_selectors,
                                                background='rgb(175,175,175)')),
                               self.series_col,
                               name='Axes')

    def setup(self, var):
        """
        To setup the generated widgets by filling the available options.
        """
        self.agg_selectors.clear()  # To empty previouly selected value from selector
        self.var = var if isinstance(var, str) else var[0]
        self.var_dims = list(self.data[var].dims)
        self.indexed_coords = set(self.var_dims).intersection(set(self.data[var].coords))
        self.non_indexed_coords = set(self.data[var].coords) - self.indexed_coords
        self.sel_options = sorted(self.var_dims + list(self.non_indexed_coords))

        self.x_guess, self.y_guess = self.guess_x_y(self.var) if mpcalc else ['None', 'None']
        x_opts = self.sel_options.copy()
        if len(x_opts):  # to check that data has dim (is not Empty)
            self.x.options = x_opts
            self.x.value = self.x_guess if self.x_guess and self.x_guess in x_opts else x_opts[0]
            y_opts = x_opts.copy()
            del y_opts[0]
            if y_opts is None:
                self.y.options = []
                self.remaining_dims = []
            else:
                self.remaining_dims = [opt for opt in y_opts if opt!=self.y.value]
                self.change_y()

    def change_y(self, value=None):
        """
        Updates the options of `y`, by removing the value of `x`,
        from the available options.
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
        y_opts = sorted(list(valid_values))
        self.y.options = y_opts
        if len(y_opts):
            self.y.value = self.y_guess if self.y_guess and self.y_guess in y_opts else y_opts[0]
        self.are_var_coords = self.check_are_var_coords()
        self.change_dim_selectors()

    def change_dim_selectors(self, *args):
        """
        Updates the dimensions available for `Aggregation` and `Extract Along`,
        upon change in value of `y`.
        """
        self.are_var_coords = self.check_are_var_coords()
        self.agg_selectors.clear()
        self.series_col.clear()
        x = self.x.value
        y = self.y.value
        used_opts = {x, y}

        if x in self.var_dims:
            self.remaining_dims = [dim for dim in self.var_dims if dim not in used_opts]
        else:  # is a coord
            #  We can't aggregate along dims which are present in x and y.
            x_val_dims = set(self.data[x].dims) if x is not None else set()
            y_val_dims = set(self.data[y].dims) if y is not None else set()
            dims_not_to_agg = x_val_dims.union(y_val_dims).union(used_opts)
            self.remaining_dims = [dim for dim in self.var_dims if dim not in dims_not_to_agg]

        for dim in sorted(self.remaining_dims):
            agg_selector = pn.widgets.Select(name=dim,
                                             options=self.agg_opts,
                                             width=200,)
            self._register(agg_selector, agg_selector.name)
            self.agg_selectors.append(agg_selector)

        self.s_selector = pn.widgets.Select(name='extract along',
                                            options=[None]+sorted(self.remaining_dims),
                                            width=200)
        self._register(self.s_selector, 'extract_along')
        self.series_col.append(self.s_selector)

    def setup_initial_values(self, init_params={}):
        for widget in [self.x, self.y] + list(self.agg_selectors) + list(self.series_col):
            if widget.name in init_params:
                widget.value = init_params[widget.name]

    @property
    def kwargs(self):
        # Column(name='Axes')
        #     [0] Row
        #         [0] Column(background='rgb(175,175,175)')
        #             [0] Markdown(str)
        #             [1] Select(name='x', width=200)
        #             [2] Select(name='y', width=200)
        #         [1] Spacer()
        #         [2] Column(background='rgb(175,175,175)')
        #             [0] Markdown(str)
        #             [1] Column()
        #     [1] Column
        #         [0] Select()
        out = {p.name: p.value for p in self.panel[0][0][1:]}  # since panel[0][0][1] is Markdown
        selectors = {p.name: p.value for p in self.panel[0][2][1]}  # remaining_dims
        out.update(selectors)
        dims_to_select_animate = [dim for dim, agg in selectors.items() if agg in ['select', 'animate']]
        dims_to_agg = [dim for dim in selectors if dim not in dims_to_select_animate]
        out.update({'dims_to_agg': dims_to_agg})
        out.update({'dims_to_select_animate': sorted(dims_to_select_animate)})
        out.update({'are_var_coords': self.are_var_coords})
        out.update({'remaining_dims': self.remaining_dims})  # dims_to_agg + dims_to_select_animate
        out.update({p.name: p.value for p in self.series_col})
        return out

    def set_coords(self, data, var):
        self.data = data
        if var:
            self.setup(var)

    def ndim_matches(self, var1, var2):
        return self.data[var1].ndim == self.data[var2].ndim

    def check_are_var_coords(self):
        '''
        Check if both `x` and `y` are coordinates of the selected variable.
        '''
        var_coords = list(self.data[self.var].coords)
        x = self.x.value
        y = self.y.value
        return True if x in var_coords and y in var_coords else False

    def guess_x_y(self, var):
        """
        To guess the value of `x` and `y` with `metpy.parse_cf`_.
        This is applicable only for the case when both `x` and `y` are data
        coordinates.

        .. _`metpy.parse_cf`: https://github.com/Unidata/MetPy/blob/master/metpy/xarray.py#L335
        """
        try:
            parsed_var = self.data.metpy.parse_cf(var)
            x, y = parsed_var.metpy.coordinates('x', 'y')
            return [coord.name for coord in (x, y)]
        except:  # fails when coords have not been set or available.
            return [None, None]
