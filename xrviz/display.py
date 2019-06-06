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
    selected_property: property which has been  selected in multiselect
        One of 'Dimensions','Coordinates','Variables','Attributes'
    selected_subproperty: subproperty which has been selected
        An attribute of its property.
        Example: `nx`,`ny`,`time` for property `Dimensions`.
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
        if isinstance(data, xr.Dataset) or isinstance(data, xr.DataArray):
            self.data = data

        self.selected_property = None
        self.select = pn.widgets.MultiSelect(size=8, min_width=300,
                                             width_policy='min',)
        self.set_selection(self.data)

        self._register(self.select, "variable_selected")

        self.panel = pn.Row(self.select)

    def set_selection(self, data):
        if isinstance(data, xr.Dataset):
            self.select.options = {self._isgeo(name): name for name in list(self.data.variables)}
        else:
            self.select.options = {self._isgeo(self.data.name): self.data.name}
            self.select.value = [self.data.name]

    def _isgeo(self, name):
        if isinstance(self.data, xr.Dataset):
            var = self.data[name]
        else:
            var = self.data

        if getattr(var, 'standard_name', "") in ['latitude', 'longitude', 'time']:
            return name + " " + '\U0001f30d'
        else:
            return name
