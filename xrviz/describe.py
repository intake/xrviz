from jinja2 import Environment, FileSystemLoader
import panel as pn
import os
import sys
import xarray as xr
from .sigslot import SigSlot


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
        self.data = data
        self.panel = pn.pane.HTML(min_width=500, height=400, css_classes=['xrviz-scroll'])
        self.panel.object = "Description Section"

    def setup(self, var):
        self.panel.object = self.data

    def set_coords(self, data, var):
        self.data = data
        if var is not None:
            self.setup(var=[var])
