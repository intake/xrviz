import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe


class Control(SigSlot):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.displayer = Display(self.data)
        self.describer = Describe(self.data)

        self.displayer.connect("variable_selected", self.describer.setup)

        self.panel = pn.Row(self.displayer.panel, self.describer.panel)
