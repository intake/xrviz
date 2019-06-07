import xarray as xr
import xrviz
from xrviz.dashboard import Dashboard

ds = xrviz.sample_data.great_lakes
ds = ds.set_coords(['lat', 'lon'])

dash = Dashboard(ds)
dash.show()
