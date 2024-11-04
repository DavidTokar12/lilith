from __future__ import annotations

import ast
import os

from utils import FUNCTION_SEPERATOR


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


def process_node(
    node, lines: list[str], output_node_content: list[dict], output_bounds: list[tuple]
):
    """Recursively process AST nodes, inserting markers around classes and functions."""

    # assert (
    #     len(output_node_content) + len(output_bounds) == 0
    # ), f"Got filled arrays as input: {output_node_content} {output_bounds}"

    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):

        code = get_code_of_node(node, lines)
        bounds = get_bounds_of_node(node)

        output_node_content.append({"type": "function", "code": code})
        output_bounds.append(bounds)

    elif isinstance(node, ast.ClassDef):
        code = get_code_of_node(node, content)

        for child in node.body:
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                method_code = get_code_of_node(child, lines)
                print(method_code)
            else:
                # Recursively process other nodes inside the class (e.g., nested classes)
                process_node(child, lines, output_node_content, output_bounds)
    else:
        # imports and expressions
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
            append_seperator(FUNCTION_SEPERATOR, new_lines)
        if i < len(lines):
            new_lines.append(lines[i])
        if i in positions_to_insert_after:
            append_seperator(FUNCTION_SEPERATOR, new_lines)

    return new_lines


with open(
    "/workspaces/python3-poetry-pyenv/tests/simplejson-master/simplejson/decoder.py"
) as f:

    content = f.read()
    lines = content.splitlines(keepends=True)

    tree = ast.parse(content, type_comments=True)

    output_node_contents = []
    output_bounds = []

    # Process top-level nodes in order
    for node in tree.body:
        process_node(node, lines, output_node_contents, output_bounds)
        # print(node)

    print(output_bounds)

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
