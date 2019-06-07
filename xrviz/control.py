import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe
from .fields import Fields


class Control(SigSlot):

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
                               pn.Row(self.fields.panel))

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        return out
