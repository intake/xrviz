import panel as pn
import xarray as xr
from .sigslot import SigSlot


class Display(SigSlot):
    """
    This widget takes input as a xarray instance. or each dataset the
    properties:
    'Dimensions','Coordinates','Variables','Attributes'
    are dislpayed. On selecting one of these,the expansion
    occurs to show the arrtibutes associated with it.

    It of these individual property could be expanded accordingly.

    Parameters
    ----------
    data: `xarray` instance: `DataSet` or `DataArray`
        datset is used to initialize the DataSelector

    Attributes
    ----------
    panel: Displays the generated Multiselect object

    Reason for adding initial letter in front of a sub_property:
        It will act as option separator for the multiSelect.
        Ex: Variable 'time' could be present in both `Dimensions` and
           and `Coordinates`. Upon selection of any one, both are
           automatically selected. However in presence of `letter`
           `d :time` belongs to dimensions while `c : time` belongs
           to `Coordinates`.
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

    def set_variables(self, variables=None):
        """
        Method for selection of variables present in `xr.DataSet`.
        This is not applicable for `xr.DataArray` since it has only one
        variable.

        Parameters
        ----------
        `variables`: A list constiting of variables present in Dataset.
        """
        if isinstance(self.data, xr.Dataset):
            if variables is None:  # place all variables in options
                self.select.options = {self._isgeo(name): name for name in list(self.data.variables)}
            else:
                if isinstance(variables, list):
                    _opts = {}
                    for name in variables:
                        if name in list(self.data.variables):
                            _opts[self._isgeo(name)] = name
                        else:
                            print(f'Variable {name} not in data.variables')
                    self.select.options = _opts
        else:  # DataArray has only single variable
            self.select.options = {self._isgeo(self.data.name): self.data.name}
            self.select.value = [self.data.name]

    def select_variable(self, variable):
        if isinstance(self.data, xr.Dataset):
            if isinstance(variable, str):
                if variable in list(self.data.variables):
                    self.select.value = [variable]
                else:
                    print(f"Variable {variable} not present data.variables")
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
