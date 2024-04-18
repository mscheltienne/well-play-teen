from datetime import datetime

import matplotlib.ticker as mticker
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from ._checks import check_type

_LABELS: dict[str, str] = {
    "acq_time": "Date/Time (UTC)",
    "game_time": "Game time (min)",
    "steam_id": "Username",
    "game_id": "Game",
    "game_time_diff": "Δ (Game time - min)",
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
        llabel = plot.get_legend().get_title().get_text()
        plot.get_legend().set_title(_LABELS.get(llabel, llabel))
    elif isinstance(plot, sns.FacetGrid):
        for ax in plot.axes.flatten():
            _make_ax_prettier(ax)
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
            try:
                ticklabels = [
                    datetime.strptime(elt.get_text(), "%Y-%m-%d %H:%M:%S%z")
                    for elt in getattr(ax, f"get_{axis}ticklabels")()
                ]
                hours = [elt.hour for elt in ticklabels]
                format_str = "%Y-%m-%d" if np.std(hours) <= 1 else "%Y-%m-%d\n %H:%M"
                ticklabels = [elt.strftime(format_str) for elt in ticklabels]
                getattr(ax, f"set_{axis}ticklabels")(ticklabels)
            except ValueError:
                continue  # already formatted

    # title
    title = ax.get_title()
    if "game_id =" in title:
        title = title.split("game_id =")[1].strip()
        ax.set_title(title)
