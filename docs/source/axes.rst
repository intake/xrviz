Axes
====

.. image:: _static/images/axes.png

This panel provides the options to select the axes to plot along.
Upon selecting a new variable in ``Displayer``, the options available
in this panel would update automatically.
It has three different sub-sections.

1. Plot Dimensions
------------------
It has following two selectors:

- ``x``: To select x-axis for the plot.
- ``y``: To select y-axis for the plot.

``x`` selector has both variable dims and coordinates available
as options. However, the options in y would be available according
to selection made in ``x``. If the selection in ``x`` is a dimension,
``y`` will have remaining dimensions as options. Similarly, for the
case when a coordinate has been selected in ``x``, only remaining
coordinates will be available in ``y``.

The default value of ``x`` and ``y`` is filled according to
guess made using `Metpy`_.


2. Aggregations
---------------


3. Extract Along
----------------

.. _Metpy: https://unidata.github.io/MetPy
