import pytest
import panel as pn
from geoviews import tile_sources as gvts
from xrviz.projection import Projection, projections_list, accepted_proj_params


@pytest.fixture()
def projection():
    return Projection()


@pytest.mark.parametrize("wid, wid_type, attrs_values",
                         [('is_geo', pn.widgets.Checkbox,
                           [('name', 'is_geo'), ('value', False),
                            ('disabled', True)]),
                          ('alpha', pn.widgets.FloatSlider,
                           [('name', 'alpha'), ('start', 0), ('end', 1),
                            ('step', 0.01), ('value', 0.7), ('width', 180)]),
                          ('show_map', pn.widgets.Checkbox,
                           [('name', 'show_map'), ('value', False),
                            ('width', 100)]),
                          ('basemap', pn.widgets.Select,
                           [('name', 'basemap'),
                            ('options', gvts.tile_sources),
                            ('value', gvts.OSM), ('disabled', True)]),
                          ('projection', pn.widgets.Select,
                           [('name', 'projection'),
                            ('options', projections_list),
                            ('value', 'PlateCarree')]),
                          ('crs', pn.widgets.Select,
                           [('name', 'crs'),
                            ('options', [None] + sorted(projections_list)),
                            ('value', None)]),
                          ('rasterize', pn.widgets.Checkbox,
                           [('name', 'rasterize'), ('value', True)]),
                          ('project', pn.widgets.Checkbox,
                           [('name', 'project'), ('value', False)]),
                          ('global_extent', pn.widgets.Checkbox,
                           [('name', 'global_extent'), ('value', False)]),
                          ('features', pn.widgets.MultiSelect,
                           [('name', 'features'),
                            ('options', ['None', 'borders', 'coastline',
                                         'grid', 'land', 'lakes',
                                         'ocean', 'rivers']),
                            ('value', ['borders', 'coastline',
                                       'grid', 'land', 'lakes',
                                       'ocean', 'rivers'])]) ])
def test_widget(projection, wid, wid_type, attrs_values):
    assert isinstance(projection.is_geo, pn.widgets.Checkbox)
    widget = getattr(projection, wid)
    assert isinstance(widget, wid_type)
    for attr_val in attrs_values:
        assert getattr(widget, attr_val[0]) == attr_val[1]


def test_setup_geo_disabled(projection):
    disabled_val = True
    projection.is_geo.disabled = True
    projection.setup()
    for row in projection.panel[1:]:
        for widget in row:
            assert widget.disabled is True
    assert projection.show_map.value is False
    assert projection.basemap.disabled is True


def test_setup_geo_changed_to_False(projection):
    projection.is_geo.disabled = False
    projection.is_geo.value = False
    for row in projection.panel[1:]:
        for widget in row:
            assert widget.disabled is True
    assert projection.show_map.value is False
    assert projection.basemap.disabled is True


def test_setup_geo_changed_to_True(projection):
    projection.is_geo.disabled = False
    projection.is_geo.value = True
    for row in projection.panel[1:]:
        for widget in row:
            if widget.name == 'basemap':
                assert widget.disabled is True
            else:
                assert widget.disabled is False


def test_show_basemap(projection):
    projection.is_geo.disabled = False
    projection.is_geo.value = True
    for value in [False, True]:
        projection.show_map.value = value
        assert projection.basemap.disabled is not value
        assert projection.projection.disabled is value
        assert projection.crs.disabled is value
        for widget in projection.proj_params:
            widget.disabled is value
        projection.features.value is [projection.feature_ops[0]] if value else projection.feature_ops[1:]


def test_add_proj_params(projection):
    projection.is_geo.disabled = False
    sample_projs = ['PlateCarree', 'Orthographic', 'EuroPP']
    for proj_value in sample_projs:
        projection.projection.value = proj_value
        accepted_params = accepted_proj_params(proj_value)
        for widget in projection.proj_params:
            assert widget.name in accepted_params


def test_set_project(projection):
    projection.is_geo.disabled = False
    projection.is_geo.value = True
    for value in [True, False]:
        projection.rasterize.value = value
        assert projection.project.disabled is not value
