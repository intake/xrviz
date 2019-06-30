from . import sample_data

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def example():
    import xarray as xr
    from . import dashboard
    ds = sample_data.great_lakes
    dash = dashboard.Dashboard(ds)
    dash.show()
