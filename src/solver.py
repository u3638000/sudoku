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


def is_solution(solution: Grid, puzzle: str) -> bool:
    "Is this proposed solution to the puzzle actually valid?"
    puzzle_grid = parse(puzzle)
    return (
        solution is not None
        and all(solution[s] in puzzle_grid[s] for s in squares)
        and all({solution[s] for s in unit} == set(digits) for unit in all_units)
    )


def guess(grid: Grid, square: Square, digit: Digit) -> Optional[Grid]:
    logger.debug(f"\nGuessing Digit: {digit} In Square: {square}")
    queue = [(square, digit, grid[square])]
    grid[square] = digit
    logger.debug(f"\nInitial queue: {queue}")

    while queue:
        square, digit, original_digits = queue.pop(0)
        logger.debug(f"-> In Square: {square} With Digit: {digit}")
        for peer in peers[square]:
            if digit in grid[peer]:
                # remove the digit from the peer's possibilities
                logger.debug(f"Removing Digit: {digit} From Peer: {peer}")
                grid[peer] = grid[peer].replace(digit, "")
                if len(grid[peer]) == 1:
                    queue.append((peer, grid[peer], digit))
                elif len(grid[peer]) == 0:
                    return None
            for unit in units[peer]:
                # check if the peer's unit has only one place for possible digits
                for possible_digit in original_digits:
                    digit_places = [s for s in unit if possible_digit in grid[s]]
                    if (
                        len(digit_places) == 1
                        and grid[digit_places[0]] != possible_digit
                    ):
                        logger.debug(
                            f"Placing Digit: {possible_digit} In Square: {digit_places[0]}"
                        )
                        queue.append(
                            (digit_places[0], possible_digit, grid[digit_places[0]])
                        )
                        grid[digit_places[0]] = possible_digit
                    elif len(digit_places) == 0:
                        return None
        logger.debug(f"\n{picture(grid)}")

    return grid


def constrain(grid: Grid) -> Optional[Grid]:
    queue = [
        (square, digit, digits) for square, digit in grid.items() if len(digit) == 1
    ]
    logger.debug(f"\nInitial queue: {queue}")

    while queue:
        square, digit, original_digits = queue.pop(0)
        logger.debug(f"-> In Square: {square} With Digit: {digit}")
        for peer in peers[square]:
            if digit in grid[peer]:
                # remove the digit from the peer's possibilities
                logger.debug(f"Removing Digit: {digit} From Peer: {peer}")
                grid[peer] = grid[peer].replace(digit, "")
                if len(grid[peer]) == 1:
                    queue.append((peer, grid[peer], digit))
                elif len(grid[peer]) == 0:
                    return None
            for unit in units[peer]:
                # check if the peer's unit has only one place for possible digits
                for possible_digit in original_digits:
                    digit_places = [s for s in unit if possible_digit in grid[s]]
                    if (
                        len(digit_places) == 1
                        and grid[digit_places[0]] != possible_digit
                    ):
                        logger.debug(
                            f"Placing Digit: {possible_digit} In Square: {digit_places[0]}"
                        )
                        queue.append(
                            (digit_places[0], possible_digit, grid[digit_places[0]])
                        )
                        grid[digit_places[0]] = possible_digit
                    elif len(digit_places) == 0:
                        return None
        logger.debug(f"\n{picture(grid)}")

    return grid


def parse(puzzle: str) -> Grid:
    import re

    vals = re.findall(r"[.1-9]", puzzle)
    assert len(vals) == 81

    return {s: digits if v == "." else v for s, v in zip(squares, vals)}


def puzzle2grid(puzzle: str) -> Grid:
    import re

    vals = re.findall(r"[.1-9]", puzzle)
    assert len(vals) == 81

    return {s: digits if v == "." else v for s, v in zip(squares, vals)}


def grid2puzzle(grid: Grid) -> str:
    return "".join(grid[s] if len(grid[s]) == 1 else "." for s in squares)


def picture(grid: Grid) -> Picture:
    """Convert a Grid to a Picture string, one line at a time."""
    if grid is None:
        return "None"

    def val(d: DigitSet) -> str:
        return "." if d == digits else d if len(d) == 1 else "{" + d + "}"

    maxwidth = max(len(val(grid[s])) for s in grid)
    dash1 = "-" * (maxwidth * 3 + 2)
    dash3 = "\n   " + "+".join(3 * [dash1])

    def cell(r, c):
        return val(grid[r + c]).center(maxwidth) + ("|" if c in "36" else " ")

    def line(r):
        return (
            r + "  " + "".join(cell(r, c) for c in cols) + (dash3 if r in "CF" else "")
        )

    columns = "   " + " ".join(c.center(maxwidth) for c in cols) + "\n\n"

    return columns + "\n".join(map(line, rows))


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
        solution = search(guess(grid.copy(), s, d))
        if solution:
            return solution
        else:
            logger.debug(f"No solution found for guessing Digit: {d} In Square: {s}")
    return None


def solve_puzzles(puzzles: list[str], verbose=True) -> list[list[str]]:
    result = []
    for puzzle in puzzles:
        grid = parse(puzzle)
        if grid is None:
            logger.error("Invalid puzzle")
            result.append([])
            continue
        logger.debug(f"initial grid:\n{picture(grid)}")

        constrained_grid = constrain(grid.copy())
        if constrained_grid is None:
            logger.error("Invalid puzzle")
            result.append([])
            continue
        logger.debug(f"constrained grid:\n{picture(constrained_grid)}")

        solution = search(constrained_grid)
        if solution is None:
            logger.error("Invalid puzzle")
            result.append([])
            continue
        result.append([grid2puzzle(solution)])
        if verbose:
            print_side_by_side(
                "\nPuzzle:\n" + picture(grid), "\nSolution:\n" + picture(solution)
            )
        logger.debug(f"Solution:\n{picture(solution)}")
    return result


def print_side_by_side(left, right, width=30):
    """Print two strings side-by-side, line-by-line, each side `width` wide."""
    for L, R in zip(left.splitlines(), right.splitlines()):
        print(L.ljust(width), R.ljust(width))


if __name__ == "__main__":
    puzzles = [
        "..5.3...26.3..91.5.9.....7.51...2..6..6.7...8.....675...........8...7.494.9.6...7",
        "....7..2.8.......6.1.2.5...9.54....8.........3....85.1...3.2.8.4.......9.7..6....",
        "..........3....8...8.......6....1.4.2........5.......1..8...............7........",
    ]
    print(solve_puzzles(puzzles, verbose=True))
