"""The automatic checks of readability, on the model code (v4-plan.md, section 12).

Each check is a function from a source text to a list of problems, "line n: what". The first
class runs the checks on the model code; the second shows that each check catches what it is
for. What a machine cannot check is left to the reader of stage 4.
"""
import ast
import io
import pathlib
import re
import tokenize
import unittest

from test_budget import ROOT, model_files

LETTERS = ("p", "c", "z", "t", "u", "i", "j", "k", "n")
MAX_LENGTH = 100
PROPOSAL = ROOT / "docs" / "design" / "v4-final-model.md"
SCHEDULER = ROOT / "model" / "scheduler.py"


def own_expressions(statement: ast.stmt) -> list[ast.AST]:
    """The nodes of a statement, without those of the statements nested in it."""
    nodes = []
    stack = list(ast.iter_child_nodes(statement))
    while stack:
        node = stack.pop()
        if not isinstance(node, ast.stmt):
            nodes.append(node)
            stack.extend(ast.iter_child_nodes(node))
    return nodes


def needs_a_comment(node: ast.AST) -> bool:
    """A comprehension that filters, a sort key or a lambda."""
    filters = isinstance(node, ast.comprehension) and bool(node.ifs)
    sort_key = isinstance(node, ast.keyword) and node.arg == "key"
    return filters or sort_key or isinstance(node, ast.Lambda)


def uncommented_selections(source: str) -> list[str]:
    """Statements that filter, sort or use a lambda without a comment line just above."""
    lines = source.splitlines()
    problems = []
    for statement in ast.walk(ast.parse(source)):
        if isinstance(statement, ast.stmt) and any(map(needs_a_comment,
                                                       own_expressions(statement))):
            above = lines[statement.lineno - 2].strip() if statement.lineno > 1 else ""
            if not above.startswith("#"):
                problems.append(f"line {statement.lineno}: a filter, a sort key or a lambda "
                                f"without a comment line above")
    return problems


def double_statements(source: str) -> list[str]:
    """Statements that do two things, as far as the syntax shows it."""
    problems = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Tuple, ast.List)):
            if any(isinstance(target, (ast.Tuple, ast.List)) for target in node.targets):
                problems.append(f"line {node.lineno}: a tuple of values assigned to a tuple "
                                f"of names")
        if isinstance(node, ast.Call):
            arguments = node.args + [keyword.value for keyword in node.keywords]
            if any(isinstance(inner, ast.IfExp)
                   for argument in arguments for inner in ast.walk(argument)):
                problems.append(f"line {node.lineno}: a conditional expression inside a call")
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.OP and token.string == ";":
            problems.append(f"line {token.start[0]}: two statements on one line")
    return problems


def short_names(source: str) -> list[str]:
    """Names of one letter that are not a symbol of the proposal or a loop index."""
    problems = []
    for node in ast.walk(ast.parse(source)):
        name = getattr(node, "id", None) if isinstance(node, ast.Name) else None
        name = node.arg if isinstance(node, ast.arg) else name
        if name is not None and len(name) == 1 and name not in LETTERS:
            problems.append(f"line {node.lineno}: the name {name!r}")
    return problems


def long_lines(source: str) -> list[str]:
    """Lines of more than 100 characters."""
    return [f"line {number}: {len(line)} characters"
            for number, line in enumerate(source.splitlines(), start=1)
            if len(line) > MAX_LENGTH]


def blocks_without_a_comment(source: str, functions: list[str]) -> list[str]:
    """In the named functions, the blocks that follow a blank line and do not open with a
    comment. A block is what follows a blank line inside the body."""
    lines = source.splitlines()
    problems = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            for number in range(node.body[0].end_lineno + 1, node.end_lineno + 1):
                line, above = lines[number - 1].strip(), lines[number - 2].strip()
                if line and not above and not line.startswith("#"):
                    problems.append(f"line {number}: a block of {node.name} without a comment")
    return problems


def proposal_sections() -> list[str]:
    """The headings of the proposal and the bold titles that open its paragraphs."""
    text = PROPOSAL.read_text()
    headings = re.findall(r"^#+ (.+)$", text, flags=re.MULTILINE)
    titles = re.findall(r"^\*\*([^*]+?)\.\*\*", text, flags=re.MULTILINE)
    return headings + titles


def missing_source(source: str, sections: list[str]) -> list[str]:
    """An equation file whose docstring does not name the proposal and one of its sections."""
    docstring = ast.get_docstring(ast.parse(source)) or ""
    if "v4-final-model.md" not in docstring:
        return ["the module docstring does not name v4-final-model.md"]
    if not any(f'"{section}"' in docstring for section in sections):
        return ["the module docstring names no section of the proposal"]
    return []


