from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from matplotlib import pyplot as plt

from wp.config import DF_DTYPES
from wp.viz import plot_barplot_total_gametime, plot_heatmap, plot_lineplot

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


def test_plot_heatmap(dataframe: pd.DataFrame, steam_ids: list[str]):
    """Test the plot_heatmap function."""
    f, ax = plot_heatmap(dataframe)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_heatmap(dataframe, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    plot_heatmap(dataframe, steam_ids, ax=ax)


def test_plot_barplot_total_gametime(dataframe: pd.DataFrame, steam_ids: list[str]):
    """Test the plot_barplot_total_gametime function."""
    f, ax = plot_barplot_total_gametime(dataframe)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_barplot_total_gametime(dataframe, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    plot_barplot_total_gametime(dataframe, steam_ids, ax=ax)


@pytest.mark.parametrize("hue", ["game_id", "steam_id"])
def test_plot_lineplot(dataframe: pd.DataFrame, steam_ids: list[str], hue: str):
    """Test the plot_lineplot function."""
    f, ax = plot_lineplot(dataframe, hue)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    f, ax = plot_lineplot(dataframe, hue, steam_ids)
    assert isinstance(f, plt.Figure)
    assert isinstance(ax, plt.Axes)

    _, ax = plt.subplots(1, 1)
    plot_lineplot(dataframe, hue, steam_ids, ax=ax)
