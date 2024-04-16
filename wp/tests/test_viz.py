from __future__ import annotations

from importlib.resources import files
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


@pytest.fixture(scope="function")
def datetimes() -> tuple[pd.Timestamp, pd.Timestamp]:
    """Start/Stop datetimes to select."""
    return (
        pd.Timestamp(year=2024, month=4, day=12, hour=12, tz="utc"),
        pd.Timestamp(year=2024, month=4, day=12, hour=16, tz="utc"),
    )


def test_plot_heatmap(
    dataframe: pd.DataFrame,
    steam_ids: list[str],
    datetimes: tuple[pd.Timestamp, pd.Timestamp],
):
    """Test the plot_heatmap function."""
    f, ax = plot_heatmap(dataframe)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_heatmap(dataframe, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_heatmap(dataframe, datetimes=datetimes)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_heatmap(dataframe, datetimes=(None, datetimes[1]))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_heatmap(dataframe, datetimes=(datetimes[0], None))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    plot_heatmap(dataframe, steam_ids, ax=ax)


@pytest.mark.parametrize("hue", ["game_id", "steam_id"])
def test_plot_lineplot(
    dataframe: pd.DataFrame,
    steam_ids: list[str],
    datetimes: tuple[pd.Timestamp, pd.Timestamp],
    hue: str,
):
    """Test the plot_lineplot function."""
    f, ax = plot_lineplot(dataframe, hue)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_lineplot(dataframe, hue, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_lineplot(dataframe, hue, datetimes=datetimes)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_lineplot(dataframe, hue, datetimes=(None, datetimes[1]))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_lineplot(dataframe, hue, datetimes=(datetimes[0], None))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    plot_lineplot(dataframe, hue, steam_ids, ax=ax)


@pytest.mark.parametrize("func", [plot_barplot_dts, plot_barplot_ids])
def test_plot_barplot(
    dataframe: pd.DataFrame,
    steam_ids: list[str],
    datetimes: tuple[pd.Timestamp, pd.Timestamp],
    func,
):
    """Test the plot_barplot_* functions."""
    f, ax = func(dataframe)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = func(dataframe, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = func(dataframe, datetimes=datetimes)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = func(dataframe, datetimes=(None, datetimes[1]))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = func(dataframe, datetimes=(datetimes[0], None))
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    func(dataframe, steam_ids, ax=ax)
