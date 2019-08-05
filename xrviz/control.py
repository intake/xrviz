import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .display import Display
from .describe import Describe
from .fields import Fields
from .style import Style
from .coord_setter import CoordSetter
from .compatibility import has_cartopy


class Control(SigSlot):
    """
    This section arranges all the panes in the form of tabs,
    hence providing the control for interaction.

    Parameters
    ----------
    data: ``xarray.DataSet`` or ``xarray.DataArray``
        Is passed to the user input panes for initialisation.

    Attributes
    ----------
    1. panel:
            A ``panel.Tabs`` instance containing the user input panes of the interface.
    2. displayer:
            A ``SigSlot`` instance which displays a list of data variables for selection.
    3. describer:
            A ``SigSlot`` instance which describes the property selected in the ``displayer``.
    4. coord_setter:
            A ``SigSlot`` instance for choosing which variables are considered coordinates.
    5. fields:
            Provides access to `Axes` pane.
    6. style:
            Provides access to `Style` pane.
    7. projection:
            Provides access to `Projection` pane (if present).
    8. kwargs:
            A dictionary gathered from the widgets of the input Panes,
            of a form which can be passed to the plotting function as kwargs.
    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.displayer = Display(self.data)
        self.describer = Describe(self.data)
        self.fields = Fields(self.data)
        self.style = Style()
        self.coord_setter = CoordSetter(self.data)
        self.tabs = pn.Tabs(pn.Row(self.displayer.panel,
                                   self.describer.panel, name='Variables'),
                            self.coord_setter.panel,
                            self.fields.panel,
                            self.style.panel,
                            background=(240, 240, 240), width=1160)

        if has_cartopy:
            from .projection import Projection
            self.projection = Projection()
            self.tabs.append(self.projection.panel)
            self.fields.connect('x', self.check_is_projectable)
            self.fields.connect('y', self.check_is_projectable)

        self.displayer.connect("variable_selected", self.describer.setup)
        self.displayer.connect("variable_selected", self.fields.setup)
        self.displayer.connect("variable_selected", self.style.setup)

        self.panel = pn.Column(self.tabs)

    def setup_initial_values(self, initial_params={}):
        self.displayer.setup_initial_values(initial_params)
        self.coord_setter.setup_initial_values(initial_params)
        self.fields.setup_initial_values(initial_params)
        self.style.setup_initial_values(initial_params)
        if has_cartopy:
            self.projection.setup_initial_values(initial_params)

    def set_coords(self, data):
        """
        Called after coordinates have been set/reset, to update the other input panes.
        """
        try:  # Upon setting coords before selecting a variable
            var = self.kwargs['Variables']
        except:
            var = None
        self.data = data
        self.coord_setter.set_coords(self.data)
        self.displayer.set_coords(self.data)
        self.describer.set_coords(self.data, var)
        self.fields.set_coords(self.data, var)

    def check_is_projectable(self, *args):
        value = not self.fields.kwargs['are_var_coords']
        self.projection.disable_geo(value)

    @property
    def kwargs(self):
        out = self.displayer.kwargs
        out.update(self.fields.kwargs)
        out.update(self.style.kwargs)
        if has_cartopy:
            out.update(self.projection.kwargs)
        return out
