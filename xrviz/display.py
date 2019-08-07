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
        self.select = pn.widgets.MultiSelect(size=8, max_width=300,
                                             height=210,
                                             width_policy='max',
                                             name='Variables')
        self.set_variables()

        self._register(self.select, "variable_selected")

        self.panel = pn.Row(self.select)

    def set_variables(self,):
        self.select.options = {
            _is_coord(self.data, name): name
            for name in list(self.data.variables)
        }

    def select_variable(self, variable):
        """
        Select a data variable from the available options.
        """
        if isinstance(variable, str):
            if variable in self.select.options.values():
                self.select.value = [variable]
            else:
                print(f"Variable {variable} not present in displayer.")

    def setup_initial_values(self, init_params={}):
        if 'Variables' in init_params:
            self.select_variable(init_params['Variables'])

    @property
    def kwargs(self):
        # Select only the first value from the selected variables.
        out = {p.name: p.value[0] for p in self.panel}
        return out

    def set_coords(self, data):
        self.data = data
        self.set_variables()
