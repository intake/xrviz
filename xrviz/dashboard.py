import panel as pn
import xarray as xr

from .sigslot import SigSlot
from .control import Control
from .output import Output


class Dashboard(SigSlot):
    """
    Main entry point to XrViz, an interactive GUI for a given dataset.

    Parameters
    ----------
    data: xarray.DataSet
        The data to be visualised

    initial_params: `dict`
        To pre-select values of widgets upon initialization. The keys are
        generally names of widgets within the input area of the interface.
        For more details, refer to
        `Set Initial Parameters <../html/set_initial_parameters.html>`_ .

    Attributes
    ----------

    1. panel:
            A ``panel.Tabs`` instance containing the user input panes and
            output graphs of the interface.
    2. control:
            A ``Control`` instance responsible for input panes (control panel).
    3. plot_button:
            A ``pn.widgets.Button`` that generates graph according to values
            selected in input panes, upon click.
    4. graph:
            A ``HoloViews(DynamicMap)`` instance containing the main graph.
    5. output:
            The ``graph`` along with the select widgets for index selection.
    6. taps_graph:
            A ``holoviews.Points`` instance to record the location of taps.
    7. series_graph:
            A ``HoloViews(Overlay)`` instance having series extracted.
    8. clear_series_button:
            A ``pn.widgets.Button`` to clear the `taps_graph` and
            `series_graph`.
    """
    def __init__(self, data, initial_params={}):
        super().__init__()
        if not isinstance(data, xr.core.dataarray.DataWithCoords):
            raise ValueError("Input should be an xarray data object, not %s" % type(data))
        self.set_data(data)
        self.initial_params = initial_params
        self.control = Control(self.data)
        self.plot_button = pn.widgets.Button(
            name='Plot', width=200, disabled=True)

        self.output = Output()

        self._register(self.plot_button, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_graph)

        self._register(self.control.coord_setter.coord_selector, 'set_coords')
        self.connect("set_coords", self.set_coords)

        self.control.displayer.connect('variable_selected',
                                       self.check_is_plottable)
        self.control.displayer.connect('variable_selected',
                                       self._link_aggregation_selectors)
        self.control.fields.connect('x', self._link_aggregation_selectors)
        self.control.fields.connect('y', self._link_aggregation_selectors)
        # self.control.fields.connect('extract_along', self.output.clear_series)

        self.panel = pn.Column(self.control.panel,
                               pn.Row(self.plot_button, self.output.clear_series_button),
                               self.output.panel)

        # To auto-select in case of single variable
        if len(list(self.data.variables)) == 1:
            self.control.displayer.select.value = self.data.variables[0]

        self.control.setup_initial_values(self.initial_params)

    def _link_aggregation_selectors(self, *args):
        for dim_selector in self.control.kwargs['remaining_dims']:
            self.control.fields.connect(dim_selector, self.control.style.setup)

    def create_graph(self, *args):
        self.output.create_graph(self.data, self.control.kwargs)

    def set_data(self, data):
        self.data = (
            xr.Dataset({f'{data.name}': data})
            if isinstance(data, xr.DataArray) else data
        )

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
        Check if a data variable can be plotted.

        If a variable is 1-d, disable plot_button for it.
        """
        self.plot_button.disabled = False  # important to enable button once disabled
        data = self.data[var]
        self.plot_button.disabled = len(data.dims) <= 1
