API
===

Variables
---------

.. autoclass:: xrviz.display.Display
   :members: __init__, select_variable

.. autoclass:: xrviz.describe.Describe
   :members: __init__, variable_pane_for_dataset

Set_Coords
----------

.. autoclass:: xrviz.coord_setter.CoordSetter
   :members: __init__

Axes
----

.. autoclass:: xrviz.fields.Fields
   :members: __init__, setup, change_y, change_dim_selectors, check_are_var_coords, guess_x_y

Style
-----

.. autoclass:: xrviz.style.Style
   :members: __init__, setup_initial_values

Projection
----------

.. autoclass:: xrviz.projection.Projection
   :members: __init__, setup, setup_initial_values, show_basemap

Control
-------

.. autoclass:: xrviz.control.Control
   :members: __init__, setup_initial_values, set_coords

Dashboard
---------

.. autoclass:: xrviz.dashboard.Dashboard
   :members: __init__, create_plot, create_indexed_graph, create_selectors_players,
             create_taps_graph, create_series_graph, clear_series, link_aggregation_selectors,
             check_is_plottable

Example
-------

.. autofunction::
   xrviz.example
