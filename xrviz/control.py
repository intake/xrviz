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

    def set_dataset_property(self, selected_property):
        if isinstance(self.data, xr.Dataset):
            if selected_property in list(self.displayer.properties):
                selected_property = f'{self.displayer.right} {selected_property}'
                self.displayer.select.value = [selected_property]
            else:
                print(f"Use one of {list(self.displayer.properties)}")
        else:
            print("This method is applicable only for xr.Dataset")
