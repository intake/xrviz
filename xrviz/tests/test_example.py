from .. import example
from xrviz.dashboard import Dashboard


def test_dashboard_example():
    dash = example(False)
    assert isinstance(dash, Dashboard)
