from . import sample_data

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def example(show=True):
    """
    Generates interface for the sample dataset.

    Parameters
    ----------
    show: True (by default): Directly opens the interface in a browser
          False : Returns the interface(dashboard) object
            Usage:
            ```
            dash = xrviz.example(show = False)
            dash.panel  # To display interface in Jupyter Notebook
            ```
    """
    import xarray as xr
    from . import dashboard
    ds = sample_data.great_lakes
    dash = dashboard.Dashboard(ds)
    return dash.show() if show else dash
