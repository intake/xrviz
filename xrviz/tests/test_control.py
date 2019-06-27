import pytest
from xrviz.control import Control
from . import data


@pytest.fixture()
def control(data):
    return Control(data)


def test_control_initial(control):
    tabs = [tab.name for tab in control.tabs]
    assert tabs == ['Set Coords', 'Variables', 'Axes', 'Style']
