import panel as pn
from .sigslot import SigSlot


class CoordSetter(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.coord_selector = pn.widgets.CrossSelector(value=list(self.data.coords),
                                                       options=list(self.data.variables))
        self.set_coord_button = pn.widgets.Button(name='Set Coords',
                                                  width=200)

        self.panel = pn.Column(self.coord_selector,
                               self.set_coord_button,
                               name='Set Coords')

    def set_coords(self, data):
        self.data = data
        self.coord_selector.value = list(self.data.coords)
