import ast

def get_bounds_of_node(node):
    start_line = node.lineno - 1
    end_line = node.end_lineno - 1
    return start_line, end_line

def get_code_of_node(node, content):
    """Retrieve the exact code from the file content based on the AST node's location."""

    lines = content.splitlines(keepends=True)
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


def process_node(node, content, output_lines):
    """Recursively process AST nodes, inserting markers around classes and functions."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        code = get_code_of_node(node, content)
    elif isinstance(node, ast.ClassDef):
        code = get_code_of_node(node, content)

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_code = get_code_of_node(child, content)
            else:
                # Recursively process other nodes inside the class (e.g., nested classes)
                process_node(child, content, output_lines)


with open(
    "/workspaces/python3-poetry-pyenv/tests/simplejson-master/simplejson/decoder.py"
) as f:
    content = f.read()
    tree = ast.parse(content, type_comments=True)

    output_lines = []

    # Process top-level nodes in order
    for node in tree.body:
        process_node(node, content, output_lines)

    # Write the modified content to a new file
    with open("xd.py", "w") as out_f:
        out_f.writelines(output_lines)


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
