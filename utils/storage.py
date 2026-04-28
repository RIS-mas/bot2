from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


class JsonStore:
    def __init__(self, path: str, default: Any):
        self.path = Path(path)
        self.default = default
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Any:
        if not self.path.exists():
            self.save(self.default)
            return self.default.copy() if isinstance(self.default, dict) else self.default

        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, OSError) as exc:
            LOGGER.warning("Failed to load %s (%s). Recreating with default.", self.path, exc)
            self.save(self.default)
            return self.default.copy() if isinstance(self.default, dict) else self.default

    def save(self, data: Any) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
