from __future__ import annotations

import ast
import os

from utils import BOUND_SEPERATOR


def get_bounds_of_node(node):
    start_line = node.lineno - 1
    end_line = node.end_lineno - 1
    return start_line, end_line


def get_code_of_node(node, lines):
    """Retrieve the exact code from the file content based on the AST node's location."""

    start_line = node.lineno - 1
    end_line = node.end_lineno - 1

    if start_line == end_line:
        code = lines[start_line][node.col_offset : node.end_col_offset]
    else:
        code_lines = [lines[start_line][node.col_offset :]]
        code_lines.extend(lines[start_line + 1 : end_line])
        code_lines.append(lines[end_line][: node.end_col_offset])

        code = "".join(code_lines)

    return code


def process_tree(
    tree: ast.Module,
    lines: list[str],
    output_node_content: list[dict],
    output_bounds: list[tuple],
):
    """Recursively process AST nodes, inserting markers around classes and functions."""
    for node in tree.body:

        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):

            function_code = get_code_of_node(node, lines)
            function_bounds = get_bounds_of_node(node)

            output_node_content.append({"type": "function", "code": function_code})
            output_bounds.append(function_bounds)

        elif isinstance(node, ast.ClassDef):

            class_code = get_code_of_node(node, content)
            class_bounds = get_bounds_of_node(node)

            output_bounds.append(class_bounds)

            output_class = {"type": "class", "code": class_code, "functions": []}

            for child_node in node.body:

                if isinstance(child_node, ast.FunctionDef | ast.AsyncFunctionDef):

                    method_code = get_code_of_node(child_node, lines)
                    method_bounds = get_bounds_of_node(child_node)
                    output_class["functions"].append(method_code)

                    output_bounds.append(method_bounds)
        else:
            pass


def append_seperator(seperator, output):
    output.append(seperator)
    output.append(os.linesep)


def add_seperators(code_lines: list[str], bounds: list[tuple]):

    positions_to_insert_before = []
    positions_to_insert_after = []

    for start, end in bounds:
        assert start < end, f"Incorrect bounds: {start}, {end}"

        positions_to_insert_before.append(start)
        positions_to_insert_after.append(end)

    new_lines = []

    for i in range(len(lines) + 1):

        if i in positions_to_insert_before:
            append_seperator(BOUND_SEPERATOR, new_lines)
        if i < len(lines):
            new_lines.append(lines[i])
        if i in positions_to_insert_after:
            append_seperator(BOUND_SEPERATOR, new_lines)

    return new_lines


with open(
    "/workspaces/python3-poetry-pyenv/tests/simplejson-master/simplejson/decoder.py"
) as f:

    content = f.read()
    lines = content.splitlines(keepends=True)

    tree = ast.parse(content, type_comments=True)

    output_node_contents = []
    output_bounds = []

    print(type(tree))
    process_tree(tree, lines, output_node_contents, output_bounds)

    seperated_lines = add_seperators(lines, output_bounds)

    with open("xd.py", "w") as out_f:
        out_f.writelines(seperated_lines)


# from __future__ import annotations

# from openai.embeddings_utils import cosine_similarity, get_embedding

# df["code_embedding"] = df["code"].apply(
#     lambda x: get_embedding(x, model="text-embedding-3-small")
# )

# def search_functions(df, code_query, n=3, pprint=True, n_lines=7):
#     embedding = get_embedding(code_query, model="text-embedding-3-small")
#     df["similarities"] = df.code_embedding.apply(
#         lambda x: cosine_similarity(x, embedding)
#     )

#     res = df.sort_values("similarities", ascending=False).head(n)
#     return res

# res = search_functions(df, "Completions API tests", n=3)
