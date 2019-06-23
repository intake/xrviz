import panel as pn
import xarray as xr
import geoviews as gv
from cartopy import crs
from geoviews import tile_sources as gvts
from .sigslot import SigSlot


class Projection(SigSlot):

    def __init__(self):
        super().__init__()
        self.is_geo = pn.widgets.Checkbox(name='is_geo', value=False)
        self.alpha = pn.widgets.FloatSlider(name='alpha', start=0, end=1,
                                            step=0.01, value=0.7)
        projections = [crs.RotatedPole, crs.Mercator, crs.LambertCylindrical, crs.Geostationary, 
                       crs.AzimuthalEquidistant, crs.OSGB, crs.EuroPP, crs.Gnomonic, crs.PlateCarree, 
                       crs.Mollweide, crs.OSNI, crs.Miller, crs.InterruptedGoodeHomolosine,
                       crs.LambertConformal, crs.SouthPolarStereo, crs.AlbersEqualArea, crs.Orthographic,
                       crs.NorthPolarStereo, crs.Robinson]

        self._register(self.is_geo, 'is_geo')
        self.connect('is_geo', self.setup)

        self.basemap = pn.widgets.Select(name='basemap',
                                         options=gvts.tile_sources,
                                         value=gvts.OSM)

        self.panel = pn.Column(self.is_geo,
                               self.basemap,
                               self.alpha,
                               name='Projection')
        self.setup(value=self.is_geo.value)

    def setup(self, value):
        if value:
            self.basemap.disabled = False
            self.alpha.disabled = False
        else:
            self.basemap.disabled = True
            self.alpha.disabled = True

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        return out
