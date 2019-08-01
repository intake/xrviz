import panel as pn
from .sigslot import SigSlot


class CoordSetter(SigSlot):

    def __init__(self, data):
        """
        To intialize
        """
        super().__init__()
        self.data = data
        self.coord_selector = pn.widgets.CrossSelector(name='Set Coords',
                                                       value=list(self.data.coords),
                                                       options=list(self.data.variables))

        self.panel = self.coord_selector

    def set_coords(self, data):
        """
        to set the coords
        """
        self.data = data
        self.coord_selector.value = list(self.data.coords)

    def setup_initial_values(self, init_params={}):
        """
        To set initial values
        """
        if 'Set Coords' in init_params:
            self.coord_selector.value = init_params['Set Coords']
