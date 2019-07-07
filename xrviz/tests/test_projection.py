import pytest
import panel as pn
from geoviews import tile_sources as gvts
from xrviz.projection import Projection, projections_list


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
                           [('name', 'project'), ('value', True)]),
                          ('global_extent', pn.widgets.Checkbox,
                           [('name', 'global_extent'), ('value', False)]),
                          ('features', pn.widgets.MultiSelect,
                           [('name', 'features'),
                            ('options', ['None', 'borders', 'coastline',
                                         'grid', 'land', 'lakes',
                                         'ocean', 'rivers']),
                            ('value', ['borders', 'coastline',
                                       'grid', 'land', 'lakes',
                                       'ocean', 'rivers'])])
                         ]
                        )
def test_widget(projection, wid, wid_type, attrs_values):
    assert isinstance(projection.is_geo, pn.widgets.Checkbox)
    widget = getattr(projection, wid)
    assert isinstance(widget, wid_type)
    for attr_val in attrs_values:
        assert getattr(widget, attr_val[0]) == attr_val[1]
