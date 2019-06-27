import panel as pn
import holoviews
from .sigslot import SigSlot


class Style(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.height = pn.widgets.IntSlider(name='height', value=300, start=100, end=1200)
        self.width = pn.widgets.IntSlider(name='width', value=700, start=100, end=1200)
        self.cmap = pn.widgets.Select(name='cmap', value='fire',
                                      options=holoviews.plotting.list_cmaps())
        self.colorbar = pn.widgets.Checkbox(name='colorbar', value=True)
        self.colormap_limits = pn.widgets.RangeSlider(name='colormap_limits',
                                                      start=0, end=1,
                                                      value=(0.1, 0.9), step=0.01)
        scaling_ops = ['linear', 'cos', 'exp', 'log', 'reciprocal',
                       'square', 'sqrt', 'sin', 'tan']
        self.color_scale = pn.widgets.Select(name='color_scale', value='linear',
                                             options=scaling_ops)
        # colormap_limits
        self.lower_limit = pn.widgets.TextInput(name='cmap lower limit', width=120)
        self.upper_limit = pn.widgets.TextInput(name='cmap upper limit', width=120)

        self._register(self.colormap_limits, "colormap_limits")

        self.panel = pn.Column(pn.Row(self.height, self.width),
                               pn.Row(self.cmap, self.colorbar),
                               pn.Row(self.colormap_limits, self.color_scale),
                               pn.Row(self.lower_limit, self.upper_limit),
                               name='Style')

    def setup(self, var):
        self.var = var if isinstance(var, str) else var[0]
        cmap_l_limit = self.colormap_limits.value[0]
        cmap_u_limit = self.colormap_limits.value[1]
        sel_data = self.data[self.var]
        self.lower_limit.value = str(sel_data.quantile(cmap_l_limit).values.round(5))
        self.upper_limit.value = str(sel_data.quantile(cmap_u_limit).values.round(5))

    @property
    def kwargs(self):
        out = {widget.name: widget.value for row in self.panel for widget in row}
        return out
