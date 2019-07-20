import panel as pn
from holoviews.plotting import list_cmaps
from .sigslot import SigSlot


class Style(SigSlot):

    def __init__(self):
        super().__init__()
        self.height = pn.widgets.IntSlider(name='height', value=300, start=100, end=1200)
        self.width = pn.widgets.IntSlider(name='width', value=700, start=100, end=1200)
        self.cmap = pn.widgets.Select(name='cmap', value='Inferno',
                                      options=list_cmaps())
        self.colorbar = pn.widgets.Checkbox(name='colorbar', value=True)
        # colormap_limits
        self.lower_limit = pn.widgets.TextInput(name='cmap lower limit', width=140)
        self.upper_limit = pn.widgets.TextInput(name='cmap upper limit', width=140)
        self.use_all_data = pn.widgets.Checkbox(name='compute min/max from all data', value=False)

        scaling_ops = ['linear', 'exp', 'log', 'reciprocal', 'square', 'sqrt']
        self.color_scale = pn.widgets.Select(name='color_scale', value='linear',
                                             options=scaling_ops)
        self.rasterize = pn.widgets.Checkbox(name='rasterize', value=True)

        self._register(self.use_all_data, 'clear_cmap_limits')
        self._register(self.color_scale, 'clear_cmap_limits')
        self.connect('clear_cmap_limits', self.setup)

        self.panel = pn.Column(pn.Row(self.height, self.width),
                               pn.Row(self.cmap, self.color_scale),
                               pn.Row(self.lower_limit, self.upper_limit),
                               pn.Row(self.use_all_data, self.colorbar,
                                      self.rasterize),
                               name='Style')

    def setup(self, *args):
        #  Clears cmap limits
        self.lower_limit.value = None
        self.upper_limit.value = None

    def setup_initial_values(self, init_params={}):
        for row in self.panel:
            for widget in row:
                if widget.name in init_params:
                    widget.value = init_params[widget.name]

    @property
    def kwargs(self):
        out = {widget.name: widget.value for row in self.panel for widget in row}
        return out
