import panel as pn
import xarray as xr
from .sigslot import SigSlot


class Fields(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.set_data(data)
        self.x = pn.widgets.Select(name='x')
        self.y = pn.widgets.Select(name='y')

        self.panel = pn.Column(self.x, self.y, name='fields',)

    def set_data(self, data):
        if isinstance(data, xr.Dataset) or isinstance(data, xr.DataArray):
            self.data = data

    def setup(self, var):
        self.var = var[0]
        coords = [coord for coord in self.data[var].coords.keys()]
        self.x.options = coords
        self.y.options = coords

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        return out
