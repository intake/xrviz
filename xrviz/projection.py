import inspect
import panel as pn
import xarray as xr
import geoviews as gv
from geoviews import tile_sources as gvts
from cartopy import crs as ccrs
from .sigslot import SigSlot
from .utils import proj_params

projections = [p for p in dir(ccrs) if inspect.isclass(getattr(ccrs, p)) and
               issubclass(getattr(ccrs, p), ccrs.Projection) and
               not p.startswith('_')]
not_to_include = ['Projection', 'UTM']
projections_list = sorted([p for p in projections if p not in not_to_include])


class Projection(SigSlot):
    """
    A pane to customise the projection of geographical data.

    The following options are available in this pane:

        1. ``is_geo`` (default `False`):
            Allows the user to decide whether or not to geographically
            project the data. If `True`, the other options in this tab are
            enabled.
        2. ``alpha`` (default 0.7):
            To adjust the opacity of the quadmesh on the map or projection.
        3. ``basemap`` (default `None`):
            To select basemap for the data from the available `tile_sources`_.
        4. ``crs`` (default `PlateCarree`):
            Here `crs` refers to `cartopy coordinate reference system`_, which
            declares the coordinate system of the data. It specifies the input
            projection, i.e. it declares how to interpret the incoming data
            values. It allows the user to select the `crs` in which data is
            present.
        5. ``crs params``:
            The default input parameters for each `crs` are auto filled upon
            selection. It allows the user to customize certain aspects of the
            projections by providing extra parameters such as
            ``central_longitude`` and ``central_latitude``. For more details
            refer to `cartopy coordinate reference system`_.
        6. ``projection`` (default `None`):
            To select what coordinate system to display the data in.
            We can also state it as output projection, i.e. how you want to
            map the data points onto the screen for display.
        7. ``projection params``:
            The default input parameters for each `projection` are auto filled
            upon selection. It allows the user to customize certain aspects of
            the projections by providing extra parameters such as
            ``central_longitude`` and ``central_latitude``.
        8. ``project`` (default `False`):
            Whether to project the data before plotting (adds initial overhead
            but avoids projecting data when plot is dynamically updated).
        9. ``global_extent`` (default `False`):
            Whether to expand the plot extent to span the whole globe.
        10. ``features`` (default=all except `None`):
            To select a set of basic geographic features to overlay behind the
            data in the plot.

        .. note::
            1. The widgets in this tab are enabled only if both ``x`` and ``y`` are data coordinates.
            2. `basemap` and `projection` are mutually exclusive options i.e it is not possible to have them both enabled simultaneously.


        .. _`cartopy projection`: https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html
        .. _`Geoviews`: http://geoviews.org/
        .. _`tile_sources`: http://geoviews.org/gallery/bokeh/tile_sources.html
        .. _`cartopy coordinate reference system`: https://scitools.org.uk/cartopy/docs/v0.15/crs/index.html#coordinate-reference-systems-in-cartopy

    """

    def __init__(self):
        """Initializes the Projection pane."""
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
        self.project = pn.widgets.Checkbox(name='project', value=False)
        self.global_extent = pn.widgets.Checkbox(name='global_extent',
                                                 value=False)
        self.crs_params = pn.widgets.TextInput(name='crs params',
                                               value="{}", width=400)
        self.proj_params = pn.widgets.TextInput(name='projection params',
                                                value="{}", width=400)

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

        self.connect('geo_changed', self.setup)
        self.connect('geo_disabled', self.setup)
        self.connect('add_crs_params', self.add_crs_params)
        self.connect('add_proj_params', self.add_proj_params)
        self.connect('show_basemap', self.show_basemap)

        self.panel = pn.Column(pn.Row(self.is_geo),
                               pn.Row(self.alpha, self.basemap),
                               pn.Row(self.crs, self.crs_params, name='crs'),
                               pn.Row(self.projection, self.proj_params,
                                      name='proj'),
                               pn.Row(self.project,
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
        self.proj_params.disabled = disabled

    def setup_initial_values(self, init_params={}):
        """
        To select initial values for the widgets in this pane.
        """
        is_geo = init_params.get('is_geo')
        if is_geo:  # since we need to enable is_geo if True
            self.is_geo.disabled = False
        for row in self.panel:
            for widget in row:
                w_name = widget.name
                if w_name in init_params:
                    if w_name == 'basemap':
                        tile = init_params[w_name]
                        widget.value = getattr(gvts, tile) if tile is not None else None
                    else:
                        widget.value = init_params[w_name]

    def show_basemap(self, *args):
        value = False if self.basemap.value is None else True
        self.projection.disabled = value
        self.proj_params.disabled = value
        self.features.value = [self.feature_ops[0]] if value else self.feature_ops[1:]

    def add_crs_params(self, *args):
        if args[0] != None:
            projs = proj_params(args[0])
            self.crs_params.value = projs

    def add_proj_params(self, *args):
        if args[0] != None:
            projs = proj_params(args[0])
            self.proj_params.value = projs

    def disable_geo(self, value):
        self.is_geo.disabled = value

    @property
    def kwargs(self):
        out = {widget.name: widget.value
               for row in self.panel for widget in row}
        return out
