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

    dash = Dashboard(great_lakes)
    if show:
        dash.show()
    return dash
