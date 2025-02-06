from src.solver import solve_puzzles

import pytest


@pytest.mark.easy
def test_solve_hardest():
    hardest = [puzzle for puzzle in open("hardest.txt")]

    assert solve_puzzles(hardest, verbose=False) is not None


@pytest.mark.hard
def test_solve_sudoku10k():
    grids10k = [puzzle for puzzle in open("sudoku10k.txt")]

    assert solve_puzzles(grids10k, verbose=False) is not None
