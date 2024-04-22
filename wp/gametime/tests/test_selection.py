import numpy as np
import pandas as pd
import pytest

from wp.gametime._config import DF_DTYPES, _GAME_IDs_MAPPING
from wp.gametime.selection import (
    prepare_dataframe,
    select_datetimes,
    select_gametimes,
    select_steam_ids,
)


@pytest.fixture(scope="function")
def mock_df_select_gametimes(gametime_dataframe_fname) -> pd.DataFrame:
    """Create a mock dataset for selection of gametimes."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df.loc[:, "steam_id"] = "76561198329580271"
    df.loc[:, "game_id"] = "2163350"
    start = df["acq_time"].min()
    for k in df.index:
        df.loc[k, "acq_time"] = start + pd.Timedelta(hours=6 * k)
        df.loc[k, "game_time"] = 60 * k  # 1h every 6h
    # recompute the game_time_diff
    df.drop(labels="game_time_diff", axis=1, inplace=True)
    diff = df.groupby("steam_id")["game_time"].diff().rename("game_time_diff")
    df = pd.concat([df, diff], axis=1)
    df.reset_index(drop=True, inplace=True)
    return df


def test_prepare_dataframe(gametime_dataframe_fname):
    """Test preparation of a dataframe."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = prepare_dataframe(df, dict())
    assert sorted(df["game_id"].unique()) == sorted(_GAME_IDs_MAPPING.values())
    assert sorted(df["steam_id"].unique()) == sorted(df["steam_id"].unique())

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    ids = sorted(df["steam_id"].unique())
    mapping = {ids[0]: "999"}  # 999 will be sorted at the end
    df = prepare_dataframe(df, mapping)
    assert sorted(df["game_id"].unique()) == sorted(_GAME_IDs_MAPPING.values())
    assert sorted(df["steam_id"].unique()) == ids[1:] + ["999"]

    # test warning with invalid game IDs
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = df.to_dict()
    df["game_id"][0] = "99"  # will be sorted first
    df = pd.DataFrame(df)
    with pytest.warns(RuntimeWarning, match="Unexpected game IDs in the dataframe"):
        df = prepare_dataframe(df, dict())
    assert sorted(df["game_id"].unique()) == ["99"] + sorted(_GAME_IDs_MAPPING.values())
    assert sorted(df["steam_id"].unique()) == sorted(df["steam_id"].unique())


def test_select_steam_ids(gametime_dataframe_fname):
    """Test selection of steam IDs."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    ids = sorted(df["steam_id"].unique())
    assert 3 < len(ids)  # more than 2 steam ID
    df = select_steam_ids(df, [ids[2]])
    assert sorted(df["steam_id"].unique()) == [ids[2]]
    assert (df.index == range(0, len(df))).all()

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    ids = sorted(df["steam_id"].unique())
    assert 2 < len(ids)  # more than 2 steam ID
    df = select_steam_ids(df, [ids[0], ids[1]])
    assert sorted(df["steam_id"].unique()) == [ids[0], ids[1]]
    assert (df.index == range(0, len(df))).all()

    with pytest.raises(TypeError, match="must be an instance of"):
        select_steam_ids(df, 101)
    with pytest.raises(TypeError, match="must be an instance of"):
        select_steam_ids(df, [101])


def test_select_datetimes(gametime_dataframe_fname):
    """Test selection of dates."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    min_dt = df["acq_time"].unique().min()
    max_dt = df["acq_time"].unique().max()
    df = select_datetimes(df, min_dt, min_dt + pd.Timedelta(hours=2))
    assert min_dt in df["acq_time"].unique()  # inclusion of edges
    assert df["acq_time"].unique().max() <= min_dt + pd.Timedelta(hours=2)
    assert (df.index == range(0, len(df))).all()

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    size = df.size
    df = select_datetimes(df, None, max_dt)
    assert df.size == size  # unchanged
    assert (df.index == range(0, len(df))).all()

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(df, None, max_dt - pd.Timedelta(hours=2))
    assert min_dt == df["acq_time"].unique().min()
    assert df["acq_time"].unique().max() <= max_dt - pd.Timedelta(hours=2)
    assert (df.index == range(0, len(df))).all()

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(df, None, max_dt - pd.Timedelta(weeks=101))
    assert df.size == 0
    assert (df.index == range(0, len(df))).all()

    # start greater than end
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    with pytest.raises(ValueError, match="end datetime must be greater than the"):
        select_datetimes(df, max_dt, min_dt)

    # selection with str
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(
        df, f"{min_dt.year}-{min_dt.month}-{min_dt.day} {min_dt.hour + 2}:00", None
    )
    assert min_dt + pd.Timedelta(hours=2) <= df["acq_time"].unique().min()
    assert (df.index == range(0, len(df))).all()


