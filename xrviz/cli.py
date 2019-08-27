import sys

def main():
    usage = "Usage: `xrviz show datafile/url`"
    if len(sys.argv) ==3 and 'show' == sys.argv[1]:
        import xarray as xr
        from .dashboard import Dashboard

        try:
            data = xr.open_dataset(sys.argv[2])
        except:
            print("Unable to open the datafile/url.", usage)
            sys.exit()
        dash = Dashboard(data)
        dash.show()
    else:
        print(usage)
