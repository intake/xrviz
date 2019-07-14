import logging

logger = logging.getLogger('xrviz')

try:
    from cartopy import crs as ccrs
    import geoviews as gv
    import geoviews.feature as gf
    has_cartopy = True
except ImportError:
    logger.debug("Install Cartopy, Geoviews to view Projection Panel.")
    has_cartopy = False
    ccrs, gv, gf = None, None, None


try:
    import metpy.calc as mpcalc
except ImportError:
    logger.debug("""
    Metpy is not installed, so XrViz cannot automatically guess the best
    dimensions for output x and y axes. To install metpy, you can execute
    the following:
        `pip install metpy`
            or
        `conda install -c conda-forge metpy pint pooch --no-deps`
    """)
    mpcalc = None
