import panel as pn
import xarray as xr
import hvplot.xarray
from cartopy import crs as ccrs
from .sigslot import SigSlot
from .control import Control
from .utils import convert_widget, player_with_name_and_value


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
                             pn.Column(name='Players'),
                             pn.Column(name='Agg Graph'),)

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
        not_to_index = [self.kwargs['x'], self.kwargs['y'], *self.kwargs['dims_to_agg']]
        self.var_selector_dims = sorted([dim for dim in self.var_dims if dim not in not_to_index])

        self.index_selectors = []
        self.output[1].clear()  # clears Index_selectors
        self.output[2].clear()  # clears Players

        for dim in self.var_selector_dims:
            if self.kwargs[dim] == 'Select':
                if self.is_dataset:
                    selector = pn.widgets.Select(name=dim, options=list(self.data[self.var][dim].values))
                else:
                    selector = pn.widgets.Select(name=dim, options=list(self.data[dim].values))
            elif self.kwargs[dim] == 'Animate':
                if self.is_dataset:
                    ops = list(self.data[self.var][dim].values)
                    selector = pn.widgets.DiscretePlayer(name=dim, value=ops[0], options=ops)
                else:
                    ops = list(self.data[dim].values)
                    selector = pn.widgets.DiscretePlayer(name=dim, value=ops[0], options=ops)

            self.index_selectors.append(selector)
            selector.param.watch(self.callback_for_indexed_graph, ['value'], onlychanged=False)

        self.output[0] = self.create_indexed_graph()
        for selector in self.index_selectors:
            if isinstance(selector, pn.widgets.Select):
                self.output[1].append(selector)
            else:
                player = player_with_name_and_value(selector)
                self.output[1].append(player)
        # self.create_players()

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
            selection[dim] = self.index_selectors[i].value
        x = self.kwargs['x']
        y = self.kwargs['y']
        dims_to_agg = self.kwargs['dims_to_agg']
        graph_opts = {'x': x,
                      'y': y,
                      'title': self.var}
        if self.is_dataset:
            sel_data = self.data[self.var]
        else:
            sel_data = self.data

        for dim in dims_to_agg:
            if self.kwargs[dim] == 'count':
                sel_data = (~ sel_data.isnull()).sum(dim)
            else:
                agg = self.kwargs[dim]
                sel_data = getattr(sel_data, agg)(dim)

        # rename the selection in case it is a coordinate, because we
        # cannot create a Dataset from a DataArray with the same name
        #  as one of its coordinates
        if sel_data.name in self.data.coords:
                sel_data = sel_data.to_dataset(name=f'{sel_data.name}_')

        sel_data = sel_data.sel(**selection, drop=True)
        assign_opts = {dim: self.data[dim] for dim in sel_data.dims}
        graph = sel_data.assign_coords(**assign_opts).hvplot.quadmesh(**graph_opts)
        return graph
