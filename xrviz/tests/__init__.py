import xarray as xr
import pytest


@pytest.fixture(scope='module')
def data():
    return xr.open_dataset("xrviz/sample_data/great_lakes.nc")
