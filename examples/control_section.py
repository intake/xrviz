import xarray as xr
import xrviz
from xrviz.control import Control

ds = xrviz.sample_data.great_lakes
ds = ds.set_coords(['lat', 'lon'])

control = Control(ds)
control.show()
