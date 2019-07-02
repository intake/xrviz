import panel as pn
from holoviews.plotting import list_cmaps
from .sigslot import SigSlot


class Style(SigSlot):

    def __init__(self):
        super().__init__()
        self.height = pn.widgets.IntSlider(name='height', value=300, start=100, end=1200)
        self.width = pn.widgets.IntSlider(name='width', value=700, start=100, end=1200)
        self.cmap = pn.widgets.Select(name='cmap', value='Inferno',
                                      options=list_cmaps(provider='bokeh', reverse = False))
        self.colorbar = pn.widgets.Checkbox(name='colorbar', value=True)
        # colormap_limits
        self.lower_limit = pn.widgets.TextInput(name='cmap lower limit', width=140)
        self.upper_limit = pn.widgets.TextInput(name='cmap upper limit', width=140)

        scaling_ops = ['linear', 'exp', 'log', 'reciprocal', 'square', 'sqrt']
        self.color_scale = pn.widgets.Select(name='color_scale', value='linear',
                                             options=scaling_ops)

        self.panel = pn.Column(pn.Row(self.height, self.width),
                               pn.Row(self.cmap, self.color_scale),
                               pn.Row(self.lower_limit, self.upper_limit,
                                      self.colorbar),
                               name='Style')

    def setup(self, *args):
        #  Changes cmap limits
        self.lower_limit.value = None
        self.upper_limit.value = None

    @property
    def kwargs(self):
        out = {widget.name: widget.value for row in self.panel for widget in row}
        return out
