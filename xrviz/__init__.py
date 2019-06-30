from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


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
    import xarray as xr
    from . import sample_data
    from . import dashboard
    ds = sample_data.great_lakes
    dash = dashboard.Dashboard(ds)
    if show:
        dash.show()
    return dash
