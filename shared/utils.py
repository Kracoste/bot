from __future__ import annotations

from datetime import datetime
from typing import Any


def log_info(message: str) -> None:
    timestamp = datetime.now().isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}")


def require_dependency(module: Any, package_name: str) -> None:
    if module is None:
        raise RuntimeError(
            f"La dépendance '{package_name}' est requise pour cette fonctionnalité. "
            f"Installez-la via 'pip install {package_name}'."
        )
