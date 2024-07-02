from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np

from ..utils._checks import check_type
from ..utils.logs import logger, warn

if TYPE_CHECKING:
    from np.typing import NDArray


def randomization(var_groups: list[NDArray[np.float64]], var_subject: float) -> int:
    """Randomize the new subject within the list of groups.

    The procedure attempts to minimize the average of the provided variable.

    Parameters
    ----------
    var_groups : list of arrays of shape (n_group, n_subject)
        List of groups, each containing the subjects value of the variable to minimize.
        The list length defines the number of group to consider, thus empty groups must
        be provided as empty array.
    var_subject : float
        Value of the variable to minimize for the new subject.

    Returns
    -------
    idx : int
        Index of the group where the new subject has been randomized, in respect to the
        groups within var_groups.
    """
    warn("Do not use this function. It corresponds to the erroneous code on Wave.")
    check_type(var_groups, (list,), "var_groups")
    for var in var_groups:
        check_type(var, (np.ndarray,), "var_groups")
        if var.ndim != 1:
            raise ValueError("Argument 'var_groups' must be a list of 1D arrays.")
    check_type(var_subject, ("numeric",), "var_subject")
    logger.info(
        "Randomizing new subject within the list of %i groups.", len(var_groups)
    )
    rng = np.random.default_rng()
    # first, we look for empty groups which will receive the new participant in priority
    # regardless of the variable to minimize.
    empty = [k for k, elt in enumerate(var_groups) if elt.size == 0]
    if len(empty) != 0:
        return rng.choice(empty)
    # if there is no empty-group, we will separate 2 cases:
    # - a single group has one less subject than the others, in which case it will
    #   automatically receive the participant regardless of the variable to minimize.
    # - else, we will look for the group which minimizes the average of the variable.
    group_sizes = np.array([elt.size for elt in var_groups])
    min_size = np.min(group_sizes)
    mask = group_sizes == min_size
    if np.sum(mask) == 1:
        return np.argmin(group_sizes)
    # now, we passed all the special case and we will finally look for the group which
    # minimizes the average of the variable of interest, but first, we need to exclude
    # all the groups which already have one more subject than the others.
    var_groups_considered = [var for k, var in enumerate(var_groups) if mask[k]]
    averages = np.zeros(len(var_groups_considered), dtype=np.float64)
    for k, group in enumerate(var_groups_considered):
        # temporary add the participant to the group considered
        temp_groups = deepcopy(var_groups_considered)
        temp_groups[k] = np.append(np.copy(group), var_subject)
        # compute the mean of the group
        averages[k] = np.mean(temp_groups[k])
    # find the group which minimizes the average
    idx = np.argmin(averages)
    return np.where(mask)[0][idx]
