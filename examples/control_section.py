import xarray as xr
import xrviz
from xrviz.dashboard import Dashboard

ds = xrviz.sample_data.great_lakes

dash = Dashboard(ds)
dash.show()
