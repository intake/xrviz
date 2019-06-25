import pytest
from xrviz.describe import Describe
from . import data


def test_describe_initial(data):
    describer = Describe(data)
    assert describer.panel.object == "Description Area"
