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
        self.set_data(data)
        self.x = pn.widgets.Select(name='x', width=200)
        self.y = pn.widgets.Select(name='y', width=200)
        self.agg_selectors = pn.Column()
        self.agg_opts = ['None', 'mean', 'max',
                         'min', 'median',
                         'std', 'count']
        self.agg_plot_button = pn.widgets.Button(name='Aggregate',
                                                 width=100,
                                                 disabled=True)
        self.agg_graph = pn.Row(pn.Spacer(name='Agg Graph'))

        self._register(self.x, 'x')
        self._register(self.agg_plot_button, 'agg_plot_button', 'clicks')

        self.connect('x', self.change_y)
        self.connect('agg_plot_button', self.create_agg_plot)

        self.panel = pn.Row(pn.Column(self.x, self.y),
                            pn.Column(self.agg_selectors,
                                      pn.Spacer(name='agg_plot_button')),
                            self.agg_graph,
                            name='Fields',)

        if not self.is_dataset:
            self.setup(data)

    def set_data(self, data):
        if isinstance(data, xr.Dataset):
            self.data = data
            self.is_dataset = True
        else:
            self.data = data
            self.is_dataset = False

    def setup(self, var):
        # print(self.panel)
        self.agg_selectors.clear()  # To empty previouly selected value from selector
        # print(self.panel[1][1])
        self.panel[1][1] = self.agg_plot_button
        self.dims_selected_for_agg = []
        self.agg_plot_button.disabled = True
        self.agg_graph[0] = pn.Spacer(name='Agg Graph')  # To clear Agg Graph upon selection of new variable

        if self.is_dataset:
            if isinstance(var, str):
                self.var = var
            else:
                self.var = var[0]
            self.var_dims = list(self.data[var].dims)
        else:
            self.var_dims = list(self.data.dims)

        self.dims_aggs = dict(zip(self.var_dims, ['None']*len(self.var_dims)))

        for dim in self.var_dims:
            dim_selector = pn.widgets.Select(name=dim,
                                             options=self.agg_opts,
                                             width=100,)
            dim_selector.param.watch(self.callback, ['value'],
                                     onlychanged=False)
            self.agg_selectors.append(dim_selector)

        # self.dims_selector.options = self.var_dims
        x_opts = self.var_dims.copy()
        if len(x_opts) > 0:  # to check that data has dim (is not Empty)
            self.x.options = x_opts
            self.x.value = x_opts[0]
            y_opts = x_opts.copy()
            del y_opts[0]
            if y_opts is None:
                self.y.options = []
            else:
                self.y.options = y_opts

    def setup_agg_button(self, selected_dims):
        self.dims_selected_for_agg = selected_dims
        self.agg_plot_button.disabled = True
        # We need atleast 1 and at max (dims-1) selections to aggregate
        # So this button would be enbled when this condition is satisfied.
        if len(selected_dims) == 1 or len(selected_dims) < len(self.dims_selector.options):
            self.agg_plot_button.disabled = False

    def change_y(self, value):
        """
        Updates the options of y, by removing option selected in x (value),
        from all the variable dimensions available as options.
        """
        values = self.var_dims.copy()
        values.remove(self.x.value)
        self.y.options = values

    def create_agg_plot(self, *args):
        sel_dims = self.dims_selected_for_agg
        if self.is_dataset:
            sel = getattr(self.data, self.var)
        else:
            sel = self.data

        for dim, agg in sel_dims.items():
            if agg == 'count':
                sel = (~ sel.isnull()).sum(dim)
            else:
                sel = getattr(sel, agg)(dim)

        assign_opts = {dim: self.data[dim] for dim in sel.dims}
        sel = sel.assign_coords(**assign_opts)

        # for 1d sel we have simple hvplot
        # for 2d or 3d we will have quadmesh
        if len(sel.shape) == 1:
            self.agg_graph[0] = sel.hvplot()
        else:
            self.agg_graph[0] = self.rearrange_graph(sel.hvplot.quadmesh())

    def rearrange_graph(self, graph):
        # Moves the sliders to bottom of graph if they are present
        # And convert them into Selectors
        graph = pn.Row(graph)
        try:  # `if graph[0][1]` or `len(graph[0][1])` results in error in case it is not present
            index_selectors = pn.Row()
            if graph[0][1]:  # if sliders are generated
                for slider in graph[0][1]:
                    index_selector = convert_widget(slider, pn.widgets.Select())
                    index_selectors.append(index_selector)
                return pn.Column(graph[0][0], index_selectors)
        except:  # else return simple graph
            return graph

    def callback(self, *events):
        for event in events:
            if event.name == 'value':
                self.dims_aggs[event.obj.name] = event.new
                selected_dims = {k: v for k, v in self.dims_aggs.items() if v is not 'None'}

        self.dims_selected_for_agg = selected_dims
        self.agg_plot_button.disabled = True
        # We need atleast 1 and at max (dims-1) selections to aggregate
        # So this button would be enbled when this condition is satisfied.
        if len(selected_dims) == 1 or len(selected_dims) < len(self.var_dims):
            self.agg_plot_button.disabled = False

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel[0]}
        return out
