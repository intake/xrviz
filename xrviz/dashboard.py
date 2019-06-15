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
        self.plot_button = pn.widgets.Button(name='Plot', width=200, disabled=True)
        self.index_selectors = []
        self.output = pn.Row(pn.Spacer(name='Graph'),
                             pn.Column(name='Index_selectors'),
                             pn.Column(name='Players'))

        self._register(self.plot_button, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_plot)
        self.control.displayer.connect('variable_selected', self.check_is_plottable)

        self.panel = pn.Column(self.control.panel,
                               self.plot_button,
                               self.output)

        if not self.is_dataset:
            self.check_is_plottable(var=None)

    def set_data(self, data):
        if isinstance(data, xr.Dataset):
            self.data = data
            self.is_dataset = True
        elif isinstance(data, xr.DataArray):
            self.data = data
            self.is_dataset = False
        else:
            raise ValueError

    def create_plot(self, *args):
        self.kwargs = self.control.kwargs
        self.var = self.kwargs['Variables']
        if self.is_dataset:
            self.var_dims = list(self.data[self.var].dims)
        else:
            self.var_dims = list(self.data.dims)
        #  var_selector_dims refers to dims for which index_selectors would be created
        self.var_selector_dims = sorted([dim for dim in self.var_dims if dim not in [self.kwargs['x'], self.kwargs['y']]])

        self.index_selectors = []
        self.output[1].clear()  # clears Index_selectors
        self.output[2].clear()  # clears Players

        if self.is_dataset:
            for dim in self.var_selector_dims:
                selector = pn.widgets.Select(name=dim, options=list(self.data[self.var][dim].values))
                self.index_selectors.append(selector)
                selector.param.watch(self.callback_for_indexed_graph, ['value'], onlychanged=False)
        else:
            for dim in self.var_selector_dims:
                selector = pn.widgets.Select(name=dim, options=list(self.data[dim].values))
                self.index_selectors.append(selector)
                selector.param.watch(self.callback_for_indexed_graph, ['value'], onlychanged=False)

        self.output[0] = self.create_indexed_graph()
        for selector in self.index_selectors:
            self.output[1].append(selector)
        self.create_players()

    def create_players(self):
        """
        To convert the Selector widgets in index_selectors into Player
        widgets. Player widgets are linked with their respective selectors.
        """
        for selector in self.index_selectors:
            player = convert_widget(selector, pn.widgets.DiscretePlayer())
            self.output[2].append(player)

    def check_is_plottable(self, var):
        """
        If a variable is 1-d, disable plot_button for it.
        """
        self.plot_button.disabled = False  # important to enable button once disabled
        if self.is_dataset:
            var = var[0]
            if len(list(self.data[var].dims)) <= 1:
                self.plot_button.disabled = True
        else:
            if len(self.data.dims) <= 1:
                self.plot_button.disabled = True

    def callback_for_indexed_graph(self, *events):
        for event in events:
            if event.name == 'value':
                selection = {event.obj.name: event.new}
                self.output[0] = self.create_indexed_graph(**selection)  # passing only one value that has been changed

    def create_indexed_graph(self, **selection):
        """
        Creates graph for  selected indexes in selectors or players.
        """
        # selection consists of only one value here
        # update it to have value of other var_selector_dims
        for i, dim in enumerate(list(self.var_selector_dims)):
            if dim not in list(selection):
                selection[dim] = self.index_selectors[i].value
        x = self.kwargs['x']
        y = self.kwargs['y']
        graph_opts = {'x': x,
                      'y': y,
                      'title': self.var}
        assign_opts = {x: self.data[x], y: self.data[y]}
        if self.is_dataset:
            sel_data = self.data[self.var]
        else:
            sel_data = self.data

        # rename the selection in case it is a coordinate, because we
        # cannot create a Dataset from a DataArray with the same name
        #  as one of its coordinates
        if sel_data.name in self.data.coords:
                sel_data = sel_data.to_dataset(name=f'{sel_data.name}_')

        graph = sel_data.sel(**selection, drop=True).assign_coords(**assign_opts).hvplot.quadmesh(**graph_opts)
        return graph
