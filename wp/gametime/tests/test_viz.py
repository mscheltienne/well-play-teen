import pandas as pd
import pytest
import seaborn as sns
from matplotlib import pyplot as plt

from wp.gametime._config import DF_DTYPES
from wp.gametime.selection import prepare_dataframe
from wp.gametime.viz import make_plot_prettier, plot_gametime_barplot


def test_make_plot_prettier(gametime_dataframe_fname):
    """Test make_plot_prettier."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = prepare_dataframe(df, dict())
    ax = sns.barplot(
        df,
        x="acq_time",
        y="game_time",
        hue="steam_id",
        errorbar=None,
    )
    assert isinstance(ax, plt.Axes)
    make_plot_prettier(ax)
    assert isinstance(ax, plt.Axes)

    grid = sns.catplot(
        df,
        kind="bar",
        x="acq_time",
        y="game_time",
        col="game_id",
        hue="steam_id",
        errorbar=None,
    )
    assert isinstance(grid, sns.FacetGrid)
    make_plot_prettier(grid)
    assert isinstance(grid, sns.FacetGrid)

    pivot_df = df.pivot_table(
        index="steam_id", columns="acq_time", values="game_time_diff"
    )
    ax = sns.heatmap(pivot_df)
    assert isinstance(ax, plt.Axes)
    make_plot_prettier(ax)
    assert isinstance(ax, plt.Axes)


def test_plot_gametime_barplot(gametime_dataframe_fname):
    """Test plotting barplot since inclusion."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    f = plot_gametime_barplot(
        df,
        ["76561198329580271", "76561198329580273"],
        {
            "76561198329580271": "2024-04-12",
            "76561198329580273": "2024-04-12",
        },
    )
    assert isinstance(f, plt.Figure)

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    with pytest.warns(RuntimeWarning, match="not at midnight"):
        f = plot_gametime_barplot(
            df,
            ["76561198329580271", "76561198329580273"],
            {
                "76561198329580271": "2024-04-12 11:40:00",
                "76561198329580273": "2024-04-12 13:40:00",
            },
        )
    assert isinstance(f, plt.Figure)

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = prepare_dataframe(df, dict())
    with pytest.warns(RuntimeWarning, match="not at midnight"):
        f = plot_gametime_barplot(
            df,
            ["76561198329580271", "76561198329580273"],
            {
                "76561198329580271": "2024-04-12 11:40:00",
                "76561198329580273": "2024-04-12 13:40:00",
            },
        )
    assert isinstance(f, plt.Figure)

    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    df = prepare_dataframe(df, {"76561198329580271": "necromancia"})
    with pytest.warns(RuntimeWarning, match="not at midnight"):
        f = plot_gametime_barplot(
            df,
            ["necromancia", "76561198329580273"],
            {
                "necromancia": "2024-04-12 11:40:00",
                "76561198329580273": "2024-04-12 13:40:00",
            },
        )
    assert isinstance(f, plt.Figure)


def test_plot_gametime_barplot_week(gametime_dataframe_fname):
    """Test plotting barplot since inclusion."""
    df = pd.read_csv(
        gametime_dataframe_fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"]
    )
    with pytest.warns(RuntimeWarning, match="Duplicate indices found."):
        f = plot_gametime_barplot(
            df,
            ["76561198329580271", "76561198329580273"],
            {
                "76561198329580271": "2024-04-12",
                "76561198329580273": "2024-04-12",
            },
            week=0,
        )
    assert isinstance(f, plt.Figure)
