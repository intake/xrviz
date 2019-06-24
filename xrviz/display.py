import panel as pn
import xarray as xr
from .sigslot import SigSlot
from .utils import _is_coord


class Display(SigSlot):
    """
    This widget takes input as a xarray instance. For each Dataset,
    its variables are displayed. In case a   DataArray  has been
    provided only a single variable of that particular array is shown.
    Variables which are coordinates are annotated with '📈'.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
           data is used to initialize the DataSelector

    Attributes
    ----------
    panel: Displays the generated Multiselect object

    """

    def __init__(self, data):
        super().__init__()
        if data is not None:
            self.set_data(data)

        self.select = pn.widgets.MultiSelect(size=8, min_width=300,
                                             height=135,
                                             width_policy='min',
                                             name='Variables')
        # self.set_selection(self.data)
        self.set_variables()

        self._register(self.select, "variable_selected")

        self.panel = pn.Row(self.select)

    def set_data(self, data):
        self.data = data
        self.is_dataset = isinstance(data, xr.Dataset)

    def set_variables(self,):
        if self.is_dataset:
            self.select.options = {_is_coord(self.data, name): name for name in list(self.data.variables)}
        else:
            self.select.options = {_is_coord(self.data, self.data.name): self.data.name}
            self.select.value = [self.data.name]

    def select_variable(self, variable):
        if self.is_dataset:
            if isinstance(variable, str):
                if variable in self.select.options.values():
                    self.select.value = [variable]
                else:
                    print(f"Variable {variable} not present in displayer.")
        else:
            print('DataArray has a single variable.')

    @property
    def kwargs(self):
        """
        Select only the first value from the selected variables.
        """
        out = {p.name: p.value[0] for p in self.panel}
        return out

    def set_coords(self, data):
        self.data = data
        self.set_variables()
