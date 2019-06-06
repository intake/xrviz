import xarray as xr
import xrviz
from xrviz.control import Control

ds = xrviz.sample_data.great_lakes

control = Control(ds)
control.show()
