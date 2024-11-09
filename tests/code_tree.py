from __future__ import annotations

import hashlib
import mimetypes
import os

from anytree import NodeMixin
from anytree import RenderTree
from anytree.exporter import JsonExporter


class CodeFolderNode(NodeMixin):
    def __init__(
        self, name: str, folder_path: str, parent: CodeFolderNode = None
    ) -> None:
        super().__init__()
        self.name = name
        self.folder_path = folder_path
        self.parent = parent

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.path})"


class CodeFileNode(NodeMixin):
    def __init__(
        self,
        name: str,
        file_path: str,
        parent: CodeFolderNode = None,
    ) -> None:
        super().__init__()
        self.name = name
        self.file_path = file_path
        self.parent: CodeFolderNode = parent
        self.content_hash = None

    def get_content(self):
        try:
            stat_info = os.stat(self.file_path)
            creation_time = stat_info.st_ctime
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
            print(f"Error: The file '{self.file_path}' does not exist.")
        except PermissionError:
            print(
                f"Error: You do not have permission to read the file '{self.file_path}'."
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def refresh_content_hash(self):
        content = self.get_content()["content"]
        self.content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, path={self.path})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, path={self.path})"


def build_tree(current_path, parent=None):
    name = os.path.basename(current_path)

    if os.path.isdir(current_path):
        node = CodeFolderNode(name=name, folder_path=current_path, parent=parent)

        for item in os.listdir(current_path):
            item_path = os.path.join(current_path, item)
            build_tree(item_path, parent=node)

    else:
        with open(current_path, encoding="utf-8") as f:
            content = f.read()

        node = CodeFileNode(
            name=name,
            file_path=current_path,
            parent=parent,
        )

        node.refresh_content_hash()

    return node


root_path = "/workspaces/python3-poetry-pyenv/tests/simplejson-master"
tree_root = build_tree(root_path)

for pre, _, node in RenderTree(tree_root):
    print(f"{pre}{node.name}")


# exporter = JsonExporter(indent=2, sort_keys=True)
# print(exporter.export(tree_root))

# print(tree_root.children[8].get_content())
