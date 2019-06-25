import xarray as xr
import panel as pn
from xrviz.dashboard import Dashboard
import pytest
from . import data
from ..utils import _is_coord


@pytest.fixture(scope='module')
def dashboard(data):
    return Dashboard(data)


@pytest.fixture(scope='module')
def dash_for_Array(data):
    return Dashboard(data.temp)


def test_check_is_plottable_1D(dashboard):
    # `validtime` is 1D variable
    dashboard.plot_button.disabled = False
    dashboard.control.displayer.select_variable('validtime')
    assert dashboard.plot_button.disabled


def test_check_is_plottable_coord(dashboard):
    # `time` is data coordinate
    dashboard.plot_button.disabled = False
    dashboard.control.displayer.select_variable('time')
    assert dashboard.plot_button.disabled


def test_check_is_plottable_other_vars(dashboard):
    # `temp` is neither 1D nor coordinate
    dashboard.plot_button.disabled = True
    dashboard.control.displayer.select_variable('temp')
    assert dashboard.plot_button.disabled is False


def test_2d_variable(dashboard):
    dashboard.control.displayer.select_variable('lat')
    fields = dashboard.control.fields
    assert fields.x.value == 'nx'
    assert fields.y.value == 'ny'
    assert [agg_sel.name for agg_sel in fields.agg_selectors] == []
    dashboard.plot_button.clicks += 1
    graph = dashboard.output[0]
    assert isinstance(graph, pn.pane.holoviews.HoloViews)
    assert [index_sel for index_sel in dashboard.output[1]] == []


def test_3d_variable(dashboard):
    dashboard.control.displayer.select_variable('air_v')
    fields = dashboard.control.fields
    assert fields.x.value == 'nx'
    assert fields.y.value == 'ny'
    agg_selectors = [agg_sel.name for agg_sel in fields.agg_selectors]
    assert agg_selectors == ['time']
    dashboard.plot_button.clicks += 1
    graph = dashboard.output[0]
    assert isinstance(graph, pn.pane.holoviews.HoloViews)
    index_selectors = [index_sel.name for index_sel in dashboard.output[1]]
    assert index_selectors == ['time']


@pytest.mark.parametrize('dashboard',
                         ['dashboard','dash_for_Array'],
                         indirect=True)
def test_4d_variable(dashboard):
    dashboard.control.displayer.select_variable('temp')
    fields = dashboard.control.fields
    assert fields.x.value == 'nx'
    assert fields.y.value == 'ny'
    agg_selectors = [agg_sel.name for agg_sel in fields.agg_selectors]
    assert agg_selectors == ['sigma', 'time']
    dashboard.plot_button.clicks += 1
    graph = dashboard.output[0]
    assert isinstance(graph, pn.pane.holoviews.HoloViews)
    index_selectors = [index_sel.name for index_sel in dashboard.output[1]]
    assert index_selectors == ['sigma', 'time']
