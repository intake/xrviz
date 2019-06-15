import panel as pn
import pytest
from panel.widgets import DiscretePlayer, DiscreteSlider, Select
from ..utils import convert_widget


@pytest.mark.parametrize("source_widget,target_widget",
                         [(Select, DiscretePlayer),
                          (DiscreteSlider, Select),
                          (DiscretePlayer, Select)])
def test_convert_widget(source_widget, target_widget):
    name = 'Alphabets'
    options = ['A', 'B', 'C', 'D']
    value = options[0]
    source = source_widget(name=name,
                           options=options,
                           value=value)

    target = convert_widget(source, target_widget())
    assert isinstance(target, target_widget)
    assert target.name is source.name
    assert target.options is source.options

    # change target's value and check if source's also change
    target.value = options[1]
    assert target.value is source.value
