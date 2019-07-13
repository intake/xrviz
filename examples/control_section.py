import xarray as xr
import xrviz.sample_data
from xrviz.dashboard import Dashboard

ds = xrviz.sample_data.great_lakes

dash = Dashboard(ds)
dash.show()
