import xarray as xr
import xrviz
from xrviz.dashboard import Dashboard
from xrviz.sample_data import great_lakes

ds = great_lakes
ds = ds.set_coords(['lat', 'lon'])
dash = Dashboard(ds)
dash.control.displayer.select_variable('temp')
dash.show()
