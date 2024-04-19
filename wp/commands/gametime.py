import argparse

from ..gametime.acquisition import update_gametime_dataset
from ..utils._checks import ensure_path


def run() -> None:
    """Run gametime() command."""
    parser = argparse.ArgumentParser(
        prog=f"{__package__.split('.')[0]}-gametime",
        description="update a gametime dataset.",
    )
    parser.add_argument(
        "folder",
        type=str,
        help="path to the gametime dataset folder.",
    )
    parser.add_argument(
        "steam_ids_ecorescue",
        type=str,
        help="path to the file containing steam ids.",
    )
    parser.add_argument(
        "steam_ids_bejeweled",
        type=str,
        help="path to the file containing steam ids.",
    )
    args = parser.parse_args()
    file = ensure_path(args.steam_ids_ecorescue, must_exist=True)
    with open(file) as fid:
        ids_ecorescue = [
            elt.strip() for elt in fid.readlines() if len(elt.strip()) != 0
        ]
    file = ensure_path(args.steam_ids_bejeweled, must_exist=True)
    with open(file) as fid:
        ids_bejeweled = [
            elt.strip() for elt in fid.readlines() if len(elt.strip()) != 0
        ]
    update_gametime_dataset(args.folder, ids_ecorescue, ids_bejeweled)
