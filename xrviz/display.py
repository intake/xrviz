import panel as pn
import xarray as xr
from .sigslot import SigSlot


class Display(SigSlot):
    """
    This widget takes input as a xarray instance. For each Dataset,
    its variables are displayed. In case a   DataArray  has been
    provided only a single variable of that particular array is shown.

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
                                             width_policy='min',)
        # self.set_selection(self.data)
        self.set_variables(variables=None)

        self._register(self.select, "variable_selected")

        self.panel = pn.Row(self.select)

    def set_data(self, data):
        if isinstance(data, xr.Dataset) or isinstance(data, xr.DataArray):
            self.data = data

    def set_variables(self, variables):
        if isinstance(self.data, xr.Dataset):
            self.select.options = {self._isgeo(name): name for name in list(self.data.variables)}
        else:
            self.select.options = {self._isgeo(self.data.name): self.data.name}
            self.select.value = [self.data.name]

    def select_variable(self, variable):
        if isinstance(self.data, xr.Dataset):
            if isinstance(variable, str):
                if variable in list(self.select.options):
                    self.select.value = [variable]
                else:
                    print(f"Variable {variable} not present in displayer.")
        else:
            print('DataArray has a single variable.')

    def _isgeo(self, name):
        if isinstance(self.data, xr.Dataset):
            var = self.data[name]
        else:
            var = self.data

        if getattr(var, 'standard_name', "") in ['latitude', 'longitude', 'time']:
            return name + " " + '\U0001f30d'
        else:
            return name
