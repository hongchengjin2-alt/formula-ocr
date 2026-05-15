"""Runtime path helpers for source and PyInstaller builds."""

from pathlib import Path
import sys


def app_root() -> Path:
    """Return the project root in source mode or the bundle root in frozen mode."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parent.parent


def resource_path(*parts: str | Path) -> Path:
    """Resolve a bundled resource path."""
    return app_root().joinpath(*map(Path, parts))
