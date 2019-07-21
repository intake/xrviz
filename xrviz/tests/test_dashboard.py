import xarray as xr
import panel as pn
from xrviz.dashboard import Dashboard
import pytest
from . import data
from ..utils import _is_coord
from ..compatibility import has_cartopy


@pytest.fixture(scope='module')
def dashboard(data):
    return Dashboard(data)


@pytest.fixture(scope='module')
def dash_for_Array(data):
    return Dashboard(data.temp)


def test_dashboard_with_invalid_datatype():
    with pytest.raises(ValueError):
        Dashboard(str)


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


def test_2d_variable_for_dims(dashboard):
    dashboard.control.displayer.select_variable('lat')
    fields = dashboard.control.fields
    assert fields.x.value == 'nx'
    assert fields.y.value == 'ny'
    assert [agg_sel.name for agg_sel in fields.agg_selectors] == []
    dashboard.plot_button.clicks += 1
    graph = dashboard.output[0]
    assert isinstance(graph, pn.pane.holoviews.HoloViews)
    assert [index_sel for index_sel in dashboard.output[1]] == []


def test_3d_variable_for_dims(dashboard):
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
                         ['dashboard', 'dash_for_Array'],
                         indirect=True)
def test_4d_variable_for_dims(dashboard):
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


def test_link_aggregation_selectors(dashboard):
    dashboard.control.displayer.select_variable('temp')
    llim = dashboard.control.style.lower_limit
    ulim = dashboard.control.style.upper_limit
    llim.value = '10'
    ulim.value = '20'
    agg_sel = dashboard.control.fields.agg_selectors[0]
    agg_sel.value = 'mean'
    assert llim.value is None
    assert ulim.value is None


def test_set_coords(dashboard):
    new_coords = sorted(['time', 'sigma', 'lat', 'lon'])
    dashboard.control.coord_setter.coord_selector.value = new_coords
    assert sorted(list(dashboard.data.coords)) == new_coords


def test_animate_wigdet_for_dims(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    fields = dashboard.control.fields
    agg_selectors = fields.agg_selectors
    agg_selectors[0].value = 'animate'
    dashboard.create_plot()
    assert isinstance(dashboard.output[0], pn.pane.holoviews.HoloViews)
    assert isinstance(dashboard.output[1][0][1], pn.widgets.player.DiscretePlayer)


@pytest.mark.skipif(not has_cartopy, reason='cartopy not present')
def test_with_is_geo_projection(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    dashboard.control.displayer.select_variable('temp')
    proj_panel = dashboard.control.projection
    proj_panel.is_geo.value = True
    proj_panel.projection.value = 'Orthographic'
    proj_panel.proj_params.value = "{'central_longitude': -78, 'central_latitude': 43, 'globe': None}"
    proj_panel.global_extent.value = True
    dashboard.create_plot()
    assert isinstance(dashboard.output[0], pn.pane.holoviews.HoloViews)
    assert isinstance(dashboard.output[1][0], pn.widgets.select.Select)


@pytest.mark.skipif(not has_cartopy, reason='cartopy not present')
def test_with_is_geo_basemap(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    dashboard.control.displayer.select_variable('temp')
    proj_panel = dashboard.control.projection
    proj_panel.is_geo.value = True
    dashboard.create_plot()
    assert isinstance(dashboard.output[0], pn.pane.holoviews.HoloViews)
    assert isinstance(dashboard.output[1][0], pn.widgets.select.Select)


def test_with_aggregations_for_dims(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    fields = dashboard.control.fields
    agg_selectors = fields.agg_selectors
    agg_selectors[0].value = 'max'
    agg_selectors[1].value = 'count'
    dashboard.plot_button.clicks += 1
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_with_aggregations_for_coords(dashboard):
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    agg_selectors = dashboard.control.fields.agg_selectors
    agg_selectors[0].value = 'max'
    agg_selectors[1].value = 'count'
    dashboard.plot_button.clicks += 1
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_color_scaling_for_dims(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    style = dashboard.control.style
    style.color_scale.value = 'log'
    dashboard.create_plot()
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_color_scaling_for_coords(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    dashboard.control.displayer.select_variable('temp')
    style = dashboard.control.style
    style.color_scale.value = 'log'
    dashboard.create_plot()
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_use_all_data_for_dims(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.style.use_all_data.value = True
    dashboard.create_plot()
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_use_all_data_for_coords(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.style.use_all_data.value = True
    dashboard.create_plot()
    assert isinstance(dashboard.output[0][0], pn.pane.holoviews.HoloViews)


def test_create_taps_and_series_graph_for_dims(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['time', 'sigma']
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.fields.s_selector.value = 'sigma'
    dashboard.create_plot()
    dashboard.create_taps_graph(x=35, y=10)
    assert isinstance(dashboard.series_graph[0], pn.pane.holoviews.HoloViews)


def test_create_taps_and_series_graph_for_2d_coords(dashboard):
    dashboard.control.coord_setter.coord_selector.value = ['lat', 'lon']
    dashboard.control.displayer.select_variable('temp')
    dashboard.control.fields.s_selector.value = 'sigma'
    dashboard.create_plot()
    dashboard.create_taps_graph(x=-79.232, y=43.273)
    assert isinstance(dashboard.series_graph[0], pn.pane.holoviews.HoloViews)
