from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np

from ..utils._checks import check_type
from ..utils.logs import logger

if TYPE_CHECKING:
    from np.typing import NDArray


def randomization(var_groups: list[NDArray[np.float64]], var_subject: float) -> int:
    """Randomize the new subject within the list of groups.

    The procedure attempts to minimize the between group variance of the provided
    variable.

    Parameters
    ----------
    var_groups : list of arrays of shape (n_group, n_subject)
        List of groups, each containing the subjects value of the variable to minimize.
        For instance, if the goal is to minimize the variance of the SCARED score, then
        each array contains the SCARED score of the subject within that group.
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
    # - else, we will look for the group which minimizes the variance of the variable.
    group_sizes = np.array([elt.size for elt in var_groups])
    min_size = np.min(group_sizes)
    if np.sum(group_sizes == min_size) == 1:
        return np.argmin(group_sizes)
    # now, we passed all the special case and we will finally look for the group which
    # minimizes the variance of the variable of interest, but first, we need to exclude
    # all the groups which already have one more subject than the others.
    if np.sum(group_sizes == min_size) == group_sizes.size:
        mask = np.ones(len(var_groups), dtype=bool)
    else:
        mask = group_sizes == min_size
    var_groups_considered = [var for k, var in enumerate(var_groups) if mask[k]]
    variances = np.zeros(len(var_groups_considered), dtype=np.float64)
    for k, group in enumerate(var_groups_considered):
        # temporary add the participant to the group considered
        temp_groups = deepcopy(var_groups_considered)
        temp_groups[k] = np.append(np.copy(group), var_subject)
        # compute the total mean and the variance between groups
        mean_total = np.mean(np.hstack(temp_groups))
        variances[k] = np.sum(
            [len(group) * (np.mean(group) - mean_total) ** 2 for group in temp_groups]
        )
    # find the group which minimizes the variance between groups
    idx = np.argmin(variances)
    return np.where(mask)[0][idx]
