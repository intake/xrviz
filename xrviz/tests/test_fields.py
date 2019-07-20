import pytest
import panel as pn
from xrviz.fields import Fields
from . import data
from .test_dashboard import dashboard
from ..compatibility import mpcalc


@pytest.fixture()
def fields(data):
    return Fields(data)


@pytest.fixture()
def fields_array(data):
    return Fields(data.temp)


@pytest.mark.parametrize('fields',
                         ['fields', 'fields_array'],
                         indirect=True)
def test_fields_initial(fields):
    assert fields.x.value is None
    assert fields.y.value is None
    assert fields.panel.name == 'Axes'
    assert fields.panel[0][0][0].object == '### Plot Dimensions'
    assert isinstance(fields.panel[0][1], pn.Spacer)
    assert fields.panel[0][2][0].object == '### Aggregations'


def test_x_y_var_without_coords(dashboard):
    dashboard.control.displayer.select_variable('temp')
    assert dashboard.control.fields.x.value == 'nx'
    assert dashboard.control.fields.y.value == 'ny'


def test_x_y_var_with_coords(dashboard):
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    x_val, y_val = ('lon', 'lat') if mpcalc else ('lat', 'lon')
    assert dashboard.control.fields.x.value == x_val
    assert dashboard.control.fields.y.value == y_val


def test_change_y_dim_selectors(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    fields = dashboard.control.fields
    fields.x.value = 'time'
    assert fields.y.value == 'nx'
    assert fields.agg_selectors[0].name == 'ny'
    assert fields.agg_selectors[1].name == 'sigma'


def test_check_are_var_coords(dashboard):
    fields = dashboard.control.fields
    fields.x.value = 'nx'
    fields.y.value = 'ny'
    assert fields.check_are_var_coords() is False
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    fields.x.value = 'lon'
    fields.y.value = 'lat'
    assert fields.check_are_var_coords() is True
