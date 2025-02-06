from logging_config import setup_logger

logger = setup_logger(__name__, "INFO")

from solver import parse, solve_puzzles


random_number = 11


def generate_puzzle() -> str:
    import random

    def generate_random() -> str:
        pic = "." * 81
        random_locations = random.sample(range(81), random_number)
        for i in random_locations:
            pic = pic[:i] + str(random.randint(1, 9)) + pic[i + 1 :]
        return pic

    pic = generate_random()
    grid = parse(pic)
    print(pic)

    success = False
    while not success:
        try:
            solve_puzzles([grid], verbose=False)
            success = True
        except AssertionError:
            pic = generate_random()
            grid = parse(pic)
            print(pic)
    return pic


pics = [
    "..........3....8...8.......6....1.4.2........5.......1..8...............7........",
]

"""
. . .|. . .|. . .
. 3 .|. . .|8 . .
. 8 .|. . .|. . .
-----+-----+-----
6 . .|. . 1|. 4 .
2 . .|. . .|. . .
5 . .|. . .|. . 1
-----+-----+-----
. . 8|. . .|. . .
. . .|. . .|. . .
7 . .|. . .|. . .
"""


def stress_test():
    cnt = 0
    for _ in range(100):
        cnt += 1 if generate_puzzle() else 0
    print(f"Generated {cnt} puzzles when picking {random_number} locations.")


if __name__ == "__main__":
    for pic in pics:
        print(pic)
        grid = parse(pic)
        solve_puzzles([grid], verbose=True)
        print()
    # stress_test()
