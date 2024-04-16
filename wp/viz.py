import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from .utils._checks import check_type, check_value
from .utils._docs import fill_doc


@fill_doc
def plot_heatmap(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    datetimes: tuple[pd.Timestamp, pd.Timestamp] | list[pd.Timestamp] | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a heatmap of the gametime deltas.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    check_type(df, (pd.DataFrame,), "df")
    _check_steam_ids(steam_ids)
    _check_datetimes(datetimes)
    check_type(ax, (plt.Axes, None), "ax")
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    if datetimes is not None:
        mask = (datetimes[0] <= df["acq_time"]) & (df["acq_time"] <= datetimes[1])
        df = df.loc[mask]
    pivot_df = df.pivot_table(
        index="steam_id", columns="acq_time", values="game_time_diff"
    )
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.heatmap(pivot_df, ax=ax)
    return ax.figure, ax


@fill_doc
def plot_lineplot(
    df: pd.DataFrame,
    hue: str,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    datetimes: tuple[pd.Timestamp, pd.Timestamp] | list[pd.Timestamp] | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a lineplot of the gametime.

    Parameters
    ----------
    %(df_gametime)s
    hue : str
        Either "game_id" or "steam_id".
    %(steam_ids)s
    %(datetimes)s
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
    _check_datetimes(datetimes)
    check_type(ax, (plt.Axes, None), "ax")
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    if datetimes is not None:
        mask = (datetimes[0] <= df["acq_time"]) & (df["acq_time"] <= datetimes[1])
        df = df.loc[mask]
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.lineplot(df, x="acq_time", y="game_time", hue=hue, ax=ax)
    return ax.figure, ax


@fill_doc
def plot_barplot_total_gametime(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] = None,
    datetimes: tuple[pd.Timestamp, pd.Timestamp] | list[pd.Timestamp] | None = None,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a barplot of the total gametime.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    check_type(df, (pd.DataFrame,), "df")
    _check_steam_ids(steam_ids)
    _check_datetimes(datetimes)
    check_type(ax, (plt.Axes, None), "ax")
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    if datetimes is not None:
        mask = (datetimes[0] <= df["acq_time"]) & (df["acq_time"] <= datetimes[1])
        df = df.loc[mask]
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


def _check_datetimes(
    datetimes: tuple[pd.Timestamp, pd.Timestamp] | list[pd.Timestamp] | None,
):
    """Validate the datetimes parameter."""
    check_type(datetimes, (tuple, None), "datetimes")
    if datetimes is not None:
        check_type(datetimes[0], (pd.Timestamp,), "datetimes[0]")
        check_type(datetimes[1], (pd.Timestamp,), "datetimes[1]")
        if datetimes[1] < datetimes[0]:
            raise ValueError("datetimes[1] must be greater than datetimes[0].")
