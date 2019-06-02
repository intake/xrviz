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

        self.down = '│'
        self.right = '└──'
        self.properties = {'Dimensions': 'dims',
                           'Coordinates': 'coords',
                           'Variables': 'data_vars',
                           'Attributes': 'attrs'}

        self.rev_map = {'d': 'Dimensions',
                        'c': 'Coordinates',
                        'v': 'Variables',
                        'a': 'Attributes'}

        self.selected_property = None
        self.selected_subproperty = None
        self.select = pn.widgets.MultiSelect(size=8, min_width=300,
                                             width_policy='min')
        self.fill_items(self.select.options)

        self._register(self.select, "property_selector")
        self.connect("property_selector", self.expand_or_collapse_nested)

        self.panel = pn.Row(self.select)

    def fill_items(self, items):
        if isinstance(self.data, xr.Dataset):
            items.append('# DataSet')
            for prop in list(self.properties):
                items.append(f'{self.right} {prop}')
        else:
            items.append('# DataArray')

    def expand_or_collapse_nested(self, value):
        self._property = value[0].split()[-1]

        def find_prop_and_subprop(value):
            prop, subprop = None, None
            if " : " in value[0]:
                subprop = value[0].split()[-1]
                prop = self.rev_map[value[0].split()[-3]]
            else:
                prop = value[0].split()[-1]
            return prop, subprop

        def collapse(options, index):
            for opt in options[index+1:]:
                if opt.split()[0] == self.right:
                    break
                if self.down in opt:
                    options.remove(opt)
            return options

        def expand(options, name, index):
            children = get_children(name)
            for i, child in enumerate(children):
                options.insert(index+i+1, (f'{self.down} {self.right} {child}'))
            return options

        def get_children(prop):
            ds_prop = self.properties[prop]
            if ds_prop == "data_vars":
                return ['v' + " : " + child for child in getattr(self.data, str(ds_prop)).keys()]
            else:
                return [ds_prop[0] + " : " + child for child in getattr(self.data, str(ds_prop)).keys()]                 

        def has_expanded(selected_property, index):
            next_index = index+1
            if (next_index) < len(old) and (self.down in old[next_index]):
                return True
            else:
                return False

        self.selected_property, self.selected_subproperty = find_prop_and_subprop(value)

        if self._property in list(self.properties):
            if self.selected_property == 'Attributes' or self.selected_property == 'Coordinates':
                pass
            else:
                old = list(self.select.options)
                index, name = next((i, self.selected_property) for i, v in enumerate(old) if self.selected_property in v)

                if has_expanded(self.selected_property, index):
                    old = collapse(old, index)
                    self.select.options = list(old)
                else:
                    old = expand(old, name, index)
                    self.select.options = list(old)
