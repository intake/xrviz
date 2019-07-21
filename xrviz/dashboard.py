import ast
import panel as pn
import pandas as pd
import numpy as np
import xarray as xr
import hvplot.xarray
import hvplot.pandas
import holoviews as hv
from holoviews import streams
from bokeh.models import HoverTool
import warnings
from itertools import cycle
import numpy
from .sigslot import SigSlot
from .control import Control
from .utils import convert_widget, player_with_name_and_value, is_float
from .compatibility import ccrs, gv, gf, has_cartopy, logger


class Dashboard(SigSlot):
    """
    This section provides access to the complete generated dashboard,
    consisting of all subsections.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
           datset is used to initialize.
    initial_params: To pre-set values of widgets.

    Attributes
    ----------
    panel: Displays the generated dashboard.
    control: Provides access to the generated control panel.
    plot: Plot button, upon click generates graph according to
          kwargs selected in other sub-sections.
    output: Provides access to generated graph.
    """

    def __init__(self, data, initial_params={}):
        super().__init__()
        if not isinstance(data, xr.core.dataarray.DataWithCoords):
            raise ValueError("Input should be an xarray data object, not %s" % type(data))
        self.set_data(data)
        self.initial_params = initial_params
        self.control = Control(self.data)
        self.plot_button = pn.widgets.Button(name='Plot', width=200, disabled=True)
        self.index_selectors = []
        self.graph = pn.Spacer(name='Graph')
        self.taps_graph = hv.Points([])
        self.series_graph = pn.Row(pn.Spacer(name='Series Graph'))
        self.clear_series_button = pn.widgets.Button(name='Clear',
                                                     width=200,
                                                     disabled=True)
        self.output = pn.Row(self.graph,
                             pn.Column(name='Index_selectors'))

        self._register(self.plot_button, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_plot)

        self._register(self.control.coord_setter.coord_selector, 'set_coords')
        self.connect("set_coords", self.set_coords)

        self._register(self.clear_series_button, 'clear_series', 'clicks')
        self.connect('clear_series', self.clear_series)

        self.control.displayer.connect('variable_selected', self.check_is_plottable)
        self.control.displayer.connect('variable_selected', self.link_aggregation_selectors)
        self.control.fields.connect('x', self.link_aggregation_selectors)
        self.control.fields.connect('y', self.link_aggregation_selectors)

        self.panel = pn.Column(self.control.panel,
                               pn.Row(self.plot_button,
                                      self.clear_series_button),
                               self.output,
                               self.series_graph)

        # To auto-select in case of single variable
        if len(list(self.data.variables)) == 1:
            self.control.displayer.select.value = list(self.data.variables)

        self.control.setup_initial_values(self.initial_params)
        self.taps = []
        self.tap_stream = streams.Tap(transient=True)
        colors = ['#60fffc', '#6da252', '#ff60d4', '#ff9400', '#f4e322',
                  '#229cf4', '#af9862', '#629baf', '#7eed5a', '#e29ec8',
                  '#ff4300']
        self.color_pool = cycle(colors)
        self.clear_points = hv.streams.Stream.define('Clear_points', clear=False)(transient=True)

    def clear_series(self, *args):
        if not self.clear_series_button.disabled:
            self.series_graph[0] = pn.Spacer(name='Series Graph')
            self.series = hv.Points([]).opts(height=self.kwargs['height'],
                                             width=self.kwargs['width'])
            self.taps.clear()
            self.clear_points.event(clear=True)

    def link_aggregation_selectors(self, *args):
        """
        To link aggregation selectors with cmap limits
        Whenever any aggregation selector changes it value,
        limits are cleared.
        """
        for dim_selector in self.control.kwargs['remaining_dims']:
            self.control.fields.connect(dim_selector, self.control.style.setup)

    def create_plot(self, *args):
        self.kwargs = self.control.kwargs
        self.var = self.kwargs['Variables']
        if self.index_selectors:
            for selector in self.index_selectors:
                del selector
        self.index_selectors = []
        self.output[1].clear()  # clears Index_selectors
        self.series_graph[0] = pn.Spacer(name='Series Graph')
        self.series = hv.Points([]).opts(height=self.kwargs['height'],
                                         width=self.kwargs['width'])
        self.taps.clear()
        self.control.fields.connect('extract_along', self.clear_series)

        are_var_coords = self.kwargs['are_var_coords']
        if are_var_coords:
            graph_opts = {'x': self.kwargs['x'],
                          'y': self.kwargs['y'],
                          'title': self.var,
                          'height': self.kwargs['height'],
                          'width': self.kwargs['width'],
                          'cmap': self.kwargs['cmap'],
                          'colorbar': self.kwargs['colorbar'],
                          'rasterize': self.kwargs['rasterize']}
            color_scale = self.kwargs['color_scale']
            dims_to_agg = self.kwargs['dims_to_agg']
            use_all_data = self.kwargs['compute min/max from all data']
            sel_data = self.data[self.var]

            if has_cartopy:
                is_geo = self.kwargs['is_geo']
                base_map = self.kwargs['basemap']
                show_map = True if base_map != None else False

                if is_geo:
                    crs_params = self.kwargs['crs params']
                    crs_params = process_proj_params(crs_params)
                    crs = getattr(ccrs, self.kwargs['crs'])(**crs_params)
                    geo_ops = {'alpha': self.kwargs['alpha'],
                               'project': self.kwargs['project'],
                               'global_extent': self.kwargs['global_extent'],
                               'geo': True,
                               'crs': crs}
                    if not show_map:
                        # find projection and crs, add it to geo_ops
                        proj_val = self.kwargs['projection']
                        if proj_val:
                            proj_params = self.kwargs['projection params']
                            proj_params = process_proj_params(proj_params)
                            projection = getattr(ccrs, self.kwargs['projection'])(**proj_params)
                            geo_ops.update({'projection': projection})

                    graph_opts.update(geo_ops)

                    feature_map = gv.Overlay([getattr(gf, feat) for feat in self.kwargs['features'] if feat is not 'None'])

            for dim in dims_to_agg:
                if self.kwargs[dim] == 'count':
                    sel_data = (~ sel_data.isnull()).sum(dim)
                else:
                    agg = self.kwargs[dim]
                    sel_data = getattr(sel_data, agg)(dim)

            if self.var in list(sel_data.coords):  # When a var(coord) is plotted wrt itself
                sel_data = sel_data.to_dataset(name=f'{sel_data.name}_')

            if color_scale is not 'linear':
                sel_data = getattr(numpy, color_scale)(sel_data)  # Color Scaling

            if not use_all_data:
                # sel the values at first step, to use for cmap limits
                sels = {dim: 0 for dim in self.kwargs['dims_to_select_animate']}
                sel_data_for_cmap = sel_data.isel(**sels, drop=True)
            else:
                sel_data_for_cmap = sel_data

            cmin, cmax = self.kwargs['cmap lower limit'], self.kwargs['cmap upper limit']
            cmin, cmax = (cmin, cmax) if is_float(cmin) and is_float(cmax) else ('', '')

            # It is better to set initial values as 0.1,0.9 rather than 0,1(min, max)
            # to get a color balance graph
            c_lim_lower, c_lim_upper = (float(cmin), float(cmax)) if cmin and cmax else ([q for q in sel_data_for_cmap.quantile([0.1, 0.9])])

            color_range = {sel_data.name: (c_lim_lower, c_lim_upper)}

            if not cmin:  # if user left blank or initial values are empty
                self.control.style.lower_limit.value = str(c_lim_lower.values.round(5))
                self.control.style.upper_limit.value = str(c_lim_upper.values.round(5))

            assign_opts = {dim: self.data[dim] for dim in sel_data.dims}
            # Following tasks are happening here:
            # 1. assign_opts: reassignment of coords(if not done result in errors for some of the selections in fields panel)
            # 2. graph_opts: customise the plot according to selections in style and projection(if available)
            # 3. color_range: customise the colormap range according to cmap lower and upper limits
            # 4. active_tools: activate the tools required such as 'wheel_zoom', 'pan'
            graph = sel_data.assign_coords(**assign_opts).hvplot.quadmesh(**graph_opts).redim.range(**color_range).opts(active_tools=['wheel_zoom', 'pan'])

            self.tap_stream.source = graph

            if has_cartopy and is_geo:
                graph = feature_map * graph if self.kwargs['features'] != ['None'] else graph
                if show_map:
                    graph = base_map * graph
                    self.tap_stream.source = graph

            self.create_selectors_players(graph)

        else:  # if one or both x,y are var_dims
            self.var_dims = list(self.data[self.var].dims)
            #  var_selector_dims refers to dims for which index_selectors would be created
            self.var_selector_dims = self.kwargs['dims_to_select_animate']

            for dim in self.var_selector_dims:
                ops = list(self.data[self.var][dim].values)

                if self.kwargs[dim] == 'select':
                    selector = pn.widgets.Select(name=dim, options=ops)
                else:
                    selector = pn.widgets.DiscretePlayer(name=dim, value=ops[0], options=ops)
                self.index_selectors.append(selector)
                self._register(selector, selector.name)
                self.connect(selector.name, self.create_indexed_graph )

            self.create_indexed_graph()
            for selector in self.index_selectors:
                if isinstance(selector, pn.widgets.Select):
                    self.output[1].append(selector)
                else:
                    player = player_with_name_and_value(selector)
                    self.output[1].append(player)

    def create_indexed_graph(self, *args):
        """
        Creates graph for  selected indexes in selectors or players.
        """
        selection = {}  # to collect the value of index selectors
        for i, dim in enumerate(list(self.var_selector_dims)):
            selection[dim] = self.index_selectors[i].value
        graph_opts = {'x': self.kwargs['x'],
                      'y': self.kwargs['y'],
                      'title': self.var,
                      'height': self.kwargs['height'],
                      'width': self.kwargs['width'],
                      'cmap': self.kwargs['cmap'],
                      'colorbar': self.kwargs['colorbar'],
                      'rasterize': self.kwargs['rasterize']}
        dims_to_agg = self.kwargs['dims_to_agg']
        color_scale = self.kwargs['color_scale']
        use_all_data = self.kwargs['compute min/max from all data']

        sel_data = self.data[self.var]

        for dim in dims_to_agg:
            if self.kwargs[dim] == 'count':
                sel_data = (~ sel_data.isnull()).sum(dim)
            else:
                agg = self.kwargs[dim]
                sel_data = getattr(sel_data, agg)(dim)

        # rename the sel_data in case it is a coordinate, because we
        # cannot create a Dataset from a DataArray with the same name
        #  as one of its coordinates
        if sel_data.name in self.data.coords:
                sel_data = sel_data.to_dataset(name=f'{sel_data.name}_')

        if not use_all_data:  # do the selection earlier
            sel_data = sel_data.sel(**selection, drop=True)

        if color_scale is not 'linear':
            sel_data = getattr(numpy, color_scale)(sel_data)  # Color Scaling

        cmin, cmax = self.kwargs['cmap lower limit'], self.kwargs['cmap upper limit']
        cmin, cmax = (cmin, cmax) if is_float(cmin) and is_float(cmax) else ('', '')

        # It is better to set initial values as 0.1,0.9 rather than 0,1(min, max)
        # to get a color balance graph
        c_lim_lower, c_lim_upper = (float(cmin), float(cmax)) if cmin and cmax else ([q for q in sel_data.quantile([0.1, 0.9])])

        color_range = {sel_data.name: (c_lim_lower, c_lim_upper)}

        if not cmin:  # if user left blank or initial values are empty
            self.control.style.lower_limit.value = str(c_lim_lower.values.round(5))
            self.control.style.upper_limit.value = str(c_lim_upper.values.round(5))

        if use_all_data:  # do the selection later
            sel_data = sel_data.sel(**selection, drop=True)

        assign_opts = {dim: self.data[dim] for dim in sel_data.dims}
        graph = sel_data.assign_coords(**assign_opts).hvplot.quadmesh(**graph_opts).redim.range(**color_range).opts(active_tools=['wheel_zoom', 'pan'])
        self.graph = graph
        if len(self.data[self.var].dims) > 2 and self.kwargs['extract along']:
            self.tap_stream.source = graph
            self.taps_graph = hv.DynamicMap(self.create_taps_graph, streams=[self.tap_stream, self.clear_points])
            self.output[0] = self.graph * self.taps_graph
            self.clear_series_button.disabled = False
        else:
            self.output[0] = self.graph
            self.clear_series_button.disabled = True

    def create_taps_graph(self, x, y, clear=False):
        color = next(iter(self.color_pool))
        if None not in [x, y]:
            self.taps.append((x, y, color))
        if self.control.kwargs['extract along'] is None:
            self.taps = []
        is_geo = self.kwargs['is_geo'] if 'is_geo' in self.kwargs else None
        geo_disabled = self.control.projection.is_geo.disabled if is_geo else None

        # Choose between gv.Points and hv.Points
        if is_geo and geo_disabled is False:
            tapped_map = gv.Points(self.taps, vdims=['z'])
        else:
            tapped_map = hv.Points(self.taps, vdims=['z'])
        tapped_map.opts(color='z', marker='triangle', line_color='black',
                        size=8)
        self.series_graph[0] = self.create_series_graph(x, y, color, clear)
        return tapped_map

    def create_series_graph(self, x, y, color, clear=False):
        # Case 1: When both x and y are NOT coords (i.e. are dims)
        # Case 2: When both x and y are coords
        #     2b: Both are 1d
        #     2b: Both are 2d with same dims
        #     2c: 2-dim with diff dims or multi-dim coords: Unable to extract
        # Note: 1 and 2a require same code.
        extract_along = self.control.kwargs['extract along']
        if None not in [x, y] and extract_along:
            color = self.taps[-1][-1] if self.taps[-1][-1] else None
            other_dims = [dim for dim in self.kwargs['remaining_dims'] if dim is not extract_along]

            # to use the value selected in index selector for selecting
            # data to create series. In case of aggregation, plot is
            # created along 0th val of the dim.
            if len(other_dims):
                other_dim_sels = {}
                for dim in other_dims:
                    dim_found = False
                    for dim_sel in self.index_selectors:
                        long_name = self.data[dim].long_name if hasattr(self.data[dim], 'long_name') else None
                        if dim_sel.name == dim or dim_sel.name == long_name:
                            val = dim_sel.value
                            other_dim_sels.update({dim: val})
                            dim_found = True
                    if not dim_found:  # when dim is used for aggregation
                        val = self.data[dim][0].values
                        other_dim_sels.update({dim: val})

            # Case 1 and  2a
            if not self.kwargs['are_var_coords'] or self.both_coords_1d():
                series_sel = {self.kwargs['x']: self.correct_val(self.kwargs['x'], x),
                              self.kwargs['y']: self.correct_val(self.kwargs['y'], y)}
            # Case 2b
            elif self.both_coords_2d_with_same_dims():
                y_dim, x_dim = self.data[self.kwargs['x']].dims

                y_mean = self.data[self.kwargs['y']].mean()*np.pi/180.
                a = (self.data[self.kwargs['y']]-y)**2 + ((self.data[self.kwargs['x']]-x)*np.cos(y_mean))**2
                j, i = np.unravel_index(a.argmin(), a.shape)

                series_sel = {x_dim: self.correct_val(x_dim, i),
                              y_dim: self.correct_val(y_dim, j)}
            # Case 2c
            else:
                logger.debug("Cannot extract 2d coords with different dims and multi-dimensional coords.")
                return self.series

            if len(other_dims):
                series_sel.update(other_dim_sels)

            sel_series_data = self.data[self.var]
            for dim, val in series_sel.items():
                sel_series_data = sel_val_from_dim(sel_series_data, dim, val)

            series_df = pd.DataFrame({extract_along: self.data[extract_along],
                                      self.var: np.asarray(sel_series_data)})

            tooltips = [(extract_along, f"@{extract_along}"),
                        (self.var, f"@{self.var}")]
            if len(other_dims):
                for dim, val in other_dim_sels.items():
                    tooltips.append((dim, str(val)))
            hover = HoverTool(tooltips=tooltips)

            series_map = series_df.hvplot(x=extract_along, y=self.var,
                                          height=self.kwargs['height'],
                                          width=self.kwargs['width'],
                                          tools=[hover])
            self.series = series_map.opts(color=color) * self.series

        return self.series

    def create_selectors_players(self, graph):
        """
        This function is applicable for when both x and y are in var coords,
        In case sliders are generated, this function moves the sliders to
        bottom of graph if they are present and convert them into Selectors,
        Players.
        """
        if len(self.data[self.var].dims) > 2 and self.kwargs['extract along']:
            self.taps_graph = hv.DynamicMap(self.create_taps_graph, streams=[self.tap_stream, self.clear_points])
            self.clear_series_button.disabled = False
            graph = graph * self.taps_graph
        else:
            self.clear_series_button.disabled = True
        graph = pn.Row(graph)
        try:  # `if graph[0][1]` or `len(graph[0][1])` results in error in case it is not present
            if graph[0][1]:  # if sliders are generated
                self.output[0] = graph[0][0]

                # link the generated slider with agg selector in fields
                for slider in graph[0][1]:
                    for dim in self.kwargs['dims_to_select_animate']:
                        long_name = self.data[dim].long_name if hasattr(self.data[dim], 'long_name') else None
                        if slider.name == dim or slider.name == long_name:
                            if self.kwargs[dim] == 'select':
                                selector = convert_widget(slider, pn.widgets.Select())
                            else:
                                selector = convert_widget(slider, pn.widgets.DiscretePlayer())
                            self.index_selectors.append(selector)

                for selector in self.index_selectors:
                    if isinstance(selector, pn.widgets.Select):
                        self.output[1].append(selector)
                    else:
                        player = player_with_name_and_value(selector)
                        self.output[1].append(player)

        except:  # else return simple graph
            self.output[0] = graph

    def set_data(self, data):
        self.data = xr.Dataset({f'{data.name}': data}, attrs=data.attrs) if isinstance(data, xr.DataArray) else data

    def set_coords(self, *args):
        # We can't reset indexed coordinates so add them every time
        # in coord_selector.value
        self.data = self.data.reset_coords()
        indexed_coords = set(self.data.dims).intersection(set(self.data.coords))
        new_coords = set(args[0]).union(indexed_coords)
        self.data = self.data.set_coords(new_coords)  # this `set_coords` belongs to xr.dataset
        self.control.set_coords(self.data)

    def check_is_plottable(self, var):
        """
        If a variable is 1-d, disable plot_button for it.
        """
        self.plot_button.disabled = False  # important to enable button once disabled
        data = self.data[var[0]]
        self.plot_button.disabled = len(data.dims) <= 1

    def correct_val(self, dim, x):
        """ Since tapped values from graph are in floats,
            we need to convert them into ints, or pass as it is
            for time
        """
        dtype = str(getattr(self.data[dim], 'dtype'))
        if 'int' in dtype:
            return int(x)
        elif 'float' in dtype:
            return float(x)
        else:
            return str(x)

    def both_coords_1d(self):
        return len(self.data[self.kwargs['x']].dims) == 1 and len(self.data[self.kwargs['y']].dims) == 1

    def both_coords_2d_with_same_dims(self):
        x_dims = self.data[self.kwargs['x']].dims
        y_dims = self.data[self.kwargs['y']].dims
        return len(x_dims) == len(y_dims) == 2 and sorted(x_dims) == sorted(y_dims)


def sel_val_from_dim(data, dim, x):
    """ To select values from a dim.
        For some dims method is required while for others it is not
    """
    try:
        return data.sel({dim: x})
    except:
        return data.sel({dim: x}, method='nearest')


def process_proj_params(params):
    params = ast.literal_eval(params)
    for k, v in params.items():
        if k == 'globe' and params['globe']:
            globe = ccrs.Globe(**v)
            params.update({'globe': globe})
    return params
