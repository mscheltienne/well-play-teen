import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from .config import STEAM_BEJEWELED_APP_ID, STEAM_ECO_RESCUE_APP_ID
from .utils._checks import check_type, check_value
from .utils._docs import fill_doc


@fill_doc
def plot_heatmap(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    steam_ids_mapping: dict[str, str] | None = None,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None] = (None, None),
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a heatmap of the gametime deltas.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(steam_ids_mapping)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    df = _prepare_df(df, steam_ids, datetimes, steam_ids_mapping)
    check_type(ax, (plt.Axes, None), "ax")
    pivot_df = df.pivot_table(
        index="steam_id", columns="acq_time", values="game_time_diff"
    )
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.heatmap(pivot_df, ax=ax)
    ax.set_xticks(list(ax.get_xticks() - 0.5) + [ax.get_xticks()[-1] + 0.5])
    ax.set_xticklabels(
        df["acq_time"].sort_values().unique().strftime("%Y-%m-%d\n %H:%M"),
        rotation=50,
    )
    return ax.figure, ax


@fill_doc
def plot_lineplot(
    df: pd.DataFrame,
    hue: str,
    steam_ids: list[str] | tuple[str, ...] | None = None,
    steam_ids_mapping: dict[str, str] | None = None,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None] = (None, None),
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a lineplot of the gametime.

    Parameters
    ----------
    %(df_gametime)s
    hue : str
        Either "game_id" or "steam_id".
    %(steam_ids)s
    %(steam_ids_mapping)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    df = _prepare_df(df, steam_ids, datetimes, steam_ids_mapping)
    check_type(hue, (str,), "hue")
    check_value(hue, ("game_id", "steam_id"), "hue")
    check_type(ax, (plt.Axes, None), "ax")
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.lineplot(df, x="acq_time", y="game_time", hue=hue, ax=ax)
    ax.set_xticks(ax.get_xticks())  # avoids warning on set_xticklabels
    ax.set_xticklabels(
        df["acq_time"].sort_values().unique().strftime("%Y-%m-%d\n %H:%M"),
        rotation=50,
    )
    return ax.figure, ax


@fill_doc
def plot_barplot_dts(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] = None,
    steam_ids_mapping: dict[str, str] | None = None,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None] = (None, None),
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a barplot of the total gametime per datetime.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(steam_ids_mapping)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    df = _prepare_df(df, steam_ids, datetimes, steam_ids_mapping)
    check_type(ax, (plt.Axes, None), "ax")
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10), layout="constrained")
    ax = sns.barplot(df, x="acq_time", y="game_time", hue="steam_id", ax=ax)
    ax.set_xticks(ax.get_xticks())  # avoids warning on set_xticklabels
    ax.set_xticklabels(
        df["acq_time"].sort_values().unique().strftime("%Y-%m-%d\n %H:%M"),
        rotation=50,
    )
    return ax.figure, ax


@fill_doc
def plot_barplot_ids(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] = None,
    steam_ids_mapping: dict[str, str] | None = None,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None] = (None, None),
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a barplot of the total gametime per IDs.

    Parameters
    ----------
    %(df_gametime)s
    %(steam_ids)s
    %(steam_ids_mapping)s
    %(datetimes)s
    %(ax_arg)s

    Returns
    -------
    %(fig)s
    %(ax_return)s
    """
    df = _prepare_df(df, steam_ids, datetimes, steam_ids_mapping)
    check_type(ax, (plt.Axes, None), "ax")
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
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None]
    | None,
):
    """Validate the datetimes parameter."""
    check_type(datetimes, (tuple, list), "datetimes")
    if len(datetimes) != 2:
        raise ValueError("datetimes must be a tuple of length 2.")
    check_type(datetimes[0], (pd.Timestamp, None), "datetimes[0]")
    check_type(datetimes[1], (pd.Timestamp, None), "datetimes[1]")
    if (
        datetimes[0] is not None
        and datetimes[1] is not None
        and datetimes[1] < datetimes[0]
    ):
        raise ValueError("datetimes[1] must be greater than datetimes[0].")


def _select_datetimes(
    df: pd.DataFrame,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None],
) -> pd.DataFrame:
    """Create a mask for the datetimes parameter."""
    if datetimes[0] is not None and datetimes[1] is not None:
        mask = (datetimes[0] <= df["acq_time"]) & (df["acq_time"] <= datetimes[1])
    elif datetimes[0] is None and datetimes[1] is not None:
        mask = df["acq_time"] <= datetimes[1]
    elif datetimes[0] is not None and datetimes[1] is None:
        mask = datetimes[0] <= df["acq_time"]
    else:
        return df
    return df.loc[mask]


def _map_game_id(df: pd.DataFrame) -> pd.DataFrame:
    """Map the game IDs to game names."""
    if sorted(df["game_id"].unique()) == ["Bejeweled", "Ecorescue"]:
        return df  # no-op
    mapping = {
        str(STEAM_ECO_RESCUE_APP_ID): "Ecorescue",
        str(STEAM_BEJEWELED_APP_ID): "Bejeweled",
    }
    mapping = {
        key: value for key, value in mapping.items() if key in df["game_id"].unique()
    }
    if sorted(df["game_id"].unique()) != sorted(mapping.keys()):
        raise ValueError("'game_id' must contain only the Ecorescue and Bejeweled IDs.")
    df.loc[:, "game_id"] = df["game_id"].map(mapping)
    return df


def _map_steam_id(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Map the steam IDs to user names."""
    if all(elt in mapping.values() for elt in df["steam_id"].unique()):
        return df  # no-op
    mapping = {
        key: value for key, value in mapping.items() if key in df["steam_id"].unique()
    }
    if sorted(df["steam_id"].unique()) != sorted(mapping.keys()):
        raise ValueError("'steam_id' must contain all the keys of the mapping.")
    df.loc[:, "steam_id"] = df["steam_id"].map(mapping)
    return df


def _prepare_df(
    df: pd.DataFrame,
    steam_ids: list[str] | tuple[str, ...] | None,
    datetimes: tuple[pd.Timestamp | None, pd.Timestamp | None]
    | list[pd.Timestamp | None],
    steam_ids_mapping: dict[str, str] | None,
) -> pd.DataFrame:
    """Prepare the DataFrame for plotting."""
    check_type(df, (pd.DataFrame,), "df")
    _check_steam_ids(steam_ids)
    _check_datetimes(datetimes)
    if steam_ids is not None:
        df = df[df["steam_id"].isin(steam_ids)]
    df = _select_datetimes(df, datetimes)
    df = _map_game_id(df)
    if steam_ids_mapping is not None:
        df = _map_steam_id(df, steam_ids_mapping)
    return df
