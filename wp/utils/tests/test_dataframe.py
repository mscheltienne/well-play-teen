import pandas as pd
import pytest

from ...gametime import DF_DTYPES
from ..dataframe import (
    _GAME_IDs_MAPPING,
    prepare_dataframe,
    select_datetimes,
    select_steam_ids,
)


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
    assert 1 < len(ids)  # more than 2 steam ID
    df = select_steam_ids(df, [ids[0]])
    assert sorted(df["steam_id"].unique()) == [ids[0]]

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    ids = sorted(df["steam_id"].unique())
    assert 2 < len(ids)  # more than 2 steam ID
    df = select_steam_ids(df, [ids[0], ids[1]])
    assert sorted(df["steam_id"].unique()) == [ids[0], ids[1]]

    with pytest.raises(TypeError, match="must be an instance of"):
        select_steam_ids(df, 101)
    with pytest.raises(TypeError, match="must be an instance of"):
        select_steam_ids(df, [101])


def test_df_select_datetimes(gametime_dataframe_fname):
    """Test selection of dates."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    min_dt = df["acq_time"].unique().min()
    max_dt = df["acq_time"].unique().max()
    df = select_datetimes(df, min_dt, min_dt + pd.Timedelta(hours=2))
    assert min_dt in df["acq_time"].unique()  # inclusion of edges
    assert df["acq_time"].unique().max() <= min_dt + pd.Timedelta(hours=2)

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    size = df.size
    df = select_datetimes(df, None, max_dt)
    assert df.size == size  # unchanged

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    size = df.size
    df = select_datetimes(df, None, None)
    assert df.size == size  # unchanged

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(df, None, max_dt - pd.Timedelta(hours=2))
    assert min_dt == df["acq_time"].unique().min()
    assert df["acq_time"].unique().max() <= max_dt - pd.Timedelta(hours=2)

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(df, None, max_dt - pd.Timedelta(weeks=101))
    assert df.size == 0

    # start greater than stop
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    with pytest.raises(ValueError, match="stop datetime must be greater than the"):
        select_datetimes(df, max_dt, min_dt)

    # selection with str
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = select_datetimes(
        df, f"{min_dt.year}-{min_dt.month}-{min_dt.day} {min_dt.hour + 2}:00", None
    )
    assert min_dt + pd.Timedelta(hours=2) <= df["acq_time"].unique().min()
