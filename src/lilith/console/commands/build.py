from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from lilith.console.utils import ConsoleError


if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class BuildCommand:
    def __init__(self, build_path: Path, reset: bool) -> None:
        self.path = build_path
        self.reset = reset

    def run(self):
        from lilith.core.code_tree import build_tree_recursive
        from lilith.core.code_tree import export_code_tree
        from lilith.database.database import Neo4jGraphDatabase

        tree_root = build_tree_recursive(self.path)
        export_data = export_code_tree(tree_root)

        with Neo4jGraphDatabase() as db:

            if self.reset:
                logger.info("Resetting database...")
                db.reset_database()
            else:
                node_count = db.get_node_count()
                if node_count > 0:
                    raise ConsoleError(
                        f"The database currently contains {node_count} nodes. To rebuild the database and start fresh, please run the build command again with the --reset option."
                    )

            db.insert_data(export_data)

        logger.info("Build successfully finished!")
