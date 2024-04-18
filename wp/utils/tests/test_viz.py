import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from wp.gametime import DF_DTYPES
from wp.utils.dataframe import prepare_dataframe
from wp.utils.viz import make_plot_prettier


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
