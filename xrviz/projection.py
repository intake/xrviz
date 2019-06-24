import panel as pn
import xarray as xr
import geoviews as gv
from geoviews import tile_sources as gvts
from .sigslot import SigSlot
from .utils import projections_list


class Projection(SigSlot):

    def __init__(self):
        super().__init__()
        self.is_geo = pn.widgets.Checkbox(name='is_geo', value=False)
        self.alpha = pn.widgets.FloatSlider(name='alpha', start=0, end=1,
                                            step=0.01, value=0.7)

        self._register(self.is_geo, 'is_geo')
        self.connect('is_geo', self.setup)

        self.basemap = pn.widgets.Select(name='basemap',
                                         options=gvts.tile_sources,
                                         value=gvts.OSM)
        self.projection = pn.widgets.Select(name='projection',
                                            options=sorted(projections_list),
                                            value='PlateCarree')
        self.features = pn.widgets.MultiSelect(name='features',
                                               options=['borders', 'coastline',
                                                        'land', 'lakes',
                                                        'grid', 'ocean',
                                                        'rivers'])

        self.panel = pn.Column(self.is_geo,
                               self.basemap,
                               self.alpha,
                               self.projection,
                               self.features,
                               name='Projection')
        self.setup(value=self.is_geo.value)

    def setup(self, value):
        # disable the widgets if not is_geo else enable
        for widget in self.panel[1:]:
            widget.disabled = not value

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        return out
