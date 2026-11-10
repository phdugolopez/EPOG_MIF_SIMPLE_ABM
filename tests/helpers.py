"""Small builders shared by the tests."""
from model.entities import Technique
from parameters import MENU


def menu() -> list[Technique]:
    """Shaikh's three techniques, in the order C, D1, D2 (addendum A1)."""
    return [Technique(name, ucs, kappa) for name, ucs, kappa in MENU]
