"""
Count lines of code in each backend, split into code, comments, docstrings
and blank lines. Used for the "code size" section of comparison_notes.md.

Run from the project root:  python docs/count_lines.py
"""

import ast
import io
import os
import tokenize

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKENDS = [os.path.join("system_oop", "backend"),
            os.path.join("system_imperative", "backend")]


def docstring_lines(source):
    """Return the set of line numbers that belong to docstrings."""
    lines = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                lines.update(range(body[0].lineno, body[0].end_lineno + 1))
    return lines


def comment_only_lines(source):
    """Return the set of line numbers that contain only a comment."""
    lines = set()
    source_lines = source.splitlines()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            line_number = token.start[0]
            if source_lines[line_number - 1].strip().startswith("#"):
                lines.add(line_number)
    return lines


def count_file(path):
    """Return a dict of counts for one Python file."""
    with open(path, encoding="utf-8") as file:
        source = file.read()
    all_lines = source.splitlines()
    blank = {number for number, text in enumerate(all_lines, start=1) if text.strip() == ""}
    docstrings = docstring_lines(source) - blank
    comments = comment_only_lines(source) - blank - docstrings
    total = len(all_lines)
    return {
        "total": total,
        "blank": len(blank),
        "comments": len(comments),
        "docstrings": len(docstrings),
        "code": total - len(blank) - len(comments) - len(docstrings),
    }


def main():
    """Print a table per backend and a summary."""
    columns = ["total", "code", "comments", "docstrings", "blank"]
    for backend in BACKENDS:
        folder = os.path.join(PROJECT_ROOT, backend)
        print(f"\n{backend}")
        print(f"  {'file':<18}" + "".join(f"{name:>11}" for name in columns))
        totals = dict.fromkeys(columns, 0)
        files = 0
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py"):
                continue
            counts = count_file(os.path.join(folder, name))
            files += 1
            for column in columns:
                totals[column] += counts[column]
            print(f"  {name:<18}" + "".join(f"{counts[c]:>11}" for c in columns))
        print(f"  {'TOTAL (' + str(files) + ' files)':<18}"
              + "".join(f"{totals[c]:>11}" for c in columns))


if __name__ == "__main__":
    main()
