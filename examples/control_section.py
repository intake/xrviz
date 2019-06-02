import xarray as xr
from xrviz.control import Control

ds = xr.open_dataset("../xrviz/sample_data/great_lakes.nc")

control = Control(ds)
control.show()
