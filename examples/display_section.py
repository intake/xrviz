import xarray as xr
from xrviz.display.section import Display

ds = xr.open_dataset("../xrviz/sample_data/great_lakes.nc")

display = Display(ds)
display.show()