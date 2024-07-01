from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from ..utils._checks import (
    check_gametime_dataframe,
    check_type,
    check_value,
    ensure_int,
    ensure_path,
)
from ..utils._docs import fill_doc
from ..utils.logs import warn
from ._config import _GAME_IDs_MAPPING

if TYPE_CHECKING:
    from pathlib import Path


def load_metadata(fname: str | Path):
    """Load the metadata from a .csv file."""
    fname = ensure_path(fname, must_exist=True)
    raise NotImplementedError


@fill_doc
def prepare_dataframe(
    df: pd.DataFrame,
    steam_ids_mapping: dict[str, str],
) -> pd.DataFrame:
    """Prepare a gametime dataframe by mapping steam IDs and game IDs.

    Parameters
    ----------
    %(df_gametime)s
    steam_ids_mapping : dict of str
        Mapping between a steam ID (str) to a username or token (str). The steam IDs
        in the column 'steam_id' will be replaced by the values in this dictionary.

    Returns
    -------
    %(df_gametime)s

    Examples
    --------
    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import prepare_dataframe
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = prepare_dataframe(df, {"76561198329580271": "necromancia"})
    """
    check_gametime_dataframe(df)
    check_type(steam_ids_mapping, (dict,), "steam_ids_mapping")
    for key, value in steam_ids_mapping.items():
        check_type(key, (str,), "steam_ids_mapping key")
        check_type(value, (str,), "steam_ids_mapping value")
    # map game IDs
    ids = sorted(df["game_id"].unique())
    ids_warn = [
        elt
        for elt in ids
        if elt not in list(_GAME_IDs_MAPPING) + list(_GAME_IDs_MAPPING.values())
    ]
    if len(ids_warn) != 0:
        warn(f"Unexpected game IDs in the dataframe: {ids_warn}.")
    mapping = {key: _GAME_IDs_MAPPING.get(key, key) for key in ids}
    df.loc[:, "game_id"] = df["game_id"].map(mapping)
    # map steam IDs
    ids = sorted(df["steam_id"].unique())
    mapping = {key: steam_ids_mapping.get(key, key) for key in ids}
    df.loc[:, "steam_id"] = df["steam_id"].map(mapping)
    return df


@fill_doc
def select_steam_ids(df: pd.DataFrame, steam_ids: list[str] | tuple[str, ...]):
    """Select steam IDs from the dataframe.

    Parameters
    ----------
    %(df_gametime)s
    steam_ids : list of str | tuple of str
        List of steam IDs to select.

    Returns
    -------
    %(df_gametime)s

    Examples
    --------
    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import select_steam_ids
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = select_steam_ids(df, ["76561198329580271", "76561198329580272"])

    This function can be called after 'prepare_dataframe':

    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import prepare_dataframe, select_steam_ids
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = prepare_dataframe(df, {"76561198329580271": "necromancia"})
    >>> df = select_steam_ids(df, ["necromancia"])
    """
    check_gametime_dataframe(df)
    check_type(steam_ids, (list, tuple), "steam_ids")
    for steam_id in steam_ids:
        check_type(steam_id, (str,), "steam_id")
    df = df[df["steam_id"].isin(steam_ids)]
    df.reset_index(drop=True, inplace=True)
    return df


