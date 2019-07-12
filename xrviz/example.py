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
    initial_params = {'projection_ops': {'is_geo': True,
                                         'projection': 'Orthographic',
                                         'proj_params': {'central_longitude': -78, 
                                                         'central_latitude': 43}},
                      # 'style_ops': {'height': 400,
                      #               'width': 800}
                      }

    dash = Dashboard(great_lakes, initial_params=initial_params)
    if show:
        dash.show()
    return dash
