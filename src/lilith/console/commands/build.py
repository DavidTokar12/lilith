from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    import logging

    from pathlib import Path


class BuildCommand:
    def __init__(self, build_path: Path, logger: logging.Logger) -> None:
        self.path = build_path
        self.logger = logger

    def run(self):
        self.logger.info("Running build")

    # def