@fill_doc
def select_datetimes(
    df: pd.DataFrame,
    start: str | pd.Timestamp | None = None,
    end: str | pd.Timestamp | None = None,
    freq: str | pd.Timedelta | None = None,
) -> pd.DataFrame:
    """Select and resample datetimes from the dataframe.

    Parameters
    ----------
    %(df_gametime)s
    start : str | pd.Timestamp | None
        Start datetime to select. If None, the minimum datetime in the dataframe is
        used. If a string is provided, it should be in the format 'YYYY-MM-DD HH:MM:SS'.
        In the string format, part of the string can be omitted, for instance
        'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'.
    end : str | pd.Timestamp | None
        End datetime to select. If None, the maximum datetime in the dataframe is
        used. If a string is provided, it should be in the format 'YYYY-MM-DD HH:MM:SS'.
        In the string format, part of the string can be omitted, for instance
        'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'.
    freq : str | pd.Timedelta | None
        Frequency to resample the datetimes. If None, no resampling is performed. If a
        string is provided, it should be in the format 'XU', where 'X' is an integer and
        'U' is a unit ('min', 'h', 'D', 'W'). If a Timedelta is provided, it is used
        directly.

    Returns
    -------
    %(df_gametime)s

    Notes
    -----
    Resampling the dataset will create a range from 'start' to 'end' (included) with
    the desired frequency. Then, it selects the rows with the closest 'acq_time' to
    each of the resampled datetimes. Finally, it re-computes the game_time_diff column
    with the new resolution.

    Examples
    --------
    Selection of all samples between 01/05/2024 and 10/05/2024:

    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import select_datetimes
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = select_datetimes(df, start="2024-05-01", end="2024-05-10")

    Selection of all samples between 01/05/2024 and 10/05/2024, resampled every 6 hours:

    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import select_datetimes
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = select_datetimes(df, start="2024-05-01", end="2024-05-10", freq="6h")
    """
    check_gametime_dataframe(df)
    check_type(start, (str, pd.Timestamp, None), "start")
    check_type(end, (str, pd.Timestamp, None), "end")
    check_type(freq, (str, pd.Timedelta, None), "freq")
    if start is None and end is None and freq is None:
        raise RuntimeError(
            "No selection or resampling requested. At least one argument among "
            "'start', 'end' and 'freq' must be provided."
        )
    if isinstance(start, str):
        start = pd.Timestamp(start, tz="utc")
    if isinstance(end, str):
        end = pd.Timestamp(end, tz="utc")
    if start is not None and end is not None and end < start:
        raise ValueError("The end datetime must be greater than the start datetime.")
    start = df["acq_time"].min() if start is None else start
    end = df["acq_time"].max() if end is None else end
    mask = (start <= df["acq_time"]) & (df["acq_time"] <= end)
    df = df.loc[mask]
    if freq is not None:
        idx = list()
        for dt in pd.date_range(start, end, freq=freq):
            series = abs(df["acq_time"] - dt)
            idx.extend(list(series[series == series.min()].index))
        if len(idx) != len(set(idx)):
            warn(
                "Duplicate indices found. Pay attention to the resampling frequency "
                f"requested '{freq}'. Dropping duplicates."
            )
        idx = sorted(set(idx))
        df = df.loc[idx]
        # and now we need to recompute the game_time_diff
        df.drop(labels="game_time_diff", axis=1, inplace=True)
        diff = df.groupby("steam_id")["game_time"].diff().rename("game_time_diff")
        df = pd.concat([df, diff], axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


@fill_doc
def select_gametimes(
    df: pd.DataFrame,
    start_dates: dict[str, str | pd.Timestamp],
    rule: str,
    amount: int,
    all_weeks: bool = True,
) -> list[str]:
    """Select steam IDs that satisfy a gametime comparison rule.

    Parameters
    ----------
    %(df_gametime)s
    start_dates : dict
        Mapping of steam IDs to the date (UTC) at which they start the play-phase.
        The date is either provided as a pd.Timestamp or as a string in the format:
        'YYYY-MM-DD'. The keys restrict the selection to the given steam IDs.
    rule : str
        Gametime comparison filter rule to apply. The following rules are available:
        - '<': less than the amount of gametime.
        - '<=': less than or equal to the amount of gametime.
        - '>': greater than the amount of gametime.
        - '>=': greater than or equal to the amount of gametime.
    amount : int
        Amount of gametime to compare.
    all_weeks : bool
        If True, the comparison must be true for all completed weeks. If False, the
        comparison must be true for any week completed.

    Returns
    -------
    steam_ids : list of str
        List of steam IDs that satisfy the gametime comparison rule.

    Examples
    --------
    Selection of all steam IDs that played less than 2 hours in any week:

    >>> import pandas as pd
    >>>
    >>> from wp.gametime import DF_DTYPE
    >>> from wp.gametime.selection import select_gametimes
    >>>
    >>> df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
    >>> df = select_gametimes(
    ...     df,
    ...     start_dates={"necromancia": "2024-05-01"},
    ...     rule="<",
    ...     amount=2,
    ...     all_weeks=False,
    ... )
    """
    check_gametime_dataframe(df)
    check_type(start_dates, (dict,), "start_dates")
    for key, value in start_dates.items():
        check_type(key, (str,), "start_dates key")
        check_value(key, df["steam_id"].unique(), "start_dates key")
        check_type(value, (str, pd.Timestamp), "start_dates value")
    check_type(rule, (str,), "rule")
    check_value(rule, ["<", "<=", ">", ">="], "rule")
    amount = ensure_int(amount, "amount")
    if amount <= 0:
        raise ValueError("The amount of gametime must be strictly positive.")
    check_type(all_weeks, (bool,), "all_weeks")
    # convert to timestamps, confirm that hours, minute and second are set to 0, else
    # warn and round
    for key, value in start_dates.items():
        if isinstance(value, str):
            value = pd.Timestamp(value, tz="utc")
        if value.hour != 0 or value.minute != 0 or value.second != 0:
            warn(
                f"Start date for {key} is not at midnight 00:00:00. Rounding to the "
                "nearest day."
            )
        start_dates[key] = value.round("1D")
    # select and compare, sadly groupby is difficult to use here since the start_date
    # is different for every participant
    df = select_steam_ids(df, list(start_dates))
    steam_ids = []
    for steam_id in df["steam_id"].unique():
        df_ = select_steam_ids(df.copy(deep=True), [steam_id])
        df_ = select_datetimes(df_, start_dates[steam_id], end=None, freq="1D")
        start = start_dates[steam_id]
        if df_["acq_time"].max() < start + pd.Timedelta(weeks=1):
            continue  # required to avoid jumping to the else statement
        while start + pd.Timedelta(weeks=1) <= df_["acq_time"].max():
            df_week = select_datetimes(
                df_.copy(deep=True), start, start + pd.Timedelta(weeks=1)
            )
            if _compare(df_week, rule, amount) and not all_weeks:
                steam_ids.append(steam_id)
                break
            elif not _compare(df_week, rule, amount) and all_weeks:
                break
            start += pd.Timedelta(weeks=1)
        else:
            steam_ids.append(steam_id)
    return steam_ids


def _compare(df: pd.DataFrame, rule: str, amount: int) -> bool:
    """Compare gametimes according to the set rule."""
    if rule == "<":
        return df["game_time_diff"].sum() < amount
    elif rule == "<=":
        return df["game_time_diff"].sum() <= amount
    elif rule == ">":
        return df["game_time_diff"].sum() > amount
    elif rule == ">=":
        return df["game_time_diff"].sum() >= amount
