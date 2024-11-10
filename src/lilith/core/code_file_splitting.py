from __future__ import annotations

import ast
import os

from itertools import groupby
from typing import TYPE_CHECKING

import black


if TYPE_CHECKING:
    from pathlib import Path


def join_code_pieces(node_array: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Joins consecutive 'code_piece' entries into a single entry, separated by os.linesep.

    Args:
        node_array (List[Dict[str, str]]): List of nodes with 'type' and 'code'.

    Returns:
        List[Dict[str, str]]: New list with joined 'code_piece' entries.
    """
    joined_nodes = []

    for node_type, group in groupby(node_array, key=lambda x: x["type"]):
        if node_type == "code_piece":
            combined_code = os.linesep.join(item["code"] for item in group)
            joined_nodes.append({"type": "code_piece", "code": combined_code})
        else:
            for item in group:
                joined_nodes.append(item)

    return joined_nodes


def format_code_pieces(node_array: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []

    for node in node_array:
        output.append(
            {
                "type": node["type"],
                "code": black.format_file_contents(
                    node["code"], fast=False, mode=black.Mode()
                ),
            }
        )

    return output


def get_function_and_class_bounds(
    tree: ast.Module,
) -> list[dict[str, str]]:
    """Recursively process AST nodes, inserting markers around classes and functions."""
    output = []

    for node in tree.body:

        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            output.append({"type": "function", "code": ast.unparse(node)})
        elif isinstance(node, ast.ClassDef):
            output.append({"type": "class", "code": ast.unparse(node)})
        else:
            output.append({"type": "code_piece", "code": ast.unparse(node)})

    joined_pieces = join_code_pieces(output)

    return format_code_pieces(joined_pieces)


def split_code_file_into_chunks(file_path: Path) -> list[tuple]:
    content = None

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    ast_tree = ast.parse(source=content, type_comments=True)

    output = get_function_and_class_bounds(ast_tree)

    return output
