XrViz
=====

*An interactive visualisation interface for Xarrays*

XrViz is an interactive graphical user interface(GUI) for visually browsing Xarrays.
You can view data arrays along various dimensions, examine data values, change
color maps, extract series, display geographic data on maps and much more.
It is built on `Xarray <http://xarray.pydata.org>`_,
`HvPlot <https://hvplot.pyviz.org>`_ and `Panel <https://panel.pyviz.org/>`_.
It can be used with `Intake <http://intake.readthedocs.io/>`_
to smooth the process of investigating and loading datasets.

.. image:: _static/images/dashboard.png

It offers the following functionality:

1. Quick visualization of xarray data.
2. Widgets to customize the visualization
3. Mapping of geospatial datasets using `Geoviews <http://geoviews.org/>`_.
4. Automatic determination of geospatial coordinates using
   `Metpy <https://unidata.github.io/MetPy/latest/api/generated/metpy.calc.html>`_
   for data following the CF conventions.
5. Ability to aggregate along non-map dimensions (e.g. compute the mean or max)
6. Extract series for non-mapped dimensions (e.g. generate a time series at a point by clicking on
   the mapped data. 

.. toctree::
   :maxdepth: 2
   :caption: Documentation Contents

   quickstart.rst
   interface
   set_initial_parameters
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
