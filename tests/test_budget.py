"""The line budget and the naming rule of the build (CLAUDE.md; plan, section 1 and Q1)."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET, LIMIT = 700, 770
STEPS = ("common", "setup", "pricing", "demand", "accounts", "scrapping", "investment", "entry")


def model_files() -> list[pathlib.Path]:
    """The model code: everything but tests, experiments and figures."""
    files = [ROOT / "parameters.py", ROOT / "run.py"]
    for package in ("equations", "markets", "model"):
        files += sorted((ROOT / package).rglob("*.py"))
    return [f for f in files if f.exists()]


def count_lines(files: list[pathlib.Path]) -> int:
    """Lines that are not blank; comments and docstrings count."""
    return sum(1 for f in files for line in f.read_text().splitlines() if line.strip())


class TestBudget(unittest.TestCase):
    def test_model_code_is_within_the_limit(self):
        lines = count_lines(model_files())
        print(f"\nmodel code: {lines} lines without blank lines (target {TARGET}, limit {LIMIT})")
        self.assertLessEqual(lines, LIMIT)

    def test_equation_files_are_named_after_their_step(self):
        for f in sorted((ROOT / "equations").glob("*.py")):
            if f.name != "__init__.py":
                self.assertIn(f.name.split("_")[0], STEPS, f.name)


if __name__ == "__main__":
    unittest.main()
