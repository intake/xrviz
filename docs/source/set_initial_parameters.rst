Set Initial Parameters
======================

Users may need to inialize the widgets present in dashboard
with custom values instead of the defaults. This could be
done by passing initial parametes to the `Dashboard` upon
initialization. All the parametes are passed using the argument
``initial_params`` which is of type ``dict``.

The keys present in ``initial_params`` must match with the name of
the widgets, whose values you want to change. Also the value passed
must be present in the available options of that widget. All the keys
must be of type ``str``.

Example:

.. code-block:: python

    from .sample_data import great_lakes
    initial_params = {# Select Variable
                      'Variables': 'temp',

                      # Set Coords
                      'Set Coords': ['lat', 'lon'],

                      # Axes
                      'x': 'lon',
                      'y': 'lat',
                      'sigma': 'animate',

                      # Style
                      'height': 300,
                      'width': 650,
                      'colorbar': True,
                      'cmap': 'Viridis',

                      # Projection
                      'is_geo': True,
                      'basemap': 'OSM',
                      'crs': 'PlateCarree',
                      'projection': 'Orthographic',
                      'crs params': "{'central_longitude': 0.0}",
                      'projection params': "{'central_longitude': -78, 'central_latitude': 43, 'globe': {'ellipse':'sphere'}"
                      }
    dash = Dashboard(great_lakes, initial_params=initial_params)
    dash.show()

Here ``crs params`` and ``projection params`` need more attention.
The parameter passed to these must be accepted by the selected projection
as defined in `cartopy projections`_.

.. _`cartopy projections`: https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html
