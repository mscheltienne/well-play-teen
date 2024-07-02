from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from ..average import randomization

if TYPE_CHECKING:
    from numpy.typing import NDArray


@pytest.fixture
def var_groups_extreme() -> list[NDArray[np.float64]]:
    """Return a list of groups with extreme values."""
    return [
        np.array([1, 2, 3], dtype=np.float64),
        np.array([35, 36, 37], dtype=np.float64),
        np.array([70, 71, 72], dtype=np.float64),
    ]


@pytest.mark.xfail(reason="This test is expected to fail.")
@pytest.mark.filterwarnings("ignore:Do not use this function*:RuntimeWarning")
@pytest.mark.parametrize("var_and_result", [(4.0, 2), (75.0, 0), (34.0, 2), (38.0, 0)])
def test_randomization_extreme_assignments(
    var_groups_extreme: list[NDArray[np.float64]], var_and_result: tuple[float, int]
) -> None:
    """Test randomization method."""
    var, result = var_and_result
    idx = randomization(var_groups_extreme, var)
    assert idx == result


@pytest.mark.filterwarnings("ignore:Do not use this function*:RuntimeWarning")
def test_randomization_unbalanced_subject_per_group() -> None:
    """Test randomization method."""
    var_groups = [
        np.array([1, 2, 3], dtype=np.float64),
        np.array([35, 36, 37], dtype=np.float64),
        np.array([70, 71], dtype=np.float64),
    ]
    idx = randomization(var_groups, 80.0)
    assert idx == 2

    var_groups = [
        np.array([1, 2, 3], dtype=np.float64),
        np.array([36, 37], dtype=np.float64),
        np.array([70, 71], dtype=np.float64),
    ]
    idx = randomization(var_groups, 80.0)
    assert idx == 1
