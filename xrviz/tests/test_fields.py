import pytest
import panel as pn
from xrviz.fields import Fields
from . import data


@pytest.fixture()
def fields(data):
    return Fields(data)


@pytest.fixture()
def fields_array(data):
    return Fields(data.temp)


@pytest.mark.parametrize('fields',
                         ['fields', 'fields_array'],
                         indirect=True)
def test_fields_initial(fields):
    assert fields.x.value is None
    assert fields.y.value is None
    assert fields.panel.name == 'Axes'
    assert fields.panel[0][0].object == '### Plot Dimensions'
    assert isinstance(fields.panel[1], pn.Spacer)
    assert fields.panel[2][0].object == '### Aggregations'
