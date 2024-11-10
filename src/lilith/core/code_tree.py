"""
{
    "id": globally unique,
    "type": folder | file | function | class | code_piece,
    "name": name of the file, folder, function or class, or None for a code piece
    "path": path of the file folder or the file path where the function/class/code piece is in,
    "parent": id of the parent file or folder,
    "code_content": full code of function/class or code piece, for file or folder null
    "embedding": embedding of the content, for folder or file is null
    "description": LLM generated description or comments for functions or classes
}
"""

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
from tqdm import tqdm

from lilith.core.code_file_splitting import split_code_file_into_chunks
from lilith.core.utils import CoreError
from lilith.core.utils import get_class_definition
from lilith.core.utils import get_function_definition


if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger(__name__)


class CodeFolderNode(NodeMixin):

    def __init__(
        self, name: str, folder_path: str, parent: CodeFolderNode | None
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
        """_summary_

        Returns:
            dict: _description_
        """
        return {
            "id": self.node_id,
            "type": "folder",
            "name": self.name,
            "path": str(self.folder_path),
            "parent": self.parent.node_id if self.parent else None,
            "code_content": None,
            "embedding": None,
            "description": None,
        }


class CodeFileNode(NodeMixin):
    def __init__(
        self,
        name: str,
        file_path: str,
        parent: CodeFolderNode,
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
        """_summary_

        Returns:
            dict: _description_
        """
        return {
            "id": self.node_id,
            "type": "file",
            "name": self.name,
            "path": str(self.file_path),
            "parent": self.parent.node_id if self.parent else None,
            "code_content": None,
            "embedding": None,
            "description": None,
        }


class CodeFunctionNode(NodeMixin):
    def __init__(self, file_path: str, parent: CodeFileNode, code_content: str) -> None:
        """_summary_

        Args:
            name (str): _description_
            file_path (str): _description_
            parent (CodeFolderNode, optional): _description_. Defaults to None.
        """
        super().__init__()

        self.node_id = str(uuid.uuid4())
        self.name = get_function_definition(code_content)
        self.file_path = file_path
        self.parent = parent
        self.code_content = code_content

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def dictify_for_neo4j(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        return {
            "id": self.node_id,
            "type": "function",
            "name": self.name,
            "path": str(self.file_path),
            "parent": self.parent.node_id,
            "code_content": self.code_content,
            "embedding": None,
            "description": None,
        }


class CodeClassNode(NodeMixin):
    def __init__(self, file_path: str, parent: CodeFileNode, code_content: str) -> None:
        """_summary_

        Args:
            name (str): _description_
            file_path (str): _description_
            parent (CodeFolderNode, optional): _description_. Defaults to None.
        """
        super().__init__()

        self.node_id = str(uuid.uuid4())
        self.name = get_class_definition(code_content)
        self.file_path = file_path
        self.parent = parent
        self.code_content = code_content

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def dictify_for_neo4j(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        return {
            "id": self.node_id,
            "type": "class",
            "name": self.name,
            "path": str(self.file_path),
            "parent": self.parent.node_id,
            "code_content": self.code_content,
            "embedding": None,
            "description": None,
        }


class CodePieceNode(NodeMixin):
    def __init__(self, file_path: str, parent: CodeFileNode, code_content: str) -> None:
        """_summary_

        Args:
            name (str): _description_
            file_path (str): _description_
            parent (CodeFolderNode, optional): _description_. Defaults to None.
        """
        super().__init__()

        self.node_id = str(uuid.uuid4())
        self.file_path = file_path
        self.parent = parent
        self.code_content = code_content

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.file_path})"

    def dictify_for_neo4j(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        return {
            "id": self.node_id,
            "type": "code_piece",
            "name": None,
            "path": str(self.file_path),
            "parent": self.parent.node_id,
            "code_content": self.code_content,
            "embedding": None,
            "description": None,
        }


def build_tree_recursive(file_path: Path) -> CodeFolderNode:
    """
    Parent function to build the file tree with progress tracking using os.walk and tqdm.

    Args:
        file_path (Path): The root path of the file system to build the tree from.

    Returns:
        Union[CodeFileNode, CodeFolderNode]: The root node of the constructed tree.
    """

    total_items = (
        sum(len(files) + len(dirs) for _, dirs, files in os.walk(file_path)) + 1
    )  # plus one for base dir

    with tqdm(
        total=total_items,
        desc="Building code tree",
        unit="item",
        bar_format="Lilith - INFO - {l_bar}{bar}{r_bar}",
    ) as pbar:
        root = __build_tree_recursive(file_path, parent=None, pbar=pbar)

    return root


def is_python_file(current_path: Path) -> bool:
    """
    Check if the given Path points to a Python file based on its extension.

    Args:
        current_path (Path): The path to check.

    Returns:
        bool: True if it's a Python file, False otherwise.
    """

    result = current_path.is_file() and current_path.suffix.lower() == ".py"
    return result


def __build_tree_recursive(
    current_path: Path,
    parent: CodeFileNode | CodeFolderNode = None,
    pbar: tqdm = None,
) -> CodeFolderNode:
    """_summary_

    Args:
        current_path (Path): _description_
        parent (CodeFileNode | CodeFolderNode, optional): _description_. Defaults to None.
        pbar (tqdm, optional): _description_. Defaults to None.

    Returns:
        CodeFolderNode: _description_
    """

    name = current_path.name

    if current_path.is_dir():
        node = CodeFolderNode(name=name, folder_path=current_path, parent=parent)

        pbar.update(1)
        try:
            for item in current_path.iterdir():
                __build_tree_recursive(item, parent=node, pbar=pbar)

        except PermissionError as e:
            logger.error(f"Permission denied: {current_path}")
            raise CoreError(f"Building code tree failed with error: {e}")

    else:
        node = CodeFileNode(name=name, file_path=current_path, parent=parent)
        node.refresh_content_hash()

        # current_path

        if is_python_file(current_path):
            chunks = split_code_file_into_chunks(current_path)

            for chunk in chunks:
                if chunk["type"] == "function":
                    CodeFunctionNode(
                        file_path=current_path, parent=node, code_content=chunk["code"]
                    )
                if chunk["type"] == "class":
                    CodeClassNode(
                        file_path=current_path, parent=node, code_content=chunk["code"]
                    )
                if chunk["type"] == "code_piece":
                    CodePieceNode(
                        file_path=current_path, parent=node, code_content=chunk["code"]
                    )

        pbar.update(1)

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
