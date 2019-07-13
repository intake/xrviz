import xarray as xr
import xrviz.sample_data
from xrviz.display import Display

ds = xrviz.sample_data.great_lakes

display = Display(ds)
display.show()
