from pathlib import Path

__all__ = [
    "DIR_PHANTOM_LIBRARY",
    "PATH_LOGGING_CONFIG"
]

DIR_PHANTOM_LIBRARY = Path(__file__).parent.parent.parent / "PhantomLib"
PATH_LOGGING_CONFIG = str(Path(__file__).parent.parent / "utils" / "logging.ini")
