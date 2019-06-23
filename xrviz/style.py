import panel as pn
import holoviews
from .sigslot import SigSlot


class Style(SigSlot):

    def __init__(self):
        super().__init__()
        self.height = pn.widgets.IntSlider(name='height', value=300, start=100, end=1200)
        self.width = pn.widgets.IntSlider(name='width', value=700, start=100, end=1200)
        self.cmap = pn.widgets.Select(name='cmap', value='fire',
                                      options=holoviews.plotting.list_cmaps())
        self.colorbar = pn.widgets.Checkbox(name='colorbar', value=True)
        self.colormap_limits = pn.widgets.RangeSlider(name='colormap_limits',
                                                      start=0, end=1,
                                                      value=(0.1, 0.9), step=0.01)
        scaling_ops = ['None', 'arcsin', 'arccos', 'arctan', 'arcsinh',
                       'arccosh', 'arctanh', 'cos', 'cosh', 'exp', 'exp2',
                       'expm1', 'log', 'log2', 'log10', 'reciprocal',
                       'square', 'sqrt', 'sin', 'sinh', 'tan', 'tanh']
        self.color_scale = pn.widgets.Select(name='color_scale', value='None',
                                             options=scaling_ops)

        self.panel = pn.Column(pn.Row(self.height, self.width),
                               pn.Row(self.cmap, self.colorbar),
                               pn.Row(self.colormap_limits, self.color_scale),
                               name='Style')

    @property
    def kwargs(self):
        out = {widget.name: widget.value for row in self.panel for widget in row}
        return out
