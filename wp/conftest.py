from __future__ import annotations  # c.f. PEP 563, PEP 649

import os
import warnings
from importlib.resources import files
from typing import TYPE_CHECKING

from pytest import fixture

from .utils.logs import logger

if TYPE_CHECKING:
    from pathlib import Path

    from pytest import Config


def pytest_configure(config: Config) -> None:
    """Configure pytest options."""
    warnings_lines = r"""
    error::
    """
    for warning_line in warnings_lines.split("\n"):
        warning_line = warning_line.strip()
        if warning_line and not warning_line.startswith("#"):
            config.addinivalue_line("filterwarnings", warning_line)
    logger.propagate = True


@fixture(scope="session")
def matplotlib_config():
    """Configure matplotlib for viz tests.

    Allow for simple interactive debugging with a call like:

        $ WP_MPL_TESTING_BACKEND=Qt5Agg pytest wp/tests/test_viz -k line -x --pdb
    """
    import matplotlib
    from matplotlib import cbook

    try:
        want = os.environ["WP_MPL_TESTING_BACKEND"]
    except KeyError:
        want = "agg"  # don't pop up windows
    with warnings.catch_warnings(record=True):  # ignore warning
        warnings.filterwarnings("ignore")
        matplotlib.use(want, force=True)
    import matplotlib.pyplot as plt

    assert plt.get_backend() == want
    # overwrite some params that can horribly slow down tests that users might have
    # changed locally (but should not otherwise affect functionality)
    plt.ioff()
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["figure.raise_window"] = False

    # make sure that we always reraise exceptions in handlers
    orig = cbook.CallbackRegistry

    class CallbackRegistryReraise(orig):
        def __init__(self, exception_handler=None, signals=None):
            super().__init__(exception_handler)

    cbook.CallbackRegistry = CallbackRegistryReraise


@fixture(autouse=True)
def close_all():
    """Close all matplotlib plots, regardless of test status."""
    import matplotlib.pyplot as plt

    yield
    plt.close("all")


@fixture(scope="session")
def gametime_dataframe_fname() -> Path:
    """Return the path of a gametime dataset."""
    return files("wp.gametime.tests") / "data" / "gametime.csv"
