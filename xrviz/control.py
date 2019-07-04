import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe
from .fields import Fields
from .coord_setter import CoordSetter


class Control(SigSlot):
    """
    This section allows the user to control the other subsections,
    such as displayer, fields.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
           datset is used to initialize.

    Attributes
    ----------
    panel: Displays the generated template.
    displayer: Provides access to `Display` sub-section.
    describer: Provides access to `Describe` sub-section.
    fields: Provides access to `Fields` sub-section.
    kwargs: Provides access to kwargs selected in different subsections.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        is_cartopy_installed()
        self.displayer = Display(self.data)
        self.describer = Describe(self.data)
        self.fields = Fields(self.data)
        self.coord_setter = CoordSetter(self.data)
        self.tabs = pn.Tabs(self.fields.panel,
                            self.coord_setter.panel,
                            background=(230, 230, 230), width=1160)

        if has_cartopy:
            from .projection import Projection
            self.projection = Projection()
            self.tabs.append(self.projection.panel)
            self.fields.connect('x', self.check_is_projectable)
            self.fields.connect('y', self.check_is_projectable)

        self.displayer.connect("variable_selected", self.describer.setup)
        self.displayer.connect("variable_selected", self.fields.setup)

        self.panel = pn.Column(
                              pn.Row(self.displayer.panel,
                                     self.describer.panel),
                              self.tabs)

    def set_coords(self, data):
        try:  # Upon setting coords before selecting a variable
            var = self.kwargs['Variables']
        except:
            var = None
        self.data = data
        self.coord_setter.set_coords(self.data)
        self.displayer.set_coords(self.data)
        self.describer.set_coords(self.data, var)
        self.fields.set_coords(self.data, var)

    def check_is_projectable(self, *args):
        self.projection.is_geo.disabled = not self.fields.kwargs['are_var_coords']

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        if has_cartopy:
            out.update(self.projection.kwargs)
        return out


def is_cartopy_installed():
    global has_cartopy
    try:
        import cartopy
        has_cartopy = True
    except:
        has_cartopy = False
