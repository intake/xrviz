import pytest
from xrviz.control import Control
from . import data
from ..compatability import has_cartopy


@pytest.fixture()
def control(data):
    return Control(data)


def test_control_initial(control):
    tabs = [tab.name for tab in control.tabs]
    if has_cartopy:
        assert tabs == ['Set Coords', 'Variables', 'Axes', 'Style',
                        'Projection']
    else:
        assert tabs == ['Set Coords', 'Variables', 'Axes', 'Style']
