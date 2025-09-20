from importlib.metadata import version

import postinfer as pi


def test_version():
    assert version('postinfer') == pi.__version__
