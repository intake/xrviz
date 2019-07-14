import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe
from .fields import Fields
from .style import Style
from .coord_setter import CoordSetter
from .compatibility import has_cartopy


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
        self.displayer = Display(self.data)
        self.describer = Describe(self.data)
        self.fields = Fields(self.data)
        self.style = Style()
        self.coord_setter = CoordSetter(self.data)
        self.tabs = pn.Tabs(pn.Row(self.displayer.panel,
                                   self.describer.panel, name='Variables'),
                            self.coord_setter.panel,
                            self.fields.panel,
                            self.style.panel,
                            background=(240, 240, 240), width=1160)

        if has_cartopy:
            from .projection import Projection
            self.projection = Projection()
            self.tabs.append(self.projection.panel)
            self.fields.connect('x', self.check_is_projectable)
            self.fields.connect('y', self.check_is_projectable)

        self.displayer.connect("variable_selected", self.describer.setup)
        self.displayer.connect("variable_selected", self.fields.setup)
        self.displayer.connect("variable_selected", self.style.setup)

        self.panel = pn.Column(self.tabs)

    def setup_initial_values(self, initial_params={}):
        self.displayer.setup_initial_values(initial_params)
        self.coord_setter.setup_initial_values(initial_params)
        self.fields.setup_initial_values(initial_params)
        self.style.setup_initial_values(initial_params)
        if has_cartopy:
            self.projection.setup_initial_values(initial_params)

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
        value = not self.fields.kwargs['are_var_coords']
        self.projection.disable_geo(value)

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        out.update(self.style.kwargs)
        if has_cartopy:
            out.update(self.projection.kwargs)
        return out
