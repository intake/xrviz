import inspect
import panel as pn
import xarray as xr
import geoviews as gv
from geoviews import tile_sources as gvts
from cartopy import crs as ccrs
from .sigslot import SigSlot

projections = [p for p in dir(ccrs) if inspect.isclass(getattr(ccrs, p)) and issubclass(getattr(ccrs, p), ccrs.Projection) and not p.startswith('_')]
not_to_include = ['Projection', 'UTM']
projections_list = sorted([p for p in projections if  p not in not_to_include ])


class Projection(SigSlot):

    def __init__(self):
        super().__init__()
        self.is_geo = pn.widgets.Checkbox(name='is_geo', value=False,
                                          disabled=True)
        self.alpha = pn.widgets.FloatSlider(name='alpha', start=0, end=1,
                                            step=0.01, value=0.7)

        basemap_opts = {'None': 'None'}
        basemap_opts.update(gvts.tile_sources)
        self.basemap = pn.widgets.Select(name='basemap',
                                         options=basemap_opts,
                                         value=gvts.OSM)
        self.projection = pn.widgets.Select(name='projection',
                                            options=projections_list,
                                            value='PlateCarree')
        self.crs = pn.widgets.Select(name='crs',
                                     options=[None] + sorted(projections_list),
                                     value=None)
        feature_ops = ['None', 'borders', 'coastline', 'grid', 'land', 'lakes',
                       'ocean', 'rivers']
        self.features = pn.widgets.MultiSelect(name='features',
                                               options=feature_ops,
                                               value=feature_ops[1:])

        self._register(self.is_geo, 'is_geo_value')
        self._register(self.is_geo, 'is_geo_disabled', 'disabled')

        self.connect('is_geo_value', self.setup)
        self.connect('is_geo_disabled', self.setup)

        self.panel = pn.Column(self.is_geo,
                               # self.basemap,
                               self.alpha,
                               self.projection,
                               self.crs,
                               self.features,
                               name='Projection')
        self.setup()

    def setup(self, *args):
        # disable the widgets if is_geo is disabled or if is_geo is False
        if self.is_geo.disabled:
            disabled = True
        else:
            disabled = False if self.is_geo.value else True
        for widget in self.panel[1:]:
            widget.disabled = disabled

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        return out
