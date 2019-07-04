import pytest
from xrviz.control import Control
from . import data
from ..utils import cartopy_geoviews_installed


@pytest.fixture()
def control(data):
    return Control(data)


def test_control_initial(control):
    tabs = [tab.name for tab in control.tabs]
    if cartopy_geoviews_installed:
        assert tabs == ['Fields', 'Set Coords', 'Projection']
    else:
        assert tabs == ['Fields', 'Set Coords']
