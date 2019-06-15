import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe
from .fields import Fields


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

        self.displayer.connect("variable_selected", self.describer.setup)
        self.displayer.connect("variable_selected", self.fields.setup)

        self.panel = pn.Column(
                               pn.Row(self.displayer.panel,
                                      self.describer.panel),
                               pn.Tabs(self.fields.panel,
                                       background=(230, 230, 230), width=1160))

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        return out
