from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from ..minvar import randomization

if TYPE_CHECKING:
    from numpy.typing import NDArray


@pytest.fixture
def var_groups_extreme() -> list[NDArray[np.float64]]:
    """Return a list of groups with extreme values."""
    return [np.array([1, 2, 3]), np.array([35, 36, 37]), np.array([70, 71, 72])]


@pytest.mark.parametrize("var_and_result", [(4.0, 2), (75.0, 0), (34.0, 2), (38.0, 0)])
def test_randomization_extreme_assignments(
    var_groups_extreme: list[NDArray[np.float64]], var_and_result: tuple[float, int]
) -> None:
    """Test randomization method."""
    var, result = var_and_result
    idx = randomization(var_groups_extreme, var)
    assert idx == result


def test_randomization_unbalanced_subject_per_group() -> None:
    """Test randomization method."""
    var_groups = [np.array([1, 2, 3]), np.array([35, 36, 37]), np.array([70, 71])]
    idx = randomization(var_groups, 80.0)
    assert idx == 2

    var_groups = [np.array([1, 2, 3]), np.array([36, 37]), np.array([70, 71])]
    idx = randomization(var_groups, 80.0)
    assert idx == 1
