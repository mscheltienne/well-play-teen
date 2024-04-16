from __future__ import annotations

from importlib.resources import files
from itertools import product
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from matplotlib import pyplot as plt

from wp.config import DF_DTYPES
from wp.viz import plot_barplot_dts, plot_barplot_ids, plot_heatmap, plot_lineplot

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(scope="session")
def fname() -> Path:
    """Path to a gametime CSV dataset."""
    return files("wp.tests") / "data" / "gametime.csv"


@pytest.fixture(scope="function")
def dataframe(fname) -> pd.DataFrame:
    """Load a gametime CSV dataset."""
    return pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])


@pytest.fixture(scope="function")
def steam_ids() -> list[str]:
    """Sample of steam IDs from the CSV dataset."""
    return ["76561198329580279", "76561198329580271"]


@pytest.mark.parametrize("func", [plot_heatmap, plot_barplot_dts, plot_barplot_ids])
def test_plot_basic(
    func,
    dataframe: pd.DataFrame,
):
    """Test the plot_* functions."""
    f, ax = func(dataframe)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


@pytest.mark.parametrize("func", [plot_heatmap, plot_barplot_dts, plot_barplot_ids])
def test_plot_select_ids(
    func,
    dataframe: pd.DataFrame,
    steam_ids: list[str],
):
    """Test the plot_* functions."""
    f, ax = func(dataframe, steam_ids=steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


@pytest.mark.parametrize("func", [plot_heatmap, plot_barplot_dts, plot_barplot_ids])
def test_plot_ax(
    func,
    dataframe: pd.DataFrame,
):
    """Test the plot_* functions."""
    _, ax = plt.subplots(1, 1)
    func(dataframe, ax=ax)


@pytest.mark.parametrize(
    "func, datetimes",
    product(
        [plot_heatmap, plot_barplot_dts, plot_barplot_ids],
        [
            (
                pd.Timestamp(year=2024, month=4, day=12, hour=12, tz="utc"),
                pd.Timestamp(year=2024, month=4, day=12, hour=16, tz="utc"),
            ),
            (None, pd.Timestamp(year=2024, month=4, day=12, hour=16, tz="utc")),
            (pd.Timestamp(year=2024, month=4, day=12, hour=12, tz="utc"), None),
        ],
    ),
)
def test_plot_select_dts(
    func,
    dataframe: pd.DataFrame,
    datetimes: tuple[pd.Timestamp, pd.Timestamp],
):
    """Test the plot_* functions."""
    f, ax = func(dataframe, datetimes=datetimes)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


@pytest.mark.parametrize("hue", ["game_id", "steam_id"])
def test_lineplot(dataframe: pd.DataFrame, hue):
    """Test the lineplot function."""
    f, ax = plot_lineplot(dataframe, hue)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


def test_select_and_map_steam_ids(dataframe: pd.DataFrame, steam_ids: list[str]):
    """Test selection and mapping of steam IDs functions."""
    f, ax = plot_heatmap(
        dataframe,
        steam_ids=steam_ids,
        steam_ids_mapping={elt: str(k) for k, elt in enumerate(steam_ids)},
    )
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


def test_select_and_map_too_many_steam_ids(
    dataframe: pd.DataFrame, steam_ids: list[str]
):
    """Test selection and mapping of steam IDs functions."""
    mapping = {elt: str(k) for k, elt in enumerate(steam_ids)}
    mapping["test"] = "101"
    f, ax = plot_heatmap(
        dataframe,
        steam_ids=steam_ids,
        steam_ids_mapping=mapping,
    )
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)


def test_select_and_map_too_few_steam_ids(
    dataframe: pd.DataFrame, steam_ids: list[str]
):
    """Test selection and mapping of steam IDs functions."""
    mapping = {elt: str(k) for k, elt in enumerate(steam_ids)}
    with pytest.raises(ValueError, match="must contain all the keys"):
        plot_heatmap(
            dataframe,
            steam_ids=None,
            steam_ids_mapping=mapping,
        )

    del mapping[steam_ids[0]]
    with pytest.raises(ValueError, match="must contain all the keys"):
        plot_heatmap(
            dataframe,
            steam_ids=steam_ids,
            steam_ids_mapping=mapping,
        )
