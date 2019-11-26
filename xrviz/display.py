import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .utils import _is_coord


class Display(SigSlot):
    """Displays a list of data variables for selection.

    For each data, its variables are displayed in ``pn.widgets.MultiSelect``.
    Variables which are data coordinates are annotated with '📈'.

    Parameters
    ----------

    data: xarray.DataSet

    Attributes
    ----------

    panel:
        A ``panel.Row`` instance which displays the Multiselect widget.

    """

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.name = 'Variables'
        self.select = pn.widgets.Select(
            min_width=100, max_width=200, width_policy='max',
            name=self.name)
        self.set_variables()

        self._register(self.select, "variable_selected")

        self.panel = pn.Row(self.select)

    def set_variables(self,):
        self.select.options = [None] + list(self.data.variables)

    def select_variable(self, variable):
        """
        Select a data variable from the available options.
        """
        if isinstance(variable, str):
            if variable in self.select.options:
                self.select.value = variable
            else:
                print(f"Variable {variable} not present in displayer.")

    def setup_initial_values(self, init_params={}):
        if self.name in init_params:
            self.select_variable(init_params[self.name])

    @property
    def kwargs(self):
        return {self.name: self.select.value}

    def set_coords(self, data):
        self.data = data
        self.set_variables()
