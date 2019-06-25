import panel as pn
import pytest
from panel.widgets import DiscretePlayer, DiscreteSlider, Select
from ..utils import convert_widget, player_with_name_and_value


@pytest.mark.parametrize("source_widget,target_widget",
                         [(Select, DiscretePlayer),
                          (DiscreteSlider, Select),
                          (DiscretePlayer, Select),
                          (DiscreteSlider, DiscretePlayer)])
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


def test_player_with_name_and_value():
    options = ['a', 'b', 'c']
    name = "Player1"
    player = pn.widgets.DiscretePlayer(name=name,
                                       value=options[0],
                                       options=options)
    out = player_with_name_and_value(player)
    out_markdown_name = out[0][0]
    assert out_markdown_name.object == player.name
    # Upon changing the value of player, markdown also changes to
    # represent the same
    player.value = 'c'
    out_markdown_value = out[0][1]
    assert out_markdown_value.object == player.value
