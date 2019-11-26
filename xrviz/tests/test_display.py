import pytest
import xarray as xr
from xrviz.display import Display
from . import data
from ..utils import _is_coord


@pytest.fixture()
def displayer(data):
    return Display(data)


@pytest.fixture()
def displayer_array(data):
    data = data.temp
    data = xr.Dataset({f'{data.name}': data}, attrs=data.attrs)
    return Display(data)


@pytest.fixture()
def displayer_array_single_var(data):
    data = data.lon
    data = xr.Dataset({f'{data.name}': data}, attrs=data.attrs)
    return Display(data)


def test_fill_items(displayer):
    assert displayer.select.options == [
        None, 'validtime', 'time', 'lon', 'lat', 'mask', 'depth',
        'sigma', 'zeta', 'air_u', 'air_v', 'u', 'v', 'temp']


def test_fill_items_array(displayer_array):
    assert displayer_array.select.options == [
        None, 'time', 'sigma', 'temp']


def test_fill_items_single_var(displayer_array_single_var):
    assert displayer_array_single_var.select.options == [None, 'lon']
