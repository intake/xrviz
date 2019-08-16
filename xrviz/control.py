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
    The user input part of the interface

    Parameters
    ----------
    data: xarray.DataSet
        The data to be visualised. Here, we are mostly concerned with
        displaying the variables, their attributes, and assigning coordinates
        to roles upon plotting.

    Attributes
    ----------
    1. panel:
            A ``panel.Tabs`` instance containing the user input panes
    2. displayer:
            A ``Display`` instance, displays a list of data variables for selection.
    3. describer:
            A ``Describe`` instance, describes the properties of the variable
            selected in the ``displayer``.
    4. coord_setter:
            A ``CoordSetter`` instance for choosing which variables are
            considered coordinates.
    5. fields:
            A ``Fields`` instance to select the axes to plot with.
    6. style:
            A ``Style`` instance to customise styling of the graphs.
    7. projection:
            A ``Projection`` instance to customise the projection of
            geographical data.
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
        self.tabs = pn.Tabs(
            pn.Row(self.displayer.panel, self.describer.panel,
                   name='Variables', width_policy='max'),
            self.coord_setter.panel,
            self.fields.panel,
            self.style.panel,
            background='#f5f5f5',
            width_policy='max',
            margin=20
        )

        if has_cartopy:
            from .projection import Projection
            self.projection = Projection()
            self.tabs.append(self.projection.panel)
            self.fields.connect('x', self.check_is_projectable)
            self.fields.connect('y', self.check_is_projectable)

        self.displayer.connect("variable_selected", self.describer.setup)
        self.displayer.connect("variable_selected", self.fields.setup)
        self.displayer.connect("variable_selected", self.style.setup)

        self.panel = pn.WidgetBox(self.tabs, width_policy='max')

    def setup_initial_values(self, initial_params={}):
        self.displayer.setup_initial_values(initial_params)
        self.coord_setter.setup_initial_values(initial_params)
        self.fields.setup_initial_values(initial_params)
        self.style.setup_initial_values(initial_params)
        if has_cartopy:
            self.projection.setup_initial_values(initial_params)

    def set_coords(self, data):
        """
        Called after coordinates have been set, to update the other input panes.
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
        """
        Check if the selected variable can be  projected geographically.

        This is possible only when both `x` and `y` are present in selected
        variable's coordinates.
        """
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
