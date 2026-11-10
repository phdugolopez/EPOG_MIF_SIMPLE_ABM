"""The line budget and the naming rule of the build (v4-plan.md, "Conventions" and section 12).

The model code has at most 1,000 lines that are not blank, not a comment line and not part of
a docstring (v4-choices.md, decision 23).
"""
import ast
import io
import pathlib
import tokenize
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIMIT = 1000
STEPS = ("common", "setup", "pricing", "demand", "accounts", "scrapping", "investment", "entry")
NOT_CODE = (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
            tokenize.ENDMARKER)


def model_files(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    """The model code: parameters.py, run.py, equations/, markets/ and model/."""
    files = [root / "parameters.py", root / "run.py"]
    for package in ("equations", "markets", "model"):
        files += sorted((root / package).rglob("*.py"))
    return [path for path in files if path.exists()]


def docstring_lines(source: str) -> set[int]:
    """The lines of the docstrings of the module, its classes and its functions."""
    lines = set()
    owners = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, owners) and ast.get_docstring(node, clean=False) is not None:
            first = node.body[0]
            lines.update(range(first.lineno, first.end_lineno + 1))
    return lines


def code_lines(source: str) -> set[int]:
    """The lines that hold code: not blank, not a comment line, not part of a docstring."""
    lines = set()
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in NOT_CODE:
            lines.update(range(token.start[0], token.end[0] + 1))
    return lines - docstring_lines(source)


def count_lines(files: list[pathlib.Path]) -> int:
    return sum(len(code_lines(path.read_text())) for path in files)


class TestCounter(unittest.TestCase):
    def test_blank_lines_comment_lines_and_docstrings_are_not_counted(self):
        source = '\n'.join([
            '"""Module docstring,',
            'on two lines."""',
            'import math  # a comment after code still counts as code',
            '',
            '# a comment line',
            'def area(radius):',
            '    """A docstring."""',
            '    # another comment line',
            '    text = """a string that is not',
            '    a docstring"""',
            '    return math.pi * radius ** 2',
            '',
        ])
        self.assertEqual(sorted(code_lines(source)), [3, 6, 9, 10, 11])


class TestBudget(unittest.TestCase):
    def test_model_code_is_within_the_limit(self):
        lines = count_lines(model_files())
        print(f"\nmodel code: {lines} lines without blank lines, comments and docstrings "
              f"(limit {LIMIT})")
        self.assertLessEqual(lines, LIMIT)

    def test_equation_files_are_named_after_their_step(self):
        for path in sorted((ROOT / "equations").glob("*.py")):
            if path.name != "__init__.py":
                self.assertIn(path.name.split("_")[0], STEPS, path.name)


if __name__ == "__main__":
    unittest.main()
