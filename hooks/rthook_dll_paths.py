"""Add bundled DLL directories before importing Qt/PyTorch extensions."""

from pathlib import Path
import os
import sys


_DLL_DIRECTORY_HANDLES = []


def _add_dll_directory(path: Path) -> None:
    if not path.exists():
        return
    if hasattr(os, "add_dll_directory"):
        _DLL_DIRECTORY_HANDLES.append(os.add_dll_directory(str(path)))
    os.environ["PATH"] = f"{path}{os.pathsep}{os.environ.get('PATH', '')}"


bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))

for relative in (
    ".",
    "PySide6",
    "shiboken6",
    "torch/lib",
    "torchvision",
    "cv2",
):
    _add_dll_directory(bundle_root / relative)
