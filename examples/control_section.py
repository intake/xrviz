import xarray as xr
import xrviz
from xrviz.dashboard import Dashboard
from xrviz.sample_data import great_lakes

ds = great_lakes

dash = Dashboard(ds)
dash.show()
