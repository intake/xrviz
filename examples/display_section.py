import xarray as xr
import xrviz
from xrviz.display import Display

ds = xrviz.sample_data.great_lakes

display = Display(ds)
display.show()