def test_resampling(gametime_dataframe_fname):
    """Test resampling of the datetimes."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    min_dt = df["acq_time"].unique().min()
    max_dt = df["acq_time"].unique().max()
    delta = max_dt - min_dt
    df = select_datetimes(df, None, None, freq=f"{delta.days + 1}D")
    assert df["steam_id"].unique().size == df["steam_id"].size
    assert (df.index == range(0, len(df))).all()

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    hours = delta.total_seconds() / 3600
    n = hours // 2
    assert 2 <= n
    df = select_datetimes(df, None, None, freq="2h")
    assert df["steam_id"].unique().size * (n + 1) == df["steam_id"].size
    assert (df.index == range(0, len(df))).all()

    # check game_time_diff
    df_ori = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    for steam_id in df["steam_id"].unique():
        sel = df[df["steam_id"] == steam_id]
        sel_ori = df_ori[df_ori["steam_id"] == steam_id]
        sum_ = 0
        i = 0
        for k, elt in enumerate(sel_ori["acq_time"].isin(sel["acq_time"]).values):
            if k == 0:
                assert np.isnan(sel["game_time_diff"].values[k])
                i += 1
                continue
            sum_ += sel_ori["game_time_diff"].values[k]
            if elt:
                assert sum_ == sel["game_time_diff"].values[i]
                sum_ = 0
                i += 1


def test_select_gametimes(mock_df_select_gametimes):
    """Test selection of steam IDs based on gametimes."""
    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        "<",
        10,
        all_weeks=True,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 0

    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        ">",
        10,
        all_weeks=True,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 1
    assert all(
        elt in mock_df_select_gametimes["steam_id"].unique() for elt in steam_ids
    )

    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        ">",
        1600,
        all_weeks=True,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 0

    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        ">",
        1600,
        all_weeks=False,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 1
    assert all(
        elt in mock_df_select_gametimes["steam_id"].unique() for elt in steam_ids
    )

    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        ">",
        1560,
        all_weeks=True,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 0

    steam_ids = select_gametimes(
        mock_df_select_gametimes,
        {"76561198329580271": "2024-04-12"},
        ">=",
        1560,
        all_weeks=True,
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 1
    assert all(
        elt in mock_df_select_gametimes["steam_id"].unique() for elt in steam_ids
    )


def test_select_gametimes_short_week(mock_df_select_gametimes):
    """Test selection by gametimes on a week too short."""
    df = mock_df_select_gametimes.copy(deep=True).iloc[:10]
    steam_ids = select_gametimes(
        df, {"76561198329580271": "2024-04-12"}, ">", 500, all_weeks=False
    )
    assert isinstance(steam_ids, list)
    assert len(steam_ids) == 0


def test_selection_gamestimes_invalid(mock_df_select_gametimes):
    """Test selection of gametimes with invalid inputs."""
    with pytest.raises(ValueError, match="must be strictly positive"):
        select_gametimes(
            mock_df_select_gametimes,
            {"76561198329580271": "2024-04-12"},
            "<",
            -101,
            all_weeks=True,
        )
