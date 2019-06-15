import xarray as xr
from xrviz.dashboard import Dashboard
import pytest
from . import data
from ..utils import _is_coord


@pytest.fixture(scope='module')
def dashboard(data):
    return Dashboard(data)


def test_check_is_plottable_1D(dashboard):
    # `validtime` is 1D variable
    dashboard.plot_button.disabled = False
    dashboard.control.displayer.select_variable('validtime')
    assert dashboard.plot_button.disabled


def test_check_is_plottable_coord(dashboard):
    # `time` is data coordinate
    dashboard.plot_button.disabled = False
    dashboard.control.displayer.select_variable('time')
    assert dashboard.plot_button.disabled


def test_check_is_plottable_other_vars(dashboard):
    # `temp` is neither 1D nor coordinate
    dashboard.plot_button.disabled = True
    dashboard.control.displayer.select_variable('temp')
    assert dashboard.plot_button.disabled is False
