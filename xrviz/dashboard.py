import panel as pn
import xarray as xr
import hvplot.xarray
from cartopy import crs as ccrs
from .sigslot import SigSlot
from .control import Control
from .utils import convert_widget


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
        self.set_data(data)
        self.control = Control(self.data)
        self.plot = pn.widgets.Button(name='Plot', width=200,)
        self.index_selectors = []
        self.output = pn.Row(pn.Spacer(name='Graph'),
                             pn.Column(name='Index_selectors'),
                             pn.Column(name='Players'))

        self._register(self.plot, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_plot)
        # self.control.displayer.connect('variable_selected', self.check_is_plottable)

        self.panel = pn.Column(self.control.panel,
                               self.plot,
                               self.output
                               )

        if isinstance(self.data, xr.DataArray):
            self.check_is_plottable(var=None)

    def set_data(self, data):
        if isinstance(data, xr.Dataset) or isinstance(data, xr.DataArray):
            self.data = data

    def create_plot(self, *args):
        self.kwargs = self.control.kwargs
        self.var = self.kwargs['Variables']
        self.var_dims = list(self.data[self.var].dims)
        self.var_selector_dims = sorted([dim for dim in self.var_dims if dim not in [ self.kwargs['x'], self.kwargs['y'] ]])
        self.index_selectors = []
        self.output[1].clear()  # clears Index_selectors
        self.output[2].clear()  # clears Players

        if isinstance(self.data, xr.Dataset):
            for dim in self.var_selector_dims:
                selector = pn.widgets.Select(name=dim, options=list(self.data[self.var][dim].values))
                self.index_selectors.append(selector)
                selector.param.watch(self.callback, ['value'], onlychanged=False)
            self.output[0] = self.create_indexed_graph()

            for selector in self.index_selectors:
                self.output[1].append(selector)
            self.create_players()

        else:
            graph_opts['title'] = self.data.name
            self.graph = pn.Row(self.data.hvplot.quadmesh(**graph_opts))

    def create_players(self):
        """
        To convert the auto-generated slider, into Select and Player
        widget.
        """
        for selector in self.index_selectors:
            player = convert_widget(selector, pn.widgets.DiscretePlayer())
            self.output[2].append(player)

    def check_is_plottable(self, var):
        self.plot.disabled = False
        if isinstance(self.data, xr.Dataset):
            var = var[0]
            if var in list(self.data.coords) or len(list(self.data[var].dims)) <= 1:
                self.plot.disabled = True
        else:
            if self.data.name in self.data.coords or len(self.data.dims) <= 1:
                self.plot.disabled = True

    def create_indexed_graph(self, **args):
        for i, dim in enumerate(list(self.var_selector_dims)):
            if dim not in list(args):
                args[dim] = self.index_selectors[i].value
        x = self.kwargs['x']
        y = self.kwargs['y']
        graph_opts = {'x': x,
                      'y': y,
                      'title': self.var}
        assign_opts = {x: self.data[x], y: self.data[y]}
        plot = self.data[self.var].sel(**args, drop=True).assign_coords(**assign_opts).hvplot.quadmesh(**graph_opts)
        return plot

    def callback(self, *events):
        for event in events:
            if event.name == 'value':
                ops = {event.obj.name: event.new}
                self.output[0] = self.create_indexed_graph(**ops)
