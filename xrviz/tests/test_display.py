import xarray as xr
from xrviz.display import Display


def test_fill_items():
    data = xr.open_dataset("xrviz/sample_data/great_lakes.nc")

    def in_DataSet(data):
        displayer = Display(data)
        for prop in ['# DataSet', '└── Dimensions', '└── Coordinates', '└── Variables', '└── Attributes']:
            assert prop in displayer.select.options

    def in_DataArray(data):
        displayer = Display(data)
        assert 'DataArray : air_u' in displayer.select.options

    in_DataSet(data)
    in_DataArray(data.air_u)
