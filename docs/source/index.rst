XrViz
=====

*An interactive visualisation interface for Xarrays*

XrViz is an interactive, in browser visualisation interface for Xarrays backed
by the full power of the Python ecosystem. It is built on `Xarray <http://xarray.pydata.org>`_,
`HvPlot <https://hvplot.pyviz.org>`_ and `Panel <https://panel.pyviz.org/>`_.
It can be used with `Intake <http://intake.readthedocs.io/>`_
to smoothen the process of investigating and loading datasets.

It offers the following functionality:

1. Quick visualization of xarray data.
2. No need to write any custom code thus saves immense time of users.
3. Different tabs to customize the output graph by interaction with
   the widgets.
4. Easy exploration of data present on cloud using Xarray's ability
   to read remote data.
5. Easy exploration of geographical, meteorological, and oceanographic
   datasets using `Geoviews <http://geoviews.org/>`_.
6. Automatic guessing of correct coordinates for ``x`` and ``y`` axis using
   `Metpy <https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.html>`_.
7. Aggregations along remaining dimensions in case of multi-dimensional
   variables.
8. Extract series for third dimension in a separate graph by clicking on
   the main 2D graphical output.

.. toctree::
   :maxdepth: 2
   :caption: Documentation Contents

   quickstart.rst
   variables.rst
   set_coords.rst
   axes.rst
   style.rst
   projection.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`