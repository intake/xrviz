import pytest
import panel as pn
from xrviz.style import Style
from holoviews.plotting import list_cmaps


@pytest.fixture()
def style():
    return Style()


def test_height(style):
    h_widget = style.height
    assert isinstance(h_widget, pn.widgets.IntSlider)
    assert h_widget.name == 'height'
    assert h_widget.value == 300
    assert h_widget.start == 100
    assert h_widget.end == 1200


def test_width(style):
    w_widget = style.width
    assert isinstance(w_widget, pn.widgets.IntSlider)
    assert w_widget.name == 'width'
    assert w_widget.value == 700
    assert w_widget.start == 100
    assert w_widget.end == 1200


def test_cmap(style):
    cmap_widget = style.cmap
    assert isinstance(cmap_widget, pn.widgets.Select)
    assert cmap_widget.name == 'cmap'
    assert cmap_widget.value == 'Inferno'
    assert cmap_widget.options == list_cmaps()


def test_colorbar(style):
    cbar_widget = style.colorbar
    assert isinstance(cbar_widget, pn.widgets.Checkbox)
    assert cbar_widget.name == 'colorbar'
    assert cbar_widget.value is True


def test_lower_limit(style):
    l_lim_widget = style.lower_limit
    assert isinstance(l_lim_widget, pn.widgets.TextInput)
    assert l_lim_widget.name == 'cmap lower limit'
    assert l_lim_widget.width == 140


def test_upper_limit(style):
    u_lim_widget = style.upper_limit
    assert isinstance(u_lim_widget, pn.widgets.TextInput)
    assert u_lim_widget.name == 'cmap upper limit'
    assert u_lim_widget.width == 140


def test_use_all_data(style):
    use_data_widget = style.use_all_data
    assert isinstance(use_data_widget, pn.widgets.Checkbox)
    assert use_data_widget.name == 'compute min/max from all data'
    assert use_data_widget.value is False


def test_color_scale(style):
    cs_widget = style.color_scale
    assert isinstance(cs_widget, pn.widgets.Select)
    assert cs_widget.name == 'color_scale'
    assert cs_widget.value == 'linear'
    scaling_ops = ['linear', 'exp', 'log', 'reciprocal', 'square', 'sqrt']
    assert cs_widget.options == scaling_ops


def test_rasterize(style):
    raster_wid = style.rasterize
    assert isinstance(raster_wid, pn.widgets.Checkbox)
    assert raster_wid.name == 'rasterize'
    assert raster_wid.value is True


def test_setup(style):
    style.lower_limit.value = '123'
    style.upper_limit.value = '123'
    style._emit('clear_cmap_limits', '')
    assert style.lower_limit.value is None
    assert style.upper_limit.value is None
