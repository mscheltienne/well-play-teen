import pandas as pd
import pytest

from ...gametime import DF_DTYPES
from ..dataframe import _GAME_IDs_MAPPING, prepare_dataframe


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
