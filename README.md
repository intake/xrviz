# XrViz

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/xrviz/badges/installer/conda.svg)](https://conda.anaconda.org/conda-forge)
[![PyPI version](https://badge.fury.io/py/xrviz.svg)](https://badge.fury.io/py/xrviz)
[![Build Status](https://travis-ci.org/intake/xrviz.svg?branch=master)](https://travis-ci.org/intake/xrviz)
[![Documentation Status](https://readthedocs.org/projects/xrviz/badge/?version=latest)](https://xrviz.readthedocs.io/en/latest/?badge=latest)
[![Gitter](https://badges.gitter.im/ESIP_GUI/community.svg)](https://gitter.im/ESIP_GUI/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

XrViz is an interactive graphical user interface(GUI) for visually browsing Xarrays.
You can view data arrays along various dimensions, examine data values, change
color maps, extract series, display geographic data on maps and much more.
It is built on [Xarray](http://xarray.pydata.org),
[HvPlot](https://hvplot.pyviz.org) and [Panel](https://panel.pyviz.org/).
It can be used with [Intake](http://intake.readthedocs.io/)
to ease the process of investigating and loading datasets.


Documentation is available at [Read the Docs](https://xrviz.readthedocs.io).
Try it out on binder: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/intake/xrviz/master?filepath=examples%2Fgreat_lakes.ipynb)

<img src="https://raw.githubusercontent.com/intake/xrviz/master/docs/source/_static/images/dashboard.png" data-canonical-src="https://raw.githubusercontent.com/intake/xrviz/master/docs/source/_static/images/dashboard.png" width="800"/><br>

### Installation

Recommended method using conda:
```
conda install -c conda-forge xrviz
```

You can also install using pip:
```
pip install xrviz
```

### Usage
You can view the example dashboard by running following in command line (this will open a tab in your browser):

```
python -c "import xrviz; xrviz.example()"
```
