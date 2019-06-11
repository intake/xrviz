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
    index_selectors: Provides access to generated index_selectors.
    plot: Plot button, upon click generates graph according to
          kwargs selected in other sub-sections.
    output: Provides access to generated graph.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.control = Control(self.data)
        self.plot = pn.widgets.Button(name='Plot', width=200, disabled=True)
        self.index_selectors = self.control.fields.index_selectors
        self.output = pn.Row(pn.Spacer(name='Graph'))

        self._register(self.plot, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_plot)
        self.control.displayer.connect('variable_selected', self.check_is_plottable)

        self.panel = pn.Column(self.control.panel,
                               self.plot,
                               self.output
                               )

        if isinstance(self.data, xr.DataArray):
            self.check_is_plottable(var=None)

    def create_plot(self, *args):
        kwargs = self.control.kwargs
        var = kwargs['Variables']
        graph_opts = {'x': kwargs['x'],
                      'y': kwargs['y'],
                      'rasterize': True,
                      'width': 600,
                      'height': 400,
                      'crs': ccrs.PlateCarree()}

        if isinstance(self.data, xr.Dataset):
            graph_opts['title'] = var
            self.graph = pn.Row(self.data[var].hvplot.quadmesh(**graph_opts))
        else:
            graph_opts['title'] = self.data.name
            self.graph = pn.Row(self.data.hvplot.quadmesh(**graph_opts))

        self.output[0] = self.graph[0][0]
        self.fill_index_selectors()

    def fill_index_selectors(self):
        """
        To convert the auto-generated slider, into Select and Player
        widget.
        """
        self.index_selectors.clear()
        try:
            for widget in self.graph[0][1]:
                selector = convert_widget(widget, pn.widgets.Select())
                player = convert_widget(selector, pn.widgets.DiscretePlayer())
                combined = pn.Column(selector, player)
                self.index_selectors.append(combined)
        except IndexError as e:
            pass

    def check_is_plottable(self, var):
        self.plot.disabled = False
        if isinstance(self.data, xr.Dataset):
            var = var[0]
            if var in list(self.data.coords) or len(list(self.data[var].dims)) <= 1:
                self.plot.disabled = True
        else:
            if self.data.name in self.data.coords or len(self.data.dims) <= 1:
                self.plot.disabled = True
