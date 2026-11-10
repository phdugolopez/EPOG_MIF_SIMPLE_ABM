"""Small builders shared by the tests."""
from model.entities import Technique
from parameters import SHAIKH_MENU


def menu() -> list[Technique]:
    """Shaikh's three techniques, in the order C, D1, D2: the menu at rbar = 0.16."""
    return [Technique(name, ucs, kappa) for name, ucs, kappa in SHAIKH_MENU]
