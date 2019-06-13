import xarray as xr
from xrviz.display import Display
from . import data
from ..utils import _is_coord


def test_fill_items_in_DataSet(data):
    displayer = Display(data)
    for prop in data.variables:
        assert _is_coord(data, prop) in displayer.select.options


def test_fill_items_in_DataArray(data):
    dataArray = data.temp
    displayer = Display(dataArray)
    assert _is_coord(dataArray, dataArray.name) in displayer.select.options
