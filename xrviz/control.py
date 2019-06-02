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

        self._register(self.displayer.select, "selection")

        self.connect("selection", self.describe)

        self.panel = pn.Row(self.displayer.panel, self.describer.panel)

    def describe(self, _):
        selected_property = self.displayer.selected_property
        sub_property = self.displayer.selected_subproperty
        self.describer.setup(selected_property, sub_property)
