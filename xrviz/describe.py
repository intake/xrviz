from jinja2 import Environment, FileSystemLoader
import panel as pn
import os
import sys
import xarray as xr
from .sigslot import SigSlot

CSS = """
.xrviz-scroll {
  overflow: scroll;
}
"""

class Describe(SigSlot):
    """
    Displays the properties of the variable selected in the Display section.

    This section has two tables as output. The first table shows
    `Variable attributes` and the second table shows `Global Attributes`.
    Upon selection of a new variable in the Display widget, the first table
    updates itself with properties of the new selection,
    while the second table stays same.

    Parameters
    ----------

    data: xarray.DataSet

    Attributes
    ----------

    panel:
        A ``panel.pane.HTML`` instance which displays the tables arranged
        next to each other.

    """
    def __init__(self, data):
        super().__init__()
        xr.set_options(display_style='html')
        pn.extension(raw_css=[CSS])
        self.data = data
        self.panel = pn.pane.HTML(min_width=500, max_height=250, css_classes=['xrviz-scroll'])
        self.panel.object = "Description Section"
        self.setup()

    def setup(self, var=None):
        self.panel.object = self.data[[var]] if var is not None else self.data

    def set_coords(self, data, var):
        self.data = data
        self.setup(var)
