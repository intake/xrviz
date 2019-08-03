import panel as pn
from .sigslot import SigSlot


class CoordSetter(SigSlot):
    """
    To set and reset the data coordinates.

    It uses a `Cross Selector <https://panel.pyviz.org/reference/widgets/CrossSelector.html>`_
    to display a list of simple and coordinate variables.
    Simple variables (which are not data coordinates) are available on
    left side and default coordinates are available on right side.
    To set variables as coordinates, make selection on left side and click
    ``>>``. Similarly making selection on right side and clicking ``<<``
    will reset the coordinates. Other panes would update themselves
    accordingly, in response to this change.
    """
    def __init__(self, data):
        """ Initializes the CoordSetter object.
        """
        super().__init__()
        self.data = data
        self.coord_selector = pn.widgets.CrossSelector(name='Set Coords',
                                                       value=list(self.data.coords),
                                                       options=list(self.data.variables))

        self.panel = self.coord_selector

    def set_coords(self, data):
        """
        To set the coords
        """
        self.data = data
        self.coord_selector.value = list(self.data.coords)

    def setup_initial_values(self, init_params={}):
        """
        To set initial values
        """
        if 'Set Coords' in init_params:
            self.coord_selector.value = init_params['Set Coords']
