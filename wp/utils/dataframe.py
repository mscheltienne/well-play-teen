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


def df_select_steam_ids(df, steam_ids: list[str] | tuple[str, ...]):
    """Select steam IDs from the dataframe."""
    check_gametime_dataframe(df)
    check_type(steam_ids, (list, tuple), "steam_ids")
    for steam_id in steam_ids:
        check_type(steam_id, (str,), "steam_id")
    df = df[df["steam_id"].isin(steam_ids)]
    return df


def df_select_datetimes(
    df, start: str | pd.Timestamp | None, stop: str | pd.Timestamp | None
) -> pd.DataFrame:
    """Select datetimes from the dataframe."""
    check_gametime_dataframe(df)
    check_type(start, (str, pd.Timestamp, None), "start")
    check_type(stop, (str, pd.Timestamp, None), "stop")
    if isinstance(start, str):  # 'YYYY-MM-DD HH:MM:SS'
        start = pd.Timestamp(start, tz="utc")
    if isinstance(stop, str):  # 'YYYY-MM-DD HH:MM:SS'
        stop = pd.Timestamp(stop, tz="utc")
    if start is not None and stop is not None:
        if stop < start:
            raise ValueError(
                "The stop datetime must be greater than the start datetime."
            )
        mask = (start <= df["acq_time"]) & (df["acq_time"] <= stop)
    elif start is None and stop is not None:
        mask = df["acq_time"] <= stop
    elif start is not None and stop is None:
        mask = start <= df["acq_time"]
    else:
        return df
    return df.loc[mask]
