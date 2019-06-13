import xarray as xr
import pytest
from ..utils import _is_coord


@pytest.fixture(scope='module')
def data():
    return xr.open_dataset("xrviz/sample_data/great_lakes.nc")
