API
===

Variables
---------

.. autoclass:: xrviz.display.Display
   :members: select_variable

.. autoclass:: xrviz.describe.Describe
   :members: variable_pane_for_dataset

Set_Coords
----------

.. autoclass:: xrviz.coord_setter.CoordSetter
   :members: set_coords, setup_initial_values

Axes
----

.. autoclass:: xrviz.fields.Fields
   :members: setup, change_y, change_dim_selectors, check_are_var_coords, guess_x_y

Style
-----

.. autoclass:: xrviz.style.Style
   :members: setup_initial_values

Projection
----------

.. autoclass:: xrviz.projection.Projection
   :members: setup_initial_values

Control
-------

.. autoclass:: xrviz.control.Control
   :members: set_coords, check_is_projectable

Dashboard
---------

.. autoclass:: xrviz.dashboard.Dashboard
   :members: create_graph, create_indexed_graph, create_selectors_players,
             create_taps_graph, create_series_graph, clear_series,
             check_is_plottable

Example
-------

.. autofunction::
   xrviz.example
