Set Coords
===========

.. image:: _static/images/set_coords.png

This pane allows the list of data coordinates to be modified by adding
or removing variables using the ``<<`` and ``>>`` widgets.

It uses a `Cross Selector <https://panel.pyviz.org/reference/widgets/CrossSelector.html>`_
to display a list of simple and coordinate variables.
Simple variables (which are not data coordinates) are available on
left side and default coordinates are available on right side.
To set variables as coordinates, make selection on left side and click
``>>``. Similarly making selection on right side and clicking ``<<``
will reset the coordinates. Other panes would update themselves accordingly, in
response to this change.

.. _`xarray coordinates`: http://xarray.pydata.org/en/stable/data-structures.html#coordinates
