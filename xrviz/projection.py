import inspect
import panel as pn
import xarray as xr
import geoviews as gv
from geoviews import tile_sources as gvts
from cartopy import crs as ccrs
from .sigslot import SigSlot

projections = [p for p in dir(ccrs) if inspect.isclass(getattr(ccrs, p)) and issubclass(getattr(ccrs, p), ccrs.Projection) and not p.startswith('_')]
not_to_include = ['Projection', 'UTM']
projections_list = sorted([p for p in projections if p not in not_to_include ])


class Projection(SigSlot):

    def __init__(self):
        super().__init__()
        self.is_geo = pn.widgets.Checkbox(name='is_geo', value=False,
                                          disabled=True)
        self.alpha = pn.widgets.FloatSlider(name='alpha', start=0, end=1,
                                            step=0.01, value=0.7, width=180)

        basemap_opts = {None: None}
        basemap_opts.update(gvts.tile_sources)
        self.basemap = pn.widgets.Select(name='basemap',
                                         options=basemap_opts,
                                         value=None)
        self.projection = pn.widgets.Select(name='projection',
                                            options=[None] + sorted(projections_list),
                                            value=None)
        self.crs = pn.widgets.Select(name='crs',
                                     options=sorted(projections_list),
                                     value='PlateCarree')
        self.rasterize = pn.widgets.Checkbox(name='rasterize', value=True)
        self.project = pn.widgets.Checkbox(name='project', value=False)
        self.global_extent = pn.widgets.Checkbox(name='global_extent',
                                                 value=False)
        self.crs_params = pn.Row()
        self.proj_params = pn.Row()

        self.feature_ops = ['None', 'borders', 'coastline', 'grid', 'land',
                            'lakes', 'ocean', 'rivers']
        self.features = pn.widgets.MultiSelect(name='features',
                                               options=self.feature_ops,
                                               value=self.feature_ops[1:])

        self._register(self.is_geo, 'geo_changed')
        self._register(self.is_geo, 'geo_disabled', 'disabled')
        self._register(self.crs, 'add_crs_params')
        self._register(self.projection, 'add_proj_params')
        self._register(self.basemap, 'show_basemap')
        self._register(self.rasterize, 'set_project')

        self.connect('geo_changed', self.setup)
        self.connect('geo_disabled', self.setup)
        self.connect('add_crs_params', self.add_crs_params)
        self.connect('add_proj_params', self.add_proj_params)
        self.connect('show_basemap', self.show_basemap)
        self.connect('set_project', self.set_project)

        self.panel = pn.Column(pn.Row(self.is_geo),
                               pn.Row(self.alpha, self.basemap),
                               pn.Row(self.crs, self.crs_params, name='crs'),
                               pn.Row(self.projection, self.proj_params, name='proj'),
                               pn.Row(self.rasterize,
                                      self.project,
                                      self.global_extent),
                               pn.Row(self.features),
                               name='Projection')
        self.setup()
        self.add_crs_params(self.crs.value)
        self.add_proj_params(self.projection.value)

    def setup(self, *args):
        # disable the widgets if is_geo is disabled or if is_geo is False
        if self.is_geo.disabled:
            disabled = True
        else:
            disabled = False if self.is_geo.value else True
        for row in self.panel[1:]:
            for widget in row:
                widget.disabled = disabled
        for widget in self.proj_params:
            widget.disabled = disabled

    def show_basemap(self, *args):
        value = False if self.basemap.value is None else True
        self.projection.disabled = value
        for widget in self.proj_params:
            widget.disabled = value
        self.features.value = [self.feature_ops[0]] if value else self.feature_ops[1:]

    def add_crs_params(self, *args):
        self.crs_params.clear()
        projs = accepted_proj_params(args[0])
        for proj in projs:
            parameter = pn.widgets.TextInput(name='{}'.format(proj),
                                             value='0', width=100)
            self.crs_params.append(parameter)

    def add_proj_params(self, *args):
        self.proj_params.clear()
        if args[0]:
            projs = accepted_proj_params(args[0])
            for proj in projs:
                parameter = pn.widgets.TextInput(name='{}'.format(proj),
                                                value='0', width=100)
                self.proj_params.append(parameter)

    def set_project(self, *args):
        """
        `project` is valid only when `rasterize` is True.
        When `rasterize` is False, `project` is disabled.
        """
        self.project.disabled = False if self.rasterize.value else True
        self.project.value = False

    @property
    def kwargs(self):
        out = {}
        out = {widget.name: widget.value for row in self.panel for widget in row if row.name not in ['crs', 'proj']}
        out.update({'crs': self.crs.value, 'projection': self.projection.value})
        out.update({'crs_params': {widget.name: widget.value for widget in self.crs_params}})
        out.update({'proj_params': {widget.name: widget.value for widget in self.proj_params}})
        return out


def accepted_proj_params(proj):
    """
    Return list consisting of `central_longitude`, `central_latitude`
    if present in parameters accepted by projection.
    """
    proj = getattr(ccrs, proj)
    params = list(inspect.signature(proj).parameters.keys())
    req_params = [p for p in params if p in ['central_longitude', 'central_latitude']]
    return req_params
