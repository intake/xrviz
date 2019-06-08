import panel as pn
import xarray as xr
import hvplot.xarray
from cartopy import crs as ccrs
from .sigslot import SigSlot
from .control import Control


class Dashboard(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.control = Control(self.data)
        self.plot = pn.widgets.Button(name='Plot', width=200)
        self.output = pn.Row(pn.Spacer(name='Plot'),)

        self._register(self.plot, 'plot_clicked', 'clicks')
        self.connect('plot_clicked', self.create_plot)

        self.panel = pn.Column(self.control.panel,
                               self.plot,
                               self.output
                               )

    def create_plot(self, *args):
        kwargs = self.control.kwargs
        var = kwargs['var']
        crs = ccrs.PlateCarree()
        if isinstance(self.data, xr.Dataset):
            self.output[0] = self.data[var][:, :, :].hvplot.quadmesh(x=kwargs['x'], y=kwargs['y'], rasterize=True,
                                                                   width=600, height=400, crs=crs, cmap='jet')
        else:
            self.output[0] = self.data[:, :, :].hvplot.quadmesh(x=kwargs['x'], y=kwargs['y'], rasterize=True,
                                                                   width=600, height=400, crs=crs, cmap='jet')
