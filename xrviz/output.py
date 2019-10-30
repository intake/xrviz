import ast
import dask
import panel as pn
import pandas as pd
import numpy as np

import hvplot.xarray
import hvplot.pandas
import holoviews as hv
from holoviews import streams
from bokeh.models import HoverTool

from itertools import cycle
from .sigslot import SigSlot

from .utils import convert_widget, player_with_name_and_value, is_float, look_for_class
from .compatibility import ccrs, gv, gf, has_cartopy, logger, has_crick_tdigest


class Output(SigSlot):
    def __init__(self):
        super().__init__()
        self.index_selectors = []
        self.taps_graph = hv.Points([])
        self.clear_series_button = pn.widgets.Button(
            name='Clear', width=200, disabled=True)

        self.panel = pn.Column(
            pn.Row(pn.Spacer(name='Graph'), pn.Column(name='Index_selectors')),
            pn.Row(pn.Spacer(name='Series Graph'))
        )

        self.taps = []
        self.tap_stream = streams.Tap(transient=True)
        colors = ['#60fffc', '#6da252', '#ff60d4', '#ff9400', '#f4e322',
                  '#229cf4', '#af9862', '#629baf', '#7eed5a', '#e29ec8',
                  '#ff4300']
        self.color_pool = cycle(colors)
        self.clear_points = hv.streams.Stream.define('Clear_points', clear=False)(transient=True)

        self._register(self.clear_series_button, 'clear_series', 'clicks')
        self.connect('clear_series', self.clear_series)

    def clear_series(self, *args):
        """
        Clears the markers on the image, and the extracted series.
        """
        self.panel[1][0] = pn.Spacer(name='Series Graph')
        self.series = hv.Points([]).opts(frame_height=self.kwargs['frame_height'],
                                        frame_width=self.kwargs['frame_width'])
        self.taps.clear()
        if args:
            self.clear_points.event(clear=True)

    def create_graph(self, data, kwargs):
        """
        Creates a graph according to the values selected in the widgets.

        This method is usually invoked by the user clicking "Plot"

        It handles the following two cases:

            1. Both `x`, `y` are present in selected variable's coordinates.
            Geographic projection is possible only in this case. It uses
            ``create_selectors_players`` method for creation of the graph.
            Here the selectors generated automatically by hvplot are used.

            2. One or both of  `x`, `y` are NOT present in selected variable's
            coordinates (both `x` and `y` are considered as dimensions). It
            uses ``create_indexed_graph`` method for creation of the graph.
            The selectors are created and linked with graph by XrViz.
        """
        self.kwargs = kwargs
        self.var = self.kwargs['Variables']

        # reassignment of coords (if not done result in
        # errors for some of the selections in fields panel)
        missing_coords = {dim: data[dim] for dim in data[self.var].dims}
        self.data = sel_data = data[self.var].assign_coords(**missing_coords)

        if self.index_selectors:
            for selector in self.index_selectors:
                del selector
        self.index_selectors = []
        self.panel[0][1].clear()  # clears Index_selectors
        self.clear_series()

        graph_opts = {'x': self.kwargs['x'],
                        'y': self.kwargs['y'],
                        'title': self.var,
                        'frame_height': self.kwargs['frame_height'],
                        'frame_width': self.kwargs['frame_width'],
                        'cmap': self.kwargs['cmap'],
                        'colorbar': self.kwargs['colorbar'],
                        'rasterize': self.kwargs['rasterize'],
                        'logz': self.kwargs['logz']}
        dims_to_agg = self.kwargs['dims_to_agg']
        use_all_data = self.kwargs['compute min/max from all data']

        if has_cartopy:
            is_geo = self.kwargs['is_geo']
            base_map = self.kwargs['basemap']
            show_map = True if base_map != None else False

            if is_geo:
                crs = process_proj(self.kwargs['crs'], self.kwargs['crs params'])
                geo_ops = {'alpha': self.kwargs['alpha'],
                            'project': self.kwargs['project'],
                            'global_extent': self.kwargs['global_extent'],
                            'geo': True,
                            'crs': crs}
                if not show_map:
                    # find projection and crs, add it to geo_ops
                    proj_class = self.kwargs['projection']
                    if proj_class:
                        proj = process_proj(proj_class, self.kwargs['projection params'])
                        geo_ops.update({'projection': proj})

                graph_opts.update(geo_ops)

                feature_map = gv.Overlay([getattr(gf, feat) for feat in self.kwargs['features'] if feat is not 'None'])

        for dim in dims_to_agg:
            print('dim:', dim)
            if self.kwargs[dim] == 'count':
                sel_data = (~ sel_data.isnull()).sum(dim)
            else:
                agg = self.kwargs[dim]
                sel_data = getattr(sel_data, agg)(dim)

        if self.var in list(sel_data.coords):  # When a var(coord) is plotted wrt itself
            sel_data = sel_data.to_dataset(name=f'{sel_data.name}_')

        if not use_all_data:
            # sel the values at first step, to use for cmap limits
            sels = {dim: 0 for dim in self.kwargs['dims_to_select_animate']}
            sel_data_for_cmap = sel_data.isel(**sels, drop=True)
        else:
            sel_data_for_cmap = sel_data

        cmin, cmax = self.kwargs['cmap lower limit'], self.kwargs['cmap upper limit']
        cmin, cmax = (cmin, cmax) if is_float(cmin) and is_float(cmax) else ('', '')

        # It is better to set initial values as 0.1,0.9 rather than
        # 0,1(min, max) to get a color balance graph
        c_lim_lower, c_lim_upper = (
            (float(cmin), float(cmax)) if cmin and cmax
            else find_cmap_limits(sel_data_for_cmap))

        color_range = {sel_data.name: (c_lim_lower, c_lim_upper)}

        # if not cmin:  # if user left blank or initial values are empty
        #     self.control.style.lower_limit.value = str(round(c_lim_lower, 5))
        #     self.control.style.upper_limit.value = str(round(c_lim_upper, 5))


        # Following tasks are happening here:

        # 2. graph_opts: customise the plot according to selections in
        # style and projection(if available)
        # 3. color_range: customise the colormap range according to cmap
        # lower and upper limits
        # 4. active_tools: activate the tools required such as 'wheel_zoom',
        # 'pan'
        graph = sel_data.hvplot.quadmesh(
            **graph_opts).redim.range(**color_range).opts(
            active_tools=['wheel_zoom', 'pan'])

        self.tap_stream.source = graph

        if has_cartopy and is_geo:
            graph = (
                feature_map * graph
                if self.kwargs['features'] != ['None'] else graph
            )
            if show_map:
                graph = base_map * graph

        if len(self.data.dims) > 2 and self.kwargs['extract along']:
            print('adding tap_graph')
            self.taps_graph = hv.DynamicMap(self.create_taps_graph,
                                            streams=[self.tap_stream,
                                                     self.clear_points])
            self.clear_series_button.disabled = False
            graph = graph * self.taps_graph
        else:
            print('nah')
            self.clear_series_button.disabled = True

        graph = pn.Row(graph)

        self.panel[0][0] = look_for_class(graph, pn.pane.HoloViews)[0]
        self.create_selectors_players(graph)

        for selector in self.index_selectors:
            if isinstance(selector, pn.widgets.Select):
                self.panel[0][1].append(selector)
            else:
                player = player_with_name_and_value(selector)
                self.panel[0][1].append(player)

    def create_taps_graph(self, x, y, clear=False):
        """
        Create an output layer in the graph which responds to taps

        Whenever the user taps (or clicks) the graph, a glyph will be overlaid,
        and a series is extracted at that point.
        """
        print('make taps', x, y)
        color = next(iter(self.color_pool))
        if None not in [x, y]:
            self.taps.append((x, y, color))
        if self.kwargs['extract along'] is None:
            self.taps = []
        is_geo = self.kwargs.get('is_geo', False)

        # Choose between gv.Points and hv.Points
        element = hv.Points if not is_geo else gv.Points
        tapped_map = element(self.taps, vdims=['z']).opts(
            color='z', marker='triangle', line_color='black', size=8)
        self.panel[1][0] = self.create_series_graph(x, y, color, clear)
        return tapped_map

    def create_series_graph(self, x, y, color, clear=False):
        """
        Extract a series at a given point, and plot it.

        The series plotted has same color as that of the marker depicting the
        location of the tap.

        The following cases have been handled:
            `Case 1`:
                When both x and y are NOT coords (i.e. are dims)

            `Case 2`:
                When both x and y are coords

                ``2a``: Both are 1-dimensional

                ``2b``: Both are 2-dimensional with same dimensions.

                ``2c``: Both are 2-dimensional with different dims or are multi-dimcoordinates. Here we are unable to extract.
            Note that ``Case 1`` and ``Case 2a`` can be handled with the same
            code.
        """
        extract_along = self.kwargs['extract along']
        if None not in [x, y] and extract_along:
            color = self.taps[-1][-1] if self.taps[-1][-1] else None
            other_dims = [dim for dim in self.kwargs['remaining_dims'] if
                          dim is not extract_along]

            # to use the value selected in index selector for selecting
            # data to create series. In case of aggregation, plot is
            # created along 0th val of the dim.
            if len(other_dims):
                other_dim_sels = {}
                for dim in other_dims:
                    dim_found = False
                    for dim_sel in self.index_selectors:
                        long_name = self.data[dim].long_name if hasattr(
                            self.data[dim], 'long_name') else None
                        if dim_sel.name == dim or dim_sel.name == long_name:
                            val = dim_sel.value
                            other_dim_sels.update({dim: val})
                            dim_found = True
                    if not dim_found:  # when dim is used for aggregation
                        val = self.data[dim][0].values
                        other_dim_sels.update({dim: val})

            # Case 1 and  2a
            if self.both_coords_1d():
                series_sel = {
                    self.kwargs['x']: self.correct_val(self.kwargs['x'], x),
                    self.kwargs['y']: self.correct_val(self.kwargs['y'], y)}
            # Case 2b
            elif self.both_coords_2d_with_same_dims():
                y_dim, x_dim = self.data[self.kwargs['x']].dims

                y_mean = self.data[self.kwargs['y']].mean() * np.pi / 180.
                a = (self.data[self.kwargs['y']] - y) ** 2 + (
                            (self.data[self.kwargs['x']] - x) * np.cos(
                        y_mean)) ** 2
                j, i = np.unravel_index(a.argmin(), a.shape)

                series_sel = {x_dim: self.correct_val(x_dim, i),
                              y_dim: self.correct_val(y_dim, j)}
            # Case 2c
            else:
                logger.debug("Cannot extract 2d coords with different dims and"
                             " multi-dimensional coords.")
                return self.series

            if len(other_dims):
                series_sel.update(other_dim_sels)

            sel_series_data = self.data
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
                                          frame_height=self.kwargs['frame_height'],
                                          frame_width=self.kwargs['frame_width'],
                                          tools=[hover])
            self.series = series_map.opts(color=color) * self.series

        return self.series

    def create_selectors_players(self, graph):
        """
        Converts the sliders generated by hvplot into selectors/players.

        This is applicable only when both `x` and `y` are present in variable
        coordinates. It converts any sliders generated by hvplot into
        selectors/players and moves them to the bottom of graph.
        """
        sliders = look_for_class(graph, pn.widgets.Widget)
        for slider in sliders:
            for dim in self.kwargs['dims_to_select_animate']:
                long_name = self.data[dim].long_name if hasattr(
                    self.data[dim], 'long_name') else None
                if slider.name == dim or slider.name == long_name:
                    if self.kwargs[dim] == 'select':
                        selector = convert_widget(slider, pn.widgets.Select)
                    else:
                        selector = convert_widget(slider, pn.widgets.DiscretePlayer)
                    self.index_selectors.append(selector)

    def correct_val(self, dim, x):
        """ Convert tapped coordinates to int, if not time-type
        """
        dtype = self.data[dim].dtype.kind
        if dtype == 'i':
            return int(x)
        elif dtype == 'f':
            return float(x)
        else:
            return str(x)

    def both_coords_1d(self):
        return len(self.data[self.kwargs['x']].dims) == 1 and len(self.data[self.kwargs['y']].dims) == 1

    def both_coords_2d_with_same_dims(self):
        x_dims = self.data[self.kwargs['x']].dims
        y_dims = self.data[self.kwargs['y']].dims
        return len(x_dims) == len(y_dims) == 2 and sorted(x_dims) == sorted(y_dims)


def find_cmap_limits(sel_data):
    if isinstance(sel_data.data, dask.array.core.Array):
        method = 'tdigest' if has_crick_tdigest else 'default'
        return dask.array.percentile(sel_data.data.ravel(), (10, 90),
                                     method=method).compute()
    else:  # if sel_data.data is numpy.ndarray
        return [float(q) for q in sel_data.quantile([0.1, 0.9])]


def sel_val_from_dim(data, dim, x):
    """ Select values from a dim.
    """
    try:
        return data.sel({dim: x})
    except:
        return data.sel({dim: x}, method='nearest')


def process_proj(cls, params):
    params = ast.literal_eval(params)
    for k, v in params.items():
        if k == 'globe' and params['globe']:
            globe = ccrs.Globe(**v)
            params.update({'globe': globe})
    return getattr(ccrs, cls)(**params)
