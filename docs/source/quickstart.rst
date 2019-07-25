Quickstart
==========

This guide will show you how to get started using XrViz
to explore your xarray data.

Installation
------------

If you are using `Anaconda`_ or Miniconda, install Intake
with the following commands::

    conda install -c conda-forge xrviz
    pip install git+https://github.com/intake/xrviz --no-deps

If you are using virtualenv/pip, run the following command::

    pip install git+https://github.com/intake/xrviz

Note that this will install with the mininum of optional requirements.
If you want a more complete install, use conda instead.

.. _Anaconda: https://www.anaconda.com/download/


Example
-------

View the example dashboard by running following in command line::

    python -c "import xrviz; xrviz.example()"

See the example dashboard:

.. image:: https://aws-uswest2-binder.pangeo.io/badge_logo.svg
   :target: https://aws-uswest2-binder.pangeo.io/badge_logo.svg)](https://aws-uswest2-binder.pangeo.io/v2/gh/hdsingh/explore_xrviz/master?filepath=01_great_lakes.ipynb

Panels
------

The following five panels are part of XrViz's interface:

1. :doc:`variables`
2. :doc:`set_coords`
3. :doc:`axes`
4. :doc:`style`
5. :doc:`projection`
