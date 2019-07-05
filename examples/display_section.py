import xarray as xr
import xrviz
from xrviz.display import Display
from xrviz.sample_data import great_lakes

ds = great_lakes

display = Display(ds)
display.show()
