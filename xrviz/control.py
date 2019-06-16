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
        self.displayer = Display(self.data)
        self.describer = Describe(self.data)
        self.fields = Fields(self.data)
        self.tabs = pn.Tabs(self.fields.panel,
                            background=(230, 230, 230), width=1160)

        if isinstance(self.data, xr.Dataset):
            self.coord_setter = CoordSetter(self.data)
            self.tabs.append(self.coord_setter.panel)

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

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        return out