class TestModelCode(unittest.TestCase):
    def check(self, problems_of) -> None:
        for path in model_files():
            problems = problems_of(path.read_text())
            self.assertEqual(problems, [], f"{path.relative_to(ROOT)}: {problems}")

    def test_a_filter_a_sort_key_or_a_lambda_has_a_comment_line_above(self):
        self.check(uncommented_selections)

    def test_no_statement_does_two_things(self):
        self.check(double_statements)

    def test_a_name_of_one_letter_is_a_symbol_or_a_loop_index(self):
        self.check(short_names)

    def test_lines_have_at_most_100_characters(self):
        self.check(long_lines)

    def test_each_equation_file_opens_with_its_source(self):
        sections = proposal_sections()
        self.assertIn("Schedule", sections)
        for path in sorted((ROOT / "equations").glob("*.py")):
            if path.name != "__init__.py":
                self.assertEqual(missing_source(path.read_text(), sections), [], path.name)

    @unittest.skipUnless(SCHEDULER.exists(), "model/scheduler.py is written in stage 2")
    def test_each_block_of_a_step_function_opens_with_a_comment(self):
        """The step functions are those of STEPS, and close_period."""
        from model import scheduler
        steps = [step.__name__ for step in scheduler.STEPS] + ["close_period"]
        self.assertEqual(blocks_without_a_comment(SCHEDULER.read_text(), steps), [])


class TestChecks(unittest.TestCase):
    """Each check catches what it is for, and lets the style of the plan through."""

    def test_a_filter_without_a_comment_is_caught(self):
        bad = "active = [firm for firm in firms if firm.plants]\n"
        good = "# The firms with a plant in operation.\n" + bad
        self.assertEqual(len(uncommented_selections(bad)), 1)
        self.assertEqual(uncommented_selections(good), [])
        self.assertEqual(uncommented_selections("prices = [firm.price for firm in firms]\n"), [])

    def test_a_sort_key_and_a_lambda_without_a_comment_are_caught(self):
        self.assertEqual(len(uncommented_selections("best = min(plants, key=cost)\n")), 1)
        self.assertEqual(len(uncommented_selections("rate = lambda price: price / 2\n")), 1)
        self.assertEqual(uncommented_selections("# Lowest cost.\nbest = min(plants, key=cost)\n"),
                         [])

    def test_the_comment_goes_above_the_statement_that_filters_not_above_its_block(self):
        source = "\n".join([
            "# Each firm.",
            "for firm in firms:",
            "    ran = [plant for plant in firm.plants if plant.output > 0]",
            "",
        ])
        self.assertEqual(uncommented_selections(source),
                         ["line 3: a filter, a sort key or a lambda without a comment line above"])

    def test_statements_that_do_two_things_are_caught(self):
        self.assertEqual(len(double_statements("p, t = industry.params, industry.time\n")), 1)
        self.assertEqual(len(double_statements("cost = 1.0; price = 2.0\n")), 1)
        self.assertEqual(len(double_statements("pay(firm, roe, cash if cash > 0 else 0.0)\n")), 1)
        self.assertEqual(double_statements("price, has_cut = cutting_step(own, rivals)\n"), [])
        self.assertEqual(double_statements("seed = int(text) if text else 0\n"), [])

    def test_a_name_of_one_letter_outside_the_list_is_caught(self):
        self.assertEqual(len(short_names("total = sum(q.capacity for q in plants)\n")), 2)
        self.assertEqual(len(short_names("def area(r):\n    return r\n")), 2)
        self.assertEqual(short_names("p = industry.params\nn = len(p.start)\n"), [])

    def test_a_long_line_is_caught(self):
        self.assertEqual(long_lines("x" * 100 + "\n"), [])
        self.assertEqual(long_lines("short\n" + "x" * 101 + "\n"), ["line 2: 101 characters"])

    def test_a_block_without_a_comment_is_caught_in_a_step_function_only(self):
        source = "\n".join([
            "def set_prices(industry):",
            '    """Step 1."""',
            "    p = industry.params",
            "",
            "    # Read every firm.",
            "    quotes = read(industry)",
            "",
            "    post(quotes)",
            "",
            "",
            "def read(industry):",
            '    """A helper."""',
            "    firms = industry.firms",
            "",
            "    return firms",
            "",
        ])
        self.assertEqual(blocks_without_a_comment(source, ["set_prices"]),
                         ["line 8: a block of set_prices without a comment"])

    def test_an_equation_file_without_its_source_is_caught(self):
        sections = ["Setting", "Schedule"]
        good = '"""uc = ucs + delta kappa.\n\nSource: v4-final-model.md, "Setting".\n"""\n'
        self.assertEqual(missing_source(good, sections), [])
        self.assertEqual(len(missing_source('"""uc = ucs + delta kappa."""\n', sections)), 1)
        self.assertEqual(len(missing_source('"""Source: v4-final-model.md."""\n', sections)), 1)
        self.assertEqual(len(missing_source("unit_cost = 1.0\n", sections)), 1)


if __name__ == "__main__":
    unittest.main()
