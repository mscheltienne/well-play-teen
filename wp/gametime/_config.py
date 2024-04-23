DF_DTYPES = {
    "steam_id": str,
    "game_id": str,
    "game_time": float,
    "game_time_diff": float,
}

_STEAM_API_KEY: str = "847931CAE62FC345F305B1F974DC8759"
_STEAM_BEJEWELED_APP_ID: int = 78000
_STEAM_ECO_RESCUE_APP_ID: int = 2163350
_GAME_IDs_MAPPING = {
    str(_STEAM_ECO_RESCUE_APP_ID): "Ecorescue",
    str(_STEAM_BEJEWELED_APP_ID): "Bejeweled",
}
_BACKUP_DAYS: int = 14
