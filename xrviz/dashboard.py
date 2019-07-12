import panel as pn
import xarray as xr
import hvplot.xarray
import holoviews as hv
from holoviews import streams
import warnings
from itertools import cycle
import numpy
from .sigslot import SigSlot
from .control import Control
from .utils import convert_widget, player_with_name_and_value, is_float


class Dashboard(SigSlot):
    """
    This section provides access to the complete generated dashboard,
    consisting of all subsections.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
           datset is used to initialize.

    Attributes
    ----------
    panel: Displays the generated dashboard.
    control: Provides access to the generated control panel.
    plot: Plot button, upon click generates graph according to
          kwargs selected in other sub-sections.
    output: Provides access to generated graph.
    """

    def __init__(self, data):
        super().__init__()
        if not isinstance(data, xr.core.dataarray.DataWithCoords):
            raise ValueError("Input should be an xarray data object, not %s" % type(data))
        self.set_data(data)
        cartopy_geoviews_installed()
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

        # self.control.fields.connect('extract_along', self.clear_series)

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

        self.taps = []
        self.tap_stream = streams.Tap(transient=True)
        colors = ['#60fffc', '#6da252', '#ff60d4', '#ff9400', '#f4e322',
                  '#229cf4', '#af9862', '#629baf', '#7eed5a', '#e29ec8',
                  '#ff4300']
        self.color_pool = cycle(colors)

    def clear_series(self, *args):
        self.series_graph[0] = pn.Spacer(name='Series Graph')
        self.series = hv.Points([]).opts(height=self.kwargs['height'],
                                         width=self.kwargs['width'])
        self.taps.clear()
        self.output[0] = self.graph * self.taps_graph

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
        print('Extract Along', self.kwargs['Extract Along'])
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

        are_var_coords = self.kwargs['are_var_coords']
        if are_var_coords:
            graph_opts = {'x': self.kwargs['x'],
                          'y': self.kwargs['y'],
                          'title': self.var,
                          'height': self.kwargs['height'],
                          'width': self.kwargs['width'],
                          'cmap': self.kwargs['cmap'],
                          'colorbar': self.kwargs['colorbar']}
            color_scale = self.kwargs['color_scale']
            dims_to_agg = self.kwargs['dims_to_agg']
            use_all_data = self.kwargs['compute min/max from all data']
            sel_data = self.data[self.var]

            if has_cartopy:
                is_geo = self.kwargs['is_geo']
                show_map = self.kwargs['show_map']
                base_map = self.kwargs['basemap']

                if is_geo:
                    geo_ops = {'alpha': self.kwargs['alpha'],
                               'project': self.kwargs['project'],
                               'rasterize': self.kwargs['rasterize'],
                               'global_extent': self.kwargs['global_extent'],
                               'geo': True}
                    if not show_map:
                        # find projection and crs, add it to geo_ops
                        proj_ops = {}
                        proj_params = self.kwargs['proj_params']
                        for p_param in proj_params:
                            proj_ops[p_param] = float(self.kwargs[p_param]) if is_float(self.kwargs[p_param]) else 0
                        projection = getattr(ccrs, self.kwargs['projection'])(**proj_ops)
                        crs_val = self.kwargs['crs']
                        crs = getattr(ccrs, crs_val)() if crs_val is not None else crs_val
                        projection_ops = {'crs': crs,
                                          'projection': projection}
                        geo_ops.update(projection_ops)

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
                sels = {dim: 0 for dim in self.kwargs['remaining_dims']}
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
                      'colorbar': self.kwargs['colorbar']}
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
        if len(self.data[self.var].dims) > 2:
            self.tap_stream.source = graph
            self.taps_graph = hv.DynamicMap(self.create_taps_graph, streams=[self.tap_stream])
            self.output[0] = self.graph * self.taps_graph
            self.clear_series_button.disabled = False
        else:
            self.output[0] = self.graph
            self.clear_series_button.disabled = True

    def create_taps_graph(self, x, y, clear=False):
        print("create_taps_graph")
        print(x, y)

        color = next(iter(self.color_pool))
        if None not in [x, y]:
            self.taps.append((x, y, color))
        tapped_map = hv.Points(self.taps, vdims=['z']).opts(color='z',
                                                            marker='triangle',
                                                            line_color='black',
                                                            size=8)
        self.series_graph[0] = self.create_series_graph(x, y, color)
        return tapped_map

    def create_series_graph(self, x, y, color):
        print("create_series_graph")
        if None not in [x, y]:
            if not self.kwargs['are_var_coords']:  # when both x and y are dims
                color = self.taps[-1][-1] if self.taps[-1][-1] else None
                extract_along = self.control.kwargs['Extract Along']
                other_dims = [dim for dim in self.kwargs['remaining_dims'] if dim is not extract_along]
                print('extract_along', extract_along)
                print('other_dims', other_dims)
                series_sel = {self.kwargs['x']: int(x),
                              self.kwargs['y']: int(y)}
                # to use the value selected in index selector for selecting
                # data to create series. In case of aggregation, plot is
                # created along 0th val of the dim.
                if len(other_dims):
                    other_dim_sels = {}
                    i_sel_names = [sel.name for sel in self.index_selectors]
                    for dim in other_dims:
                        dim_found = False
                        long_name = self.data[dim].long_name if hasattr(self.data[dim], 'long_name') else None
                        for dim_sel in self.index_selectors:
                            if dim_sel.name == long_name or dim_sel.name == dim:
                                val = dim_sel.value
                                other_dim_sels.update({dim: val})
                                dim_found = True
                        if not dim_found:
                            val = self.data[dim][0].values
                            other_dim_sels.update({dim: val})

                series_sel.update(other_dim_sels)
                print('series_sel', series_sel)
                sel_series_data = self.data.sel(**series_sel)
                series_map = sel_series_data[self.var].hvplot(height=self.kwargs['height'],
                                                              width=self.kwargs['width'])
                self.series = series_map.opts(color=color) * self.series

        return self.series

    def create_selectors_players(self, graph):
        """
        This function is applicable for when both x and y are in var coords,
        In case sliders are generated, this function moves the sliders to
        bottom of graph if they are present and convert them into Selectors,
        Players.
        """
        if len(self.data[self.var].dims) > 2:
            self.taps_graph = hv.DynamicMap(self.create_taps_graph, streams=[self.tap_stream])
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

        except Exception as e:  # else return simple graph
            print(e)
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


def cartopy_geoviews_installed():
    """
    Checks if both cartopy and geoviews are present.
    Projection panel would be displayed only if both present.
    """
    global has_cartopy
    try:
        from cartopy import crs as ccrs
        import geoviews as gv
        import geoviews.feature as gf
        has_cartopy = True
        global ccrs, gv, gf
    except:
        warnings.warn("Install Cartopy, Geoviews to view Projection Panel.", Warning)
        has_cartopy = False
