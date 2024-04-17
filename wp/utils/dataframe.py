import pandas as pd

from ..config import STEAM_BEJEWELED_APP_ID, STEAM_ECO_RESCUE_APP_ID
from ._checks import check_gametime_dataframe, check_type
from .logs import warn

_GAME_IDs_MAPPING = {
    str(STEAM_ECO_RESCUE_APP_ID): "Ecorescue",
    str(STEAM_BEJEWELED_APP_ID): "Bejeweled",
}


def prepare_dataframe(
    df: pd.DataFrame,
    steam_ids_mapping: dict[str, str],
) -> pd.DataFrame:
    """Prepare a gametime dataframe by mapping steam IDs and game IDs."""
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


def select_steam_ids(df: pd.DataFrame, steam_ids: list[str] | tuple[str, ...]):
    """Select steam IDs from the dataframe."""
    check_gametime_dataframe(df)
    check_type(steam_ids, (list, tuple), "steam_ids")
    for steam_id in steam_ids:
        check_type(steam_id, (str,), "steam_id")
    df = df[df["steam_id"].isin(steam_ids)]
    df.reset_index(drop=True, inplace=True)
    return df


def select_datetimes(
    df: pd.DataFrame,
    start: str | pd.Timestamp | None,
    stop: str | pd.Timestamp | None,
    freq: str | pd.Timedelta | None = None,
) -> pd.DataFrame:
    """Select and resample datetimes from the dataframe."""
    check_gametime_dataframe(df)
    check_type(start, (str, pd.Timestamp, None), "start")
    check_type(stop, (str, pd.Timestamp, None), "stop")
    check_type(freq, (str, pd.Timedelta, None), "freq")
    if isinstance(start, str):  # 'YYYY-MM-DD HH:MM:SS'
        start = pd.Timestamp(start, tz="utc")
    if isinstance(stop, str):  # 'YYYY-MM-DD HH:MM:SS'
        stop = pd.Timestamp(stop, tz="utc")
    if start is not None and stop is not None and stop < start:
        raise ValueError("The stop datetime must be greater than the start datetime.")
    start = df["acq_time"].min() if start is None else start
    stop = df["acq_time"].max() if stop is None else stop
    mask = (start <= df["acq_time"]) & (df["acq_time"] <= stop)
    df = df.loc[mask]
    if freq is not None:
        idx = list()
        for dt in pd.date_range(start, stop, freq=freq):
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
