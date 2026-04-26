"""Repo-local package shim for plain Python invocations.

This keeps ``python3 -m electri_city_ops`` and plain ``unittest`` discovery
working from the repository root without requiring ``PYTHONPATH=src``.
"""

from pathlib import Path
from pkgutil import extend_path


__path__ = extend_path(__path__, __name__)

SRC_PACKAGE = Path(__file__).resolve().parents[1] / "src" / __name__
if SRC_PACKAGE.is_dir():
    src_package = str(SRC_PACKAGE)
    if src_package not in __path__:
        __path__.append(src_package)

__version__ = "0.1.0"
