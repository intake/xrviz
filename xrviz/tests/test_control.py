import pytest
from xrviz.control import Control
from . import data
from ..compatibility import has_cartopy


@pytest.fixture()
def control(data):
    return Control(data)


def test_control_initial(control):
    tabs = [tab.name for tab in control.tabs]
    if has_cartopy:
        assert tabs == ['Variables', 'Set Coords', 'Axes', 'Style',
                        'Projection']
    else:
        assert tabs == ['Variables', 'Set Coords', 'Axes', 'Style']
