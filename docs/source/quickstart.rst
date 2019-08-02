Quickstart
==========

Installation
------------

If you are using `Anaconda`_ or Miniconda::

    conda install -c conda-forge xrviz

If you are using virtualenv/pip::

    pip install xrviz

Note that this will install with the mininum of optional requirements.
If you want a more complete install, use conda instead.

If you want to develop::

    git clone https://github.com/intake/xrviz
    cd xrviz
    pip install -e .

.. _Anaconda: https://www.anaconda.com/download/


Example
-------

To open a local or remote data in the interface:

.. code-block:: python

    import xarray as xr
    from xrviz.dashboard import Dashboard

    # open data with xarray
    data = xr.tutorial.open_dataset('air_temperature')

    # or open remote data with xarray
    url = 'http://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/LOOFS/MODELS/201907/glofs.loofs.fields.forecast.20190720.t06z.nc'
    data = xr.open_dataset(url)

    # pass the data to Dashboard
    dash = Dashboard(data)
    dash.show()


Note that ``dash.show()`` will open a new tab in browser, while
``dash.panel`` is applicable only for a jupyter cell.

You can view the example dashboard by running following in command line
(this will open a tab in your browser)::

    python -c "import xrviz; xrviz.example()"

The above line will initialise the interface, which looks as follows:

.. image:: https://aws-uswest2-binder.pangeo.io/badge_logo.svg
   :target: https://aws-uswest2-binder.pangeo.io/badge_logo.svg)](https://aws-uswest2-binder.pangeo.io/v2/gh/hdsingh/explore_xrviz/master?filepath=01_great_lakes.ipynb

Overview
--------

.. overview of what the interface is, the structure/layout and purpose.

The user input section of the interface constitutes of five sub-sections
composed of `Panel widgets <https://panel.pyviz.org/reference/index.html#widgets>`_.
These sub-sections have been arranged in tabs, each of which has been described
in detail in the following sections:

1. :ref:`interface:variables`
2. :ref:`interface:Set_Coords`
3. :ref:`interface:axes`
4. :ref:`interface:style`
5. :ref:`interface:projection`

The user can interact with the widgets present in these panes to select
desired inputs. Together, they govern the output produced upon pressing
the ``Plot`` button.
