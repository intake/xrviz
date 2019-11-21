import panel as pn
from holoviews.plotting import list_cmaps
from .sigslot import SigSlot

TEXT = """
Control the style of the plot. For more information, please refer to the
[documentation](https://xrviz.readthedocs.io/en/latest/interface.html#style).
"""


class Style(SigSlot):
    """
    A pane to customise styling of the graphs.

    The following options are available in this pane:

        1. ``frame_height`` (default `300`):
            To modify the frame_height of main and series graph.
        2. ``frame_width`` (default `450`):
            To modify the frame_width of the main and series graph.
        3. ``cmap`` (default `Inferno`):
            To select a colormap for the main graph.
        4. ``color_scale`` (default `linear`):
            To scale the values to be plotted.
            The scaling options available are ``linear``, ``exp``, ``log``,
            ``reciprocal``, ``square`` and ``sqrt``. Here ``linear`` implies
            no scaling.
        5. ``cmap limits``:
            To change the colormap limits. User can fill these limits before
            plotting a variable. In case not filled by user, automatic filling
            of limits happen.

            - ``lower limit``: auto-filled value equals ``quantile(0.1)`` of values to be plotted.
            - ``upper limit``: auto-filled value equals ``quantile(0.9)`` of values to be plotted.

            In case of dask array, `dask.array.percentile <https://docs.dask.org/en/latest/array-api.html#dask.array.percentile>`_
            is use to compute the limits. ``tdigest`` method is used in case `crick <https://pypi.org/project/crick/>`_ is present.
            The value of limits is rounded off to 5 decimal places, for simplicity.

            Note that these values are filled with respect to color scaled
            values. Also these limits clear upon change in variable or
            color scaling.

        6. ``compute min/max from all data`` (default `False`):
            - ``True``: all values present in a data variable are used to compute upper and lower colormap limits.
            - ``False``: only values necessary to create first step/instance of graph are used.

            It is better to have its value `False` for larger datasets, to save
            computation time.
        7. ``colorbar`` (default `True`):
            Provides option to display/hide colorbar.
        8. ``rasterize`` (default `True`):
            Provides option to use `data shading <http://datashader.org/>`_ .
            It is better to have its value `True`, to get highly optimized
            rendering.
    """

    def __init__(self):
        super().__init__()
        self.frame_height = pn.widgets.IntSlider(name='frame_height', value=300, start=100,
                                                 end=1200)
        self.frame_width = pn.widgets.IntSlider(name='frame_width', value=450, start=100,
                                                end=1200)
        self.cmap = pn.widgets.Select(name='cmap', value='Inferno',
                                      options=list_cmaps())
        self.colorbar = pn.widgets.Checkbox(name='colorbar', value=True, width=150)
        # colormap_limits
        self.lower_limit = pn.widgets.TextInput(name='cmap lower limit',
                                                width=140)
        self.upper_limit = pn.widgets.TextInput(name='cmap upper limit',
                                                width=140)
        self.use_all_data = pn.widgets.Checkbox(name='compute min/max from all data', value=False)

        scaling_ops = ['linear', 'exp', 'log', 'reciprocal', 'square', 'sqrt']
        self.color_scale = pn.widgets.Select(name='color_scale',
                                             value='linear',
                                             options=scaling_ops)
        self.rasterize = pn.widgets.Checkbox(name='rasterize', value=True, width=150)

        self._register(self.use_all_data, 'clear_cmap_limits')
        self._register(self.color_scale, 'clear_cmap_limits')
        self.connect('clear_cmap_limits', self.setup)

        self.panel = pn.Column(
            pn.pane.Markdown(TEXT, margin=(0, 10)),
            pn.Row(self.frame_height, self.frame_width),
            pn.Row(self.cmap, self.color_scale),
            pn.Row(self.lower_limit, self.upper_limit),
            pn.Row(self.use_all_data, self.colorbar, self.rasterize),
            name='Style'
        )

    def setup(self, *args):
        #  Clears cmap limits
        self.lower_limit.value = None
        self.upper_limit.value = None

    def setup_initial_values(self, init_params={}):
        """
        To select initial values for the widgets in this pane.
        """
        for row in self.panel[1:]:
            for widget in row:
                if widget.name in init_params:
                    widget.value = init_params[widget.name]

    @property
    def kwargs(self):
        out = {widget.name: widget.value
               for row in self.panel[1:] for widget in row}
        return out
