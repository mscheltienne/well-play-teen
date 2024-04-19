from __future__ import annotations

from datetime import datetime, timedelta
from shutil import copy2
from time import sleep
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import requests

from ..utils._checks import check_gametime_dataframe, check_type, ensure_path
from ..utils._docs import fill_doc
from ..utils.logs import add_file_handler, logger, verbose, warn
from ._config import (
    _BACKUP_DAYS,
    _STEAM_API_KEY,
    _STEAM_BEJEWELED_APP_ID,
    _STEAM_ECO_RESCUE_APP_ID,
    DF_DTYPES,
)

if TYPE_CHECKING:
    from pathlib import Path


_URL = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={_STEAM_API_KEY}&steamid={{}}&format=json"  # noqa: E501


@fill_doc
@verbose
def fetch_gametime(
    steam_id: str,
    game_id: int,
    *,
    verbose: bool | str | int | None = None,
) -> int | np.nan:
    """Fetch the playtime for a game and user on Steam.

    Parameters
    ----------
    steam_id : str
        The Steam ID of the user (format 64 decimal).
    game_id : int
        The game app ID.
    %(verbose)s

    Returns
    -------
    gametime : int
        Total gametime in minutes. np.nan is returned if the API requests failed or if
        the game was not found in the recent games list.
    """
    logger.info("Fetching gametime for '%s'.", steam_id)
    try:
        response = requests.get(
            _URL.format(steam_id),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=10,
        )
        status_code = response.status_code
        reason = response.reason
        if not response.ok:  # True if status code is inferior to 400
            raise RuntimeError(
                "The steam API did not returned a successful response. "
                f"Status code: {status_code}, Reason: {reason}."
            )
        response = response.json()
        if "response" not in response:  # should never happen if response.ok
            raise RuntimeError(
                "The steam API returned an unexpected response lacking the root key "
                f"'response'. Status code: {status_code}, Reason: {reason}."
            )
        response = response["response"]
        if len(response) == 0:
            raise RuntimeError(
                "The steam API returned a valid but empty response. Hint: check the "
                "steam id and public/private settings of the steam account. "
                f"Status code: {status_code}, Reason: {reason}."
            )
    except Exception as error:
        warn(
            f"Failed to fetch user '{steam_id}' information. Check the logs for the "
            "error traceback."
        )
        logger.exception(error)
        return np.nan
    games = response.get("games", [])
    for game in games:
        if game.get("appid", -1) == game_id:
            return game.get("playtime_forever", 0)
    else:
        warn(
            f"Game '{game_id}' not found in user's '{steam_id}' recently played games."
        )
        return np.nan


def update_gametime_dataset(
    folder: str | Path,
    steam_ids_ecorescue: list[str] | tuple[str, ...],
    steam_ids_bejeweled: list[str] | tuple[str, ...],
) -> None:
    """Update the gametime dataset in-place, with backup and logging.

    Parameters
    ----------
    folder : str | Path
        Path to the folder containing the dataset.
    steam_ids_ecorescue : list of str | tuple of str
        List of Steam IDs to fetch ecorescue gametime for (format 64 decimal).
    steam_ids_bejeweled : list of str | tuple of str
        List of Steam IDs to fetch bejeweled gametime for (format 64 decimal).
    """
    folder = ensure_path(folder, must_exist=True)
    fname = ensure_path(folder / "gametime.csv", must_exist=False)
    check_type(steam_ids_ecorescue, (list, tuple), "steam_ids_ecorescue")
    for elt in steam_ids_ecorescue:
        check_type(elt, (str,), "steam_id_ecorescue")
    check_type(steam_ids_bejeweled, (list, tuple), "steam_ids_bejeweled")
    for elt in steam_ids_ecorescue:
        check_type(elt, (str,), "steam_id_bejeweled")
    if len(steam_ids_ecorescue) == 0 and len(steam_ids_bejeweled) == 0:
        raise ValueError("At least one steam_id must be provided.")
    if len(set(steam_ids_ecorescue) & set(steam_ids_bejeweled)):
        raise ValueError("The same 'steam_id' cannot be used for both games.")
    # check backup and logs folder
    backup = folder / "backup"
    backup.mkdir(exist_ok=True)
    logs = folder / "logs"
    logs.mkdir(exist_ok=True)
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    add_file_handler(logs / f"gametime_{now}.log")
    # define dataset structure and load existing dataset
    dataset = {"steam_id": [], "acq_time": [], "game_time": [], "game_id": []}
    try:
        df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])
        check_gametime_dataframe(df)
        df.drop(labels="game_time_diff", axis=1, inplace=True)
    except FileNotFoundError:
        warn("No gametime dataset found. Creating a new one.")
        df = pd.DataFrame(dataset)
    except pd.errors.EmptyDataError:
        warn("Empty gametime dataset.")
        df = pd.DataFrame(dataset)
    # fetch new datapoints
    ts = pd.Timestamp.now(tz="utc").round("s")  # simpler for visualization and triage
    for steam_ids, game_id in (
        (steam_ids_ecorescue, _STEAM_ECO_RESCUE_APP_ID),
        (steam_ids_bejeweled, _STEAM_BEJEWELED_APP_ID),
    ):
        for steam_id in steam_ids:
            dataset["steam_id"].append(steam_id)
            dataset["acq_time"].append(ts)
            dataset["game_time"].append(
                fetch_gametime(steam_id, game_id, verbose="INFO")
            )
            dataset["game_id"].append(game_id)
            sleep(1)
    # concatenate, compute gametime deltas and save
    df = _concatenate_dataframes(df, pd.DataFrame(dataset))
    if fname.exists():
        copy2(fname, backup / f"gametime_{now}.csv")
    df.to_csv(fname)
    clean_backup_and_logs(folder, verbose="INFO")
    logger.handlers[-1].close()


def _concatenate_dataframes(df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """Concatenate both dataframes, add difference and clean-up edge cases."""
    if df.size == 0:
        diff = new_df.groupby("steam_id")["game_time"].diff().rename("game_time_diff")
        return pd.concat([new_df, diff], axis=1)
    # in case the game was not played recently, we need to look through our dataset
    for idx in new_df["game_time"].isna().index:
        sid = new_df.iloc[idx]["steam_id"]
        sel = df[df["steam_id"] == sid]
        if sel.size == 0:
            continue
        new_df.at[idx, "game_time"] = sel.iloc[-1]["game_time"]
    # concatenate and compute difference
    df = pd.concat((df, new_df), ignore_index=True)
    diff = df.groupby("steam_id")["game_time"].diff().rename("game_time_diff")
    df = pd.concat([df, diff], axis=1)
    return df


@fill_doc
@verbose
def clean_backup_and_logs(
    folder: str | Path, *, verbose: bool | str | int | None = None
) -> None:
    """Remove old backups and logs.

    Parameters
    ----------
    folder : str | Path
        Path to the folder containing the dataset.
    %(verbose)s
    """
    folder = ensure_path(folder, must_exist=True)
    backup = ensure_path(folder / "backup", must_exist=True)
    logs = ensure_path(folder / "logs", must_exist=True)
    for folder in (backup, logs):
        finfo = []
        for file in folder.iterdir():
            try:
                dt = datetime.strptime(
                    file.stem.removeprefix("gametime_"), "%Y%m%d-%H%M%S"
                )
            except Exception:
                warn(f"Skipping file '{file.name}' with unexpected name format.")
                continue
            finfo.append((dt, file))
        for dt, file in finfo:
            if timedelta(days=_BACKUP_DAYS) < datetime.now() - dt:
                logger.info("Removing old file '%s'.", file.name)
                file.unlink(missing_ok=False)
