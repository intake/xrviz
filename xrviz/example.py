from .dashboard import Dashboard


def example(show=True):
    """
    Generates interface for the sample dataset.

    Parameters
    ----------
    show: bool (True)
        Whether to directly execute the interface. If True, a new browser tab
        will be opened, and the function will block until interrupted. If
        False, the Dashboard instance is returned without being executed.
    """
    from .sample_data import great_lakes

    great_lakes = great_lakes.set_coords(['lat', 'lon'])
    initial_params = {'Variables': 'temp',
                      'Set Coords': ['lat', 'lon'],
                      'x': 'lon',
                      'y': 'lat',
                      'sigma': 'animate',

                      # style
                      'height': 400,
                      'width': 700,
                      'colorbar': False,
                      # projection

                      'is_geo': True,
                      'crs': 'PlateCarree',
                      'projection': 'Orthographic',
                      'crs params': {'central_longitude': 0.0},
                      'projection params': {'central_longitude': -78,
                                            'central_latitude': 43,
                                            'globe': None}}
    dash = Dashboard(great_lakes, initial_params=initial_params)
    if show:
        dash.show()
    return dash
