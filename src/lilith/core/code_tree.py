from __future__ import annotations

import hashlib
import logging
import mimetypes
import os
import uuid

from typing import TYPE_CHECKING

from anytree import NodeMixin
from anytree import PreOrderIter
from anytree import RenderTree


if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger(__name__)


class CodeFolderNode(NodeMixin):

    def __init__(
        self, name: str, folder_path: str, parent: CodeFolderNode | None = None
    ) -> None:
        """_summary_

        Args:
            name (str): _description_
            folder_path (str): _description_
            parent (CodeFolderNode, optional): _description_. Defaults to None.
        """
        super().__init__()
        self.node_id = str(uuid.uuid4())
        self.name = name
        self.folder_path = folder_path
        self.parent = parent

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.folder_path},parent={self.parent})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.folder_path},parent={self.parent})"

    def dictify_for_neo4j(self) -> dict:
        return {
            "id": self.node_id,
            "type": "folder",
            "name": self.name,
            "path": str(self.folder_path),
            "parent": self.parent.node_id if self.parent else None,
        }


class CodeFileNode(NodeMixin):
    def __init__(
        self,
        name: str,
        file_path: str,
        parent: CodeFolderNode | None = None,
    ) -> None:
        """_summary_

        Args:
            name (str): _description_
            file_path (str): _description_
            parent (CodeFolderNode, optional): _description_. Defaults to None.
        """
        super().__init__()

        self.node_id = str(uuid.uuid4())
        self.name = name
        self.file_path = file_path
        self.parent = parent
        self.content_hash = None

    def get_file_data(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        try:
            stat_info = os.stat(self.file_path)
            creation_time = stat_info.st_birthtime
            modification_time = stat_info.st_mtime

            file_extension = os.path.splitext(self.file_path)[1]
            mime_type, _ = mimetypes.guess_type(self.file_path)

            with open(self.file_path, encoding="utf-8") as file:
                content = file.read()

            return {
                "content": content,
                "file_name": os.path.basename(self.file_path),
                "file_extension": file_extension,
                "mime_type": mime_type,
                "creation_time": creation_time,
                "modification_time": modification_time,
                "file_size": stat_info.st_size,
            }

        except FileNotFoundError:
            logger.error(f"Error: The file '{self.file_path}' does not exist.")
        except PermissionError:
            logger.error(
                f"Error: You do not have permission to read the file '{self.file_path}'."
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def refresh_content_hash(self):
        content = self.get_file_data()["content"]
        self.content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def dictify_for_neo4j(self) -> dict:
        return {
            "id": self.node_id,
            "type": "file",
            "name": self.name,
            "path": str(self.file_path),
            "parent": self.parent.node_id if self.parent else None,
        }


def build_tree_recursive(
    file_path: Path, parent: CodeFileNode | CodeFolderNode | None = None
):
    name = os.path.basename(file_path)

    if os.path.isdir(file_path):
        node = CodeFolderNode(name=name, folder_path=file_path, parent=parent)

        for item in os.listdir(file_path):
            item_path = os.path.join(file_path, item)
            build_tree_recursive(item_path, parent=node)

    else:

        node = CodeFileNode(
            name=name,
            file_path=file_path,
            parent=parent,
        )

        node.refresh_content_hash()

    return node


def stringify_code_tree(tree_root: CodeFileNode | CodeFolderNode) -> str:
    """_summary_

    Args:
        tree (CodeFileNode | CodeFolderNode): _description_

    Returns:
        str: _description_
    """
    code_list = [(pre, node.name) for pre, _, node in RenderTree(tree_root)]
    return os.linesep.join(f"{pre}{name}" for pre, name in code_list)


def export_code_tree(tree_root: CodeFileNode | CodeFolderNode) -> dict:
    """_summary_

    Args:
        tree_root (CodeFileNode | CodeFolderNode): _description_

    Returns:
        dict: _description_
    """
    result = []

    for item in iterate_code_tree(tree_root):
        result.append(item.dictify_for_neo4j())

    return result


def iterate_code_tree(
    tree_root: CodeFileNode | CodeFolderNode, max_level: int = 10
) -> PreOrderIter:
    """_summary_

    Args:
        tree_root (CodeFileNode | CodeFolderNode): _description_

    Returns:
        _type_: _description_
    """
    return PreOrderIter(tree_root, maxlevel=max_level)
