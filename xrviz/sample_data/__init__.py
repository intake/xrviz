import os
import xarray as xr

great_lakes = xr.open_dataset(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__)+'/great_lakes.nc')))
