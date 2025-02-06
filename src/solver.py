from logging_config import setup_logger

logger = setup_logger(__name__, "DEBUG")

from typing import Dict, Optional


def cross(A, B) -> tuple:
    "Cross product of strings in A and strings in B."
    return tuple(a + b for a in A for b in B)


Digit = str  # e.g. '1'
digits = "123456789"
DigitSet = str  # e.g. '123'
rows = "ABCDEFGHI"
cols = digits
Square = str  # e.g. 'A9'
squares = cross(rows, cols)
Grid = Dict[Square, DigitSet]  # E.g. {'A9': '123', ...}
all_boxes = [
    cross(rs, cs) for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")
]
all_units = [cross(rows, c) for c in cols] + [cross(r, cols) for r in rows] + all_boxes
units = {s: tuple(u for u in all_units if s in u) for s in squares}
peers = {s: set().union(*units[s]) - {s} for s in squares}
Picture = str


def is_solution(solution: Grid, puzzle: Grid) -> bool:
    "Is this proposed solution to the puzzle actually valid?"
    return (
        solution is not None
        and all(solution[s] in puzzle[s] for s in squares)
        and all({solution[s] for s in unit} == set(digits) for unit in all_units)
    )


def constrain(puzzle: str) -> Optional[Grid]:
    for s, d in zip(squares, puzzle):
        if d in digits:
            
    queue = [
        (square, digit)
        for square in grid
        for digit in grid[square]
        if len(grid[square]) == 1
    ]
    logger.debug(f"\nInitial queue: {queue}")
    while queue:
        square, digit = queue.pop()
        logger.debug(f"Processing square: {square} with digit: {digit}")
        candidates = []
        for peer in peers[square]:
            if digit in grid[peer]:
                # remove the digit from the peer's possibilities
                logger.debug(f"Removing digit: {digit} from peer: {peer}")
                candidates.append((peer, grid[peer]))
                grid[peer] = grid[peer].replace(digit, "")
                if len(grid[peer]) == 1:
                    queue.append((peer, grid[peer]))
                elif len(grid[peer]) == 0:
                    return None
        logger.debug(f"\n{picture(grid)}")

        for peer, peer_digits in candidates:
            for peer_unit in units[peer]:
                for candidate_digit in peer_digits:
                    # check if the peer's unit has only one place for the candidate digit
                    digit_places = [s for s in peer_unit if candidate_digit in grid[s]]
                    if (
                        len(digit_places) == 1
                        and grid[digit_places[0]] != candidate_digit
                    ):
                        logger.debug(
                            f"Placing digit: {candidate_digit} in square: {digit_places[0]}"
                        )
                        grid[digit_places[0]] = candidate_digit
                        queue.append((digit_places[0], candidate_digit))
                    elif len(digit_places) == 0:
                        return None
        logger.debug(f"\n{picture(grid)}")

    return grid


def parse(puzzle: str) -> Grid:
    import re

    vals = re.findall(r"[.1-9]", puzzle)
    assert len(vals) == 81

    return {s: digits if v == "." else v for s, v in zip(squares, vals)}


def picture(grid) -> Picture:
    """Convert a Grid to a Picture string, one line at a time."""
    if grid is None:
        return "None"

    def val(d: DigitSet) -> str:
        return "." if d == digits else d if len(d) == 1 else "{" + d + "}"

    maxwidth = max(len(val(grid[s])) for s in grid)
    dash1 = "-" * (maxwidth * 3 + 2)
    dash3 = "\n" + "+".join(3 * [dash1])

    def cell(r, c):
        return val(grid[r + c]).center(maxwidth) + ("|" if c in "36" else " ")

    def line(r):
        return "".join(cell(r, c) for c in cols) + (dash3 if r in "CF" else "")

    return "\n".join(map(line, rows))


def search(grid) -> Grid:
    "Depth-first search with constraint propagation to find a solution."
    if grid is None:
        return None
    s = min(
        (s for s in squares if len(grid[s]) > 1),
        default=None,
        key=lambda s: len(grid[s]),
    )
    if s is None:  # No squares with multiple possibilities; the search has succeeded
        return grid
    for d in grid[s]:
        solution = search(fill(grid.copy(), s, d))
        if solution:
            return solution
    return None


def solve_puzzles(puzzles: list[str], verbose=True) -> int:
    for puzzle in puzzles:
        grid = parse(puzzle)
        assert grid is not None
        logger.debug(f"\n{picture(grid)}")

        constrained_grid = constrain(puzzle)
        assert constrained_grid is not None
        logger.debug(f"\n{picture(constrained_grid)}")

        assert False

        solution = search(constrained_grid)
        assert is_solution(solution, puzzle)
        if verbose:
            print_side_by_side(
                "\nPuzzle:\n" + picture(puzzle), "\nSolution:\n" + picture(solution)
            )
    return len(puzzles)


def print_side_by_side(left, right, width=20):
    """Print two strings side-by-side, line-by-line, each side `width` wide."""
    for L, R in zip(left.splitlines(), right.splitlines()):
        print(L.ljust(width), R.ljust(width))


if __name__ == "__main__":
    puzzles = [
        "..5.3...26.3..91.5.9.....7.51...2..6..6.7...8.....675...........8...7.494.9.6...7",
        "....7..2.8.......6.1.2.5...9.54....8.........3....85.1...3.2.8.4.......9.7..6....",
        # "..........3....8...8.......6....1.4.2........5.......1..8...............7........",
    ]
    print(solve_puzzles(puzzles, verbose=True))
