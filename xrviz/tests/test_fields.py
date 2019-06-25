import pytest
from xrviz.fields import Fields
from . import data

@pytest.fixture()
def fields(data):
    return Fields(data)


def test_fields_initial(fields):
    assert fields.x.value is None
    assert fields.y.value is None
    assert fields.panel.name == 'Fields'
    assert fields.panel[0][0].object == '### Plot Dimensions'
    assert fields.panel[1][0].object == '### Aggregations'
