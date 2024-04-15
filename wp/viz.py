import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from .utils._checks import check_type, check_value
from .utils._docs import fill_doc


@fill_doc
def plot_heatmap(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a heatmap of the gametime deltas.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    check_type(df, (pd.DataFrame,), "df")
    _check_steam_ids(steam_ids)
    check_type(ax, (plt.Axes, None), "ax")
    pivot_df = df.pivot_table(
        index="steam_id", columns="acq_time", values="game_time_diff"
    )
    if steam_ids is not None:
        pivot_df = pivot_df.loc[steam_ids]
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.heatmap(pivot_df, ax=ax)
    return ax.figure, ax


@fill_doc
def plot_lineplot(
    df: pd.DataFrame,
    hue: str,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a lineplot of the gametime.

    Parameters
    ----------
    %(df_gametime)s
    hue : str
        Either "game_id" or "steam_id".
    %(steam_ids)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    check_type(df, (pd.DataFrame,), "df")
    check_type(hue, (str,), "hue")
    check_value(hue, ("game_id", "steam_id"), "hue")
    _check_steam_ids(steam_ids)
    check_type(ax, (plt.Axes, None), "ax")
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.lineplot(df, x="acq_time", y="game_time", hue=hue, ax=ax)
    return ax.figure, ax


@fill_doc
def plot_barplot_total_gametime(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a barplot of the total gametime.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    check_type(df, (pd.DataFrame,), "df")
    _check_steam_ids(steam_ids)
    check_type(ax, (plt.Axes, None), "ax")
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    data = dict()
    for elt in df.groupby("steam_id"):
        data[elt[0]] = []
        data[elt[0]].append(elt[1].iloc[-1]["game_time"])
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.barplot(pd.DataFrame(data), ax=ax)
    return ax.figure, ax


def _check_steam_ids(steam_ids: list[str] | tuple[str, ...] | None):
    """Validate the steam_ids parameter."""
    check_type(steam_ids, (list, tuple, None), "steam_ids")
    if steam_ids is not None:
        for elt in steam_ids:
            check_type(elt, (str,), "steam_id")
        if len(steam_ids) == 0:
            raise ValueError("steam_ids cannot be an empty list or tuple.")
