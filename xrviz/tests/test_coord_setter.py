import pytest
from xrviz.coord_setter import CoordSetter
from . import data

@pytest.fixture()
def coord_setter(data):
    return CoordSetter(data)


def test_coord_setter_initial(coord_setter, data):
    assert coord_setter.panel.name == 'Set Coords'
    assert coord_setter.coord_selector.options == list(data.variables)
    assert coord_setter.coord_selector.value == list(data.coords)
