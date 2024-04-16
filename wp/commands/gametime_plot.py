import argparse
from datetime import datetime

import pandas as pd

from ..config import DF_DTYPES
from ..utils._checks import ensure_path
from ..viz import plot_barplot_total_gametime, plot_heatmap, plot_lineplot


def run() -> None:
    """Run plot_gametime() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-gametime",
        description="update a gametime dataset.",
    )
    parser.add_argument(
        "fname",
        type=str,
        help="path to the gametime CSV dataset file.",
    )
    parser.add_argument(
        "-s",
        "--steam-ids",
        type=str,
        metavar="str",
        help="path to the file containing steam ids to select.",
        default=None,
    )
    parser.add_argument(
        "-dt-start",
        "--datetime-start",
        type=str,
        metavar="str",
        help="start datetime to select, format UTC 'YYYY-MM-DD HH:MM:SS'.",
        default=None,
    )
    parser.add_argument(
        "-dt-stop",
        "--datetime-stop",
        type=str,
        metavar="str",
        help="stop datetime to select, format UTC 'YYYY-MM-DD HH:MM:SS'.",
        default=None,
    )
    parser.add_argument(
        "--lineplot",
        help="plot the lineplots.",
        action="store_true",
    )
    parser.add_argument(
        "--heatmap",
        help="plot the heatmap.",
        action="store_true",
    )
    parser.add_argument(
        "--barplot",
        help="plot the total gametime barplot.",
        action="store_true",
    )
    args = parser.parse_args()
    fname = ensure_path(args.fname, must_exist=True)
    now = datetime.now().strftime("%Y%m%d")
    out = fname.parent / "plots" / now
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(fname, index_col=0, dtype=DF_DTYPES, parse_dates=["acq_time"])

    if args.steam_ids is not None:
        steam_ids = ensure_path(args.steam_ids, must_exist=True)
        with open(steam_ids) as fid:
            ids = [elt.strip() for elt in fid.readlines() if len(elt.strip()) != 0]
    else:
        ids = None
    dt_start = (
        None
        if args.datetime_start is None
        else pd.Timestamp(args.datetime_start, tz="utc")
    )
    dt_stop = (
        None
        if args.datetime_stop is None
        else pd.Timestamp(args.datetime_stop, tz="utc")
    )

    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.lineplot:
        f, _ = plot_lineplot(df, "game_id", ids, (dt_start, dt_stop))
        f.savefig(out / f"lineplot_gid_{now}.svg", transparent=True)
        f, _ = plot_lineplot(df, "steam_id", ids, (dt_start, dt_stop))
        f.savefig(out / f"lineplot_sid_{now}.svg", transparent=True)
    if args.heatmap:
        f, _ = plot_heatmap(df, ids, (dt_start, dt_stop))
        f.savefig(out / f"heatmap_{now}.svg", transparent=True)
    if args.barplot:
        f, _ = plot_barplot_total_gametime(df, ids, (dt_start, dt_stop))
        f.savefig(out / f"barplot_{now}.svg", transparent=True)
