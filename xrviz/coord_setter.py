import panel as pn
from .compatibility import logger
from .sigslot import SigSlot

TEXT = """
Convert data variables to coordinates to use them as axes. For more information,
please refer to the [documentation](https://xrviz.readthedocs.io/en/latest/interface.html#set-coords).
"""


class CoordSetter(SigSlot):
    """
    An input pane for choosing which variables are considered coordinates.

    It uses a `Cross Selector <https://panel.pyviz.org/reference/widgets/CrossSelector.html>`_
    to display a list of simple and coordinate variables.
    Simple variables (which are not data coordinates) are available on
    left side and default coordinates are available on right side.
    To set variables as coordinates, make selection on left side and click
    ``>>``. Similarly making selection on right side and clicking ``<<``
    will reset the coordinates. Other panes update themselves
    accordingly, in response to this change.
    """
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.name = 'Set Coords'
        self.coord_selector = pn.widgets.CrossSelector(
            value=list(self.data.coords),
            options=list(self.data.variables)
        )

        self.panel = pn.Column(
            pn.pane.Markdown(TEXT, margin=(0, 20)),
            self.coord_selector, name=self.name)

    def set_coords(self, data):
        """
        Called when the data attribute of the interface has change in variables considered as coordinates.
        """
        self.data = data
        logger.debug(self.coord_selector.value)
        self.coord_selector.value = list(self.data.coords)

    def setup_initial_values(self, init_params={}):
        """
        To set the variables, whose names have been passed, as coordinates.
        """
        if self.name in init_params:
            self.coord_selector.value = init_params[self.name]
