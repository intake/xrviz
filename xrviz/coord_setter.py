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
        # self._register(self.set_coord_button, "set_coords", 'clicks')

        # self.connect("set_coords", self.set_coords)

        self.panel = pn.Column(self.coord_selector,
                               self.set_coord_button,
                               name='Set Coords')

    def set_coords(self, data):
        self.data = data
        self.coord_selector.value = list(self.data.coords)
        print('Coords Setter:', list(self.data.coords))

    # def set_coords(self, *args):
    #     # We can't reset indexed coordinates so add them every time
    #     # in coord_selector.value
    #     self.data = self.data.reset_coords()
    #     indexed_coords = set(self.data.dims) & set(self.data.coords)
    #     new_coords = list(set(self.coord_selector.value) | set(indexed_coords))
    #     self.data = self.data.set_coords(new_coords)
    #     self.coord_selector.value = new_coords
    #     print(list(self.data.coords))
