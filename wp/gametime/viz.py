from datetime import datetime

import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from ..utils._checks import check_gametime_dataframe, check_type, check_value
from ..utils._docs import fill_doc
from ..utils.logs import warn
from .selection import select_datetimes, select_steam_ids

_LABELS: dict[str, str] = {
    "acq_time": "Date/Time (UTC)",
    "game_time": "Game time (min)",
    "steam_id": "Username",
    "game_id": "Game",
    "game_time_diff": "Δ game time (min)",
}


def make_plot_prettier(plot: plt.Axes | sns.FacetGrid) -> None:
    """Make plot prettier by detecting and formatting labels and ticks.

    Parameters
    ----------
    plot : Axes | FacetGrid
        The plot or facetgrid to prettify.
    """
    check_type(plot, (plt.Axes, sns.FacetGrid), "plot")
    if isinstance(plot, plt.Axes):
        _make_ax_prettier(plot)
        if plot.get_legend() is not None:
            llabel = plot.get_legend().get_title().get_text()
            plot.get_legend().set_title(_LABELS.get(llabel, llabel))
    elif isinstance(plot, sns.FacetGrid):
        for ax in plot.axes.flatten():
            _make_ax_prettier(ax)
        if plot.legend is not None:
            llabel = plot.legend.get_title().get_text()
            plot.legend.set_title(_LABELS.get(llabel, llabel))
    # layout
    if isinstance(plot, plt.Axes):
        plt.tight_layout()


def _make_ax_prettier(ax: plt.Axes):
    """Make a matplotlib Axes prettier."""
    for axis in ("x", "y"):
        label = getattr(ax, f"get_{axis}label")()
        getattr(ax, f"set_{axis}label")(_LABELS.get(label, label))
        if label == "acq_time":
            # rotate
            ax.tick_params(axis=axis, rotation=50)
            # set fix tick position
            loc = getattr(ax, f"get_{axis}ticks")()
            getattr(ax, f"{axis}axis").set_major_locator(mticker.FixedLocator(loc))
            # map ticklabels to human readable format
            for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.000000000"):
                try:
                    ticklabels = [
                        datetime.strptime(elt.get_text(), fmt)
                        for elt in getattr(ax, f"get_{axis}ticklabels")()
                    ]
                    hours = [elt.hour for elt in ticklabels]
                    format_str = (
                        "%Y-%m-%d" if np.std(hours) <= 1 else "%Y-%m-%d\n %H:%M"
                    )
                    ticklabels = [elt.strftime(format_str) for elt in ticklabels]
                    getattr(ax, f"set_{axis}ticklabels")(ticklabels)
                except ValueError:
                    continue  # already formatted

    # title
    title = ax.get_title()
    if "game_id =" in title:
        title = title.split("game_id =")[1].strip()
        ax.set_title(title)
    if "steam_id =" in title:
        title = title.split("steam_id =")[1].strip()
        ax.set_title(title)


@fill_doc
def plot_gametime_barplot(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...],
    start_dates: dict[str, str | pd.Timestamp],
) -> plt.Figure:
    """Plot the total gametime in function of time, per day and per steam ID.

    Parameters
    ----------
    %(df_gametime)s
    steam_ids : list of str | tuple of str
        List of steam IDs to select.
    start_dates : dict
        Mapping of steam IDs to the date (UTC) at which they start the play-phase.
        The date is either provided as a pd.Timestamp or as a string in the format:
        'YYYY-MM-DD'.

    Returns
    -------
    fig : Figure
        Matplotlib figure.

    Notes
    -----
    If :func:`~wp.gametime.prepare_dataframe` is used, the steam IDs in the selection
    must match the usernames provided in the mapping.
    """
    check_gametime_dataframe(df)
    check_type(steam_ids, (list, tuple), "steam_ids")
    for steam_id in steam_ids:
        check_type(steam_id, (str,), "steam_id")
    check_type(start_dates, (dict,), "start_dates")
    for key, value in start_dates.items():
        check_type(key, (str,), "start_dates key")
        check_value(key, steam_ids, "start_dates key")
        check_type(value, (str, pd.Timestamp), "start_dates value")
    # convert to timestamps, confirm that hours, minute and second are set to 0, else
    # warn and round
    for key, value in start_dates.items():
        if isinstance(value, str):
            value = pd.Timestamp(value, tz="utc")
        if value.hour != 0 or value.minute != 0 or value.second != 0:
            warn(
                f"Start date for {key} is not at midnight 00:00:00. Rounding to the "
                "nearest day."
            )
        start_dates[key] = value.round("1D")
    # select steam IDs, then let's create one dataframe per ID with the correct dates
    df = select_steam_ids(df, steam_ids)
    dfs = dict()
    for steam_id in steam_ids:
        df_ = select_steam_ids(df.copy(deep=True), [steam_id])
        df_ = select_datetimes(df_, start_dates[steam_id], end=None, freq="1D")
        df_["Day"] = [str(k + 1) for k in df_.index]
        dfs[steam_id] = df_
    # concatenate back the dataframes into a single object and plot
    df = pd.concat(dfs.values(), ignore_index=True)
    ax = sns.barplot(
        df,
        x="Day",
        y="game_time",
        hue="steam_id",
        errorbar=None,
    )
    make_plot_prettier(ax)
    return ax.figure
