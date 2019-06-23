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

        self.panel = pn.Column(self.height,
                               self.width,
                               self.cmap,
                               self.colorbar,
                               self.colormap_limits,
                               name='Style')

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        return out
