import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
import requests
from numpy.testing import assert_allclose

from wp.gametime._config import (
    _BACKUP_DAYS,
    _STEAM_BEJEWELED_APP_ID,
    _STEAM_ECO_RESCUE_APP_ID,
    DF_DTYPES,
)
from wp.gametime.acquisition import (
    _URL,
    clean_backup_and_logs,
    fetch_gametime,
    update_gametime_dataset,
)


@pytest.fixture(scope="function")
def folder(tmp_path):
    """Create folder with logs and backups."""
    backup = tmp_path / "backup"
    logs = tmp_path / "logs"
    backup.mkdir()
    logs.mkdir()
    now = datetime.now()
    for dt in (
        now,
        now - timedelta(days=_BACKUP_DAYS - 1),
        now - timedelta(days=_BACKUP_DAYS),
    ):
        dt = dt.strftime("%Y%m%d-%H%M%S")
        with open(backup / f"gametime_{dt}.csv", "w") as fid:
            fid.write("This is a csv file.")
        with open(logs / f"gametime_{dt}.log", "w") as fid:
            fid.write("This is a log file.")
    return tmp_path


@pytest.fixture(scope="session")
def steam_id():
    """Return a steam id."""
    return "7656119832958027"


def requires_recent_played_games(steam_id: str):
    """Skip test if games were not played in the last 2 weeks."""
    response = requests.get(
        _URL.format(steam_id),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=10,
    )
    status_code = response.status_code
    reason = response.reason
    if not response.ok:  # True if status code is inferior to 400
        pytest.skip(
            f"Request response not OK. Status code: {status_code}, Reason: {reason}."
        )
    response = response.json()
    if "response" not in response:
        pytest.skip("Incomplete request response.")
    response = response["response"]
    if len(response) == 0:
        pytest.skip(f"No recently played games found on steam ID {steam_id}.")
    games = response.get("games", [])
    ids = [game.get("appid", -1) for game in games]
    if _STEAM_BEJEWELED_APP_ID not in ids or _STEAM_ECO_RESCUE_APP_ID not in ids:
        pytest.skip(
            "Requires both games to be played in the last 2 weeks on steam "
            f"ID {steam_id}."
        )


def test_clean_backup_and_logs(folder):
    """Test cleaning of backups and log folders."""
    log_files1 = [elt.name for elt in (folder / "logs").iterdir()]
    backup_files1 = [elt.name for elt in (folder / "backup").iterdir()]
    clean_backup_and_logs(folder)
    log_files2 = [elt.name for elt in (folder / "logs").iterdir()]
    backup_files2 = [elt.name for elt in (folder / "backup").iterdir()]
    assert len(log_files1) == 3
    assert len(backup_files1) == 3
    assert len(log_files2) == 2
    assert len(backup_files2) == 2


def test_fetch_gametime(steam_id):
    """Test fetching the playtime for both games."""
    requires_recent_played_games(steam_id)
    gt = fetch_gametime(steam_id, _STEAM_BEJEWELED_APP_ID)
    assert 0 < gt
    time.sleep(0.1)
    gt = fetch_gametime(steam_id, _STEAM_ECO_RESCUE_APP_ID)
    assert 0 < gt


def test_fetch_gametime_invalid_steam_id():
    """Test fetching the playtime with an invalid steam ID."""
    with pytest.warns(RuntimeWarning, match="Failed to fetch user"):
        gt = fetch_gametime("76561199999999999", _STEAM_BEJEWELED_APP_ID)
    assert gt is np.nan


def test_update_gametime_dataset(tmp_path, steam_id):
    """Test updating the gametime dataset."""
    requires_recent_played_games(steam_id)
    assert not (tmp_path / "gametime.csv").exists()
    assert not (tmp_path / "backup").exists()
    assert not (tmp_path / "logs").exists()
    with pytest.warns(RuntimeWarning, match="No gametime dataset found"):
        update_gametime_dataset(tmp_path, [steam_id], [])
    assert (tmp_path / "gametime.csv").exists()
    assert len([elt for elt in (tmp_path / "backup").iterdir()]) == 0
    assert len([elt for elt in (tmp_path / "logs").iterdir()]) == 1
    df = pd.read_csv(
        tmp_path / "gametime.csv",
        index_col=0,
        dtype=DF_DTYPES,
        parse_dates=["acq_time"],
    )
    assert df.shape == (1, 5)
    assert np.isnan(df["game_time_diff"].values).all()
    assert 0 < df["game_time"].values[0]
    # add second query of the same game
    update_gametime_dataset(tmp_path, [steam_id], [])
    df = pd.read_csv(
        tmp_path / "gametime.csv",
        index_col=0,
        dtype=DF_DTYPES,
        parse_dates=["acq_time"],
    )
    assert df.shape == (2, 5)
    assert_allclose(df["game_time_diff"].values, [np.nan, 0], equal_nan=True)
    assert np.all(0 < df["game_time"].values)
    # add third query with different game
    update_gametime_dataset(tmp_path, [], [steam_id])
    df = pd.read_csv(
        tmp_path / "gametime.csv",
        index_col=0,
        dtype=DF_DTYPES,
        parse_dates=["acq_time"],
    )
    # don't bother checking something else than the shape, we are not suppose to call
    # the same steam ID with both games
    assert df.shape == (3, 5)


def test_update_gametime_dataset_invalid(tmp_path, steam_id):
    """Test updating the gametime dataset with invalid inputs."""
    with pytest.raises(ValueError, match="The same 'steam_id'"):
        update_gametime_dataset(tmp_path, [steam_id], [steam_id])
    with pytest.raises(ValueError, match="At least one steam_id"):
        update_gametime_dataset(tmp_path, [], [])
